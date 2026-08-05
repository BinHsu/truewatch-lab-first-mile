# ADR-0004 — v0.2.0/v0.3.0 thin closed loop + TF+JSON (local state)

- **Status:** Accepted
- **Date:** 2026-08-05
- **Deciders:** Owner
- **Supersedes / relates:** Extends [ADR-0002](0002-release-tags-and-emit-mode.md) tags; apply details in
  [`docs/design/monitor-dashboard-as-code.md`](../design/monitor-dashboard-as-code.md)

## Context

After ingest checkpoint v0.1.x, the lab needs a thin closed loop (Dashboard + Monitor +
email notify) and a later MCP exercise (OWL + Tobylike). Path-1 OWL CLI alone does not
cover notify object + alert policy cleanly; the owner wants Terraform + JSON content,
**local** `tfstate` (solo), forkers choose their own backend.

## Decision

### Release tags

| Tag | Scope |
|---|---|
| **v0.2.0** | Monitor + Dashboard + N3 email notify via **TF + JSON**; **local** tfstate in this lab |
| **v0.3.0** | MCP: **OWL + Tobylike** (both). Prefer OWL day-to-day. No Dashboard create via MCP |

### Content (v0.2.0)

- **Dashboard B:** one multi-series metrics chart (all four emit paths) + one APM chart
- **Notify N3:** `mailGroup` to `LAB_ALERT_EMAIL` / `TF_VAR_lab_alert_email` (gitignored `.env` only)
- Chain: `truewatch_notify_object` → `truewatch_alert_policy` → monitor (+ dashboard)

### Delivery

- Canonical tree: `terraform/` (HCL) + `terraform/json/*.json`
- State: **local** only for upstream owner; never commit `*.tfstate` (already gitignored)
- Forkers: own backend optional; do not expect upstream state
- CLI apply contract remains documented as an alternative, not the v0.2.0 default

## Consequences

- Scaffold under `terraform/`; runbook `docs/runbooks/monitor-dashboard-tf.md`
- ADR-0002 tag table gains v0.2.0 / v0.3.0 via addendum
- Cloud `apply` remains owner-gated (`confirm`); scaffold may ship with `enable_*` flags

## Re-check trigger

Provider cannot create `mailGroup` for the lab site; or owner requires remote state.
