# Etap 0 — Fundament

Wpisy dodawane po zamknięciu każdego zadania etapu (szablon: [KONWENCJE.md](../KONWENCJE.md#szablon-wpisu-implementacyjnego)).

<!-- Nowe wpisy poniżej, od najstarszego. -->

### #7 Create External Client App with JWT certificate for CI

- **Data:** 2026-10-28 · **PR:** #96 · **Wymagania:** NFR-SEC-05, NFR-SEC-06
- **Co zrobiono:** Wygenerowano samopodpisany certyfikat X.509 (RSA 2048, ważny do 2027-10-28) i utworzono w Dev Hubie External Client App `insurance-app-ci` z włączonym JWT Bearer Flow i pre-autoryzacją użytkowników. Klucz prywatny, client id i nazwę użytkownika zapisano jako sekrety GitHub Environment `devhub`. Opisano procedurę rotacji certyfikatu.
- **Jak:**
  - Klucz i certyfikat poza repozytorium, w `~/.sf-keys/insurance-app/`:
    `openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt -subj "//CN=insurance-app-ci"`.
  - External Client App: Distribution State _Local_; OAuth scopes `api`, `refresh_token offline_access`, `web`; Flow Enablement → _Enable JWT Bearer Flow_ z wgranym `server.crt`; Policies → _Admin approved users are pre-authorized_.
  - Sekrety: `gh secret set SF_JWT_KEY|SF_CLIENT_ID|SF_USERNAME --env devhub`.
  - Test lokalny: `sf org login jwt --client-id … --jwt-key-file ~/.sf-keys/insurance-app/server.key --username … --alias devhub-jwt`.
  - `.gitignore` uzupełniony o `*.key`, `*.pem`, `*.crt`, `*.p12`, `*.pfx`.
- **Decyzje i alternatywy:** JWT Bearer zamiast Client Credentials i SFDX auth URL — brak współdzielonego sekretu i długo żyjących tokenów, natywne wsparcie w `sf` CLI. Sekrety na poziomie środowiska, nie repozytorium, aby móc ograniczyć dostęp regułami środowiska. Szczegóły: [ADR 0003](../adr/0003-jwt-bearer-ci-auth.md). Rotacja: [runbook](../runbooki/rotacja-certyfikatu-jwt.md).
- **Problemy:** W Git Bashu `-subj "/CN=…"` jest zamieniany przez MSYS na ścieżkę Windows (`C:/Program Files/Git/CN=…`), a `\CN=…` odrzuca OpenSSL. Obejście: `//CN=…` albo `MSYS_NO_PATHCONV=1`.
- **Dowody:** <!-- zrzut konfiguracji External Client App (bez Consumer Key), wynik `sf org login jwt`, lista sekretów `gh secret list --env devhub` -->
- **Do pracy:** rozdział #84 (bezpieczeństwo integracji: JWT, OAuth) oraz #83 (zarządzanie sekretami w potoku); Machapatri (2020).

### #8 Spike: Experience Cloud LWR site in a scratch org

- **Data:** 2026-10-28 · **PR:** #97 · **Wymagania:** FR-PRT-01
- **Co zrobiono:** Rozszerzono definicję scratch orga o Experience Cloud, utworzono stronę „Insurance Portal” z szablonu Build Your Own (LWR), pobrano ją do źródeł i wdrożono do drugiego, czystego scratch orga, gdzie została opublikowana. Werdykt: GO z obejściami.
- **Jak:** `config/project-scratch-def.json` (feature `Communities`, `enableNetworksEnabled`, `enableExperienceBundleMetadata`); `sf community create … --template-name "Build Your Own (LWR)"`; `sf project retrieve start -m Network -m CustomSite -m DigitalExperienceConfig -m DigitalExperienceBundle -m NavigationMenu`; `replacements` w `sfdx-project.json` dla nazwy administratora strony.
- **Decyzje i alternatywy:** Strona trzymana jako metadane (DigitalExperienceBundle), a nie tworzona skryptem w każdym orgu — daje przegląd zmian w PR i powtarzalność. Wartości zależne od orga podstawiane przy deployu zamiast commitowania. `sourceApiVersion` → 68.0.
- **Problemy:** nazwa użytkownika scratch orga w `CustomSite`; prywatny e-mail w `Network`; błąd schematu `geoBotsAllowed` przy deployu w API 62.0. Szczegóły: [spike](../spikes/experience-cloud-lwr.md).
- **Dowody:** deploy `0AfO500000fvtMjKAI` do `spike-lwr-2`: Succeeded, 31/31 komponentów; `sf community publish` zakończony powodzeniem. <!-- zrzut opublikowanej strony -->
- **Do pracy:** rozdział #85/#86 (projekt i implementacja portalu), #84 (efemeryczne środowiska — infrastruktura jako kod także dla warstwy UI).

### #10 ADR-001 monorepo and ADR-002 custom objects instead of Financial Services Cloud

- **Data:** 2026-10-29 · **PR:** #<nr> · **Wymagania:** NFR-MNT-03
- **Co zrobiono:** Spisano dwie decyzje podjęte przy planowaniu: jedno repozytorium dla metadanych Salesforce, backendu Python i CI/CD oraz własny model danych zamiast obiektów Financial Services Cloud. Uzupełniono indeks ADR.
- **Jak:** [ADR 0001](../adr/0001-monorepo.md), [ADR 0002](../adr/0002-custom-objects-vs-fsc.md), indeks w `docs/adr/README.md`.
- **Decyzje i alternatywy:** monorepo vs osobne repozytoria vs Unlocked Packages; obiekty custom vs FSC vs obiekty standardowe (`Asset`/`Case`). Obiekty custom nazwane i powiązane analogicznie do FSC, aby ewentualna migracja była mapowaniem.
- **Problemy:** brak.
- **Dowody:** pliki ADR w repozytorium.
- **Do pracy:** rozdział #85 (wymagania i projekt systemu) — uzasadnienie architektury i modelu danych; ograniczenia zakresu (brak FSC) w podsumowaniu (#88).
