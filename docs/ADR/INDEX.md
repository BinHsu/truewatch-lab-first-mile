# ADR index

Route by reader goal. Status lives in `docs/handoff/CURRENT.md`, not here.

| ADR | Title | When to read |
|---|---|---|
| [0001](0001-three-ingest-paths.md) | Lab covers three ingest paths (DataKit, DataWay, DDTrace→DataKit); addendum adds OTel | Before implementing emitters or choosing a single ingest shortcut |
| [0002](0002-release-tags-and-emit-mode.md) | Release tags v0.0.1–v0.0.4 + `EMIT_MODE` / Docker-first | Before adding emit modes or cutting a release tag |
| [0003](0003-otel-trace-path.md) | v0.0.3/v0.0.4: DDTrace & OTel each prove **metric + span** via DataKit | Before implementing ddtrace/otel modes or scoping APM vs LP metrics |
| [0004](0004-tf-json-closed-loop.md) | v0.2.0 TF+JSON closed loop (local state); v0.3.0 OWL+Tobylike MCP | Before Monitor/Dashboard/notify IaC or MCP dual-client work |
