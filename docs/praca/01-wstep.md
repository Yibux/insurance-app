# 1. Wstęp

> **WERSJA ROBOCZA (PROWIZORYCZNA).** Konspekt pracy nie został jeszcze uzgodniony z promotorem (issue #12). Rozdział napisano według roboczego podziału na rozdziały wynikającego z [HARMONOGRAM.md](../HARMONOGRAM.md) (rozdziały teoretyczne 1–3, etapy M0–M8) i z listy zadań pisarskich #81–#89 w [BACKLOG.md](../BACKLOG.md). Po zatwierdzeniu konspektu numeracja rozdziałów, pytania badawcze (podrozdz. 1.3) i opis struktury pracy (podrozdz. 1.6) mogą się zmienić. Stan repozytorium opisany w tekście: 2026-11-02 (zakończony etap M0, trwający etap M1). Elementy systemu, które na ten dzień nie istnieją, są w tekście nazywane „planowanymi”.
>
> **Konwencja cytowania w wersji roboczej.** Źródła literaturowe są przywoływane w postaci (Autor, rok) i odpowiadają pozycjom z [RAPORT.md, rozdz. 3 i 9](../RAPORT.md#3-przegląd-literatury). Plik `docs/praca/bibliografia.md` (przygotowywany przez `literature-researcher`) jeszcze nie istnieje, dlatego pełne opisy bibliograficzne i numery stron zostaną uzupełnione później. Fakty dotyczące budowanego systemu są przywoływane przez numer ADR, numer issue/PR lub sekcję dziennika implementacji.

## 1.1. Tło i motywacja

Systemy zarządzania relacjami z klientem (ang. _Customer Relationship Management_, CRM) są coraz częściej udostępniane w modelu chmury obliczeniowej jako usługa (ang. _Software as a Service_, SaaS), w którym jeden dostawca utrzymuje platformę współdzieloną przez wielu klientów [ŹRÓDŁO? definicja SaaS i chmury obliczeniowej, np. NIST SP 800-145]. Jedną z takich platform jest Salesforce. Jej architektura jest wielodostępna (ang. _multi-tenant_): dane i metadane wielu organizacji-klientów są przechowywane i przetwarzane na wspólnej infrastrukturze, a izolacja między nimi jest realizowana logicznie przez platformę [ŹRÓDŁO? oficjalny opis architektury multi-tenant Salesforce]. W takim modelu odpowiedzialność za bezpieczeństwo jest podzielona: dostawca odpowiada za infrastrukturę i mechanizmy platformy, a klient za konfigurację dostępu, kod własnych aplikacji i integracje. Al Kalach (2025) opisuje rozwój modelu bezpieczeństwa Salesforce w kierunku obrony wielowarstwowej (ang. _defense in depth_) i zwraca uwagę na model współodpowiedzialności (ang. _shared responsibility_) między dostawcą platformy a klientem.

Branża ubezpieczeniowa jest szczególnie wymagającym przypadkiem użycia takiej platformy. System obsługi ubezpieczeń przetwarza dane osobowe ubezpieczonych, informacje o zdarzeniach szkodowych (w tym potencjalnie dane o zdrowiu) oraz dane finansowe [ŹRÓDŁO? charakterystyka danych przetwarzanych przez zakłady ubezpieczeń i kategorie danych szczególnych wg RODO, art. 9]. Podlega przy tym regulacjom dotyczącym ochrony danych osobowych i odporności operacyjnej sektora finansowego [ŹRÓDŁO? RODO (Rozporządzenie (UE) 2016/679) oraz regulacje sektorowe, np. DORA (Rozporządzenie (UE) 2022/2554) — do potwierdzenia, czy mają zastosowanie do zakresu pracy]. Błąd w konfiguracji uprawnień lub w kodzie aplikacji może więc prowadzić do ujawnienia danych klientów innym klientom albo nieuprawnionym pracownikom.

Drugim źródłem ryzyka jest sam proces wytwarzania oprogramowania. Zmiany w aplikacji na platformie Salesforce mają postać metadanych (definicji obiektów, uprawnień, stron) i kodu (Apex, Lightning Web Components), które są wdrażane między środowiskami. Guduru (2023) opisuje ciągłą integrację i ciągłe dostarczanie (ang. _Continuous Integration / Continuous Delivery_, CI/CD) w ekosystemie Salesforce jako automatyzację wdrażania metadanych, konfiguracji i kodu do różnych środowisk, od sandboxów po organizację produkcyjną. Jeżeli kontrola bezpieczeństwa takich zmian odbywa się dopiero po wdrożeniu lub okresowo, podatność może przez długi czas pozostawać w systemie produkcyjnym.

Odpowiedzią na ten problem jest podejście DevSecOps, czyli włączenie praktyk bezpieczeństwa (ang. _Security_) do zintegrowanego procesu wytwarzania (ang. _Development_) i utrzymania (ang. _Operations_) oprogramowania, tak aby kontrole bezpieczeństwa były zautomatyzowanymi krokami potoku CI/CD, a nie osobnym etapem po zakończeniu prac [ŹRÓDŁO? definicja DevSecOps z publikacji przeglądowej lub normy/standardu, np. NIST SP 800-204C]. Z DevSecOps ściśle wiąże się zasada przesunięcia bezpieczeństwa w lewo (ang. _shift-left security_), tj. wykrywania podatności w jak najwcześniejszej fazie cyklu życia oprogramowania. Autorzy opracowania _Shift Left Security_ (2025) ujmują ją jako proaktywne usuwanie podatności na wczesnych etapach cyklu życia oprogramowania (ang. _Software Development Life Cycle_, SDLC) zamiast reagowania na nie po fakcie. Bavadiya (2022) wskazuje, że włączenie zautomatyzowanych kontroli bezpieczeństwa do wszystkich etapów CI/CD może ograniczyć ryzyko po wdrożeniu, wzmocnić reagowanie na incydenty i jednocześnie utrzymać tempo wytwarzania oprogramowania.

Badania empiryczne pokazują jednak, że deklaracje nie przekładają się automatycznie na praktykę. W badaniu ankietowym Cheenepalli i in. (2025) bezpieczeństwo jest priorytetem dla 73% kadry kierowniczej, ale tylko 12% organizacji wykonuje skanowanie bezpieczeństwa przy każdym commicie. Przegląd systematyczny opublikowany przez IEEE w 2025 roku (IEEE SLR, 2025) wśród najistotniejszych zagrożeń dla środowisk DevOps wymienia niekontrolowaną automatyzację, ujawnianie sekretów w potokach CI/CD i ataki na łańcuch dostaw oprogramowania. Jammeh (2020) podkreśla z kolei, że skuteczność DevSecOps zależy od dostępu zespołu do wiedzy o bezpieczeństwie i od zrozumienia przez każdego jego członka własnej odpowiedzialności.

Wreszcie, same narzędzia automatyzujące kontrolę bezpieczeństwa nie są bezbłędne. Autorzy pracy _Find Bugs in Static Bug Finders_ (IEEE/ACM, 2022) zidentyfikowali 46 błędów w implementacji lub projekcie reguł narzędzi statycznej analizy kodu (ang. _Static Application Security Testing_, SAST). Ta obserwacja znalazła potwierdzenie już na wczesnym etapie prac nad systemem opisanym w niniejszej pracy:

- domyślny zestaw reguł `Recommended` narzędzia Salesforce Code Analyzer nie zgłosił klasy Apex z jawną deklaracją `without sharing` ani klasy wykonującej operacje DML bez deklaracji współdzielenia; konieczne było dodanie reguły `ApexSharingViolations` i reguły własnej (dziennik M1, wpis #18; [ADR 0004](../adr/0004-code-analyzer-rules.md));
- bramka pokrycia kodu testami uruchamiana na wszystkich testach lokalnych organizacji przepuściła klasę o pokryciu 40%, ponieważ wynik łączny (82,14%) zawyżały klasy kontrolerów dodawane przez Experience Cloud; poprawka polegała na liczeniu wyłącznie testów i klas z repozytorium (dziennik M1, wpis #17, przebiegi 41360184741 i 41360432846).

Oba przypadki pokazują, że potok bezpieczeństwa należy nie tylko zbudować, lecz także sprawdzić, czy faktycznie wykrywa to, do czego jest przeznaczony. Ta potrzeba stanowi bezpośrednią motywację części badawczej pracy (podrozdz. 1.3).

## 1.2. Problem

Na podstawie przedstawionego tła sformułowano problem, którym zajmuje się praca: **jak zaprojektować i zbudować system obsługi ubezpieczeń na platformie Salesforce tak, aby (a) model dostępu do danych realizował zasadę minimalnych uprawnień i model zerowego zaufania, a (b) każda zmiana w systemie była przed scaleniem automatycznie weryfikowana przez bramki bezpieczeństwa, których skuteczność da się zmierzyć.**

Model zerowego zaufania (ang. _Zero Trust_) rozumiany jest w pracy jako zasada, zgodnie z którą żaden użytkownik, proces ani system nie otrzymuje dostępu domyślnie, a każdy dostęp jest jawnie nadany i weryfikowany [ŹRÓDŁO? definicja Zero Trust Architecture, np. NIST SP 800-207]; jego odniesienie do platformy Salesforce omawia Al Kalach (2025). Bramka bezpieczeństwa (ang. _security gate_) oznacza w pracy zautomatyzowany krok potoku CI/CD, którego negatywny wynik oznacza niepowodzenie walidacji zmiany (ang. _pull request_, PR).

Problem ma dwa wymiary, które w pracy traktuje się łącznie. Wymiar projektowy dotyczy mechanizmów platformy (domyślnej widoczności rekordów, zestawów uprawnień, egzekwowania uprawnień do obiektów i pól w kodzie) oraz bezpieczeństwa integracji z systemem zewnętrznym. Wymiar procesowy dotyczy potoku, który ma te same zasady wymuszać przy każdej zmianie.

## 1.3. Cel pracy, cele szczegółowe i pytania badawcze

**Celem głównym pracy** jest zaprojektowanie i zaimplementowanie systemu do zarządzania polisami i szkodami ubezpieczeniowymi na platformie Salesforce, wytwarzanego zgodnie z metodyką DevSecOps, oraz empiryczna ocena skuteczności zastosowanych automatycznych bramek bezpieczeństwa. Cel ten rozwija sformułowanie z [RAPORT.md, rozdz. 2](../RAPORT.md#2-temat-pracy) o element pomiarowy opisany w [HARMONOGRAM.md, pkt 4](../HARMONOGRAM.md#4-część-badawcza-żeby-praca-nie-była-tylko-zbudowałem-aplikację).

**Cele szczegółowe:**

1. Przegląd literatury dotyczącej bezpieczeństwa chmurowych systemów CRM, modelu zerowego zaufania w Salesforce oraz praktyk DevSecOps (rozdziały 2–4).
2. Specyfikacja wymagań funkcjonalnych i niefunkcjonalnych systemu z macierzą śledzenia do zadań i literatury ([WYMAGANIA.md](../WYMAGANIA.md), wersja 0.1 z 18.10.2026: 35 wymagań funkcjonalnych i 35 niefunkcjonalnych).
3. Budowa potoku CI/CD, który dla każdego PR tworzy efemeryczne środowisko, wdraża do niego zmiany, uruchamia testy z progiem pokrycia 75% oraz statyczną analizę kodu, skanowanie sekretów i analizę podatnych zależności (wymagania FR-CI-01 – FR-CI-09).
4. Zaprojektowanie modelu danych i modelu uprawnień zgodnego z zasadą minimalnych uprawnień (NFR-SEC-01 – NFR-SEC-04) oraz portalu klienta z dostępem ograniczonym do danych własnego konta (NFR-SEC-07) — planowane w etapach M2–M3.
5. Integracja z zewnętrznym serwerem w języku Python: bezpieczne ładowanie danych historycznych oraz prezentacja danych wrażliwych bez ich przechowywania w CRM (NFR-SEC-06, NFR-SEC-08, NFR-CMP-01) — planowane w etapach M4–M5.
6. Przeprowadzenie eksperymentu oceniającego bramki potoku na zbiorze celowo wprowadzonych podatności — planowane w etapie M6.

**Pytania badawcze (propozycja do uzgodnienia z promotorem):**

- **PB1.** Jaka część celowo wprowadzonych podatności typowych dla aplikacji Salesforce (m.in. wstrzyknięcie SOQL, brak kontroli uprawnień do obiektów i pól, `without sharing`, zaszyty sekret, podatna zależność, XSS w komponencie LWC, zapytanie SOQL w pętli) zostaje wykryta przez poszczególne bramki potoku i ile fałszywych alarmów one generują? Miary: liczba wyników prawdziwie pozytywnych (TP), fałszywie negatywnych (FN) i fałszywie pozytywnych (FP) dla każdej bramki.
- **PB2.** Na którym etapie podatność zostaje wykryta: lokalnie przed commitem (hooki Git), w potoku PR, czy wcale?
- **PB3.** Jaki jest koszt czasowy pełnej walidacji PR w ograniczeniach środowiska Developer Edition i czy mieści się w założonym limicie mediany 20 minut (NFR-PERF-01)?

Katalog kategorii podatności, liczba zmian (ok. 20–30) i mierzone wielkości pochodzą z planu eksperymentu w [HARMONOGRAM.md, pkt 4](../HARMONOGRAM.md#4-część-badawcza-żeby-praca-nie-była-tylko-zbudowałem-aplikację). Projekt eksperymentu nawiązuje do oceny bramek jakości u Bavadiyi (2022) i do analizy błędów narzędzi SAST (IEEE/ACM, 2022).

## 1.4. Zakres pracy i ograniczenia

### Zakres

System składa się z trzech warstw opisanych w [RAPORT.md, rozdz. 2](../RAPORT.md#2-temat-pracy) i rozwijanych w jednym repozytorium ([ADR 0001](../adr/0001-monorepo.md)):

- **warstwa CRM i portal klienta** — model danych polis, zakresów ochrony, szkód i dokumentów szkód na platformie Salesforce oraz portal ubezpieczonego w technologii Experience Cloud (platforma Salesforce do budowy portali dla użytkowników zewnętrznych), w którym ubezpieczony przegląda własne polisy, zgłasza szkody i komunikuje się z agentem (FR-POL, FR-CLM, FR-PRT, FR-COM);
- **potok CI/CD** — GitHub Actions z Salesforce CLI, uwierzytelnianiem do Dev Hubu przepływem JWT Bearer ([ADR 0003](../adr/0003-jwt-bearer-ci-auth.md)) i efemeryczną organizacją testową (ang. _scratch org_) tworzoną dla każdego PR i usuwaną po walidacji (dziennik M1, wpis #16). Scratch org to tymczasowe, konfigurowane plikiem definicji środowisko Salesforce (SF DX Guide); szczegóły w rozdziale 4;
- **serwer integracyjny w języku Python** — ładowanie danych historycznych przez Bulk API 2.0 (FR-MIG) oraz udostępnianie danych wrażliwych w protokole OData 4.0, prezentowanych w Salesforce jako obiekty zewnętrzne (ang. _External Objects_), czyli bez kopiowania ich do CRM (FR-EXT, NFR-CMP-01). Dostępność tego mechanizmu w środowisku projektu potwierdzono w spike'u #9 ([notatka](../spikes/salesforce-connect-odata.md)).

Rozdzielenie etapów prac jest podporządkowane zasadzie shift-left: potok z bramkami bezpieczeństwa powstaje (etap M1) przed logiką biznesową (etapy M2–M5), aby cały kod aplikacji od początku przechodził przez bramki ([HARMONOGRAM.md, „Założenia”](../HARMONOGRAM.md#założenia)).

### Poza zakresem

Zgodnie z [WYMAGANIA.md, rozdz. 4](../WYMAGANIA.md#4-poza-zakresem-w) poza zakresem pracy pozostają: rozliczenia finansowe i integracja z systemem płatności, kalkulacja składki, natywna aplikacja mobilna oraz Financial Services Cloud.

### Ograniczenia

- **Brak Financial Services Cloud.** Salesforce oferuje branżowy model danych ubezpieczeniowych w ramach Financial Services Cloud [ŹRÓDŁO? dokumentacja Salesforce: Financial Services Cloud — Insurance data model]. Model ten wymaga licencji niedostępnej w Developer Edition i w scratch orgach tworzonych z Dev Hubu projektu, dlatego zaprojektowano własne obiekty (`Policy__c`, `Coverage__c`, `Claim__c`, `Claim_Document__c`), nazwane i powiązane analogicznie do modelu branżowego ([ADR 0002](../adr/0002-custom-objects-vs-fsc.md)). Wyniki pracy nie obejmują więc funkcji i automatyzacji dostarczanych przez produkt branżowy.
- **Limity Developer Edition.** Dev Hub działa na organizacji Developer Edition, w której obowiązuje limit 3 aktywnych i 6 nowych scratch orgów w ciągu doby [ŹRÓDŁO? dokumentacja Salesforce: Scratch Org Allocations for Salesforce Editions]. Wpływa to na konstrukcję potoku (filtr ścieżek, globalna kolejka zadań tworzących scratch org; dziennik M1, wpis #16; [ADR 0001](../adr/0001-monorepo.md)) i ogranicza liczbę przebiegów możliwych do wykonania w eksperymencie (NFR-PERF-05).
- **Jeden autor i projekt dyplomowy.** System jest rozwijany przez jedną osobę, bez rzeczywistych użytkowników i wyłącznie na danych syntetycznych (NFR-CMP-02). Wnioski dotyczące procesu (np. przeglądy kodu, czynnik ludzki opisywany przez Jammeha (2020)) mają więc ograniczoną możliwość uogólnienia na zespoły.
- **Egzekwowanie bramek.** Na dzień 2026-11-02 reguły ochrony gałęzi `main` wymagające zielonych checków nie są włączone (zadania #6 i #25); bramki oznaczają PR jako niepoprawny, ale nie blokują jeszcze technicznie scalenia (dziennik M1, wpis #27).
- **Narzędzia komercyjne nieporównywane eksperymentalnie.** Wybór GitHub Actions zamiast wyspecjalizowanej platformy Copado uzasadniono analizą dokumentacji i modelu licencyjnego, bez wdrożenia Copado (dziennik M1, wpis #27). Porównanie ma charakter jakościowy.

## 1.5. Metoda i przebieg prac

Praca łączy trzy metody:

1. **Analizę literatury** — przegląd publikacji naukowych i branżowych zebranych w [RAPORT.md](../RAPORT.md), uzupełniany o dokumentację techniczną platformy Salesforce i ramy oceny bezpieczeństwa (np. OWASP) [ŹRÓDŁO? OWASP Top 10 / OWASP SAMM — do dodania do bibliografii, zgodnie z uwagą w HARMONOGRAM.md, pkt 3].
2. **Projekt i implementację** (ang. _design and implementation_) — wytwarzanie systemu w ośmiu etapach (M0–M8) od 12.10.2026, z zamrożeniem kodu 15.06.2027 ([HARMONOGRAM.md, pkt 2](../HARMONOGRAM.md#2-harmonogram-start-12102026-kod-zamrożony-15062027-oddanie-ix-2027)). Każda decyzja architektoniczna lub wybór narzędzia jest zapisywana jako rekord decyzji architektonicznej (ang. _Architecture Decision Record_, ADR) w katalogu `docs/adr/` (kontekst, rozważane opcje, decyzja, konsekwencje), a każde zakończone zadanie — jako wpis w dzienniku implementacji `docs/implementacja/` z sekcjami „Decyzje i alternatywy”, „Problemy” i „Dowody” ([KONWENCJE.md, pkt 3](../KONWENCJE.md#3-definition-of-done-każde-zadanie)). Dzięki temu rozumowanie prowadzące do rozwiązań (problem → opcje → decyzja → dowód) jest udokumentowane w momencie podejmowania decyzji, a nie odtwarzane po fakcie.
3. **Eksperyment** — pomiar skuteczności bramek na zbiorze celowo podatnych zmian zgłaszanych jako osobne PR (podrozdz. 1.3, etap M6), z wynikami gromadzonymi w `docs/experiment/`.

Przebiegi potoku CI/CD są przechowywane w historii GitHub Actions i powoływane w tekście numerem przebiegu, co pozwala recenzentowi zweryfikować przytaczane wyniki.

## 1.6. Struktura pracy

Roboczy układ pracy przedstawiono w tabeli 1.1.

**Tabela 1.1.** Roboczy układ rozdziałów pracy (do zatwierdzenia z promotorem, issue #12)

| Rozdział | Tytuł roboczy                                                                     | Zawartość                                                                                                                                               | Zadanie |
| -------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| 1        | Wstęp                                                                             | motywacja, problem, cel, pytania badawcze, zakres, metoda                                                                                               | #81     |
| 2        | Bezpieczeństwo chmurowych systemów CRM i model zerowego zaufania w Salesforce     | wielodostępność, model współodpowiedzialności, Zero Trust (Al Kalach, 2025), mechanizmy bezpieczeństwa platformy (widoczność rekordów, uprawnienia, FLS) | #82     |
| 3        | DevSecOps i CI/CD                                                                 | shift-left, SAST, zarządzanie sekretami, łańcuch dostaw; Bavadiya (2022), Cheenepalli i in. (2025), IEEE SLR (2025), Jammeh (2020), Lakade (2025) i in. | #83     |
| 4        | Środowiska efemeryczne i bezpieczeństwo integracji                                | scratch orgi (Guduru, 2023; SF DX Guide), JWT i OAuth 2.0 (Machapatri, 2020), obiekty zewnętrzne i rezydencja danych                                    | #84     |
| 5        | Wymagania i projekt systemu                                                       | wymagania, decyzje architektoniczne (ADR), model danych, model uprawnień, architektura potoku                                                           | #85     |
| 6        | Implementacja                                                                     | realizacja etapów M0–M6 na podstawie dziennika implementacji                                                                                            | #86     |
| 7        | Wyniki eksperymentu i dyskusja                                                    | metodyka, wyniki, zagrożenia dla trafności, porównanie z literaturą                                                                                     | #87     |
| 8        | Podsumowanie i wnioski                                                            | ocena realizacji celów, ograniczenia, kierunki dalszych prac                                                                                            | #88     |

Źródło: opracowanie własne na podstawie [BACKLOG.md](../BACKLOG.md) (zadania #81–#88) i [HARMONOGRAM.md, pkt 3](../HARMONOGRAM.md#3-literatura-z-raportu-gdzie-ją-wykorzystać).

Rozdziały 2–4 stanowią część teoretyczną i przygotowują pojęcia wykorzystywane w części projektowej. Rozdział 5 przekłada wymagania i decyzje architektoniczne na projekt systemu, rozdział 6 opisuje jego realizację, a rozdział 7 odpowiada na pytania badawcze PB1–PB3. Rozdział 8 zestawia cele pracy z uzyskanymi wynikami. Streszczenia, słowa kluczowe i bibliografia są przedmiotem zadania #89.

---

## Materiał roboczy (do usunięcia przed redakcją końcową)

### Luki źródłowe `[ŹRÓDŁO?]`

1. Definicja SaaS / chmury obliczeniowej (np. NIST SP 800-145) — podrozdz. 1.1.
2. Oficjalny opis architektury multi-tenant Salesforce (np. dokument techniczny Salesforce o architekturze wielodostępnej) — podrozdz. 1.1.
3. Charakterystyka danych przetwarzanych przez ubezpieczycieli, w tym dane szczególnych kategorii (RODO, art. 9) — podrozdz. 1.1.
4. Regulacje: RODO (Rozporządzenie (UE) 2016/679); ewentualnie DORA (Rozporządzenie (UE) 2022/2554) — do decyzji, czy powoływać — podrozdz. 1.1.
5. Definicja DevSecOps z publikacji przeglądowej lub standardu (np. NIST SP 800-204C) — podrozdz. 1.1.
6. Definicja Zero Trust Architecture (np. NIST SP 800-207) — podrozdz. 1.2.
7. Dokumentacja Salesforce: Financial Services Cloud — model danych ubezpieczeniowych — podrozdz. 1.4.
8. Dokumentacja Salesforce: limity scratch orgów dla edycji (Scratch Org Allocations) — podrozdz. 1.4.
9. OWASP Top 10 / OWASP SAMM jako rama oceny — podrozdz. 1.5.

Dodatkowo dla źródeł już obecnych w [RAPORT.md](../RAPORT.md) brakuje danych potrzebnych do pełnego opisu bibliograficznego: autorów publikacji „IEEE SLR (2025)” i „Shift Left Security (2025)” (w raporcie opisanych jako „Publikacja IEEE” i „Praca zbiorowa”), autorów pracy „Find Bugs in Static Bug Finders” (IEEE/ACM, 2022), numerów stron dla przytaczanych tez oraz DOI. Tezy przytoczone w podrozdz. 1.1 są parafrazami cytatów z RAPORT.md i wymagają sprawdzenia z oryginałami.

### Pytania otwarte do promotora

1. Czy roboczy układ ośmiu rozdziałów (tabela 1.1) odpowiada oczekiwaniom, czy rozdziały 2–4 połączyć w jeden rozdział teoretyczny?
2. Czy pytania badawcze PB1–PB3 mają pozostać pytaniami, czy należy sformułować tezę lub hipotezy (np. o odsetku podatności wykrywanych w PR)?
3. Czy do motywacji powoływać regulacje sektorowe (DORA, wytyczne nadzoru), skoro system nie jest wdrażany w rzeczywistym zakładzie ubezpieczeń?
4. Czy źródło Al Kalach (2025), dostępne w serwisie Scribd, jest akceptowalne jako pozycja naukowa, czy należy je zastąpić publikacją recenzowaną lub dokumentacją Salesforce (Security Implementation Guide)?
5. Czy we wstępie przywoływać wczesne obserwacje z budowy potoku (dziennik M1, wpisy #17 i #18), czy przenieść je w całości do rozdziałów 6–7?
6. Jaki styl cytowania (autor–rok czy numeryczny) wymaga uczelnia?

### Wykorzystane fakty z repozytorium

- [RAPORT.md](../RAPORT.md), rozdz. 1–3: temat, cel, zakres technologiczny, tezy Al Kalach (2025), Guduru (2023), Shift Left Security (2025), Bavadiya (2022), Cheenepalli i in. (2025: 73%, 12%), IEEE SLR (2025), Jammeh (2020), IEEE/ACM (2022: 46 błędów).
- [HARMONOGRAM.md](../HARMONOGRAM.md): zasada shift-left w kolejności etapów, etapy M0–M8, daty 12.10.2026 i 15.06.2027, plan eksperymentu (20–30 zmian, kategorie podatności, TP/FN/FP, czas potoku), uwaga o OWASP.
- [WYMAGANIA.md](../WYMAGANIA.md), wersja 0.1 z 18.10.2026: grupy FR-POL, FR-CLM, FR-PRT, FR-COM, FR-MIG, FR-EXT, FR-CI (35 wymagań funkcjonalnych), NFR (35 wymagań niefunkcjonalnych, w tym NFR-SEC-01–04, 06, 07, 08, NFR-CMP-01, 02, NFR-PERF-01, 05), rozdz. 4 „Poza zakresem”.
- [ADR 0001](../adr/0001-monorepo.md) (monorepo), [ADR 0002](../adr/0002-custom-objects-vs-fsc.md) (brak FSC), [ADR 0003](../adr/0003-jwt-bearer-ci-auth.md) (JWT Bearer), [ADR 0004](../adr/0004-code-analyzer-rules.md) (reguły Code Analyzer).
- [Spike #9](../spikes/salesforce-connect-odata.md): Salesforce Connect OData 4.0 dostępny w DE i scratch orgu.
- Dziennik M1 (`docs/implementacja/M1-potok-devsecops.md`): wpis #16 (scratch org per PR, concurrency), #17 (pokrycie 40% vs 82,14%, przebiegi 41360184741 i 41360432846), #18 (`Recommended` nie wykrył `without sharing`), #27 (branch protection niewłączone, Copado nietestowane). Uwaga: wpis #27 i ADR 0008 są w PR #115, który w chwili pisania nie jest scalony do `main` — dlatego rozdział nie linkuje bezpośrednio ADR 0008 ani `docs/architektura/potok-cicd.md`.
- [BACKLOG.md](../BACKLOG.md): zadania #12, #81–#89 (struktura rozdziałów), #6 i #25 (ochrona gałęzi).
