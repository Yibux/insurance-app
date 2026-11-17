// SONDA SDM1 — nie scalać. DOM XSS: fragment adresu trafia do innerHTML.
import { LightningElement } from "lwc";

export default class ProbeXss extends LightningElement {
  renderedCallback() {
    const target = this.template.querySelector("div");
    target.innerHTML = decodeURIComponent(window.location.hash.substring(1));
  }
}
