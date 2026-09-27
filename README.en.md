# retrieval-index-parity

Checks IDs, hashes and ACLs across source, FTS5 and vector metadata.

[Français](README.md) · [English](README.en.md) · [Español](README.es.md)

## Related projects

- [sqlite-fts5-check — internal FTS5 drift](https://github.com/agentscope-ai-java/sqlite-fts5-check)
- [rag-staleness-check — stale documents in indexes](https://pypi.org/project/rag-staleness-check/)
- [Truffler — hybrid retrieval with labels](https://github.com/kieranklaassen/truffler)

These projects document the need or cover part of the problem. No affiliation or integration with them is claimed.

## Quick start

```bash
python3 tool.py demo
python3 tool.py check examples/healthy.sql
```

Python 3.11+; no external package required. / Python 3.11+ ; aucune dépendance externe. / Python 3.11+; sin dependencias externas.

## Current scope

The SQLite comparator checks active IDs, tombstones, hashes and ACLs across source, FTS and vector metadata, plus FTS5 retrieval by a probe term. It does not yet search a real vector index.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT.
