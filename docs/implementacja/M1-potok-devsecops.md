# Etap 1 — Potok DevSecOps

Wpisy dodawane po zamknięciu każdego zadania etapu (szablon: [KONWENCJE.md](../KONWENCJE.md#szablon-wpisu-implementacyjnego)).

<!-- Nowe wpisy poniżej, od najstarszego. -->

### #14 Create pr-validation workflow: lint, Prettier check and LWC Jest

- **Data:** 2026-10-29 · **PR:** #100 · **Wymagania:** FR-CI-01, NFR-QA-04
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

- **Data:** 2026-10-29 · **PR:** #101 · **Wymagania:** NFR-SEC-05, NFR-SEC-06
- **Co zrobiono:** Workflow `scratch-org-validation.yml` loguje się do Dev Hubu przez JWT Bearer Flow z użyciem sekretów środowiska `devhub` (konfiguracja z #7). Klucz prywatny istnieje na dysku runnera tylko na czas logowania.
- **Jak:** job z `environment: devhub`; klucz zapisywany do `$RUNNER_TEMP/devhub.key` z `umask 077`, `sf org login jwt …`, natychmiastowe `rm`, a dodatkowo `rm` i `sf org logout --all` w krokach `if: always()`. Wyjście komend logowania przekierowane do `/dev/null`; sekrety są dodatkowo maskowane przez GitHub.
- **Decyzje i alternatywy:** sekrety środowiska zamiast repozytorium ([ADR 0003](../adr/0003-jwt-bearer-ci-auth.md)); wersja `sf` CLI przypięta (`SF_CLI_VERSION`) i instalowana z `--ignore-scripts`; wyłączona telemetria i autoaktualizacja CLI.
- **Problemy:**
  - kontekst `runner` nie jest dostępny w `env` na poziomie joba — ścieżka klucza przez zmienną powłoki `$RUNNER_TEMP`;
  - pierwszy przebieg: `client identifier invalid` — w sekrecie `SF_CLIENT_ID` była zła wartość; poprawiono na Consumer Key aplikacji i potwierdzono lokalnym `sf org login jwt`.
- **Dowody:** [przebieg 41359225427](https://github.com/Yibux/insurance-app/actions/runs/41359225427) — krok „Authenticate to Dev Hub (JWT Bearer)” zielony w 3 s, sekrety w logu widoczne wyłącznie jako `***`.
- **Do pracy:** rozdział #84 (JWT w CI), #83 (zarządzanie sekretami w potoku).

### #16 Create, deploy to and always delete a scratch org per PR

- **Data:** 2026-10-29 · **PR:** #101 · **Wymagania:** FR-CI-02, NFR-PERF-05
- **Co zrobiono:** Dla każdego PR zmieniającego metadane Salesforce powstaje efemeryczny scratch org (1 dzień, unikalny alias), do którego wdrażane są źródła; błąd deployu oblewa job. Org jest usuwany w kroku `always()`, także po błędzie lub anulowaniu.
- **Jak:** `.github/workflows/scratch-org-validation.yml`: `sf org create scratch --duration-days 1`, alias `pr-<nr>-<run_id>-<attempt>`; `SF_SITE_ADMIN_USERNAME` ustawiana z `sf org display` (wymóg ze spike'a #8); `sf project deploy start`; `sf org delete scratch` w `if: always()`.
- **Decyzje i alternatywy:**
  - Osobny workflow od `pr-validation.yml` z filtrem `paths:` (`force-app/`, `config/`, `sfdx-project.json`) — zmiany w dokumentacji nie zużywają limitu 6 scratch orgów dziennie ([ADR 0001](../adr/0001-monorepo.md)).
  - Dwa poziomy `concurrency`: per PR z `cancel-in-progress` (nowy push anuluje stary przebieg) oraz globalna grupa `devhub-scratch-org` na poziomie joba — w danej chwili działa najwyżej jeden job tworzący scratch org (limit 3 aktywnych).
  - Alternatywa: pula długo żyjących scratch orgów współdzielona między PR-ami — odrzucona, bo łamie izolację (stan z poprzedniego PR) i główną tezę o środowiskach efemerycznych.
- **Problemy:** `sf org create scratch` z Dev Hubem zalogowanym przez External Client App kończył się błędem `The callback URL provided is not valid` (lokalnie: `RemoteOrgSignupFailed`, kod C-1016) — serwis zakładania scratch orgów nie replikuje ECA do nowego orga. Obejście: `SF_SCRATCH_SIGNUP_CONNECTED_APP=PlatformCLI` i `SF_SCRATCH_SIGNUP_CALLBACK_URL=http://localhost:1717/OauthRedirect` w kroku tworzenia orga — przy zakładaniu orga używana jest wbudowana aplikacja CLI, a dostęp do Dev Hubu nadal idzie przez naszą ECA i JWT.
- **Dowody:** [przebieg 41359225427](https://github.com/Yibux/insurance-app/actions/runs/41359225427): instalacja CLI 16 s, logowanie 3 s, utworzenie scratch orga 20 s, deploy (w tym strona Experience Cloud) 30 s, usunięcie orga 4 s — cały job ok. 1 min 20 s.
- **Do pracy:** rozdział #84 (środowiska efemeryczne), pomiar czasu potoku w eksperymencie (M6, NFR-PERF-05).

### #17 Run Apex tests and enforce 75% coverage gate (check_coverage.py)

- **Data:** 2026-11-02 · **PR:** #102 · **Wymagania:** FR-CI-03, NFR-QA-01
- **Co zrobiono:** Po deployu do scratch orga workflow uruchamia testy Apex z pokryciem kodu i przepuszcza wynik przez własną bramkę `scripts/ci/check_coverage.py`. Bramka oblewa PR przy nieudanych testach lub pokryciu poniżej progu (domyślnie 75%, zmienna `COVERAGE_THRESHOLD`). Surowy wynik trafia do artefaktu `apex-test-results`, a tabela pokrycia do podsumowania joba.
- **Jak:**
  - `sf apex run test --class-names … --code-coverage --output-dir … --json`; kod wyjścia 100 (nieudane testy) przekazywany do bramki, inne błędy przerywają job.
  - `check_coverage.py <raport> --source-dir force-app` — pokrycie liczone ważone liniami (suma pokrytych / suma linii), opcje `--threshold`, `--per-class-threshold`, `--exclude`, `--fail-on-empty`; tabela Markdown do `$GITHUB_STEP_SUMMARY`.
  - 16 testów jednostkowych skryptu (`unittest`, bez zależności) uruchamianych w `pr-validation.yml`.
- **Decyzje i alternatywy:**
  - Własna bramka zamiast polegania na platformie — Salesforce egzekwuje 75% tylko przy deployu na produkcję, w scratch orgu nie.
  - Uruchamiane są tylko testy z repozytorium (`--class-names`), a liczone tylko klasy z `force-app/` (`--source-dir`), patrz „Problemy”.
  - Gdy w repozytorium nie ma jeszcze testów Apex, kroki bramki są pomijane (job zielony); `--fail-on-empty` pozwoli to zaostrzyć, gdy w M2 pojawi się logika.
  - `unittest` zamiast `pytest` — skrypt CI bez zależności instalowanych w potoku.
- **Problemy:** Experience Cloud dodaje do scratch orga własne kontrolery z testami (`SiteRegisterController`, `CommunitiesSelfRegController` i in.). Przy `RunLocalTests` liczyły się do wyniku i zawyżały go: klasa testowa z 40% pokrycia dała łącznie 82,14% i bramka przepuściła PR. Poprawka: tylko nasze testy i tylko nasze klasy. Lokalnie nie dało się sprawdzić formatu wyniku: CLI 2.78 nie obsługuje obejścia C-1016, a nowy CLI wymaga Node 22 — weryfikacja odbyła się w CI.
- **Dowody:**
  - [przebieg 41360184741](https://github.com/Yibux/insurance-app/actions/runs/41360184741) — przed poprawką: tymczasowa klasa `Probe` (40%) przepuszczona przez kontrolery platformy (82,14%);
  - [przebieg 41360432846](https://github.com/Yibux/insurance-app/actions/runs/41360432846) — po poprawce: `Probe` 40% → **bramka oblewa job**, artefakt zapisany, org usunięty;
  - [przebieg 41360678033](https://github.com/Yibux/insurance-app/actions/runs/41360678033) — po usunięciu klasy: brak testów Apex, kroki bramki pominięte, job zielony.
- **Do pracy:** rozdział #83 (bramki jakości w potoku), eksperyment M6 — zmiany obniżające pokrycie jako kategoria „wprowadzonych błędów”; argument, że ślepe `RunLocalTests` może dawać fałszywie zielony wynik.
