# 0003. Uwierzytelnianie CI w Dev Hubie przez JWT Bearer Flow

- **Status:** przyjęta
- **Data:** 2026-10-28
- **Issue:** #7
- **Wymagania:** NFR-SEC-05, NFR-SEC-06

## Kontekst

Potok GitHub Actions (M1) musi bez udziału człowieka logować się do Dev Hubu, żeby tworzyć scratch orgi per PR, wdrażać metadane i uruchamiać testy Apex. Poświadczenia nie mogą trafić do repozytorium (NFR-SEC-05), a CI nie może używać haseł użytkownika; sesje mają być krótkotrwałe (NFR-SEC-06). Narzędziem wykonawczym jest `sf` CLI.

## Rozważane opcje

1. **JWT Bearer Flow (External Client App + certyfikat X.509)** — CI podpisuje kluczem prywatnym krótko żyjącą asercję JWT, Salesforce weryfikuje ją certyfikatem publicznym i wydaje access token.
   - Zalety: klucz prywatny nie opuszcza runnera i nie jest przesyłany; w Salesforce leży tylko certyfikat publiczny, którego wyciek niczego nie daje; natywne wsparcie w CLI (`sf org login jwt`); brak refresh tokenów do przechowywania; certyfikat ma datę ważności, co wymusza rotację.
   - Wady: trzeba wygenerować certyfikat i pilnować jego rotacji; konfiguracja aplikacji jest dłuższa (pre-autoryzacja użytkowników).
2. **OAuth 2.0 Client Credentials Flow (client id + client secret)** — aplikacja wymienia sekret na token w imieniu przypisanego użytkownika „run as”.
   - Zalety: najprostsza konfiguracja, brak certyfikatu.
   - Wady: współdzielony sekret symetryczny przesyłany przy każdym żądaniu tokenu — kto go przechwyci, działa jako CI; brak dedykowanej komendy w `sf` CLI, więc token trzeba pobierać ręcznie (`curl`) i przekazywać przez `sf org login access-token`, łącznie z obsługą wygasania.
3. **SFDX auth URL (`sf org login sfdx-url`)** — w sekrecie przechowywany jest URL z refresh tokenem.
   - Zalety: jedna komenda, zero konfiguracji aplikacji.
   - Wady: długo żyjący refresh token powiązany z sesją użytkownika jest de facto hasłem; jego wyciek daje trwały dostęp do momentu ręcznego unieważnienia; sprzeczne z NFR-SEC-06.

## Decyzja

Wybrano **JWT Bearer Flow** z External Client App `insurance-app-ci` w Dev Hubie. Uwierzytelnianie asymetryczne eliminuje współdzielone sekrety i długo żyjące tokeny, co odpowiada modelowi Zero-Trust i rekomendacjom Machapatri (2020) dotyczącym zastąpienia uwierzytelniania opartego na hasłach bezstanowymi tokenami JWT w integracjach Salesforce. Ten sam mechanizm zostanie użyty w backendzie Python (#59), więc w systemie jest jeden wzorzec uwierzytelniania maszynowego.

Klucz prywatny, client id i nazwa użytkownika są przechowywane jako sekrety GitHub Environment `devhub` (`SF_JWT_KEY`, `SF_CLIENT_ID`, `SF_USERNAME`), a nie jako sekrety repozytorium — dzięki temu dostęp do nich można później ograniczyć regułami środowiska (gałęzie, zatwierdzenia).

## Konsekwencje

- Certyfikat jest ważny 365 dni (do 2027-10-28) — rotacja według [runbooka](../runbooki/rotacja-certyfikatu-jwt.md), najpóźniej miesiąc przed wygaśnięciem.
- Dostęp aplikacji ograniczony do użytkowników pre-autoryzowanych przez profil / permission set — nowy użytkownik CI wymaga jawnego dodania.
- Joby CI korzystające z Dev Hubu muszą deklarować `environment: devhub`, żeby otrzymać sekrety (#15).
- Klucz prywatny istnieje lokalnie poza repozytorium (`~/.sf-keys/insurance-app/`); `.gitignore` blokuje typowe rozszerzenia kluczy, a gitleaks (#19) stanowi drugą linię obrony.
