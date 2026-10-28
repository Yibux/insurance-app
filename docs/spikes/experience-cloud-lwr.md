# Spike: Experience Cloud LWR w scratch orgu

- **Issue:** #8 · **Data:** 2026-10-28 · **Wymagania:** FR-PRT-01
- **Werdykt:** **GO, z obejściami** (opisane niżej)

## Pytanie

Czy portal klienta na Experience Cloud (szablon LWR) da się tworzyć w efemerycznym scratch orgu z Dev Hubu Developer Edition, przechowywać jako kod źródłowy i odtwarzać w nowym orgu, tak aby potok CI (scratch org per PR) mógł wdrażać portal?

## Co sprawdzono

1. Definicja scratch orga (`config/project-scratch-def.json`): feature `Communities`, `communitiesSettings.enableNetworksEnabled`, `experienceBundleSettings.enableExperienceBundleMetadata`.
2. Org `spike-lwr-1`: `sf community list template` pokazuje m.in. **Build Your Own (LWR)**; utworzono stronę:

   ```bash
   sf community create -o spike-lwr-1 --name "Insurance Portal" --template-name "Build Your Own (LWR)" --url-path-prefix portal
   ```

   Tworzenie jest asynchroniczne (BackgroundOperation, ok. 1–2 min).

3. Pobranie do źródeł:

   ```bash
   sf project retrieve start -o spike-lwr-1 -m Network -m CustomSite -m DigitalExperienceConfig -m DigitalExperienceBundle -m NavigationMenu
   ```

   Powstało 31 komponentów: `networks/`, `sites/`, `digitalExperienceConfigs/`, `digitalExperiences/site/Insurance_Portal1/` (widoki, routy, motyw, układy) i `navigationMenus/`.

4. Nowy org `spike-lwr-2` z tej samej definicji, `sf project deploy start -d force-app` → **Succeeded, 31/31**, następnie `sf community publish` → strona opublikowana.

## Problemy i obejścia

| Problem                                                                                                                                                     | Obejście                                                                                                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `CustomSite` zawiera `siteAdmin` i `siteGuestRecordDefaultOwner` z nazwą użytkownika konkretnego scratch orga — w każdym nowym orgu jest inna.              | Placeholder `__SITE_ADMIN_USERNAME__` w źródłach + `replacements` w `sfdx-project.json` podstawiające zmienną `SF_SITE_ADMIN_USERNAME` przy deployu. W CI ustawiana z `sf org display` po utworzeniu scratch orga. |
| `Network` zawierał prywatny adres e-mail autora (`emailSenderAddress`, `newSenderAddress`).                                                                 | `emailSenderAddress` → `noreply@example.com`, `newSenderAddress` usunięty. Danych osobowych nie commitujemy (spójne z gitleaks, #19).                                                                              |
| Deploy w API 62.0 odrzucał `content.json` strony: `geoBotsAllowed` — „additionalProperties is set to false”. Retrieve pobrał metadane w wersji orga (68.0). | `sourceApiVersion` podniesiony do **68.0** — wersja źródeł musi być nie niższa niż wersja, w której pobrano DigitalExperienceBundle.                                                                               |
| Nazwa API strony to `Insurance_Portal1` (sufiks dodawany automatycznie).                                                                                    | Akceptujemy; zmiana nazwy bundla po fakcie jest ryzykowna.                                                                                                                                                         |

## Wpływ na backlog

- **M1 (#16, scratch org per PR):** job deployu musi ustawić `SF_SITE_ADMIN_USERNAME` przed `sf project deploy start`; deploy strony wydłuża walidację o ok. 30–40 s.
- **M1 (#18, Code Analyzer):** `digitalExperiences/**/content.json` to JSON generowany przez platformę — prawdopodobnie do wykluczenia z części reguł / Prettiera.
- **M3 (portal):** zmiany w Experience Builder wykonujemy w scratch orgu i pobieramy tym samym `retrieve`; profile/permission sety gościa i członków sieci (`networkMemberGroups`) dojdą wraz z modelem bezpieczeństwa (M2).
- Każda zmiana wersji API orga może zmieniać schemat `content.json` — przy podnoszeniu `sourceApiVersion` warto zrobić ponowny retrieve.
