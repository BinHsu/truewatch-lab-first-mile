#!/usr/bin/env python3
"""HTTP smoke for OWL MCP + Tobylike (legacy) MCP — twin of Cursor dual-server wiring.

Does not print secrets. Requires repo-root .env with OWL_TOKEN (or OWL_API_KEY).

Usage:
  python3 scripts/mcp-dual-smoke.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env() -> dict:
    env = {}
    path = ROOT / ".env"
    if not path.is_file():
        raise SystemExit("MISSING: .env")
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k] = v.strip().strip('"').strip("'")
    return env


def parse_body(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("{"):
        return json.loads(raw)
    data_lines = [line[5:].strip() for line in raw.splitlines() if line.startswith("data:")]
    for d in reversed(data_lines):
        if d and d != "[DONE]":
            return json.loads(d)
    raise ValueError("no jsonrpc body: " + raw[:300])


class McpClient:
    def __init__(self, url: str, auth_headers: dict, label: str):
        self.url = url
        self.auth = auth_headers
        self.label = label
        self.session_id = None
        self._id = 0

    def request(self, method: str, params=None, notification: bool = False):
        self._id += 1
        payload = {"jsonrpc": "2.0", "method": method}
        if not notification:
            payload["id"] = self._id
        if params is not None:
            payload["params"] = params
        body = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            **self.auth,
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(self.url, data=body, method="POST", headers=headers)
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8", "replace")
            for k, v in resp.headers.items():
                if k.lower() == "mcp-session-id":
                    self.session_id = v
            if notification or not raw.strip():
                return resp.status, None
            return resp.status, parse_body(raw)

    def handshake(self) -> dict:
        _, init = self.request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "lab-mcp-dual-smoke", "version": "0.3.0"},
            },
        )
        try:
            self.request("notifications/initialized", {}, notification=True)
        except urllib.error.HTTPError:
            # OWL often does not require session/notification; ignore.
            pass
        return (init or {}).get("result") or {}


def text_payload(rpc) -> str:
    content = ((rpc.get("result") or {}).get("content")) or []
    parts = []
    for c in content:
        if isinstance(c, dict) and c.get("type") == "text":
            parts.append(c.get("text") or "")
    return "\n".join(parts)


def smoke_owl(token: str) -> None:
    print("=== OWL MCP ===")
    url = "https://id1-owl-mcp.truewatch.com/mcp"
    c = McpClient(url, {"Authorization": f"Bearer {token}"}, "owl")
    info = c.handshake()
    print("serverInfo", info.get("serverInfo"))
    _, tools = c.request("tools/list", {})
    names = [t.get("name") for t in ((tools or {}).get("result") or {}).get("tools") or []]
    print("wrapper_tools", names)

    now = int(time.time() * 1000)
    start = now - 2 * 3600 * 1000
    print("window_ms", start, now)

    _, mon = c.request(
        "tools/call",
        {
            "name": "exec_tool",
            "arguments": {
                "tool_name": "owl.monitor.list",
                "parameters": {"search": "lab-first-mile"},
            },
        },
    )
    mon_text = text_payload(mon or {})
    print("owl.monitor.list_has_lab", "lab-first-mile" in mon_text)

    _, q = c.request(
        "tools/call",
        {
            "name": "exec_tool",
            "arguments": {
                "tool_name": "owl.data.simple_query",
                "parameters": {
                    "namespace": "M",
                    "source": "truewatch_lab_first_mile",
                    "select_clause": "last(ping), count(ping)",
                    "where_clause": "path = 'dataway'",
                    "start_time": start,
                    "end_time": now,
                },
            },
        },
    )
    q_text = text_payload(q or {})
    print("owl.simple_query_snippet", q_text[:240].replace("\n", " "))
    if "last(ping)" not in q_text:
        raise SystemExit("OWL smoke failed: simple_query missing last(ping)")


def smoke_toby(token: str) -> None:
    print("=== Tobylike MCP (legacy) ===")
    url = "https://us1-toby-ai.truewatch.com/toby_ai_mcp/mcp"
    # SITE_KEY for Indonesia / id1 OpenAPI is id2 (docs SITE_KEY_MAP).
    c = McpClient(url, {"Authorization": f"{token};Endpoint=id2"}, "toby")
    info = c.handshake()
    print("serverInfo", info.get("serverInfo"))
    if not c.session_id:
        raise SystemExit("Tobylike smoke failed: missing Mcp-Session-Id")
    _, tools = c.request("tools/list", {})
    names = [t.get("name") for t in ((tools or {}).get("result") or {}).get("tools") or []]
    print("tools", names)

    _, checkers = c.request(
        "tools/call",
        {"name": "list_checkers", "arguments": {"page_index": 1, "page_size": 50}},
    )
    ch_text = text_payload(checkers or {})
    lab_hits = ch_text.count("lab-first-mile")
    print("list_checkers_lab_hits", lab_hits)
    if lab_hits < 1:
        raise SystemExit(
            "Tobylike smoke failed: no lab-first-mile checkers (wrong Endpoint?)"
        )

    dql = (
        "M::`truewatch_lab_first_mile`:(last(`ping`), count(`ping`)) "
        "{ path = 'dataway' }"
    )
    _, metric = c.request(
        "tools/call",
        {
            "name": "query_metric_data",
            "arguments": {"dql": dql, "time_delta": 7200000},
        },
    )
    m_text = text_payload(metric or {})
    print("query_metric_data_has_series", "last(ping)" in m_text)
    if "last(ping)" not in m_text:
        raise SystemExit("Tobylike smoke failed: metric query empty/missing last(ping)")


def main() -> None:
    env = load_env()
    token = env.get("OWL_TOKEN") or env.get("OWL_API_KEY") or env.get("TRUEWATCH_ACCESS_TOKEN")
    if not token:
        raise SystemExit("MISSING: OWL_TOKEN")
    print("mcp_dual_smoke=1")
    smoke_owl(token)
    smoke_toby(token)
    print("mcp_dual_smoke=OK")
    print("finished_utc=" + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:400]
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        raise SystemExit(1)
