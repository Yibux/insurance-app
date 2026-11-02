# Architecture Decision Records

Każda istotna decyzja architektoniczna lub wybór narzędzia to jeden plik `NNNN-tytul.md` na bazie [0000-template.md](0000-template.md). Numeracja rosnąca; plików nie usuwamy — zmienioną decyzję oznaczamy jako „zastąpiona przez”.

| Nr                                    | Tytuł                                                                    | Status   |
| ------------------------------------- | ------------------------------------------------------------------------ | -------- |
| [0001](0001-monorepo.md)              | Monorepo dla metadanych Salesforce, backendu Python i potoku CI/CD       | przyjęta |
| [0002](0002-custom-objects-vs-fsc.md) | Własne obiekty custom zamiast modelu danych Financial Services Cloud     | przyjęta |
| [0003](0003-jwt-bearer-ci-auth.md)    | Uwierzytelnianie CI w Dev Hubie przez JWT Bearer Flow                    | przyjęta |
| [0004](0004-code-analyzer-rules.md)   | Dobór reguł Salesforce Code Analyzer i próg blokowania PR                | przyjęta |
| [0005](0005-codeql-workflow.md)       | CodeQL jako osobny workflow z pakietem `security-extended`               | przyjęta |
| [0006](0006-dependabot-npm-audit.md)  | Dependabot (npm, github-actions) i bramka `npm audit --audit-level=high` | przyjęta |
