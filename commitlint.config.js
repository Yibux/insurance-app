// Conventional Commits check for the Husky commit-msg hook (#23, FR-CI-09).
// Allowed types follow docs/KONWENCJE.md (section 2).
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "chore",
        "docs",
        "test",
        "ci",
        "refactor",
        "build",
        "security"
      ]
    ],
    "subject-case": [0],
    "header-max-length": [2, "always", 100]
  }
};
