"""Cross-index parity check for a SQLite source, FTS5 and vector metadata."""
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def check(connection):
    source = {r['id']: dict(r) for r in connection.execute('SELECT id, body, acl, active FROM source WHERE active=1')}
    lexical = {r['id']: dict(r) for r in connection.execute('SELECT id, body_hash, acl, probe FROM lexical_meta')}
    vector = {r['id']: dict(r) for r in connection.execute('SELECT id, body_hash, acl FROM vector_meta')}
    findings = []
    for index_name, index in [('lexical', lexical), ('vector', vector)]:
        for key in sorted(source.keys() - index.keys()):
            findings.append(f'{index_name}: missing active source {key}')
        for key in sorted(index.keys() - source.keys()):
            findings.append(f'{index_name}: orphan or tombstone {key}')
        for key in sorted(source.keys() & index.keys()):
            if index[key]['body_hash'] != digest(source[key]['body']):
                findings.append(f'{index_name}: stale hash {key}')
            if index[key]['acl'] != source[key]['acl']:
                findings.append(f'{index_name}: ACL mismatch {key}')
    fts_rows = [dict(r) for r in connection.execute('SELECT id, body FROM lexical_fts')]
    fts_ids = {r['id'] for r in fts_rows}
    if len(fts_ids) != len(fts_rows):
        findings.append('FTS: duplicate document IDs')
    for key in sorted(fts_ids - source.keys()):
        findings.append(f'FTS: orphan or tombstone {key}')
    for key in sorted(source.keys() - fts_ids):
        findings.append(f'FTS: missing active source {key}')
    for row in fts_rows:
        if row['id'] in source and digest(row['body']) != digest(source[row['id']]['body']):
            findings.append(f'FTS: stale body {row["id"]}')
    for key in sorted(source.keys() & lexical.keys() & fts_ids):
        probe = lexical[key]['probe']
        if not probe.isalnum() or not probe in source[key]['body']:
            findings.append(f'FTS: invalid probe {key}')
            continue
        hits = {r['id'] for r in connection.execute('SELECT id FROM lexical_fts WHERE lexical_fts MATCH ?', (probe,))}
        if key not in hits:
            findings.append(f'FTS: active source not retrievable by probe {key}')
    return {'ok': not findings, 'active_sources': len(source), 'lexical_rows': len(lexical),
            'vector_metadata_rows': len(vector), 'findings': findings}


def connect_sql(path):
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    db.executescript(Path(path).read_text())
    return db


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('demo', 'check'):
        raise SystemExit('usage: tool.py demo | check DATABASE.db or SETUP.sql')
    path = Path(__file__).parent/'examples/healthy.sql' if sys.argv[1] == 'demo' else Path(sys.argv[2])
    db = connect_sql(path) if path.suffix == '.sql' else sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    healthy = check(db)
    if sys.argv[1] == 'demo':
        db.execute('UPDATE source SET active=0 WHERE id=?', ('doc-1',))
        stale = check(db)
        print(json.dumps({'healthy': healthy, 'after_tombstone': stale}, indent=2))
        return 0 if healthy['ok'] and not stale['ok'] else 1
    print(json.dumps(healthy, indent=2))
    return 0 if healthy['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
