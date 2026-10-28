# Rotacja certyfikatu JWT dla CI

Dotyczy External Client App `insurance-app-ci` w Dev Hubie i sekretów GitHub Environment `devhub`. Decyzja: [ADR 0003](../adr/0003-jwt-bearer-ci-auth.md).

**Kiedy:** co roku, najpóźniej miesiąc przed wygaśnięciem (obecny certyfikat: do 2027-10-28), oraz natychmiast przy podejrzeniu wycieku klucza.

Sprawdzenie daty ważności:

```bash
openssl x509 -in ~/.sf-keys/insurance-app/server.crt -noout -enddate
```

## Procedura

1. **Nowa para kluczy** (poza repozytorium; w Git Bashu `//CN` zamiast `/CN`, bo MSYS zamienia `/CN=…` na ścieżkę):

   ```bash
   cd ~/.sf-keys/insurance-app
   openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout server-new.key -out server-new.crt -subj "//CN=insurance-app-ci"
   ```

2. **Certyfikat w Salesforce:** Setup → External Client App Manager → `insurance-app-ci` → Edit Settings → Flow Enablement → wgraj `server-new.crt` i zapisz. Aplikacja przyjmuje jeden certyfikat, więc od tej chwili stary klucz przestaje działać — kroki 3–4 wykonać od razu.

3. **Test lokalny:**

   ```bash
   sf org login jwt --client-id <SF_CLIENT_ID> --jwt-key-file ~/.sf-keys/insurance-app/server-new.key --username <SF_USERNAME> --alias devhub-jwt
   ```

   Zmiana propaguje się do kilku minut; przy błędzie `invalid_grant` odczekać i powtórzyć.

4. **Sekret w GitHubie:**

   ```bash
   gh secret set SF_JWT_KEY --env devhub < ~/.sf-keys/insurance-app/server-new.key
   ```

5. **Weryfikacja w CI:** uruchomić ponownie dowolny workflow korzystający ze środowiska `devhub` i sprawdzić krok logowania.

6. **Sprzątanie:** zastąpić stare pliki nowymi (`server-new.*` → `server.*`), zaktualizować datę ważności w tym pliku i w ADR 0003.

## Przy wycieku klucza

Wykonać kroki 1–4 natychmiast (wgranie nowego certyfikatu unieważnia stary klucz), następnie w Setup → Session Management / OAuth Usage unieważnić aktywne tokeny aplikacji `insurance-app-ci` i odnotować incydent w dzienniku implementacji.
