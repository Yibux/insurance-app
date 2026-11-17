/**
 * SONDA SDM1 — nie scalać. Test tylko po to, by bramka pokrycia nie
 * zasłaniała wyniku deployu klas sondy.
 */
@IsTest
private class ProbeSondyTest {
  @IsTest
  static void coversProbes() {
    Id accId = ProbeSystemMode.dmlAsSystem('Sonda');
    Assert.areEqual(1, ProbeSystemMode.soqlSystemMode().size());
    Assert.areEqual(1, ProbeSystemMode.dynamicSystemMode('Sonda').size());
    ProbeLegacyApi.rename(accId, 'Sonda 2');
    Assert.areEqual('Sonda 2', ProbeLegacyApi.readAll()[0].Name);
  }
}
