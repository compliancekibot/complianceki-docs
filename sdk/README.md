# ComplianceKI Python SDK

Programmatic client for the ComplianceKI compliance scanning API.

## Installation

```bash
pip install complianceki-sdk
```

Or from source:

```bash
pip install -e sdk/
```

## Quick Start

```python
from complianceki import ComplianceKI

client = ComplianceKI(
    base_url="https://api.example.com",
    api_key="sk-...",
)

# Check health
print(client.health())

# Trigger a compliance run
run = client.create_run(
    repo_ref="https://github.com/user/repo.git",
    mode="assessment_only",
)
print(f"Run created: {run.id}")

# Wait for completion
run = client.wait_for_run(run.id, poll_interval=5)
print(f"Run completed: {run.status}")

# Get high-severity findings
findings = client.list_findings(run_id=run.id, severity="high")
for f in findings:
    print(f"[{f.severity}] {f.title}")

# Download a generated document
docs = client.list_documents(run_id=run.id)
if docs:
    print(client.download_document(docs[0].id))
```

## API Coverage

- ✅ Health check
- ✅ Runs (create, list, get, rerun, cancel, wait)
- ✅ Run summary
- ✅ Findings (list, get)
- ✅ Documents (list, download)
- ✅ Evidence (list, chain)
- ✅ Webhooks (create, list, delete)
