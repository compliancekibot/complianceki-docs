# ComplianceKIbot.de — Public SDK, Integrations & Docs

**Automated compliance scanning for GDPR (DSGVO) + EU AI Act.** Point them at a repository and
ComplianceKI maps findings to 45 legal rules and generates the relevant audit documents — 
**deterministically, LLM-free, at €0 per scan.**

This repository holds the **public** building blocks of the platform (the product core and the
deployed website — landing pages, legal pages, app UI — are closed source and live in a separate
**private** repo). The public SDK, integrations and the **developer documentation** live here:

| Path | What it is |
|---|---|
| [`sdk/`](./sdk) | **Python SDK** (`complianceki-sdk`) — programmatic client for the ComplianceKI API |
| [`vscode/`](./vscode) | **VSCode extension** — scan files/workspaces and see findings inline |
| [`integrations/`](./integrations) | **CI/CD integrations** — GitLab CI template + GitHub App (with a reusable `complianceki-scan` GitHub Action) |
| [`docs/`](./docs) | **Developer documentation** — API reference, SDK user guide and the public CHANGELOG (the end-user site docs, "how-to-use" plus FAQ, stay on the deployed website, which links here) |

Everything here is licensed under **Apache-2.0** ([LICENSE](./LICENSE)).

> Dienstanbieter / Provider: **TOTEMA – Prozesse. Neu gedacht.** ([Impressum](https://totema.de/impressum/)) · German product page: [ComplianceKIbot.de](https://compliancekibot.de)

---

## 🐍 Python SDK (`complianceki-sdk`)

```bash
pip install complianceki-sdk
```

```python
from complianceki import ComplianceKI

client = ComplianceKI(base_url="https://api.compliancekibot.de", api_key="YOUR_API_KEY")

# Start a compliance scan
run = client.create_run(repo_ref="https://github.com/you/private-repo.git")
run = client.wait_for_run(run.id, poll_interval=5)

# Findings (filterable) + the generated documents + the SHA-256 evidence chain
findings = client.list_findings(run_id=run.id, severity="high")
docs = client.list_documents(run_id=run.id)
evidence = client.get_evidence_chain(run_id=run.id)
```

### Full API surface
`health` · `create_run` · `get_run` · `list_runs` · `get_run_summary` · `rerun` · `cancel_run` ·
`wait_for_run` · `list_findings` · `get_finding` · `list_documents` · `download_document` ·
`list_evidence` · `get_evidence_chain` · `create_webhook` · `list_webhooks` · `delete_webhook`

---

## 🧩 VSCode extension

Scan a file or the whole workspace and see ComplianceKI findings as inline diagnostics.

1. Install the `.vsix` from the [releases](../../releases) page (or `code --install-extension`).
2. Run **`ComplianceKI: Set API Key`** then **`ComplianceKI: Scan Workspace`** / **`Scan File`**.
3. Findings appear in the Problems panel, linked back to your `base_url`.

---

## ⚙️ CI/CD integrations

- **GitLab CI** — use the [`complianceki-scan.gitlab-ci.yml`](./integrations/complianceki-scan.gitlab-ci.yml)
  template: drop in your `.gitlab-ci.yml` and set `COMPLIANCEKI_API_KEY` / `COMPLIANCEKI_BASE_URL`.
- **GitHub App** — [`integrations/github-app/`](./integrations/github-app) installs the GitHub App so
  PRs are scanned automatically and reported as check-runs.
- **GitHub Action** — `uses: compliancekibot/complianceki-docs/integrations@main` wraps the same scan in a reusable action.

---

## 📚 Documentation

- [User guide](./docs/user-guide.md)
- [API reference](./docs/api-reference.md)

---

## License
Apache-2.0 — see [LICENSE](./LICENSE). The **product/compliance logic is not** part of this repo
and remains closed source.

## Contributing
Issues and PRs are welcome for the SDK, integrations, and docs. By contributing you agree to the
license and to the [code of conduct](https://github.com/compliancekibot/.github).
