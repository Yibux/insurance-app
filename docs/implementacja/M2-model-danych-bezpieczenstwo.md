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
