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

- **Data:** 2026-11-02 · **PR:** #115 · **Wymagania:** NFR-MNT-03
- **Co zrobiono:** Opisano potok CI/CD (diagram Mermaid jobów i bramek, tabela bramek, cechy wspólne, powiązanie z literaturą) oraz zapisano decyzję o wyborze GitHub Actions + Salesforce CLI zamiast Copado.
- **Jak:** [docs/architektura/potok-cicd.md](../architektura/potok-cicd.md); [ADR 0008](../adr/0008-github-actions-vs-copado.md) z wierszem w indeksie ADR. Opis powstał na podstawie rzeczywistych workflowów (`pr-validation.yml`, `scratch-org-validation.yml`, `codeql.yml`) i wpisów tego logu.
- **Decyzje i alternatywy:** GitHub Actions zamiast Copado i innych CI (powody w ADR 0008). Dokument opisuje stan faktyczny: elementy #22 (raporty) i #24 (deploy) są oznaczone jako planowane, a branch protection jako niewłączone (ruleset `main` ma tylko regułę blokady usunięcia; zadania #6 i #25). Plik leży w `docs/architektura/` zgodnie z kryteriami issue, jako nowy plik bez zmian w istniejących plikach tego katalogu (równolegle trwa #29).
- **Problemy:** Copado nie był testowany; porównanie opiera się na dokumentacji i modelu licencyjnym, co zapisano w ADR jako ograniczenie. PR jest ułożony na #114 (#23) ze względu na wiersz ADR 0007 w indeksie i wpis #23 w tym logu.
- **Dowody:** Lokalnie `npm run lint` i `prettier:verify` bez błędów. Po zmergowaniu #114 baza PR #115 zmieniona na `main`, a main scalony do gałęzi; CI na 810c2f6: [PR validation 41485686246](https://github.com/Yibux/insurance-app/actions/runs/41485686246) (zielony), [CodeQL 41485686235](https://github.com/Yibux/insurance-app/actions/runs/41485686235) (zielony). Scratch org nie był używany (zmiany tylko w `docs/`).
- **Do pracy:** rozdział #86 (implementacja potoku, diagram), #83 (bramki jako odpowiedź na lukę automatyzacji — Cheenepalli 2025, Bavadiya 2022), uzasadnienie wyboru narzędzia. **Do aktualizacji po merge'u #24 (przed 2026-12-06):** `potok-cicd.md` (tabela i diagram); część dotycząca #22 zaktualizowana w #123.

### #22 Publish test and scan reports as PR job summary and artifacts

- **Data:** 2026-11-02 · **PR:** #119 · **Wymagania:** FR-CI-07, NFR-OBS-02
- **Co zrobiono:** Każda bramka zostawia teraz czytelne podsumowanie w zakładce przebiegu (wyniki testów Apex, pokrycie, liczby naruszeń Code Analyzera wg wagi, czasy kroków) oraz surowe raporty w artefaktach. Czasy trwania każdej bramki są zapisywane jako dane wejściowe eksperymentu.
- **Jak:**
  - `scripts/ci/gate_report.py` (+ `test_gate_report.py`): podkomendy `apex-tests`, `code-analyzer`, `durations`; zapis do `$GITHUB_STEP_SUMMARY`, odporne na brak pliku wejściowego;
  - `.github/actions/gate-durations/action.yml`: ostatni krok każdego joba (`if: always()`) pobiera czasy kroków z API Actions i wysyła `gate-durations-*`;
  - `scratch-org-validation.yml`: krok „Apex test results summary” (tabela obok istniejącej tabeli pokrycia z `check_coverage.py`);
  - `pr-validation.yml`: Code Analyzer zapisuje dodatkowo `code-analyzer.json` (liczby wg wagi w podsumowaniu), raport gitleaks jako artefakt `gitleaks-report`; jobom dodano `actions: read`.
