# insurance-app

The master's repository — an insurance application built on the Salesforce platform (Salesforce DX project).

## Structure

- `force-app/main/default` — metadata source (Apex classes, triggers, LWC, objects, layouts, permission sets, ...)
- `config/project-scratch-def.json` — scratch org definition
- `scripts/` — sample anonymous Apex and SOQL scripts
- `sfdx-project.json` — project configuration

## Getting started

Requirements: [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli), Node.js, VS Code with the Salesforce Extension Pack.

```bash
npm install
sf org login web --set-default-dev-hub --alias devhub
sf org create scratch --definition-file config/project-scratch-def.json --alias insurance-app --set-default --duration-days 30
sf project deploy start
sf org open
```

## Useful commands

```bash
npm run lint          # ESLint for LWC/Aura
npm test              # LWC Jest unit tests
npm run prettier      # format sources
sf apex run test --code-coverage --result-format human --wait 10
```
