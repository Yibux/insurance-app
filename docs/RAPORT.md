# Raport: Bezpieczeństwo i Automatyzacja CI/CD w Ekosystemie Chmurowym Salesforce

## 1. Wprowadzenie do Nowoczesnego Ekosystemu Chmurowego

W dobie powszechnej cyfryzacji i bezprecedensowej migracji krytycznych procesów biznesowych do chmury obliczeniowej, platformy klasy Enterprise, takie jak Salesforce, stały się absolutnym fundamentem globalnego zarządzania relacjami z klientami (CRM) oraz danymi korporacyjnymi. Architektura wielodostępna (multi-tenant), na której opiera się ten ekosystem, oferuje ogromną skalowalność, elastyczność operacyjną oraz optymalizację kosztów. Jednakże, z architektonicznego punktu widzenia, stawia ona przed inżynierami oprogramowania i specjalistami ds. cyberbezpieczeństwa niezwykle złożone wyzwania. Konieczność zachowania rygorystycznej izolacji danych pomiędzy dzierżawcami, zapewnienie ciągłej zgodności z międzynarodowymi regulacjami oraz nieustanna ochrona przed coraz bardziej zaawansowanymi wektorami ataków wymagają całkowitego odejścia od tradycyjnych, reaktywnych modeli bezpieczeństwa.

Odpowiedzią na te wyzwania jest głęboka integracja rygorystycznych praktyk bezpieczeństwa z metodykami zwinnego wytwarzania oprogramowania, znana w branży jako DevSecOps (Development, Security, Operations). Jak zauważają badacze zjawiska "Shift-Left": "Shift Left Security is a means for security in the software development lifecycle (SDLC), and it believes that proactively addressing vulnerabilities early on in SDLC instead of being reactionary is more beneficial". Przeniesienie procesów testowania i analizy kodu do wczesnych faz projektowania redukuje podatność systemów informatycznych na ataki.

## 2. Temat Pracy

**Projekt i implementacja bezpiecznego systemu obsługi ubezpieczeń z wykorzystaniem metodyki DevSecOps w ekosystemie Salesforce**

### Cel pracy

Celem projektu jest stworzenie nowoczesnego systemu do zarządzania polisami i roszczeniami ubezpieczeniowymi, opartego na platformie Salesforce, z silnym naciskiem na automatyzację procesu wytwórczego i zapewnienie wysokich standardów bezpieczeństwa.

### Zakres technologiczny i architektura

- **Warstwa Kliencka (Experience Cloud)**
  Utworzenie bezpiecznego portalu (Experience Site), w którym ubezpieczeni mogą przeglądać swoje aktywne polisy, zgłaszać szkody i komunikować się z agentami.

- **Automatyzacja CI/CD (DevSecOps)**
  Wdrożenie w pełni zautomatyzowanego potoku wdrożeniowego (np. przy użyciu GitHub Actions). Każda zmiana w kodzie (przy otwartym Pull Request) będzie inicjować utworzenie środowiska efemerycznego (Scratch Org), na którym uruchomiona zostanie statyczna analiza kodu (SAST) oraz walidacja testów jednostkowych Apex. Potok ma rygorystycznie egzekwować minimum 75% pokrycia kodu testami przed dopuszczeniem do wdrożenia.

- **Integracja z serwerem zewnętrznym (Python)**
  Wdrożenie zewnętrznego backendu w języku Python. W pierwszej fazie serwer będzie odpowiedzialny za bezpieczne i zautomatyzowane ładowanie danych historycznych/transakcyjnych do Salesforce za pomocą API. Docelowo system zakłada integrację za pomocą mechanizmu External Objects, co pozwoli na wirtualne wyświetlanie wrażliwych danych z systemów zewnętrznych bez ich fizycznego przechowywania w CRM, spełniając tym samym wymogi rezydencji danych.

## 3. Przegląd Literatury

Aby zapewnić rygorystyczną bazę naukową, poniżej przedstawiono przegląd 10 kluczowych publikacji akademickich i branżowych. Stanowią one teoretyczny trzon nowoczesnego podejścia do bezpieczeństwa platform CRM i metodyki DevSecOps.

