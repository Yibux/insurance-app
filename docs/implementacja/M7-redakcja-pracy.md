# Etap 7 — Redakcja pracy

Wpisy dla zadań pisarskich (`type:thesis`), pisanych równolegle z implementacją (szablon: [KONWENCJE.md](../KONWENCJE.md#szablon-wpisu-implementacyjnego)). Rozdziały pracy leżą w [`docs/praca/`](../praca/).

<!-- Nowe wpisy poniżej, od najstarszego. -->

### #81 Chapter: Introduction — motivation, goal, scope

- **Data:** 2026-11-02 · **PR:** #117 · **Wymagania:** —
- **Co zrobiono:** Napisano roboczą (prowizoryczną) wersję rozdziału 1 „Wstęp”: tło i motywacja, problem, cel główny i cele szczegółowe, propozycja pytań badawczych PB1–PB4, zakres i ograniczenia, metoda, wkład własny, roboczy układ pracy (tabela 1.1). Rozdział jest oznaczony jako prowizoryczny, bo konspekt nie został uzgodniony z promotorem (#12). Wersję poprawiono po przeglądzie `thesis-reviewer`.
- **Jak:** [docs/praca/01-wstep.md](../praca/01-wstep.md); źródła: RAPORT.md rozdz. 1–3 (kryterium akceptacji issue), HARMONOGRAM.md (etapy, plan eksperymentu), WYMAGANIA.md, ADR 0001–0004, spike #9, dziennik M1 (#16, #17, #18, #19), zadania #6, #24, #25, #27. Układ rozdziałów przyjęto według zadań #81–#88 z BACKLOG.md.
- **Decyzje i alternatywy:**
  - Pytania badawcze zamiast tezy: PB1–PB3 wynikają z planu eksperymentu (TP/FN/FP, etap wykrycia, czas potoku), PB4 dodano dla wymiaru projektowego (model uprawnień, testy `runAs` i test penetracyjny portalu); forma do decyzji promotora.
  - Plan eksperymentu rozszerzony propozycją grupy kontrolnej zmian poprawnych (pomiar FP); SOQL w pętli opisany jako wada wydajnościowa (NFR-PERF-02), nie podatność.
  - Wczesne obserwacje z budowy potoku przedstawione jako „podobne ryzyko” do opisanego w IEEE/ACM (2022), a nie jako błędy narzędzi: luka w konfiguracji domyślnej (#18) i wada w projekcie własnej bramki (#17). Wskazano zagrożenie rozumowaniem kołowym (autor dobiera reguły i pisze podatności) z odesłaniem do rozdziału 7.
  - Model zerowego zaufania zawężony do autoryzacji dostępu do danych i uwierzytelniania maszynowego.
  - Cytowanie autor–rok wg RAPORT.md, bo `docs/praca/bibliografia.md` jeszcze nie istnieje; brakujące źródła oznaczone `[ŹRÓDŁO?]` (14 pozycji, lista na końcu rozdziału).
  - Ograniczenia dotyczące ochrony gałęzi i Copado odwołują się do zadań #6, #25, #27, a nie do wpisu #27 dziennika M1 (ten jest w PR #115).
- **Problemy:** Brak uzgodnionego konspektu (#12) i brak pliku bibliografii; część opisów źródeł w RAPORT.md nie ma autorów (IEEE SLR 2025, Shift Left Security 2025, IEEE/ACM 2022), numerów stron ani DOI. Pierwsza wersja zawierała błędy wskazane w przeglądzie (liczba etapów, status M0, utożsamienie obserwacji z #17/#18 z błędami narzędzi SAST, odwołanie do nie scalonego wpisu #27) — poprawione. Kryterium „Draft based on RAPORT.md sections 1–2” spełnione, ale rozdział pozostaje prowizoryczny.
- **Dowody:** plik rozdziału w repozytorium; zmiany wyłącznie w `docs/`, scratch org nie był używany.
- **Do pracy:** rozdział 1 (#81); po uzgodnieniu konspektu (#12) zaktualizować tabelę 1.1 i podrozdz. 1.3; po uzupełnieniu bibliografii przez `literature-researcher` zastąpić `[ŹRÓDŁO?]`. Po merge'u #115 dodać odsyłacze do ADR 0008, opisu potoku i wpisu #27. Zagrożenie rozumowaniem kołowym rozwinąć w rozdziale 7 (#87).
