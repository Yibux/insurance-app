/**
 * SONDA SDM1 — nie scalać. Celowo podatna klasa: jawne przełączenia w tryb
 * systemowy, które od API 67.0 są jedyną drogą obejścia CRUD/FLS/sharingu.
 */
public with sharing class ProbeSystemMode {
  public static List<Account> soqlSystemMode() {
    return [SELECT Id, Name FROM Account WITH SYSTEM_MODE LIMIT 10];
  }

  public static List<Account> dynamicSystemMode(String name) {
    return Database.query(
      'SELECT Id FROM Account WHERE Name = :name',
      AccessLevel.SYSTEM_MODE
    );
  }

  public static Id dmlAsSystem(String name) {
    Account acc = new Account(Name = name);
    insert as system acc;
    return acc.Id;
  }
}