| Lp. | Publikacja i Autor                                                              | Opis i Analiza                                                                                                                                                                                                                                                                         | Kluczowy Cytat                                                                                                                                                                                                                                                              |
| --- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | N. Al Kalach (2025)<br>[Scribd][scribd]                                         | Praca stanowi fundamentalną analizę wdrożenia modelu Zero-Trust w środowisku Salesforce. Autorka analizuje mechanizmy warstwowej kontroli dostępu, kryptografii (Platform Shield) oraz zarządzania sesjami. Badania te dowodzą skuteczności platformy w modelu współodpowiedzialności. | "Results show how Salesforce has been fully moving towards its defense-in-depth model without overstating the shared-responsibility paradigm between the platform provider and the customer."                                                                               |
| 2   | S.V.V. Machapatri (2020)<br>[ResearchGate][jwt]                                 | Kluczowe badanie definiujące ryzyka tradycyjnego uwierzytelniania w integracjach chmurowych (Basic Auth) i udowadniające konieczność przejścia na bezstanowe tokeny kryptograficzne JWT połączone ze standardem OAuth 2.0 dla integracji serwerów zewnętrznych.                        | "In Salesforce integrations, a JWT is used to securely validate external partner systems prior to granting them access to your Salesforce instance."                                                                                                                        |
| 3   | J. Cheenepalli i inni (2025)<br>[arXiv][arxiv]                                  | Obszerne badanie empiryczne (próba 405 specjalistów), które diagnozuje przepaść między świadomością kadry zarządzającej a faktyczną automatyzacją testów bezpieczeństwa w potokach CI/CD.                                                                                              | "Despite strong leadership prioritization of security (73%), automation gaps persist, with only 12% of organizations conducting security scans per commit."                                                                                                                 |
| 4   | P. Bavadiya (2022)<br>[ResearchGate][bavadiya]                                  | Badanie symulacyjne badające wykrywalność luk w architekturze na etapie CI/CD. Autor matematycznie udowadnia efektywność "bram jakości", z których aż 93,64% poprawnie odrzuca wadliwy kod jeszcze w środowisku przejściowym.                                                          | "By incorporating automated security into all stages of continuous integration and continuous delivery, these findings illustrate that post-deployment risk may be efficiently reduced, incident response can be strengthened, and development velocity can be maintained." |
| 5   | Publikacja IEEE (2025)<br>[IEEE Xplore][ieee-slr]                               | Metaanaliza 62 artykułów z lat 2016-2025. Wskazuje luki w łańcuchu dostaw oraz zarządzaniu hasłami jako główne wyzwanie współczesnego DevOpsu.                                                                                                                                         | "The analysis revealed that the most significant threats are related to uncontrolled automation, exposure of sensitive secrets in CI/CD pipelines, lack of mutual authentication between distributed services, supply chain attacks..."                                     |
| 6   | V.S. Guduru (2023)<br>[ResearchGate][copado]                                    | Artykuł poświęcony specyfice zautomatyzowanych wdrożeń natywnych metadanych w architekturze Salesforce z użyciem wyspecjalizowanych narzędzi wspierających proces ciągłej integracji i korzystania z efemerycznych sandboxów.                                                          | "In the Salesforce ecosystem, this means that metadata, configurations, and code changes are automated for deployment across a variety of environments-the sandboxes and production org."                                                                                   |
| 7   | Praca zbiorowa (2025)<br>[ResearchGate][shift-left]                             | Opracowanie skupiające się na ewolucji zabezpieczeń z modelu post-produkcyjnego na metodykę aktywnego poszukiwania luk we wczesnych fazach kodowania.                                                                                                                                  | "Shift Left Security is a means for security in the software development lifecycle (SDLC), and it believes that proactively addressing vulnerabilities early on in SDLC instead of being reactionary is more beneficial."                                                   |
| 8   | B. Jammeh (2020)<br>[ResearchGate][jammeh]                                      | Praca badawcza, która podkreśla czynnik ludzki. Wdrożenie narzędzi automatycznych nie odniesie skutku, jeśli programiści z powodu braku edukacji będą ignorować alerty bezpieczeństwa rzucane przez analizatory kodu.                                                                  | "We understand that access to security knowledge and expertise is key in DevSecOps, and every team member must understand their security responsibilities."                                                                                                                 |
| 9   | Konferencja IEEE/ACM (2022)<br>[IEEE Xplore / Conference Proceeding][ieee-sast] | Niezwykle ważne badanie podważające całkowite zaufanie do skanerów bezpieczeństwa (SAST). Wykazano w nim, że same narzędzia analizy statycznej, na których opiera się branża, posiadają poważne usterki.                                                                               | "Our study finds 46 bugs about the implementation or design of static analysis rules, among which 30 are fixed/confirmed and the left are awaiting confirmation."                                                                                                           |
| 10  | S. Lakade (2025)<br>[JICRCR][jicrcr]                                            | Koncepcja operacyjna dotycząca uwierzytelniania. Autor proponuje, by potoki CI/CD korzystały z wygasających w kilka minut poświadczeń (OIDC), całkowicie eliminując zaszyte w systemie hasła.                                                                                          | "The zero-touch approach fundamentally reduces attack surfaces by ensuring credentials exist only during active use, automatically rotate without operational intervention, and provide complete audit trails..."                                                           |

