# Konwencje pracy i dokumentowania

Cel: każde zadanie zostawia po sobie **kod + dokumentację**, a dokumentacja jest gotowym materiałem do rozdziałów implementacyjnych pracy. Śledzenie postępu odbywa się w GitHub Project _insurance-app — Master's thesis_.

**Języki:** issues, PR-y, commity, kod i szablony GitHub — **angielski**. Dokumenty w `docs/` (wymagania, ADR, opisy implementacji, eksperyment) — **polski**.

---

## 1. Struktura zadań

```
Milestone  = etap harmonogramu (M0 … M8, z datą końcową)
└─ Epic    = issue `type:epic`, jeden na etap; zadania podpięte jako sub-issues
   └─ Task = issue 0,5–3 dni pracy (feature / chore / spike / docs / research / thesis)
```

| Milestone | Etap                                 | Termin     |
| --------- | ------------------------------------ | ---------- |
| M0        | Foundation                           | 25.10.2026 |
| M1        | DevSecOps pipeline                   | 06.12.2026 |
| M2        | Data model & security                | 31.01.2027 |
| M3        | Experience Cloud portal              | 14.03.2027 |
| M4        | Python backend — data loading        | 25.04.2027 |
| M5        | External Objects                     | 31.05.2027 |
| M6        | Experiment & hardening (code freeze) | 15.06.2027 |
| M7        | Thesis writing                       | 31.08.2027 |
| M8        | Defense                              | 30.09.2027 |

Zadania pisarskie (`type:thesis`) z rozdziałów teoretycznych są w M7, ale mają daty startu od listopada 2026 — piszemy równolegle.

### Etykiety

| Grupa       | Wartości                                                                                                |
| ----------- | ------------------------------------------------------------------------------------------------------- |
| `type:`     | `epic`, `feature`, `chore`, `spike`, `docs`, `research`, `thesis`                                       |
| `area:`     | `ci`, `security`, `data-model`, `portal`, `backend`, `external-objects`, `experiment`, `thesis`, `repo` |
| `priority:` | `P1` (blokuje etap), `P2` (ważne), `P3` (miłe do posiadania)                                            |
| `size:`     | `S` (≤ 0,5 dnia), `M` (1–2 dni), `L` (3 dni; większe dzielimy)                                          |

### Pola w GitHub Project

`Status` (Todo / In progress / In review / Done), `Stage` (M0–M8), `Work type`, `Priority`, `Size`, `Start date`, `Target date`. Pole `Work type` ma inną nazwę niż etykieta `type:`, bo GitHub rezerwuje nazwę `Type` dla typów issues.

---

## 2. Cykl życia zadania

1. **Todo → In progress**: przypisz się, utwórz gałąź od `main`:
   - `feat/<nr>-krotki-opis`, `fix/<nr>-…`, `chore/<nr>-…`, `docs/<nr>-…`, `spike/<nr>-…`.
