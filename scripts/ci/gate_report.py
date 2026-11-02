#!/usr/bin/env python3
"""Markdown reports for the CI job summary (FR-CI-07, NFR-OBS-02).

Sub-commands, each printing Markdown and appending it to
``$GITHUB_STEP_SUMMARY`` when that variable is set:

* ``apex-tests REPORT``  - Apex test results from ``sf apex run test --json``
* ``code-analyzer REPORT`` - violation counts from the Code Analyzer JSON
* ``durations JOBS_JSON`` - per-step durations from the Actions jobs API

All commands tolerate a missing input file: a report that was never produced
(for example because an earlier step failed) must not hide the original error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SEVERITY_NAMES = {1: "Critical", 2: "High", 3: "Moderate", 4: "Low", 5: "Info"}


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def render_apex_tests(data: dict | None) -> str:
    if data is None:
        return "### Apex test results\n\nNo test report was produced.\n"
    report = data.get("result", data)
    summary = report.get("summary") or {}
    tests = report.get("tests") or []
    passing = int(summary.get("passing", sum(1 for t in tests if t.get("Outcome") == "Pass")))
    failing = int(summary.get("failing", sum(1 for t in tests if t.get("Outcome") in ("Fail", "CompileFail"))))
    skipped = int(summary.get("skipped", 0))
    ran = int(summary.get("testsRan", passing + failing + skipped))
    status = "passed" if failing == 0 else "failed"
    lines = [
        f"### Apex test results: {status}",
        "",
        "| Tests run | Passing | Failing | Skipped | Test time | Org-wide coverage |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| {ran} | {passing} | {failing} | {skipped} | "
        f"{summary.get('testTotalTime', 'n/a')} | {summary.get('orgWideCoverage', 'n/a')} |",
    ]
    failed = [t for t in tests if t.get("Outcome") not in (None, "Pass")]
    if failed:
        lines += ["", "| Failed test | Message |", "| --- | --- |"]
        for test in failed:
            first_line = (str(test.get("Message") or "").splitlines() or [""])[0]
            lines.append(f"| `{test.get('FullName', 'unknown')}` | {first_line.replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def count_violations(data: dict) -> dict[int, int]:
    """Counts per severity, from ``violationCounts`` or the violation list."""
    counts = data.get("violationCounts")
    if isinstance(counts, dict) and any(f"sev{n}" in counts for n in SEVERITY_NAMES):
        return {n: int(counts.get(f"sev{n}", 0)) for n in SEVERITY_NAMES}
    result = {n: 0 for n in SEVERITY_NAMES}
    for violation in data.get("violations") or []:
        severity = int(violation.get("severity", 5))
        result[severity] = result.get(severity, 0) + 1
    return result


def render_code_analyzer(data: dict | None, threshold: int | None) -> str:
    if data is None:
        return "### Code Analyzer\n\nNo report was produced.\n"
    counts = count_violations(data)
    total = sum(counts.values())
    lines = ["### Code Analyzer violations", "", "| Severity | Count |", "| --- | ---: |"]
    lines += [f"| {n} - {name} | {counts.get(n, 0)} |" for n, name in SEVERITY_NAMES.items()]
    lines.append(f"| **Total** | **{total}** |")
    if threshold is not None:
        blocking = sum(c for n, c in counts.items() if n <= threshold)
        verdict = "blocking" if blocking else "none blocking"
        lines += ["", f"Severity threshold {threshold}: {blocking} violation(s) at or above it ({verdict})."]
    return "\n".join(lines) + "\n"


def _seconds(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None

    def parse(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    return (parse(end) - parse(start)).total_seconds()


def step_durations(data: dict, job_name: str | None) -> list[dict]:
    """Flat list of ``{job, step, seconds}`` rows from the jobs API payload."""
    rows = []
    for job in data.get("jobs") or []:
        if job_name and job.get("name") != job_name:
            continue
        # The calling job is still running when this report is built, so its
        # total is the time elapsed up to this step.
        end = job.get("completed_at") or datetime.now(timezone.utc).isoformat()
        rows.append({"job": job["name"], "step": "(job total)", "seconds": _seconds(job.get("started_at"), end)})
        for step in job.get("steps") or []:
            if step.get("conclusion") == "skipped":
                continue
            seconds = _seconds(step.get("started_at"), step.get("completed_at"))
            rows.append({"job": job["name"], "step": step["name"], "seconds": seconds})
    return rows


def render_durations(rows: list[dict]) -> str:
    lines = ["### Gate durations", "", "| Job | Step | Duration |", "| --- | --- | ---: |"]
    for row in rows:
        seconds = row["seconds"]
        shown = "running" if seconds is None else f"{seconds:.0f} s"
        lines.append(f"| {row['job']} | {row['step']} | {shown} |")
    return "\n".join(lines) + "\n"


def emit(markdown: str) -> None:
    print(markdown)
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if target:
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(markdown + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("apex-tests").add_argument("report", type=Path)
    ca = sub.add_parser("code-analyzer")
    ca.add_argument("report", type=Path)
    ca.add_argument("--severity-threshold", type=int)
    du = sub.add_parser("durations")
    du.add_argument("jobs_json", type=Path)
    du.add_argument("--job-name")
    du.add_argument("--output", type=Path, help="also write the rows as JSON")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    if args.command == "apex-tests":
        emit(render_apex_tests(load_json(args.report)))
    elif args.command == "code-analyzer":
        emit(render_code_analyzer(load_json(args.report), args.severity_threshold))
    else:
        data = load_json(args.jobs_json) or {}
        rows = step_durations(data, args.job_name)
        if args.output:
            args.output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        emit(render_durations(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
