# 0005. CodeQL jako osobny workflow z pakietem `security-extended`

- **Status:** przyjęta
- **Data:** 2026-11-02
- **Issue:** #20
- **Wymagania:** FR-CI-06

## Kontekst

Code Analyzer (ADR 0004) analizuje kod Salesforce, ale jego silnik ESLint ma ograniczoną analizę przepływu danych. FR-CI-06 wymaga uzupełnienia go o CodeQL dla JavaScriptu (teraz: komponenty LWC i skrypty w `scripts/`) i Pythona (od M4, #58), z wynikami w zakładce Security.

## Rozważane opcje

1. **Domyślna konfiguracja CodeQL (ustawienia repozytorium)** — zero plików w repo, ale konfiguracji nie da się przejrzeć w PR, przypiąć wersji akcji ani rozszerzyć o język w tym samym PR, który go wprowadza.
2. **Osobny workflow `codeql.yml`** — wybrany; konfiguracja jako kod, spójna z resztą potoku.
3. **Dodatkowy job w `pr-validation.yml`** — odrzucone: harmonogram tygodniowy i uruchomienie na `push` do `main` nie pasują do tego pliku, a awaria CodeQL zaciemniałaby wynik pozostałych bramek.

## Decyzja

- Wyzwalacze: `pull_request` do `main`, `push` do `main` (punkt odniesienia, bez którego GitHub nie porównuje alertów PR z gałęzią bazową) oraz `schedule` raz w tygodniu (nowe zapytania CodeQL bez zmian w kodzie).
- Język `javascript-typescript`, `build-mode: none` (język interpretowany); kolejny język dopisujemy do macierzy `language`.
- Pakiet zapytań `security-extended` zamiast domyślnego: więcej zapytań bezpieczeństwa o niższej precyzji; przy małej bazie kodu koszt fałszywych alarmów jest niski, a eksperyment M6 mierzy wykrywalność.
- Akcje przypięte do SHA (v4.39.1), uprawnienie `security-events: write` tylko w jobie, `persist-credentials: false`.
- Workflow nie ma filtra `paths:`: analiza nie wymaga scratch orga, więc nie zużywa limitu, a check jest zawsze obecny.

## Konsekwencje

- Workflow **raportuje** do code scanning, ale sam nie oblewa PR przy znalezieniu alertu. Blokowanie wymaga reguły „Code scanning results” w rulesecie `main` (ustawienie repozytorium, do zrobienia przez właściciela razem z pozostałymi wymaganymi checkami).
- Dopóki w repozytorium włączona jest konfiguracja domyślna CodeQL, nie można jej łączyć z tym workflow (obecnie `not-configured`).