- **Decyzje i alternatywy:** czasy z API zamiast własnych znaczników w każdym kroku lub zewnętrznej akcji — [ADR 0010](../adr/0010-raporty-bramek-w-podsumowaniu-zadania.md).
- **Problemy:** czas samego kroku raportującego i całego joba nie jest dokładny (job jeszcze trwa), co opisano w ADR. Format JSON Code Analyzera (`violationCounts.sev1..sev5`, `violations[].severity`) przyjęto z dokumentacji i potwierdzono w przebiegu CI (podsumowanie z 2 naruszeniami wagi 4). W kroku Code Analyzer dwa argumenty `--output-file` trafiły do jednej linii (kosmetyka, działa). Na Windows lokalne testy wymagają `PYTHONUTF8=1`.
- **Dowody:** lokalnie `unittest` (24 testy), `npm run lint`, `prettier:verify` bez błędów. Przebiegi CI (wszystkie zielone): [PR validation 42187693451](https://github.com/Yibux/insurance-app/actions/runs/42187693451) — artefakty `code-analyzer-report` (html, json, sarif), `gitleaks-report`, `gate-durations-{static-checks,gitleaks,code-analyzer}`, podsumowanie Code Analyzera i tabela czasów w logu; [Scratch org validation 42187693917](https://github.com/Yibux/insurance-app/actions/runs/42187693917) — `gate-durations-scratch-org`. `gh api` z `actions: read` działa. Krok „Apex test results summary” i artefakt `apex-test-results` zostały pominięte, bo repozytorium nie ma jeszcze klas testowych Apex (niezweryfikowane w CI).
- **Do pracy:** rozdział #86 (obserwowalność potoku), eksperyment M6 — czasy bramek jako zmienna zależna (czas informacji zwrotnej dla programisty). `potok-cicd.md` zaktualizowano w #123.

### Chore (Refs #23): poprawki po przeglądzie PR #114

- **Data:** 2026-11-06 · **PR:** patrz nagłówek PR (chore bez własnego issue, `Refs #23`) · **Wymagania:** FR-CI-09
- **Co zrobiono:** Trzy drobne poprawki po przeglądzie #114: plik `.nvmrc` i pole `engines` w `package.json`, doprecyzowanie runbooka hooków (CI nie sprawdza komunikatów commitów), ograniczenie anulowania przebiegów CodeQL do PR-ów.
- **Jak:** `.nvmrc` = `22.12.0`; `engines.node` = `>=22.12.0` (wymóg `@commitlint/cli` 21; `lint-staged` 15 wymaga `>=18.12`, `husky` 9 `>=18`, więc minimum wyznacza commitlint). Workflowy w CI używają `node-version: 22` (najnowsze 22.x), zgodnie z `engines`, więc nie zmieniano ich. W `codeql.yml` `cancel-in-progress` ma wartość `${{ github.event_name == 'pull_request' }}` (grupa współbieżności bez zmian), dzięki czemu przebiegi bazowe na `main` i harmonogram nie są anulowane. Poprawiono [hooki-git.md](../runbooki/hooki-git.md).
- **Decyzje i alternatywy:** `.nvmrc` ze ściśle określoną wersją minimalną zamiast `22`/`lts/*` (powtarzalność lokalna); ujednolicenie CI do `.nvmrc` (`node-version-file`) pominięto, bo zmieniałoby wszystkie workflowy, w tym scratch-org (budżet orgów). Można to zrobić osobno.
- **Problemy:** Lokalnie zainstalowany Node 21 jest poniżej `engines` (ostrzeżenie `npm`); wymaga aktualizacji lokalnego Node.
- **Dowody:** lokalnie `npm run lint` i `prettier:verify`; przebiegi CI w opisie PR. Scratch org nie był używany (brak zmian w ścieżkach wyzwalających).
- **Do pracy:** rozdział #83 (shift-left: ograniczenia kontroli lokalnych, powtarzalność środowiska narzędziowego).

### Poprawki z przeglądu bezpieczeństwa PR #119 (część #22)

- **Data:** 2026-11-06 · **PR:** zob. historia PR (ułożony na #119) · **Wymagania:** FR-CI-07, NFR-OBS-02
- **Co zrobiono:** Drobne poprawki po przeglądzie bezpieczeństwa raportów z #22, bez własnego issue (`Refs #22`).
- **Jak:**
  - `gitleaks-report`: retencja 14 -> 3 dni; w [ADR 0010](../adr/0010-raporty-bramek-w-podsumowaniu-zadania.md) dopisano obowiązek rotacji wykrytego sekretu;
  - odporność raportowania: `gate-durations` kończy się ostrzeżeniem (`|| echo "::warning::..."`), `gate_report.py` używa `.get("name", "?")` i traktuje uszkodzony JSON jak brak pliku (3 nowe testy, razem 27);
  - `scratch-org-validation.yml`: do `paths` dodano `scripts/ci/gate_report.py` i `.github/actions/gate-durations/**`;
  - `dependabot.yml`: `github-actions` skanuje `directories` `/` i `/.github/actions/*` (akcja lokalna ma własny `action.yml`);
  - kosmetyka: rozbite sklejone `--output-file`, `GH_TOKEN` ustawiany tylko dla `gh api`, escapowanie `|` i backticków w komórkach tabel.
- **Decyzje i alternatywy:** zawężenie `GH_TOKEN` do polecenia zamiast całego kroku; escapowanie `|` jako `\|` (poprawny Markdown) zamiast dotychczasowej zamiany na `/`.
- **Problemy:** Zmiana `paths` w workflow scratch org sprawia, że ten PR zużyje jeden scratch org. Po squashu #119 ten PR może wymagać rebase lub merge `main`.
- **Dowody:** lokalnie `unittest` (27 testów, `PYTHONUTF8=1`), `npm run lint`, `prettier:verify` bez błędów. Przebiegi CI: [PR validation 42209376592](https://github.com/Yibux/insurance-app/actions/runs/42209376592), [Scratch org validation 42209376578](https://github.com/Yibux/insurance-app/actions/runs/42209376578).
- **Do pracy:** rozdział #83 (higiena artefaktów z wynikami skanów sekretów).

### #123 Update pipeline documentation after reports and gate durations shipped

- **Data:** 2026-11-06 · **PR:** zob. nagłówek PR (`Closes #123`) · **Wymagania:** FR-CI-07, NFR-OBS-02
- **Co zrobiono:** Zaktualizowano `potok-cicd.md` do stanu po #22: opisano job summary, artefakty, zapis czasów bramek, skrypt `gate_report.py` i akcję `gate-durations`. Elementy faktycznie niewdrożone (#24 deploy, #122 delta deployment, #25 wymagane checki) pozostały oznaczone jako planowane. Do sekcji poprawek po przeglądzie PR #119 dopisano linki do przebiegów CI.
- **Jak:** stan zweryfikowano w workflowach na `main` (`pr-validation.yml`, `scratch-org-validation.yml`, `.github/actions/gate-durations/action.yml`). W `potok-cicd.md`: nowa sekcja „Raporty, artefakty i czasy bramek” (tabele podkomend i artefaktów z retencją), wiersz „Raporty i czasy bramek” w tabeli jobów, zmieniony diagram (raporty jako stan faktyczny, delta deployment jako planowany), uprawnienie `actions: read` w cechach wspólnych. Zmiany tylko w `docs/`.
- **Decyzje i alternatywy:** bez nowego ADR (brak nowej decyzji, indeks ADR bez zmian); dokument odsyła do [ADR 0010](../adr/0010-raporty-bramek-w-podsumowaniu-zadania.md). Artefakty opisano w osobnej sekcji zamiast rozbudowywać tabelę jobów, by ta pozostała czytelna.
- **Problemy:** `apex-test-results` i podsumowanie testów Apex nie zostały dotąd zweryfikowane w CI, bo w repozytorium nie ma klas testowych Apex; zaznaczono to w dokumencie.
- **Dowody:** lokalnie `prettier --check` dla zmienionych plików; przebiegi CI: [PR validation 42211549524](https://github.com/Yibux/insurance-app/actions/runs/42211549524), [CodeQL 42211549511](https://github.com/Yibux/insurance-app/actions/runs/42211549511) (oba zielone). Scratch org nie był używany (zmiany tylko w `docs/`).
- **Do pracy:** rozdziały #86 (implementacja potoku, obserwowalność) i #83 (bramki, artefakty); eksperyment M6 (czasy bramek). **Do aktualizacji po merge'u #24, #122 i #25 (przed 2026-12-06).**

### #26 Measure baseline pipeline duration

- **Data:** 2026-11-06 · **PR:** #125 (ułożony na #124: **należy zmergować po #124**) · **Wymagania:** NFR-PERF-05
- **Co zrobiono:** Zmierzono bazowy czas całego potoku PR przy pełnym wdrożeniu do scratch orga (stan przed #122, delta deployment). Wyniki: [docs/experiment/results/baseline.csv](../experiment/results/baseline.csv) (5 przebiegów + wiersze `stat_*`: mediana, średnia, wariancja i odchylenie z próby, min, max).
- **Jak (definicja pomiaru):**
  - jednostka pomiaru: jeden head SHA w PR do `main`; `pipeline_seconds` = od utworzenia najwcześniejszego z trzech przebiegów (PR validation, CodeQL, Scratch org validation; przybliżenie momentu push) do najpóźniejszego `updated_at` któregokolwiek z nich (ścieżka krytyczna); wartość z API Actions, rozdzielczość 1 s;
  - kolumny dodatkowe: czasy workflowów, jobów (`job_*`) i kroków scratch orga (`step_*`) z API zadań; pokrywają się z artefaktami `gate-durations-*` (pobranymi i sprawdzonymi dla wszystkich 5 przebiegów), ale `job_*` liczone z API są dokładniejsze niż „(job total)” z artefaktu (ten liczy do chwili zapisu raportu);
  - przebiegi istniejące (B1, B2): PR #119 (SHA 72fb160; PR validation 42187693451, CodeQL 42187693431, scratch 42187693917) i PR #121 (SHA 6428929; 42209376592, 42209376467, 42209376578);
  - przebiegi nowe (N1-N3): trzy kolejne pushe na gałęzi tego PR, każdy zmieniający wyłącznie kolejność kluczy w `force-app/main/default/aura/.eslintrc.json` (plik na liście `.forceignore`, brak komponentów Aura, więc wdrożenie bez zmian, a filtr `paths` workflowu scratch orga się uruchamia); SHA 9ed2b78 (PR validation 42299196136, CodeQL 42299196045, scratch 42299196052), 6d17141 (42299538436, 42299538437, 42299538433), 4cbe20c (42299871197, 42299871014, 42299871050). Przebiegi wykonywano pojedynczo, po zakończeniu poprzedniego. Zmiana pliku została cofnięta w kolejnym commicie (`[skip ci]`), więc wynikowy diff PR względem `main` nie dotyka `force-app/`;
  - wersja potoku: workflowy i `scripts/ci/` w N1-N3 są identyczne z `main` w dc4abb0 (zawiera #119 i #121); B1 działał na wersji z #119 przed poprawkami przeglądu z #121 (różnice dotyczą `paths`, raportowania i Dependabota, nie kroków wdrożenia);
  - wynik: mediana `pipeline_seconds` = 102 s, wariancja z próby = 130,7 s² (odchylenie 11,4 s), zakres 87-118 s; ścieżką krytyczną jest zawsze Scratch org validation (mediana 102 s; wdrożenie źródeł ok. 33 s, utworzenie orga ok. 22 s, instalacja `sf` ok. 24 s), PR validation i CodeQL kończą się po ok. 62-66 s.
- **Decyzje i alternatywy:** pełny pomiar potoku (ścieżka krytyczna trzech workflowów) zamiast samego joba scratch orga (decyzja zleceniodawcy); powtórzenia przez pushe z neutralną zmianą w `force-app/` zamiast `gh run rerun`, bo tylko świeży push uruchamia wszystkie trzy workflowy razem. Starszych czterech przebiegów scratch orga z 2026-11-01 (41359225427, 41360184741, 41360678033, 41361714442) nie włączono do próby: obejmują wcześniejsze wersje potoku (bez Code Analyzera, raportów i `gate-durations`; pierwszy bez testów Apex), traktować je tylko pomocniczo.
- **Problemy:**
  - w N2 i N3 job „Lint, format and LWC Jest” zakończył się błędem na `npm ci` (`ERESOLVE`: `@salesforce/eslint-config-lwc@3.7.2` wymaga peer `@salesforce/eslint-plugin-lightning@^1.0.0`, a projekt ma `2.0.0`), choć w N1 ten sam krok przeszedł, a `package*.json` jest identyczny z `main`. Przyczyna niezbadana (niedeterminizm środowiska runnera/npm); nie jest związana ze zmianą w `force-app/`. Skutek dla pomiaru: `job_static_checks_s` w N2 i N3 (7-8 s) to czas do awarii, nie czas bramki, więc statystyki tej kolumny i `pr_validation_seconds` nie są wiarygodne dla tych dwóch przebiegów; `pipeline_seconds` nie zależy od nich, bo ścieżką krytyczną jest scratch org. Wymaga osobnego zgłoszenia;
  - czas trwania zależy od obciążenia współdzielonych runnerów i Dev Hubu, próba n=5 jest mała, a punkt startu to czas utworzenia przebiegu, nie moment `git push`.
- **Dowody:** `gh api` dla każdego z 15 przebiegów (dane w CSV, skrypt jednorazowy poza repozytorium); wszystkie przebiegi Scratch org validation i CodeQL zakończone sukcesem, PR validation: B1, B2, N1 sukces, N2, N3 błąd opisany wyżej. Zużyto 3 scratch orgi (N1-N3); w ciągu 24 h wcześniej 2 (8:26 i 11:19 UTC). Brak `LIMIT_EXCEEDED`.
- **Do pracy:** rozdział wyników (M6, NFR-PERF-05): punkt odniesienia dla porównania z delta deployment (#122).
