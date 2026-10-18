# Backlog

> Plik generowany przez `scripts/github/create-backlog.mjs` z `scripts/github/backlog.json` — nie edytować ręcznie.
> Status zadań: [GitHub Project](https://github.com/users/Yibux/projects/3) · Konwencje: [KONWENCJE.md](KONWENCJE.md) · Wymagania: [WYMAGANIA.md](WYMAGANIA.md)

## M0 Foundation (2026-10-12 → 2026-10-25) — [#2](https://github.com/Yibux/insurance-app/issues/2)

Prepare Dev Hub, repository rules, JWT credentials and de-risk Experience Cloud and Salesforce Connect before building anything.

| Issue                                                   | Zadanie                                                                         | Typ    | Prio | Rozmiar | Start      | Termin     | Wymagania              |
| ------------------------------------------------------- | ------------------------------------------------------------------------------- | ------ | ---- | ------- | ---------- | ---------- | ---------------------- |
| [#3](https://github.com/Yibux/insurance-app/issues/3)   | Sign up Developer Edition org and enable Dev Hub                                | chore  | P1   | S       | 2026-10-12 | 2026-10-13 | NFR-MNT-01             |
| [#4](https://github.com/Yibux/insurance-app/issues/4)   | Merge SFDX scaffold into main and verify local setup from README                | chore  | P1   | S       | 2026-10-13 | 2026-10-14 | NFR-MNT-05             |
| [#5](https://github.com/Yibux/insurance-app/issues/5)   | Add repository conventions, issue/PR templates and CODEOWNERS                   | docs   | P1   | S       | 2026-10-14 | 2026-10-15 | NFR-MNT-03, NFR-MNT-04 |
| [#6](https://github.com/Yibux/insurance-app/issues/6)   | Configure branch protection on main                                             | chore  | P1   | S       | 2026-10-15 | 2026-10-15 | NFR-SEC-11             |
| [#7](https://github.com/Yibux/insurance-app/issues/7)   | Create External Client App with JWT certificate for CI                          | chore  | P1   | M       | 2026-10-16 | 2026-10-19 | NFR-SEC-05, NFR-SEC-06 |
| [#8](https://github.com/Yibux/insurance-app/issues/8)   | Spike: Experience Cloud LWR site in a scratch org                               | spike  | P1   | M       | 2026-10-19 | 2026-10-21 | FR-PRT-01              |
| [#9](https://github.com/Yibux/insurance-app/issues/9)   | Spike: Salesforce Connect OData 4.0 availability in DE/scratch                  | spike  | P1   | M       | 2026-10-21 | 2026-10-23 | FR-EXT-02              |
| [#10](https://github.com/Yibux/insurance-app/issues/10) | ADR-001 monorepo and ADR-002 custom objects instead of Financial Services Cloud | docs   | P2   | S       | 2026-10-23 | 2026-10-24 | NFR-MNT-03             |
| [#11](https://github.com/Yibux/insurance-app/issues/11) | Review requirements specification with supervisor                               | docs   | P1   | S       | 2026-10-20 | 2026-10-25 | —                      |
| [#12](https://github.com/Yibux/insurance-app/issues/12) | Agree thesis outline (table of contents) with supervisor                        | thesis | P1   | S       | 2026-10-20 | 2026-10-25 | —                      |

## M1 DevSecOps pipeline (2026-10-26 → 2026-12-06) — [#13](https://github.com/Yibux/insurance-app/issues/13)

Every pull request is validated in an ephemeral scratch org with tests, SAST, secret and dependency scanning before any business logic is written.

| Issue                                                   | Zadanie                                                            | Typ      | Prio | Rozmiar | Start      | Termin     | Wymagania                                  |
| ------------------------------------------------------- | ------------------------------------------------------------------ | -------- | ---- | ------- | ---------- | ---------- | ------------------------------------------ |
| [#14](https://github.com/Yibux/insurance-app/issues/14) | Create pr-validation workflow: lint, Prettier check and LWC Jest   | feature  | P1   | S       | 2026-10-26 | 2026-10-27 | FR-CI-01, NFR-QA-04                        |
| [#15](https://github.com/Yibux/insurance-app/issues/15) | Authenticate CI to Dev Hub with JWT Bearer Flow                    | feature  | P1   | S       | 2026-10-28 | 2026-10-29 | NFR-SEC-05, NFR-SEC-06                     |
| [#16](https://github.com/Yibux/insurance-app/issues/16) | Create, deploy to and always delete a scratch org per PR           | feature  | P1   | M       | 2026-10-29 | 2026-11-03 | FR-CI-02, NFR-PERF-05                      |
| [#17](https://github.com/Yibux/insurance-app/issues/17) | Run Apex tests and enforce 75% coverage gate (check_coverage.py)   | feature  | P1   | M       | 2026-11-03 | 2026-11-06 | FR-CI-03, NFR-QA-01                        |
| [#18](https://github.com/Yibux/insurance-app/issues/18) | Integrate Salesforce Code Analyzer v5 with severity gate and SARIF | feature  | P1   | M       | 2026-11-09 | 2026-11-12 | FR-CI-04, FR-CI-07, NFR-SEC-03, NFR-SEC-04 |
| [#19](https://github.com/Yibux/insurance-app/issues/19) | Add gitleaks secret scanning in CI and pre-commit                  | feature  | P1   | S       | 2026-11-12 | 2026-11-13 | FR-CI-05, FR-CI-09, NFR-SEC-05             |
| [#20](https://github.com/Yibux/insurance-app/issues/20) | Add CodeQL workflow for JavaScript                                 | feature  | P2   | S       | 2026-11-16 | 2026-11-16 | FR-CI-06                                   |
| [#21](https://github.com/Yibux/insurance-app/issues/21) | Configure Dependabot and npm audit gate                            | feature  | P2   | S       | 2026-11-17 | 2026-11-17 | FR-CI-05                                   |
| [#22](https://github.com/Yibux/insurance-app/issues/22) | Publish test and scan reports as PR job summary and artifacts      | feature  | P2   | M       | 2026-11-18 | 2026-11-20 | FR-CI-07, NFR-OBS-02                       |
| [#23](https://github.com/Yibux/insurance-app/issues/23) | Review Husky and lint-staged pre-commit hooks                      | chore    | P3   | S       | 2026-11-23 | 2026-11-23 | FR-CI-09                                   |
| [#24](https://github.com/Yibux/insurance-app/issues/24) | Create deploy workflow to target org with environment approval     | feature  | P1   | M       | 2026-11-24 | 2026-11-27 | FR-CI-08, NFR-SEC-06                       |
| [#25](https://github.com/Yibux/insurance-app/issues/25) | Update branch protection with required pipeline checks             | chore    | P1   | S       | 2026-11-30 | 2026-11-30 | NFR-SEC-11                                 |
| [#26](https://github.com/Yibux/insurance-app/issues/26) | Measure baseline pipeline duration                                 | research | P2   | S       | 2026-12-01 | 2026-12-02 | NFR-PERF-01                                |
| [#27](https://github.com/Yibux/insurance-app/issues/27) | Document the pipeline and write ADR GitHub Actions vs Copado       | docs     | P1   | M       | 2026-12-02 | 2026-12-06 | NFR-MNT-03                                 |

## M2 Data model & security (2026-12-07 → 2027-01-31) — [#28](https://github.com/Yibux/insurance-app/issues/28)

Implement the insurance data model and a Zero-Trust access model with layered Apex code and ≥ 85% coverage.

| Issue                                                   | Zadanie                                                                             | Typ     | Prio | Rozmiar | Start      | Termin     | Wymagania                                     |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------- | ---- | ------- | ---------- | ---------- | --------------------------------------------- |
| [#29](https://github.com/Yibux/insurance-app/issues/29) | Design data model (ERD) and document it                                             | docs    | P1   | S       | 2026-12-07 | 2026-12-08 | FR-POL-01, FR-CLM-01, NFR-CMP-03              |
| [#30](https://github.com/Yibux/insurance-app/issues/30) | Create Policy__c and Coverage__c objects with fields and validation rules           | feature | P1   | M       | 2026-12-08 | 2026-12-11 | FR-POL-01, FR-POL-02, FR-POL-03               |
| [#31](https://github.com/Yibux/insurance-app/issues/31) | Create Claim__c and Claim_Document__c objects with field history                    | feature | P1   | M       | 2026-12-14 | 2026-12-17 | FR-CLM-01, FR-CLM-03, FR-CLM-06               |
| [#32](https://github.com/Yibux/insurance-app/issues/32) | Set OWD Private and sharing rules                                                   | feature | P1   | S       | 2026-12-18 | 2026-12-18 | NFR-SEC-01, FR-POL-04                         |
| [#33](https://github.com/Yibux/insurance-app/issues/33) | Create permission sets and permission set groups (Agent, Claims Adjuster, Customer) | feature | P1   | M       | 2026-12-21 | 2026-12-23 | NFR-SEC-02                                    |
| [#34](https://github.com/Yibux/insurance-app/issues/34) | Implement Apex selector layer with WITH USER_MODE                                   | feature | P1   | M       | 2027-01-04 | 2027-01-06 | NFR-SEC-03, NFR-SEC-04, NFR-MNT-02            |
| [#35](https://github.com/Yibux/insurance-app/issues/35) | Implement PolicyService and ClaimService                                            | feature | P1   | L       | 2027-01-07 | 2027-01-12 | FR-CLM-01, FR-CLM-05, NFR-SEC-03, NFR-PERF-02 |
| [#36](https://github.com/Yibux/insurance-app/issues/36) | Add trigger framework and claim status transition handler                           | feature | P1   | M       | 2027-01-13 | 2027-01-15 | FR-CLM-02, NFR-MNT-02, NFR-PERF-02            |
| [#37](https://github.com/Yibux/insurance-app/issues/37) | Auto-assign new claims to adjusters                                                 | feature | P2   | S       | 2027-01-18 | 2027-01-19 | FR-CLM-04                                     |
| [#38](https://github.com/Yibux/insurance-app/issues/38) | Schedule automatic policy expiry                                                    | feature | P3   | S       | 2027-01-19 | 2027-01-20 | FR-POL-05                                     |
| [#39](https://github.com/Yibux/insurance-app/issues/39) | Add Apex error logging utility                                                      | feature | P3   | S       | 2027-01-20 | 2027-01-20 | NFR-OBS-03                                    |
| [#40](https://github.com/Yibux/insurance-app/issues/40) | Add Restriction Rules for sensitive records                                         | feature | P2   | S       | 2027-01-20 | 2027-01-21 | NFR-SEC-01, NFR-SEC-07                        |
| [#41](https://github.com/Yibux/insurance-app/issues/41) | Create test data factory and sample data plans                                      | feature | P1   | M       | 2027-01-21 | 2027-01-25 | NFR-QA-05, NFR-CMP-02                         |
| [#42](https://github.com/Yibux/insurance-app/issues/42) | Write security tests with System.runAs and reach ≥ 85% coverage                     | feature | P1   | M       | 2027-01-25 | 2027-01-28 | NFR-QA-01, NFR-SEC-01, NFR-SEC-03             |
| [#43](https://github.com/Yibux/insurance-app/issues/43) | Build Lightning app, layouts and record pages for agents and adjusters              | feature | P2   | M       | 2027-01-28 | 2027-01-31 | FR-POL-04, FR-COM-02                          |

## M3 Experience Cloud portal (2027-02-01 → 2027-03-14) — [#44](https://github.com/Yibux/insurance-app/issues/44)

Secure LWR portal where insured customers see their policies, submit claims and talk to their agent.

| Issue                                                   | Zadanie                                                         | Typ     | Prio | Rozmiar | Start      | Termin     | Wymagania                                   |
| ------------------------------------------------------- | --------------------------------------------------------------- | ------- | ---- | ------- | ---------- | ---------- | ------------------------------------------- |
| [#45](https://github.com/Yibux/insurance-app/issues/45) | Create LWR site in metadata and deploy it via pipeline          | feature | P1   | M       | 2027-02-01 | 2027-02-04 | FR-PRT-01, NFR-MNT-01                       |
| [#46](https://github.com/Yibux/insurance-app/issues/46) | Provision customer community users with Customer permission set | feature | P1   | S       | 2027-02-04 | 2027-02-05 | FR-PRT-01, NFR-SEC-02                       |
| [#47](https://github.com/Yibux/insurance-app/issues/47) | Configure Sharing Sets for customer access to own records       | feature | P1   | S       | 2027-02-08 | 2027-02-09 | NFR-SEC-07                                  |
| [#48](https://github.com/Yibux/insurance-app/issues/48) | LWC: policy list and policy details                             | feature | P1   | M       | 2027-02-09 | 2027-02-12 | FR-PRT-02, NFR-UX-02                        |
| [#49](https://github.com/Yibux/insurance-app/issues/49) | LWC: claim submission form with document upload                 | feature | P1   | L       | 2027-02-15 | 2027-02-19 | FR-PRT-03, FR-CLM-03, NFR-SEC-10, NFR-UX-03 |
| [#50](https://github.com/Yibux/insurance-app/issues/50) | LWC: claim status tracking                                      | feature | P1   | S       | 2027-02-22 | 2027-02-23 | FR-PRT-04                                   |
| [#51](https://github.com/Yibux/insurance-app/issues/51) | Customer-to-agent communication via Case                        | feature | P1   | M       | 2027-02-24 | 2027-02-27 | FR-COM-01, FR-COM-02                        |
| [#52](https://github.com/Yibux/insurance-app/issues/52) | Email notification on claim status change                       | feature | P3   | S       | 2027-03-01 | 2027-03-02 | FR-COM-03                                   |
| [#53](https://github.com/Yibux/insurance-app/issues/53) | Harden portal: guest user, Lightning Web Security, CSP          | feature | P1   | M       | 2027-03-02 | 2027-03-05 | NFR-SEC-07, NFR-SEC-09                      |
| [#54](https://github.com/Yibux/insurance-app/issues/54) | Accessibility audit of portal (WCAG 2.1 AA)                     | feature | P2   | S       | 2027-03-08 | 2027-03-09 | NFR-UX-01                                   |
| [#55](https://github.com/Yibux/insurance-app/issues/55) | Reach LWC Jest coverage ≥ 70% and document the portal           | docs    | P2   | M       | 2027-03-10 | 2027-03-14 | NFR-QA-02                                   |

## M4 Python backend — data loading (2027-03-15 → 2027-04-25) — [#56](https://github.com/Yibux/insurance-app/issues/56)

Python service that securely loads historical data into Salesforce via Bulk API 2.0 using JWT Bearer, with its own DevSecOps pipeline.

| Issue                                                   | Zadanie                                                                  | Typ     | Prio | Rozmiar | Start      | Termin     | Wymagania                         |
| ------------------------------------------------------- | ------------------------------------------------------------------------ | ------- | ---- | ------- | ---------- | ---------- | --------------------------------- |
| [#57](https://github.com/Yibux/insurance-app/issues/57) | Scaffold integration-server (FastAPI, ruff, pytest, pinned dependencies) | chore   | P1   | S       | 2027-03-15 | 2027-03-16 | NFR-QA-04                         |
| [#58](https://github.com/Yibux/insurance-app/issues/58) | Add python-ci workflow with ruff, pytest, Bandit, pip-audit and CodeQL   | feature | P1   | M       | 2027-03-17 | 2027-03-19 | FR-CI-05, FR-CI-06, NFR-QA-03     |
| [#59](https://github.com/Yibux/insurance-app/issues/59) | Implement JWT Bearer authentication module                               | feature | P1   | M       | 2027-03-22 | 2027-03-24 | NFR-SEC-06                        |
| [#60](https://github.com/Yibux/insurance-app/issues/60) | Synthetic historical data generator                                      | feature | P1   | M       | 2027-03-25 | 2027-03-29 | FR-MIG-04, NFR-CMP-02             |
| [#61](https://github.com/Yibux/insurance-app/issues/61) | Bulk API 2.0 loader with upsert by External ID                           | feature | P1   | L       | 2027-03-30 | 2027-04-05 | FR-MIG-01, FR-MIG-02, NFR-PERF-03 |
| [#62](https://github.com/Yibux/insurance-app/issues/62) | Report rejected records and produce audit report                         | feature | P1   | M       | 2027-04-06 | 2027-04-08 | FR-MIG-03, NFR-OBS-01             |
| [#63](https://github.com/Yibux/insurance-app/issues/63) | Integration tests of loader against scratch org in CI                    | feature | P2   | M       | 2027-04-12 | 2027-04-15 | FR-MIG-01                         |
| [#64](https://github.com/Yibux/insurance-app/issues/64) | Write runbook and document integration security                          | docs    | P1   | M       | 2027-04-19 | 2027-04-25 | NFR-MNT-03, NFR-MNT-05            |

## M5 External Objects (2027-04-26 → 2027-05-31) — [#65](https://github.com/Yibux/insurance-app/issues/65)

Show sensitive external data in Salesforce and the portal without storing it in the CRM.

| Issue                                                   | Zadanie                                                                   | Typ      | Prio | Rozmiar | Start      | Termin     | Wymagania                        |
| ------------------------------------------------------- | ------------------------------------------------------------------------- | -------- | ---- | ------- | ---------- | ---------- | -------------------------------- |
| [#66](https://github.com/Yibux/insurance-app/issues/66) | Implement OData 4.0 endpoint for payment history                          | feature  | P1   | L       | 2027-04-26 | 2027-04-30 | FR-EXT-01, NFR-PERF-04           |
| [#67](https://github.com/Yibux/insurance-app/issues/67) | Secure the OData endpoint (authentication and per-customer filtering)     | feature  | P1   | M       | 2027-05-03 | 2027-05-05 | NFR-SEC-08, FR-EXT-03            |
| [#68](https://github.com/Yibux/insurance-app/issues/68) | Deploy backend to HTTPS hosting                                           | chore    | P1   | M       | 2027-05-06 | 2027-05-10 | NFR-SEC-08                       |
| [#69](https://github.com/Yibux/insurance-app/issues/69) | Create External Data Source and Named/External Credential in metadata     | feature  | P1   | M       | 2027-05-11 | 2027-05-13 | FR-EXT-02, NFR-SEC-08            |
| [#70](https://github.com/Yibux/insurance-app/issues/70) | Show external payment history in portal and Lightning with access control | feature  | P1   | M       | 2027-05-17 | 2027-05-20 | FR-PRT-05, FR-EXT-03, NFR-CMP-01 |
| [#71](https://github.com/Yibux/insurance-app/issues/71) | Measure OData performance                                                 | research | P3   | S       | 2027-05-24 | 2027-05-25 | NFR-PERF-04                      |
| [#72](https://github.com/Yibux/insurance-app/issues/72) | Write ADR on data residency and document External Objects                 | docs     | P1   | S       | 2027-05-26 | 2027-05-31 | NFR-CMP-01, NFR-MNT-03           |

## M6 Experiment & hardening (2027-06-01 → 2027-06-15) — [#73](https://github.com/Yibux/insurance-app/issues/73)

Measure effectiveness of the DevSecOps gates with intentionally vulnerable changes, fix findings and freeze the code.

| Issue                                                   | Zadanie                                                     | Typ      | Prio | Rozmiar | Start      | Termin     | Wymagania          |
| ------------------------------------------------------- | ----------------------------------------------------------- | -------- | ---- | ------- | ---------- | ---------- | ------------------ |
| [#74](https://github.com/Yibux/insurance-app/issues/74) | Prepare catalog of 20–30 intentionally vulnerable changes   | research | P1   | M       | 2027-05-24 | 2027-06-02 | FR-CI-04, FR-CI-05 |
| [#75](https://github.com/Yibux/insurance-app/issues/75) | Automate opening experiment PRs and collecting gate results | feature  | P1   | M       | 2027-06-01 | 2027-06-04 | NFR-OBS-02         |
| [#76](https://github.com/Yibux/insurance-app/issues/76) | Run the experiment and record TP/FN/FP and pipeline time    | research | P1   | M       | 2027-06-05 | 2027-06-08 | NFR-PERF-01        |
| [#77](https://github.com/Yibux/insurance-app/issues/77) | Analyse results with charts                                 | research | P1   | M       | 2027-06-08 | 2027-06-11 | —                  |
| [#78](https://github.com/Yibux/insurance-app/issues/78) | Hardening: fix findings and run final security review       | feature  | P1   | M       | 2027-06-09 | 2027-06-14 | NFR-SEC-03         |
| [#79](https://github.com/Yibux/insurance-app/issues/79) | Code freeze: tag v1.0.0 and record demo video               | chore    | P1   | S       | 2027-06-15 | 2027-06-15 | —                  |

## M7 Thesis writing (2026-11-02 → 2027-08-31) — [#80](https://github.com/Yibux/insurance-app/issues/80)

Write the thesis in parallel with implementation; finalize after code freeze.

| Issue                                                   | Zadanie                                                                                 | Typ    | Prio | Rozmiar | Start      | Termin     | Wymagania |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------ | ---- | ------- | ---------- | ---------- | --------- |
| [#81](https://github.com/Yibux/insurance-app/issues/81) | Chapter: Introduction — motivation, goal, scope                                         | thesis | P2   | M       | 2026-11-02 | 2026-11-30 | —         |
| [#82](https://github.com/Yibux/insurance-app/issues/82) | Chapter: Security of cloud CRM and Zero-Trust in Salesforce                             | thesis | P1   | L       | 2026-11-16 | 2026-12-20 | —         |
| [#83](https://github.com/Yibux/insurance-app/issues/83) | Chapter: DevSecOps and CI/CD — shift-left, SAST, secrets, supply chain                  | thesis | P1   | L       | 2026-12-01 | 2027-01-17 | —         |
| [#84](https://github.com/Yibux/insurance-app/issues/84) | Chapter: Ephemeral environments and integration security (JWT, OAuth, External Objects) | thesis | P1   | M       | 2027-01-04 | 2027-01-31 | —         |
| [#85](https://github.com/Yibux/insurance-app/issues/85) | Chapter: Requirements and system design                                                 | thesis | P1   | L       | 2027-02-01 | 2027-03-14 | —         |
| [#86](https://github.com/Yibux/insurance-app/issues/86) | Chapter: Implementation                                                                 | thesis | P1   | L       | 2027-06-16 | 2027-07-15 | —         |
| [#87](https://github.com/Yibux/insurance-app/issues/87) | Chapter: Experiment results and discussion                                              | thesis | P1   | L       | 2027-06-16 | 2027-07-31 | —         |
| [#88](https://github.com/Yibux/insurance-app/issues/88) | Chapter: Summary and conclusions                                                        | thesis | P1   | M       | 2027-08-01 | 2027-08-10 | —         |
| [#89](https://github.com/Yibux/insurance-app/issues/89) | Abstracts (PL/EN), keywords, bibliography and formatting                                | thesis | P1   | M       | 2027-08-05 | 2027-08-20 | —         |
| [#90](https://github.com/Yibux/insurance-app/issues/90) | Supervisor review and corrections                                                       | thesis | P1   | L       | 2027-08-15 | 2027-08-31 | —         |

## M8 Submission & defense (2027-09-01 → 2027-09-30) — [#91](https://github.com/Yibux/insurance-app/issues/91)

Submit the thesis and prepare the defense.

| Issue                                                   | Zadanie                                                     | Typ    | Prio | Rozmiar | Start      | Termin     | Wymagania |
| ------------------------------------------------------- | ----------------------------------------------------------- | ------ | ---- | ------- | ---------- | ---------- | --------- |
| [#92](https://github.com/Yibux/insurance-app/issues/92) | Submit thesis (anti-plagiarism check and university system) | thesis | P1   | S       | 2027-09-01 | 2027-09-10 | —         |
| [#93](https://github.com/Yibux/insurance-app/issues/93) | Prepare defense presentation and live demo script           | thesis | P1   | M       | 2027-09-06 | 2027-09-20 | —         |
| [#94](https://github.com/Yibux/insurance-app/issues/94) | Revise diploma exam questions and run mock defense          | thesis | P2   | M       | 2027-09-13 | 2027-09-27 | —         |
