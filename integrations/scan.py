#!/usr/bin/env python3
"""ComplianceKI GitHub Action — scan a repository and post findings as annotations.

Runs against the ComplianceKI API via the `complianceki-sdk`. Environment is set by
`action.yml` (inputs). Exits non-zero when findings exist at/above COMPLIANCEKI_FAIL_ON.
"""
import os
import sys

from complianceki import ComplianceKI


def main() -> int:
    base = os.environ.get("COMPLIANCEKI_BASE_URL", "https://api.compliancekibot.de")
    api_key = os.environ.get("COMPLIANCEKI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: COMPLIANCEKI_API_KEY is required", file=sys.stderr)
        return 2

    repo_ref = os.environ.get("GITHUB_REPOSITORY", "")
    commit_hash = os.environ.get("GITHUB_SHA") or None
    mode = os.environ.get("COMPLIANCEKI_MODE", "assessment_only")
    fail_on = os.environ.get("COMPLIANCEKI_FAIL_ON", "high").strip().lower()

    client = ComplianceKI(base_url=base, api_key=api_key)
    run = client.create_run(repo_ref=repo_ref, commit_hash=commit_hash, mode=mode)
    print(f"run={run.id} status={run.status}")
    run = client.wait_for_run(run.id, poll_interval=10)
    if run.status != "completed":
        print(f"ERROR: scan did not complete (status={run.status})", file=sys.stderr)
        return 1

    summary = client.get_run_summary(run.id)
    print(f"findings={summary.findings_total} data_flows={summary.data_flows} "
          f"ai_models={summary.ai_models} documents={summary.documents}")

    levels = ["critical", "high", "medium", "low", "info"]
    threshold = levels.index(fail_on) if fail_on in levels else 1  # default = high
    failures = 0
    for sev in levels[: threshold + 1]:
        for f in client.list_findings(run_id=run.id, severity=sev):
            msg = f"[{sev}] {f.title} (score {f.risk_score})"
            if f.file_path:
                print(f"::error file={f.file_path}::{msg}")
            else:
                print(f"::error::{msg}")
            failures += 1

    if fail_on and failures:
        print(f"ERROR: {failures} finding(s) at/above '{fail_on}'", file=sys.stderr)
        return 1

    print("Compliance scan passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
