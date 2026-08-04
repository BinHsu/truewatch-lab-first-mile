# Threat Model

> Practice 3/4 reference: security-sensitive changes (auth, crypto, payments, PII) require
> a threat-model entry here + an integration test exercising the failure mode. This is the
> template — one entry per sensitive surface. Keep it lightweight (STRIDE-lite), not a thesis.

## Entry template

### {{Surface name — e.g. "User authentication endpoint"}}
- **Asset:** what's being protected (credentials, PII, money, availability).
- **Entry points:** how untrusted input reaches it (HTTP body, upload, queue message, MCP/agent output).
- **Threats (STRIDE-lite):**
  - Spoofing — {{can identity be faked?}}
  - Tampering — {{can data/requests be altered in transit / at rest?}}
  - Repudiation — {{is the action audited?}}
  - Info disclosure — {{what leaks in errors / logs / responses?}}
  - Denial of service — {{rate limit? resource exhaustion?}}
  - Elevation of privilege — {{can a normal user reach admin scope? IDOR?}}
- **Mitigations:** {{what's in place — link to code / SECURITY.md section}}
- **Failure-mode test:** {{the integration test that exercises the threat}}

## Agent-era additions (this codebase uses AI agents)

- **Indirect prompt injection** — external content (fetched URLs, uploaded docs, MCP/tool
  output) is wrapped in `<untrusted>` and never treated as instructions. (SECURITY.md §2.)
- **Tool poisoning / supply chain** — MCP servers + dependencies vetted before adoption
  (reputation + CVE scan); see global rule (h). New MCP server = a threat-model entry here.
- **Credential exfiltration** — agents must not splice `.env` into commit messages, write
  tokens to error logs, or upload folders to external "debug" services. Caught by the
  cleanup-scanner + pre-commit hook.

## Sensitive surfaces in THIS repo

{{List the actual auth/crypto/payments/PII surfaces here, each with an entry above.}}
