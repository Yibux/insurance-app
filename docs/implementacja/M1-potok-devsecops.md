# Etap 1 — Potok DevSecOps

Wpisy dodawane po zamknięciu każdego zadania etapu (szablon: [KONWENCJE.md](../KONWENCJE.md#szablon-wpisu-implementacyjnego)).

<!-- Nowe wpisy poniżej, od najstarszego. -->

### #14 Create pr-validation workflow: lint, Prettier check and LWC Jest

- **Data:** 2026-10-29 · **PR:** #<nr> · **Wymagania:** FR-CI-01, NFR-QA-04
- **Co zrobiono:** Dodano pierwszy workflow GitHub Actions `pr-validation.yml`, uruchamiany dla każdego PR do `main`. Job `static-checks` wykonuje ESLint (LWC/Aura), sprawdzenie formatowania Prettierem i testy LWC Jest; błąd dowolnego kroku oblewa PR.
- **Jak:** `.github/workflows/pr-validation.yml`; `actions/setup-node` z cache npm; `npm ci --ignore-scripts`; skrypty `npm run lint`, `npm run prettier:verify`, `npm run test:unit -- --ci`.
- **Decyzje i alternatywy:**
  - Akcje przypięte do pełnego SHA commita (z tagiem w komentarzu) zamiast `@v7` — tag można przesunąć, SHA nie (ochrona łańcucha dostaw, IEEE 2025); aktualizacje SHA przejmie Dependabot (#21).
  - `permissions: contents: read` — najmniejsze uprawnienia `GITHUB_TOKEN`; `persist-credentials: false` przy checkout, żeby token nie został w `.git/config`.
  - `npm ci --ignore-scripts` — instalacja z lockfile bez uruchamiania skryptów instalacyjnych pakietów (i bez hooka Husky, zbędnego w CI).
  - `concurrency` z `cancel-in-progress` — nowy push do PR anuluje poprzedni przebieg.
  - Job jest lekki i biegnie dla każdego PR (bez filtra `paths:`), aby mógł być wymaganym checkiem w branch protection (#25).
- **Problemy:** brak.
- **Dowody:** <!-- link do zielonego przebiegu workflow w PR -->
- **Do pracy:** rozdział #83 (shift-left: te same bramki lokalnie w Husky i w CI), #86 (implementacja potoku).
