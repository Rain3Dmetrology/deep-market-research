#!/usr/bin/env python3
"""Source health monitor prototype for the deep-market-research (dmr) skill.

Maintainer-side CI helper. Probes each registered source for liveness and
enforces a PR consistency gate (deprecated sources must not be referenced as
active routes; registry <-> docs parity is reported as warnings).

Pure standard library + PyYAML. No secrets are ever hard-coded; all external
URLs use $ENV_VAR placeholders and all logging redacts query/key material.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

try:
    import yaml
except ImportError:  # pragma: no cover - yaml is installed in CI
    yaml = None


# --- Paths -----------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_REGISTRY = "sources.registry.yaml"


# --- Source alias table (doc name -> registry key) --------------------------

# Heuristic mapping from the human-readable names used inside SKILL.md /
# references/*.md to the canonical registry keys. Used by check_consistency()
# to build the set of documented sources (S_doc).
KNOWN_SOURCES = {
    "Hacker News": "hn",
    "Reddit": "reddit",
    "Twitter": "twitter_x",
    "Twitter/X": "twitter_x",
    "GitHub": "github",
    "Hugging Face": "huggingface",
    "ModelScope": "modelscope",
    "arXiv": "arxiv",
    "Semantic Scholar": "semantic_scholar",
    "Crossref": "crossref",
    "OpenAlex": "openalex",
    "Firecrawl": "firecrawl",
    "Exa": "exa",
    "Tavily": "tavily",
    "Zhihu": "zhihu",
    "Patsnap": "patsnap",
    "Connected Papers": "connected_papers",
    "FRED": "fred",
    "midu": "midu_hotsearch",
    "WeChat MP": "wechat_mp_rss",
    # v2.8 / 审计 T-03：SKILL.md L107 既有提及而三表漏登记，按 2026-08-29 凭据直测注册。
    "AgentKey": "agentkey",
}

# Documented tools that are intentionally NOT in the registry (external skills /
# local MCPs / third-party backends routed elsewhere). Used by the M2/T-07
# blind-spot heuristic to avoid warning on known, deliberately unmonitored
# names; new unknown mentions still surface as WARN.
KNOWN_EXTERNAL_TOOLS = {
    "wechat-article-search",
    "ReadGZH-Agent",
    "douyinmcp",
    "TikHub",
    "tdx-connector",
    "Algolia",
}

# Reverse mapping: registry key -> list of doc aliases (for the deprecated
# "still referenced" blocking check).
KEY_TO_ALIASES = {}
for _alias, _key in KNOWN_SOURCES.items():
    KEY_TO_ALIASES.setdefault(_key, []).append(_alias)

# Tokens that, when co-occurring with a source mention, mark the mention as a
# deprecation / removal notice rather than an active routing instruction.
_DEPRECATION_MARKERS = re.compile(
    r"弃用|deprecat|已弃|删除|removed|替代|replaced|不兼容|oauth|"
    r"discontinu|retir|下线|停用|removed from|no longer",
    re.IGNORECASE,
)


def _active_reference_lines(doc_text, token):
    """Yield doc lines that mention `token` WITHOUT a deprecation marker.

    A deprecated source that is only mentioned inside a deprecation/removal
    notice is NOT treated as an active route (so it must not block CI).
    """
    for line in doc_text.splitlines():
        if re.search(r"\b" + re.escape(token) + r"\b", line, re.IGNORECASE):
            if _DEPRECATION_MARKERS.search(line):
                continue
            yield line


# --- URL env substitution & redaction ---------------------------------------

_ENV_PATTERN = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")


def _substitute_env(url):
    """Replace $ENV_VAR placeholders with real env values.

    Returns (resolved_url, missing) where `missing` is a list of env var names
    that were referenced but unset. If `missing` is non-empty the source must
    be skipped.
    """
    missing = []

    def _repl(match):
        name = match.group(1)
        val = os.environ.get(name)
        if val is None or val == "":
            missing.append(name)
            return ""
        return val

    resolved = _ENV_PATTERN.sub(_repl, url)
    return resolved, missing


def redact_url(url):
    """Mask query-string / key material for safe logging.

    `?key=abcd` -> `?key=***`; path-embedded secrets are likewise masked. The
    scheme/host/path structure is preserved so logs stay useful.
    """
    if "?" not in url:
        return url
    base, _, query = url.partition("?")
    redacted_pairs = []
    for pair in query.split("&"):
        if "=" in pair:
            k, _, _v = pair.partition("=")
            redacted_pairs.append("%s=***" % k)
        else:
            redacted_pairs.append(pair)
    return "%s?%s" % (base, "&".join(redacted_pairs))


# --- Action / aggregation rules ---------------------------------------------

def _action(status, layer):
    """Decide the maintainer action for a single probe result.

    Only a *default-layer* source whose status is DEAD or REGRESSED requires an
    issue + uncovered-dimension marking. Everything else (optional layer at any
    status, DEGRADED, DEPRECATED) is a backoff+log situation.

    Disclosure note (audit L5): "open_issue+mark_uncovered" is a maintainer
    follow-up label, NOT an automation -- no issue is filed automatically
    (人工跟进，无自动开 issue 动作); the action string is also printed
    verbatim in main() alongside the same note.
    """
    if layer == "default" and status in ("DEAD", "REGRESSED"):
        return "open_issue+mark_uncovered"
    return "backoff+log"


# --- Probing ----------------------------------------------------------------

DEFAULT_TIMEOUT = 15.0
DEGRADED_BACKOFF = 5.0


def run_probe(registry):
    """Probe every non-deprecated source; return a list of result dicts.

    Each result: {key, name, url(redacted), layer, needs_key, status, action,
    detail}. DEPRECATED sources and sources whose env placeholder is missing are
    skipped (not probed).
    """
    results = []
    for key, spec in registry.items():
        name = spec.get("name", key)
        layer = spec.get("layer", "default")
        needs_key = bool(spec.get("needs_key", False))
        status_field = str(spec.get("status", "")).upper()

        # DEPRECATED sources are never probed.
        if status_field == "DEPRECATED" or layer == "deprecated":
            results.append({
                "key": key, "name": name, "url": redact_url(spec.get("url", "")),
                "layer": layer, "needs_key": needs_key,
                "status": "DEPRECATED", "action": "backoff+log",
                "detail": "deprecated; probe skipped",
            })
            continue

        url = spec.get("url", "")
        probe_type = str(spec.get("probe_type", "url")).lower()
        resolved, missing = _substitute_env(url)
        if missing:
            # Required env var(s) absent -> skip this source (no penalty).
            # For MCP probes this doubles as the "no credential -> skip, never
            # misjudge as DEAD" contract demanded by audit T-03 acceptance #1.
            results.append({
                "key": key, "name": name, "url": redact_url(url),
                "layer": layer, "needs_key": needs_key,
                "status": "SKIPPED", "action": "backoff+log",
                "detail": "missing env: %s" % ",".join(sorted(set(missing))),
            })
            continue

        if probe_type == "mcp":
            # v2.8 / audit T-03: MCP-only services (e.g. AgentKey) have no
            # REST surface -- _http_probe (URL GET only) cannot probe them.
            token_env = str(spec.get("auth_env", "") or "")
            token = os.environ.get(token_env, "") if token_env else ""
            if not token:
                results.append({
                    "key": key, "name": name, "url": redact_url(resolved),
                    "layer": layer, "needs_key": needs_key,
                    "status": "SKIPPED", "action": "backoff+log",
                    "detail": "mcp probe needs a valid credential (auth_env: %s); skipped, not failed"
                              % (token_env or "unset"),
                })
                continue
            status, detail = _mcp_probe(resolved, token)
            results.append({
                "key": key, "name": name, "url": redact_url(resolved),
                "layer": layer, "needs_key": needs_key,
                "status": status, "action": _action(status, layer),
                "detail": detail,
            })
            continue

        if probe_type != "url":
            # custom / future probe types (e.g. header-auth REST like X API v2):
            # the plain _http_probe cannot express them; report SKIP instead of
            # faking a passing probe (audit M3).
            results.append({
                "key": key, "name": name, "url": redact_url(resolved),
                "layer": layer, "needs_key": needs_key,
                "status": "SKIPPED", "action": "backoff+log",
                "detail": "probe_type=%s not supported by _http_probe (URL-only); "
                          "manual/custom probe required" % probe_type,
            })
            continue

        status, detail = _http_probe(resolved)
        results.append({
            "key": key, "name": name, "url": redact_url(resolved),
            "layer": layer, "needs_key": needs_key,
            "status": status, "action": _action(status, layer),
            "detail": detail,
        })
    return results


def _http_probe(url):
    """Perform a single HTTP probe; map the outcome to a status string."""
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "dmr-source-health/0.1 (+maintainer-ci)",
        "Accept": "*/*",
    })
    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            code = resp.getcode()
            if code == 429:
                time.sleep(DEGRADED_BACKOFF)
                return "DEGRADED", "HTTP 429 rate-limited; backed off"
            if code != 200:
                return "DEAD", "HTTP %s" % code
            body = resp.read()
            if not body or not body.strip():
                return "DEGRADED", "HTTP 200 but empty body"
            return "ALIVE", "HTTP 200, %d bytes" % len(body)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(DEGRADED_BACKOFF)
            return "DEGRADED", "HTTP 429 rate-limited; backed off"
        return "DEAD", "HTTPError %s" % e.code
    except Exception as e:  # timeout / URLError / etc.
        return "DEAD", "exception: %s" % type(e).__name__


def _mcp_probe(url, token):
    """Minimal MCP (Streamable HTTP) health probe; maps outcome to a status.

    v2.8 / audit T-03: `_http_probe` only supports plain URL probes, which
    cannot observe MCP-only services (no REST surface; everything behind a
    JSON-RPC handshake). This probe performs the minimum MCP `initialize`
    handshake: a single JSON-RPC 2.0 POST with Bearer auth. The response
    `result.serverInfo` (or any `result`) proves the endpoint is live and
    speaks MCP -- deliberately cheaper than an `execute_tool` round-trip so
    the probe never consumes paid credits. Redaction note: the token travels
    in a request header (never in the URL), so `redact_url` stays sufficient.
    """
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "dmr-source-health", "version": "0.2"},
        },
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "User-Agent": "dmr-source-health/0.2 (+maintainer-ci)",
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % token,
    })
    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            code = resp.getcode()
            if code == 429:
                time.sleep(DEGRADED_BACKOFF)
                return "DEGRADED", "HTTP 429 rate-limited; backed off"
            if code != 200:
                return "DEAD", "HTTP %s" % code
            body = resp.read(65536)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(DEGRADED_BACKOFF)
            return "DEGRADED", "HTTP 429 rate-limited; backed off"
        if e.code in (401, 403):
            return "DEAD", "HTTPError %s (credential rejected)" % e.code
        return "DEAD", "HTTPError %s" % e.code
    except Exception as e:  # timeout / URLError / etc.
        return "DEAD", "exception: %s" % type(e).__name__
    if not body or not body.strip():
        return "DEGRADED", "HTTP 200 but empty body"
    head = body.decode("utf-8", errors="replace")[:4096]
    # SSE-wrapped or plain JSON responses both contain the JSON-RPC payload.
    if '"result"' in head:
        return "ALIVE", "MCP initialize handshake ok (HTTP 200, %d bytes)" % len(body)
    if '"error"' in head:
        return "DEGRADED", "MCP initialize returned a JSON-RPC error"
    return "DEGRADED", "HTTP 200 but no MCP initialize result in body"


# --- Aggregation ------------------------------------------------------------

def aggregate(results):
    """Compute summary metrics from probe results."""
    dimensions_uncovered = sum(
        1 for r in results
        if r["layer"] == "default" and r["status"] in ("DEAD", "REGRESSED")
    )
    actions = {r["key"]: r["action"] for r in results}
    return {
        "dimensions_uncovered": dimensions_uncovered,
        "total": len(results),
        "by_status": _count_by(results, "status"),
        "actions": actions,
    }


def _count_by(results, field):
    out = {}
    for r in results:
        out[r[field]] = out.get(r[field], 0) + 1
    return out


# --- Consistency gate (static, no network) ----------------------------------

# M2/T-07 blind-spot heuristic: "<name> MCP/API/skill" mentions in SKILL.md /
# references/data-sources.md that map to no registry entry surface as WARN
# (never BLOCK) so "structural blindness" stays observable. False positives
# are accepted by design; known names are filtered via KNOWN_SOURCES aliases,
# KNOWN_EXTERNAL_TOOLS, registry keys/names and a generic-word stoplist.
_DOC_TOOL_CANDIDATE = re.compile(r"([A-Za-z][A-Za-z0-9]*(?:[ _-][A-Za-z0-9]+)*?)\s+(?:MCP|API|skill)\b")
_GENERIC_TOOL_WORDS = {
    "rest", "api", "mcp", "http", "https", "url", "json", "rss", "cli", "sdk",
    "seo", "saas", "the", "and", "for", "not", "no", "se", "peer", "keyless",
    "web", "app", "token", "key", "search", "free", "open", "public", "remote",
    "local", "official", "via", "based", "hosted", "stdio", "bearer",
    "streamable", "any", "some", "this", "that", "with", "using", "skill",
    "our", "its", "per", "one", "two",
}


def _candidate_tool_names(doc_text):
    """Scan doc text for tool-name candidates not covered by any known table.

    Returns a sorted list of human-readable names. Used by check_consistency()
    to emit WARN-level "new tool mention" findings (audit M2 / T-07).
    """
    aliases = set(a.lower() for a in KNOWN_SOURCES) | set(a.lower() for a in KNOWN_EXTERNAL_TOOLS)
    out = set()
    for m in _DOC_TOOL_CANDIDATE.finditer(doc_text):
        name = m.group(1).strip()
        low = name.lower()
        words = re.split(r"[ _-]+", low)
        if not words or len(words[0]) < 3:
            continue
        if any(w in _GENERIC_TOOL_WORDS for w in words):
            continue
        # covered by a known alias in either direction
        # ("Hugging Face Hub" contains alias "hugging face"; "patsnap-search"
        # contains alias "patsnap").
        if any(a in low or low in a for a in aliases):
            continue
        out.add(name)
    return sorted(out)


def _load_registry(registry_path):
    if yaml is None:
        raise RuntimeError("PyYAML is required to read the registry")
    with open(registry_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError("registry must be a mapping of source-id -> spec")
    return data


def _collect_doc_text(repo_root):
    texts = []
    skill = os.path.join(repo_root, "SKILL.md")
    if os.path.isfile(skill):
        with open(skill, "r", encoding="utf-8") as fh:
            texts.append(fh.read())
    ref_dir = os.path.join(repo_root, "references")
    if os.path.isdir(ref_dir):
        for fn in sorted(os.listdir(ref_dir)):
            if fn.endswith(".md"):
                with open(os.path.join(ref_dir, fn), "r", encoding="utf-8") as fh:
                    texts.append(fh.read())
    return "\n".join(texts)


def _blindspot_doc_text(repo_root):
    """M2/T-07 启发式扫描面（按审计定稿）：仅 SKILL.md + references/data-sources.md。

    刻意比 _collect_doc_text 窄：候选词探测只盯主管线入口与数据源清单，
    避免对可选工具指南等外围文档里的历史工具名反复告警。
    """
    texts = []
    for rel in ("SKILL.md", os.path.join("references", "data-sources.md")):
        p = os.path.join(repo_root, rel)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as fh:
                texts.append(fh.read())
    return "\n".join(texts)


def check_consistency(registry_path=None, out_path=None, repo_root=None):
    """Static PR consistency gate. No network calls.

    Blocking (exit 1): a registry source marked DEPRECATED (or layer
    'deprecated') is still referenced as an *active* route in SKILL.md or
    references/*.md.

    Warning-level (exit 0, written to parity_report.json): doc<->registry
    parity -- blind spots (documented but unmonitored) and orphan probes
    (monitored but undocumented, possibly stale).

    Returns the process exit code (1 if blocking, else 0).
    """
    registry_path = registry_path or os.path.join(REPO_ROOT, DEFAULT_REGISTRY)
    repo_root = repo_root or REPO_ROOT
    registry = _load_registry(registry_path)
    doc_text = _collect_doc_text(repo_root)

    blocking = []

    # 1) Blocking: deprecated sources must not be referenced as active routes.
    #    A mention that sits inside a deprecation/removal notice does NOT count
    #    as an active route (the source is documented as deprecated on purpose).
    for key, spec in registry.items():
        status_field = str(spec.get("status", "")).upper()
        layer = spec.get("layer", "default")
        if status_field == "DEPRECATED" or layer == "deprecated":
            aliases = KEY_TO_ALIASES.get(key, [])
            name = spec.get("name", "")
            referenced = False
            for alias in aliases:
                if any(_active_reference_lines(doc_text, alias)):
                    referenced = True
                    break
            if not referenced and name:
                if any(_active_reference_lines(doc_text, name)):
                    referenced = True
            if referenced:
                blocking.append(key)

    # 2) Parity: build S_doc from documented aliases, S_reg from registry keys.
    s_doc = set()
    for alias, mapped_key in KNOWN_SOURCES.items():
        if re.search(r"\b" + re.escape(alias) + r"\b", doc_text, re.IGNORECASE):
            s_doc.add(mapped_key)
    s_reg = set(registry.keys())
    # Audit T-10: deprecated registry entries are intentionally retained in the
    # registry (as deprecation records) while no longer actively documented.
    # Their doc<->registry gap is a *declared deprecation*, not an orphan
    # probe -- reporting them as orphans is stale noise (the probe itself is
    # already skipped in run_probe). Exclude them from the orphan diff; the
    # deprecated-as-active-route blocking check above stays untouched.
    s_deprecated = {
        key for key, spec in registry.items()
        if str(spec.get("status", "")).upper() == "DEPRECATED"
        or spec.get("layer", "default") == "deprecated"
    }
    blind = sorted(s_doc - s_reg)
    orphan = sorted((s_reg - s_doc) - s_deprecated)

    # 3) M2/T-07 blind-spot heuristic: doc-mentioned tool names absent from the
    #    mapping table AND the registry -> WARN (non-blocking by design).
    candidates = _candidate_tool_names(_blindspot_doc_text(repo_root))
    reg_lookup = {k.lower() for k in registry}
    reg_lookup |= {str(spec.get("name", "")).lower() for spec in registry.values()}
    candidates = [c for c in candidates if c.lower() not in reg_lookup]

    warnings = []
    if blind:
        warnings.append("blind spots (documented but unmonitored): %s" % blind)
    if orphan:
        warnings.append("orphan probes (monitored but undocumented, possibly stale): %s" % orphan)
    if candidates:
        warnings.append(
            "WARN: undocumented source candidates in docs (register them or map in "
            "KNOWN_SOURCES/KNOWN_EXTERNAL_TOOLS): %s" % candidates)
    if blocking:
        warnings.append("BLOCKING: deprecated sources still referenced as active routes: %s" % blocking)

    parity_report = {
        "blind": blind,
        "orphan": orphan,
        "new_tool_candidates": candidates,
        "warnings": warnings,
        "blocking": blocking,
    }
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(parity_report, fh, indent=2, ensure_ascii=False)
        print("[consistency] wrote parity report -> %s" % out_path)

    if blocking:
        print("[consistency] FAIL: deprecated sources still referenced: %s" % blocking)
    else:
        print("[consistency] OK: no deprecated source referenced as active route")
    print("[consistency] blind=%d orphan=%d" % (len(blind), len(orphan)))
    if candidates:
        print("[consistency] WARN: %d undocumented source candidate(s): %s" % (len(candidates), candidates))

    return 1 if blocking else 0


# --- CLI --------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="dmr source health monitor")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY,
                        help="path to sources.registry.yaml")
    parser.add_argument("--out", default="parity_report.json",
                        help="path to write the parity report JSON")
    args = parser.parse_args(argv)

    registry = _load_registry(args.registry)

    print("[probe] probing %d registered sources (deprecated skipped)..." % len(registry))
    results = run_probe(registry)
    summary = aggregate(results)
    # Audit L5 disclosure: `open_issue+mark_uncovered` is a maintainer
    # follow-up label only (人工跟进，无自动开 issue 动作) -- this run takes
    # no automated issue-filing action, exit code stays unchanged.
    for r in results:
        print("[probe] %-18s %-10s %-22s %s" % (
            r["key"], r["status"], r["action"], r.get("detail", "")))

    print("[summary] dimensions_uncovered=%d total=%d by_status=%s" % (
        summary["dimensions_uncovered"], summary["total"], summary["by_status"]))

    exit_code = check_consistency(registry_path=args.registry, out_path=args.out)
    print("[summary] blind/orphan reported in %s" % args.out)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
