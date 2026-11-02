# Etap 2 — Model danych i bezpieczeństwo

Wpisy dodawane po zamknięciu każdego zadania etapu (szablon: [KONWENCJE.md](../KONWENCJE.md#szablon-wpisu-implementacyjnego)).

<!-- Nowe wpisy poniżej, od najstarszego. -->

### #29 Design data model (ERD) and document it

- **Data:** 2026-11-02 · **PR:** #113 · **Wymagania:** FR-POL-01, FR-CLM-01, NFR-CMP-03
- **Co zrobiono:** Zaprojektowano model danych czterech obiektów custom (`Policy__c`, `Coverage__c`, `Claim__c`, `Claim_Document__c`) wraz z relacjami do standardowych `Contact`, `User`, `Case`, `ContentDocumentLink` oraz obiektem zewnętrznym płatności. Dla każdego pola określono typ, klasyfikację danych (PII / wrażliwe / biznesowe / techniczne) i rekomendowany dostęp per rola.
- **Jak:** nowy dokument [`docs/architektura/model-danych.md`](../architektura/model-danych.md) z diagramem Mermaid `erDiagram`, tabelą relacji z uzasadnieniem typu (lookup vs master-detail), listami pól i listą danych celowo nieprzechowywanych; odnośnik w `docs/architektura/README.md`. Zmiana wyłącznie dokumentacyjna — bez metadanych w `force-app/`, więc bez zużycia scratch orgów.
- **Decyzje i alternatywy:** `Coverage__c` i `Claim_Document__c` jako master-detail (dziedziczą widoczność przy OWD Private); `Claim__c` jako lookup do polisy, bo ma własny model dostępu (likwidator, agent, klient). Spójność „zakres należy do polisy i obowiązuje w dniu zdarzenia” (FR-CLM-01) wymuszana w Apex (#35), nie w schemacie. Ubezpieczony jako `Contact` (ADR-0002). Minimalizacja danych: brak PESEL, daty urodzenia, numerów kont; dane płatnicze w systemie źródłowym. Nowy ADR nie był potrzebny — decyzje wynikają z ADR-0002.
- **Problemy:** brak; nazwy API są propozycją i mogą się zmienić w #30/#31 (wtedy aktualizacja dokumentu).
- **Dowody:** [`model-danych.md`](../architektura/model-danych.md) (diagram renderowany przez GitHub); CI: [PR validation](https://github.com/Yibux/insurance-app/actions/runs/41477862012), [CodeQL](https://github.com/Yibux/insurance-app/actions/runs/41477862105) (oba zielone).
- **Do pracy:** rozdział implementacyjny „Model danych i zabezpieczenia” (ERD, klasyfikacja danych, minimalizacja RODO); uzasadnienie master-detail vs lookup przy OWD Private (Al Kalach 2025).

#### #29 — zmiany po przeglądzie bezpieczeństwa

- **B1 (mechanizm dostępu agenta):** deklaratywne reguły współdzielenia nie udostępniają rekordu użytkownikowi wskazanemu w lookupie, więc `Agent__c` usunięto; agent jest właścicielem polisy (`OwnerId`). Dostęp agenta do szkód przez Apex managed sharing (`Claim__Share`, własny `RowCause`) utrzymywany serwisem Apex (#35). Likwidator jest właścicielem szkody, `Adjuster__c` usunięto.
- **B2 (IDOR przy zgłaszaniu szkody):** `Claimant__c` ustawiany po stronie serwera z `User.ContactId`; serwis weryfikuje własność polisy zapytaniem `WITH USER_MODE`; test negatywny `runAs` z cudzą polisą w #35.
- **B3 (zapis klienta):** klient portalu ma tylko odczyt na `Claim__c`/`Claim_Document__c`; szkody i dokumenty tworzy wyłącznie Apex po kontroli własności. Wyłączono „Allow reparenting” na obu master-detail.
- **M2/M3:** doprecyzowano klasyfikację (`Policy_Number__c` jako PII pośrednie, klasa „art. 9” dla opisu szkody i plików), `Premium__c` ukryta przed likwidatorem, pola Auto Number tylko do odczytu, dodano rolę użytkownika integracyjnego do macierzy FLS.
- **Do potwierdzenia przez użytkownika (bez ADR):** agent jako właściciel polisy, Apex managed sharing dla `Claim__c` oraz klient portalu tylko do odczytu. Jeśli decyzje zostaną utrzymane, zalecany ADR przy zadaniu #32.

#### Do rozstrzygnięcia w #30 / #31 / #33 / #35

- **M1 (#31, #33):** wszystkie dokumenty szkody są widoczne dla klienta, także wewnętrzne (opinia rzeczoznawcy, notatka o podejrzeniu nadużycia). Potrzebne rozróżnienie (np. `Visible_To_Customer__c` lub wartość `Document_Type__c`) oraz `ContentDocumentLink.Visibility = InternalUsers` dla plików wewnętrznych. Usunięcie `Claim__c` kasuje `Claim_Document__c`, ale nie `ContentDocument` — osierocone pliki z PII i danymi zdrowotnymi; wymaga polityki retencji (RODO) i ograniczenia, kto może usuwać `Claim__c`.
- **M4 (#32, #35):** NFR-SEC-07 mówi o rekordach „własnego konta”, a `Insured__c`/`Claimant__c` wskazują `Contact`. Rozstrzygnąć zakres kontakt vs konto oraz kto widzi szkodę, gdy `Claimant__c` ≠ `Insured__c`.
- **M5 (M5, #33):** obiekt zewnętrzny płatności nie obsługuje OWD ani sharingu rekordowego; filtrowanie per użytkownik musi wykonać serwis OData (tożsamość per użytkownik w Named/External Credential) albo dostęp tylko przez Apex. Indirect lookup wymaga `Policy_Number__c` jako External ID.
- **M6 (#30, #31):** wymagane lookupy do `Contact` blokują usunięcie kontaktu (art. 17 RODO); usunięcie lub anonimizacja jako proces poza schematem.
