# Hooki Git (Husky)

Dotyczy #23 (FR-CI-09). Hooki instalują się automatycznie po `npm install` (skrypt `prepare` → `husky`).

| Hook         | Co robi                                                                                         | Skutek błędu     |
| ------------ | ----------------------------------------------------------------------------------------------- | ---------------- |
| `pre-commit` | gitleaks na zmianach w stage, potem lint-staged: Prettier (`--write`) i ESLint dla `aura`/`lwc` | commit przerwany |
| `commit-msg` | commitlint: Conventional Commits, typy z [KONWENCJE](../KONWENCJE.md)                           | commit przerwany |

Format komunikatu: `typ(zakres): opis (#nr)`; typy: `feat`, `fix`, `chore`, `docs`, `test`, `ci`, `refactor`, `build`, `security`. Konfiguracja: `commitlint.config.js`.

Ręczne sprawdzenie komunikatu:

```bash
echo "feat(claims): add guard (#42)" | npx --no commitlint
```

## Gdy hook nie działa

- Hook nie uruchamia się: sprawdź `git config core.hooksPath` (powinno być `.husky/_`); napraw przez `npm run prepare`.
- Brak gitleaks: skan jest pomijany z ostrzeżeniem, instalacja w [skanowanie-sekretow.md](skanowanie-sekretow.md).
- Pominięcie hooków (`--no-verify`) nie omija CI — te same kontrole biegną w `pr-validation.yml`.
