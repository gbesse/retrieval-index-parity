import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bm25_plan import analyze, read_json

BASE = Path(__file__).resolve().parents[1] / "examples" / "bm25"
INDEX = "idx_memory_units_text_search"


class BM25PlanTests(unittest.TestCase):
    def test_reported_scan_misses_expected_index(self):
        result = analyze(read_json(BASE / "slow-plan.json"), INDEX, read_json(BASE / "catalog.json"))
        self.assertEqual(result["status"], "not_used")
        self.assertTrue(result["catalog_confirms_index"])
        self.assertEqual(result["used_indexes"], ["idx_memory_units_observations"])

    def test_index_execution_is_observed(self):
        result = analyze(read_json(BASE / "indexed-plan.json"), INDEX, read_json(BASE / "catalog.json"))
        self.assertEqual(result["status"], "used")
        self.assertEqual(result["execution_time_ms"], 506.0)

    def test_plan_without_analyze_is_inconclusive(self):
        capture = read_json(BASE / "indexed-plan.json")
        del capture[0]["Execution Time"]
        self.assertEqual(analyze(capture, INDEX)["status"], "inconclusive")

    def test_plan_not_executed_is_inconclusive(self):
        capture = read_json(BASE / "indexed-plan.json")
        capture[0]["Plan"]["Actual Loops"] = 0
        self.assertEqual(analyze(capture, INDEX)["status"], "inconclusive")

    def test_branch_not_executed_does_not_count_as_used(self):
        capture = read_json(BASE / "indexed-plan.json")
        capture[0]["Plan"]["Plans"][0]["Actual Loops"] = 0
        self.assertEqual(analyze(capture, INDEX)["status"], "not_used")

    def test_catalog_without_index_is_inconclusive(self):
        self.assertEqual(analyze(read_json(BASE / "slow-plan.json"), INDEX, [])["status"], "inconclusive")

    def test_invalid_plan_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze({"Plan": {"Plans": {}}}, INDEX)


if __name__ == "__main__":
    unittest.main()
