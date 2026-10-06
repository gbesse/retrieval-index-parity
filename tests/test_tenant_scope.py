import unittest

from tenant_scope import audit, audit_leviathan


class TenantScopeTests(unittest.TestCase):
    def test_explicit_labeled_fallback_is_allowed_when_policy_says_so(self):
        data = {"requested_group": "a", "policy": "labeled_fallback",
                "results": [{"group": "b", "label": "OTHER CUSTOMER"}]}
        self.assertTrue(audit(data)["ok"])

    def test_same_result_violates_strict_policy(self):
        data = {"requested_group": "a", "policy": "strict",
                "results": [{"group": "b", "label": "OTHER CUSTOMER"}]}
        self.assertEqual(audit(data)["findings"][0]["kind"], "cross_group")

    def test_unlabeled_fallback_is_flagged(self):
        data = {"requested_group": "a", "policy": "labeled_fallback",
                "results": [{"group": "b"}]}
        self.assertEqual(audit(data)["findings"][0]["kind"], "unlabeled_fallback")

    def test_actual_leviathan_search_outcome_with_labeled_fallback(self):
        outcome = {"results": [], "other_groups": [
            {"id": "ticket-2", "group": "customer-b", "other_group": True}]}
        self.assertTrue(audit_leviathan(outcome, "customer-a", "labeled_fallback")["ok"])
        self.assertEqual(audit_leviathan(outcome, "customer-a", "strict")["findings"][0]["kind"], "cross_group")

    def test_leviathan_unlabeled_fallback_fails(self):
        outcome = {"results": [], "other_groups": [{"id": "ticket-2", "group": "customer-b"}]}
        self.assertEqual(audit_leviathan(outcome, "customer-a", "labeled_fallback")["findings"][0]["kind"], "unlabeled_fallback")


if __name__ == "__main__":
    unittest.main()
