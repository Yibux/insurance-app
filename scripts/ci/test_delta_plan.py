import tempfile
import unittest
from pathlib import Path
from unittest import mock

import delta_plan as dp

LWC = "force-app/main/default/lwc/probe/probe.js"
CLS = "force-app/main/default/classes/Foo.cls"


def mod(path):
    return dp.Change("M", path)


class ParseTests(unittest.TestCase):
    def test_simple_and_rename(self):
        raw = b"M\0a.txt\0A\0b.txt\0R100\0old.txt\0new.txt\0"
        self.assertEqual(
            dp.parse_name_status(raw),
            [
                dp.Change("M", "a.txt"),
                dp.Change("A", "b.txt"),
                dp.Change("D", "old.txt"),
                dp.Change("A", "new.txt"),
            ],
        )

    def test_path_with_space_and_newline(self):
        raw = b"M\0force-app/a b\nc.xml\0"
        self.assertEqual(dp.parse_name_status(raw), [dp.Change("M", "force-app/a b\nc.xml")])

    def test_empty(self):
        self.assertEqual(dp.parse_name_status(b""), [])


class PlanTests(unittest.TestCase):
    def test_ui_only_is_delta(self):
        result = dp.plan([mod(LWC), dp.Change("A", "force-app/main/default/sites/S.site-meta.xml")], 100)
        self.assertEqual(result.mode, "delta")
        self.assertEqual(len(result.paths), 2)

    def test_docs_alongside_are_ignored(self):
        result = dp.plan([mod(LWC), mod("docs/x.md")], 100)
        self.assertEqual(result.mode, "delta")
        self.assertEqual(result.paths, (LWC,))

    def test_apex_forces_full(self):
        self.assertEqual(dp.plan([mod(CLS), mod(LWC)], 100).mode, "full")

    def test_objects_force_full(self):
        path = "force-app/main/default/objects/A__c/A__c.object-meta.xml"
        self.assertEqual(dp.plan([mod(path)], 100).mode, "full")

    def test_unknown_layout_forces_full(self):
        self.assertEqual(dp.plan([mod("force-app/other/thing.txt")], 100).mode, "full")

    def test_deletion_and_type_change_force_full(self):
        for status in ("D", "T"):
            with self.subTest(status=status):
                self.assertEqual(dp.plan([dp.Change(status, LWC)], 100).mode, "full")

    def test_shared_paths_force_full(self):
        for path in (
            "sfdx-project.json",
            ".forceignore",
            "config/project-scratch-def.json",
            "scripts/ci/check_coverage.py",
            ".github/actions/gate-durations/action.yml",
            ".github/workflows/scratch-org-validation.yml",
        ):
            with self.subTest(path=path):
                self.assertEqual(dp.plan([mod(LWC), mod(path)], 100).mode, "full")

    def test_empty_and_ignored_only_force_full(self):
        self.assertEqual(dp.plan([], 100).mode, "full")
        ignored = "force-app/main/default/lwc/.eslintrc.json"
        self.assertEqual(dp.plan([mod(ignored)], 100).mode, "full")
        jest = "force-app/main/default/lwc/x/__tests__/x.test.js"
        self.assertEqual(dp.plan([mod(jest)], 100).mode, "full")

    def test_large_delta_forces_full(self):
        many = [mod(f"force-app/main/default/lwc/c{i}/c{i}.js") for i in range(dp.MAX_CHANGED_FILES + 1)]
        self.assertEqual(dp.plan(many, 10_000).mode, "full")
        self.assertEqual(dp.plan([mod(LWC)] * 6, 10).mode, "full")  # 60% of tracked files
        self.assertEqual(dp.plan([mod(LWC)] * 4, 10).mode, "delta")


class DecideTests(unittest.TestCase):
    SHA = "a" * 40

    def test_non_pr_event(self):
        self.assertEqual(dp.decide("push", self.SHA).mode, "full")

    def test_malformed_base(self):
        for value in ("", "main", "abc", self.SHA + "; rm -rf /", "$(id)"):
            with self.subTest(value=value):
                with mock.patch.object(dp, "collect") as collect:
                    self.assertEqual(dp.decide("pull_request", value).mode, "full")
                    collect.assert_not_called()

    def test_tool_failure_falls_back(self):
        with mock.patch.object(dp, "collect", side_effect=RuntimeError("boom")):
            result = dp.decide("pull_request", self.SHA)
        self.assertEqual(result.mode, "full")
        self.assertIn("RuntimeError", result.reason)
        self.assertNotIn("boom", result.reason)

    def test_happy_path(self):
        with mock.patch.object(dp, "collect", return_value=([mod(LWC)], 50)):
            self.assertEqual(dp.decide("pull_request", self.SHA).mode, "delta")


class OutputTests(unittest.TestCase):
    def test_paths_file_is_nul_delimited_and_outputs_have_no_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.txt"
            paths_file = Path(tmp) / "sub" / "paths.nul"
            with mock.patch.dict("os.environ", {"GITHUB_OUTPUT": str(out)}, clear=False):
                dp.write_outputs(dp.Plan("delta", "2 UI-only file(s) changed", ("a b", "c\nd")), paths_file)
            self.assertEqual(paths_file.read_bytes(), b"a b\0c\nd\0")
            self.assertEqual(out.read_text(), "mode=delta\nreason=2 UI-only file(s) changed\nfiles=2\n")


if __name__ == "__main__":
    unittest.main()
