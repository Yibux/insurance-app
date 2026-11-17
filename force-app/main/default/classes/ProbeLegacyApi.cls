/**
 * SONDA SDM1 — nie scalać. Klasa bez deklaracji sharingu zapisana w API 66.0:
 * w tej wersji domyślnym trybem jest nadal tryb systemowy.
 */
public class ProbeLegacyApi {
  public static List<Account> readAll() {
    return [SELECT Id, Name FROM Account LIMIT 10];
  }

  public static void rename(Id accountId, String name) {
    update new Account(Id = accountId, Name = name);
  }
}
