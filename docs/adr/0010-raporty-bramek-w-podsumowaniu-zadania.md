# 0010. Raporty bramek: podsumowanie zadania, artefakty i czasy z API Actions

- **Status:** przyjęta
- **Data:** 2026-11-02
- **Issue:** #22
- **Wymagania:** FR-CI-07, NFR-OBS-02

## Kontekst

Wyniki bramek (testy, pokrycie, Code Analyzer, gitleaks) były widoczne tylko w logach. Praca potrzebuje ich w formie czytelnej dla recenzenta PR oraz czasów trwania każdej bramki jako danych wejściowych eksperymentu (M6). Czasy muszą dać się zebrać bez przepisywania każdego kroku workflowu.

## Rozważane opcje

1. **Pomiar własny** (`date +%s` przed i po każdym kroku, zapis do pliku) — wady: zaśmieca każdy workflow, nie obejmuje kroków akcji, łatwo o pominięcie.
2. **Zewnętrzna akcja do podsumowań/metryk** — wady: dodatkowa zależność w łańcuchu dostaw, mniejsza kontrola nad formatem.
3. **Odczyt czasów kroków z API Actions** (`/actions/runs/{id}/attempts/{n}/jobs`) w ostatnim kroku joba, własny skrypt Pythona i lokalna akcja kompozytowa — wybrane.

## Decyzja

Opcja 3. Skrypt `scripts/ci/gate_report.py` (biblioteka standardowa, z testami) generuje trzy tabele Markdown do `$GITHUB_STEP_SUMMARY`: wyniki testów Apex, liczby naruszeń Code Analyzera wg wagi i czasy kroków. Lokalna akcja `.github/actions/gate-durations` odpytuje API przez `gh` z tokenem `GITHUB_TOKEN` (uprawnienie `actions: read` tylko w jobach, które jej używają) i wysyła surowe wiersze jako artefakt `gate-durations-*`. Surowe raporty trafiają do artefaktów: wyniki testów Apex (już były), `code-analyzer-report` (SARIF, HTML, JSON), `gitleaks-report`.

## Konsekwencje

- Czas ostatniego kroku (samego raportowania) jest zapisany jako „running”, a czas całego joba to czas do chwili raportu — niedokładność rzędu sekund, akceptowalna dla eksperymentu.
- Błąd API nie oblewa bramki (ostrzeżenie i pusta tabela).
- Pokrycie nadal raportuje `check_coverage.py` (tabela per klasa).
- Akcja lokalna nie jest objęta Dependabotem dla `github-actions` w katalogu `/`; jej zależność (`upload-artifact`) ma ten sam SHA co workflowy.
- Dokument potoku (`docs/architektura/potok-cicd.md`) wymaga aktualizacji przed 2026-12-06.
