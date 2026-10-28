# Etap 0 — Fundament

Wpisy dodawane po zamknięciu każdego zadania etapu (szablon: [KONWENCJE.md](../KONWENCJE.md#szablon-wpisu-implementacyjnego)).

<!-- Nowe wpisy poniżej, od najstarszego. -->

### #8 Spike: Experience Cloud LWR site in a scratch org

- **Data:** 2026-10-28 · **PR:** #<nr> · **Wymagania:** FR-PRT-01
- **Co zrobiono:** Rozszerzono definicję scratch orga o Experience Cloud, utworzono stronę „Insurance Portal” z szablonu Build Your Own (LWR), pobrano ją do źródeł i wdrożono do drugiego, czystego scratch orga, gdzie została opublikowana. Werdykt: GO z obejściami.
- **Jak:** `config/project-scratch-def.json` (feature `Communities`, `enableNetworksEnabled`, `enableExperienceBundleMetadata`); `sf community create … --template-name "Build Your Own (LWR)"`; `sf project retrieve start -m Network -m CustomSite -m DigitalExperienceConfig -m DigitalExperienceBundle -m NavigationMenu`; `replacements` w `sfdx-project.json` dla nazwy administratora strony.
- **Decyzje i alternatywy:** Strona trzymana jako metadane (DigitalExperienceBundle), a nie tworzona skryptem w każdym orgu — daje przegląd zmian w PR i powtarzalność. Wartości zależne od orga podstawiane przy deployu zamiast commitowania. `sourceApiVersion` → 68.0.
- **Problemy:** nazwa użytkownika scratch orga w `CustomSite`; prywatny e-mail w `Network`; błąd schematu `geoBotsAllowed` przy deployu w API 62.0. Szczegóły: [spike](../spikes/experience-cloud-lwr.md).
- **Dowody:** deploy `0AfO500000fvtMjKAI` do `spike-lwr-2`: Succeeded, 31/31 komponentów; `sf community publish` zakończony powodzeniem. <!-- zrzut opublikowanej strony -->
- **Do pracy:** rozdział #85/#86 (projekt i implementacja portalu), #84 (efemeryczne środowiska — infrastruktura jako kod także dla warstwy UI).
