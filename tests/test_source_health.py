"""Real unit tests for scripts/source_health.py.

These resolve review limitation #4 ("仓库零测试"): the new source-health
module now ships with executable tests instead of planning-only conclusions.

Run:  pytest tests/test_source_health.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import source_health as s  # noqa: E402


# --- _action gate ----------------------------------------------------------

def test_action_default_dead_opens_issue():
    assert s._action("DEAD", "default") == "open_issue+mark_uncovered"
    assert s._action("REGRESSED", "default") == "open_issue+mark_uncovered"


def test_action_optional_never_opens_issue():
    # architect spec: fred is optional -> even DEAD only backoff+log
    assert s._action("DEAD", "optional") == "backoff+log"
    assert s._action("REGRESSED", "optional") == "backoff+log"


def test_action_degraded_not_blocking():
    assert s._action("DEGRADED", "default") == "backoff+log"
    assert s._action("DEGRADED", "optional") == "backoff+log"


# --- aggregate --------------------------------------------------------------

def test_aggregate_excludes_optional_from_dimensions_uncovered():
    results = [
        {"layer": "default", "status": "DEAD", "key": "a", "action": "open_issue+mark_uncovered"},
        {"layer": "optional", "status": "DEAD", "key": "fred", "action": "backoff+log"},
        {"layer": "default", "status": "ALIVE", "key": "b", "action": "backoff+log"},
        {"layer": "optional", "status": "REGRESSED", "key": "c", "action": "backoff+log"},
    ]
    agg = s.aggregate(results)
    # only default+DEAD counts -> fred (optional) is excluded
    assert agg["dimensions_uncovered"] == 1


# --- redact_url -------------------------------------------------------------

def test_redact_url_masks_key():
    out = s.redact_url("https://api.example.com/x?api_key=SECRET123&b=2")
    assert "SECRET123" not in out          # raw secret value gone
    assert "api_key=***" in out            # key name preserved, value masked
    assert "b=***" in out                  # key name preserved, value masked
    assert "b=2" not in out                # raw value gone


# --- check_consistency (static, bidirectional parity) -----------------------

def _write_tmp_repo(tmp_path, registry_dict, skill_text):
    import yaml

    reg_path = tmp_path / "registry.yaml"
    reg_path.write_text(yaml.safe_dump(registry_dict), encoding="utf-8")
    (tmp_path / "SKILL.md").write_text(skill_text, encoding="utf-8")
    return reg_path


def test_check_consistency_bidirectional(tmp_path):
    registry = {
        "github": {"name": "GitHub", "url": "https://api.github.com", "layer": "default", "needs_key": False},
        "orphan_src": {"name": "Orphan", "url": "https://orphan.example", "layer": "default", "needs_key": False},
    }
    # docs mention GitHub (in registry) + Hugging Face (NOT in registry)
    skill = "We use GitHub and Hugging Face for research.\n"
    reg_path = _write_tmp_repo(tmp_path, registry, skill)
    out = tmp_path / "parity.json"
    rc = s.check_consistency(registry_path=str(reg_path), out_path=str(out), repo_root=str(tmp_path))
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert "huggingface" in rep["blind"]       # documented but unmonitored
    assert "orphan_src" in rep["orphan"]        # monitored but undocumented
    assert rep["blocking"] == []                # warnings only -> non-blocking
    assert rc == 0


def test_check_consistency_blocks_deprecated_as_active_route(tmp_path):
    registry = {
        "midu_hotsearch": {"name": "midu HotSearch", "url": "https://midu.com/x?app_secret=$MIDU_APP_SECRET",
                           "layer": "default", "needs_key": True, "status": "DEPRECATED"},
    }
    # midu referenced as an ACTIVE route (no deprecation marker on the line)
    skill = "You can still use midu for hotsearch aggregation.\n"
    reg_path = _write_tmp_repo(tmp_path, registry, skill)
    out = tmp_path / "parity.json"
    rc = s.check_consistency(registry_path=str(reg_path), out_path=str(out), repo_root=str(tmp_path))
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert rep["blocking"] == ["midu_hotsearch"]
    assert rc == 1  # CI must fail


def test_check_consistency_ignores_deprecated_mention_in_notice(tmp_path):
    registry = {
        "midu_hotsearch": {"name": "midu HotSearch", "url": "https://midu.com/x?app_secret=$MIDU_APP_SECRET",
                           "layer": "default", "needs_key": True, "status": "DEPRECATED"},
    }
    # midu only appears inside a deprecation/removal notice -> must NOT block
    skill = "midu was deprecated; use Firecrawl instead.\n"
    reg_path = _write_tmp_repo(tmp_path, registry, skill)
    out = tmp_path / "parity.json"
    rc = s.check_consistency(registry_path=str(reg_path), out_path=str(out), repo_root=str(tmp_path))
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert rep["blocking"] == []
    assert rc == 0


# --- T-03: AgentKey registration + MCP probe branch ---------------------------
# 守护场景：审计 T-03 验收标准 #1 —— _http_probe 仅支持 URL，MCP 型条目必须有独立
# 探针分支；无凭据时输出 SKIPPED 而非误判失败；不得照抄对方报告 yaml 示例。

def test_known_sources_maps_agentkey():
    assert s.KNOWN_SOURCES["AgentKey"] == "agentkey"


def test_registry_contains_agentkey_mcp_entry():
    import yaml as _yaml
    with open(os.path.join(REPO_ROOT, "sources.registry.yaml"), encoding="utf-8") as fh:
        reg = _yaml.safe_load(fh)
    ak = reg["agentkey"]
    assert ak["probe_type"] == "mcp"
    assert ak["url"] == "https://api.agentkey.app/v1/mcp"
    assert ak["auth_env"] == "AGENTKEY_API_KEY"
    # 凭据只走 $ENV 占位，绝不硬编码进探针 URL
    assert "AGENTKEY_API_KEY" not in ak["url"]
    # 数字必须标注实测来源（2026-08-29 凭据直测），且不得回填被证伪的事实（v1.14.0）
    assert "2026-08-29" in ak["note"] and "1981" in ak["note"]
    assert "v1.14.0" not in ak["note"]


def test_registry_twitter_x_m3_fix():
    # 守护场景：审计 M3 —— 域名 api.x.com，认证改请求头说明，不伪造可通过的探针。
    import yaml as _yaml
    with open(os.path.join(REPO_ROOT, "sources.registry.yaml"), encoding="utf-8") as fh:
        reg = _yaml.safe_load(fh)
    tw = reg["twitter_x"]
    assert tw["url"].startswith("https://api.x.com/")
    assert "bearer_token=" not in tw["url"]  # 凭据不再拼入 query
    assert tw["probe_type"] == "custom"      # 头部认证无法被 _http_probe 表达


class _FakeResp:
    def __init__(self, code=200, body=b'{"jsonrpc":"2.0","id":1,"result":{"serverInfo":{"name":"agentkey"}}}'):
        self._code = code
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def getcode(self):
        return self._code

    def read(self, limit=None):
        return self._body if limit is None else self._body[:limit]


def test_mcp_probe_alive_on_initialize_result(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["method"] = req.get_method()
        captured["auth"] = req.get_header("Authorization")
        return _FakeResp()

    monkeypatch.setattr(s.urllib.request, "urlopen", fake_urlopen)
    status, detail = s._mcp_probe("https://api.agentkey.app/v1/mcp", "test-key")
    assert status == "ALIVE", detail
    assert captured["method"] == "POST"          # JSON-RPC 握手，非 GET 探针
    assert captured["auth"] == "Bearer test-key"  # 凭据走请求头，不进 URL/日志


def test_mcp_probe_dead_on_credential_rejection(monkeypatch):
    import urllib.error

    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 401, "unauthorized", {}, None)

    monkeypatch.setattr(s.urllib.request, "urlopen", fake_urlopen)
    status, detail = s._mcp_probe("https://api.agentkey.app/v1/mcp", "bad-key")
    assert status == "DEAD"
    assert "401" in detail


def test_mcp_probe_degraded_on_non_mcp_body(monkeypatch):
    monkeypatch.setattr(s.urllib.request, "urlopen",
                        lambda req, timeout=None: _FakeResp(body=b"<html>not an mcp endpoint</html>"))
    status, _ = s._mcp_probe("https://api.agentkey.app/v1/mcp", "test-key")
    assert status == "DEGRADED"


def test_run_probe_mcp_without_credential_skips(monkeypatch):
    # 无凭据 -> SKIPPED（不误判失败），审计 T-03 验收标准 #1 的后半句。
    monkeypatch.delenv("AGENTKEY_API_KEY", raising=False)
    registry = {
        "agentkey": {"name": "AgentKey", "url": "https://api.agentkey.app/v1/mcp",
                     "layer": "optional", "needs_key": True,
                     "probe_type": "mcp", "auth_env": "AGENTKEY_API_KEY"},
    }

    def boom(url, token=None):
        raise AssertionError("no-credential MCP entry must not be probed")

    monkeypatch.setattr(s, "_mcp_probe", boom)
    results = s.run_probe(registry)
    assert results[0]["status"] == "SKIPPED"
    assert "credential" in results[0]["detail"]


def test_run_probe_mcp_with_credential_uses_mcp_branch(monkeypatch):
    monkeypatch.setenv("AGENTKEY_API_KEY", "dummy")
    registry = {
        "agentkey": {"name": "AgentKey", "url": "https://api.agentkey.app/v1/mcp",
                     "layer": "optional", "needs_key": True,
                     "probe_type": "mcp", "auth_env": "AGENTKEY_API_KEY"},
    }

    def http_boom(url):
        raise AssertionError("MCP entry must not fall into _http_probe")

    monkeypatch.setattr(s, "_http_probe", http_boom)
    monkeypatch.setattr(s, "_mcp_probe", lambda url, token: ("ALIVE", "stubbed handshake"))
    results = s.run_probe(registry)
    assert results[0]["status"] == "ALIVE"
    assert results[0]["detail"] == "stubbed handshake"


def test_run_probe_custom_probe_type_skips(monkeypatch):
    # 守护场景：审计 M3 —— 头部认证源不得伪造一个可通过的 URL 探针。
    monkeypatch.setenv("TWITTER_BEARER_TOKEN", "dummy")
    registry = {
        "twitter_x": {"name": "Twitter/X", "url": "https://api.x.com/2/tweets/search/recent",
                      "layer": "optional", "needs_key": True, "probe_type": "custom"},
    }

    def http_boom(url):
        raise AssertionError("custom probe_type must not fall into _http_probe")

    monkeypatch.setattr(s, "_http_probe", http_boom)
    results = s.run_probe(registry)
    assert results[0]["status"] == "SKIPPED"
    assert "custom" in results[0]["detail"]


# --- M2/T-07: KNOWN_SOURCES blind-spot heuristic (WARN, never BLOCK) ----------

def test_candidate_tool_names_flags_fictional_tool():
    doc = "We use GitHub for code. Frobzit MCP provides extra signals.\n"
    assert "Frobzit" in s._candidate_tool_names(doc)


def test_candidate_tool_names_no_false_positive_on_known():
    # 真实工具名（已映射 / 已知外部 / 泛词）零误报。
    doc = ("GitHub API, Hugging Face Hub API, patsnap-search skill, "
           "wechat-article-search skill, REST API, Tavily MCP, AgentKey MCP")
    assert s._candidate_tool_names(doc) == []


def test_check_consistency_warns_on_undocumented_candidate(tmp_path):
    registry = {
        "github": {"name": "GitHub", "url": "https://api.github.com", "layer": "default", "needs_key": False},
    }
    skill = "We use GitHub. Frobzit MCP provides extra signals.\n"
    reg_path = _write_tmp_repo(tmp_path, registry, skill)
    out = tmp_path / "parity.json"
    rc = s.check_consistency(registry_path=str(reg_path), out_path=str(out), repo_root=str(tmp_path))
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert "Frobzit" in rep["new_tool_candidates"]
    assert any("WARN: undocumented" in w for w in rep["warnings"])
    assert rc == 0  # WARN 不 BLOCK：结构性失明可观测，但不拦截 PR


def test_real_repo_blindspot_scan_clean(tmp_path):
    # 守护场景：验收「真实工具名零误报」——现行仓库的 SKILL.md + references/data-sources.md
    # 不得触发盲区 WARN（已知外部工具已入 KNOWN_EXTERNAL_TOOLS）。
    out = tmp_path / "parity.json"
    rc = s.check_consistency(registry_path=os.path.join(REPO_ROOT, "sources.registry.yaml"),
                             out_path=str(out), repo_root=REPO_ROOT)
    rep = json.loads(out.read_text(encoding="utf-8"))
    assert rc == 0
    assert rep["new_tool_candidates"] == [], rep["new_tool_candidates"]
    # T-03 闭环旁证：AgentKey 注册后不再出现在 blind/orphan 差集中。
    assert "agentkey" not in rep["blind"]
    assert "agentkey" not in rep["orphan"]

