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

### #18 Integrate Salesforce Code Analyzer v5 with severity gate and SARIF

- **Data:** 2026-11-02 · **PR:** #103 · **Wymagania:** FR-CI-04, FR-CI-07, NFR-SEC-03, NFR-SEC-04
- **Co zrobiono:** Do `pr-validation.yml` dodano job `code-analyzer`: Salesforce Code Analyzer v5 (PMD, ESLint, RetireJS, Flow Scanner, Graph Engine i reguła własna) skanuje `force-app/` i oblewa PR przy naruszeniach o wadze ≤ 2. Wyniki trafiają do GitHub code scanning (SARIF) i do artefaktu z raportem HTML.
- **Jak:** `code-analyzer.yml` (nadpisanie `ApexSharingViolations`, reguła regex `ApexNoWithoutSharing`, ustawienia silnika Flow); `sf code-analyzer run --workspace force-app --rule-selector … --severity-threshold 2 --output-file reports/code-analyzer.sarif --output-file reports/code-analyzer.html`; `github/codeql-action/upload-sarif` (v4.39.1, SHA) z `if: always()`; uprawnienie `security-events: write` tylko dla tego joba.
- **Decyzje i alternatywy:** zestaw `Recommended` wybranych silników uzupełniony o reguły bezpieczeństwa z wymagań zamiast „wszystkich reguł” (szum) albo samego `Recommended` (luki w sharingu) — [ADR 0004](../adr/0004-code-analyzer-rules.md). SAST nie potrzebuje orga, więc biegnie w `pr-validation.yml` dla każdego PR i nie zużywa limitu scratch orgów. Wersje CLI i pluginu przypięte.
- **Problemy:** Domyślny zestaw `Recommended` przepuścił klasę z jawnym `without sharing` i klasę z DML bez deklaracji sharingu (NFR-SEC-03). Dodano `ApexSharingViolations` z wagą 2 i własną regułę regex. Wygenerowany CSS strony LWR daje 2 naruszenia Low; nie blokują i zostają w raporcie.
- **Dowody:**
  - [przebieg 41361714452](https://github.com/Yibux/insurance-app/actions/runs/41361714452) — sam `force-app/`: 2 × Low, job zielony, SARIF wysłany;
  - [przebieg 41361891695](https://github.com/Yibux/insurance-app/actions/runs/41361891695) — tymczasowa podatna klasa: `ApexSOQLInjection` i `ApexCRUDViolation` (High) → **job oblany**, `without sharing` niewykryte;
  - [przebieg 41362094070](https://github.com/Yibux/insurance-app/actions/runs/41362094070) — po dodaniu reguł: 5 × High (SOQL injection, 2 × CRUD, `without sharing`, brak sharingu) → job oblany;
  - [przebieg 41362236031](https://github.com/Yibux/insurance-app/actions/runs/41362236031) — po usunięciu klas testowych: job zielony.
- **Do pracy:** rozdział #83 (SAST w potoku, dobór reguł vs szum), eksperyment M6 — macierz „podatność → reguła → wynik” jako baza do TP/FN; argument, że domyślne zestawy reguł trzeba weryfikować pod wymagania (Bavadiya 2022).

### #19 Add gitleaks secret scanning in CI and pre-commit

- **Data:** 2026-11-02 · **PR:** #104 · **Wymagania:** FR-CI-05, FR-CI-09, NFR-SEC-05
- **Co zrobiono:** Dodano skanowanie sekretów gitleaks w dwóch miejscach: job `gitleaks` w `pr-validation.yml` skanuje **całą historię** repozytorium przy każdym PR (SARIF do code scanning), a hook pre-commit Husky skanuje zmiany w stage przed commitem. Konfiguracja i allowlista w `.gitleaks.toml`, procedura w [runbooku](../runbooki/skanowanie-sekretow.md).
- **Jak:**
  - binarka gitleaks 8.30.1 pobierana z wydania na GitHubie i weryfikowana **przypiętą sumą SHA-256** (nie plikiem sum z tego samego wydania);
  - `gitleaks git . --config .gitleaks.toml --redact --report-format sarif` po `checkout` z `fetch-depth: 0`;
  - `scripts/hooks/gitleaks-staged.sh` → `gitleaks git --pre-commit --staged --redact`, wywoływany z `.husky/pre-commit` przed `lint-staged`.
- **Decyzje i alternatywy:**
  - Binarka CLI zamiast `gitleaks/gitleaks-action` — pełna kontrola wersji i sumy kontrolnej, brak zależności od licencji akcji.
  - Pełna historia przy każdym PR zamiast tylko commitów PR — repo jest małe (sekundy), a wykrywa też sekret dodany i usunięty w kolejnych commitach.
  - **Autotest z kanarkiem**: job generuje w locie token w formacie GitHub PAT i wymaga, żeby gitleaks go wykrył — zepsuty skaner nie da fałszywie zielonego wyniku. Token nie trafia do historii (stały fałszywy sekret w repo psułby skan całej historii).
  - Hook lokalny ostrzega i przepuszcza commit, gdy gitleaks nie jest zainstalowany — CI pozostaje bramką obowiązkową.
  - `--redact` wszędzie: znaleziony sekret nie trafia do logów CI ani do SARIF.
- **Problemy:** PR trafił w konflikt w `docs/adr/README.md` (gałąź wyrosła z `main` sprzed merge'a #98), przez co **workflowy `pull_request` w ogóle się nie uruchomiły** — GitHub nie tworzy merge refa dla PR z konfliktem. Rozwiązano przez merge `main` do #103 i przeniesienie do #104.
- **Dowody:** [przebieg 41363508969](https://github.com/Yibux/insurance-app/actions/runs/41363508969) — suma kontrolna OK, kanarek wykryty, „26 commits scanned, no leaks found”, SARIF wysłany. <!-- commit testowy z hookiem po instalacji gitleaks lokalnie -->
- **Do pracy:** rozdział #83 (sekrety i łańcuch dostaw — IEEE 2025 SLR), eksperyment M6 — kategoria „wyciek sekretu” w katalogu podatnych zmian (sekret generowany w eksperymencie, nie commitowany na stałe).

### #20 Add CodeQL workflow for JavaScript

- **Data:** 2026-11-02 · **PR:** #106 · **Wymagania:** FR-CI-06
- **Co zrobiono:** Dodano workflow `.github/workflows/codeql.yml` uruchamiający analizę CodeQL dla JavaScriptu/TypeScriptu przy PR do `main`, przy pushu do `main` i raz w tygodniu. Wyniki trafiają do GitHub code scanning (zakładka Security) z kategorią `/language:javascript-typescript`.
- **Jak:** `github/codeql-action/init` (`build-mode: none`, `queries: security-extended`) i `analyze` w wersji 4.39.1 przypiętej do SHA; macierz `language` gotowa na dopisanie Pythona w #58; cron `17 4 * * 1`; `security-events: write` tylko w jobie analizy.
- **Decyzje i alternatywy:** osobny workflow zamiast konfiguracji domyślnej lub joba w `pr-validation.yml`, pakiet `security-extended` — [ADR 0005](../adr/0005-codeql-workflow.md). Workflow nie ma filtra `paths:` i nie dotyka scratch orgów.
- **Problemy:** brak. Uwaga: CodeQL tylko raportuje alerty; blokowanie merge'a wymaga reguły code scanning w rulesecie `main` (ustawienie repozytorium, poza kodem).
- **Dowody:** [przebieg 41455615705](https://github.com/Yibux/insurance-app/actions/runs/41455615705) — job zielony; API `code-scanning/analyses` dla `refs/pull/106/merge` zwraca analizę narzędzia CodeQL (103 reguły, 0 wyników) obok analiz Code Analyzer i gitleaks. Ścieżka „blokuje podatny kod” nie była sprawdzana (workflow nie oblewa PR sam z siebie).
- **Do pracy:** rozdział #83 (SAST drugiej generacji — analiza przepływu danych vs reguły wzorcowe), eksperyment M6 — porównanie wykrywalności CodeQL i Code Analyzera na tych samych wstrzykniętych podatnościach JS.

### #21 Configure Dependabot and npm audit gate

- **Data:** 2026-11-02 · **PR:** #107 · **Wymagania:** FR-CI-05
- **Co zrobiono:** Dodano `.github/dependabot.yml` (cotygodniowe aktualizacje zależności npm i akcji GitHub) oraz krok `npm audit --audit-level=high` w jobie `static-checks` w `pr-validation.yml`. PR z nową podatnością o wadze high lub critical w zależnościach jest oblewany.
- **Jak:**
  - Dependabot: ekosystemy `npm` i `github-actions`, poniedziałek, limit 5 PR-ów, grupowanie minor/patch (npm; akcje w grupach `actions-scratch-org` i `actions-other`), `cooldown` 7 dni, prefiksy `chore(deps)` / `chore(ci)`; `pip` dojdzie w #58.
  - `npm audit --audit-level=high` po `npm ci --ignore-scripts`, na pełnym drzewie (z zależnościami deweloperskimi).
  - Decyzja i alternatywy: [ADR 0006](../adr/0006-dependabot-npm-audit.md).
- **Decyzje i alternatywy:** `dependabot.yml` plus bramka w PR zamiast samych alertów (nie blokują) lub zewnętrznego skanera SCA (zbędna zależność). Próg `high`, bo `moderate` (33 porady w narzędziach deweloperskich, stan z 2026-11-02) zablokowałoby wszystkie PR-y bez możliwości naprawy.
- **Problemy:** Bramka od razu byłaby czerwona: `npm audit` (stan bazy porad z 2026-11-02) zgłaszał 2 porady high w zależnościach deweloperskich (`follow-redirects` 1.16.1 i `joi` 18.2.9, tranzytywnie przez `prettier-plugin-apex` → `wait-on`). Naprawa bez zmiany `package.json`: `npm update follow-redirects joi` (1.16.2 i 18.3.1, tylko `package-lock.json`). Pozostałe 45 porad (low/moderate, stan z 2026-11-02) zostaje poniżej progu. Przegląd bezpieczeństwa wskazał, że PR Dependabota zmieniający akcje używane w `scratch-org-validation.yml` uruchomi walidację scratch org (zużyje org i padnie na braku sekretów `devhub`); dlatego te akcje są w osobnej grupie `actions-scratch-org`, a taki czerwony check obsługuje właściciel ręcznie (ADR 0006). Dodano też `cooldown` 7 dni i ograniczono grupy akcji do minor/patch. Na Windows lokalne testy `scripts/ci` wymagają `PYTHONUTF8=1` (emoji w tabeli podsumowania), w CI (Linux) problemu nie ma.
- **Dowody:**
  - [przebieg 41457587365](https://github.com/Yibux/insurance-app/actions/runs/41457587365) — `PR validation` zielony, w tym krok `npm audit --audit-level=high` (0 podatności high) w jobie `static-checks`; [przebieg CodeQL 41457587148](https://github.com/Yibux/insurance-app/actions/runs/41457587148) zielony;
  - po poprawkach z przeglądu bezpieczeństwa (grupy akcji, `cooldown`): [PR validation 41476103483](https://github.com/Yibux/insurance-app/actions/runs/41476103483) i [CodeQL 41476103529](https://github.com/Yibux/insurance-app/actions/runs/41476103529) zielone;
  - ścieżka „blokuje” sprawdzona **tylko lokalnie**: z tymczasową zależnością `lodash@4.17.20` `npm audit --audit-level=high` kończy się kodem 1 (commit próbny c617ee7, wycofany w 9c3ce08); w CI nie powtarzano.
- **Do pracy:** rozdział #83 (analiza składu oprogramowania i łańcuch dostaw — IEEE 2025 SLR), eksperyment M6 — kategoria „podatna zależność” w katalogu wprowadzanych błędów; obserwacja, że bramka SCA wykrywa porady z bazy w danym dniu, więc ten sam commit może zmienić wynik.

### #23 Review Husky and lint-staged pre-commit hooks

- **Data:** 2026-11-02 · **PR:** #114 · **Wymagania:** FR-CI-09
- **Co zrobiono:** Przejrzano istniejące hooki (Husky + lint-staged z Prettier i ESLint oraz gitleaks z #19) i dodano brakujący hook `commit-msg` z commitlint, który wymusza Conventional Commits zgodnie z KONWENCJE. Hooki sprawdzono na rzeczywistych commitach.
- **Jak:** `@commitlint/cli` i `@commitlint/config-conventional` (devDependencies), `commitlint.config.js` (typy z KONWENCJE, limit nagłówka 100), `.husky/commit-msg` (`npx --no -- commitlint --edit "$1"`); runbook [hooki-git.md](../runbooki/hooki-git.md); decyzja w [ADR 0007](../adr/0007-hooki-husky-commitlint.md).
- **Decyzje i alternatywy:** commitlint lokalnie zamiast samej walidacji w CI lub własnego regexa; numer issue w nagłówku niewymuszany (commity merge, Dependabota i docs-only go nie mają). Pre-commit bez zmian: kolejność gitleaks → Prettier → ESLint jest poprawna (ESLint widzi już sformatowany kod).
- **Problemy:** Hooki da się pominąć `--no-verify`, więc nie zastępują CI. Podczas prób wycofanie sondy przez `git reset --hard` skasowało niezacommitowane zmiany w `package.json` — instalację zależności powtórzono.
- **Dowody:** lokalne commity próbne (wycofane, nie ma ich w historii PR): komunikat `bad message` odrzucony przez commitlint (`subject-empty`, `type-empty`, kod 1); `wip: x` i `update stuff` odrzucone, `feat(x): ok thing (#1)`, `security(ci): harden (#2)` i `Merge pull request …` przyjęte; staged plik z tokenem wygenerowanym w locie zablokowany przez gitleaks (`leaks found: 1`); staged `const   a = {b:1}` automatycznie sformatowany przez Prettier do `const a = { b: 1 };`. Lokalnie `npm run lint`, `prettier:verify`, `npm test`, `npm audit --audit-level=high` bez błędów. Przebiegi CI: [PR validation 41478583158](https://github.com/Yibux/insurance-app/actions/runs/41478583158) (zielony: static-checks, Code Analyzer, gitleaks), [CodeQL 41478583229](https://github.com/Yibux/insurance-app/actions/runs/41478583229). Scratch org nie był używany (brak zmian w ścieżkach wyzwalających).
- **Do pracy:** rozdział #83 (shift-left: kontrole lokalne jako pierwsza, nieobowiązkowa linia obrony vs obowiązkowe CI), eksperyment M6 — `--no-verify` jako przykład obejścia kontroli lokalnych, wychwytywanego dopiero w CI.

### #27 Document the pipeline and write ADR GitHub Actions vs Copado

- **Data:** 2026-11-02 · **PR:** <!-- numer PR --> · **Wymagania:** NFR-MNT-03
- **Co zrobiono:** Opisano potok CI/CD (diagram Mermaid jobów i bramek, tabela bramek, cechy wspólne, powiązanie z literaturą) oraz zapisano decyzję o wyborze GitHub Actions + Salesforce CLI zamiast Copado.
- **Jak:** [docs/architektura/potok-cicd.md](../architektura/potok-cicd.md); [ADR 0008](../adr/0008-github-actions-vs-copado.md) z wierszem w indeksie ADR. Opis powstał na podstawie rzeczywistych workflowów (`pr-validation.yml`, `scratch-org-validation.yml`, `codeql.yml`) i wpisów tego logu.
- **Decyzje i alternatywy:** GitHub Actions zamiast Copado i innych CI (powody w ADR 0008). Dokument opisuje stan faktyczny: elementy #22 (raporty) i #24 (deploy) są oznaczone jako planowane, a branch protection jako niewłączone (ruleset `main` ma tylko regułę blokady usunięcia; zadania #6 i #25). Plik leży w `docs/architektura/` zgodnie z kryteriami issue, jako nowy plik bez zmian w istniejących plikach tego katalogu (równolegle trwa #29).
- **Problemy:** Copado nie był testowany; porównanie opiera się na dokumentacji i modelu licencyjnym, co zapisano w ADR jako ograniczenie. PR jest ułożony na #114 (#23) ze względu na wiersz ADR 0007 w indeksie i wpis #23 w tym logu.
- **Dowody:** <!-- linki do przebiegów CI -->
- **Do pracy:** rozdział #86 (implementacja potoku, diagram), #83 (bramki jako odpowiedź na lukę automatyzacji — Cheenepalli 2025, Bavadiya 2022), uzasadnienie wyboru narzędzia. **Do aktualizacji po merge'u #22 i #24 (przed 2026-12-06):** `potok-cicd.md` (tabela i diagram) oraz ten wpis.
