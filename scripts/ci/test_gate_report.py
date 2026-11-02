import json
import tempfile
import unittest
from pathlib import Path

import gate_report as gr


class ApexTestsTest(unittest.TestCase):
    def test_missing_report(self):
        self.assertIn("No test report", gr.render_apex_tests(None))

    def test_summary_and_failures(self):
        data = {
            "result": {
                "summary": {
                    "passing": 3,
                    "failing": 1,
                    "skipped": 0,
                    "testsRan": 4,
                    "testTotalTime": "120 ms",
                    "orgWideCoverage": "80%",
                },
                "tests": [
                    {"Outcome": "Pass", "FullName": "A.ok"},
                    {"Outcome": "Fail", "FullName": "A.bad", "Message": "boom | pipe\nstack"},
                ],
            }
        }
        out = gr.render_apex_tests(data)
        self.assertIn("failed", out)
        self.assertIn("| 4 | 3 | 1 | 0 | 120 ms | 80% |", out)
        self.assertIn("`A.bad` | boom / pipe", out)


class CodeAnalyzerTest(unittest.TestCase):
    def test_counts_from_violation_counts(self):
        data = {"violationCounts": {"total": 3, "sev1": 0, "sev2": 1, "sev3": 2}}
        out = gr.render_code_analyzer(data, 2)
        self.assertIn("| 2 - High | 1 |", out)
        self.assertIn("**3**", out)
        self.assertIn("1 violation(s) at or above", out)

    def test_counts_from_violation_list(self):
        counts = gr.count_violations({"violations": [{"severity": 1}, {"severity": 4}, {"severity": 4}]})
        self.assertEqual((counts[1], counts[4]), (1, 2))

    def test_missing_report(self):
        self.assertIn("No report", gr.render_code_analyzer(None, 2))


class DurationsTest(unittest.TestCase):
    JOBS = {
        "jobs": [
            {
                "name": "Gate",
                "started_at": "2026-11-02T10:00:00Z",
                "completed_at": None,
                "steps": [
                    {
                        "name": "Checkout",
                        "conclusion": "success",
                        "started_at": "2026-11-02T10:00:01Z",
                        "completed_at": "2026-11-02T10:00:04Z",
                    },
                    {"name": "Skipped", "conclusion": "skipped", "started_at": None, "completed_at": None},
                    {
                        "name": "Summary",
                        "conclusion": None,
                        "started_at": "2026-11-02T10:01:00Z",
                        "completed_at": None,
                    },
                ],
            },
            {"name": "Other", "steps": []},
        ]
    }

    def test_filters_job_and_skips_skipped(self):
        rows = gr.step_durations(self.JOBS, "Gate")
        self.assertEqual([r["step"] for r in rows], ["(job total)", "Checkout", "Summary"])
        self.assertEqual(rows[1]["seconds"], 3)
        self.assertIsNone(rows[2]["seconds"])

    def test_render(self):
        out = gr.render_durations(gr.step_durations(self.JOBS, "Gate"))
        self.assertIn("| Gate | Checkout | 3 s |", out)
        self.assertIn("running", out)

    def test_main_writes_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp, "jobs.json"), Path(tmp, "out.json")
            src.write_text(json.dumps(self.JOBS), encoding="utf-8")
            gr.main(["durations", str(src), "--job-name", "Gate", "--output", str(dst)])
            self.assertEqual(len(json.loads(dst.read_text(encoding="utf-8"))), 3)


if __name__ == "__main__":
    unittest.main()
