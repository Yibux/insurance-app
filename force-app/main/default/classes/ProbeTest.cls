@isTest
private class ProbeTest {
  @isTest
  static void addsNumbers() {
    Assert.areEqual(3, Probe.add(1, 2));
  }
}
