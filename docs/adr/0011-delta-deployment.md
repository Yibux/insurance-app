# 0011. Delta deployment w walidacji scratch orga: własny diff zamiast sfdx-git-delta, pełny deploy jako bezpieczny domyślny

- **Status:** przyjęta
- **Data:** 2026-11-08
- **Issue:** #122
- **Wymagania:** FR-CI-02, FR-CI-03 (bramka pokrycia), FR-CI-07, NFR-PERF-01, NFR-PERF-05

## Kontekst

Workflow `scratch-org-validation` tworzy dla każdego PR **nowy, pusty** scratch org (1 dzień), wdraża cały `force-app/`, uruchamia wszystkie testy Apex i sprawdza pokrycie (`check_coverage.py`, próg 75%). Pomiar bazowy ([baseline.csv](../experiment/results/baseline.csv), #26) pokazał, że ścieżką krytyczną potoku jest ten job (mediana 97 s z 102 s całego potoku), a samo wdrożenie źródeł trwa ok. 33 s. Wraz z rozrostem metadanych ten czas rośnie liniowo. Issue #122 prosi o wdrażanie wyłącznie zmienionych komponentów względem bazy PR, bez osłabienia bramki pokrycia.

Cechy środowiska, które przesądzają o projekcie:

- **Org jest pusty.** Delta wdrożona do pustego orga nie zawiera niezmienionych zależności. W typowym projekcie (np. Apex zależny od obiektów custom, [ADR 0002](0002-custom-objects-vs-fsc.md)) wdrożenie samej delty się nie powiedzie lub, gorzej, pominie testy, które trzeba by uruchomić.
- **Org nie pamięta poprzedniego stanu**, więc komponenty usunięte w PR nigdy w nim nie istniały.
- **Limity Dev Hubu** (3 aktywne, 6 nowych orgów na dobę) wykluczają strategie, które wymagają wielu orgów na PR.
- Repozytorium nie ma jeszcze klas Apex ani obiektów custom (w `force-app/` są tylko metadane witryny Experience Cloud), więc decyzja musi zachować poprawność dla przyszłej zawartości, a nie tylko dla obecnej.

## Rozważane opcje

### Narzędzie do wyznaczenia delty

1. **`sfdx-git-delta` (sgd)** — wtyczka `sf` generująca `package.xml` i `destructiveChanges.xml` z `git diff`. Zalety: dojrzałe, zna typy metadanych, obsługuje usunięcia i zmiany nazw. Wady: nowa zależność w łańcuchu dostaw (wersja 6.45.1, licencja MIT, 8 zależności bezpośrednich, m.in. `@salesforce/source-deploy-retrieve`, `@salesforce/core`, `@oclif/core`); jej funkcja najcenniejsza w praktyce, czyli manifest zniszczeń, nie ma zastosowania w pustym orgu (patrz niżej); samo wyznaczenie listy plików to jedno wywołanie `git diff`. Nie można jej dodać do `package.json` (lockfile i Dependabot objęłyby ją, ale konsolidacja zależności jest prowadzona osobno), więc trzeba by ją instalować w workflow przez `sf plugins install sfdx-git-delta@<wersja>`.
2. **Własny skrypt: `git diff` + `sf project deploy start --source-dir`** — wybrane. `sf` samo rozpoznaje komponent po ścieżce pliku (także pliku wewnątrz paczki LWC) i stosuje `replacements` z `sfdx-project.json`. Zalety: zero nowych zależności, pełna kontrola reguł awaryjnych (testowalny skrypt Pythona, biblioteka standardowa, jak `check_coverage.py`). Wady: sami utrzymujemy reguły; nie generuje manifestu zniszczeń (niepotrzebnego w pustym orgu).
3. **Śledzenie źródeł (source tracking) `sf project deploy start` bez argumentów** — nie wnosi nic, bo świeży org nie ma historii zmian; wdraża całość.
4. **Migawka lub wstępnie zbudowany org z bazą z `main`**, na który nakładana jest delta. Rozwiązałoby problem zależności, lecz wymaga osobnego spike'u (dostępność migawek w Dev Hubie Developer Edition nie została sprawdzona, a utrzymywany org bazowy zjada limit „aktywnych”). Poza zakresem tego zadania, odnotowane jako kierunek dalszych prac.

### Zakres testów Apex w trybie delta

1. **`RunLocalTests` / wszystkie klasy testowe** — wymaga wdrożenia całego Apex, czyli faktycznie pełnego deployu.
2. **`RunSpecifiedTests` dla zmienionych klas** — wymaga wdrożenia klas testowych i ich zależności do pustego orga; mapowanie klasa-test po nazwach jest kruche, a pominięcie testu klasy niezmienionej, której zachowanie zmieniła zmiana w obiekcie lub polu, osłabia bramkę.
3. **Delta tylko dla metadanych, od których testy Apex nie zależą (LWC, Aura); każda inna zmiana to pełny deploy i pełne testy** — wybrane.

### Zakres Code Analyzera

1. **Tylko delta** — tańsze, lecz reguły przepływu danych (`sfge`) i `flow` potrzebują kontekstu całego workspace'u, a naruszenie w kodzie, którego dotyka zmiana pośrednio, umknęłoby.
2. **Całe `force-app/`** — wybrane; bez zmian względem [ADR 0004](0004-code-analyzer-rules.md).

## Decyzja

Wprowadzamy tryb **delta** w jobie `deploy` z własnym planistą `scripts/ci/delta_plan.py` (+ testy `test_delta_plan.py`) i zasadą „w razie wątpliwości pełny deploy”. Narzędzia `sfdx-git-delta` nie dodajemy.

### Wyznaczanie bazy (PR)

- Baza to `github.event.pull_request.base.sha`, przekazana do skryptu zmienną środowiskową `BASE_SHA` (nigdy przez interpolację w treści `run:`), a w skrypcie zwalidowana wyrażeniem `^[0-9a-f]{40}$`. Nazwy gałęzi, tytuł i opis PR nie są używane.
- `git fetch --no-tags --depth=1 origin <BASE_SHA>`, potem `git diff --name-status -z --no-renames <BASE_SHA> HEAD`. Checkout dotyczy commita scalającego PR z bazą, więc diff to dokładnie zmiany PR (z ewentualnymi nowszymi zmianami `main`, co może tylko powiększyć deltę). Płytki fetch wystarcza, bo porównujemy dwa drzewa, a nie historię.
- Nazwy plików są niezaufane: odczyt rozdzielany znakiem NUL (`-z`), zapis do pliku rozdzielanego NUL-em, odczyt w powłoce przez `mapfile -d ''` do tablicy i przekazanie jako osobne argumenty `--source-dir`. Nazwy plików nie trafiają do `GITHUB_OUTPUT` ani do logów (wynik zawiera wyłącznie stałe komunikaty i liczby).

### Zaufanie do planisty (przegląd bezpieczeństwa PR #133)

Workflow `pull_request` uruchamia kod z PR, więc PR mógłby zmienić planistę tak, by zawsze zwracał `delta` i omijał testy Apex oraz bramkę pokrycia. Dlatego: (1) planista jest wykonywany z **commita bazowego** (`git show <BASE_SHA>:scripts/ci/delta_plan.py`, `python3 -I`), nie z PR; brak pliku w bazie (jak w PR wprowadzającym planistę) to błąd planisty, czyli pełny deploy; (2) poza planistą, w samym kroku workflow, każda zmiana w `.github/` lub `scripts/ci/` względem bazy wymusza pełny deploy; (3) przed wdrożeniem delty bash odrzuca pustą listę (puste `--source-dir` wdrożyłoby wszystko) oraz każdą ścieżkę spoza `force-app/main/default/lwc/` i `aura/`; błąd oznacza fallback do pełnego deployu. Wciąż jednak PR może sam zmienić workflow; ochroną przed tym jest przegląd zmian w `.github/` (CODEOWNERS) i, docelowo, wymagane checki.

### Reguły (pierwsza pasująca wygrywa; wszystko poza „delta” to pełny deploy)

| Sytuacja                                                                                                                                                             | Tryb                                                                     |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| zdarzenie inne niż `pull_request`, brak lub niepoprawny `BASE_SHA`                                                                                                   | pełny                                                                    |
| błąd planisty (git, parsowanie): wyjątek jest łapany, krok ma `continue-on-error`, brak wyjścia `mode` jest traktowany jak pełny                                     | pełny                                                                    |
| zmiana `sfdx-project.json`, `.forceignore`, `config/`, `scripts/ci/check_coverage.py`, `gate_report.py`, `delta_plan.py`, akcji `gate-durations` lub samego workflow | pełny                                                                    |
| pusta delta (po odrzuceniu plików z `.forceignore`, np. `.eslintrc.json`, `jsconfig.json`, `__tests__/`)                                                             | pełny                                                                    |
| jakikolwiek plik usunięty, przeniesiony lub ze zmienionym typem w `force-app/`                                                                                       | pełny                                                                    |
| duża delta: więcej niż 200 plików lub więcej niż połowa śledzonych plików `force-app/`                                                                               | pełny                                                                    |
| jakikolwiek zmieniony plik poza `force-app/main/default/lwc/` i `.../aura/` (Apex, obiekty, pola, flowy, zestawy uprawnień, Experience Cloud itd.)                   | pełny                                                                    |
| wyłącznie pliki w `lwc/` lub `aura/` (dodane lub zmodyfikowane)                                                                                                      | delta                                                                    |
| wdrożenie delty zakończone błędem                                                                                                                                    | po błędzie wdrażany jest cały `force-app/` (krok `Deploy source (full)`) |

### Usunięcia i zmiany nazw (destructive changes)

Scratch org jest pusty, więc usunięty komponent nie istnieje w orgu i manifest zniszczeń nie ma czego usuwać. Prawdziwe ryzyko jest inne: usunięty lub przemianowany komponent może być nadal używany przez niezmieniony komponent, a delta tego **nie wykryje**, bo niezmieniony komponent nie jest wdrażany. Dlatego każde usunięcie lub zmiana nazwy (`--no-renames` rozbija ją na usunięcie i dodanie) wymusza pełny deploy. Manifest zniszczeń będzie potrzebny dopiero przy wdrożeniu na trwały org docelowy (#24); wtedy ocena `sfdx-git-delta` wraca (patrz konsekwencje).

### Testy Apex i bramka pokrycia

- Tryb pełny: bez zmian: wszystkie klasy testowe z `force-app/`, `check_coverage.py` z `--source-dir force-app` i progiem 75%. `check_coverage.py` nie został zmieniony.
- Tryb delta: ponieważ delta obejmuje wyłącznie paczki LWC i Aura, których wynik testów Apex nie może zmienić (zależność idzie od LWC do Apex, nie odwrotnie), testy Apex i bramka pokrycia są pomijane, a podsumowanie przebiegu mówi to wprost. Bramka nie jest osłabiona: każda zmiana, która mogłaby zmienić wynik testów lub pokrycia (Apex, obiekty, pola, reguły walidacji, flowy, uprawnienia), uruchamia pełny deploy i pełny zestaw testów. Lista dozwolonych folderów (`DELTA_ELIGIBLE_FOLDERS`) jest jedynym miejscem, które trzeba rozszerzać świadomie.
- Założenie do weryfikacji w M2: gdy pojawi się Apex, trzeba ocenić `RunSpecifiedTests` na podstawie pomiarów (udział PR dotykających tylko LWC/Aura).

### Zakres Code Analyzera

Bez zmian: skanowany jest cały `force-app/` w osobnym jobie `code-analyzer` (workflow `pr-validation`), niezależnie od trybu wdrożenia. Wybór jest celowy (powody w opcjach). Job nie używa scratch orga i nie zależy od tej decyzji.

### Łańcuch dostaw i bezpieczeństwo

- Nie dodajemy żadnej nowej zależności: planista używa wyłącznie biblioteki standardowej Pythona i `git`, a wdrożenie `sf` w już przypiętej wersji (2.156.8). Nie ma więc nic do przypięcia ani do objęcia Dependabotem lub `npm audit`.
- Gdyby wybrano sgd: wtyczka instalowana przez `sf plugins install` leży poza `package.json` i lockfile, więc **Dependabot ani `npm audit` jej nie widzą**, a przypięcie wersji wtyczki nie przypina jej zależności przechodnich (brak lockfile; wtyczka uruchamiałaby kod w jobie z uwierzytelnioną sesją Dev Huba). To główny argument za własnym skryptem. Analogiczne ryzyko istnieje już dla wtyczki `code-analyzer` (przypięta wersja 5.16.0), lecz ten job nie ma sekretów Dev Huba.
- Brak nowych uprawnień ani sekretów; planista działa w jobie `deploy` z tym samym `contents: read`. Wejście niezaufane (nazwy plików) nie trafia do powłoki w postaci tekstu.
- Wymagania: w issue wskazano NFR-SEC-05, lecz w [WYMAGANIA.md](../WYMAGANIA.md) dotyczy on sekretów; łańcuch dostaw nie ma osobnego identyfikatora, więc powiązanie jest informacyjne.

## Konsekwencje

- **Zysk.** W przebiegu delta (3 pliki LWC) krok wdrożenia trwał 4 s zamiast ok. 33 s, a job scratch orga 58 s zamiast mediany 97 s; ścieżką krytyczną staje się wtedy PR validation. Dane: [delta.csv](../experiment/results/delta.csv), dowody w logu etapu M1 (sekcja #122).
- **Koszt błędnej delty.** Wdrożenie delty może zawieść z powodu brakującej niezmienionej zależności; zaobserwowano to dla paczki `digitalExperiences` (`The site/Insurance_Portal1 workspace doesn't exist`, [przebieg 42505086736](https://github.com/Yibux/insurance-app/actions/runs/42505086736)). Skutek: ok. 4 s straty i pełny deploy (113 s całego potoku zamiast ok. 102 s mediany). Folder `digitalExperiences` i pokrewne metadane Experience Cloud wyłączono z listy dozwolonych właśnie z tego powodu. Prawdziwy błąd w delcie powtórzy się w pełnym deployu, który wyda ostateczny werdykt.
- **Zakres praktyczny jest wąski i tak ma być.** Gdy repozytorium zyska Apex i obiekty, większość PR da pełny deploy; delta pomaga głównie PR-om dotykającym wyłącznie LWC/Aura. Jest to wynik do zapisania w eksperymencie (M6): różnica czasu delta vs pełny wystąpi tylko w części PR.
- **Założenie: baza przeszła pełną walidację.** Delta sprawdza tylko zmiany PR względem bazy i zakłada, że `main` jest zielony w pełnej walidacji (testy, pokrycie). Obecnie nic tego nie wymusza: brak wymaganych checków na `main` (#25, #6) i brak przebiegu pełnej walidacji po push do `main`. Mitygacja: **odroczona do #25/#6** (wymagane checki na `main`); opcjonalnie dodatkowo zaplanowany lub po-merge'owy pełny przebieg walidacji, jeśli pomiary pokażą taką potrzebę. Do tego czasu delta może przepuścić regresję odziedziczoną z bazy.
- **Pomijanie testów Apex w trybie delta** opiera się na założeniu niezależności LWC/Aura od wyniku testów; założenie wymaga ponownej oceny przy każdym rozszerzeniu `DELTA_ELIGIBLE_FOLDERS`.
- **Oczekiwanie dla #24 (deploy na org docelowy).** Tam org nie jest pusty, a usunięcia trzeba stosować; wtedy `sfdx-git-delta` (manifest zniszczeń) ma sens i wymaga osobnej oceny łańcucha dostaw (np. dodanie do `package.json` z lockfile, objęcie Dependabotem).
- **Ograniczenia weryfikacji.** Nie przetestowano w CI gałęzi: przebieg z błędem samego planisty (pokryty testem jednostkowym i `continue-on-error`), diff z nazwą pliku zawierającą znak nowej linii (pokryty testem jednostkowym), duża delta (test jednostkowy).
- Dokument potoku [potok-cicd.md](../architektura/potok-cicd.md) opisuje reguły w sekcji „Delta deployment”.
