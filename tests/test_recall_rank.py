import contextlib
import copy
import io
import math
import unittest
from pathlib import Path

from recall_rank import analyze, main, metrics, read_capture

BASE = Path(__file__).parents[1] / "examples" / "recall-rank"


class RecallRankTests(unittest.TestCase):
    def test_multilingual_drop_not_hidden_by_other_languages(self):
        report = analyze(read_capture(BASE / "multilingual.json"))
        zh = report["by_language"]["zh"]
        self.assertEqual(zh["before"]["recall_at_k"], 1)
        self.assertEqual(zh["after"]["recall_at_k"], 0)
        self.assertEqual(zh["regressed_case_count"], 1)
        for lang in ("fr", "en", "es"):
            self.assertEqual(report["by_language"][lang]["regressed_case_count"], 0)
        ranks = report["cases"][-1]["judged_ranks"]
        self.assertEqual([r["after_rank"] for r in ranks], [70, 74, 71])

    def test_known_ir_metrics_and_cutoff(self):
        m = metrics(["x", "a", "y", "b"], {"a", "b"}, 3)
        self.assertEqual(m["recall_at_k"], 0.5)
        self.assertEqual(m["reciprocal_rank_at_k"], 0.5)
        self.assertAlmostEqual(
            m["ndcg_at_k"], (1 / math.log2(3)) / (1 + 1 / math.log2(3))
        )
        self.assertEqual(metrics(["a"], {"a", "b"}, 12)["recall_at_k"], 0.5)
        self.assertEqual(metrics([], {"a"}, 12)["ndcg_at_k"], 0)

    def test_rank_regression_inside_top_k(self):
        capture = {
            "cases": [
                {
                    "case_id": "test",
                    "language": "fr",
                    "k": 3,
                    "relevant_ids": ["a"],
                    "before": ["a", "x"],
                    "after": ["x", "a"],
                }
            ]
        }
        report = analyze(capture)
        self.assertTrue(report["regression"])
        self.assertEqual(report["cases"][0]["lost_from_top_k"], [])

    def test_dropped_candidate_is_absent_not_rank_zero(self):
        capture = read_capture(BASE / "healthy.json")
        capture["cases"][0]["after"] = ["x"]
        report = analyze(capture)
        self.assertIsNone(report["cases"][0]["judged_ranks"][0]["after_rank"])
        self.assertEqual(report["cases"][0]["lost_from_top_k"], ["a", "b", "c"])

    def test_invalid_judgments_ranks_and_case_ids(self):
        seed = read_capture(BASE / "healthy.json")
        for key, value in [
            ("k", True),
            ("k", 0),
            ("relevant_ids", []),
            ("before", ["a", "a"]),
            ("after", [None]),
            ("language", ""),
        ]:
            capture = copy.deepcopy(seed)
            capture["cases"][0][key] = value
            with self.assertRaises(ValueError):
                analyze(capture)
        seed["cases"].append(copy.deepcopy(seed["cases"][0]))
        with self.assertRaises(ValueError):
            analyze(seed)

    def test_arithmetic_mean_uses_queries_not_document_count(self):
        a = {
            "case_id": "one",
            "language": "en",
            "k": 1,
            "relevant_ids": ["a"],
            "before": ["a"],
            "after": ["a"],
        }
        b = {
            "case_id": "two",
            "language": "en",
            "k": 1,
            "relevant_ids": ["a", "b", "c"],
            "before": ["x"],
            "after": ["x"],
        }
        self.assertEqual(
            analyze({"cases": [a, b]})["by_language"]["en"]["after"]["recall_at_k"], 0.5
        )

    def test_cli_languages_exit_codes_and_no_query_text(self):
        for lang in ("fr", "en", "es"):
            with (
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(main(["demo", "--lang", lang]), 0)
                self.assertEqual(
                    main(["check", str(BASE / "multilingual.json"), "--lang", lang]), 2
                )
                self.assertEqual(
                    main(["check", str(BASE / "healthy.json"), "--lang", lang]), 0
                )
                self.assertEqual(main(["check", "--lang", lang]), 1)
        capture = read_capture(BASE / "healthy.json")
        capture["cases"][0]["query"] = "PRIVATE_QUERY"
        self.assertNotIn("PRIVATE_QUERY", str(analyze(capture)))


if __name__ == "__main__":
    unittest.main()
