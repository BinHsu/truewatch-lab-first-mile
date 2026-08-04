# Runbook — TrueWatch credentials → local `.env` (OWL + ingest)

How to obtain console credentials, map them into this lab’s local `.env`, verify
OWL CLI, and prepare Workspace Token + DataWay for ingest (ADR-0001).

**Secrets stay in gitignored `.env` only.** Never paste tokens into chat,
commits, or this file.

## Credential names (do not mix)

| Lab use | What it is | Console path | Typical shape |
|---|---|---|---|
| OWL / Open API | **API Key Secret** (`DF-API-KEY`) | **Management → API Key Management** ([docs](https://docs.truewatch.com/management/api-key/)) | Key (Secret) from API Key details — **not** Key ID |
| DataKit + DataWay write | **Workspace Token** | **Management → Workspace Settings → Token** | usually starts with `tkn_` |
| RUM Public DataWay only | RUM **Client Token** | **Management → Client Tokens** ([docs](https://docs.truewatch.com/management/client-token/)) | hex-like; **cannot** call Open API / OWL |

**Gotcha `[VERIFIED]` 2026-08-04:** creating `lab-first-mile-owl` under **Client Tokens** produced a RUM Client Token. DataWay ingest still worked (Workspace Token). `owl exec` / Open API returned `401 ft.InvalidAPIKey`. OWL needs an **API Key Secret**, not a Client Token.

**Working paths `[VERIFIED]` 2026-08-04:** **Management → API Key Management**, or account menu **Personal API Key** — put the Secret in `OWL_TOKEN` / `OWL_API_KEY` / `TRUEWATCH_API_KEY`. Then `owl workspace list` succeeds.

OWL rules: [`docs/truewatch-owl.md`](../truewatch-owl.md).  
Status: [`docs/handoff/CURRENT.md`](../handoff/CURRENT.md).

---

## 1. Create local env file

From the repo root:

```bash
cp .env.example .env
```

Edit **`.env`**. Do not put real secrets in `.env.example`.

---

## 2. Confirm workspace site

You need the site so OWL endpoints match the workspace.

1. Log into the TrueWatch console for your trial workspace.
2. Confirm the correct workspace in the top-left switcher.
3. Open **Management → Workspace Settings**.
4. Note **Site** (for example Oregon / Singapore / Frankfurt).
5. Optionally cross-check the login host prefix: `us1-auth`, `ap1-auth`, `eu1-auth`, …

| Site | `OWL_REGISTRY_ENDPOINT` | `OWL_MCP_URL` | `DATAWAY_URL` (host only) |
|---|---|---|---|
| Global 1 (Oregon) | `https://us1-owl-api.truewatch.com` | `https://us1-owl-mcp.truewatch.com/mcp` | `https://us1-openway.truewatch.com` |
| Europe 1 (Frankfurt) | `https://eu1-owl-api.truewatch.com` | `https://eu1-owl-mcp.truewatch.com/mcp` | `https://eu1-openway.truewatch.com` |
| Asia Pacific 1 (Singapore) | `https://ap1-owl-api.truewatch.com` | `https://ap1-owl-mcp.truewatch.com/mcp` | `https://ap1-openway.truewatch.com` |
| Africa 1 (South Africa) | `https://za1-owl-api.truewatch.com` | `https://za1-owl-mcp.truewatch.com/mcp` | `https://za1-openway.truewatch.com` |
| Indonesia 1 (Jakarta) | `https://id1-owl-api.truewatch.com` | `https://id1-owl-mcp.truewatch.com/mcp` | `https://id1-openway.truewatch.com` |
| Middle East 1 (UAE) | `https://me1-owl-api.truewatch.com` | `https://me1-owl-mcp.truewatch.com/mcp` | `https://me1-openway.truewatch.com` |

`DATAWAY_URL` for **id1** was probed reachable (`curl -I` → HTTP 400, host exists)
`[VERIFIED]` 2026-08-04. Prefer the URL embedded in **Integrations → DataKit**
install command if it differs from the table.

Do **not** append `/api/v1` to `OWL_REGISTRY_ENDPOINT`.

Install package base URL (usually fixed):

```text
OWL_INSTALL_BASE_URL=https://static.truewatch.com/owl
```

---

## 3. Create the Open API Key (for OWL)

Requires Administrator or Owner. Official path:
[API Keys Management](https://docs.truewatch.com/management/api-key/).

1. Console → left nav **Management → API Key Management**  
   (UI may say **API Keys**. **Do not** use **Client Tokens** — that is RUM-only.)
2. Upper right → **Create Key**.
3. Suggested fields:
   - **Name:** `lab-first-mile-owl-openapi`
   - **Role:** read-capable workspace role (widen later for monitor/dashboard writes)
   - **Note:** `truewatch-lab-first-mile OWL CLI / Open API`
4. Confirm / save.
5. Open key details → copy **Key (Secret)** only (not Key ID).
6. This Secret is `DF-API-KEY` for Open API and `OWL_TOKEN` / `OWL_API_KEY`.

If you only see **Client Tokens** and no **API Key Management**, search Management
for “API Key”, or use an Owner account — some roles may not see that menu.

Verify after updating `.env` (no secrets in chat):

```bash
set -a && source .env && set +a
export PATH="$HOME/.local/bin:$PATH"
owl workspace list    # must NOT return ft.InvalidAPIKey
```

---

## 4. Map Secret → `.env` keys

Put the **same** Key (Secret) into all three token keys so local tools that read
different names still work:

| `.env` key | Value | Used for |
|---|---|---|
| `TRUEWATCH_API_KEY` | Key (Secret) | Lab alias |
| `OWL_TOKEN` | same | OWL CLI (official) |
| `OWL_API_KEY` | same | Alias of `OWL_TOKEN`; **wins if both are set** |

Uncomment / set site endpoints:

| `.env` key | Value |
|---|---|
| `OWL_REGISTRY_ENDPOINT` | Site row from §2 |
| `OWL_INSTALL_BASE_URL` | `https://static.truewatch.com/owl` |
| `OWL_MCP_URL` | Site MCP URL from §2 (safe to fill now; wire MCP later) |

Example shape for Oregon (replace the secret locally):

```bash
TRUEWATCH_API_KEY=<Key Secret>
OWL_TOKEN=<Key Secret>
OWL_API_KEY=<Key Secret>
OWL_MCP_URL=https://us1-owl-mcp.truewatch.com/mcp
OWL_REGISTRY_ENDPOINT=https://us1-owl-api.truewatch.com
OWL_INSTALL_BASE_URL=https://static.truewatch.com/owl
```

---

## 5. Workspace Token + DataWay URL (ingest — forker checklist)

Needed for ADR-0001 paths **DataKit** and **DataWay** direct write (and later
as DataKit’s upstream when using **DDTrace → DataKit**).  
Docs: [Workspace Settings / Token](https://docs.truewatch.com/management/settings/),
[DataKit host install](https://docs.truewatch.com/datakit/datakit-install/).

### Step W1 — open Workspace Settings

1. Log into the TrueWatch console.
2. Confirm the correct workspace (top-left).
3. Left nav → **Management → Workspace Settings**  
   (same page as §2 Site).

### Step W2 — copy Workspace Token

1. In **Basic Information**, find **Token**  
   (docs: “authentication key for data reporting”; **Owner or Administrator** can view — see [Workspace Settings](https://docs.truewatch.com/management/settings/)).
2. Click the **copy** control next to Token (or reveal, then copy).
3. Expect a value that often starts with `tkn_` (DataKit Token in product FAQ).
4. Paste into local `.env` only — never into git, chat, or screenshots you share.

**Permission blocked** (seen on this lab’s trial UI, 2026-08-04): if Token is
masked and a tooltip says you do not have permission to view Token content,
your console role cannot read it. The Open API Key (§3) and RUM Client Token
are different credentials and **cannot** substitute for Workspace Token.

Unblock options (owner of the workspace):

1. Sign in as a user with **Owner** or **Administrator** on that workspace, reopen
   **Management → Workspace Settings**, copy Token; or
2. **Management → Members** — raise the lab user’s role to Administrator (or have
   Owner paste Token into the local `.env` out-of-band); or
3. If the product allows Token **Replace** only for Owner: Owner rotates/copies
   Token and shares it securely once (not via public chat/git).

Do **not** use:
- the Open API Key Secret from §3, or
- a RUM **Client Token** from **Management → Client Tokens**.

### Step W3 — get the DataWay URL for your site

**Preferred (matches console install command):**

1. Left nav → **Integrations → DataKit**.
2. Select your OS (e.g. macOS / Linux).
3. Copy the install one-liner. It contains something like:

   ```bash
   DK_DATAWAY=https://<site>-openway.truewatch.com?token=<TOKEN> ...
   ```

4. From that string:
   - host part → `DATAWAY_URL` (no `?token=…`)
   - full `https://…?token=…` → `DK_DATAWAY` (used when installing DataKit)
   - token query value should match the Workspace Token from W2

**If the install page is unavailable**, use the `DATAWAY_URL` column in §2 for
your site. This lab’s workspace is **id1**:

```text
DATAWAY_URL=https://id1-openway.truewatch.com
```

Optional reachability check (no secret; 400/404 both mean the host answered):

```bash
curl -sS -o /dev/null -w '%{http_code}\n' -I https://id1-openway.truewatch.com
```

### Step W4 — map into `.env`

Add or fill these keys in **`.env`** (names also listed in `.env.example`):

| `.env` key | Value | Used for |
|---|---|---|
| `TRUEWATCH_WORKSPACE_TOKEN` | Workspace Token from W2 | DataWay writes; DataKit auth |
| `DATAWAY_URL` | `https://id1-openway.truewatch.com` (or your site) | Base host for direct write |
| `DK_DATAWAY` | `${DATAWAY_URL}?token=${TRUEWATCH_WORKSPACE_TOKEN}` | Official DataKit install env |

Example shape for **id1** (secret redacted):

```bash
TRUEWATCH_WORKSPACE_TOKEN=tkn_xxxxxxxx
DATAWAY_URL=https://id1-openway.truewatch.com
DK_DATAWAY=https://id1-openway.truewatch.com?token=tkn_xxxxxxxx
```

Direct write URL pattern (emitters will use this later):

```text
${DATAWAY_URL}/v1/write/metric?token=${TRUEWATCH_WORKSPACE_TOKEN}
${DATAWAY_URL}/v1/write/logging?token=${TRUEWATCH_WORKSPACE_TOKEN}
```

### Step W5 — sanity check (no secret echo)

```bash
cd /path/to/truewatch-lab-first-mile
set -a && source .env && set +a
echo "dataway=${DATAWAY_URL}"
case "${TRUEWATCH_WORKSPACE_TOKEN}" in
  tkn_*) echo "workspace_token=set (tkn_ prefix)" ;;
  "")    echo "workspace_token=MISSING" ;;
  *)     echo "workspace_token=set (len=${#TRUEWATCH_WORKSPACE_TOKEN}; confirm it is Workspace Token not API Key)" ;;
esac
test -n "${DK_DATAWAY}" && echo "dk_dataway=set" || echo "dk_dataway=MISSING"
```

Report back only: site prefix, whether W5 printed `set`, and that you did **not**
paste the token.

---

## 6. Install OWL CLI and verify (forker checklist)

Prerequisites: §1–§4 done (local `.env` filled; never commit it).  
Needs: `bash`, `curl`, `tar`. Official install doc:
https://docs.truewatch.com/owl/install-owl/

These commands were run successfully on macOS arm64 against the `id1` site
(`[VERIFIED]` 2026-08-04 → `owl` v1.1.1, `owl sync` → 13 categories). Your site
prefix may differ; the commands stay the same.

### Step A — load env from repo root

```bash
cd /path/to/truewatch-lab-first-mile
set -a && source .env && set +a

# sanity (prints endpoints only — do not echo token values)
echo "registry=${OWL_REGISTRY_ENDPOINT}"
echo "mcp=${OWL_MCP_URL}"
echo "install_base=${OWL_INSTALL_BASE_URL}"
test -n "${OWL_TOKEN}${OWL_API_KEY}" && echo "token=set" || echo "token=MISSING"
```

### Step B — online install

```bash
OWL_INSTALL_BASE_URL="${OWL_INSTALL_BASE_URL}" \
OWL_REGISTRY_ENDPOINT="${OWL_REGISTRY_ENDPOINT}" \
OWL_TOKEN="${OWL_TOKEN:-$OWL_API_KEY}" \
bash -c "$(curl -fsSL "${OWL_INSTALL_BASE_URL}/install.sh")" -- --yes
```

Expect roughly:

- download `owl-cli-<os>-<arch>-<version>.tar.gz` + checksum OK
- binary at `$HOME/.local/bin/owl`
- config dir `$HOME/.owl` (writes `config.yaml`; may store token locally)
- registry endpoint matches your `.env`
- hint to restart shell / `source ~/.zshrc` if PATH was updated

Windows: use the PowerShell flow in the official install doc (same three env vars).

### Step C — put `owl` on PATH in this shell

```bash
export PATH="$HOME/.local/bin:$PATH"
# or: source ~/.zshrc   # after install on macOS/Linux zsh
which owl
# expect: .../.local/bin/owl
```

### Step D — verify binary + credentials

```bash
set -a && source .env && set +a   # env overrides profile for this process
export PATH="$HOME/.local/bin:$PATH"

owl version
owl config show
```

Expect:

- `owl version` prints a version (lab saw `v1.1.1`)
- `Registry Endpoint:` equals your `OWL_REGISTRY_ENDPOINT`
- `API Key Source:` / `Credential Source:` shows env (`OWL_API_KEY` or `OWL_TOKEN`)
- Do **not** paste `owl config show` into issues/PRs — it can reveal key fragments

### Step E — sync tool catalog

```bash
owl sync
```

Expect: exit 0 and a list of categories (lab saw 13, including `data`, `monitor`,
`dashboard`, …). Cache lands under `$HOME/.owl/cache/`.

### Step F — failure triage

| Symptom | Likely cause |
|---|---|
| auth / 401 / invalid key | Wrong Secret (Key ID instead of Secret), or empty `.env` |
| connection / DNS / TLS to registry | Wrong site endpoint for the workspace |
| `owl: command not found` | PATH missing `$HOME/.local/bin`; redo Step C |
| sync permission error | Client Token role too narrow for catalog sync |

Re-run Step B to upgrade; it is safe to repeat with the same `.env`.

### Step G — done when

1. `which owl` resolves  
2. `owl sync` exits 0  
3. Continue from `docs/handoff/CURRENT.md` (next lab milestone after CLI)

Optional later: install
[owl-diagnostics](https://github.com/TrueWatchTech/ai-skills/tree/main/owl-diagnostics)
for agent-assisted diagnostics (needs a working local `owl`).

---

## 7. What to report back (no secrets)

After §5 and/or §6:

1. Site prefix (`us1` / `ap1` / `id1` / …)
2. Whether §5 W5 shows workspace token + `DK_DATAWAY` set (yes/no)
3. `owl version` line only (if §6 done)
4. Whether `owl sync` succeeded and roughly how many categories

Never paste Workspace Token, API Key Secret, full `owl config show`, `DK_DATAWAY`, or `.env` contents.
