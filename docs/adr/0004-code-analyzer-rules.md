# 0004. Dobór reguł Salesforce Code Analyzer i próg blokowania PR

- **Status:** przyjęta
- **Data:** 2026-11-02
- **Issue:** #18
- **Wymagania:** FR-CI-04, FR-CI-07, NFR-SEC-03, NFR-SEC-04

## Kontekst

Każdy PR musi przejść analizę statyczną (SAST) kodu Salesforce, a naruszenia o wysokiej wadze mają go blokować (FR-CI-04). Salesforce Code Analyzer v5 łączy kilka silników o różnym koszcie i zakresie. Za szeroki zestaw reguł zalewa PR szumem (np. reguły stylu i dokumentacji), więc bramkę trzeba wyłączyć albo zaczyna się ją ignorować. Za wąski przepuszcza podatności, które praca ma wykrywać w eksperymencie (M6): SOQL injection, brak CRUD/FLS, obejście sharingu.

## Rozważane opcje

1. **Wszystkie reguły wszystkich silników** — maksymalne pokrycie, ale setki ostrzeżeń stylu i ApexDoc, a próg trzeba by ustawić tak nisko, że przestaje blokować.
2. **Domyślny zestaw `Recommended` bez zmian** — rozsądny punkt startowy, ale w testach (patrz „Weryfikacja”) nie zgłasza jawnego `without sharing` ani braku deklaracji sharingu, choć wymaga tego NFR-SEC-03.
3. **`Recommended` dla wybranych silników + uzupełnienie o reguły bezpieczeństwa z wymagań** — wybrany.

## Decyzja

Silniki i selektory (w `.github/workflows/pr-validation.yml`):

| Selektor                     | Silnik                       | Po co                                                                                |
| ---------------------------- | ---------------------------- | ------------------------------------------------------------------------------------ |
| `pmd:Recommended`            | PMD (Apex, Visualforce, XML) | SOQL injection, CRUD/FLS, sharing, błędy wydajności (SOQL/DML w pętli)               |
| `eslint:Recommended`         | ESLint (LWC, Aura, JS)       | podatności i błędy w kodzie front-endu (np. niebezpieczne `innerHTML`)               |
| `retire-js`                  | RetireJS                     | znane podatne biblioteki JS (np. w static resources)                                 |
| `flow`                       | Flow Scanner                 | niebezpieczne wzorce we Flow (uruchamianie w trybie systemowym, brak obsługi błędów) |
| `sfge`                       | Salesforce Graph Engine      | analiza ścieżek: CRUD/FLS śledzony przez wywołania metod (dokładniejszy niż PMD)     |
| `regex:ApexNoWithoutSharing` | Regex (reguła własna)        | jawne `without sharing` (NFR-SEC-03)                                                 |

Uzupełnienia w `code-analyzer.yml`:

- `pmd:ApexSharingViolations` dołączona do `Recommended` z wagą **2**: klasa wykonująca DML/SOQL bez deklaracji sharingu.
- Własna reguła regex `ApexNoWithoutSharing` z wagą **2**: PMD nie zgłasza jawnego `without sharing`. Wyjątek wymaga ADR i jawnego wyciszenia.

**Próg:** `--severity-threshold 2` — job oblewa się przy naruszeniach **Critical (1)** i **High (2)**. Naruszenia Moderate/Low (3–5) są raportowane w tabeli, SARIF i raporcie HTML, ale nie blokują.

**Raportowanie (FR-CI-07):** SARIF wysyłany do GitHub code scanning (`category: salesforce-code-analyzer`) także wtedy, gdy bramka się obleje, więc alerty widać w zakładce _Files changed_ PR; raport HTML jako artefakt `code-analyzer-report`.

Wersje są przypięte (`@salesforce/cli` 2.156.8, `code-analyzer` 5.16.0), żeby zmiana zestawu reguł w nowej wersji nie zmieniała wyników eksperymentu bez naszej wiedzy.

## Weryfikacja

Tymczasowe klasy Apex z celowymi podatnościami (usunięte przed merge'em):

| Podatność                                 | Reguła                       | Waga | Wynik   |
| ----------------------------------------- | ---------------------------- | ---- | ------- |
| `Database.query` z konkatenacją parametru | `pmd:ApexSOQLInjection`      | 2    | blokuje |
| `update` bez sprawdzenia CRUD             | `pmd:ApexCRUDViolation`      | 2    | blokuje |
| jawne `without sharing`                   | `regex:ApexNoWithoutSharing` | 2    | blokuje |
| klasa z DML bez deklaracji sharingu       | `pmd:ApexSharingViolations`  | 2    | blokuje |
| brak komentarzy ApexDoc                   | `pmd:ApexDoc`                | 4    | raport  |

Przed dodaniem dwóch ostatnich reguł bezpieczeństwa oba przypadki sharingu przechodziły niezauważone.

## Konsekwencje

- Wygenerowane metadane strony Experience Cloud (`digitalExperiences/**/styles.css`) dają 2 naruszenia Low (`slds/no-hardcoded-values-slds2`) — nie blokują, zostają w raporcie.
- Uzasadnione użycie `without sharing` (np. w M3 dla operacji gościa portalu) wymaga ADR i wyciszenia w kodzie.
- Graph Engine jest najwolniejszy; przy obecnym kodzie to kilka sekund, czas joba będzie mierzony w eksperymencie (NFR-PERF-05). Jeśli zacznie dominować, można go przenieść do osobnego joba lub uruchamiać tylko dla zmian w Apex.
- Aktualizacja wersji Code Analyzer to świadoma zmiana (PR z porównaniem wyników), a nie automatyczny Dependabot.
