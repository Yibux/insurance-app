# Etap 7 — Redakcja pracy

Wpisy dla zadań pisarskich (`type:thesis`), pisanych równolegle z implementacją (szablon: [KONWENCJE.md](../KONWENCJE.md#szablon-wpisu-implementacyjnego)). Rozdziały pracy leżą w [`docs/praca/`](../praca/).

<!-- Nowe wpisy poniżej, od najstarszego. -->

### #81 Chapter: Introduction — motivation, goal, scope

- **Data:** 2026-11-02 · **PR:** #<nr> · **Wymagania:** —
- **Co zrobiono:** Napisano roboczą (prowizoryczną) wersję rozdziału 1 „Wstęp”: tło i motywacja, problem, cel główny i cele szczegółowe, propozycja pytań badawczych PB1–PB3, zakres i ograniczenia, metoda, roboczy układ pracy (tabela 1.1). Rozdział jest oznaczony jako prowizoryczny, bo konspekt nie został uzgodniony z promotorem (#12).
- **Jak:** [docs/praca/01-wstep.md](../praca/01-wstep.md); źródła: RAPORT.md rozdz. 1–3 (kryterium akceptacji issue), HARMONOGRAM.md (etapy, plan eksperymentu), WYMAGANIA.md, ADR 0001–0004, spike #9, dziennik M1 (#16, #17, #18, #27). Układ rozdziałów przyjęto według zadań #81–#88 z BACKLOG.md.
- **Decyzje i alternatywy:**
  - Pytania badawcze zamiast tezy — PB1–PB3 wynikają bezpośrednio z planu eksperymentu (TP/FN/FP, etap wykrycia, czas potoku); forma do decyzji promotora.
  - Wczesne obserwacje z budowy potoku (zawyżone pokrycie 82,14% przy klasie z 40%; `Recommended` nie wykrył `without sharing`) użyte jako motywacja części badawczej, w powiązaniu z IEEE/ACM (2022).
  - Cytowanie autor–rok wg RAPORT.md, bo `docs/praca/bibliografia.md` jeszcze nie istnieje; brakujące źródła oznaczone `[ŹRÓDŁO?]` (9 pozycji, lista na końcu rozdziału).
  - Bez linków do ADR 0008 i `docs/architektura/potok-cicd.md`, bo są w nie scalonym PR #115; fakty o niewłączonej ochronie gałęzi i nietestowanym Copado odwołują się do wpisu #27 dziennika M1.
- **Problemy:** Brak uzgodnionego konspektu (#12) i brak pliku bibliografii; część opisów źródeł w RAPORT.md nie ma autorów (IEEE SLR 2025, Shift Left Security 2025, IEEE/ACM 2022), numerów stron ani DOI. Kryterium „Draft based on RAPORT.md sections 1–2” spełnione, ale rozdział pozostaje prowizoryczny.
- **Dowody:** plik rozdziału w repozytorium; zmiany wyłącznie w `docs/`, scratch org nie był używany.
- **Do pracy:** rozdział 1 (#81); po uzgodnieniu konspektu (#12) zaktualizować tabelę 1.1 i podrozdz. 1.3; po uzupełnieniu bibliografii przez `literature-researcher` zastąpić `[ŹRÓDŁO?]`. Po merge'u #115 można dodać odsyłacze do ADR 0008 i opisu potoku.
