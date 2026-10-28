# Etap 0 — Fundament

Wpisy dodawane po zamknięciu każdego zadania etapu (szablon: [KONWENCJE.md](../KONWENCJE.md#szablon-wpisu-implementacyjnego)).

<!-- Nowe wpisy poniżej, od najstarszego. -->

### #7 Create External Client App with JWT certificate for CI

- **Data:** 2026-10-28 · **PR:** #<nr> · **Wymagania:** NFR-SEC-05, NFR-SEC-06
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
