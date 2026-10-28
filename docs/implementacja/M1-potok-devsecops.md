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

### #15 Authenticate CI to Dev Hub with JWT Bearer Flow

- **Data:** 2026-10-29 · **PR:** #<nr> · **Wymagania:** NFR-SEC-05, NFR-SEC-06
- **Co zrobiono:** Workflow `scratch-org-validation.yml` loguje się do Dev Hubu przez JWT Bearer Flow z użyciem sekretów środowiska `devhub` (konfiguracja z #7). Klucz prywatny istnieje na dysku runnera tylko na czas logowania.
- **Jak:** job z `environment: devhub`; klucz zapisywany do `$RUNNER_TEMP/devhub.key` z `umask 077`, `sf org login jwt …`, natychmiastowe `rm`, a dodatkowo `rm` i `sf org logout --all` w krokach `if: always()`. Wyjście komend logowania przekierowane do `/dev/null`; sekrety są dodatkowo maskowane przez GitHub.
- **Decyzje i alternatywy:** sekrety środowiska zamiast repozytorium ([ADR 0003](../adr/0003-jwt-bearer-ci-auth.md)); wersja `sf` CLI przypięta (`SF_CLI_VERSION`) i instalowana z `--ignore-scripts`; wyłączona telemetria i autoaktualizacja CLI.
- **Problemy:** kontekst `runner` nie jest dostępny w `env` na poziomie joba — ścieżka klucza przez zmienną powłoki `$RUNNER_TEMP`.
- **Dowody:** <!-- link do przebiegu: krok „Authenticate to Dev Hub (JWT Bearer)” bez danych uwierzytelniających w logu -->
- **Do pracy:** rozdział #84 (JWT w CI), #83 (zarządzanie sekretami w potoku).

### #16 Create, deploy to and always delete a scratch org per PR

- **Data:** 2026-10-29 · **PR:** #<nr> · **Wymagania:** FR-CI-02, NFR-PERF-05
- **Co zrobiono:** Dla każdego PR zmieniającego metadane Salesforce powstaje efemeryczny scratch org (1 dzień, unikalny alias), do którego wdrażane są źródła; błąd deployu oblewa job. Org jest usuwany w kroku `always()`, także po błędzie lub anulowaniu.
- **Jak:** `.github/workflows/scratch-org-validation.yml`: `sf org create scratch --duration-days 1`, alias `pr-<nr>-<run_id>-<attempt>`; `SF_SITE_ADMIN_USERNAME` ustawiana z `sf org display` (wymóg ze spike'a #8); `sf project deploy start`; `sf org delete scratch` w `if: always()`.
- **Decyzje i alternatywy:**
  - Osobny workflow od `pr-validation.yml` z filtrem `paths:` (`force-app/`, `config/`, `sfdx-project.json`) — zmiany w dokumentacji nie zużywają limitu 6 scratch orgów dziennie ([ADR 0001](../adr/0001-monorepo.md)).
  - Dwa poziomy `concurrency`: per PR z `cancel-in-progress` (nowy push anuluje stary przebieg) oraz globalna grupa `devhub-scratch-org` na poziomie joba — w danej chwili działa najwyżej jeden job tworzący scratch org (limit 3 aktywnych).
  - Alternatywa: pula długo żyjących scratch orgów współdzielona między PR-ami — odrzucona, bo łamie izolację (stan z poprzedniego PR) i główną tezę o środowiskach efemerycznych.
- **Problemy:** <!-- uzupełnić po pierwszych przebiegach -->
- **Dowody:** <!-- link do przebiegu: czasy kroków create / deploy / delete -->
- **Do pracy:** rozdział #84 (środowiska efemeryczne), pomiar czasu potoku w eksperymencie (M6, NFR-PERF-05).