## 4. Architektura Zero-Trust w Środowisku Wielodostępnym

Zrozumienie bezpieczeństwa Salesforce wymaga uprzedniego zdefiniowania specyfiki jego architektury opartej na metadanych. Architektura ta znacząco wzmacnia izolację, ponieważ oddziela fizyczny nośnik danych od logicznej warstwy aplikacji. Koncepcja Zero-Trust Architecture wprowadza zasadę: "Nigdy nie ufaj, zawsze weryfikuj". W architekturze Salesforce paradygmat ten zaimplementowano poprzez tak zwany model zorientowany na tożsamość. Jak zauważa badaczka Nancy Al Kalach: "Results show how Salesforce has been fully moving towards its defense-in-depth model without overstating the shared-responsibility paradigm between the platform provider and the customer."

Ochrona opiera się na wielowarstwowej kontroli dostępu, izolacji kryptograficznej i szyfrowaniu w spoczynku, ale pełne wykorzystanie tego modelu wymaga przeniesienia tych standardów na grunt infrastruktury jako kodu (IaC) przy użyciu DevSecOps.

## 5. Ewolucja Potoków CI/CD w Kierunku DevSecOps

Tradycyjne modele inżynierii opóźniały weryfikację bezpieczeństwa, co znacząco zwiększało jej koszty. Transformacja do DevSecOps stała się jedyną racjonalną odpowiedzią branży technologicznej. Zintegrowany proces polega na automatycznym egzekwowaniu zasad i uruchamianiu skanerów kodu bezpośrednio po każdej operacji połączenia (merge/pull request) dokonywanej przez programistę. Skuteczność takiego rozwiązania udowadnia P. Bavadiya, zaznaczając: "By incorporating automated security into all stages of continuous integration and continuous delivery, these findings illustrate that post-deployment risk may be efficiently reduced, incident response can be strengthened, and development velocity can be maintained."

Niestety, proces adaptacji bywa wyboisty. Według obszernego badania ankietowego przeprowadzonego przez Cheenepalli i in. z 2025 roku, o ile kierownictwo w 73% deklaruje cyberbezpieczeństwo jako priorytet, o tyle systemy CI/CD nie nadążają technologicznie: "Despite strong leadership prioritization of security (73%), automation gaps persist, with only 12% of organizations conducting security scans per commit." Niezbędna jest tu silna zmiana świadomości organizacyjnej, co znajduje odzwierciedlenie w słowach B. Jammeha: "We understand that access to security knowledge and expertise is key in DevSecOps, and every team member must understand their security responsibilities."

## 6. Anatomia i Złożoność Statycznej Analizy Kodu (SAST)

Filar zabezpieczeń w potokach Salesforce opiera się na analizatorach statycznych, takich jak Apex PMD. Narzędzia te są "bramkami kontrolnymi", oceniającymi m.in. użycie języka SOQL wewnątrz pętli lub luki w obszarze sprawdzania uprawnień FLS (Field Level Security). Jednak branża nie może w 100% polegać na algorytmach. Problem "Błędów w Poszukiwaczach Błędów" opisano na międzynarodowych konferencjach IEEE, poddając inżynierii odwrotnej same silniki analizujące: "Our study finds 46 bugs about the implementation or design of static analysis rules, among which 30 are fixed/confirmed and the left are awaiting confirmation." SAST musi być stale wspierany dynamicznymi testami integracyjnymi.

## 7. Zarządzanie Sekretami i Integracja Zewnętrzna

W potoku łączącym serwer backendowy w Pythonie z ekosystemem Salesforce fundamentalną rolę odgrywa mechanizm Zero-Touch Secrets Management. Jak opisuje literatura badawcza: "The zero-touch approach fundamentally reduces attack surfaces by ensuring credentials exist only during active use, automatically rotate without operational intervention, and provide complete audit trails." Potok automatyzacji loguje się do Salesforce DX bez statycznych, nieszyfrowanych haseł.

