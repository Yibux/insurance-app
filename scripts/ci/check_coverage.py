#!/usr/bin/env python3
"""Apex code coverage gate for CI.

Reads the JSON written by
``sf apex run test --code-coverage --result-format json`` and exits with
status 1 when tests failed or coverage is below the threshold.

The platform enforces 75% only on production deployments, so scratch org
validation needs its own gate (NFR-QA-01).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_THRESHOLD = 75.0


@dataclass(frozen=True)
class ClassCoverage:
    name: str
    covered: int
    total: int

    @property
    def percent(self) -> float:
        return 100.0 if self.total == 0 else self.covered * 100.0 / self.total


@dataclass(frozen=True)
class GateResult:
    passed: bool
    org_wide: float | None
    failing_tests: int
    below_threshold: list[ClassCoverage]
    classes: list[ClassCoverage]
    messages: list[str]


def load_report(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    # `sf --json` wraps the payload in {"status": …, "result": …};
    # `--result-format json --output-dir` writes the bare result.
    return data.get("result", data)


def parse_classes(report: dict) -> list[ClassCoverage]:
    coverage = report.get("coverage") or {}
    entries = coverage.get("coverage") or []
    classes = []
    for entry in entries:
        total = int(entry.get("totalLines", 0))
        covered = entry.get("totalCovered")
        if covered is None:
            covered = sum(1 for hit in (entry.get("lines") or {}).values() if hit)
        classes.append(ClassCoverage(entry["name"], int(covered), total))
    return classes


def failing_tests(report: dict) -> int:
    summary = report.get("summary") or {}
    if "failing" in summary:
        return int(summary["failing"])
    return sum(1 for test in report.get("tests") or [] if test.get("Outcome") != "Pass")


def source_class_names(source_dir: Path) -> set[str]:
    """Names of Apex classes kept in the repository (``*.cls`` files)."""
    return {path.stem for path in source_dir.rglob("*.cls")}


def evaluate(
    report: dict,
    threshold: float = DEFAULT_THRESHOLD,
    per_class_threshold: float | None = None,
    exclude: list[str] | None = None,
    fail_on_empty: bool = False,
    only: set[str] | None = None,
) -> GateResult:
    exclude = exclude or []
    classes = [
        c
        for c in parse_classes(report)
        if (only is None or c.name in only) and not any(fnmatch.fnmatch(c.name, p) for p in exclude)
    ]
    failed = failing_tests(report)
    messages: list[str] = []
    passed = True

    if failed:
        passed = False
        messages.append(f"{failed} Apex test(s) failed.")

    total = sum(c.total for c in classes)
    if total == 0:
        org_wide = None
        if fail_on_empty:
            passed = False
            messages.append("No Apex code coverage data found.")
        else:
            messages.append("No Apex classes to cover; coverage gate skipped.")
    else:
        org_wide = sum(c.covered for c in classes) * 100.0 / total
        if org_wide < threshold:
            passed = False
            messages.append(f"Org-wide coverage {org_wide:.2f}% is below {threshold:g}%.")
        else:
            messages.append(f"Org-wide coverage {org_wide:.2f}% meets {threshold:g}%.")

    below: list[ClassCoverage] = []
    if per_class_threshold is not None:
        below = [c for c in classes if c.total and c.percent < per_class_threshold]
        if below:
            passed = False
            names = ", ".join(f"{c.name} ({c.percent:.2f}%)" for c in below)
            messages.append(f"Classes below {per_class_threshold:g}%: {names}.")

    return GateResult(passed, org_wide, failed, below, classes, messages)


def render_markdown(result: GateResult, threshold: float) -> str:
    status = "✅ passed" if result.passed else "❌ failed"
    lines = [f"### Apex coverage gate: {status}", ""]
    lines += [f"- {m}" for m in result.messages]
    if result.classes:
        lines += ["", "| Class | Covered | Lines | Coverage |", "| --- | ---: | ---: | ---: |"]
        for c in sorted(result.classes, key=lambda c: c.percent):
            flag = " ⚠️" if c.total and c.percent < threshold else ""
            lines.append(f"| `{c.name}` | {c.covered} | {c.total} | {c.percent:.2f}%{flag} |")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    env_threshold = os.environ.get("COVERAGE_THRESHOLD")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report", type=Path, help="JSON from sf apex run test --code-coverage")
    parser.add_argument(
        "--threshold",
        type=float,
        default=float(env_threshold) if env_threshold else DEFAULT_THRESHOLD,
        help="minimum org-wide coverage in percent (default: $COVERAGE_THRESHOLD or 75)",
    )
    parser.add_argument(
        "--per-class-threshold",
        type=float,
        help="also require every class to reach this coverage",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="class name glob to ignore (repeatable)",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="count only classes whose .cls file is in this directory, ignoring "
        "classes the platform adds to the org (e.g. Experience Cloud controllers)",
    )
    parser.add_argument(
        "--fail-on-empty",
        action="store_true",
        help="fail when the report has no coverage data",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = evaluate(
        load_report(args.report),
        threshold=args.threshold,
        per_class_threshold=args.per_class_threshold,
        exclude=args.exclude,
        fail_on_empty=args.fail_on_empty,
        only=source_class_names(args.source_dir) if args.source_dir else None,
    )
    summary = render_markdown(result, args.per_class_threshold or args.threshold)
    print(summary)
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as handle:
            handle.write(summary)
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
