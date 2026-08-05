# Observability glossary + TrueWatch console map

Lab-oriented glossary for Metrics / Logs / APM / RUM and related terms.
Not a status file — progress stays in [`handoff/CURRENT.md`](handoff/CURRENT.md).

Official product surfaces evolve; menu labels below match TrueWatch docs patterns
([Explorer](https://docs.truewatch.com/scene/explorer/),
[platform capabilities](https://docs.truewatch.com/platform-capabilities/),
[RUM Explorer](https://docs.truewatch.com/real-user-monitoring/explorer/),
[APM collection](https://docs.truewatch.com/application-performance-monitoring/collection/)).
Trial UI language may be EN/ZH mixed.

---

## TrueWatch console ↔ signal (where to click)

| You want… | Typical left-nav / area | Lab / OWL hint |
|---|---|---|
| Time-series numbers (`ping`, CPU, `dk`) | **Metrics** → Explorer / Metric Analysis | DQL namespace **`M`**; our measurement `truewatch_lab_first_mile` |
| Event text / app logs | **Logs** → Explorer | DQL **`L`** (often needs an index) |
| Request chains, `trace_id`, service map | **APM** / **Application Performance Monitoring** → Traces / Service | DQL **`T`**; v0.0.3/v0.0.4 also send **protocol-native metrics** (not LP `ping`) into **Metrics** |
| Real browser/app UX | **RUM** / **Real User Monitoring** → Session / View / … | Needs RUM SDK + **Client Token** (≠ OWL API Key, ≠ Workspace Token) |
| Synthetic probes | **Synthetic Tests** (or similar) | Not in current emit modes |
| Hosts / containers / K8s objects | **Infrastructure** | Often from DataKit collectors; OWL `owl.infrastructure.*` |
| Alerts | **Monitoring** / Monitors | Optional lab scope (`AWAITING DECISION`) |
| Charts | **Scenarios** / Dashboards | Optional; Dashboard writes via CLI/console, not MCP |
| Custom saved queries | **Scenarios** → **Explorer** list (can pin into Metrics/Logs/APM menus) | — |

**Explorer** is the shared “query + filter + table/chart” UI pattern reused under Metrics, Logs, APM, RUM, etc.

### What this lab has proven so far

| Path | Console place | Evidence |
|---|---|---|
| DataWay / DataKit **metric** `ping` | **Metrics** | `path=dataway` / `path=datakit` `[VERIFIED]` |
| DataKit self-metrics | **Metrics** measurement **`dk`** | Side effect of `ENV_DEFAULT_ENABLED_INPUTS=dk` — see [`runbooks/datakit-emit.md`](runbooks/datakit-emit.md) |
| Traces | **APM** | Not yet — stubs until v0.0.3 / v0.0.4 |
| RUM | **RUM** | Out of ADR ingest set; Client Token gotcha only |

---

## Glossary (signals)

| Term | Meaning |
|---|---|
| **Logs** | Discrete event records (“what happened”). |
| **Metrics** | Numeric series over time (QPS, latency, `ping=1`). |
| **Traces** | One request’s journey across services as a tree of steps. |
| **Telemetry** | Generic name for the above (plus events, profiles, …). |
| **MELT** | Metrics, Events, Logs, Traces (mnemonic). |

---

## Glossary (tracing / APM) — including **span**

| Term | Meaning |
|---|---|
| **Span** | **One step** in a trace (HTTP call, DB query, function). Has start time, duration, name. **Not “spam”.** |
| **Trace** | The whole tree of spans for one request, sharing one **trace_id**. |
| **trace_id** | ID shared by every span in that request. |
| **span_id** | ID of this span. |
| **parent_id** | Parent span’s id (root often `0` / empty). |
| **APM** | Application Performance Monitoring — services, traces, dependencies, error/latency views. |
| **Operation / span name** | Label for the step (`GET /api`, `SELECT …`). |
| **Service** | Which app/component emitted the span. |
| **Resource** | Finer target (route, SQL). |
| **Instrumentation** | Code or auto-agent that creates spans. |
| **Propagation** | Passing `trace_id` across process boundaries (`traceparent`, etc.). |
| **Sampling** | Keeping only a fraction of traces. |
| **OTLP** | OpenTelemetry export protocol (gRPC/HTTP). |
| **DDTrace** | Datadog-style tracing protocol/SDK family DataKit can receive. |

```text
Trace (one trace_id)
└─ Span (API) 
   ├─ Span (service A)
   │  └─ Span (DB)
   └─ Span (service B)
```

**Span’s job:** break one user request into timed steps so you can find the slow/error hop. Metrics alone cannot show that graph; logs alone usually cannot stitch the tree without IDs.

If someone says **spam** in this context, ask whether they mean **span**. Alert/log **spam** means noisy flood — different word.

---

## Glossary (RUM / frontend)

| Term | Meaning |
|---|---|
| **RUM** | Real User Monitoring — real browsers/apps. |
| **Session** | One user’s visit period. |
| **View** | A page/screen view. |
| **Action** | Click/tap/input. |
| **Long Task** | Main-thread block (often >50ms). |
| **Resource** (RUM) | Loaded asset/XHR timing on the page. |
| **Synthetic** | Scripted probes, not real users. |

---

## Glossary (metrics / logs plumbing)

| Term | Meaning |
|---|---|
| **Measurement** | Metric name (`truewatch_lab_first_mile`). |
| **Field** | Numeric (or payload) field (`ping`). |
| **Tag / label** | Dimension (`path=datakit`) for filter/group. |
| **Index** (logs) | Log partition for query (`L("default")::…`). |
| **Pipeline** | Parse/enrich/drop rules on ingest. |
| **Cardinality** | How many unique tag combinations — high cardinality → cost/load. |

---

## Glossary (platform / TrueWatch lab)

| Term | Meaning |
|---|---|
| **DataKit** | TrueWatch agent (local receive → DataWay). |
| **DataWay** | Cloud write gateway (`*-openway`). |
| **Ingest** | Data entering the platform. |
| **Input / collector** | DataKit module (`dk`, `ddtrace`, `opentelemetry`, …). |
| **Self-metrics (`dk`)** | DataKit’s own health metrics — not the lab `ping` series. |
| **DaemonSet / sidecar** | K8s ways to run DataKit. |
| **Operator (DataKit Operator)** | Can auto-inject language APM agents into pods. |
| **DQL** | Query language; OWL `owl.data.query`. |
| **Monitor** | Alert rule. |
| **Dashboard** | Chart board. |
| **Workspace Token** | Ingest write (`tkn_…`) — not OWL. |
| **API Key / Personal API Key** | Open API / OWL. |
| **Client Token** | RUM public token — not OWL, not Workspace Token. |

---

## Release modes in this lab

| Tag | Mode | Signal you prove |
|---|---|---|
| v0.0.1 | `dataway` | Metrics via DataWay (**LP** `ping`) |
| v0.0.2 | `datakit` | Metrics via DataKit (**LP** `ping`; optional `dk`) |
| v0.0.3 | `ddtrace` | **StatsD metric + DDTrace span** (DataKit translates) — see [`runbooks/ddtrace-emit.md`](runbooks/ddtrace-emit.md) |
| v0.0.4 | `otel` | **OTLP metric + OTLP span** (DataKit translates) |

See [ADR-0002](ADR/0002-release-tags-and-emit-mode.md), [ADR-0003](ADR/0003-otel-trace-path.md).