Tę samą technologię stosuje się do wirtualnej wymiany danych poprzez External Objects. Do zabezpieczenia uwierzytelnienia pomiędzy warstwami używa się połączenia OAuth 2.0 i przepływu JWT Bearer Flow. Machapatri w swoich badaniach podkreśla znaczenie tego mechanizmu przy zwalidowaniu relacji B2B w modelu Data Residency: "In Salesforce integrations, a JWT is used to securely validate external partner systems prior to granting them access to your Salesforce instance."

## 8. Środowiska Efemeryczne w Architekturze Salesforce

Wyeliminowanie problemu zatorów konfiguracyjnych i wycieku danych podczas testowania jest możliwe dzięki środowiskom efemerycznym, takim jak Scratch Orgs w architekturze Salesforce. Konfiguracja powoływana do życia natychmiastowo pozwala na stworzenie absolutnie wolnego od długu technologicznego miejsca do zwalidowania kodu. Guduru V.S. doskonale opisuje tę pętlę w Salesforce: "In the Salesforce ecosystem, this means that metadata, configurations, and code changes are automated for deployment across a variety of environments-the sandboxes and production org." Środowisko istnieje tylko przez czas trwania potoku testowego w chmurze, minimalizując wektor ataku z wielu dni lub miesięcy (jak w klasycznych sandboxach) do minut.

## 9. Bibliografia

- [Shift Left Security][shift-left] – ResearchGate (Dostęp: czerwca 2026).
- [Salesforce Security: Zero-Trust & Compliance][scribd] – Scribd (Dostęp: czerwca 2026).
- [Securing Salesforce Integrations with JWT Authentication and OAuth 2.0: A Comprehensive Approach to Real-Time Data Protection][jwt] – ResearchGate (Dostęp: czerwca 2026).
- [Advancing DevSecOps in SMEs: Challenges and Best Practices][arxiv] – arXiv (Dostęp: czerwca 2026).
- [Devsecops: Automating Security Vulnerability Detection and Response in CI/CD Pipelines][bavadiya] – ResearchGate (Dostęp: czerwca 2026).
- [Cybersecurity in DevOps Environments: A Systematic Literature Review][ieee-slr] – IEEE Xplore (Dostęp: czerwca 2026).
- [The Future of DevOps in Salesforce: Implementing CI/CD with Copado][copado] – ResearchGate (Dostęp: czerwca 2026).
- [DevSecOps Security Expertise a Key to Automated Testing in CI/CD Pipeline][jammeh] – ResearchGate (Dostęp: czerwca 2026).
- [Find Bugs in Static Bug Finders][ieee-sast] – IEEE Xplore / Conference Proceeding (Dostęp: czerwca 2026).
- [Zero-Touch Secrets Management: Securing Ci/Cd Pipelines Through Ephemeral Credentials][jicrcr] – JICRCR (Dostęp: czerwca 2026).
- [Build Your Own Scratch Org Definition File][sfdx-scratch] – Salesforce DX Developer Guide (Dostęp: czerwca 2026).

[scribd]: https://www.scribd.com/document/969370449/Salesforce-Security-Architecture-for-Zero-Trust-Encryption-Compliance
[jwt]: https://www.researchgate.net/publication/385814964_Securing_Salesforce_Integrations_with_JWT_Authentication_and_OAuth_20_A_Comprehensive_Approach_to_Real-Time_Data_Protection
[arxiv]: https://arxiv.org/abs/2503.22612
[bavadiya]: https://www.researchgate.net/publication/395472364_Devsecops_Automating_Security_Vulnerability_Detection_and_Response_in_CICD_Pipelines
[ieee-slr]: https://ieeexplore.ieee.org/iel8/6287639/10820123/11050425.pdf
[copado]: https://www.researchgate.net/publication/385774691_The_Future_of_DevOps_in_Salesforce_Implementing_CICD_with_Copado
[shift-left]: https://www.researchgate.net/publication/394857544_Shift_Left_Security
[jammeh]: https://www.researchgate.net/publication/347441415_DevSecOps_Security_Expertise_a_Key_to_Automated_Testing_in_CICD_Pipeline
[ieee-sast]: https://ieeexplore.ieee.org/iel7/9796152/9796159/09796187.pdf
[jicrcr]: https://jicrcr.com/index.php/jicrcr/article/view/3601
[sfdx-scratch]: https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_scratch_orgs_def_file.htm
