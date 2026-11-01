public with sharing class Probe {
  public static Integer add(Integer a, Integer b) {
    return a + b;
  }
  public static Integer neverCalled(Integer a) {
    Integer x = a * 2;
    return x;
  }
}
