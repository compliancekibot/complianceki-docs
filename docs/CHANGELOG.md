# Changelog

All notable changes to the **public** ComplianceKI artifacts — the Python SDK, VSCode extension, CI/CD
integrations and developer documentation.

Format follows [Keep a Changelog](https://keepachangelog.com/); versioning follows
[SemVer](https://semver.org/). The product core and the deployed website remain closed source and are
tracked separately.

## [0.1.0] — 2026-09-06

### Added
- **Python SDK** (`complianceki-sdk`) — HTTP client for runs, findings, documents, evidence chain and
  webhooks, with configurable timeout + polling.
- **VSCode extension** — scan a workspace or file, set/rotate the API key, and view findings as inline
  diagnostics and a results output channel.
- **CI/CD integrations** — reusable **GitHub Action** (`compliancekibot/complianceki-docs/integrations@v1`),
  a **GitLab CI** template and a **GitHub App** manifest.
- **Developer documentation** — API reference, SDK user guide.
- **Apache-2.0** licensing for all public artifacts.

### Notes
- Initial public release of the SDK, integrations and docs. The product core + website are **not** part
  of this repository.
