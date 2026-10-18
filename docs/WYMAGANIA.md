# Specyfikacja wymagań

- **Temat:** Projekt i implementacja bezpiecznego systemu obsługi ubezpieczeń z wykorzystaniem metodyki DevSecOps w ekosystemie Salesforce
- **Powiązane:** [RAPORT.md](RAPORT.md) · [HARMONOGRAM.md](HARMONOGRAM.md) · [KONWENCJE.md](KONWENCJE.md) · [BACKLOG.md](BACKLOG.md)
- **Wersja:** 0.1 (18.10.2026) — do przeglądu z promotorem

Priorytety według **MoSCoW**: **M** (Must), **S** (Should), **C** (Could), **W** (Won't, poza zakresem tej wersji).
Etap odpowiada numerowi z [harmonogramu](HARMONOGRAM.md#2-harmonogram-start-12102026-kod-zamrożony-15062027-oddanie-ix-2027) (M0–M8).

---

## 1. Aktorzy

| Aktor                 | Opis                                                                | Kanał                      |
| --------------------- | ------------------------------------------------------------------- | -------------------------- |
| **Ubezpieczony**      | Klient posiadający polisę; przegląda polisy, zgłasza szkody         | Portal Experience Cloud    |
| **Agent**             | Pracownik obsługujący klientów i polisy w swoim portfelu            | Lightning Experience       |
| **Likwidator szkód**  | Ocenia i rozlicza zgłoszone szkody                                  | Lightning Experience       |
| **Administrator**     | Zarządza konfiguracją, użytkownikami, uprawnieniami                 | Setup, SF CLI              |
| **System zewnętrzny** | Backend Python: ładowanie danych historycznych, źródło danych OData | REST / Bulk API 2.0, OData |
| **Potok CI/CD**       | GitHub Actions: walidacja zmian, bramki bezpieczeństwa, wdrożenia   | SF CLI (JWT), GitHub API   |

---

## 2. Wymagania funkcjonalne

### 2.1 Polisy (FR-POL)

| ID        | Wymaganie                                                                                                 | Prio | Etap | Weryfikacja                       |
| --------- | --------------------------------------------------------------------------------------------------------- | ---- | ---- | --------------------------------- |
| FR-POL-01 | System przechowuje polisy (`Policy__c`): numer, typ produktu, ubezpieczony, agent, okres, składka, status | M    | 2    | Test Apex, metadane obiektu       |
| FR-POL-02 | Polisa ma zakresy ochrony (`Coverage__c`) z sumą ubezpieczenia i udziałem własnym                         | M    | 2    | Test Apex                         |
| FR-POL-03 | Status polisy przechodzi wyłącznie po dozwolonych ścieżkach (Draft → Active → Expired/Cancelled)          | M    | 2    | Reguły walidacji + test negatywny |
| FR-POL-04 | Agent widzi i edytuje wyłącznie polisy ze swojego portfela                                                | M    | 2    | Test `System.runAs`               |
| FR-POL-05 | System automatycznie oznacza polisy jako wygasłe po dacie końcowej                                        | S    | 2    | Test zaplanowanego zadania / Flow |

### 2.2 Szkody (FR-CLM)

| ID        | Wymaganie                                                                                             | Prio | Etap | Weryfikacja                        |
| --------- | ----------------------------------------------------------------------------------------------------- | ---- | ---- | ---------------------------------- |
| FR-CLM-01 | Szkoda (`Claim__c`) jest powiązana z aktywną polisą i zakresem ochrony obowiązującym w dniu zdarzenia | M    | 2    | Test Apex (przypadki brzegowe dat) |
| FR-CLM-02 | Cykl życia szkody: Submitted → Under Review → Approved/Rejected → Paid → Closed, z kontrolą przejść   | M    | 2    | Test triggera                      |
| FR-CLM-03 | Szkoda może mieć załączniki (`Claim_Document__c` + Files)                                             | M    | 2–3  | Test Apex + Jest                   |
| FR-CLM-04 | Nowa szkoda jest automatycznie przydzielana do likwidatora (kolejka / reguła przydziału)              | S    | 2    | Test Apex                          |
| FR-CLM-05 | Kwota wypłaty nie może przekroczyć sumy ubezpieczenia pomniejszonej o udział własny                   | M    | 2    | Test negatywny                     |
| FR-CLM-06 | Zmiany statusu szkody są audytowane (historia pól)                                                    | S    | 2    | Field History Tracking             |

### 2.3 Portal klienta (FR-PRT)

| ID        | Wymaganie                                                                                    | Prio | Etap | Weryfikacja                             |
| --------- | -------------------------------------------------------------------------------------------- | ---- | ---- | --------------------------------------- |
| FR-PRT-01 | Ubezpieczony loguje się do portalu (Experience Cloud LWR); brak dostępu dla gościa do danych | M    | 3    | Test manualny + konfiguracja            |
| FR-PRT-02 | Ubezpieczony widzi listę **własnych** polis i ich szczegóły z zakresami                      | M    | 3    | Jest + test `runAs` użytkownika portalu |
| FR-PRT-03 | Ubezpieczony zgłasza szkodę formularzem z walidacją i załącznikami                           | M    | 3    | Jest + test Apex kontrolera             |
| FR-PRT-04 | Ubezpieczony śledzi status swoich szkód                                                      | M    | 3    | Jest                                    |
| FR-PRT-05 | Ubezpieczony widzi historię płatności pochodzącą z systemu zewnętrznego (External Object)    | S    | 5    | Test manualny / integracyjny            |

### 2.4 Komunikacja z agentem (FR-COM)

| ID        | Wymaganie                                                                                    | Prio | Etap | Weryfikacja      |
| --------- | -------------------------------------------------------------------------------------------- | ---- | ---- | ---------------- |
| FR-COM-01 | Ubezpieczony wysyła wiadomość/zapytanie do swojego agenta z poziomu polisy lub szkody (Case) | M    | 3    | Jest + test Apex |
| FR-COM-02 | Agent odpowiada w Lightning; odpowiedź jest widoczna w portalu                               | M    | 3    | Test manualny    |
| FR-COM-03 | Ubezpieczony otrzymuje powiadomienie e-mail o zmianie statusu szkody                         | C    | 3    | Test manualny    |

### 2.5 Migracja danych historycznych (FR-MIG)

| ID        | Wymaganie                                                                                   | Prio | Etap | Weryfikacja                    |
| --------- | ------------------------------------------------------------------------------------------- | ---- | ---- | ------------------------------ |
| FR-MIG-01 | Serwer Python ładuje dane historyczne (klienci, polisy, szkody) przez Bulk API 2.0          | M    | 4    | pytest + test na scratch orgu  |
| FR-MIG-02 | Ładowanie jest idempotentne (upsert po External ID) i wznawialne po błędzie                 | M    | 4    | pytest (powtórne uruchomienie) |
| FR-MIG-03 | Rekordy odrzucone są raportowane z przyczyną, a z przebiegu powstaje raport audytowy        | M    | 4    | pytest                         |
| FR-MIG-04 | Dostępny jest generator syntetycznych danych testowych (bez danych osobowych realnych osób) | M    | 4    | pytest                         |

### 2.6 External Objects (FR-EXT)

| ID        | Wymaganie                                                                                      | Prio | Etap | Weryfikacja                        |
| --------- | ---------------------------------------------------------------------------------------------- | ---- | ---- | ---------------------------------- |
| FR-EXT-01 | Backend udostępnia endpoint OData 4.0 z danymi wrażliwymi (np. historia płatności)             | M    | 5    | Testy kontraktowe pytest           |
| FR-EXT-02 | Salesforce prezentuje te dane jako External Object (Salesforce Connect) bez kopiowania do CRM  | M    | 5    | Test manualny, brak rekordów w CRM |
| FR-EXT-03 | Dostęp do External Object podlega uprawnieniom (permission set) i filtrowaniu per ubezpieczony | M    | 5    | Test manualny / integracyjny       |

### 2.7 Potok CI/CD (FR-CI)

| ID       | Wymaganie                                                                                                       | Prio | Etap | Weryfikacja                   |
| -------- | --------------------------------------------------------------------------------------------------------------- | ---- | ---- | ----------------------------- |
| FR-CI-01 | Każdy PR uruchamia walidację: lint, formatowanie, testy Jest                                                    | M    | 1    | Przebieg workflow             |
| FR-CI-02 | Każdy PR tworzy efemeryczny scratch org, wdraża metadane, uruchamia testy Apex i usuwa org (także przy błędzie) | M    | 1    | Przebieg workflow             |
| FR-CI-03 | Potok blokuje PR przy pokryciu testami Apex < 75%                                                               | M    | 1    | PR testowy z niskim pokryciem |
| FR-CI-04 | Potok uruchamia Salesforce Code Analyzer i blokuje PR przy naruszeniach severity ≤ 2                            | M    | 1    | PR testowy z naruszeniem      |
| FR-CI-05 | Potok wykrywa sekrety (gitleaks) i podatne zależności (Dependabot, npm audit, pip-audit)                        | M    | 1, 4 | PR testowy                    |
| FR-CI-06 | Potok uruchamia CodeQL dla JS i Python                                                                          | S    | 1, 4 | Zakładka Security             |
| FR-CI-07 | Wyniki skanów są publikowane w PR (summary, artefakty, SARIF)                                                   | S    | 1    | Widok PR                      |
| FR-CI-08 | Merge do `main` wdraża zmiany na org docelowy po akceptacji w GitHub Environment                                | M    | 1    | Przebieg workflow             |
| FR-CI-09 | Hook pre-commit uruchamia formatowanie, lint i skan sekretów lokalnie                                           | S    | 1    | Commit testowy                |

---

## 3. Wymagania niefunkcjonalne

### 3.1 Bezpieczeństwo (NFR-SEC)

| ID         | Wymaganie                                                                                                             | Prio | Etap | Weryfikacja                          |
| ---------- | --------------------------------------------------------------------------------------------------------------------- | ---- | ---- | ------------------------------------ |
| NFR-SEC-01 | Model Zero-Trust: OWD **Private** dla obiektów biznesowych, dostęp nadawany wyłącznie przez sharing i permission sets | M    | 2    | Przegląd metadanych + testy `runAs`  |
| NFR-SEC-02 | Uprawnienia oparte o Permission Sets / PSG (zasada najmniejszych uprawnień); profile minimalne                        | M    | 2    | Macierz uprawnień                    |
| NFR-SEC-03 | Cały kod Apex działa `with sharing` i egzekwuje CRUD/FLS (`WITH USER_MODE`, `stripInaccessible`)                      | M    | 2    | Code Analyzer + testy                |
| NFR-SEC-04 | Brak dynamicznego SOQL bez bind variables (ochrona przed SOQL injection)                                              | M    | 2    | Code Analyzer                        |
| NFR-SEC-05 | Brak sekretów w repozytorium; sekrety w GitHub Encrypted Secrets / Environments                                       | M    | 0–1  | gitleaks                             |
| NFR-SEC-06 | CI i backend uwierzytelniają się w Salesforce JWT Bearer Flow (bez haseł), sesje krótkotrwałe                         | M    | 0, 4 | Konfiguracja + przegląd              |
| NFR-SEC-07 | Użytkownik portalu ma dostęp wyłącznie do rekordów własnego konta (Sharing Sets, Restriction Rules)                   | M    | 3    | Test penetracyjny manualny + `runAs` |
| NFR-SEC-08 | Komunikacja Salesforce ↔ backend wyłącznie po HTTPS, uwierzytelniona (Named/External Credential)                      | M    | 5    | Konfiguracja + test                  |
| NFR-SEC-09 | Komponenty LWC odporne na XSS (brak `innerHTML` z danymi użytkownika, Lightning Web Security)                         | M    | 3    | ESLint LWC + Code Analyzer           |
| NFR-SEC-10 | Upload plików: limit rozmiaru i dozwolone typy MIME                                                                   | S    | 3    | Test Jest/Apex                       |
| NFR-SEC-11 | Branch protection na `main`: wymagane zielone checki i review, brak force-push                                        | M    | 0    | Ustawienia repo                      |

### 3.2 Jakość i testowalność (NFR-QA)

| ID        | Wymaganie                                                                             | Prio | Etap | Weryfikacja         |
| --------- | ------------------------------------------------------------------------------------- | ---- | ---- | ------------------- |
| NFR-QA-01 | Pokrycie kodu Apex ≥ 75% (bramka), cel ≥ 85%                                          | M    | 1–2  | `check_coverage.py` |
| NFR-QA-02 | Pokrycie LWC (Jest) ≥ 70%                                                             | S    | 3    | Raport Jest         |
| NFR-QA-03 | Pokrycie backendu Python (pytest-cov) ≥ 80%                                           | S    | 4    | Raport pytest-cov   |
| NFR-QA-04 | Kod zgodny z Prettier / ESLint / ruff; spójny styl wymuszany w CI                     | M    | 1    | CI                  |
| NFR-QA-05 | Testy Apex używają fabryki danych, nie polegają na danych z orga (`SeeAllData=false`) | M    | 2    | Przegląd kodu       |

### 3.3 Wydajność i limity (NFR-PERF)

| ID          | Wymaganie                                                                                   | Prio | Etap | Weryfikacja                 |
| ----------- | ------------------------------------------------------------------------------------------- | ---- | ---- | --------------------------- |
| NFR-PERF-01 | Pełna walidacja PR trwa ≤ 20 min (mediana)                                                  | S    | 1, 6 | Pomiar w eksperymencie      |
| NFR-PERF-02 | Logika Apex jest „bulkified” (brak SOQL/DML w pętli), poprawna dla 200 rekordów w triggerze | M    | 2    | Test masowy + Code Analyzer |
| NFR-PERF-03 | Loader obsługuje ≥ 100 000 rekordów w jednym przebiegu                                      | S    | 4    | Pomiar                      |
| NFR-PERF-04 | Endpoint OData odpowiada ≤ 2 s dla stron do 100 rekordów                                    | S    | 5    | Pomiar                      |
| NFR-PERF-05 | Potok mieści się w limitach Dev Hub DE (≤ 3 aktywne scratch orgi, ≤ 6/dzień)                | M    | 1    | Konfiguracja concurrency    |

### 3.4 Utrzymywalność i dokumentacja (NFR-MNT)

| ID         | Wymaganie                                                                                | Prio | Etap | Weryfikacja              |
| ---------- | ---------------------------------------------------------------------------------------- | ---- | ---- | ------------------------ |
| NFR-MNT-01 | Cała konfiguracja jako kod (metadane w `force-app/`, workflowy, definicje orgów)         | M    | 0–5  | Odtworzenie z repo       |
| NFR-MNT-02 | Architektura warstwowa Apex: trigger → handler → serwis → selektor                       | M    | 2    | Przegląd kodu            |
| NFR-MNT-03 | Decyzje architektoniczne zapisane jako ADR w `docs/adr/`                                 | M    | 0–6  | Przegląd docs            |
| NFR-MNT-04 | Każde zadanie zostawia wpis w `docs/implementacja/` (patrz [KONWENCJE.md](KONWENCJE.md)) | M    | 0–6  | DoD w PR                 |
| NFR-MNT-05 | Środowisko deweloperskie odtwarzalne jedną sekwencją poleceń (README)                    | S    | 0    | Test na czystej maszynie |

### 3.5 Użyteczność i dostępność (NFR-UX)

| ID        | Wymaganie                                                              | Prio | Etap | Weryfikacja      |
| --------- | ---------------------------------------------------------------------- | ---- | ---- | ---------------- |
| NFR-UX-01 | Portal zgodny z WCAG 2.1 AA (kontrast, nawigacja klawiaturą, etykiety) | S    | 3    | axe / Lighthouse |
| NFR-UX-02 | Portal responsywny (telefon, desktop)                                  | M    | 3    | Test manualny    |
| NFR-UX-03 | Komunikaty błędów zrozumiałe dla klienta, bez szczegółów technicznych  | M    | 3    | Przegląd         |

### 3.6 Zgodność i dane (NFR-CMP)

| ID         | Wymaganie                                                                                       | Prio | Etap | Weryfikacja      |
| ---------- | ----------------------------------------------------------------------------------------------- | ---- | ---- | ---------------- |
| NFR-CMP-01 | Dane wrażliwe (płatności) pozostają w systemie źródłowym — rezydencja danych (External Objects) | M    | 5    | Brak kopii w CRM |
| NFR-CMP-02 | W środowiskach deweloperskich/CI używane są wyłącznie dane syntetyczne                          | M    | 2, 4 | Przegląd         |
| NFR-CMP-03 | Minimalizacja danych osobowych zgodnie z RODO (tylko pola niezbędne do procesu)                 | S    | 2    | Przegląd modelu  |

### 3.7 Obserwowalność i audyt (NFR-OBS)

| ID         | Wymaganie                                                                                 | Prio | Etap | Weryfikacja    |
| ---------- | ----------------------------------------------------------------------------------------- | ---- | ---- | -------------- |
| NFR-OBS-01 | Backend loguje operacje strukturalnie (JSON) bez danych wrażliwych                        | M    | 4    | Przegląd logów |
| NFR-OBS-02 | Każde wdrożenie i wynik bramek są śledzone (historia GitHub Actions, artefakty)           | M    | 1    | GitHub         |
| NFR-OBS-03 | Błędy Apex są logowane w sposób umożliwiający diagnozę (np. obiekt logu / Platform Event) | C    | 2    | Test           |

---

## 4. Poza zakresem (W)

- Rozliczenia finansowe i integracja z systemem płatności.
- Kalkulacja składki (rating engine) — składka wprowadzana ręcznie lub z danych historycznych.
- Financial Services Cloud (wymaga licencji niedostępnej w DE/scratch, patrz ADR-002).
- Aplikacja mobilna natywna.

---

## 5. Macierz śledzenia

Kolumna **Issues** jest uzupełniana przez `scripts/github/create-backlog.mjs` na podstawie pola `requirements` w [backlog.json](../scripts/github/backlog.json). Kolumna **Literatura** odwołuje się do tabeli w [RAPORT.md](RAPORT.md#3-przegląd-literatury).

<!-- TRACEABILITY:START -->

| Wymaganie   | Issues                                                                                                                                                                                                                                                                                      | Literatura                            |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| FR-CI-01    | [#14](https://github.com/Yibux/insurance-app/issues/14)                                                                                                                                                                                                                                     | —                                     |
| FR-CI-02    | [#16](https://github.com/Yibux/insurance-app/issues/16)                                                                                                                                                                                                                                     | Guduru 2023; SF DX Guide              |
| FR-CI-03    | [#17](https://github.com/Yibux/insurance-app/issues/17)                                                                                                                                                                                                                                     | Bavadiya 2022                         |
| FR-CI-04    | [#18](https://github.com/Yibux/insurance-app/issues/18), [#74](https://github.com/Yibux/insurance-app/issues/74)                                                                                                                                                                            | Bavadiya 2022; IEEE/ACM 2022          |
| FR-CI-05    | [#19](https://github.com/Yibux/insurance-app/issues/19), [#21](https://github.com/Yibux/insurance-app/issues/21), [#58](https://github.com/Yibux/insurance-app/issues/58), [#74](https://github.com/Yibux/insurance-app/issues/74)                                                          | IEEE 2025 SLR                         |
| FR-CI-06    | [#20](https://github.com/Yibux/insurance-app/issues/20), [#58](https://github.com/Yibux/insurance-app/issues/58)                                                                                                                                                                            | Cheenepalli i in. 2025                |
| FR-CI-07    | [#18](https://github.com/Yibux/insurance-app/issues/18), [#22](https://github.com/Yibux/insurance-app/issues/22)                                                                                                                                                                            | —                                     |
| FR-CI-08    | [#24](https://github.com/Yibux/insurance-app/issues/24)                                                                                                                                                                                                                                     | —                                     |
| FR-CI-09    | [#19](https://github.com/Yibux/insurance-app/issues/19), [#23](https://github.com/Yibux/insurance-app/issues/23)                                                                                                                                                                            | Shift Left Security 2025              |
| FR-CLM-01   | [#29](https://github.com/Yibux/insurance-app/issues/29), [#31](https://github.com/Yibux/insurance-app/issues/31), [#35](https://github.com/Yibux/insurance-app/issues/35)                                                                                                                   | —                                     |
| FR-CLM-02   | [#36](https://github.com/Yibux/insurance-app/issues/36)                                                                                                                                                                                                                                     | —                                     |
| FR-CLM-03   | [#31](https://github.com/Yibux/insurance-app/issues/31), [#49](https://github.com/Yibux/insurance-app/issues/49)                                                                                                                                                                            | —                                     |
| FR-CLM-04   | [#37](https://github.com/Yibux/insurance-app/issues/37)                                                                                                                                                                                                                                     | —                                     |
| FR-CLM-05   | [#35](https://github.com/Yibux/insurance-app/issues/35)                                                                                                                                                                                                                                     | —                                     |
| FR-CLM-06   | [#31](https://github.com/Yibux/insurance-app/issues/31)                                                                                                                                                                                                                                     | —                                     |
| FR-COM-01   | [#51](https://github.com/Yibux/insurance-app/issues/51)                                                                                                                                                                                                                                     | —                                     |
| FR-COM-02   | [#43](https://github.com/Yibux/insurance-app/issues/43), [#51](https://github.com/Yibux/insurance-app/issues/51)                                                                                                                                                                            | —                                     |
| FR-COM-03   | [#52](https://github.com/Yibux/insurance-app/issues/52)                                                                                                                                                                                                                                     | —                                     |
| FR-EXT-01   | [#66](https://github.com/Yibux/insurance-app/issues/66)                                                                                                                                                                                                                                     | —                                     |
| FR-EXT-02   | [#9](https://github.com/Yibux/insurance-app/issues/9), [#69](https://github.com/Yibux/insurance-app/issues/69)                                                                                                                                                                              | Machapatri 2020                       |
| FR-EXT-03   | [#67](https://github.com/Yibux/insurance-app/issues/67), [#70](https://github.com/Yibux/insurance-app/issues/70)                                                                                                                                                                            | —                                     |
| FR-MIG-01   | [#61](https://github.com/Yibux/insurance-app/issues/61), [#63](https://github.com/Yibux/insurance-app/issues/63)                                                                                                                                                                            | Machapatri 2020                       |
| FR-MIG-02   | [#61](https://github.com/Yibux/insurance-app/issues/61)                                                                                                                                                                                                                                     | —                                     |
| FR-MIG-03   | [#62](https://github.com/Yibux/insurance-app/issues/62)                                                                                                                                                                                                                                     | —                                     |
| FR-MIG-04   | [#60](https://github.com/Yibux/insurance-app/issues/60)                                                                                                                                                                                                                                     | —                                     |
| FR-POL-01   | [#29](https://github.com/Yibux/insurance-app/issues/29), [#30](https://github.com/Yibux/insurance-app/issues/30)                                                                                                                                                                            | —                                     |
| FR-POL-02   | [#30](https://github.com/Yibux/insurance-app/issues/30)                                                                                                                                                                                                                                     | —                                     |
| FR-POL-03   | [#30](https://github.com/Yibux/insurance-app/issues/30)                                                                                                                                                                                                                                     | —                                     |
| FR-POL-04   | [#32](https://github.com/Yibux/insurance-app/issues/32), [#43](https://github.com/Yibux/insurance-app/issues/43)                                                                                                                                                                            | —                                     |
| FR-POL-05   | [#38](https://github.com/Yibux/insurance-app/issues/38)                                                                                                                                                                                                                                     | —                                     |
| FR-PRT-01   | [#8](https://github.com/Yibux/insurance-app/issues/8), [#45](https://github.com/Yibux/insurance-app/issues/45), [#46](https://github.com/Yibux/insurance-app/issues/46)                                                                                                                     | —                                     |
| FR-PRT-02   | [#48](https://github.com/Yibux/insurance-app/issues/48)                                                                                                                                                                                                                                     | —                                     |
| FR-PRT-03   | [#49](https://github.com/Yibux/insurance-app/issues/49)                                                                                                                                                                                                                                     | —                                     |
| FR-PRT-04   | [#50](https://github.com/Yibux/insurance-app/issues/50)                                                                                                                                                                                                                                     | —                                     |
| FR-PRT-05   | [#70](https://github.com/Yibux/insurance-app/issues/70)                                                                                                                                                                                                                                     | —                                     |
| NFR-CMP-01  | [#70](https://github.com/Yibux/insurance-app/issues/70), [#72](https://github.com/Yibux/insurance-app/issues/72)                                                                                                                                                                            | Machapatri 2020                       |
| NFR-CMP-02  | [#41](https://github.com/Yibux/insurance-app/issues/41), [#60](https://github.com/Yibux/insurance-app/issues/60)                                                                                                                                                                            | —                                     |
| NFR-CMP-03  | [#29](https://github.com/Yibux/insurance-app/issues/29)                                                                                                                                                                                                                                     | —                                     |
| NFR-MNT-01  | [#3](https://github.com/Yibux/insurance-app/issues/3), [#45](https://github.com/Yibux/insurance-app/issues/45)                                                                                                                                                                              | —                                     |
| NFR-MNT-02  | [#34](https://github.com/Yibux/insurance-app/issues/34), [#36](https://github.com/Yibux/insurance-app/issues/36)                                                                                                                                                                            | —                                     |
| NFR-MNT-03  | [#5](https://github.com/Yibux/insurance-app/issues/5), [#10](https://github.com/Yibux/insurance-app/issues/10), [#27](https://github.com/Yibux/insurance-app/issues/27), [#64](https://github.com/Yibux/insurance-app/issues/64), [#72](https://github.com/Yibux/insurance-app/issues/72)   | —                                     |
| NFR-MNT-04  | [#5](https://github.com/Yibux/insurance-app/issues/5)                                                                                                                                                                                                                                       | Jammeh 2020                           |
| NFR-MNT-05  | [#4](https://github.com/Yibux/insurance-app/issues/4), [#64](https://github.com/Yibux/insurance-app/issues/64)                                                                                                                                                                              | —                                     |
| NFR-OBS-01  | [#62](https://github.com/Yibux/insurance-app/issues/62)                                                                                                                                                                                                                                     | —                                     |
| NFR-OBS-02  | [#22](https://github.com/Yibux/insurance-app/issues/22), [#75](https://github.com/Yibux/insurance-app/issues/75)                                                                                                                                                                            | —                                     |
| NFR-OBS-03  | [#39](https://github.com/Yibux/insurance-app/issues/39)                                                                                                                                                                                                                                     | —                                     |
| NFR-PERF-01 | [#26](https://github.com/Yibux/insurance-app/issues/26), [#76](https://github.com/Yibux/insurance-app/issues/76)                                                                                                                                                                            | Bavadiya 2022; Cheenepalli i in. 2025 |
| NFR-PERF-02 | [#35](https://github.com/Yibux/insurance-app/issues/35), [#36](https://github.com/Yibux/insurance-app/issues/36)                                                                                                                                                                            | —                                     |
| NFR-PERF-03 | [#61](https://github.com/Yibux/insurance-app/issues/61)                                                                                                                                                                                                                                     | —                                     |
| NFR-PERF-04 | [#66](https://github.com/Yibux/insurance-app/issues/66), [#71](https://github.com/Yibux/insurance-app/issues/71)                                                                                                                                                                            | —                                     |
| NFR-PERF-05 | [#16](https://github.com/Yibux/insurance-app/issues/16)                                                                                                                                                                                                                                     | —                                     |
| NFR-QA-01   | [#17](https://github.com/Yibux/insurance-app/issues/17), [#42](https://github.com/Yibux/insurance-app/issues/42)                                                                                                                                                                            | —                                     |
| NFR-QA-02   | [#55](https://github.com/Yibux/insurance-app/issues/55)                                                                                                                                                                                                                                     | —                                     |
| NFR-QA-03   | [#58](https://github.com/Yibux/insurance-app/issues/58)                                                                                                                                                                                                                                     | —                                     |
| NFR-QA-04   | [#14](https://github.com/Yibux/insurance-app/issues/14), [#57](https://github.com/Yibux/insurance-app/issues/57)                                                                                                                                                                            | —                                     |
| NFR-QA-05   | [#41](https://github.com/Yibux/insurance-app/issues/41)                                                                                                                                                                                                                                     | —                                     |
| NFR-SEC-01  | [#32](https://github.com/Yibux/insurance-app/issues/32), [#40](https://github.com/Yibux/insurance-app/issues/40), [#42](https://github.com/Yibux/insurance-app/issues/42)                                                                                                                   | Al Kalach 2025                        |
| NFR-SEC-02  | [#33](https://github.com/Yibux/insurance-app/issues/33), [#46](https://github.com/Yibux/insurance-app/issues/46)                                                                                                                                                                            | Al Kalach 2025                        |
| NFR-SEC-03  | [#18](https://github.com/Yibux/insurance-app/issues/18), [#34](https://github.com/Yibux/insurance-app/issues/34), [#35](https://github.com/Yibux/insurance-app/issues/35), [#42](https://github.com/Yibux/insurance-app/issues/42), [#78](https://github.com/Yibux/insurance-app/issues/78) | Al Kalach 2025; IEEE/ACM 2022         |
| NFR-SEC-04  | [#18](https://github.com/Yibux/insurance-app/issues/18), [#34](https://github.com/Yibux/insurance-app/issues/34)                                                                                                                                                                            | —                                     |
| NFR-SEC-05  | [#7](https://github.com/Yibux/insurance-app/issues/7), [#15](https://github.com/Yibux/insurance-app/issues/15), [#19](https://github.com/Yibux/insurance-app/issues/19)                                                                                                                     | IEEE 2025 SLR; Lakade 2025            |
| NFR-SEC-06  | [#7](https://github.com/Yibux/insurance-app/issues/7), [#15](https://github.com/Yibux/insurance-app/issues/15), [#24](https://github.com/Yibux/insurance-app/issues/24), [#59](https://github.com/Yibux/insurance-app/issues/59)                                                            | Machapatri 2020; Lakade 2025          |
| NFR-SEC-07  | [#40](https://github.com/Yibux/insurance-app/issues/40), [#47](https://github.com/Yibux/insurance-app/issues/47), [#53](https://github.com/Yibux/insurance-app/issues/53)                                                                                                                   | Al Kalach 2025                        |
| NFR-SEC-08  | [#67](https://github.com/Yibux/insurance-app/issues/67), [#68](https://github.com/Yibux/insurance-app/issues/68), [#69](https://github.com/Yibux/insurance-app/issues/69)                                                                                                                   | Machapatri 2020                       |
| NFR-SEC-09  | [#53](https://github.com/Yibux/insurance-app/issues/53)                                                                                                                                                                                                                                     | —                                     |
| NFR-SEC-10  | [#49](https://github.com/Yibux/insurance-app/issues/49)                                                                                                                                                                                                                                     | —                                     |
| NFR-SEC-11  | [#6](https://github.com/Yibux/insurance-app/issues/6), [#25](https://github.com/Yibux/insurance-app/issues/25)                                                                                                                                                                              | —                                     |
| NFR-UX-01   | [#54](https://github.com/Yibux/insurance-app/issues/54)                                                                                                                                                                                                                                     | —                                     |
| NFR-UX-02   | [#48](https://github.com/Yibux/insurance-app/issues/48)                                                                                                                                                                                                                                     | —                                     |
| NFR-UX-03   | [#49](https://github.com/Yibux/insurance-app/issues/49)                                                                                                                                                                                                                                     | —                                     |

<!-- TRACEABILITY:END -->
