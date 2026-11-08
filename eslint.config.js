// ESLint 9 flat config. Replaces the per-bundle .eslintrc.json files that used
// to live in force-app/main/default/{aura,lwc} (see #131).
const lwcConfig = require("@salesforce/eslint-config-lwc");
const auraPlugin = require("@salesforce/eslint-plugin-aura");
const globals = require("globals");

const lwcFiles = ["**/lwc/**/*.js"];
const auraFiles = ["**/aura/**/*.js"];

// Shared configs carry no `files`, so scope each one to its bundle directory.
const scoped = (configs, files) =>
  configs.map((config) => ({ ...config, files }));

module.exports = [
  ...scoped(lwcConfig.configs.recommended, lwcFiles),
  {
    files: ["**/lwc/**/*.test.js"],
    languageOptions: { globals: { ...globals.node } },
    rules: { "@lwc/lwc/no-unexpected-wire-adapter-usages": "off" }
  },
  ...scoped(auraPlugin.configs.recommended, auraFiles),
  {
    files: auraFiles,
    rules: {
      "vars-on-top": "off",
      "no-unused-expressions": "off"
    }
  }
];
