import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tool import check, connect_sql
ROOT = Path(__file__).resolve().parents[1]

class ParityTests(unittest.TestCase):
    def db(self):
        return connect_sql(ROOT/'examples/healthy.sql')

    def test_healthy(self):
        self.assertTrue(check(self.db())['ok'])

    def test_tombstone_orphan(self):
        db = self.db()
        db.execute('UPDATE source SET active=0 WHERE id=?', ('doc-1',))
        self.assertFalse(check(db)['ok'])

    def test_acl_mismatch(self):
        db = self.db()
        db.execute('UPDATE vector_meta SET acl=?', ('public',))
        self.assertIn('vector: ACL mismatch doc-1', check(db)['findings'])

    def test_fts_missing(self):
        db = self.db()
        db.execute('DELETE FROM lexical_fts WHERE id=?', ('doc-1',))
        self.assertIn('FTS: missing active source doc-1', check(db)['findings'])
