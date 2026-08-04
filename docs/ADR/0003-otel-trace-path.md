# ADR-0003 — OpenTelemetry + DDTrace APM slices (metric + span)

- **Status:** Accepted
- **Date:** 2026-08-04
- **Deciders:** Owner
- **Supersedes / extends:** [ADR-0001](0001-three-ingest-paths.md) (addendum: fourth path),
  [ADR-0002](0002-release-tags-and-emit-mode.md) (tags **v0.0.3** / **v0.0.4**)

## Context

ADR-0001 scoped DataKit, DataWay, and DDTrace → DataKit. After DataKit **line-protocol**
metrics worked (v0.0.2), the owner accepted a fourth path: OpenTelemetry → DataKit
(v0.0.4), and clarified that DDTrace / OTLP are not “just another `ping` LP.”

Follow-up owner decision: **v0.0.3 and v0.0.4 must each prove both a protocol-native
metric and a span**, so DataKit’s **conversion into TrueWatch Metrics + APM** is
verified — not spans alone.

## Decision

### Release scope

| Tag | Mode | Must emit (both required) | DataKit inputs (typical) |
|---|---|---|---|
| **v0.0.3** | `ddtrace` | **Span** via DDTrace receiver **and** **metric** via DogStatsD/StatsD (or documented DDTrace-adjacent metric path DataKit accepts) | `ddtrace` + `statsd` |
| **v0.0.4** | `otel` | **Span** via OTLP traces **and** **metric** via OTLP metrics | `opentelemetry` (traces + metrics APIs) |

Lab synthetic naming should stay recognizable (e.g. measurement/metric name tied to
`truewatch_lab_first_mile` or clearly tagged `path=ddtrace` / `path=otel`) but the
**wire format must not be** `/v1/write/metric` line protocol for these two modes —
that path is already proven by v0.0.1/v0.0.2.

### Acceptance per tag

- **Metrics:** point visible under **Metrics** after DataKit conversion `[VERIFIED]`
  with OWL `M::…` or console; tags distinguish path.
- **Traces:** at least one span in **APM** / DQL **`T`** with a `trace_id`.
- Compose: enable the needed inputs; document ports (`9529` DDTrace/OTLP HTTP,
  `8125` StatsD, `4317` OTLP gRPC as applicable).
- Runbooks + [`observability-glossary.md`](../observability-glossary.md) updated.
- Until implemented, stubs print `NOT-IMPLEMENTED` and exit **non-zero**.

### Non-goals

- Replacing v0.0.1/v0.0.2 LP emit.
- Requiring full language auto-instrumentation agents for the lab stub (minimal
  synthetic emit is enough if protocol-correct).

## Consequences

- `EMIT_MODE=ddtrace` / `otel` each mean **metric + span** dual proof.
- v0.0.3 Compose grows `statsd` (or equivalent) alongside `ddtrace`.
- v0.0.4 must hit both `/otel/v1/traces` and `/otel/v1/metrics` (or gRPC equivalents).
- Forkers should not expect a fourth LP `ping` — they get two LP paths and two
  “ecosystem format → DataKit translate” paths.

## Addendum timeline

- 2026-08-04: OTel path accepted as v0.0.4 (trace-focused first draft).
- 2026-08-04 (same day): Owner required **metric + span** for **both** v0.0.3 and
  v0.0.4; this document is the merged decision record.

## Re-check trigger

Revisit if DataKit drops StatsD or OTLP metrics ingress, or if TrueWatch documents
a preferred single dual-signal protocol that makes separate DDTrace/OTel slices
redundant.
