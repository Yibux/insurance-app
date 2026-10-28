# 0001. Monorepo dla metadanych Salesforce, backendu Python i potoku CI/CD

- **Status:** przyjęta
- **Data:** 2026-10-29
- **Issue:** #10
- **Wymagania:** NFR-MNT-01, NFR-MNT-03

## Kontekst

System składa się z trzech części rozwijanych przez jedną osobę w ramach jednej pracy dyplomowej:

- metadanych Salesforce (`force-app/`: obiekty, Apex, LWC, strona Experience Cloud, permission sety),
- backendu Python (`integration-server/`: loader Bulk API 2.0, endpoint OData dla External Objects),
- potoku CI/CD (`.github/workflows/`) i dokumentacji (`docs/`), które dotyczą obu powyższych.

Części są ze sobą powiązane kontraktami: endpoint OData musi odpowiadać definicji External Data Source w metadanych, a loader — polom obiektów custom (External ID). Cała konfiguracja ma być kodem i być odtwarzalna z repozytorium (NFR-MNT-01). Eksperyment (M6) mierzy skuteczność bramek bezpieczeństwa na całym systemie.

## Rozważane opcje

1. **Monorepo** — jedno repozytorium z katalogami `force-app/`, `integration-server/`, `scripts/`, `.github/`, `docs/`.
   - Zalety: zmiana kontraktu (np. nowe pole obiektu + zmiana loadera) w jednym PR i jednym przeglądzie; jedna konfiguracja branch protection, CODEOWNERS, sekretów i Dependabota; wspólny backlog, macierz śledzenia wymagań i historia commitów jako dowód dla pracy; prostsze odtworzenie środowiska (jedno `git clone`).
   - Wady: workflowy muszą filtrować po ścieżkach (`paths:`), żeby zmiana w Pythonie nie tworzyła scratch orga i odwrotnie; repozytorium miesza dwa ekosystemy narzędzi (npm i pip).
2. **Osobne repozytoria** (Salesforce, backend, ewentualnie dokumentacja).
   - Zalety: niezależne cykle wydań, mniejsze i prostsze workflowy w każdym repo.
   - Wady: zmiany przekrojowe rozbite na kilka PR-ów, które trzeba scalać w odpowiedniej kolejności; zdublowana konfiguracja bezpieczeństwa (branch protection, sekrety, skanery) — więcej miejsc na pomyłkę; rozproszone dowody do eksperymentu. Przy jednym autorze niezależne wydania nie dają korzyści.
3. **Unlocked Packages z osobnymi katalogami pakietów** w repozytorium Salesforce — rozważane jako sposób podziału samych metadanych.
   - Na obecnym etapie nadmiarowe: aplikacja nie jest dystrybuowana do wielu orgów. Monorepo nie wyklucza dodania pakietów później (kolejne `packageDirectories` w `sfdx-project.json`).

## Decyzja

Wybrano **monorepo** (opcja 1). Struktura docelowa jest opisana w [HARMONOGRAM.md](../HARMONOGRAM.md#docelowa-struktura-monorepo). Workflowy GitHub Actions są rozdzielone per obszar (`pr-validation.yml` dla Salesforce, `python-ci.yml` dla backendu) i uruchamiane filtrami `paths:`, a wspólne bramki (gitleaks, CodeQL, Dependabot) obejmują całe repozytorium.

## Konsekwencje

- Każdy workflow musi deklarować `paths:` / `paths-ignore:`, aby nie zużywać dziennego limitu scratch orgów (6/dzień w DE) na zmiany niedotyczące Salesforce.
- Wymagane checki w branch protection muszą uwzględniać, że część workflowów nie uruchomi się dla danego PR (checki pomijane przez `paths:` traktowane są jako brakujące) — rozwiązanie w #25.
- CODEOWNERS i Dependabot konfigurowane per katalog (`/force-app`, `/integration-server`).
- Historia jednego repozytorium służy jako ślad audytowy wszystkich zmian w systemie, wykorzystywany w eksperymencie (M6) i rozdziale implementacyjnym.
