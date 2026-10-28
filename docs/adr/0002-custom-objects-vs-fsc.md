# 0002. Własne obiekty custom zamiast modelu danych Financial Services Cloud

- **Status:** przyjęta
- **Data:** 2026-10-29
- **Issue:** #10
- **Wymagania:** NFR-MNT-01, NFR-MNT-03

## Kontekst

System obsługuje polisy, zakresy ochrony, szkody i dokumenty szkód. Salesforce oferuje gotowy branżowy model ubezpieczeniowy w ramach Financial Services Cloud / Insurance (m.in. `InsurancePolicy`, `InsurancePolicyCoverage`, `Claim`, `ClaimParticipant`).

Ograniczenia projektu:

- środowiskiem jest Dev Hub w **Developer Edition** i efemeryczne **scratch orgi** tworzone z niego w CI (#16) — każda funkcja musi dać się włączyć w definicji scratch orga i działać w każdym PR;
- obiekty branżowe Financial Services Cloud są licencjonowane; Developer Edition ich nie zawiera, a uzyskanie ich wymaga osobnego orga z licencją (np. trial branżowy z ograniczonym czasem życia) — nie da się ich zapewnić w scratch orgach tworzonych z naszego Dev Huba przez cały okres pracy;
- praca dotyczy bezpieczeństwa i DevSecOps — model danych ma być w pełni kontrolowany (OWD, FLS, sharing) i opisany w repozytorium.

## Rozważane opcje

1. **Financial Services Cloud / Insurance data model**
   - Zalety: gotowy, standardowy model branżowy; zgodność z praktyką wdrożeń komercyjnych.
   - Wady: wymaga licencji niedostępnej w DE i scratch orgach z naszego Dev Huba; potok „scratch org per PR” nie mógłby walidować metadanych zależnych od tych obiektów; dodatkowa złożoność (obiekty, pola i automatyzacje, których nie potrzebujemy) poszerza powierzchnię ataku i utrudnia analizę bezpieczeństwa.
2. **Własne obiekty custom** — `Policy__c`, `Coverage__c`, `Claim__c`, `Claim_Document__c`; ubezpieczony jako standardowy `Account`/`Contact`.
   - Zalety: działa w DE i każdym scratch orgu bez licencji; pełna kontrola nad modelem i jego zabezpieczeniami (OWD Private, permission sety, Sharing Sets dla portalu); cały model jako metadane w `force-app/` (NFR-MNT-01); mniejsza powierzchnia do analizy SAST i testów.
   - Wady: model trzeba zaprojektować samodzielnie; brak gotowych komponentów i automatyzacji branżowych; mniejsza zgodność z produktem komercyjnym.
3. **Standardowe obiekty ogólne** (np. `Asset` jako polisa, `Case` jako szkoda).
   - Zalety: brak obiektów custom, działa wszędzie.
   - Wady: semantyka obiektów nie pasuje do domeny, pola i relacje wymagałyby obejść; `Case` zostaje wykorzystany do komunikacji klienta z agentem w portalu (M3), więc nie może jednocześnie reprezentować szkody.

## Decyzja

Wybrano **własne obiekty custom** (opcja 2). Nazwy i relacje obiektów są wzorowane na modelu FSC (polisa → zakresy ochrony, polisa → szkody → dokumenty), aby ewentualna migracja do FSC była mapowaniem 1:1, a nie przeprojektowaniem.

## Konsekwencje

- Projekt modelu danych (ERD) i jego zabezpieczeń powstaje w M2 i jest dokumentowany w `docs/architektura/`.
- Ubezpieczony to `Contact` powiązany z `Account`, co pozwala na dostęp z portalu Experience Cloud (użytkownicy społeczności powiązani z kontaktem) — zgodne z wynikiem spike'a #8.
- Ograniczenie wpisane do zakresu pracy: rozwiązanie nie korzysta z Financial Services Cloud; w podsumowaniu pracy migracja do FSC może być wskazana jako kierunek rozwoju.
- Jeśli w przyszłości będzie dostępny org z licencją FSC, decyzję można zastąpić nowym ADR.
