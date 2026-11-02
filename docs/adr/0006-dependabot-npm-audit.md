# 0006. Dependabot (npm, github-actions) i bramka `npm audit --audit-level=high`

- **Status:** przyjęta
- **Data:** 2026-11-02
- **Issue:** #21
- **Wymagania:** FR-CI-05

## Kontekst

FR-CI-05 wymaga wykrywania podatnych zależności. Projekt ma zależności npm (narzędzia: ESLint, Prettier, Jest, Husky) i akcje GitHub przypięte do SHA. Przypięcie do SHA daje powtarzalność, ale bez automatu aktualizacje przestają napływać. Zależności Pythona pojawią się w M4 (#58).

## Rozważane opcje

1. **Tylko Dependabot alerts / security updates (ustawienia repozytorium)** — powiadamia, ale nie blokuje PR i nie aktualizuje akcji przypiętych do SHA.
2. **`dependabot.yml` (version updates) + krok `npm audit` w PR** — wybrane: Dependabot dostarcza aktualizacje (też akcji, wraz z komentarzem wersji przy SHA), `npm audit` blokuje PR przy nowych poważnych podatnościach.
3. **Zewnętrzny skaner SCA (np. Snyk, OSV-Scanner)** — odrzucone: dodatkowa zależność i konto, bez zysku przy tak małym drzewie zależności.

## Decyzja

- `.github/dependabot.yml`: ekosystemy `npm` i `github-actions`, cotygodniowo (poniedziałek), limit 5 otwartych PR-ów na ekosystem, aktualizacje minor/patch npm grupowane w jeden PR, wszystkie akcje w jednym PR; prefiksy commitów `chore(deps)` i `chore(ci)` zgodne z Conventional Commits. Ekosystem `pip` zostanie dopisany w #58.
- Krok `npm audit --audit-level=high` w jobie `static-checks` (`pr-validation.yml`), po `npm ci`. Obejmuje pełne drzewo, także zależności deweloperskie — uruchamiają się w CI i na maszynach deweloperów (hook Husky).
- `cooldown: default-days: 7` w obu ekosystemach: nowa wersja trafia do PR najwcześniej po tygodniu od publikacji. Ogranicza to ryzyko świeżo opublikowanej, złośliwej wersji (typowy atak na łańcuch dostaw jest wykrywany i wycofywany w ciągu dni), ale to złagodzenie, nie ochrona — patrz „Konsekwencje”.
- Grupy akcji obejmują tylko aktualizacje minor i patch; wersje major przychodzą osobnymi PR-ami do indywidualnej oceny. Akcje używane także w `scratch-org-validation.yml` (`actions/checkout`, `actions/setup-node`, `actions/upload-artifact`) są w osobnej grupie `actions-scratch-org`, pozostałe (CodeQL) w `actions-other`.
- Aktualizacje Dependabota przechodzą przez te same bramki co zwykłe PR-y.

## Konsekwencje

- Nowa porada o wadze high/critical dla dowolnej zależności (także tranzytywnej) oblewa **każdy** PR, również niezwiązany z zależnościami, aż do poprawki. To zamierzone (bramka bezpieczeństwa), ale bywa uciążliwe; wyjątki wymagałyby jawnego wpisu i uzasadnienia, a nie obniżenia progu.
- Poziomy low i moderate nie blokują (w momencie wprowadzenia: 45 takich porad w narzędziach deweloperskich); są widoczne w `npm audit` i alertach Dependabota.
- `npm audit` zależy od bazy GitHub Advisory Database, więc wynik tego samego commita może zmienić się w czasie.
- **Aktualizacje akcji a scratch org:** `scratch-org-validation.yml` jest w `paths` własnego wyzwalacza, więc PR Dependabota zmieniający akcje w tym pliku uruchamia walidację scratch org i zużywa org z limitu 6/dobę. PR Dependabota nie ma dostępu do sekretów Environment `devhub`, więc ta walidacja kończy się błędem autoryzacji. Dependabot nie pozwala grupować wg pliku, a trzy wspólne akcje występują we wszystkich workflowach, więc pełnego wyłączenia się nie da osiągnąć bez rezygnacji z ich aktualizacji. Wybrano rozwiązanie najmniej inwazyjne: osobna grupa `actions-scratch-org` (najwyżej jeden taki PR minor/patch tygodniowo, czyli jeden org), a czerwony check scratch org w takim PR jest oczekiwany i obsługuje go właściciel ręcznie (zmiany akcji weryfikują `PR validation` i CodeQL; właściciel scala PR świadomie mimo czerwonego checku scratch org). Odrzucone: `ignore` tych akcji (przestaną być aktualizowane, a są przypięte do SHA) oraz warunek w `scratch-org-validation.yml` (zmiana pliku z `paths` sama zużyłaby org).
- **Wersje świeżo opublikowane (przykład FN dla M6):** `cooldown` nie wykryje złośliwej wersji starszej niż 7 dni, a `npm audit` zna tylko porady już opublikowane w bazie — podatność lub paczka złośliwa przed zgłoszeniem przejdzie obie bramki. To kategoria fałszywie negatywnego wyniku do opisania w eksperymencie M6.
- **Dependabot alerts i security updates** są ustawieniem repozytorium (Settings → Code security), a nie plikiem `dependabot.yml`; plik konfiguruje wyłącznie aktualizacje wersji. Włączenie alertów należy do właściciela repozytorium.
