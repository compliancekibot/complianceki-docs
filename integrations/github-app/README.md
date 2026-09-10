# ComplianceKI Scanner — GitHub App

The **ComplianceKI Scanner** GitHub App scans pull requests and reports results as **check-runs** and a
**PR comment**, so compliance issues are caught on every change.

> **Scope:** this public repository holds the **app manifest + registration** (`manifest.yml`). The
> webhook **receiver** and the check-run/comment logic are part of the **private ComplianceKI service**
> (the endpoint `POST /api/v1/webhooks/github` in the product backend), so a running ComplianceKI
> instance is required for the app to function.

## Install

1. Create the app from the manifest: **GitHub → Settings → Developer settings → GitHub Apps → New
   GitHub App → "From a manifest"** and paste `manifest.yml`.
2. Set the **Webhook URL** to your ComplianceKI instance:
   `https://api.compliancekibot.de/api/v1/webhooks/github`.
3. Generate + note the **App ID**, **Client ID**, and a **private key** (or an
   `APP_PRIVATE_KEY` secret) in your ComplianceKI configuration.
4. Install the app on the repositories / organisations you want scanned.

## Permissions & events (per `manifest.yml`)
- **Permissions:** `pull_requests: write`, `checks: write`, `contents: read`, `metadata: read`.
- **Events:** `pull_request`, `pull_request_review`.

## Behaviour
1. On `pull_request.opened` / `synchronize`, ComplianceKI creates a compliance scan run for the PR head.
2. It creates a **check-run** (pass/fail) with a summary of findings.
3. It posts a **PR comment** with the finding overview.
