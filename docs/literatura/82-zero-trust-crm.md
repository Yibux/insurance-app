# Literatura do rozdziału: bezpieczeństwo chmurowego CRM i Zero-Trust w Salesforce (#82)

Notatka źródłowa do zadania [#82](https://github.com/Yibux/insurance-app/issues/82). Wpisy są w formacie z `.claude/AGENT_RULES.md` (klucz, opis, teza, cytat, weryfikacja). Data dostępu dla wszystkich wpisów: 2026-11-02.

Legenda pola **Weryfikacja:** „pełny tekst" (otwarto i przeczytano całość), „tylko abstrakt/strona" (otwarto stronę opisową), „nie zweryfikowano".

Powiązane wymagania: NFR-SEC-01 (Zero-Trust, OWD Private), NFR-SEC-02 (najmniejsze uprawnienia), NFR-SEC-07 (portal widzi tylko własne rekordy). Zob. [WYMAGANIA.md](../WYMAGANIA.md).

## 1. Źródła zweryfikowane

### Rose2020 (norma / dokument NIST)

- **Klucz:** Rose2020
- **Opis bibliograficzny:** Rose S., Borchert O., Mitchell S., Connelly S., *Zero Trust Architecture*, NIST Special Publication 800-207, National Institute of Standards and Technology, 2020, DOI: 10.6028/NIST.SP.800-207, https://csrc.nist.gov/pubs/sp/800/207/final (dostęp: 2026-11-02)
- **Wspiera tezę:** Definicja Zero Trust (przesunięcie ochrony z perymetru sieciowego na użytkowników, zasoby i uwierzytelnianie/autoryzację przed każdą sesją), która jest podstawą NFR-SEC-01 i NFR-SEC-02.
- **Cytat (opcjonalnie):** „Zero trust (ZT) is the term for an evolving set of cybersecurity paradigms that move defenses from static," (abstrakt na stronie katalogowej CSRC; fragment, bo narzędzie ucina cytat)
- **Weryfikacja:** tylko abstrakt. Autorzy, rok i DOI potwierdzone na stronie CSRC. Plik PDF pobrano, ale nie dało się go odczytać, więc numerów stron, sekcji i listy tez (tenets) nie sprawdzono.

### Pelkey2026 (publikacja producenta, blog Salesforce)

- **Klucz:** Pelkey2026
- **Opis bibliograficzny:** Pelkey L., *Security as a Shared Responsibility Between Provider and Customer*, Salesforce Blog, 22.01.2026, https://www.salesforce.com/blog/shared-responsibility-model/ (dostęp: 2026-11-02)
- **Wspiera tezę:** Salesforce sam deklaruje model współodpowiedzialności, w którym klient odpowiada za swoje dane, konfigurację i prawa dostępu (czyli dokładnie za warstwę wdrażaną w tym projekcie: OWD, Permission Sets, Apex `with sharing`).
- **Cytat (opcjonalnie):** „security is a shared responsibility between Salesforce and its customers." oraz „customers are responsible for protecting their own data, configurations, and access rights." (sekcje bez numeracji)
- **Weryfikacja:** pełny tekst (strona otwarta, cytaty potwierdzone dosłownie). Uwaga: to blog producenta, nie recenzowana publikacja. Traktować jako deklarację dostawcy, nie niezależną analizę. Data wpisu pochodzi ze strony, nie sprawdzono, czy jest to data pierwotnej publikacji.

### Sheck2024 (organizacja branżowa, blog CSA)

- **Klucz:** Sheck2024
- **Opis bibliograficzny:** Sheck N., *What is the Shared Responsibility Model in the Cloud?*, Cloud Security Alliance, 25.01.2024, https://cloudsecurityalliance.org/blog/2024/01/25/what-is-the-shared-responsibility-model-in-the-cloud (dostęp: 2026-11-02)
- **Wspiera tezę:** Niezależna (od Salesforce) definicja modelu współodpowiedzialności w chmurze oraz zasada, że klient może delegować zarządzanie ryzykiem, ale nie odpowiedzialność za nie.
- **Cytat (opcjonalnie):** „Organizations can choose to delegate risk management but not the accountability for managing these risks."
- **Weryfikacja:** pełny tekst (cytaty potwierdzone dosłownie). Uwaga: wpis blogowy CSA, rangą poniżej recenzowanej literatury. Alternatywa do rozważenia: *Security Guidance for Critical Areas of Focus in Cloud Computing v5* (CSA, 2024), niezweryfikowana, bo nie udało się otworzyć jej PDF.

### Palleti2025 (czasopismo, status recenzji niepotwierdzony)

- **Klucz:** Palleti2025
- **Opis bibliograficzny:** Palleti P., *Zero Trust Security in Multi-Tenant Salesforce Environments*, European Journal of Advances in Engineering and Technology, vol. 12, nr 5, s. 23-26, 2025, DOI: 10.5281/zenodo.15681093, https://zenodo.org/records/15681093 (dostęp: 2026-11-02)
- **Wspiera tezę:** Zastosowanie Zero Trust (NIST SP 800-207) w wielodostępnym Salesforce przez kontrole natywne (Hyperforce, Shield, Event Monitoring) i podejście warstwowe: tożsamość, dane, sieć, analityka zachowań.
- **Cytat (opcjonalnie):** „offers a robust security framework that is particularly well-suited for dynamic, cloud-native, multi-tenant environments." (abstrakt; zdanie mówi o ZTA według NIST SP 800-207)
- **Weryfikacja:** tylko abstrakt (rekord Zenodo, licencja CC BY 4.0). Pełnego tekstu nie czytano. Strona nie podaje informacji o recenzji, a artykuł ma 4 strony, więc wagę dowodową oceniać ostrożnie. Numer DOI jest DOI rekordu Zenodo, nie wydawcy czasopisma.

### Oladimeji2024 (preprint)

- **Klucz:** Oladimeji2024
- **Opis bibliograficzny:** Oladimeji G., *A Critical Analysis of Foundations, Challenges and Directions for Zero Trust Security in Cloud Environments*, arXiv:2411.06139, 2024, DOI: 10.48550/arXiv.2411.06139, https://arxiv.org/abs/2411.06139 (dostęp: 2026-11-02)
- **Wspiera tezę:** Ogólny (nie Salesforce-specyficzny) przegląd Zero Trust w chmurze: niewystarczalność ochrony perymetrycznej, mikrosegmentacja, najmniejsze uprawnienia, ciągłe monitorowanie oraz wyzwania (skalowalność, koszty, integracja, zgodność).
- **Cytat (opcjonalnie):** brak (nie udało się odczytać tekstu PDF).
- **Weryfikacja:** tylko abstrakt. Preprint bez recenzji; w metadanych PDF występuje odwołanie do DOI 10.21203/rs.3.rs-3152878/v1 (Research Square), którego nie sprawdzono.

## 2. Źródła z Raportu, których NIE udało się zweryfikować

| Źródło w [RAPORT.md](../RAPORT.md) | Wynik | Zalecenie |
| --- | --- | --- |
| N. Al Kalach (2025), Scribd | Strona Scribd nie podaje autora (widoczny tylko login uploadera), roku, wydawcy ani DOI. Cytat „Results show how Salesforce has been fully moving towards its defense-in-depth model..." **nie występuje** w widocznej części dokumentu (tekst był ucięty, więc nie wykluczono, że jest dalej). Ten sam tytuł pojawia się w wynikach wyszukiwania jako rekord ResearchGate 398441881, bez możliwości otwarcia (HTTP 403). | Nie cytować jako „Al Kalach 2025", dopóki nie zostanie potwierdzony autor i miejsce publikacji. Sprawdzić ręcznie rekord ResearchGate. Do czasu weryfikacji użyć Palleti2025 + Rose2020. |
| S.V.V. Machapatri (2020), ResearchGate | Wyszukiwanie nie znalazło pracy o tym tytule ani autorze w żadnym indeksie; rekord ResearchGate niedostępny (403). | Nie cytować (dotyczy NFR-SEC-06/08). Dla JWT Bearer Flow użyć oficjalnej dokumentacji Salesforce (OAuth 2.0 JWT Bearer Flow), po sprawdzeniu jej treści w przeglądarce. |
| Dokumentacja Salesforce: Organization-Wide Sharing Defaults | Strona help.salesforce.com ładuje się dynamicznie i nie zwróciła treści; Security Guide zwrócił HTTP 403. Znane są tylko streszczenia z wyszukiwarki. | Otworzyć ręcznie w przeglądarce i wpisać dosłowny cytat; potrzebne do NFR-SEC-01. |
| Kandydat: „Zero-Trust Access Management for Enterprise Salesforce CRM" (PDF na pdfs.semanticscholar.org/a4cd/66c7c320999a38724e1aae94cea8970663b2.pdf) | Plik PDF nieczytelny dla narzędzi (skompresowane strumienie); autorzy, rok i miejsce publikacji nieustalone. Streszczenie z wyszukiwarki twierdzi, że zastosowanie Zero Trust do SaaS CRM ma „limited academic attention" i mapuje wymiary NIST 800-207, ale tego nie potwierdzono. | Bardzo obiecujące dla luki badawczej w rozdziale. Pobrać PDF lokalnie, ustalić metadane, wtedy dodać wpis. |
| Kandydat: „Exploring Security and Privacy Challenges in Cloud CRM Solutions: An Analytical Study Using Salesforce as a Model" (ResearchGate 384897743) | Rekord istnieje w wynikach wyszukiwania, ale 403, brak autorów, roku, DOI. | Zweryfikować ręcznie. |

## 3. Status luk `[ŹRÓDŁO?]`

W repozytorium nie ma znaczników `[ŹRÓDŁO?]` (przeszukano `docs/`). Poniżej status względem tez rozdziału #82:

- **Definicja Zero Trust:** domknięta (Rose2020), z zastrzeżeniem braku numerów stron.
- **Model współodpowiedzialności Salesforce:** domknięta (Pelkey2026 jako stanowisko producenta; Sheck2024 jako ujęcie ogólne). Brak źródła recenzowanego.
- **Zero Trust w wielodostępnym Salesforce:** częściowo (Palleti2025, tylko abstrakt, niska ranga).
- **Zero Trust w chmurze, przegląd ogólny:** częściowo (Oladimeji2024, preprint).
- **OWD Private / least privilege / sharing (NFR-SEC-01, 02, 07) w oficjalnej dokumentacji Salesforce:** otwarta.
- **Uwierzytelnianie JWT Bearer (NFR-SEC-06, 08):** otwarta (Machapatri niezweryfikowany).
- **Cytat Al Kalach używany w RAPORT.md §3 i §4:** otwarta; cytat niepotwierdzony. Rozważyć usunięcie lub zastąpienie przed wykorzystaniem w pracy.
- **Źródło recenzowane (IEEE/ACM/Springer/Elsevier) dla Zero Trust w CRM/Salesforce:** otwarta. Nie znaleziono żadnego.

Ograniczenie narzędzi: nie dało się odczytać plików PDF ani stron za logowaniem/JS (ResearchGate, help.salesforce.com), dlatego większość wpisów ma poziom „tylko abstrakt".
