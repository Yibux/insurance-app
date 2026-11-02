# 0008. GitHub Actions + Salesforce CLI zamiast Copado jako platforma potoku CI/CD

- **Status:** przyjęta
- **Data:** 2026-11-02
- **Issue:** #27
- **Wymagania:** NFR-MNT-03

## Kontekst

Potok ma walidować każdy PR (testy, SAST, sekrety, zależności) w efemerycznym scratch orgu, w repozytorium publicznym, bez budżetu na licencje (Developer Edition Dev Hub, projekt magisterski). Potok jest też przedmiotem pracy: bramki muszą być w pełni jawne, wersjonowane w repozytorium i powtarzalne dla recenzenta. Do wyboru była platforma dedykowana ekosystemowi Salesforce (Copado) albo ogólna (GitHub Actions) z oficjalnym Salesforce CLI.

## Rozważane opcje

1. **Copado (DevOps Center / Copado Essentials)** — zalety: gotowe promocje między środowiskami, śledzenie zmian dla administratorów, wbudowane integracje (m.in. testy, compliance). Wady: komercyjna licencja i konfiguracja po stronie platformy (nie w repozytorium), słabsza powtarzalność dla czytelnika pracy, mniejsza kontrola nad przypięciem wersji narzędzi i uprawnieniami, wiązanie potoku z jednym dostawcą.
2. **GitHub Actions + Salesforce CLI** — wybrane: workflowy jako kod w repozytorium, darmowe dla repozytoriów publicznych, pełna kontrola nad krokami, uprawnieniami `GITHUB_TOKEN` i wersjami (przypięcie akcji do SHA), natywna integracja z code scanning (SARIF), Dependabotem i środowiskami z sekretami. Wady: każdy element (bramka pokrycia, tabela wyników, czyszczenie orgów) trzeba zbudować samemu; brak graficznego widoku promocji zmian.
3. **Inne CI (GitLab CI, Jenkins, Azure DevOps)** — odrzucone: repozytorium i tak jest na GitHubie; dodatkowa platforma zwiększa koszt utrzymania bez korzyści dla tezy.

## Decyzja

Potok budujemy na **GitHub Actions z Salesforce CLI** (wersja przypięta w workflowach), uwierzytelnianiem JWT do Dev Hubu ([ADR 0003](0003-jwt-bearer-ci-auth.md)) i scratch orgiem na PR. Powody: (1) brak kosztu licencji, (2) cała konfiguracja w repozytorium, a więc audytowalna i odtwarzalna przy ocenie pracy, (3) kontrola nad łańcuchem dostaw (przypięte SHA, najmniejsze uprawnienia), (4) wymagania pracy dotyczą własnych bramek (np. próg pokrycia 75% w `check_coverage.py`), których nie narzuca platforma.

Copado pozostaje rozwiązaniem, które rozważyłby zespół z budżetem i administratorami wymagającymi graficznego zarządzania wydaniami. Ograniczenie: Copado **nie było wdrażane ani mierzone**; ocena opiera się na dokumentacji i modelu licencyjnym, nie na teście.

## Konsekwencje

- Utrzymujemy sami: bramkę pokrycia, obsługę limitów scratch orgów (globalna `concurrency`, filtr `paths:`), obejście błędu C-1016 przy zakładaniu orgów, rotację certyfikatu JWT ([runbook](../runbooki/rotacja-certyfikatu-jwt.md)).
- Przeniesienie na inną platformę wymagałoby przepisania workflowów, ale skrypty (`scripts/ci/`) i polecenia `sf` są niezależne od GitHub Actions.
- Egzekwowanie bramek zależy od ustawień repozytorium (wymagane checki w rulesecie `main`), które na dzień 2026-11-02 **nie są włączone** (zadania #6, #25) — do tego czasu bramki informują, ale nie blokują merge'a.
- Opis potoku: [potok-cicd.md](../architektura/potok-cicd.md).
