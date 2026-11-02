# 0007. Hooki Git: Husky + lint-staged + gitleaks (pre-commit) i commitlint (commit-msg)

- **Status:** przyjęta
- **Data:** 2026-11-02
- **Issue:** #23
- **Wymagania:** FR-CI-09

## Kontekst

FR-CI-09 wymaga lokalnego formatowania, lintu i skanu sekretów przed commitem. Husky, lint-staged (Prettier, ESLint) i hook gitleaks istniały już po #19; brakowało walidacji komunikatów commitów, choć `docs/KONWENCJE.md` wymaga Conventional Commits.

## Rozważane opcje

1. **Tylko walidacja w CI (tytuł PR / commity)** — późna informacja zwrotna, a przy squash merge liczy się tytuł PR, nie pojedyncze commity.
2. **commitlint w hooku `commit-msg` (Husky)** — wybrane: natychmiastowa informacja, ta sama infrastruktura Husky co pre-commit.
3. **Własny skrypt shell z regexem** — odrzucone: commitlint ma gotową konfigurację `config-conventional` i czytelne komunikaty.

## Decyzja

- `.husky/pre-commit`: `scripts/hooks/gitleaks-staged.sh`, potem `lint-staged` (Prettier `--write`, ESLint na plikach `aura`/`lwc`).
- `.husky/commit-msg`: `npx --no -- commitlint --edit "$1"` z `commitlint.config.js` (`@commitlint/config-conventional`).
- Dozwolone typy z KONWENCJE: `feat`, `fix`, `chore`, `docs`, `test`, `ci`, `refactor`, `build`, `security`; limit nagłówka 100 znaków; wielkość liter tematu nie jest wymuszana. Numer issue w nagłówku **nie** jest wymuszany (commity merge, Dependabota i docs-only go nie mają).
- Domyślnie ignorowane przez commitlint są commity `Merge …`.

## Konsekwencje

- Hooki są obchodliwe (`git commit --no-verify`), więc nie są bramką bezpieczeństwa — bramką pozostaje CI (gitleaks na całej historii, ESLint, Prettier). Hooki skracają pętlę zwrotną.
- Brak gitleaks lokalnie: skan jest pomijany z ostrzeżeniem (decyzja z #19).
- Walidacja tytułu PR/commitów w CI nie została dodana (poza zakresem #23); przy squash merge format tytułu PR nadal zależy od autora.
- Nowe zależności deweloperskie: `@commitlint/cli`, `@commitlint/config-conventional` (objęte `npm audit` i Dependabotem).
