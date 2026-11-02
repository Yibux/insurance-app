# Spike: Salesforce Connect (OData 4.0) w DE i scratch orgu

- **Issue:** #9 · **Data:** 2026-10-29 · **Wymagania:** FR-EXT-02
- **Werdykt:** **GO**, bez obejść: Salesforce Connect z adapterem OData 4.0 działa w Developer Edition i w scratch orgach z naszego Dev Huba, bez dodatkowych features w definicji scratch orga.

## Pytanie

Czy External Objects (Salesforce Connect, adapter OData 4.0) są dostępne w Developer Edition i w scratch orgach tworzonych w CI, tak aby w M5 wystawić dane z backendu FastAPI jako obiekty `__x` bez ich przechowywania w CRM? Było to największe ryzyko w [HARMONOGRAM.md](../HARMONOGRAM.md).

## Co sprawdzono

Metadane testowe w formacie Metadata API: [`spikes/salesforce-connect-odata/`](../../spikes/salesforce-connect-odata/):

- `ExternalDataSource` `Northwind` — typ `OData4`, publiczny serwis `https://services.odata.org/V4/Northwind/Northwind.svc`, bez uwierzytelniania, tylko odczyt;
- obiekt zewnętrzny `Customers__x` z polami `CompanyName__c`, `City__c` (mapowanie przez `externalDeveloperName`);
- permission set `Northwind_Spike` (odczyt obiektu i pól).

| Krok                                                                                     | Wynik                                                                       |
| ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Walidacja w Dev Hubie DE: `sf project deploy start -o devhub --metadata-dir … --dry-run` | Succeeded (bez zmian w orgu)                                                |
| Deploy do scratch orga z obecnej `config/project-scratch-def.json`                       | Succeeded                                                                   |
| `SELECT ExternalId, CompanyName__c, City__c FROM Customers__x WHERE City__c = 'London'`  | 5 rekordów pobranych na żywo z serwisu OData (np. `AROUT`, Around the Horn) |
| Limity (`sf org list limits`), DE i scratch                                              | `HourlyODataCallout`: 1000/h                                                |

Odtworzenie:

```bash
sf org create scratch -f config/project-scratch-def.json -a spike-odata -y 1
sf project deploy start -o spike-odata --metadata-dir spikes/salesforce-connect-odata
sf org assign permset -o spike-odata -n Northwind_Spike
sf data query -o spike-odata -q "SELECT ExternalId, CompanyName__c, City__c FROM Customers__x LIMIT 5"
```

## Problemy

| Problem                                                                 | Rozwiązanie                                                                                                               |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Pole obiektu zewnętrznego z elementem `externalName` → błąd parsowania. | W `CustomField` nazwa kolumny źródła to `externalDeveloperName` (`externalName` jest tylko na poziomie obiektu).          |
| Po deployu `No such column 'CompanyName__c'`.                           | Deploy metadanych nie nadaje FLS — potrzebny permission set. To zgodne z modelem M2 (dostęp tylko przez permission sety). |

## Wnioski i wpływ na backlog

- **M5 (#External Objects):** plan bez zmian — endpoint OData 4.0 w FastAPI + `ExternalDataSource` w metadanych. Zamiast `NoAuthentication` użyjemy **Named Credential + External Credential**, a endpoint musi być publiczny po HTTPS (hosting do wyboru w M5).
- Limit 1000 wywołań OData na godzinę wystarcza dla demo i eksperymentu; listy w portalu powinny stronicować i filtrować po stronie serwera (`pagination: SERVER`), żeby nie mnożyć wywołań.
- **CI (#16):** obiekty zewnętrzne można wdrażać do scratch orga per PR jak każde inne metadane. Testy Apex nie wykonują wywołań OData (callouty w testach są zablokowane) — w testach trzeba będzie mockować dostęp do `__x` (np. warstwa selektora wstrzykiwana w testach).
- Do sprawdzenia w M3/M5: widoczność obiektów zewnętrznych dla użytkowników portalu Experience Cloud (licencja użytkowników społeczności, permission set dla profilu portalu).
- **Fallback** (gdyby w przyszłości Salesforce Connect przestał być dostępny w DE): Apex callout przez Named Credential do REST API FastAPI + LWC wyświetlające dane bez zapisu w CRM. Nie jest potrzebny na tym etapie.
