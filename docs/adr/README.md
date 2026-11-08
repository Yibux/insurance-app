# Architecture Decision Records

Każda istotna decyzja architektoniczna lub wybór narzędzia to jeden plik `NNNN-tytul.md` na bazie [0000-template.md](0000-template.md). Numeracja rosnąca; plików nie usuwamy — zmienioną decyzję oznaczamy jako „zastąpiona przez”.

| Nr                                                    | Tytuł                                                                                                        | Status   |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------- |
| [0001](0001-monorepo.md)                              | Monorepo dla metadanych Salesforce, backendu Python i potoku CI/CD                                           | przyjęta |
| [0002](0002-custom-objects-vs-fsc.md)                 | Własne obiekty custom zamiast modelu danych Financial Services Cloud                                         | przyjęta |
| [0003](0003-jwt-bearer-ci-auth.md)                    | Uwierzytelnianie CI w Dev Hubie przez JWT Bearer Flow                                                        | przyjęta |
| [0004](0004-code-analyzer-rules.md)                   | Dobór reguł Salesforce Code Analyzer i próg blokowania PR                                                    | przyjęta |
| [0005](0005-codeql-workflow.md)                       | CodeQL jako osobny workflow z pakietem `security-extended`                                                   | przyjęta |
| [0006](0006-dependabot-npm-audit.md)                  | Dependabot (npm, github-actions) i bramka `npm audit --audit-level=high`                                     | przyjęta |
| [0007](0007-hooki-husky-commitlint.md)                | Hooki Git: Husky + lint-staged + gitleaks (pre-commit) i commitlint (commit-msg)                             | przyjęta |
| [0008](0008-github-actions-vs-copado.md)              | GitHub Actions + Salesforce CLI zamiast Copado jako platforma potoku CI/CD                                   | przyjęta |
| [0009](0009-model-wspoldzielenia-rekordow.md)         | Model współdzielenia: agent jako właściciel polisy, Apex managed sharing dla szkód, klient portalu read-only | przyjęta |
| [0010](0010-raporty-bramek-w-podsumowaniu-zadania.md) | Raporty bramek: podsumowanie zadania, artefakty i czasy z API Actions                                        | przyjęta |
| [0011](0011-delta-deployment.md)                      | Delta deployment w walidacji scratch orga: własny diff zamiast sfdx-git-delta, pełny deploy jako domyślny    | przyjęta |
