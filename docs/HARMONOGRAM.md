# Harmonogram i plan realizacji pracy

- **Temat:** Projekt i implementacja bezpiecznego systemu obsługi ubezpieczeń z wykorzystaniem metodyki DevSecOps w ekosystemie Salesforce
- **Wymagania i literatura:** [RAPORT.md](RAPORT.md)

## Założenia

- Oddanie pracy: czerwiec–wrzesień 2027; zamrożenie kodu 15.06.2027.
- Org Salesforce Developer Edition z włączonym Dev Hub (do założenia w Etapie 0).
- Monorepo: metadane Salesforce (`force-app/`) i backend Python (`integration-server/`) w jednym repozytorium.
- Zasada nadrzędna to **Shift-Left**: potok CI/CD z bramkami bezpieczeństwa powstaje _przed_ logiką biznesową, więc cały kod aplikacji od początku przechodzi przez bramki.

---

## 1. Z czego skorzystać (stos technologiczny)

| Obszar                   | Narzędzie / mechanizm                                                                                                                                             | Uwagi                                                                                                                                                                         |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Środowiska               | Salesforce **Developer Edition** jako Dev Hub + **Scratch Orgi**                                                                                                  | Limity DE: ok. 3 aktywne i 6 dziennie scratch orgów, więc w CI scratch org powstaje per PR i jest kasowany na końcu                                                           |
| Model danych             | Obiekty custom: `Policy__c`, `Coverage__c`, `Claim__c`, `Claim_Document__c`; ubezpieczony = Contact/Account                                                       | Financial Services Cloud (InsurancePolicy, Claim) wymaga licencji, której nie ma w DE/scratch                                                                                 |
| Bezpieczeństwo platformy | OWD Private, Permission Sets / Permission Set Groups, Sharing Sets dla portalu, `with sharing`, `WITH USER_MODE`, `Security.stripInaccessible`, Restriction Rules | Bezpośrednio odpowiada Zero-Trust (Al Kalach) i FLS w SAST                                                                                                                    |
| Logika                   | Apex (warstwa serwisów + selektory), Apex triggers (wzorzec handler), Flow tam, gdzie wystarczy                                                                   |                                                                                                                                                                               |
| Portal                   | **Experience Cloud** (szablon Build Your Own LWR / Customer Account Portal) + **LWC**                                                                             | Scratch def: feature `Communities`, `communitiesSettings.enableNetworksEnabled`. Do zrobienia: spike na start                                                                 |
| CI/CD                    | **GitHub Actions**: `pr-validation.yml` (PR → scratch org → deploy → testy → SAST → kasowanie orga), `deploy.yml` (merge do `main` → org docelowy)                |                                                                                                                                                                               |
| Auth CI → Salesforce     | **JWT Bearer Flow** (External Client App / Connected App + certyfikat), klucz w GitHub Encrypted Secrets / Environments                                           | Machapatri, Lakade. Krótko żyjące sesje, brak haseł                                                                                                                           |
| SAST Salesforce          | **Salesforce Code Analyzer v5** (`sf code-analyzer run`: PMD, ESLint/LWC, RetireJS, Flow Scanner, Graph Engine)                                                   | Próg: fail na severity ≤ 2                                                                                                                                                    |
| SAST / SCA pozostałe     | **gitleaks** (sekrety), **CodeQL** (JS/Python), **Bandit** + **pip-audit** (Python), **Dependabot**, `npm audit`                                                  | IEEE 2025: sekrety i łańcuch dostaw                                                                                                                                           |
| Testy                    | Apex tests (`sf apex run test --code-coverage`), **LWC Jest** (`sfdx-lwc-jest`), **pytest**                                                                       | Bramka 75% liczona własnym skryptem z wyniku JSON (`--result-format json`), bo platforma egzekwuje 75% tylko przy deployu na produkcję                                        |
| Jakość                   | Prettier (+ plugin Apex), ESLint, Husky + lint-staged (pre-commit, czyli shift-left lokalnie), ruff dla Pythona                                                   | Już w szablonie                                                                                                                                                               |
| Backend                  | **Python 3.12 + FastAPI**; `simple-salesforce` / **Bulk API 2.0**; PyJWT do JWT Bearer                                                                            | Etap 1: ładowanie danych historycznych                                                                                                                                        |
| External Objects         | **Salesforce Connect, adapter OData 4.0** → endpoint OData w FastAPI; **Named Credential + External Credential**                                                  | Wymaga publicznego HTTPS: hosting (Render / Azure App Service free / Cloudflare Tunnel). Dostępność Salesforce Connect w DE/scratch sprawdzić w spike'u, to największe ryzyko |
| Repo / proces            | Branch protection na `main` (wymagane checki, review), Conventional Commits, CODEOWNERS, szablon PR                                                               |                                                                                                                                                                               |

### Docelowa struktura monorepo

```
insurance-app/
├─ force-app/main/default/        # metadane Salesforce (objects, classes, lwc, permissionsets, experiences…)
├─ config/project-scratch-def.json
├─ integration-server/            # Python: FastAPI, loader Bulk API, endpoint OData, testy pytest
├─ scripts/ci/                    # check_coverage.py, parsowanie raportów SAST
├─ .github/workflows/             # pr-validation.yml, deploy.yml, python-ci.yml, codeql.yml
├─ .github/dependabot.yml, CODEOWNERS, pull_request_template.md
├─ code-analyzer.yml              # konfiguracja reguł SAST
└─ docs/                          # HARMONOGRAM.md, architektura, ADR-y, wyniki pomiarów
```

---

## 2. Harmonogram (start 12.10.2026, kod zamrożony 15.06.2027, oddanie IX 2027)

