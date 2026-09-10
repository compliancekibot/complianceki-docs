# Contributing to ComplianceKI public artifacts

Thanks for your interest! This repo holds the **public** building blocks of
[ComplianceKIbot.de](https://compliancekibot.de): the Python SDK, a VSCode extension, CI/CD
integrations, and user docs. The product core is closed source and not part of this repository.

## Ways to contribute

- **Report a bug** — open an issue with a clear title, reproduction steps, and expected vs. actual.
- **Request a feature** — open an issue describing the use case.
- **Fix / improve** — open a pull request against `main`.

## Development setup

### Python SDK (`sdk/`)
```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e "sdk[dev]"                       # or: pip install -e sdk
```
Run tests:
```bash
pytest sdk
```

### VSCode extension (`vscode/`)
```bash
cd vscode
npm install
# open the folder in VS Code and press F5 to launch the Extension Development Host
```
Package: `npm run package` (produces a `.vsix`).

### CI templates (`integrations/`)
Copy the GitLab template into your project, or reference the repository action. Test with a valid
`COMPLIANCEKI_API_KEY`.

## Guidelines

- Keep PRs focused; one change per PR, with a clear title and a summary of the change.
- Match the existing style; run the project's formatters/linters if present.
- Add/adjust tests for behavior you change.
- Do **not** commit generated artifacts (`.vsix`, `dist/`, `__pycache__` — see `.gitignore`).
- Follow the [Code of Conduct](https://github.com/compliancekibot/.github/blob/main/CODE_OF_CONDUCT.md).

## Licensing

Contributed code is licensed under **Apache-2.0** (see [LICENSE](./LICENSE)). By contributing you
confirm the contribution is your own and you grant it under these terms.
