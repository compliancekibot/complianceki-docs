"""
ComplianceKI – SDK Data Models
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Tenant:
    id: uuid.UUID
    name: str
    slug: str
    schema_name: str
    s3_bucket: str
    branding: dict | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Run:
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    repo_ref: str = ""
    commit_hash: str | None = None
    mode: str = "assessment_only"
    status: str = "pending"
    version: str = "0.1.0"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Finding:
    id: uuid.UUID
    run_id: uuid.UUID
    severity: str
    category: str
    title: str
    description: str | None = None
    legal_refs: list[str] = field(default_factory=list)
    file_path: str | None = None
    line: int | None = None
    remediation: str | None = None
    risk_score: float | None = None
    likelihood: str | None = None
    status: str = "open"
    created_at: datetime | None = None


@dataclass
class Document:
    id: uuid.UUID
    run_id: uuid.UUID
    doc_type: str
    language: str
    title: str
    storage_key: str | None = None
    version: str = "0.1.0"
    hash: str | None = None
    status: str = "pending"
    created_at: datetime | None = None


@dataclass
class EvidenceItem:
    id: uuid.UUID
    run_id: uuid.UUID
    evidence_type: str
    source: str
    hash: str
    storage_key: str | None = None
    chain_of_custody: list[str] = field(default_factory=list)
    previous_hash: str | None = None
    created_at: datetime | None = None


@dataclass
class Webhook:
    id: uuid.UUID
    tenant_id: uuid.UUID
    url: str
    events: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime | None = None


@dataclass
class RunSummary:
    run_id: uuid.UUID
    status: str
    repo_ref: str
    findings_total: int = 0
    findings_by_severity: dict[str, int] = field(default_factory=dict)
    data_flows: int = 0
    ai_models: int = 0
    documents: int = 0
    duration_ms: int | None = None
