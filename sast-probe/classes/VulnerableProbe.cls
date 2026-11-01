public without sharing class VulnerableProbe {
  public static List<Account> findByName(String name) {
    return Database.query(
      'SELECT Id FROM Account WHERE Name = \'' + name + '\''
    );
  }

  public static void rename(Id accountId, String newName) {
    update new Account(Id = accountId, Name = newName);
  }
}
