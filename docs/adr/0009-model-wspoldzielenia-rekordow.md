# 0009. Model współdzielenia rekordów: agent jako właściciel polisy, Apex managed sharing dla szkód, klient portalu tylko do odczytu

- **Status:** przyjęta
- **Data:** 2026-11-02
- **Issue:** #32 (tylko część ADR; implementacja w `force-app/` w etapie M2, issue pozostaje otwarte)
- **Wymagania:** NFR-SEC-01, NFR-SEC-03, NFR-SEC-07, FR-POL-04, FR-CLM-01, FR-CLM-04

## Kontekst

Obiekty biznesowe (`Policy__c`, `Claim__c`) mają OWD **Private** (NFR-SEC-01), a dostęp ma wynikać wyłącznie z własności, hierarchii ról i jawnego współdzielenia. Trzy role muszą widzieć różne rekordy: agent (portfel własnych polis i ich szkód, nadzór kierownika), likwidator (przydzielone szkody, FR-CLM-04) i klient portalu (tylko własne rekordy, NFR-SEC-07). Przegląd bezpieczeństwa modelu danych (#29) wykazał, że deklaratywne reguły współdzielenia opierają się na właścicielu lub kryteriach pól i nie udostępniają rekordu użytkownikowi wskazanemu w lookupie, więc pole `Agent__c` z lookupem na `User` nie dawałoby agentowi dostępu. Ponadto FLS nie odróżnia tworzenia od edycji, a reguły przydziału (assignment rules) nie działają na obiektach custom. Decyzje zatwierdził właściciel pracy 2026-11-02 w PR #113 (zadanie #29); szczegóły schematu w [`model-danych.md`](../architektura/model-danych.md), sekcja „Model dostępu a schemat”.

## Rozważane opcje

**Dostęp agenta do polis**

1. **Agent jako `OwnerId` polisy, nadzór przez hierarchię ról** — zero dodatkowego kodu, dostęp wynika z natywnej własności; hierarchia daje kierownikowi odczyt portfela. Wada: jedna polisa ma jednego agenta (zmiana agenta = zmiana właściciela).
2. **`Agent__c` (lookup do `User`) + sharing rules** — odrzucona: reguły nie sięgają do użytkownika z lookupu, więc nic by nie udostępniły.
3. **Apex managed sharing `Policy__Share`** — odrzucona dla polis jako zbędnie złożona, skoro własność w pełni opisuje portfel.

**Dostęp agenta do szkód**

1. **Apex managed sharing `Claim__Share` z własnym `RowCause` `Agent_Portfolio__c`** — szkoda jest lookupem do polisy, nie dziedziczy sharingu i żadna reguła nie sięga do `Policy__r.OwnerId`; Apex jest jedynym mechanizmem. Wada: kod do utrzymania (tworzenie, zmiana właściciela polisy, szkody z integracji).
2. **Zdenormalizowane pole agenta na szkodzie + sharing rules** — odrzucona: pole typu `User` nadal nie współdzieli, a kryteria na polu wymagałyby grup/ról per agent; też kończy się Apexem, bez zysku.

**Likwidator:** `OwnerId` szkody (użytkownik lub kolejka); pole `Adjuster__c` zbędne. Nowe szkody trafiają do kolejki likwidatorów.

**Zapis przez klienta portalu**

1. **Read-only + serwis Apex** (wybrana) — klient ma tylko odczyt na `Policy__c`, `Coverage__c`, `Claim__c`, `Claim_Document__c`; szkody i dokumenty tworzy serwis po weryfikacji własności.
2. **Read/Write + reguły walidacji blokujące zmiany po statusie Submitted** — odrzucona: FLS nie odróżnia create od edit, a utworzenie dokumentu (master-detail) wymaga zapisu na szkodzie, co po zgłoszeniu otwierałoby edycję `Incident_Date__c`, `Claimed_Amount__c`, `Description__c`; ochrona zależałaby od kompletności reguł walidacji.

**Reparenting:** pozostawienie „Allow reparenting” (odrzucone) pozwalałoby przenieść potomka pod cudzego rodzica i obejść dziedziczony sharing.

## Decyzja

1. **Agent = `OwnerId` polisy**; nadzór przez hierarchię ról.
2. **Szkody dla agenta przez Apex managed sharing** `Claim__Share` z `RowCause` = `Agent_Portfolio__c` (Read dla właściciela polisy), utrzymywany serwisem Apex (#35). **Likwidator = `OwnerId` szkody** (kolejka).
3. **Klient portalu tylko do odczytu** na czterech obiektach. Szkodę i dokumenty tworzy serwis Apex (`with sharing`): (a) `Claimant__c` z `User.ContactId` po stronie serwera, nigdy z żądania; (b) walidacja własności polisy i zakresu zapytaniem `WITH USER_MODE` (obrona przed IDOR); (c) wąski krok DML w trybie systemowym (`Database.insert(..., AccessLevel.SYSTEM_MODE)`) w małej dedykowanej klasie: `OwnerId` = kolejka likwidatorów, zapis `Claim__Share`; (d) zapis wyłącznie allowlisty pól (`Incident_Date__c`, `Description__c`, `Claimed_Amount__c`, `Coverage__c`, `Policy__c`), `Status__c` wymuszony na Submitted, nigdy `Approved_Amount__c` ani `Payout_Amount__c`.
4. **„Allow reparenting” wyłączone** na `Coverage__c` → `Policy__c` i `Claim_Document__c` → `Claim__c`. **Sharing Set po kontakcie** (`User.Contact` = `Insured__c` / `Claimant__c`).

**Udokumentowany wyjątek od NFR-SEC-03.** Krok (c) działa w trybie systemowym, bo klient jest read-only (`insert as user` zawsze by się nie powiódł), a zapis `Claim__Share` wymaga uprawnienia do udostępniania. Wyjątek jest ograniczony do jednej małej klasy, poprzedzony walidacją w trybie użytkownika i allowlistą pól. PMD (`ApexCRUDViolation`, `ApexSharingViolations`) go zgłosi; supresja ma być jawna, z uzasadnieniem w kodzie i odwołaniem do tego ADR (materiał do analizy FN/FP w pracy).

## Konsekwencje

- Mniejsza powierzchnia ataku po stronie klienta: brak bezpośredniego zapisu, więc mass assignment i edycja po zgłoszeniu są niemożliwe na poziomie uprawnień, a nie tylko reguł walidacji.
- Poprawność autoryzacji zależy od jednego serwisu Apex; wymaga testów negatywnych `System.runAs` (cudza polisa, próba ustawienia pól spoza allowlisty) w #35 oraz przeglądu bezpieczeństwa tej klasy.
- Utrzymanie `Claim__Share` to dług: trzeba obsłużyć zmianę właściciela polisy, szkody ładowane integracją (M4) i klasę recalculation (R8).
- Zmiana agenta polisy = zmiana właściciela i przeliczenie udostępnień szkód.
- Implementacja (OWD, `Claim__Share`/`RowCause`, Sharing Set, role, kolejka) pozostaje w `force-app/` w M2; ten ADR jej nie zawiera.

### Punkty otwarte (nie rozstrzygnięte tym ADR)

Pełne opisy w [logu M2](../implementacja/M2-model-danych-bezpieczenstwo.md), sekcja „Do rozstrzygnięcia”. W logu występują R1, R4–R13 oraz N1 (brak R2 i R3).

- R1 — widoczność dokumentów wewnętrznych dla klienta, osierocone `ContentDocument`, retencja (#31, #33)
- R4 — zakres kontakt vs konto (NFR-SEC-07) i widoczność szkody gdy `Claimant__c` ≠ `Insured__c` (#32, #35)
- R5 — obiekt zewnętrzny płatności bez sharingu rekordowego (M5, #33)
- R6 — wymagane lookupy do `Contact` a usunięcie danych (art. 17 RODO) (#30, #31)
- R7 — Sharing Set „po kontakcie” vs dodanie `Account__c`; potwierdzenie (#32)
- R8 — `Claim__Share` dla szkód z integracji i zmiany właściciela polisy (#35)
- R9 — odczyt dokumentów szkody przez agenta (need-to-know) (#31, #33)
- R10 — edycja `Policy__c.Insured__c` przez agenta zmienia widoczność szkód (#30)
- R11 — spójność polisa/zakres przy update szkody przez likwidatora (#35)
- R12 — zawężenie użytkownika integracyjnego (#33)
- R13 — odebranie Delete na `Claim__c` rolom A/L/K (#33)
