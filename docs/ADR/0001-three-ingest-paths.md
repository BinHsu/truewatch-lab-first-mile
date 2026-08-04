# ADR-0001 — Lab covers three ingest paths

- **Status:** Accepted
- **Date:** 2026-08-04
- **Deciders:** Owner

## Context

The first-mile lab needs a concrete ingest story. Options were a single path
(DataKit only, or DataWay direct only) versus demonstrating how TrueWatch
accepts data through multiple compatible entry points. Owner chose full
coverage of the three paths discussed in-session.

## Decision

This lab will exercise **all three** ingest paths against the same trial
workspace (`id1`):

| # | Path | Meaning in this lab |
|---|---|---|
| 1 | **DataKit** | Install/run TrueWatch DataKit; synthetic host/app data (or a simple push into DataKit) appears in Explorer via DataKit → DataWay. |
| 2 | **DataWay** | Emitter POSTs directly to the site DataWay write API (`/v1/write/…?token=…`) without requiring DataKit for that slice. |
| 3 | **DDTrace → DataKit** | App (or a tiny instrumented stub) sends Datadog-trace protocol traffic to DataKit’s `ddtrace` receiver (`:9529`); DataKit uploads to TrueWatch. Not “Datadog Agent → DataKit”. |

They are **parallel capabilities**, not mutually exclusive. Implementation may be
sliced (prove one path end-to-end before the next), but the **goal** is all three
documented and runnable for forkers.

## Consequences

- `.env.example` will grow Workspace / DataWay token and DataKit-related vars
  (secrets still only in local `.env`).
- Runbooks must keep Client Token (OWL/Open API) distinct from Workspace Token
  (ingest).
- DDTrace slice depends on a working DataKit with `ddtrace` enabled.
- Day-1 may still defer Monitor/Dashboard; ingest visibility in Explorer is the
  acceptance bar per path unless a later decision expands scope.

## Addendum — 2026-08-04 (fourth path: OTel; dual signal on APM slices)

Owner accepted **OpenTelemetry (OTLP) → DataKit** as **v0.0.4** (`EMIT_MODE=otel`).
Additionally, **v0.0.3 (DDTrace) and v0.0.4 (OTel) each must emit protocol-native
metrics and spans** so DataKit conversion into Metrics + APM is proven. See
[ADR-0003](0003-otel-trace-path.md). Path 3’s original “trace traffic” wording is
extended — not replaced — by that dual-signal requirement.

## Re-check trigger

Revisit if TrueWatch changes DataWay write URLs for `id1`, deprecates the
`ddtrace` collector port model, or the trial workspace cannot enable DataKit.
