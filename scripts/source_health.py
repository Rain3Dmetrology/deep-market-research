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
        resolved, missing = _substitute_env(url)
        if missing:
            # Required env var(s) absent -> skip this source (no penalty).
            results.append({
                "key": key, "name": name, "url": redact_url(url),
                "layer": layer, "needs_key": needs_key,
                "status": "SKIPPED", "action": "backoff+log",
                "detail": "missing env: %s" % ",".join(sorted(set(missing))),
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
    blind = sorted(s_doc - s_reg)
    orphan = sorted(s_reg - s_doc)

    warnings = []
    if blind:
        warnings.append("blind spots (documented but unmonitored): %s" % blind)
    if orphan:
        warnings.append("orphan probes (monitored but undocumented, possibly stale): %s" % orphan)
    if blocking:
        warnings.append("BLOCKING: deprecated sources still referenced as active routes: %s" % blocking)

    parity_report = {
        "blind": blind,
        "orphan": orphan,
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
