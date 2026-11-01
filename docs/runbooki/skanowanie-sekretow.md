# Skanowanie sekretów (gitleaks)

Dotyczy #19 (FR-CI-05, FR-CI-09, NFR-SEC-05). Dwie linie obrony:

| Gdzie                   | Co skanuje                     | Skutek wykrycia                       |
| ----------------------- | ------------------------------ | ------------------------------------- |
| Hook pre-commit (Husky) | zmiany w stage (`--staged`)    | commit przerwany                      |
| CI, job `gitleaks` w PR | **cała historia** repozytorium | PR zablokowany, alert w code scanning |

CI skanuje całą historię przy każdym PR: repozytorium jest małe (sekundy), a dzięki temu sekret dodany i usunięty w kolejnych commitach też zostanie wykryty. Job zaczyna od autotestu: generuje w locie token-kanarek w formacie GitHub PAT i sprawdza, że gitleaks go wykrywa, więc „zielony” wynik nie oznacza po cichu zepsutego skanera. Kanarek nie trafia do repozytorium.

## Instalacja lokalna

Hook pomija skan z ostrzeżeniem, jeśli gitleaks nie jest zainstalowany (CI i tak go uruchomi):

```bash
winget install --id Gitleaks.Gitleaks
```

Ręczny skan całej historii:

```bash
gitleaks git . --config .gitleaks.toml --redact
```

## Allowlista (`.gitleaks.toml`)

Konfiguracja rozszerza wbudowany zestaw reguł (`useDefault = true`). Obecne wyjątki:

| Wyjątek             | Powód                                                     | Dodano |
| ------------------- | --------------------------------------------------------- | ------ |
| `package-lock.json` | sumy `integrity` wyglądają jak tokeny o wysokiej entropii | #19    |

Zasady dodawania wyjątków:

1. Najpierw upewnić się, że to fałszywy alarm (np. wartość przykładowa, hash, identyfikator publiczny).
2. Preferować najwęższy wyjątek: komentarz `gitleaks:allow` w linii kodu > `regexes` dla konkretnej wartości > `paths` dla całego pliku.
3. Każdy wpis w `.gitleaks.toml` z komentarzem: powód + numer issue/PR; zmiana przechodzi przez review (CODEOWNERS).

## Gdy wykryto prawdziwy sekret

1. **Unieważnić sekret u źródła** (np. rotacja certyfikatu JWT — [runbook](rotacja-certyfikatu-jwt.md)). Usunięcie z kodu nie wystarcza: sekret pozostaje w historii i w forkach.
2. Usunąć sekret z kodu i przenieść go do GitHub Environment secrets.
3. Jeśli sekret trafił na `main`: przepisać historię (`git filter-repo`) dopiero po unieważnieniu, a fakt odnotować w dzienniku implementacji.
