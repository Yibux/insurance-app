# Shared rules for insurance-app agents

Every agent in `.claude/agents/` reads this file first. Project context:
master's thesis "Secure insurance system with DevSecOps on Salesforce".
Repository `Yibux/insurance-app` (public), monorepo: Salesforce metadata in
`force-app/`, Python backend in `integration-server/` (from M4), CI in
`.github/workflows/`, documentation in `docs/`.

## Sources of truth

- `docs/KONWENCJE.md` — branches, Conventional Commits, Definition of Done,
  implementation-log template.
- `docs/WYMAGANIA.md` — FR/NFR requirement IDs and traceability matrix.
- `docs/HARMONOGRAM.md` — stages M0–M8, tech stack.
- `docs/adr/` — decisions already made; do not re-litigate them, write a new
  ADR that supersedes one if a decision really changes.
- `docs/implementacja/M<n>-*.md` — implementation log per stage.
- GitHub issues/PRs (`gh issue view N`, `gh pr list`) — task status.

## Language

- Code, commit messages, PR titles/descriptions, issue comments: **English**.
- Everything in `docs/` (logs, ADRs, spikes, runbooks, thesis chapters):
  **Polish**.

## Git and PRs

- Branch from an up-to-date `main` (`git fetch && git switch main && git pull`).
  If the work depends on an open PR or touches the same files (same workflow,
  same `docs/implementacja/M<n>` file, `docs/adr/README.md`), stack the branch
  on that PR's branch and state the merge order in the PR description.
- A PR with a merge conflict gets **no `pull_request` workflow runs** at all —
  merge `main` (or the base PR branch) in and push before expecting CI.
- PR body follows `.github/pull_request_template.md`, includes `Closes #N`,
  requirement IDs and links to CI runs as evidence.
- **No attribution footers** (no `Co-Authored-By`, no "Generated with").
- **Never merge PRs, never force-push, never push to `main`, never delete
  branches** — the user does that.
- Docs-only follow-up commits on a PR that touches `force-app/` get
  `[skip ci]` in the message to save scratch orgs.

## Salesforce limits (Developer Edition Dev Hub)

- **6 new scratch orgs per rolling 24 h, 3 active.** Every push to a PR that
  touches `force-app/`, `config/`, `sfdx-project.json`,
  `scripts/ci/check_coverage.py` or the scratch-org workflow costs one org.
- Only one agent at a time may push changes that trigger the scratch-org
  workflow. Batch commits locally and push once.
- To exercise a gate (Code Analyzer, coverage, gitleaks), put temporary probes
  **outside** `force-app/` when possible, and remove them before handing over.
- `LIMIT_EXCEEDED` on scratch org creation is not a code bug — report it and
  ask for a re-run later.
- Local `sf` CLI (2.78) and Node (21) are too old for scratch-org signup via
  the JWT Dev Hub (error C-1016 workaround needs CLI ≥ 2.15x / Node 22).
  Verify org-dependent behaviour in CI.

## Secrets and data

- Never print, commit or paste secrets, keys, tokens or real personal data.
  JWT key lives outside the repo (`~/.sf-keys/insurance-app/`), CI secrets in
  the GitHub Environment `devhub`.
- Never commit a fake secret either (it would break the full-history gitleaks
  scan) — generate canaries at runtime.

## Reporting back

Finish with: what changed (files/PR URL), what was verified and how (run
links), what was **not** verified, and any decision the user must make.
Do not claim CI is green without having seen the run.
