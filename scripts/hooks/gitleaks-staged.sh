#!/bin/sh
# Pre-commit secret scan of staged changes (#19, FR-CI-09).
# CI scans the full history anyway; locally the hook warns when gitleaks
# is missing instead of blocking the commit.

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "gitleaks not found - skipping local secret scan (CI will still run it)."
  echo "Install: winget install --id Gitleaks.Gitleaks  |  brew install gitleaks"
  exit 0
fi

exec gitleaks git --pre-commit --staged --redact --no-banner --config .gitleaks.toml
