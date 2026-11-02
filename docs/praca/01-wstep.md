# 1. Wstęp

> **WERSJA ROBOCZA (PROWIZORYCZNA).** Konspekt pracy nie został jeszcze uzgodniony z promotorem (issue #12). Rozdział napisano według roboczego układu wynikającego z [HARMONOGRAM.md](../HARMONOGRAM.md) i z listy zadań pisarskich #81–#89 w [BACKLOG.md](../BACKLOG.md). Po zatwierdzeniu konspektu numeracja rozdziałów, pytania badawcze (podrozdz. 1.3) i opis struktury pracy (podrozdz. 1.7) mogą się zmienić. Tekst opisuje stan repozytorium na dzień 2026-11-02. Etap M0 jest wtedy zakończony z wyjątkiem zadania #6 (ochrona gałęzi), a etap M1 trwa. Elementy systemu, które na ten dzień nie istnieją, są w tekście nazywane „planowanymi”.
>
> **Konwencja cytowania w wersji roboczej.** Źródła literaturowe są przywoływane w postaci (Autor, rok) i odpowiadają pozycjom z [RAPORT.md, rozdz. 3 i 9](../RAPORT.md#3-przegląd-literatury). Pełne opisy bibliograficzne i numery stron zostaną uzupełnione później. Fakty dotyczące budowanego systemu są przywoływane przez numer ADR, numer zadania (issue) lub PR albo wpis dziennika implementacji. W tekście końcowym odwołania do dokumentów repozytorium zostaną przeniesione do przypisów lub do załącznika.

## 1.1. Tło i motywacja

Systemy zarządzania relacjami z klientem (ang. _Customer Relationship Management_, CRM) są udostępniane m.in. w modelu oprogramowania jako usługi (ang. _Software as a Service_, SaaS). W tym modelu jeden dostawca utrzymuje platformę współdzieloną przez wielu klientów [ŹRÓDŁO? definicja SaaS i chmury obliczeniowej, np. NIST SP 800-145; dane o upowszechnieniu CRM w modelu SaaS]. Jedną z takich platform jest Salesforce. Jej architektura jest wielodostępna (ang. _multi-tenant_): dane i metadane wielu organizacji-klientów są przechowywane i przetwarzane na wspólnej infrastrukturze, a izolację między nimi zapewnia logicznie platforma [ŹRÓDŁO? oficjalny opis architektury multi-tenant Salesforce].

W takim modelu odpowiedzialność za bezpieczeństwo jest podzielona. Dostawca odpowiada za infrastrukturę i mechanizmy platformy, a klient za konfigurację dostępu, kod własnych aplikacji i integracje. Al Kalach (2025) opisuje rozwój modelu bezpieczeństwa Salesforce w kierunku obrony wielowarstwowej (ang. _defense in depth_). Zwraca przy tym uwagę na model współodpowiedzialności (ang. _shared responsibility_) między dostawcą platformy a klientem.

Branża ubezpieczeniowa jest wymagającym przypadkiem użycia takiej platformy. System obsługi ubezpieczeń przetwarza dane osobowe ubezpieczonych, informacje o zdarzeniach szkodowych (w tym potencjalnie dane o zdrowiu) oraz dane finansowe [ŹRÓDŁO? charakterystyka danych przetwarzanych przez zakłady ubezpieczeń i kategorie danych szczególnych wg RODO, art. 9]. Podlega przy tym regulacjom dotyczącym ochrony danych osobowych i odporności operacyjnej sektora finansowego [ŹRÓDŁO? RODO (Rozporządzenie (UE) 2016/679) oraz regulacje sektorowe, np. DORA (Rozporządzenie (UE) 2022/2554) — do potwierdzenia, czy mają zastosowanie do zakresu pracy]. Z tego powodu w pracy przyjęto założenie, że błąd w konfiguracji uprawnień lub w kodzie aplikacji należy traktować jako potencjalną drogę ujawnienia danych klientów innym klientom albo nieuprawnionym pracownikom.

Drugim źródłem ryzyka jest sam proces wytwarzania oprogramowania. Zmiany w aplikacji na platformie Salesforce mają postać metadanych (definicji obiektów, uprawnień, stron) i kodu. Kod jest pisany w języku Apex (języku programowania wykonywanym na serwerach platformy) oraz w bibliotece komponentów interfejsu Lightning Web Components (LWC) [ŹRÓDŁO? dokumentacja Salesforce: Apex Developer Guide, LWC Developer Guide]. Guduru (2023) opisuje ciągłą integrację i ciągłe dostarczanie (ang. _Continuous Integration / Continuous Delivery_, CI/CD) w ekosystemie Salesforce jako automatyzację wdrażania metadanych, konfiguracji i kodu do różnych środowisk, od sandboxów po organizację produkcyjną. W pracy przyjęto rozumowanie, że jeżeli kontrola bezpieczeństwa takich zmian odbywa się dopiero po wdrożeniu lub okresowo, to wprowadzona podatność pozostaje w systemie produkcyjnym co najmniej do najbliższej kontroli.

Odpowiedzią na ten problem jest podejście DevSecOps. Polega ono na włączeniu praktyk bezpieczeństwa (ang. _Security_) do zintegrowanego procesu wytwarzania (ang. _Development_) i utrzymania (ang. _Operations_) oprogramowania. Kontrole bezpieczeństwa stają się wtedy zautomatyzowanymi krokami potoku CI/CD, a nie osobnym etapem po zakończeniu prac [ŹRÓDŁO? definicja DevSecOps z publikacji przeglądowej lub normy/standardu, np. NIST SP 800-204C]. Z DevSecOps ściśle wiąże się zasada przesunięcia bezpieczeństwa w lewo (ang. _shift-left security_), tj. wykrywania podatności w jak najwcześniejszej fazie cyklu życia oprogramowania (ang. _Software Development Life Cycle_, SDLC). Autorzy opracowania _Shift Left Security_ (2025) ujmują ją jako proaktywne usuwanie podatności na wczesnych etapach SDLC zamiast reagowania na nie po fakcie. Bavadiya (2022) wskazuje, że włączenie zautomatyzowanych kontroli bezpieczeństwa do wszystkich etapów CI/CD może ograniczyć ryzyko po wdrożeniu i wzmocnić reagowanie na incydenty. Według autora pozwala to jednocześnie utrzymać tempo wytwarzania oprogramowania.

Badania empiryczne pokazują jednak, że deklaracje nie przekładają się automatycznie na praktykę. Cheenepalli i in. (2025) przeprowadzili badanie ankietowe na próbie 405 specjalistów, dotyczące DevSecOps w małych i średnich przedsiębiorstwach (MŚP). Bezpieczeństwo było w nim priorytetem dla 73% kadry kierowniczej, ale tylko 12% organizacji wykonywało skanowanie bezpieczeństwa przy każdym zatwierdzeniu zmian w repozytorium (ang. _commit_). Przegląd systematyczny opublikowany przez IEEE w 2025 roku (IEEE SLR, 2025) wśród najistotniejszych zagrożeń dla środowisk DevOps wymienia niekontrolowaną automatyzację, ujawnianie sekretów w potokach CI/CD i ataki na łańcuch dostaw oprogramowania. Jammeh (2020) podkreśla z kolei, że skuteczność DevSecOps zależy od dostępu zespołu do wiedzy o bezpieczeństwie. Zależy też od tego, czy każdy członek zespołu rozumie własną odpowiedzialność w tym zakresie.

Wreszcie, same narzędzia automatyzujące kontrolę bezpieczeństwa nie są bezbłędne. Autorzy pracy _Find Bugs in Static Bug Finders_ (IEEE/ACM, 2022) zidentyfikowali 46 błędów w implementacji lub projekcie reguł narzędzi statycznej analizy kodu (ang. _static analysis_). Statyczna analiza kodu ukierunkowana na bezpieczeństwo jest w branży określana jako SAST (ang. _Static Application Security Testing_) [ŹRÓDŁO? definicja SAST, np. OWASP]. Podobne ryzyko — że automatyczna kontrola daje wynik inny niż oczekiwany — zaobserwowano już na wczesnym etapie budowy potoku opisanego w niniejszej pracy. Żaden z dwóch przypadków nie jest błędem w samym narzędziu w rozumieniu cytowanej pracy:

- **Luka w konfiguracji domyślnej.** Domyślny zestaw reguł `Recommended` narzędzia Salesforce Code Analyzer nie zgłosił klasy Apex z jawną deklaracją `without sharing` (wyłączenie reguł współdzielenia rekordów). Nie zgłosił też klasy wykonującej operacje zapisu danych (ang. _Data Manipulation Language_, DML) bez deklaracji współdzielenia. Reguła `ApexSharingViolations` nie należy do tego zestawu, a jawnego `without sharing` nie zgłaszała żadna reguła PMD z użytej konfiguracji. Konieczne było dołączenie `ApexSharingViolations` i dodanie reguły własnej (dziennik M1, wpis #18; [ADR 0004](../adr/0004-code-analyzer-rules.md)).
- **Wada w projekcie własnej bramki.** Pierwsza wersja bramki pokrycia kodu testami liczyła wynik ze wszystkich testów lokalnych organizacji (`RunLocalTests`). Do wyniku wliczały się więc klasy kontrolerów dodawane przez platformę Experience Cloud. W efekcie klasa o pokryciu 40% przeszła bramkę, ponieważ wynik łączny wyniósł 82,14%. Poprawka polegała na liczeniu wyłącznie testów i klas z repozytorium (dziennik M1, wpis #17; przebiegi 41360184741 i 41360432846).

Oba przypadki pokazują, że potok bezpieczeństwa należy nie tylko zbudować, lecz także sprawdzić, czy faktycznie wykrywa to, do czego jest przeznaczony. Ta potrzeba stanowi bezpośrednią motywację części badawczej pracy (podrozdz. 1.3).

## 1.2. Problem

Na podstawie przedstawionego tła sformułowano problem, którym zajmuje się praca: **jak zaprojektować i zbudować system obsługi ubezpieczeń na platformie Salesforce tak, aby (a) model dostępu do danych realizował zasadę najmniejszych uprawnień i model zerowego zaufania w zakresie autoryzacji dostępu do danych, a (b) każda zmiana w systemie była przed scaleniem automatycznie weryfikowana przez bramki bezpieczeństwa, których skuteczność da się zmierzyć.**

Zasada najmniejszych uprawnień (ang. _principle of least privilege_) oznacza nadawanie użytkownikowi lub procesowi wyłącznie uprawnień niezbędnych do wykonania jego zadań [ŹRÓDŁO? definicja zasady najmniejszych uprawnień, np. NIST SP 800-53 AC-6 lub glosariusz NIST]. Model zerowego zaufania (ang. _Zero Trust_) rozumiany jest w pracy jako zasada, zgodnie z którą żaden użytkownik, proces ani system nie otrzymuje dostępu domyślnie, a każdy dostęp jest jawnie nadany i weryfikowany [ŹRÓDŁO? definicja Zero Trust Architecture, np. NIST SP 800-207]. Jego odniesienie do platformy Salesforce omawia Al Kalach (2025).

Praca obejmuje tylko część elementów architektury zerowego zaufania. Obejmuje domyślny brak dostępu do rekordów, jawne nadawanie uprawnień przez zestawy uprawnień, egzekwowanie uprawnień w kodzie oraz uwierzytelnianie maszynowe bez współdzielonych haseł. Nie obejmuje natomiast m.in. ciągłej oceny ryzyka sesji na podstawie kontekstu, segmentacji sieci ani centralnego monitorowania zdarzeń bezpieczeństwa [ŹRÓDŁO? NIST SP 800-207 — lista składników architektury Zero Trust].

Bramka bezpieczeństwa (ang. _security gate_) oznacza w pracy zautomatyzowany krok potoku CI/CD. Negatywny wynik tego kroku oznacza niepowodzenie walidacji zgłoszenia zmiany do scalenia z gałęzią główną (ang. _pull request_, PR).

Problem ma dwa wymiary, które w pracy traktuje się łącznie. Wymiar projektowy dotyczy mechanizmów platformy (domyślnej widoczności rekordów, zestawów uprawnień, egzekwowania uprawnień do obiektów i pól w kodzie) oraz bezpieczeństwa integracji z systemem zewnętrznym. Wymiar procesowy dotyczy potoku, który ma te same zasady wymuszać przy każdej zmianie.

## 1.3. Cel pracy, cele szczegółowe i pytania badawcze

**Celem głównym pracy** jest zaprojektowanie i zaimplementowanie systemu do zarządzania polisami i szkodami ubezpieczeniowymi na platformie Salesforce, wytwarzanego zgodnie z metodyką DevSecOps. Częścią celu jest empiryczna ocena skuteczności zastosowanych automatycznych bramek bezpieczeństwa oraz zaprojektowanego modelu dostępu. Cel ten rozwija sformułowanie z [RAPORT.md, rozdz. 2](../RAPORT.md#2-temat-pracy) o element pomiarowy opisany w [HARMONOGRAM.md, pkt 4](../HARMONOGRAM.md#4-część-badawcza-żeby-praca-nie-była-tylko-zbudowałem-aplikację).

**Cele szczegółowe:**

1. Przegląd literatury dotyczącej bezpieczeństwa chmurowych systemów CRM, modelu zerowego zaufania w Salesforce oraz praktyk DevSecOps (rozdziały 2–4).
2. Specyfikacja wymagań funkcjonalnych i niefunkcjonalnych systemu z macierzą śledzenia do zadań i literatury ([WYMAGANIA.md](../WYMAGANIA.md), wersja 0.1 z 18.10.2026: 35 wymagań funkcjonalnych i 35 niefunkcjonalnych).
3. Budowa potoku CI/CD walidującego każdy PR. Potok uruchamia testy, statyczną analizę kodu, skanowanie sekretów i analizę podatnych zależności. Dla każdego PR zmieniającego metadane Salesforce tworzy dodatkowo efemeryczne środowisko, wdraża do niego zmiany i egzekwuje próg pokrycia kodu testami 75%. Cel obejmuje wymagania FR-CI-01 – FR-CI-07 i FR-CI-09; wdrożenie po scaleniu (FR-CI-08) jest planowane w zadaniu #24.
4. Zaprojektowanie modelu danych i modelu uprawnień zgodnego z zasadą najmniejszych uprawnień (NFR-SEC-01 – NFR-SEC-04) oraz portalu klienta z dostępem ograniczonym do danych własnego konta (NFR-SEC-07) — planowane w etapach M2–M3.
5. Integracja z zewnętrznym serwerem w języku Python: bezpieczne ładowanie danych historycznych (FR-MIG-01 – FR-MIG-04) oraz prezentacja danych wrażliwych bez ich przechowywania w CRM (FR-EXT-01 – FR-EXT-03, NFR-SEC-06, NFR-SEC-08, NFR-CMP-01) — planowane w etapach M4–M5.
6. Przeprowadzenie eksperymentu oceniającego bramki potoku na zbiorze celowo wprowadzonych podatności i wad oraz weryfikacja modelu dostępu — planowane w etapie M6.

**Pytania badawcze (propozycja do uzgodnienia z promotorem):**

- **PB1.** Jaka część celowo wprowadzonych podatności i wad typowych dla aplikacji Salesforce zostaje wykryta przez poszczególne bramki potoku i ile fałszywych alarmów one generują? Planowane kategorie to:
  - podatności: wstrzyknięcie zapytania w języku SOQL (ang. _Salesforce Object Query Language_), brak kontroli uprawnień do operacji na obiektach (ang. _Create, Read, Update, Delete_, CRUD) i do pól (ang. _Field-Level Security_, FLS), `without sharing`, zaszyty sekret, podatna zależność, wstrzyknięcie skryptu (ang. _cross-site scripting_, XSS) w komponencie LWC;
  - wady wydajnościowe: zapytanie SOQL w pętli (wymaganie NFR-PERF-02).

  Miary to liczba wyników prawdziwie pozytywnych (TP), fałszywie negatywnych (FN) i fałszywie pozytywnych (FP) dla każdej bramki. Do pomiaru FP proponuje się grupę kontrolną zmian poprawnych, zgłaszanych tak samo jak zmiany podatne.

- **PB2.** Na którym etapie podatność zostaje wykryta: lokalnie przed zatwierdzeniem zmiany, przez skrypty uruchamiane automatycznie przez system Git (ang. _Git hooks_), w potoku PR, czy wcale?
- **PB3.** Jaki jest koszt czasowy pełnej walidacji PR w ograniczeniach środowiska Developer Edition? Czy mediana czasu walidacji mieści się w założonym limicie 20 minut (NFR-PERF-01)?
- **PB4.** Czy zaprojektowany model uprawnień spełnia wymagania NFR-SEC-01 – NFR-SEC-04 i NFR-SEC-07? Weryfikacja obejmuje negatywne testy Apex wykonywane w kontekście konkretnych użytkowników (`System.runAs`), czyli próby odczytu i modyfikacji cudzych rekordów. Obejmuje też manualny test penetracyjny portalu klienta.

Pytania PB1–PB3 dotyczą wymiaru procesowego problemu (podrozdz. 1.2), a PB4 — wymiaru projektowego. Katalog kategorii, liczba zmian (ok. 20–30) i mierzone wielkości pochodzą z planu eksperymentu w [HARMONOGRAM.md, pkt 4](../HARMONOGRAM.md#4-część-badawcza-żeby-praca-nie-była-tylko-zbudowałem-aplikację). Grupa kontrolna zmian poprawnych i pytanie PB4 rozszerzają ten plan. Sposoby weryfikacji w PB4 pochodzą z kolumny „Weryfikacja” w [WYMAGANIA.md](../WYMAGANIA.md). Projekt eksperymentu nawiązuje do oceny bramek jakości u Bavadiyi (2022) i do analizy błędów narzędzi statycznej analizy (IEEE/ACM, 2022).

Eksperyment obciąża istotne zagrożenie dla trafności wyników. Ta sama osoba dobiera reguły bramek i przygotowuje podatne zmiany, a zestaw reguł był już korygowany po zaobserwowaniu przeoczeń (dziennik M1, wpis #18). Grozi to rozumowaniem kołowym: bramki mogą wykrywać głównie te podatności, pod które je dostrojono. Zagrożenie to i sposoby jego ograniczenia są omówione w rozdziale 7 (zagrożenia dla trafności).

## 1.4. Zakres pracy i ograniczenia

### 1.4.1. Zakres

System składa się z trzech warstw opisanych w [RAPORT.md, rozdz. 2](../RAPORT.md#2-temat-pracy) i rozwijanych w jednym repozytorium ([ADR 0001](../adr/0001-monorepo.md)):

- **Warstwa CRM i portal klienta.** Obejmuje model danych polis, zakresów ochrony, szkód i dokumentów szkód na platformie Salesforce. Obejmuje też portal ubezpieczonego zbudowany w Experience Cloud, czyli usłudze Salesforce do budowy portali dla użytkowników zewnętrznych. W portalu ubezpieczony przegląda własne polisy, zgłasza szkody i komunikuje się z agentem (FR-POL, FR-CLM, FR-PRT, FR-COM).
- **Potok CI/CD.** Potok działa w GitHub Actions z Salesforce CLI. Uwierzytelnia się do Dev Hubu, czyli organizacji Salesforce uprawnionej do tworzenia środowisk tymczasowych, przepływem JWT Bearer ([ADR 0003](../adr/0003-jwt-bearer-ci-auth.md)). Przepływ ten wykorzystuje podpisany token JSON Web Token (JWT) w miejsce hasła. Dla każdego PR zmieniającego metadane Salesforce potok tworzy efemeryczną organizację testową (ang. _scratch org_) i usuwa ją po walidacji (dziennik M1, wpis #16). Scratch org to tymczasowe środowisko Salesforce konfigurowane plikiem definicji (SF DX Guide); szczegóły w rozdziale 4.
- **Serwer integracyjny w języku Python.** Serwer ładuje dane historyczne przez interfejs programistyczny (ang. _Application Programming Interface_, API) Bulk API 2.0 (FR-MIG-01 – FR-MIG-04). Udostępnia też dane wrażliwe w protokole OData 4.0 (ang. _Open Data Protocol_). Salesforce prezentuje je jako obiekty zewnętrzne (ang. _External Objects_), czyli bez kopiowania ich do CRM (FR-EXT-01 – FR-EXT-03, NFR-CMP-01). Dostępność tego mechanizmu w środowisku projektu potwierdzono w krótkim eksperymencie rozpoznawczym (ang. _spike_) w zadaniu #9 ([notatka](../spikes/salesforce-connect-odata.md)).

Kolejność etapów jest podporządkowana zasadzie shift-left. Potok z bramkami bezpieczeństwa powstaje (etap M1) przed logiką biznesową (etapy M2–M5), aby cały kod aplikacji od początku przechodził przez bramki ([HARMONOGRAM.md, „Założenia”](../HARMONOGRAM.md#założenia)).

### 1.4.2. Poza zakresem

Zgodnie z [WYMAGANIA.md, rozdz. 4](../WYMAGANIA.md#4-poza-zakresem-w) poza zakresem pracy pozostają: rozliczenia finansowe i integracja z systemem płatności, kalkulacja składki, natywna aplikacja mobilna oraz Financial Services Cloud.

### 1.4.3. Ograniczenia

- **Brak Financial Services Cloud.** Salesforce oferuje branżowy model danych ubezpieczeniowych w ramach Financial Services Cloud [ŹRÓDŁO? dokumentacja Salesforce: Financial Services Cloud — Insurance data model]. Model ten wymaga licencji niedostępnej w Developer Edition i w scratch orgach tworzonych z Dev Hubu projektu. Dlatego zaprojektowano własne obiekty (`Policy__c`, `Coverage__c`, `Claim__c`, `Claim_Document__c`), nazwane i powiązane analogicznie do modelu branżowego ([ADR 0002](../adr/0002-custom-objects-vs-fsc.md)). Wyniki pracy nie obejmują więc funkcji i automatyzacji dostarczanych przez produkt branżowy.
- **Limity Developer Edition.** Dev Hub działa na organizacji Developer Edition, w której obowiązuje limit 3 aktywnych i 6 nowych scratch orgów w ciągu doby [ŹRÓDŁO? dokumentacja Salesforce: Scratch Org Allocations for Salesforce Editions]. Wpływa to na konstrukcję potoku: filtr ścieżek i globalną kolejkę zadań tworzących scratch org (dziennik M1, wpis #16; [ADR 0001](../adr/0001-monorepo.md)). Ogranicza też liczbę przebiegów możliwych do wykonania w eksperymencie (NFR-PERF-05).
- **Jeden autor i projekt dyplomowy.** System jest rozwijany przez jedną osobę, bez rzeczywistych użytkowników i wyłącznie na danych syntetycznych (NFR-CMP-02). Wnioski dotyczące procesu, np. przeglądów kodu i czynnika ludzkiego opisywanego przez Jammeha (2020), mają więc ograniczoną możliwość uogólnienia na zespoły.
- **Egzekwowanie bramek.** Na dzień 2026-11-02 reguły ochrony gałęzi `main` wymagające pomyślnego wyniku kontroli nie są włączone (zadania #6 i #25). Bramki oznaczają PR jako niepoprawny, ale nie blokują jeszcze technicznie scalenia.
- **Narzędzia komercyjne nieporównywane eksperymentalnie.** Wybór GitHub Actions zamiast wyspecjalizowanej platformy Copado uzasadniono analizą dokumentacji i modelu licencyjnego, bez wdrożenia Copado (zadanie #27). Porównanie ma charakter jakościowy.
- **Zakres modelu zerowego zaufania.** Praca realizuje model zerowego zaufania wyłącznie w zakresie autoryzacji dostępu do danych i uwierzytelniania maszynowego (podrozdz. 1.2).

## 1.5. Metoda i przebieg prac

Praca łączy trzy metody:

1. **Analizę literatury.** Obejmuje przegląd publikacji naukowych i branżowych zebranych w [RAPORT.md](../RAPORT.md). Jest on uzupełniany o dokumentację techniczną platformy Salesforce i ramy oceny bezpieczeństwa, np. OWASP [ŹRÓDŁO? OWASP Top 10 / OWASP SAMM — do dodania do bibliografii, zgodnie z uwagą w HARMONOGRAM.md, pkt 3].
2. **Projekt i implementację** (ang. _design and implementation_). Prace zaplanowano w dziewięciu etapach (M0–M8), z czego M0–M6 obejmują wytwarzanie systemu. Prace rozpoczęto 12.10.2026, a zamrożenie kodu przewidziano na 15.06.2027 ([HARMONOGRAM.md, pkt 2](../HARMONOGRAM.md#2-harmonogram-start-12102026-kod-zamrożony-15062027-oddanie-ix-2027)). Każda decyzja architektoniczna lub wybór narzędzia jest zapisywana jako rekord decyzji architektonicznej (ang. _Architecture Decision Record_, ADR) w katalogu `docs/adr/`. Rekord zawiera kontekst, rozważane opcje, decyzję i konsekwencje. Każde zakończone zadanie jest opisywane wpisem w dzienniku implementacji `docs/implementacja/`, z sekcjami „Decyzje i alternatywy”, „Problemy” i „Dowody” ([KONWENCJE.md, pkt 3](../KONWENCJE.md#3-definition-of-done-każde-zadanie)). Dzięki temu rozumowanie prowadzące do rozwiązań (problem → opcje → decyzja → dowód) jest w większości przypadków dokumentowane na bieżąco, a nie odtwarzane po fakcie.
3. **Eksperyment.** Obejmuje pomiar skuteczności bramek na zbiorze celowo podatnych zmian oraz grupie kontrolnej zmian poprawnych, zgłaszanych jako osobne PR. Obejmuje też weryfikację modelu dostępu (podrozdz. 1.3, PB1–PB4; etap M6). Wyniki są gromadzone w `docs/experiment/`.

Przebiegi potoku CI/CD są powoływane w tekście numerem przebiegu GitHub Actions. Logi przebiegów są jednak przechowywane przez ograniczony czas, domyślnie 90 dni [ŹRÓDŁO? dokumentacja GitHub: okres przechowywania logów i artefaktów GitHub Actions]. Dlatego kluczowe wyniki są przepisywane do dziennika implementacji, a wyniki eksperymentu archiwizowane w `docs/experiment/`.

## 1.6. Wkład własny

Wkład własny autora obejmuje:

- specyfikację wymagań systemu ubezpieczeniowego z macierzą śledzenia wymagań do zadań i literatury;
- projekt i implementację potoku DevSecOps dla platformy Salesforce w ograniczeniach Developer Edition. Elementy autorskie to m.in. bramka pokrycia licząca wyłącznie klasy z repozytorium (dziennik M1, wpis #17), rozszerzenie zestawu reguł analizy statycznej o reguły wynikające z wymagań bezpieczeństwa ([ADR 0004](../adr/0004-code-analyzer-rules.md)) oraz samosprawdzenie skanera sekretów sztucznym sekretem generowanym w trakcie przebiegu (dziennik M1, wpis #19);
- projekt modelu danych i modelu uprawnień dla domeny ubezpieczeniowej bez Financial Services Cloud (planowane, etapy M2–M3);
- projekt i przeprowadzenie eksperymentu oceniającego bramki oraz model dostępu (planowane, etap M6);
- udokumentowanie decyzji projektowych wraz z rozważanymi alternatywami w formie rekordów ADR.

## 1.7. Struktura pracy

Roboczy układ pracy przedstawiono w tabeli 1.1.

**Tabela 1.1.** Roboczy układ rozdziałów pracy (do zatwierdzenia z promotorem, issue #12)

| Rozdział | Tytuł roboczy                                                                 | Zawartość                                                                                                                                                | Zadanie |
| -------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| 1        | Wstęp                                                                         | motywacja, problem, cel, pytania badawcze, zakres, metoda, wkład własny                                                                                  | #81     |
| 2        | Bezpieczeństwo chmurowych systemów CRM i model zerowego zaufania w Salesforce | wielodostępność, model współodpowiedzialności, Zero Trust (Al Kalach, 2025), mechanizmy bezpieczeństwa platformy (widoczność rekordów, uprawnienia, FLS) | #82     |
| 3        | DevSecOps i CI/CD                                                             | shift-left, SAST, zarządzanie sekretami, łańcuch dostaw; Bavadiya (2022), Cheenepalli i in. (2025), IEEE SLR (2025), Jammeh (2020), Lakade (2025) i in.  | #83     |
| 4        | Środowiska efemeryczne i bezpieczeństwo integracji                            | scratch orgi (Guduru, 2023; SF DX Guide), JWT i OAuth 2.0 (Machapatri, 2020), obiekty zewnętrzne i rezydencja danych                                     | #84     |
| 5        | Wymagania i projekt systemu                                                   | wymagania, decyzje architektoniczne (ADR), model danych, model uprawnień, architektura potoku                                                            | #85     |
| 6        | Implementacja                                                                 | realizacja etapów M0–M6 na podstawie dziennika implementacji                                                                                             | #86     |
| 7        | Wyniki eksperymentu i dyskusja                                                | metodyka, wyniki, zagrożenia dla trafności, porównanie z literaturą                                                                                      | #87     |
| 8        | Podsumowanie i wnioski                                                        | ocena realizacji celów, ograniczenia, kierunki dalszych prac                                                                                             | #88     |

Źródło: opracowanie własne na podstawie [BACKLOG.md](../BACKLOG.md) (zadania #81–#88) i [HARMONOGRAM.md, pkt 3](../HARMONOGRAM.md#3-literatura-z-raportu-gdzie-ją-wykorzystać).

Rozdziały 2–4 stanowią część teoretyczną i przygotowują pojęcia wykorzystywane w części projektowej. Rozdział 5 przekłada wymagania i decyzje architektoniczne na projekt systemu, a rozdział 6 opisuje jego realizację. Rozdział 7 odpowiada na pytania badawcze PB1–PB4 i omawia zagrożenia dla trafności wyników. Rozdział 8 zestawia cele pracy z uzyskanymi wynikami. Streszczenia, słowa kluczowe i bibliografia są przedmiotem zadania #89.

---

## Materiał roboczy (do usunięcia przed redakcją końcową)

### Uwagi redakcyjne

- **Numeracja rozdziałów teoretycznych.** [HARMONOGRAM.md, pkt 2](../HARMONOGRAM.md#2-harmonogram-start-12102026-kod-zamrożony-15062027-oddanie-ix-2027) mówi o „rozdziałach teoretycznych (1–3)”, licząc bez wstępu. W tabeli 1.1 wstęp ma numer 1, więc te same trzy rozdziały teoretyczne (#82–#84) mają numery 2–4.
- **Bibliografia.** Plik `docs/praca/bibliografia.md` (przygotowywany przez agenta `literature-researcher`) jeszcze nie istnieje. Do tego czasu odwołania (Autor, rok) wskazują na RAPORT.md.
- **Odwołania do repozytorium.** Odwołania do ADR, zadań, wpisów dziennika i numerów przebiegów zostaną w tekście końcowym przeniesione do przypisów lub do załącznika.
- **Linki po scaleniu #115.** Ograniczenia „Egzekwowanie bramek” i „Narzędzia komercyjne” odwołują się do zadań #6, #25 i #27. Po scaleniu PR #115 można dodać odsyłacze do [ADR 0008](../adr/0008-github-actions-vs-copado.md) i do opisu potoku `docs/architektura/potok-cicd.md` (wraz z rysunkiem potoku) oraz do wpisu #27 dziennika M1.
- **Al Kalach (2025), Bavadiya (2022).** Szczegóły tych źródeł (status recenzji, liczby z badania Bavadiyi) nie są we wstępie rozwijane do czasu weryfikacji oryginałów — patrz pytanie otwarte 4.

### Luki źródłowe `[ŹRÓDŁO?]`

1. Definicja SaaS / chmury obliczeniowej (np. NIST SP 800-145) i dane o upowszechnieniu CRM w modelu SaaS — podrozdz. 1.1.
2. Oficjalny opis architektury multi-tenant Salesforce — podrozdz. 1.1.
3. Charakterystyka danych przetwarzanych przez ubezpieczycieli, w tym dane szczególnych kategorii (RODO, art. 9) — podrozdz. 1.1.
4. Regulacje: RODO (Rozporządzenie (UE) 2016/679); ewentualnie DORA (Rozporządzenie (UE) 2022/2554) — do decyzji, czy powoływać — podrozdz. 1.1.
5. Dokumentacja Salesforce: Apex Developer Guide, LWC Developer Guide (definicje Apex, LWC; także SOQL, DML, CRUD/FLS) — podrozdz. 1.1 i 1.3.
6. Definicja DevSecOps z publikacji przeglądowej lub standardu (np. NIST SP 800-204C) — podrozdz. 1.1.
7. Definicja SAST (np. OWASP) — podrozdz. 1.1.
8. Definicja zasady najmniejszych uprawnień (np. NIST SP 800-53, AC-6) — podrozdz. 1.2.
9. Definicja Zero Trust Architecture (NIST SP 800-207) — podrozdz. 1.2.
10. NIST SP 800-207 — składniki architektury Zero Trust (do rozróżnienia elementów objętych i nieobjętych pracą) — podrozdz. 1.2.
11. Dokumentacja Salesforce: Financial Services Cloud — model danych ubezpieczeniowych — podrozdz. 1.4.3.
12. Dokumentacja Salesforce: limity scratch orgów dla edycji (Scratch Org Allocations) — podrozdz. 1.4.3.
13. OWASP Top 10 / OWASP SAMM jako rama oceny — podrozdz. 1.5.
14. Dokumentacja GitHub: okres przechowywania logów i artefaktów GitHub Actions (90 dni domyślnie) — podrozdz. 1.5.

Dodatkowo dla źródeł już obecnych w [RAPORT.md](../RAPORT.md) brakuje danych potrzebnych do pełnego opisu bibliograficznego. Brakuje autorów publikacji „IEEE SLR (2025)” i „Shift Left Security (2025)” (w raporcie opisanych jako „Publikacja IEEE” i „Praca zbiorowa”), autorów pracy „Find Bugs in Static Bug Finders” (IEEE/ACM, 2022), numerów stron dla przytaczanych tez oraz DOI. Tezy przytoczone w podrozdz. 1.1 są parafrazami cytatów z RAPORT.md i wymagają sprawdzenia z oryginałami. Dotyczy to też opisu próby u Cheenepalli i in. (2025): 405 specjalistów, MŚP.

### Pytania otwarte do promotora

1. Czy roboczy układ ośmiu rozdziałów (tabela 1.1) odpowiada oczekiwaniom, czy rozdziały 2–4 połączyć w jeden rozdział teoretyczny?
2. Czy pytania badawcze PB1–PB4 mają pozostać pytaniami, czy należy sformułować tezę lub hipotezy (np. o odsetku podatności wykrywanych w PR)?
3. Czy do motywacji powoływać regulacje sektorowe (DORA, wytyczne nadzoru), skoro system nie jest wdrażany w rzeczywistym zakładzie ubezpieczeń?
4. Czy źródło Al Kalach (2025), dostępne w serwisie Scribd, jest akceptowalne jako pozycja naukowa, czy należy je zastąpić publikacją recenzowaną lub dokumentacją Salesforce (Security Implementation Guide)? Czy wyniki liczbowe Bavadiyi (2022) można przytaczać po weryfikacji oryginału?
5. Czy we wstępie przywoływać wczesne obserwacje z budowy potoku (dziennik M1, wpisy #17 i #18), czy przenieść je w całości do rozdziałów 6–7?
6. Jaki styl cytowania (autor–rok czy numeryczny) wymaga uczelnia?
7. Czy rozszerzenie planu eksperymentu o grupę kontrolną zmian poprawnych i o PB4 (model dostępu) jest akceptowalne w zakresie czasowym etapu M6 (01.06–15.06.2027)?

### Wykorzystane fakty z repozytorium

- [RAPORT.md](../RAPORT.md), rozdz. 1–3: temat, cel, zakres technologiczny, tezy Al Kalach (2025), Guduru (2023), Shift Left Security (2025), Bavadiya (2022), Cheenepalli i in. (2025: próba 405 specjalistów, MŚP, 73%, 12%), IEEE SLR (2025), Jammeh (2020), IEEE/ACM (2022: 46 błędów).
- [HARMONOGRAM.md](../HARMONOGRAM.md): zasada shift-left w kolejności etapów, etapy M0–M8, daty 12.10.2026 i 15.06.2027, plan eksperymentu (20–30 zmian, kategorie, TP/FN/FP, czas potoku), uwaga o OWASP, „rozdziały teoretyczne (1–3)”.
- [WYMAGANIA.md](../WYMAGANIA.md), wersja 0.1 z 18.10.2026: grupy FR-POL, FR-CLM, FR-PRT, FR-COM, FR-MIG-01–04, FR-EXT-01–03, FR-CI-01–09 (35 wymagań funkcjonalnych), NFR (35 wymagań niefunkcjonalnych, w tym NFR-SEC-01–04, 06, 07, 08, NFR-CMP-01, 02, NFR-PERF-01, 02, 05), kolumna „Weryfikacja” (NFR-SEC-07: test penetracyjny manualny + `runAs`), rozdz. 4 „Poza zakresem”.
- [ADR 0001](../adr/0001-monorepo.md) (monorepo), [ADR 0002](../adr/0002-custom-objects-vs-fsc.md) (brak FSC), [ADR 0003](../adr/0003-jwt-bearer-ci-auth.md) (JWT Bearer), [ADR 0004](../adr/0004-code-analyzer-rules.md) (`ApexSharingViolations` dołączona do `Recommended`, reguła własna `ApexNoWithoutSharing`).
- [Spike #9](../spikes/salesforce-connect-odata.md): Salesforce Connect OData 4.0 dostępny w DE i scratch orgu.
- Dziennik M1 (`docs/implementacja/M1-potok-devsecops.md`): wpis #16 (scratch org dla PR zmieniających metadane, filtr `paths:`, concurrency), #17 (`RunLocalTests`, pokrycie 40% vs 82,14%, przebiegi 41360184741 i 41360432846), #18 (`Recommended` nie wykrył `without sharing`), #19 (kanarek gitleaks).
- [BACKLOG.md](../BACKLOG.md) i zadania GitHub: #12, #81–#89 (struktura rozdziałów), #6 i #25 (ochrona gałęzi), #24 (deploy, FR-CI-08), #27 (ADR GitHub Actions vs Copado).
