"""
ComplianceKI – Python SDK Client
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime
from typing import Any

import httpx

from client.models import (
    Document,
    EvidenceItem,
    Finding,
    Run,
    RunSummary,
    Webhook,
)


class ComplianceKI:
    """Client for the ComplianceKI API."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self._headers: dict[str, str] = {}
        if api_key:
            self._headers["X-API-Key"] = api_key

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._headers,
            timeout=timeout,
            verify=verify_ssl,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> ComplianceKI:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ── Response parsing helpers ──

    def _parse_run(self, data: dict) -> Run:
        return Run(
            id=uuid.UUID(data["id"]),
            tenant_id=uuid.UUID(data["tenant_id"]) if data.get("tenant_id") else None,
            repo_ref=data.get("repo_ref", ""),
            commit_hash=data.get("commit_hash"),
            mode=data.get("mode", "assessment_only"),
            status=data.get("status", "pending"),
            version=data.get("version", "0.1.0"),
            started_at=_parse_dt(data.get("started_at")),
            completed_at=_parse_dt(data.get("completed_at")),
            duration_ms=data.get("duration_ms"),
            created_at=_parse_dt(data.get("created_at")),
            updated_at=_parse_dt(data.get("updated_at")),
        )

    def _parse_finding(self, data: dict) -> Finding:
        return Finding(
            id=uuid.UUID(data["id"]),
            run_id=uuid.UUID(data["run_id"]),
            severity=data["severity"],
            category=data["category"],
            title=data["title"],
            description=data.get("description"),
            legal_refs=data.get("legal_refs", []),
            file_path=data.get("file_path"),
            line=data.get("line"),
            remediation=data.get("remediation"),
            risk_score=data.get("risk_score"),
            likelihood=data.get("likelihood"),
            status=data.get("status", "open"),
            created_at=_parse_dt(data.get("created_at")),
        )

    # ── Health ──

    def health(self) -> dict:
        """Check API health."""
        resp = self._client.get("/health/status")
        resp.raise_for_status()
        return resp.json()

    # ── Runs ──

    def create_run(
        self,
        repo_ref: str,
        commit_hash: str | None = None,
        mode: str = "assessment_only",
    ) -> Run:
        """Trigger a new compliance run."""
        payload = {"repo_ref": repo_ref, "mode": mode}
        if commit_hash:
            payload["commit_hash"] = commit_hash
        resp = self._client.post("/api/v1/runs", json=payload)
        resp.raise_for_status()
        return self._parse_run(resp.json())

    def get_run(self, run_id: str | uuid.UUID) -> Run:
        """Get run status and metadata."""
        resp = self._client.get(f"/api/v1/runs/{run_id}")
        resp.raise_for_status()
        return self._parse_run(resp.json())

    def list_runs(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Run]:
        """List recent runs."""
        resp = self._client.get(f"/api/v1/runs?limit={limit}&offset={offset}")
        resp.raise_for_status()
        return [self._parse_run(r) for r in resp.json()]

    def get_run_summary(self, run_id: str | uuid.UUID) -> RunSummary:
        """Get a summary with counts and key metrics."""
        resp = self._client.get(f"/api/v1/runs/{run_id}/summary")
        resp.raise_for_status()
        data = resp.json()
        return RunSummary(
            run_id=uuid.UUID(data["run_id"]),
            status=data["status"],
            repo_ref=data["repo_ref"],
            findings_total=data.get("findings", {}).get("total", 0),
            findings_by_severity=data.get("findings", {}).get("by_severity", {}),
            data_flows=data.get("data_flows", 0),
            ai_models=data.get("ai_models", 0),
            documents=data.get("documents", 0),
            duration_ms=data.get("duration_ms"),
        )

    def rerun(self, run_id: str | uuid.UUID) -> Run:
        """Re-run a previous compliance scan."""
        resp = self._client.post(f"/api/v1/runs/{run_id}/rerun")
        resp.raise_for_status()
        return self._parse_run(resp.json())

    def cancel_run(self, run_id: str | uuid.UUID) -> Run:
        """Cancel a pending or running run."""
        resp = self._client.delete(f"/api/v1/runs/{run_id}")
        resp.raise_for_status()
        return self._parse_run(resp.json())

    def wait_for_run(
        self,
        run_id: str | uuid.UUID,
        poll_interval: float = 5.0,
        timeout: float = 600.0,
    ) -> Run:
        """Poll until a run completes or fails."""
        deadline = time.time() + timeout
        terminal_states = {"completed", "failed"}
        while time.time() < deadline:
            run = self.get_run(run_id)
            if run.status in terminal_states:
                return run
            time.sleep(poll_interval)
        raise TimeoutError(f"Run {run_id} did not complete within {timeout}s")

    # ── Findings ──

    def list_findings(
        self,
        run_id: str | uuid.UUID | None = None,
        severity: str | None = None,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Finding]:
        """List findings with optional filters."""
        params = f"limit={limit}&offset={offset}"
        if run_id:
            params += f"&run_id={run_id}"
        if severity:
            params += f"&severity={severity}"
        if category:
            params += f"&category={category}"
        resp = self._client.get(f"/api/v1/findings?{params}")
        resp.raise_for_status()
        return [self._parse_finding(f) for f in resp.json()]

    def get_finding(self, finding_id: str | uuid.UUID) -> Finding:
        """Get a single finding by ID."""
        resp = self._client.get(f"/api/v1/findings/{finding_id}")
        resp.raise_for_status()
        return self._parse_finding(resp.json())

    # ── Documents ──

    def list_documents(
        self,
        run_id: str | uuid.UUID | None = None,
        doc_type: str | None = None,
        language: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Document]:
        """List generated documents."""
        params = f"limit={limit}&offset={offset}"
        if run_id:
            params += f"&run_id={run_id}"
        if doc_type:
            params += f"&doc_type={doc_type}"
        if language:
            params += f"&language={language}"
        resp = self._client.get(f"/api/v1/documents?{params}")
        resp.raise_for_status()
        return [
            Document(
                id=uuid.UUID(d["id"]),
                run_id=uuid.UUID(d["run_id"]),
                doc_type=d["doc_type"],
                language=d["language"],
                title=d["title"],
                storage_key=d.get("storage_key"),
                version=d.get("version", "0.1.0"),
                hash=d.get("hash"),
                status=d.get("status", "pending"),
                created_at=_parse_dt(d.get("created_at")),
            )
            for d in resp.json()
        ]

    def download_document(self, doc_id: str | uuid.UUID) -> str:
        """Download a generated document content."""
        resp = self._client.get(f"/api/v1/documents/{doc_id}/download")
        resp.raise_for_status()
        return resp.text

    # ── Evidence ──

    def list_evidence(
        self,
        run_id: str | uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EvidenceItem]:
        """List evidence chain items."""
        params = f"limit={limit}&offset={offset}"
        if run_id:
            params += f"&run_id={run_id}"
        resp = self._client.get(f"/api/v1/evidence?{params}")
        resp.raise_for_status()
        return [
            EvidenceItem(
                id=uuid.UUID(e["id"]),
                run_id=uuid.UUID(e["run_id"]),
                evidence_type=e["evidence_type"],
                source=e["source"],
                hash=e["hash"],
                storage_key=e.get("storage_key"),
                chain_of_custody=e.get("chain_of_custody", []),
                previous_hash=e.get("previous_hash"),
                created_at=_parse_dt(e.get("created_at")),
            )
            for e in resp.json()
        ]

    def get_evidence_chain(self, run_id: str | uuid.UUID) -> list[EvidenceItem]:
        """Get the full evidence chain for a run."""
        resp = self._client.get(f"/api/v1/evidence/chain/{run_id}")
        resp.raise_for_status()
        return [
            EvidenceItem(
                id=uuid.UUID(e["id"]),
                run_id=uuid.UUID(e["run_id"]),
                evidence_type=e["evidence_type"],
                source=e["source"],
                hash=e["hash"],
                storage_key=e.get("storage_key"),
                chain_of_custody=e.get("chain_of_custody", []),
                previous_hash=e.get("previous_hash"),
                created_at=_parse_dt(e.get("created_at")),
            )
            for e in resp.json()
        ]

    # ── Webhooks ──

    def create_webhook(
        self,
        url: str,
        events: list[str] | None = None,
        secret: str | None = None,
    ) -> Webhook:
        """Register a webhook endpoint."""
        payload = {"url": url}
        if events:
            payload["events"] = events
        if secret:
            payload["secret"] = secret
        resp = self._client.post("/api/v1/webhooks", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return Webhook(
            id=uuid.UUID(data["id"]),
            tenant_id=uuid.UUID(data["tenant_id"]),
            url=data["url"],
            events=data.get("events", []),
            is_active=data.get("is_active", True),
            created_at=_parse_dt(data.get("created_at")),
        )

    def list_webhooks(self) -> list[Webhook]:
        """List webhook configurations."""
        resp = self._client.get("/api/v1/webhooks")
        resp.raise_for_status()
        return [
            Webhook(
                id=uuid.UUID(w["id"]),
                tenant_id=uuid.UUID(w["tenant_id"]),
                url=w["url"],
                events=w.get("events", []),
                is_active=w.get("is_active", True),
                created_at=_parse_dt(w.get("created_at")),
            )
            for w in resp.json()
        ]

    def delete_webhook(self, webhook_id: str | uuid.UUID) -> None:
        """Delete a webhook configuration."""
        resp = self._client.delete(f"/api/v1/webhooks/{webhook_id}")
        resp.raise_for_status()


def _parse_dt(value: str | None) -> datetime | None:
    """Parse an ISO datetime string."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)
    return value
