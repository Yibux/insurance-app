# Literatura do rozdziału: DevSecOps i CI/CD (#83)

Notatka źródłowa do zadania [#83](https://github.com/Yibux/insurance-app/issues/83). Wpisy są w formacie z `.claude/AGENT_RULES.md` (klucz, opis, teza, cytat, weryfikacja). Data dostępu dla wszystkich wpisów: 2026-11-08. Wzorzec: [82-zero-trust-crm.md](82-zero-trust-crm.md).

Legenda pola **Weryfikacja:** „pełny tekst" (otwarto i przeczytano całość), „tylko abstrakt/strona" (otwarto stronę opisową lub abstrakt), „tylko metadane" (potwierdzono istnienie i dane bibliograficzne w Crossref/OpenAlex, bez treści), „nie zweryfikowano".

Powiązane wymagania: FR-CI-03, FR-CI-04, FR-CI-06, FR-CI-09, NFR-SEC-05, NFR-SEC-06, NFR-PERF-01, NFR-MNT-04. Zob. [WYMAGANIA.md](../WYMAGANIA.md) (macierz śledzenia) i [potok-cicd.md](../architektura/potok-cicd.md).

Ograniczenie narzędzi: nie dało się odczytać plików PDF (IEEE Xplore zwraca HTTP 418, PDF-y są skompresowane, brak `pdftoppm`) ani stron ResearchGate (HTTP 403). Dlatego większość pozycji ma poziom „tylko abstrakt". **Żadnej pozycji nie przeczytano w pełnym tekście.**

## 1. Podsumowanie weryfikacji siedmiu źródeł planowanych

| Źródło z RAPORT.md | Status | Najważniejsza uwaga |
| --- | --- | --- |
| Cheenepalli i in. 2025 | zweryfikowane (abstrakt) | Liczby 405 / 73% / 12% potwierdzone w abstrakcie arXiv. Praca ma też wersję konferencyjną IEEE ISDFS 2025. |
| IEEE 2025 SLR | zweryfikowane (abstrakt), **autorzy nieznani w RAPORT.md** | To Bautista Ramos i Yoo, IEEE Access vol. 13; „62 artykuły z lat 2016-2025" i lista zagrożeń potwierdzone. |
| IEEE/ACM 2022 | zweryfikowane **z błędem w cytacie** | Praca istnieje (Wang i in., ICPC 2022), ale cytat mówi o „30 fixed/confirmed", a abstrakt podaje **24**. Cytatu nie używać. |
| Lakade 2025 | zweryfikowane częściowo | Praca istnieje (JICRCR, 2025). Fraza „zero-touch approach fundamentally reduces attack surfaces" potwierdzona; **OIDC nie występuje** na stronie artykułu. |
| Shift Left 2025 | zweryfikowane częściowo | Autorzy: Malik i Prashasti, ESISCS 2025. **Cytat z RAPORT.md nie występuje** w opisie na stronie czasopisma. |
| Jammeh 2020 | częściowo | Autor i tytuł potwierdzone (ResearchGate, kopia w ISTQB); cytat potwierdzony tylko przez fragmenty wyszukiwarki. Brak recenzowanego wydawcy. |
| Bavadiya 2022 | **słabe, nie zweryfikowano** | Rok 2022 podejrzany (PDF utworzony we wrześniu 2025, ID ResearchGate z 2025). Liczby 93,64% i cytatu nie znaleziono. Opis w RAPORT.md („matematycznie udowadnia") nie jest poparty. |

## 2. Źródła zweryfikowane

### Cheenepalli2025 (konferencja IEEE; preprint arXiv)

- **Klucz:** Cheenepalli2025
- **Opis bibliograficzny:** Cheenepalli J., Hastings J. D., Ahmed K. M., Fenner C., _Advancing DevSecOps in SMEs: Challenges and Best Practices for Secure CI/CD Pipelines_, 2025 IEEE 13th International Symposium on Digital Forensics and Security (ISDFS), 2025, DOI: 10.1109/ISDFS65363.2025.11011960 (wersja konferencyjna wskazana w rekordzie arXiv; nie otwierano strony IEEE); preprint: arXiv:2503.22612, DOI: 10.48550/arXiv.2503.22612, https://arxiv.org/abs/2503.22612 (dostęp: 2026-11-08)
- **Wspiera tezę:** Luka między deklarowanym priorytetem bezpieczeństwa a automatyzacją skanów w CI/CD w MŚP, uzasadniająca skan przy każdym PR/commicie (FR-CI-06, NFR-PERF-01).
- **Cytat (opcjonalnie):** „only 12% of organizations conducting security scans per commit" (abstrakt). Abstrakt zawiera też „strong leadership prioritization of security (73%)" i dane od 405 specjalistów MŚP. Pełny cytat z RAPORT.md (zdanie z „Despite ... persist") jest zgodny co do liczb; nie sprawdzono dosłowności całego zdania.
- **Weryfikacja:** tylko abstrakt (strona arXiv). Uwaga: w abstrakcie 68% respondentów wdrożyło DevSecOps; badanie dotyczy MŚP, nie dużych organizacji. Cytować wersję konferencyjną IEEE (po potwierdzeniu strony), nie sam preprint.

### BautistaRamos2025 (czasopismo IEEE Access; „IEEE 2025 SLR")

- **Klucz:** BautistaRamos2025
- **Opis bibliograficzny:** Bautista Ramos R. C., Yoo S. G., _Cybersecurity in DevOps Environments: A Systematic Literature Review_, IEEE Access, vol. 13, s. 191959-191979, 2025, DOI: 10.1109/ACCESS.2025.3582892, https://ieeexplore.ieee.org/document/11050425 (dostęp: 2026-11-08)
- **Wspiera tezę:** Najczęstsze zagrożenia w DevOps (niekontrolowana automatyzacja, ujawnienie sekretów w CI/CD, ataki na łańcuch dostaw) i środki zaradcze (SAST/DAST/IAST, walidacja IaC, magazyny sekretów); uzasadnia NFR-SEC-05 oraz przypięcie akcji i skan sekretów.
- **Cytat (opcjonalnie):** „62 peer-reviewed articles published between 2016 and 2025" (abstrakt, odtworzony z OpenAlex). Sformułowanie z RAPORT.md „most significant threats are related to uncontrolled automation, exposure of sensitive secrets in CI/CD pipelines, lack of mutual authentication ... supply chain attacks" występuje w abstrakcie dosłownie.
- **Weryfikacja:** tylko abstrakt (OpenAlex i Crossref; strona IEEE i PDF niedostępne). Powiązanie numeru dokumentu 11050425 z DOI potwierdza Crossref. Numeru strony cytatu brak. Abstrakt zaznacza, że większość badanych prac nie ma porównawczej walidacji empirycznej. Autorzy brakowali w RAPORT.md; dopisać.

### Wang2022 (konferencja IEEE/ACM ICPC; „IEEE/ACM 2022")

- **Klucz:** Wang2022
- **Opis bibliograficzny:** Wang J., Huang Y., Wang S., Wang Q., _Find Bugs in Static Bug Finders_, Proceedings of the 30th IEEE/ACM International Conference on Program Comprehension (ICPC '22), 2022, DOI: 10.1145/3524610.3527899 (dostęp: 2026-11-08). Preprint: _An Approach to Detecting Bugs in Pattern-Based Bug Detectors_, arXiv:2109.02245 (v2, 2021).
- **Wspiera tezę:** Reguły analizatorów statycznych (SonarQube, PMD, SpotBugs, ErrorProne) same zawierają błędy, więc wynik SAST wymaga weryfikacji (eksperyment wykrywalności w M6, doboru reguł PMD).
- **Cytat (opcjonalnie):** „reveals 46 bugs in the static bug finders, among which 24 are fixed or confirmed" (abstrakt na stronie ICPC 2022, researchr). **Cytat z RAPORT.md („30 are fixed/confirmed and the left are awaiting confirmation") nie zgadza się**: źródła podają 24 poprawione lub potwierdzone (ok. 38 błędów typu fałszywie ujemny i 8 fałszywie dodatnich wg streszczenia wyszukiwarki). Używać 46 i 24.
- **Weryfikacja:** tylko abstrakt (strona ICPC, arXiv, metadane Crossref). Plik PDF IEEE (`09796187.pdf` z RAPORT.md) nie został otwarty (HTTP 418), więc to, że wskazuje właśnie na tę pracę, jest wnioskiem (zgodny zakres numeracji ICPC 2022), a nie potwierdzeniem. Uwaga: narzędzia badane to narzędzia Java, nie Apex PMD; wniosek dotyczy narzędzi SAST ogólnie.

### Lakade2025 (czasopismo; ranga niska)

- **Klucz:** Lakade2025
- **Opis bibliograficzny:** Lakade S., _Zero-Touch Secrets Management: Securing CI/CD Pipelines Through Ephemeral Credentials_, Journal of International Crisis and Risk Communication Research, vol. 8, nr S12, s. 499-509, 2025 (publikacja 2025-12-02), DOI: 10.63278/jicrcr.vi.3601, https://jicrcr.com/index.php/jicrcr/article/view/3601 (dostęp: 2026-11-08)
- **Wspiera tezę:** Krótko żyjące poświadczenia związane z tożsamością zamiast trwałych sekretów w CI/CD (NFR-SEC-05, NFR-SEC-06; decyzja o JWT Bearer i GitHub Environments).
- **Cytat (opcjonalnie):** „The zero-touch approach fundamentally reduces attack surfaces" (abstrakt, fragment).
- **Weryfikacja:** tylko abstrakt. Czasopismo (kryzysy i komunikacja ryzyka) jest tematycznie odległe od inżynierii oprogramowania, a numer specjalny S12 to sygnał ostrożności; recenzji nie potwierdzono. Opis w RAPORT.md mówi o OIDC i „kilkuminutowych" poświadczeniach: **OIDC nie występuje na stronie artykułu**, więc nie przypisywać tej pracy OIDC. Pełne zdanie z RAPORT.md („...by ensuring credentials exist only during active use...") nie zostało potwierdzone.

### MalikPrashasti2025 (czasopismo; „Shift Left 2025")

- **Klucz:** MalikPrashasti2025
- **Opis bibliograficzny:** Malik G., Prashasti, _Shift Left Security_, The Eastasouth Journal of Information System and Computer Science, vol. 2, nr 03, s. 219-245, 2025-04-30, DOI: 10.58812/esiscs.v2i03.528, https://esj.eastasouth-institute.com/index.php/esiscs/article/view/528 (dostęp: 2026-11-08)
- **Wspiera tezę:** Definicja i uzasadnienie shift-left: przeniesienie testów bezpieczeństwa na wczesne fazy SDLC, ciągłe testy i szybkie pętle zwrotne (FR-CI-09, husky pre-commit).
- **Cytat (opcjonalnie):** brak. Cytat z RAPORT.md („Shift Left Security is a means for security in the SDLC ...") **nie występuje** w opisie na stronie czasopisma; nie wykluczono, że jest w pełnym tekście.
- **Weryfikacja:** tylko abstrakt/strona. Utożsamienie z rekordem ResearchGate 394857544 jest prawdopodobne (ten sam tytuł, kwiecień 2025, wyszukiwarka wiąże go z profilem Malika), ale nie potwierdzone (ResearchGate 403). Mało znane czasopismo, ranga niska; traktować jako ilustrację pojęcia, nie dowód skuteczności.

### Jammeh2020 (praca niezależna; ranga niska)

- **Klucz:** Jammeh2020
- **Opis bibliograficzny:** Jammeh B., _DevSecOps: Security Expertise a Key to Automated Testing in CI/CD Pipeline_, Bournemouth University, grudzień 2020, https://www.researchgate.net/publication/347441415 (dostęp: 2026-11-08). Brak DOI i wydawcy w znalezionych metadanych; kopia PDF: https://www.istqb.org/wp-content/uploads/2025/06/DevSecOps.pdf (nie dało się odczytać).
- **Wspiera tezę:** Wiedza o bezpieczeństwie i odpowiedzialność członków zespołu to warunek skutecznego testowania bezpieczeństwa w CI/CD (szablon PR, checklisty; NFR-MNT-04).
- **Cytat (opcjonalnie):** „access to security knowledge and expertise is key in DevSecOps, and every team member must understand their security responsibilities" (fragment abstraktu widoczny w wynikach wyszukiwania; nie otwarto samego dokumentu).
- **Weryfikacja:** nie zweryfikowano treści dokumentu. Autor, tytuł i data potwierdzone tylko przez wyniki wyszukiwania (ResearchGate, Scribd, ISTQB). Nie wiadomo, czy to recenzowana publikacja (prawdopodobnie raport studencki/preprint). Do pracy dyplomowej cytować ostrożnie lub zastąpić (sekcja 4).

## 3. Źródło, którego NIE udało się zweryfikować

### Bavadiya2022 (słabe)

- **Klucz:** Bavadiya2022
- **Opis bibliograficzny:** Bavadiya P., _DevSecOps: Automating Security Vulnerability Detection and Response in CI/CD Pipelines_, deklarowane: Journal of Information Systems Engineering and Management (JISEM), 11.2022; https://www.researchgate.net/publication/395472364 (dostęp: 2026-11-08). Brak DOI.
- **Wspiera tezę:** (jeśli potwierdzone) automatyzacja kontroli bezpieczeństwa w potoku zmniejsza ryzyko po wdrożeniu; bramki jakości jako uzasadnienie FR-CI-03, FR-CI-04.
- **Cytat (opcjonalnie):** brak.
- **Weryfikacja:** nie zweryfikowano. Powody: (1) ResearchGate (403), a PDF czasopisma (`jisem-journal.com/download/11_JISEM-nov-2022.pdf`, 7 stron) jest nieczytelny dla narzędzi; (2) metadane PDF wskazują utworzenie 2025-09-10, a ID ResearchGate pochodzi z 2025, co kłóci się z rokiem 2022; (3) strona główna JISEM nie wymienia autora ani numeru z listopada 2022, a rocznik 2022 to vol. 7; (4) liczba **93,64%** i cytat z RAPORT.md nie zostały znalezione w żadnym indeksie; (5) wyszukiwarka opisuje pracę jako studium przypadku/symulację 110 buildów, a nie „matematyczny dowód". Nie cytować liczby 93,64% ani nazwiska w tezie, dopóki użytkownik nie otworzy PDF-a i nie potwierdzi roku, wydawcy i liczb. Wzmianki w `potok-cicd.md` i `M1-potok-devsecops.md` do rewizji (poza zakresem tej notatki).

## 4. Propozycje zamienników i uzupełnień (zweryfikowane)

### Rajapakse2022 (czasopismo Elsevier, recenzowane)

- **Klucz:** Rajapakse2022
- **Opis bibliograficzny:** Rajapakse R. N., Zahedi M., Babar M. A., Shen H., _Challenges and solutions when adopting DevSecOps: A systematic review_, Information and Software Technology, vol. 141, art. 106700, 2022, DOI: 10.1016/j.infsof.2021.106700; preprint arXiv:2103.08266 (dostęp: 2026-11-08)
- **Wspiera tezę:** Recenzowany przegląd 54 badań o wyzwaniach i rozwiązaniach wdrażania DevSecOps; zamiennik dla Jammeha (czynnik ludzki, wiedza) i uzupełnienie Bavadiyi (bramki, automatyzacja).
- **Cytat (opcjonalnie):** brak.
- **Weryfikacja:** tylko abstrakt (strona arXiv: tytuł, autorzy, czasopismo, DOI, 54 badania).

### Chandramouli2024 (norma NIST)

- **Klucz:** Chandramouli2024
- **Opis bibliograficzny:** Chandramouli R., Kautz F., Torres-Arias S., _Strategies for the Integration of Software Supply Chain Security in DevSecOps CI/CD Pipelines_, NIST SP 800-204D, luty 2024, DOI: 10.6028/NIST.SP.800-204D, https://csrc.nist.gov/pubs/sp/800/204/d/final (dostęp: 2026-11-08)
- **Wspiera tezę:** Oficjalne zalecenia dla kontroli łańcucha dostaw w potokach CI/CD (przypinanie zależności i akcji, SCA); zamiennik/uzupełnienie dla Lakade i SLR w zakresie NFR-SEC-05.
- **Cytat (opcjonalnie):** brak.
- **Weryfikacja:** tylko abstrakt (strona CSRC: tytuł, autorzy, data, DOI). Treści dokumentu nie czytano.

### OWASP2022 (dokumentacja organizacji)

- **Klucz:** OWASP2022
- **Opis bibliograficzny:** Gil O., Segal O., Krivelevich D., _OWASP Top 10 CI/CD Security Risks_, OWASP Lab Project, https://owasp.org/www-project-top-10-ci-cd-security-risks/ (dostęp: 2026-11-08). Rok wydania na stronie nie podany, nie ustalono.
- **Wspiera tezę:** Katalog ryzyk potoku CI/CD, m.in. CICD-SEC-4 Poisoned Pipeline Execution, CICD-SEC-6 Insufficient Credential Hygiene, CICD-SEC-3 Dependency Chain Abuse; mapowanie bramek (gitleaks, SCA, przypięte akcje) na ryzyka.
- **Cytat (opcjonalnie):** brak.
- **Weryfikacja:** tylko strona projektu (lista 10 ryzyk potwierdzona). Projekt Lab, nie standard; rok i wersja do ustalenia.

### Rangnau2020 (konferencja IEEE; kandydat)

- **Klucz:** Rangnau2020
- **Opis bibliograficzny:** Rangnau T., van Buijtenen R., Fransen F., Türkmen F., _Continuous Security Testing: A Case Study on Integrating Dynamic Security Testing Tools in CI/CD Pipelines_, IEEE 24th International Enterprise Distributed Object Computing Conference (EDOC), 2020, DOI: 10.1109/EDOC49727.2020.00026 (dostęp: 2026-11-08)
- **Wspiera tezę:** (hipoteza) studium przypadku integracji testów bezpieczeństwa w CI/CD; kandydat na zamiennik dla Jammeha (pytanie o realizm automatyzacji w zespołach).
- **Cytat (opcjonalnie):** brak.
- **Weryfikacja:** tylko metadane (OpenAlex). Abstraktu nie czytano; przed użyciem sprawdzić, czy treść wspiera tezę.

## 5. Status luk `[ŹRÓDŁO?]`

W repozytorium nie ma znaczników `[ŹRÓDŁO?]` (przeszukano `docs/`). Status względem tez rozdziału #83:

- **Luka automatyzacji skanów (73% / 12%, FR-CI-06):** domknięta (Cheenepalli2025, abstrakt).
- **Zagrożenia i środki w DevSecOps, sekrety i łańcuch dostaw (NFR-SEC-05):** domknięta (BautistaRamos2025, abstrakt; uzupełnienie Chandramouli2024, OWASP2022).
- **Zawodność reguł SAST (M6):** domknięta po poprawce liczb (Wang2022: 46 błędów, 24 potwierdzone).
- **Krótko żyjące poświadczenia (NFR-SEC-05/06):** częściowo (Lakade2025, ranga niska, bez potwierdzenia OIDC). Dla OIDC/JWT w GitHub Actions potrzebna dokumentacja GitHub (GitHub Docs, „OpenID Connect"), której tu nie sprawdzano: **otwarta**.
- **Definicja i wartość shift-left (FR-CI-09):** częściowo (MalikPrashasti2025, ranga niska, cytat niepotwierdzony).
- **Czynnik ludzki (NFR-MNT-04):** częściowo (Jammeh2020 niezweryfikowany; zamiennik Rajapakse2022).
- **Skuteczność bramek jakości w liczbach (FR-CI-03/04, NFR-PERF-01; 93,64%):** **otwarta**. Bavadiya2022 niezweryfikowany; brak zweryfikowanego zamiennika z taką liczbą.
- **Cytaty w RAPORT.md do poprawy przed użyciem w pracy:** IEEE/ACM 2022 (24, nie 30), Shift Left (cytat nieznaleziony), Lakade (OIDC), Bavadiya (liczby, rok).