2. **Commity**: [Conventional Commits](https://www.conventionalcommits.org/) po angielsku, z numerem issue:
   `feat(claims): add claim status transition guard (#42)`.
   Typy: `feat`, `fix`, `chore`, `docs`, `test`, `ci`, `refactor`, `build`, `security`.
3. **PR → In review**: szablon PR, w opisie `Closes #<nr>`. Wszystkie checki zielone.
4. **Merge → Done**: squash merge; issue zamyka się automatycznie.

---

## 3. Definition of Done (każde zadanie)

- [ ] Kryteria akceptacji z issue spełnione.
- [ ] Testy dodane/zaktualizowane; potok CI zielony (bramki: pokrycie, Code Analyzer, gitleaks, CodeQL).
- [ ] **Wpis implementacyjny** w `docs/implementacja/<etap>.md` (szablon niżej).
- [ ] **ADR** w `docs/adr/`, jeśli zapadła decyzja architektoniczna lub wybór narzędzia.
- [ ] Spike → notatka w `docs/spikes/` z wnioskiem (go / no-go / obejście).
- [ ] README / runbook zaktualizowany, jeśli zmienia się sposób uruchamiania.
- [ ] Jeśli zadanie realizuje wymaganie — ID wymagania podane w issue (macierz w [WYMAGANIA.md](WYMAGANIA.md)).

### Szablon wpisu implementacyjnego

Plik: `docs/implementacja/M<n>-<nazwa>.md`, jedna sekcja na zadanie:

```markdown
### #<nr> <tytuł issue>

- **Data:** RRRR-MM-DD · **PR:** #<nr> · **Wymagania:** FR-…, NFR-…
- **Co zrobiono:** 2–4 zdania.
- **Jak:** kluczowe pliki, komendy, konfiguracja (fragmenty kodu tylko istotne).
- **Decyzje i alternatywy:** dlaczego tak; link do ADR.
- **Problemy:** co nie działało i jak to obejście.
- **Dowody:** zrzut ekranu / link do przebiegu CI / wynik testu.
- **Do pracy:** w którym rozdziale wykorzystać, powiązana literatura.
```

Sekcje „Decyzje”, „Problemy” i „Do pracy” są najcenniejsze przy pisaniu — nie pomijać.

---

## 4. Dokumentacja — gdzie co trzymamy

| Ścieżka               | Zawartość                                                                   |
| --------------------- | --------------------------------------------------------------------------- |
| `docs/WYMAGANIA.md`   | Wymagania FR/NFR + macierz śledzenia                                        |
| `docs/BACKLOG.md`     | Lista epików i zadań z numerami issues (generowana skryptem)                |
| `docs/HARMONOGRAM.md` | Etapy, stos technologiczny, plan eksperymentu                               |
| `docs/adr/`           | Architecture Decision Records (`NNNN-tytul.md`, szablon `0000-template.md`) |
| `docs/implementacja/` | Dziennik implementacji per etap — materiał do rozdziałów implementacyjnych  |
| `docs/spikes/`        | Wyniki spike'ów                                                             |
| `docs/experiment/`    | Katalog podatnych zmian, surowe wyniki, analiza                             |
| `docs/architektura/`  | Diagramy (ERD, przepływy, potok CI/CD) — Mermaid lub PlantUML               |

---

## 5. Backlog jako kod

Źródłem backlogu jest [`scripts/github/backlog.json`](../scripts/github/backlog.json). Skrypt [`scripts/github/create-backlog.mjs`](../scripts/github/create-backlog.mjs) tworzy na GitHubie etykiety, milestones, epiki, zadania (jako sub-issues), Project v2 z polami oraz generuje `docs/BACKLOG.md` i macierz śledzenia.

```bash
winget install --id GitHub.cli
gh auth login --scopes "project,repo"
node scripts/github/create-backlog.mjs --dry-run
node scripts/github/create-backlog.mjs
```

Skrypt jest idempotentny (dopasowuje po tytule), więc nowe zadania można dopisać do `backlog.json` i uruchomić go ponownie. Po utworzeniu zadań źródłem prawdy o **statusie** jest GitHub; drobne zadania można dodawać bezpośrednio z szablonu issue.

### Widoki w Project (jednorazowo, ręcznie)

`gh` nie tworzy widoków, więc po pierwszym uruchomieniu w przeglądarce:

0. **Status** — w ustawieniach pola `Status` dodaj opcję `In review` między `In Progress` a `Done`.
1. **Board** — layout Board, grupowanie po `Status`, filtr `-type:epic`.
2. **Roadmap** — layout Roadmap, daty `Start date` → `Target date`, grupowanie po `Stage`.
3. **By stage** — layout Table, grupowanie po `Stage`, sortowanie po `Priority`.
4. **Thesis** — Table, filtr `label:type:thesis`.
5. Workflows projektu: włącz „Item closed → Done”, „Pull request merged → Done”, „Item added → Todo”.

---

## 6. Rytm

- Co 2 tygodnie: przegląd Roadmap, przesunięcie dat, krótka notatka w opisie epiku.
- Po zamknięciu etapu: podsumowanie w epiku (co zrobiono, co przeniesiono), uzupełniony plik `docs/implementacja/M<n>-*.md`, 1–2 strony szkicu rozdziału.
