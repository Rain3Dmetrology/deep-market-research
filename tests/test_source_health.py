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
