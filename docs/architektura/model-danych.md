# Model danych (ERD)

- **Status:** projekt (M2, #29) — implementacja metadanych: #30 (`Policy__c`, `Coverage__c`) i #31 (`Claim__c`, `Claim_Document__c`)
- **Wymagania:** FR-POL-01, FR-CLM-01, NFR-CMP-03 (powiązane: FR-POL-02, FR-CLM-03, FR-CLM-06, NFR-SEC-01, NFR-CMP-01)
- **Decyzje:** [ADR-0002](../adr/0002-custom-objects-vs-fsc.md) (obiekty custom zamiast FSC)

Dokument opisuje docelowy model danych. Jest specyfikacją dla zadań #30 i #31; po ich wdrożeniu metadane w `force-app/` są źródłem prawdy, a ewentualne różnice należy tu odnotować.

## 1. Diagram ERD

```mermaid
erDiagram
    ACCOUNT ||--o{ CONTACT : "grupuje"
    CONTACT ||--o{ POLICY : "ubezpieczony (Insured__c)"
    USER ||--o{ POLICY : "agent = właściciel (OwnerId)"
    POLICY ||--|{ COVERAGE : "zakresy ochrony (master-detail)"
    POLICY ||--o{ CLAIM : "szkody (Policy__c)"
    COVERAGE ||--o{ CLAIM : "zakres szkody (Coverage__c)"
    CONTACT ||--o{ CLAIM : "zgłaszający (Claimant__c)"
    USER ||--o{ CLAIM : "likwidator = właściciel (OwnerId)"
    CLAIM ||--o{ CLAIM_DOCUMENT : "dokumenty (master-detail)"
    CLAIM_DOCUMENT ||--o{ CONTENT_DOCUMENT_LINK : "pliki (Files)"
    CONTACT ||--o{ CASE : "komunikacja z agentem (M3)"
    POLICY ||--o{ PAYMENT_X : "historia płatności (External Object, M5)"

    ACCOUNT {
        Id Id PK
        string Name
    }
    CONTACT {
        Id Id PK
        Id AccountId FK
        string FirstName
        string LastName
        string Email
        string Phone
    }
    USER {
        Id Id PK
        string Name
    }
    POLICY {
        Id Id PK
        string Name "autonumer"
        string Policy_Number__c UK "numer polisy"
        string Product_Type__c "picklist"
        Id OwnerId FK "User: agent"
        Id Insured__c FK "Contact"
        date Start_Date__c
        date End_Date__c
        currency Premium__c
        string Status__c "Draft, Active, Expired, Cancelled"
        string External_Id__c UK "migracja"
    }
    COVERAGE {
        Id Id PK
        string Name "autonumer"
        Id Policy__c FK "master-detail"
        string Coverage_Type__c "picklist"
        currency Sum_Insured__c
        currency Deductible__c
        string External_Id__c UK "migracja"
    }
    CLAIM {
        Id Id PK
        string Name "autonumer"
        Id Policy__c FK
        Id Coverage__c FK
        Id OwnerId FK "User/kolejka: likwidator"
        Id Claimant__c FK "Contact"
        date Incident_Date__c
        string Description__c
        string Status__c "Submitted ... Closed"
        currency Claimed_Amount__c
        currency Approved_Amount__c
        currency Payout_Amount__c
        string External_Id__c UK "migracja"
    }
    CLAIM_DOCUMENT {
        Id Id PK
        string Name
        Id Claim__c FK "master-detail"
        string Document_Type__c "picklist"
        string External_Id__c UK "migracja"
    }
    CONTENT_DOCUMENT_LINK {
        Id Id PK
        Id LinkedEntityId FK "Claim_Document__c"
        Id ContentDocumentId FK
    }
    CASE {
        Id Id PK
        Id ContactId FK
        string Subject
    }
    PAYMENT_X {
        string ExternalId PK
        string PolicyNumber "klucz logiczny do Policy__c"
        date PaymentDate
        decimal Amount
    }
```

Legenda: `PK` — klucz główny, `FK` — klucz obcy (lookup lub master-detail), `UK` — pole unikalne (External ID). `Account`, `Contact`, `User`, `Case`, `ContentDocumentLink` są obiektami standardowymi; `Policy__c`, `Coverage__c`, `Claim__c`, `Claim_Document__c` — custom. `PAYMENT_X` to obiekt zewnętrzny (OData, M5), którego **dane nie są kopiowane do CRM** (NFR-CMP-01). Statusy: polisa Draft → Active → Expired/Cancelled (FR-POL-03); szkoda Submitted → Under Review → Approved/Rejected → Paid → Closed (FR-CLM-02).

## 2. Relacje i uzasadnienie

| Relacja                          | Typ                   | Uzasadnienie                                                                                                                                                                               |
| -------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Policy__c` → `Contact`          | Lookup (wymagany)     | Ubezpieczony to `Contact` powiązany z `Account` (ADR-0002); użytkownik portalu jest powiązany z kontaktem, co umożliwia Sharing Sets (NFR-SEC-07).                                         |
| `Coverage__c` → `Policy__c`      | Master-detail         | Zakres nie istnieje bez polisy; przy OWD Private rekord potomny dziedziczy widoczność po polisie, więc nie trzeba utrzymywać osobnego współdzielenia; „Allow reparenting” wyłączone.       |
| `Claim__c` → `Policy__c`         | Lookup (wymagany)     | Szkoda ma własny cykl życia i własny model dostępu (likwidator, agent, klient), dlatego nie dziedziczy sharingu po polisie; usuwanie polisy ze szkodami blokowane (`restrict delete`).     |
| `Claim__c` → `Coverage__c`       | Lookup (wymagany)     | FR-CLM-01: szkoda wskazuje zakres obowiązujący w dniu zdarzenia. Spójność (zakres należy do tej samej polisy, polisa aktywna w `Incident_Date__c`) wymusza logika Apex (#35), nie schemat. |
| `Claim_Document__c` → `Claim__c` | Master-detail         | Dokument dziedziczy widoczność po szkodzie; usunięcie szkody usuwa metadane dokumentów; „Allow reparenting” wyłączone.                                                                     |
| Pliki → `Claim_Document__c`      | `ContentDocumentLink` | Pliki (Salesforce Files) podpinane do rekordu `Claim_Document__c`; limity rozmiaru i typów MIME: NFR-SEC-10 (#49).                                                                         |
| `Case` → `Contact`               | Standardowa           | Komunikacja klient–agent (FR-COM, M3); `Case` nie reprezentuje szkody (ADR-0002, opcja 3).                                                                                                 |
| Płatności (External Object)      | Brak kopii            | Powiązanie logiczne po numerze polisy (M5); dane płatnicze zostają w systemie źródłowym.                                                                                                   |

### Model dostępu a schemat (decyzje do potwierdzenia)

Uzasadnienie wyborów poniżej: deklaratywne reguły współdzielenia (sharing rules) opierają się na właścicielu rekordu lub kryteriach pól i udostępniają rekordy rolom, grupom i kolejkom — **nie** użytkownikowi wskazanemu w polu lookup. Pole `User` w lookupie niczego więc nie współdzieli przy OWD Private.

- **Portfel agenta — Policy (FR-POL-04, NFR-SEC-01).** Wybrano wariant (a): agent jest **właścicielem polisy** (`OwnerId`); osobne pole `Agent__c` nie istnieje. Dostęp wynika z własności, a nadzór (kierownik) z hierarchii ról. Wariant (b) (Apex managed sharing `Policy__Share`) odrzucono dla polis jako zbędnie złożony, skoro własność w pełni opisuje portfel.
- **Dostęp agenta do szkód.** Szkoda nie dziedziczy sharingu po polisie (jest lookupem), a reguła nie sięga do `Policy__r.OwnerId`. Wybrano **Apex managed sharing** (`Claim__Share`, własny `RowCause` np. `Agent_Portfolio__c`): serwis Apex (#35) przy tworzeniu szkody udostępnia ją właścicielowi polisy (Read) i utrzymuje wpis przy zmianie właściciela polisy. Alternatywa — zdenormalizowane pole agenta na szkodzie — też wymagałoby Apex sharingu, więc nie daje korzyści.
- **Likwidator** jest właścicielem szkody (`OwnerId`: użytkownik lub kolejka, FR-CLM-04); pole `Adjuster__c` zbędne.
- **Klient portalu: tylko odczyt.** Wybrano wariant (a): klient ma **Read-only** na `Claim__c`, `Claim_Document__c`, `Policy__c`, `Coverage__c` (Sharing Set po kontakcie: `User.Contact` = `Insured__c`/`Claimant__c`; do potwierdzenia w #32). Szkodę i dokumenty tworzy wyłącznie serwis Apex (kontroler portalu → serwis) po weryfikacji własności; wariant (b) (Read/Write + reguły walidacji blokujące zmiany po statusie Submitted) odrzucono, bo FLS nie odróżnia tworzenia od edycji, a tworzenie dokumentu (master-detail) wymagałoby zapisu na szkodzie, co otwierałoby edycję `Incident_Date__c`, `Claimed_Amount__c` i `Description__c` po zgłoszeniu.
- **Reparenting.** Oba master-detail (`Coverage__c` → `Policy__c`, `Claim_Document__c` → `Claim__c`) mają wyłączone „Allow reparenting”, by nie dało się przenieść potomka pod cudzego rodzica i obejść sharingu.

Decyzje te wymagają potwierdzenia przez właściciela pracy; jeśli zostaną utrzymane, warto je spisać w ADR przy zadaniu #32.

Uwaga o `Claim__Share`: wiersze udostępnienia agentowi są tworzone przez serwis Apex (krok w trybie systemowym, patrz niżej) i, dla szkód ładowanych przez integrację, przez trigger handler `Claim__c`; bez tego szkoda nie jest widoczna dla agenta.

### Założenia dla implementacji (#30, #31)

- OWD **Private** dla `Policy__c` i `Claim__c` (NFR-SEC-01), dostęp agenta przez własność (polisa) i Apex managed sharing (szkoda); `Coverage__c` i `Claim_Document__c` dziedziczą dostęp po rodzicu (master-detail). OWD dla `Contact`/`Account` ustala zadanie dot. sharingu (#32).
- Każdy z czterech obiektów ma pole `External_Id__c` (Text, unique, External ID) pod migrację z backendu Python (M4) i upsert po kluczu zewnętrznym.
- Statusy jako picklisty z regułami walidacji ścieżek przejść (FR-POL-03, FR-CLM-02); Field History Tracking dla `Claim__c.Status__c` oraz kwot (FR-CLM-06, #31).
- Tworzenie szkody (FR-CLM-01, NFR-SEC-07, NFR-SEC-03): `Claimant__c` ustawiany **po stronie serwera** z `User.ContactId` zalogowanego użytkownika, nigdy z danych wysłanych przez klienta. Serwis Apex (`with sharing`) weryfikuje w trybie użytkownika, że wskazana polisa należy do zgłaszającego (`Policy__c.Insured__c` = jego `ContactId` / to samo konto) zapytaniem `WITH USER_MODE` oraz że zakres należy do tej polisy; brak weryfikacji oznaczałby IDOR (podanie Id cudzej polisy). Test negatywny `System.runAs` użytkownika portalu z cudzą polisą — w #35.
- Ścieżka zapisu szkody z portalu (wyjątek od NFR-SEC-03): klient jest read-only, więc `insert as user` zawsze by się nie powiódł, a zapis `Claim__Share` wymaga kontekstu uprawnionego do udostępniania. Reguły przydziału (assignment rules) nie działają na obiektach custom, więc bez jawnego Apex właścicielem szkody byłby klient i likwidator jej nie widziałby (OWD Private, FR-CLM-04). Dlatego: (1) walidacja własności polisy i zakresu w trybie użytkownika (`WITH USER_MODE`); (2) wąski krok DML w trybie systemowym (`Database.insert(..., AccessLevel.SYSTEM_MODE)`) w małej dedykowanej klasie, który ustawia `OwnerId` = kolejka likwidatorów i zapisuje `Claim__Share` (`RowCause` = `Agent_Portfolio__c`). Serwis zapisuje wyłącznie allowlistę pól z żądania (`Incident_Date__c`, `Description__c`, `Claimed_Amount__c`, `Coverage__c`, `Policy__c`), wymusza `Status__c` = Submitted i nigdy nie przyjmuje `Approved_Amount__c` ani `Payout_Amount__c`. Jest to udokumentowany, uzasadniony wyjątek od NFR-SEC-03; PMD (`ApexCRUDViolation`, `ApexSharingViolations`) w #35 to zgłosi — supresja ma być jawna i opisana w kodzie (przykład do analizy FN/FP w pracy).
- Nazwy API są propozycją; ostateczne ustalają #30/#31 — zmiany należy odzwierciedlić w tym dokumencie.

## 3. Lista pól i klasyfikacja danych

Klasyfikacja:

- **PII** — dane osobowe w rozumieniu RODO (identyfikują osobę bezpośrednio lub pośrednio albo umożliwiają kontakt);
- **Wrażliwe** — dane o podwyższonym ryzyku: kwoty finansowe, swobodne opisy mogące zawierać dane zdrowotne lub osobowe, dokumenty;
- **Biznesowe** — dane operacyjne bez bezpośredniej identyfikacji osoby;
- **Szczególna kategoria (art. 9 RODO)** — dane o zdrowiu i inne dane szczególnie chronione, które mogą pojawić się w swobodnym tekście lub plikach;
- **Techniczne** — identyfikatory i pola systemowe.

Kolumna „FLS” to rekomendacja dostępu dla zestawów uprawnień: A — Agent, L — Likwidator, K — Klient portalu, I — użytkownik integracyjny (backend Python, M4: ładowanie danych przez upsert po `External_Id__c`); R — odczyt, E — edycja, `-` — brak. Ostateczna macierz powstanie w #33 (NFR-SEC-02).

### 3.1 `Policy__c`

| Pole API           | Typ                     | Klasyfikacja                 | Uzasadnienie / minimalizacja (NFR-CMP-03)                                      | FLS (A/L/K/I) |
| ------------------ | ----------------------- | ---------------------------- | ------------------------------------------------------------------------------ | ------------- |
| `Name`             | Auto Number             | Techniczne                   | Identyfikator rekordu                                                          | R/R/R/R       |
| `Policy_Number__c` | Text(30), unique        | PII (identyfikator pośredni) | Numer polisy; pośrednio identyfikuje osobę — nie logować w komunikatach błędów | E/R/R/E       |
| `Product_Type__c`  | Picklist                | Biznesowe                    | Wymagane do procesu                                                            | E/R/R/E       |
| `Insured__c`       | Lookup(Contact)         | PII (relacja)                | Wiąże polisę z osobą; dane osoby zostają w `Contact`, nie są powielane         | E/R/R/E       |
| `Start_Date__c`    | Date                    | Biznesowe                    | Okres ochrony; reguły walidacji dat                                            | E/R/R/E       |
| `End_Date__c`      | Date                    | Biznesowe                    | Podstawa wygaszania polis (FR-POL-05)                                          | E/R/R/E       |
| `Premium__c`       | Currency                | Wrażliwe                     | Składka (dane finansowe); ukryta przed rolami bez potrzeby biznesowej          | E/-/R/E       |
| `Status__c`        | Picklist                | Biznesowe                    | Draft / Active / Expired / Cancelled                                           | E/R/R/E       |
| `External_Id__c`   | Text(50), unique, ExtId | Techniczne                   | Klucz migracji; w dev/CI wyłącznie identyfikatory syntetyczne (NFR-CMP-02)     | R/-/-/E       |

### 3.2 `Coverage__c`

| Pole API           | Typ                     | Klasyfikacja | Uzasadnienie / minimalizacja                | FLS (A/L/K/I) |
| ------------------ | ----------------------- | ------------ | ------------------------------------------- | ------------- |
| `Name`             | Auto Number             | Techniczne   | Identyfikator                               | R/R/R/R       |
| `Policy__c`        | Master-Detail(Policy)   | Biznesowe    | Rodzic; dziedziczenie widoczności           | E/R/R/E       |
| `Coverage_Type__c` | Picklist                | Biznesowe    | Rodzaj ochrony                              | E/R/R/E       |
| `Sum_Insured__c`   | Currency                | Wrażliwe     | Limit odpowiedzialności; podstawa FR-CLM-05 | E/R/R/E       |
| `Deductible__c`    | Currency                | Wrażliwe     | Udział własny; podstawa FR-CLM-05           | E/R/R/E       |
| `External_Id__c`   | Text(50), unique, ExtId | Techniczne   | Klucz migracji                              | R/-/-/E       |

### 3.3 `Claim__c`

| Pole API             | Typ                     | Klasyfikacja                  | Uzasadnienie / minimalizacja                                                                               | FLS (A/L/K/I) |
| -------------------- | ----------------------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------- |
| `Name`               | Auto Number             | Techniczne                    | Identyfikator                                                                                              | R/R/R/R       |
| `Policy__c`          | Lookup(Policy)          | Biznesowe                     | Polisa, której dotyczy szkoda                                                                              | R/R/R/E       |
| `Coverage__c`        | Lookup(Coverage)        | Biznesowe                     | Zakres obowiązujący w dniu zdarzenia (FR-CLM-01)                                                           | R/E/R/E       |
| `Claimant__c`        | Lookup(Contact)         | PII (relacja)                 | Zgłaszający; bez kopiowania danych kontaktowych do szkody                                                  | R/R/R/E       |
| `Incident_Date__c`   | Date                    | Biznesowe                     | Data zdarzenia                                                                                             | R/R/R/E       |
| `Description__c`     | Long Text(5000)         | Szczególna kategoria (art. 9) | Opis zdarzenia od klienta; może zawierać dane osobowe/zdrowotne — w formularzu ostrzeżenie o minimalizacji | R/R/R/E       |
| `Status__c`          | Picklist                | Biznesowe                     | Cykl życia (FR-CLM-02); Field History Tracking (FR-CLM-06)                                                 | R/E/R/E       |
| `Claimed_Amount__c`  | Currency                | Wrażliwe                      | Kwota zgłoszona; Field History                                                                             | R/R/R/E       |
| `Approved_Amount__c` | Currency                | Wrażliwe                      | Kwota zatwierdzona przez likwidatora; Field History                                                        | -/E/R/E       |
| `Payout_Amount__c`   | Currency                | Wrażliwe                      | Kwota wypłaty, limit z FR-CLM-05; Field History. Transakcje płatnicze pozostają poza CRM                   | -/E/R/E       |
| `External_Id__c`     | Text(50), unique, ExtId | Techniczne                    | Klucz migracji                                                                                             | R/-/-/E       |

### 3.4 `Claim_Document__c`

| Pole API                   | Typ                     | Klasyfikacja                  | Uzasadnienie / minimalizacja                                                                                               | FLS (A/L/K/I) |
| -------------------------- | ----------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `Name`                     | Text(80)                | Techniczne                    | Etykieta dokumentu; nie wpisywać danych osobowych w nazwie                                                                 | R/R/R/E       |
| `Claim__c`                 | Master-Detail(Claim)    | Biznesowe                     | Rodzic; dziedziczenie widoczności                                                                                          | R/R/R/E       |
| `Document_Type__c`         | Picklist                | Biznesowe                     | Rodzaj (zdjęcie, protokół, faktura)                                                                                        | R/E/R/E       |
| `External_Id__c`           | Text(50), unique, ExtId | Techniczne                    | Klucz migracji                                                                                                             | R/-/-/E       |
| (pliki — `ContentVersion`) | Salesforce Files        | Szczególna kategoria (art. 9) | Treść może zawierać PII i dane zdrowotne; limit rozmiaru i typów MIME (NFR-SEC-10), widoczność przez `ContentDocumentLink` | R/R/R/E       |

### 3.5 Standardowe obiekty użyte w modelu

Dane identyfikacyjne i kontaktowe osób znajdują się tylko w `Contact` (oraz `User` dla pracowników); obiekty custom odwołują się do nich relacjami, bez duplikowania. Pośrednie identyfikatory (np. numer polisy) i swobodny tekst w obiektach custom są klasyfikowane osobno w sekcjach 3.1–3.4.

| Obiekt.pole                      | Klasyfikacja     | Uwagi                                                                                        |
| -------------------------------- | ---------------- | -------------------------------------------------------------------------------------------- |
| `Contact.FirstName/LastName`     | PII              | Wymagane do identyfikacji ubezpieczonego                                                     |
| `Contact.Email`, `Contact.Phone` | PII              | Wymagane do kontaktu i logowania do portalu; w danych testowych wyłącznie adresy syntetyczne |
| `Contact.MailingAddress`         | PII              | Opcjonalne; pominąć, jeśli proces tego nie wymaga (minimalizacja)                            |
| `Account.Name`                   | PII / biznesowe  | W modelu B2C może zawierać nazwisko                                                          |
| `User` (agent, likwidator)       | PII (pracownicy) | Widoczność użytkowników ograniczona do niezbędnej                                            |
| `Case.Subject`, treść            | Wrażliwe         | Swobodny tekst klienta (M3); polityka jak dla `Claim__c.Description__c`                      |

Pola, których celowo **nie** przechowujemy (NFR-CMP-03): PESEL i numer dokumentu tożsamości, data urodzenia, numery kont bankowych i kart, dane zdrowotne w polach ustrukturyzowanych. Dane płatnicze zostają w systemie zewnętrznym (NFR-CMP-01).

## 4. Dane syntetyczne

Wszystkie rekordy w środowiskach deweloperskich i CI są syntetyczne (NFR-CMP-02): losowe imiona, adresy e-mail w domenie zarezerwowanej `example.com`, losowe numery polis. Plany danych (`sf data import tree`) — zadanie #41.

## 5. Powiązane

- [ADR-0002](../adr/0002-custom-objects-vs-fsc.md), [WYMAGANIA.md](../WYMAGANIA.md), [HARMONOGRAM.md](../HARMONOGRAM.md)
- Zadania wdrożeniowe: #30, #31; sharing i uprawnienia: #32, #33.
