# ComplianceKIbot.de — API Reference

**Base URL:** `https://api.compliancekibot.de`
**Auth:** `X-API-Key: <YOUR_API_KEY>`
**Content-Type:** `application/json`

All responses are JSON. Errors return a standard `{"detail": "<message>"}` with an appropriate HTTP
status (400/401/404/422/502).

---

## Health

| Method | Path | Description |
|---|---|---|
| GET | `/health/status` | System status: `{api, version, database, redis, s3, healthy}` |

---

## Runs

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/runs` | Create a run. Body: `{repo_ref, mode, commit_hash?, dry_run?, access_token?}` |
| GET | `/api/v1/runs` | List runs (query: `limit`, `offset`) |
| GET | `/api/v1/runs/{run_id}` | Run detail (`status`, `findings_count`, `documents_count`, `error_message`) |
| GET | `/api/v1/runs/{run_id}/summary` | Aggregated run summary |
| POST | `/api/v1/runs/{run_id}/rerun` | Re-run |
| DELETE | `/api/v1/runs/{run_id}` | Cancel a run |

`mode` is `assessment_only` (default) or `full_implementation`. `access_token` is optional and used only
for private-repo cloning (never persisted).

---

## Findings

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/findings` | List (query: `run_id`, `severity`, `category`, `limit`, `offset`) |
| GET | `/api/v1/findings/{finding_id}` | Finding detail |

A finding: `{id, run_id, severity, category, title, description, file_path, line, legal_refs,
risk_score, likelihood, status, hash, created_at}`.

---

## Documents

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/documents` | List (query: `run_id`, `doc_type`, `language`, `limit`, `offset`) |
| GET | `/api/v1/documents/{doc_id}/download` | Download the document as markdown |

A document: `{id, run_id, doc_type, language, title, storage_key, version, hash, status, note,
created_at}`. `status` is `generated` or `skipped` (a skipped document carries a `note`/vermerk).

---

## Evidence

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/evidence/chain/{run_id}` | SHA-256 evidence chain for a run |

---

## Webhooks

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/webhooks` | Create a webhook |
| GET | `/api/v1/webhooks` | List webhooks |
| DELETE | `/api/v1/webhooks/{webhook_id}` | Delete a webhook |

---

## Example

```bash
# Create a run
curl -sS -X POST https://api.compliancekibot.de/api/v1/runs \
  -H "X-API-Key: $COMPLIANCEKI_API_KEY" -H "Content-Type: application/json" \
  -d '{"repo_ref":"https://github.com/you/repo.git","mode":"assessment_only"}'
```

The Python SDK wraps all of this (`complianceki-sdk`); see the [user guide](./user-guide.md).