| #   | Okres                   | Etap                              | Rezultat (Definition of Done)                                                                                                                                                                                 |
| --- | ----------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0   | 12.10 – 25.10.2026      | **Fundament**                     | Dev Hub (DE) założony; szkielet SFDX zacommitowany i wypchnięty; branch protection; External Client App + certyfikat JWT; **spike'i**: Experience Cloud w scratch orgu, Salesforce Connect OData w DE/scratch |
| 1   | 26.10 – 06.12.2026      | **Potok DevSecOps (shift-left)**  | `pr-validation.yml`: scratch org → deploy → Apex + Jest → Code Analyzer → bramka 75% → delete org; gitleaks, CodeQL, Dependabot; artefakty raportów w PR; dokumentacja potoku                                 |
| 2   | 07.12.2026 – 31.01.2027 | **Model danych i bezpieczeństwo** | Obiekty Policy/Coverage/Claim, OWD Private, permission sets (Agent, Claims Adjuster, Customer), serwisy Apex z `USER_MODE`, triggery, testy ≥ 85%; dane testowe (`sf data import tree`)                       |
| 3   | 01.02 – 14.03.2027      | **Portal Experience Cloud**       | Site LWR w metadanych; LWC: lista polis, szczegóły, zgłoszenie szkody (upload dokumentów), komunikacja z agentem (Case/Chatter); Sharing Sets; testy Jest                                                     |
| 4   | 15.03 – 25.04.2027      | **Backend Python, faza 1**        | `integration-server/`: loader danych historycznych przez Bulk API 2.0, JWT Bearer, upsert po External ID, logowanie i audyt; `python-ci.yml` (ruff, pytest, Bandit, pip-audit)                                |
| 5   | 26.04 – 31.05.2027      | **External Objects**              | Endpoint OData 4.0 w FastAPI (np. historia płatności / dane medyczne szkody); hosting HTTPS; External Data Source + Named/External Credential; wyświetlanie w portalu bez przechowywania w CRM                |
| 6   | 01.06 – 15.06.2027      | **Eksperyment i hardening**       | Pomiary do części badawczej (patrz pkt 4); poprawki; **zamrożenie kodu 15.06**                                                                                                                                |
| 7   | 16.06 – 31.08.2027      | **Redakcja pracy**                | Rozdziały implementacyjne i wyniki dopisane do szkicu; korekta, promotor                                                                                                                                      |
| 8   | IX 2027                 | Bufor / obrona                    | Prezentacja, demo                                                                                                                                                                                             |

**Pisanie równolegle (od razu, nie na końcu):**

- XI–I: rozdziały teoretyczne (1–3) na bazie Raportu;
- po każdym etapie: 1–2 strony opisu implementacji i decyzje w `docs/adr/`;
- czerwiec: wyniki eksperymentu.

Rytm pracy: co 2 tygodnie przegląd postępu (issue/milestone na GitHub per etap).

---

## 3. Literatura z Raportu: gdzie ją wykorzystać

| Publikacja                               | Rozdział pracy / element systemu                                      |
| ---------------------------------------- | --------------------------------------------------------------------- |
| Al Kalach 2025 (Zero-Trust)              | Model bezpieczeństwa: OWD, permission sets, Restriction Rules, portal |
| Machapatri 2020 (JWT + OAuth 2.0)        | Integracja Python ↔ SF, CI → Dev Hub                                  |
| Cheenepalli i in. 2025 (DevSecOps w MŚP) | Uzasadnienie skanu per commit/PR                                      |
| Bavadiya 2022 (bramki jakości)           | Projekt bramek + eksperyment wykrywalności                            |
| IEEE 2025 SLR (cyberbezp. DevOps)        | gitleaks, Dependabot, ochrona sekretów, łańcuch dostaw                |
| Guduru 2023 (Copado / CI/CD SF)          | Porównanie: GitHub Actions + SF CLI vs Copado                         |
| Shift Left Security 2025                 | Kolejność etapów (potok najpierw), husky pre-commit                   |
| Jammeh 2020 (czynnik ludzki)             | Szablon PR, checklisty, dokumentacja reguł                            |
| IEEE/ACM 2022 (błędy w SAST)             | Analiza false positives/negatives Code Analyzera                      |
| Lakade 2025 (zero-touch secrets)         | Krótko żyjące poświadczenia, GitHub Environments, rotacja certyfikatu |
| SF DX Guide (scratch def)                | `config/project-scratch-def.json`                                     |

Do uzupełnienia: oficjalna dokumentacja Salesforce (Security Implementation Guide, Salesforce Connect OData 4.0, Experience Cloud LWR, Code Analyzer) oraz OWASP Top 10 / OWASP SAMM jako rama oceny.

---

## 4. Część badawcza (żeby praca nie była tylko „zbudowałem aplikację”)

Eksperyment w stylu Bavadiya + IEEE/ACM 2022:

1. Przygotować zbiór ok. 20–30 **celowo podatnych zmian**, każda jako osobny PR:
   - SOQL injection;
   - brak FLS/CRUD;
   - `without sharing`;
   - zaszyty sekret;
   - podatna zależność npm/pip;
   - XSS w LWC;
   - SOQL w pętli.
2. Zmierzyć dla każdej bramki:
   - wykrywalność (TP/FN);
   - fałszywe alarmy (FP);
   - czas potoku.
3. Porównać:
   - wykrycie lokalnie (pre-commit) vs w PR vs brak wykrycia;
   - koszt czasowy potoku vs „velocity”.
4. Wyniki zebrać w `docs/experiment/` jako materiał do rozdziału wyników.
