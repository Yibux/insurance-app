## Summary

<!-- What and why, 1–3 sentences. -->

Closes #

## Requirements

<!-- e.g. FR-CLM-02, NFR-SEC-03 -->

## Checklist

- [ ] Conventional Commit title, e.g. `feat(claims): … (#nr)`
- [ ] Tests added/updated; CI green (coverage ≥ 75%, Code Analyzer, gitleaks, CodeQL)
- [ ] Apex: `with sharing`, `WITH USER_MODE` / `stripInaccessible`, no SOQL/DML in loops, binds in dynamic SOQL
- [ ] LWC: no unsafe `innerHTML`, input validated
- [ ] No secrets, credentials or real personal data committed
- [ ] Implementation log entry in `docs/implementacja/`
- [ ] ADR added (if a decision was made)
- [ ] README / runbook updated (if setup changed)
