# Etap 2 — Model danych i bezpieczeństwo

Wpisy dodawane po zamknięciu każdego zadania etapu (szablon: [KONWENCJE.md](../KONWENCJE.md#szablon-wpisu-implementacyjnego)).

<!-- Nowe wpisy poniżej, od najstarszego. -->

### #29 Design data model (ERD) and document it

- **Data:** 2026-11-02 · **PR:** #113 · **Wymagania:** FR-POL-01, FR-CLM-01, NFR-CMP-03
- **Co zrobiono:** Zaprojektowano model danych czterech obiektów custom (`Policy__c`, `Coverage__c`, `Claim__c`, `Claim_Document__c`) wraz z relacjami do standardowych `Contact`, `User`, `Case`, `ContentDocumentLink` oraz obiektem zewnętrznym płatności. Dla każdego pola określono typ, klasyfikację danych (PII / wrażliwe / biznesowe / techniczne) i rekomendowany dostęp per rola.
- **Jak:** nowy dokument [`docs/architektura/model-danych.md`](../architektura/model-danych.md) z diagramem Mermaid `erDiagram`, tabelą relacji z uzasadnieniem typu (lookup vs master-detail), listami pól i listą danych celowo nieprzechowywanych; odnośnik w `docs/architektura/README.md`. Zmiana wyłącznie dokumentacyjna — bez metadanych w `force-app/`, więc bez zużycia scratch orgów.
- **Decyzje i alternatywy:** `Coverage__c` i `Claim_Document__c` jako master-detail (dziedziczą widoczność przy OWD Private); `Claim__c` jako lookup do polisy, bo ma własny model dostępu (likwidator, agent, klient). Spójność „zakres należy do polisy i obowiązuje w dniu zdarzenia” (FR-CLM-01) wymuszana w Apex (#35), nie w schemacie. Ubezpieczony jako `Contact` (ADR-0002). Minimalizacja danych: brak PESEL, daty urodzenia, numerów kont; dane płatnicze w systemie źródłowym. ~~Nowy ADR nie był potrzebny~~ (zastąpione: decyzje dostępowe z przeglądu czekają na potwierdzenie, ewentualny ADR przy #32).
- **Problemy:** ~~brak~~ (zastąpione podsekcją „zmiany po przeglądzie bezpieczeństwa” poniżej); nazwy API są propozycją i mogą się zmienić w #30/#31 (wtedy aktualizacja dokumentu).
- **Dowody:** [`model-danych.md`](../architektura/model-danych.md) (diagram renderowany przez GitHub); CI na ostatnim head (`aad24c6`): [PR validation](https://github.com/Yibux/insurance-app/actions/runs/41480166860), [CodeQL](https://github.com/Yibux/insurance-app/actions/runs/41480166836) (oba zielone).
- **Do pracy:** rozdział implementacyjny „Model danych i zabezpieczenia” (ERD, klasyfikacja danych, minimalizacja RODO); uzasadnienie master-detail vs lookup przy OWD Private (Al Kalach 2025).

#### #29 — zmiany po przeglądzie bezpieczeństwa

- **B1 (mechanizm dostępu agenta):** deklaratywne reguły współdzielenia nie udostępniają rekordu użytkownikowi wskazanemu w lookupie, więc `Agent__c` usunięto; agent jest właścicielem polisy (`OwnerId`). Dostęp agenta do szkód przez Apex managed sharing (`Claim__Share`, własny `RowCause`) utrzymywany serwisem Apex (#35). Likwidator jest właścicielem szkody, `Adjuster__c` usunięto.
- **B2 (IDOR przy zgłaszaniu szkody):** `Claimant__c` ustawiany po stronie serwera z `User.ContactId`; serwis weryfikuje własność polisy zapytaniem `WITH USER_MODE`; test negatywny `runAs` z cudzą polisą w #35.
- **B3 (zapis klienta):** klient portalu ma tylko odczyt na `Policy__c`, `Coverage__c`, `Claim__c` i `Claim_Document__c`; szkody i dokumenty tworzy wyłącznie Apex po kontroli własności. Wyłączono „Allow reparenting” na obu master-detail.
- **Klasyfikacja i FLS:** doprecyzowano klasyfikację (`Policy_Number__c` jako PII pośrednie, klasa „art. 9” dla opisu szkody i plików), `Premium__c` ukryta przed likwidatorem, pola Auto Number tylko do odczytu, dodano rolę użytkownika integracyjnego do macierzy FLS.
- **Do potwierdzenia przez użytkownika (bez ADR):** agent jako właściciel polisy, Apex managed sharing dla `Claim__c` oraz klient portalu tylko do odczytu. Jeśli decyzje zostaną utrzymane, zalecany ADR przy zadaniu #32.

- **Decyzje potwierdzone (2026-11-02):** właściciel pracy utrzymał decyzje z punktów B1–B3; zapisano je w [ADR 0009](../adr/0009-model-wspoldzielenia-rekordow.md) (Refs #32; implementacja w `force-app/` pozostaje w M2).

#### Do rozstrzygnięcia w #30 / #31 / #32 / #33 / #35

- **R1 (#31, #33):** wszystkie dokumenty szkody są widoczne dla klienta, także wewnętrzne (opinia rzeczoznawcy, notatka o podejrzeniu nadużycia). Potrzebne rozróżnienie (np. `Visible_To_Customer__c` lub wartość `Document_Type__c`) oraz `ContentDocumentLink.Visibility = InternalUsers` dla plików wewnętrznych. Usunięcie `Claim__c` kasuje `Claim_Document__c`, ale nie `ContentDocument` — osierocone pliki z PII i danymi zdrowotnymi; wymaga polityki retencji (RODO) i ograniczenia, kto może usuwać `Claim__c`.
- **R4 (#32, #35):** NFR-SEC-07 mówi o rekordach „własnego konta”, a `Insured__c`/`Claimant__c` wskazują `Contact`. Rozstrzygnąć zakres kontakt vs konto oraz kto widzi szkodę, gdy `Claimant__c` ≠ `Insured__c`.
- **R5 (etap M5, #33):** obiekt zewnętrzny płatności nie obsługuje OWD ani sharingu rekordowego; filtrowanie per użytkownik musi wykonać serwis OData (tożsamość per użytkownik w Named/External Credential) albo dostęp tylko przez Apex. Indirect lookup wymaga `Policy_Number__c` jako External ID.
- **R6 (#30, #31):** wymagane lookupy do `Contact` blokują usunięcie kontaktu (art. 17 RODO); usunięcie lub anonimizacja jako proces poza schematem.
- **N1 (#35):** ścieżka tworzenia szkody z portalu opisana w `model-danych.md` (walidacja `WITH USER_MODE`, potem wąski DML w trybie systemowym ustawiający właściciela-kolejkę i `Claim__Share`, allowlista pól, status wymuszony) jest udokumentowanym wyjątkiem od NFR-SEC-03; PMD (`ApexCRUDViolation`, `ApexSharingViolations`) ją zgłosi, supresja musi być jawna i opisana (materiał do analizy FN/FP).
- **R7 (#32):** Sharing Set „po koncie” nie ma pola do mapowania (obiekty mają lookupy tylko do `Contact`) — przyjęto „po kontakcie” (`User.Contact` = `Insured__c`/`Claimant__c`) albo dodać `Account__c`; potwierdzić.
- **R8 (#35):** szkody ładowane przez integrację (M4) nie dostaną `Claim__Share` — logika w trigger handlerze `Claim__c`, obsługa zmiany właściciela `Policy__c` i klasa recalculation.
- **R9 (#31, #33):** agent przez master-detail dostaje Read na `Claim_Document__c` i pliki (art. 9) — uzasadnić need-to-know albo ograniczyć (powiązane z R1).
- **R10 (#30):** agent może edytować `Policy__c.Insured__c`, co zmienia widoczność szkód u innego klienta — walidacja blokująca zmianę po statusie Draft albo E tylko dla użytkownika integracyjnego.
- **R11 (#35):** likwidator może edytować `Claim__c.Coverage__c` — spójność polisa/zakres także przy update (trigger).
- **R12 (#33):** użytkownik integracyjny zbyt szeroki: API Only, osobny permission set, JWT (NFR-SEC-06), jawny dostęp do rekordów przy OWD Private, zawężenie E na polach wypłat po migracji.
- **R13 (#33):** odebrać Delete na `Claim__c` rolom A/L/K.
