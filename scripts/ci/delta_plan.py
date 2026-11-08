#!/usr/bin/env python3
"""Choose between delta and full deployment for scratch org validation.

Compares the pull request head with its base commit and prints a plan: either
``delta`` (deploy only the changed UI metadata) or ``full`` (deploy
``force-app`` as before). Every doubtful case selects ``full``; see
docs/adr/0011-delta-deployment.md for the rules and the reasoning.

The base commit comes from the ``BASE_SHA`` environment variable (the
``github.event.pull_request.base.sha`` context value) and is validated as a
40-character hex string. No branch name, title or other free text from the pull
request is used. File names in the diff are untrusted: they are read
NUL-delimited, never echoed to ``GITHUB_OUTPUT`` and never passed through a
shell.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

SOURCE_ROOT = "force-app"

# Changes to any of these affect how every deployment or gate behaves, so they
# always select a full deployment.
SHARED_PATHS = (
    "sfdx-project.json",
    ".forceignore",
    "config/",
    "scripts/ci/check_coverage.py",
    "scripts/ci/gate_report.py",
    "scripts/ci/delta_plan.py",
    ".github/actions/gate-durations/",
    ".github/workflows/scratch-org-validation.yml",
)

# Metadata folders (under force-app/main/default/) eligible for a delta deploy.
# They are self-contained bundles that Apex tests cannot depend on, so a change
# confined to them may skip the Apex tests and the coverage gate. Everything
# else (classes, triggers, objects, flows, permission sets, ...) can change test
# outcomes and forces a full deployment. Experience Cloud metadata
# (digitalExperiences, networks, sites, ...) is deliberately absent: a bundle
# deployed alone is rejected by an empty scratch org ("workspace doesn't
# exist", observed in CI run 42505086736).
DELTA_ELIGIBLE_FOLDERS = frozenset({"lwc", "aura"})

MAX_CHANGED_FILES = 200
MAX_CHANGED_RATIO = 0.5

# Mirrors .forceignore: files the CLI never deploys.
IGNORED_BASENAMES = frozenset({"package.xml", "jsconfig.json", ".eslintrc.json"})
IGNORED_DIRS = frozenset({"__tests__"})

BASE_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SOURCE_PATH_PATTERN = re.compile(rf"^{SOURCE_ROOT}/main/default/([^/]+)/")


@dataclass(frozen=True)
class Change:
    status: str  # single letter: A, M, D, T, U, ...
    path: str


@dataclass(frozen=True)
class Plan:
    mode: str  # "delta" or "full"
    reason: str
    paths: tuple[str, ...] = ()


def parse_name_status(raw: bytes) -> list[Change]:
    """Parse ``git diff --name-status -z``. Renames and copies are split into a
    deletion of the old path and an addition of the new one."""
    tokens = [t.decode("utf-8", "surrogateescape") for t in raw.split(b"\0") if t]
    changes: list[Change] = []
    index = 0
    while index < len(tokens):
        status = tokens[index]
        if status[0] in "RC":
            old, new = tokens[index + 1], tokens[index + 2]
            changes += [Change("D" if status[0] == "R" else "M", old), Change("A", new)]
            index += 3
        else:
            changes.append(Change(status[0], tokens[index + 1]))
            index += 2
    return changes


def is_ignored(path: str) -> bool:
    pure = PurePosixPath(path)
    return pure.name in IGNORED_BASENAMES or any(part in IGNORED_DIRS for part in pure.parts)


def is_shared(path: str) -> bool:
    return any(path == s or (s.endswith("/") and path.startswith(s)) for s in SHARED_PATHS)


def plan(changes: list[Change], tracked_source_files: int) -> Plan:
    if any(is_shared(c.path) for c in changes):
        return Plan("full", "shared configuration, workflow or gate script changed")

    source = [c for c in changes if c.path.startswith(SOURCE_ROOT + "/") and not is_ignored(c.path)]
    if not source:
        return Plan("full", "empty delta (no deployable change under force-app)")
    if any(c.status not in ("A", "M") for c in source):
        return Plan("full", "component deleted, renamed or type-changed")
    if len(source) > MAX_CHANGED_FILES:
        return Plan("full", f"large delta ({len(source)} files > {MAX_CHANGED_FILES})")
    if tracked_source_files and len(source) / tracked_source_files > MAX_CHANGED_RATIO:
        return Plan("full", f"large delta ({len(source)} of {tracked_source_files} files)")
    for change in source:
        match = SOURCE_PATH_PATTERN.match(change.path)
        if not match or match.group(1) not in DELTA_ELIGIBLE_FOLDERS:
            return Plan("full", "change can affect Apex tests (not UI-only metadata)")
    return Plan("delta", f"{len(source)} UI-only file(s) changed", tuple(c.path for c in source))


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def collect(base_sha: str) -> tuple[list[Change], int]:
    git("fetch", "--no-tags", "--depth=1", "origin", base_sha)
    diff = git("diff", "--name-status", "-z", "--no-renames", base_sha, "HEAD")
    tracked = [p for p in git("ls-files", "-z", "--", SOURCE_ROOT).split(b"\0") if p]
    deployable = [p for p in tracked if not is_ignored(p.decode("utf-8", "surrogateescape"))]
    return parse_name_status(diff), len(deployable)


def decide(event_name: str, base_sha: str) -> Plan:
    if event_name != "pull_request":
        return Plan("full", "not a pull_request event")
    if not BASE_SHA_PATTERN.match(base_sha):
        return Plan("full", "base commit unknown or malformed")
    try:
        changes, tracked = collect(base_sha)
        return plan(changes, tracked)
    except Exception as error:  # any tool failure must fall back to a full deploy
        return Plan("full", f"delta planning failed ({type(error).__name__})")


def write_outputs(result: Plan, paths_file: Path) -> None:
    paths_file.parent.mkdir(parents=True, exist_ok=True)
    paths_file.write_bytes(b"".join(p.encode("utf-8", "surrogateescape") + b"\0" for p in result.paths))
    lines = [f"mode={result.mode}", f"reason={result.reason}", f"files={len(result.paths)}"]
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(f"### Deployment plan: {result.mode}\n\n- {result.reason}\n")
            if result.mode == "delta":
                handle.write(f"- files in delta: {len(result.paths)}\n")
    print("\n".join(lines))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--paths-file", type=Path, required=True, help="NUL-delimited list of delta paths")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    result = decide(os.environ.get("EVENT_NAME", ""), os.environ.get("BASE_SHA", ""))
    write_outputs(result, args.paths_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
