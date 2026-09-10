# ComplianceKIbot.de — User Guide

ComplianceKI scans a repository for GDPR (DSGVO) and EU AI Act obligations, maps findings to 45 legal
rules, and generates the relevant audit documents. The product deterministically runs local SAST tools
(Semgrep, Gitleaks, OSV-Scanner) + data-flow analysis — **no LLM calls, €0 per scan**.

This guide covers using the **public** building blocks from this repo. The hosted dashboard and the
product core are closed source.

---

## 1. Get started

### 1.1 API key + base URL
You need an API key from ComplianceKI. All requests use the **`X-API-Key`** header.

- **Base URL (API):** `https://api.compliancekibot.de`
- **Auth header:** `X-API-Key: <YOUR_API_KEY>`
- **Content-Type:** `application/json`

> Sandbox/local? The SDK accepts a custom `base_url` (see below).

### 1.2 Install the SDK
```bash
pip install complianceki-sdk
```

---

## 2. Python SDK

```python
from complianceki import ComplianceKI

client = ComplianceKI(base_url="https://api.compliancekibot.de", api_key="YOUR_API_KEY")
```

### Scan a repository
```python
run = client.create_run(repo_ref="https://github.com/you/repo.git")
run = client.wait_for_run(run.id, poll_interval=5)   # blocks until done
print(run.status, run.findings_count, run.documents_count)
```

### Read the results
```python
# High-severity findings
findings = client.list_findings(run_id=run.id, severity="high")
for f in findings:
    print(f"[{f.severity}] {f.title} @ {f.file_path}")

# Generated documents (DE + EN)
for doc in client.list_documents(run_id=run.id):
    print(doc.doc_type, doc.language, doc.version)

# The tamper-evident SHA-256 evidence chain
for item in client.get_evidence_chain(run_id=run.id):
    print(item.hash, item.description)
```

### Download a document
```python
markdown = client.download_document(doc_id)   # returns the document as markdown
```

### Full API surface
| Area | Methods |
|---|---|
| Health | `health()` |
| Runs | `create_run` · `get_run` · `list_runs` · `get_run_summary` · `rerun` · `cancel_run` · `wait_for_run` |
| Findings | `list_findings` · `get_finding` |
| Documents | `list_documents` · `download_document` |
| Evidence | `list_evidence` · `get_evidence_chain` |
| Webhooks | `create_webhook` · `list_webhooks` · `delete_webhook` |

---

## 3. VSCode extension

Scan files or a workspace and see findings inline.

1. Install the `.vsix` from the releases page.
2. Run **ComplianceKI: Set API Key** (and **ComplianceKI: Set Base URL** if not using the default).
3. Run **ComplianceKI: Scan Workspace** or **ComplianceKI: Scan File**.
4. Findings appear in the **Problems** panel as diagnostics.

---

## 4. CI/CD integrations

### 4.1 GitHub Action
```yaml
name: compliance-scan
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: compliancekibot/complianceki-docs/integrations@v1     # reusable action
        with:
          api-key: ${{ secrets.COMPLIANCEKI_API_KEY }}
          mode: assessment_only
```

### 4.2 GitLab CI
Use the [complianceki-scan.gitlab-ci.yml](../integrations/complianceki-scan.gitlab-ci.yml) template:

```yaml
include:
  - project: 'compliancekibot/complianceki-docs'
    file: '/integrations/complianceki-scan.gitlab-ci.yml'
```
Set `COMPLIANCEKI_API_KEY` (and optionally `COMPLIANCEKI_BASE_URL`) as CI variables.

### 4.3 GitHub App
Install the app from [integrations/github-app](../integrations/github-app) so pull requests are scanned
automatically and reported as check-runs.

---

## 5. Understanding the output

- **Findings** each carry a `severity` (critical/high/medium/low/info), a `category`
  (security/privacy/ai_governance/license), a `legal_refs` list, and a `risk_score` (severity ×
  likelihood, 1–25).
- **Documents** are generated per applicable doc type and language (DE/EN), each with a `version` and a
  **SHA-256 evidence chain** so they are tamper-evident.

---

## 6. FAQ / support

- **Provider:** TOTEMA – Prozesse. Neu gedacht. ([Impressum](https://totema.de/impressum/))
- **Site:** [ComplianceKIbot.de](https://compliancekibot.de)
- File an issue in this repo for SDK/integration/docs problems.
