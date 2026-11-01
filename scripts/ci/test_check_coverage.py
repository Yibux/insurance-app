import json
import tempfile
import unittest
from pathlib import Path

import check_coverage as cc


def report(classes, failing=0, wrapped=True):
    """Build a report shaped like `sf apex run test --code-coverage --json`."""
    payload = {
        "summary": {"outcome": "Failed" if failing else "Passed", "failing": failing},
        "tests": [],
        "coverage": {
            "coverage": [
                {"id": f"01p{i}", "name": name, "totalLines": total, "totalCovered": covered}
                for i, (name, covered, total) in enumerate(classes)
            ]
        },
    }
    return {"status": 0, "result": payload} if wrapped else payload


class EvaluateTest(unittest.TestCase):
    def test_passes_at_threshold(self):
        result = cc.evaluate(report([("A", 75, 100)])["result"], threshold=75)
        self.assertTrue(result.passed)
        self.assertAlmostEqual(result.org_wide, 75.0)

    def test_fails_below_threshold(self):
        result = cc.evaluate(report([("A", 74, 100)])["result"], threshold=75)
        self.assertFalse(result.passed)

    def test_org_wide_is_weighted_by_lines(self):
        # 90/100 + 0/10 = 81.8%, although the average of percentages is 45%.
        result = cc.evaluate(report([("Big", 90, 100), ("Small", 0, 10)])["result"])
        self.assertTrue(result.passed)
        self.assertAlmostEqual(result.org_wide, 90 * 100 / 110)

    def test_per_class_threshold(self):
        data = report([("Big", 90, 100), ("Small", 0, 10)])["result"]
        result = cc.evaluate(data, per_class_threshold=75)
        self.assertFalse(result.passed)
        self.assertEqual([c.name for c in result.below_threshold], ["Small"])

    def test_exclude_pattern(self):
        data = report([("Big", 90, 100), ("Legacy_Small", 0, 10)])["result"]
        result = cc.evaluate(data, per_class_threshold=75, exclude=["Legacy_*"])
        self.assertTrue(result.passed)
        self.assertEqual([c.name for c in result.classes], ["Big"])

    def test_failing_tests_fail_gate(self):
        result = cc.evaluate(report([("A", 100, 100)], failing=2)["result"])
        self.assertFalse(result.passed)
        self.assertEqual(result.failing_tests, 2)

    def test_empty_report_passes_by_default(self):
        result = cc.evaluate(report([])["result"])
        self.assertTrue(result.passed)
        self.assertIsNone(result.org_wide)

    def test_empty_report_fails_when_requested(self):
        result = cc.evaluate(report([])["result"], fail_on_empty=True)
        self.assertFalse(result.passed)

    def test_covered_lines_counted_from_line_map(self):
        data = {"coverage": {"coverage": [{"name": "A", "totalLines": 4, "lines": {"1": 1, "2": 0, "3": 3, "4": 0}}]}}
        self.assertEqual(cc.parse_classes(data)[0].covered, 2)

    def test_failing_counted_from_tests_without_summary(self):
        data = {"tests": [{"Outcome": "Pass"}, {"Outcome": "Fail"}]}
        self.assertEqual(cc.failing_tests(data), 1)


class MainTest(unittest.TestCase):
    def run_main(self, payload, *args, env=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            old = {k: cc.os.environ.get(k) for k in ("COVERAGE_THRESHOLD", "GITHUB_STEP_SUMMARY")}
            try:
                for key in old:
                    cc.os.environ.pop(key, None)
                cc.os.environ.update(env or {})
                return cc.main([str(path), *args])
            finally:
                for key, value in old.items():
                    if value is None:
                        cc.os.environ.pop(key, None)
                    else:
                        cc.os.environ[key] = value

    def test_exit_codes(self):
        self.assertEqual(self.run_main(report([("A", 80, 100)])), 0)
        self.assertEqual(self.run_main(report([("A", 70, 100)])), 1)

    def test_unwrapped_report(self):
        self.assertEqual(self.run_main(report([("A", 80, 100)], wrapped=False)), 0)

    def test_threshold_from_cli_and_env(self):
        data = report([("A", 80, 100)])
        self.assertEqual(self.run_main(data, "--threshold", "85"), 1)
        self.assertEqual(self.run_main(data, env={"COVERAGE_THRESHOLD": "85"}), 1)
        self.assertEqual(self.run_main(data, "--threshold", "70", env={"COVERAGE_THRESHOLD": "85"}), 0)

    def test_writes_step_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.md"
            self.run_main(report([("A", 80, 100)]), env={"GITHUB_STEP_SUMMARY": str(summary)})
            self.assertIn("Apex coverage gate", summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
