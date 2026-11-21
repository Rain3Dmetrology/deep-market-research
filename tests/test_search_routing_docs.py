import importlib.util
import re
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "data-sources.md"
CROSS_PLATFORM = ROOT / "references" / "cross-platform-tools.md"
SKILL = ROOT / "SKILL.md"
REGISTRY = ROOT / "sources.registry.yaml"


def test_canonical_catalog_defines_single_owner_and_specialist_parallelism():
    text = CATALOG.read_text(encoding="utf-8")
    assert "每个广域查询簇默认一个 owner" in text
    assert "专业证据域可以并行" in text
    assert "第二个广域 owner 必须有理由" in text


def test_cross_platform_guide_does_not_reintroduce_default_fanout():
    text = CROSS_PLATFORM.read_text(encoding="utf-8")
    assert "基座始终并行调用" not in text
    assert "增强层并行叠加" not in text
    assert "references/data-sources.md" in text


def test_skill_delegates_provider_catalog_to_one_canonical_file():
    text = SKILL.read_text(encoding="utf-8")
    assert "references/data-sources.md" in text
    assert "references/cross-platform-tools.md" in text


def test_registry_urls_never_embed_credential_values_or_placeholders():
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    credential_query = re.compile(
        r"[?&](?:api_key|auth|access_token|token|app_secret|bearer_token)=",
        re.IGNORECASE,
    )
    for source_id, spec in registry.items():
        url = spec.get("url", "")
        assert not credential_query.search(url), (
            f"{source_id} embeds a credential-like URL parameter"
        )


def test_keyed_rest_providers_are_not_misreported_by_url_only_get_probe():
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    for source_id, spec in registry.items():
        if spec.get("layer") == "deprecated" or spec.get("status") == "DEPRECATED":
            continue
        if spec.get("needs_key") and spec.get("probe_type") != "mcp":
            assert spec.get("probe_type") == "custom", (
                f"{source_id} needs an authenticated request adapter before it can be probed"
            )


def test_custom_auth_rest_probes_are_skipped_without_network(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "dmr_source_health_routing_test", ROOT / "scripts" / "source_health.py"
    )
    source_health = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source_health)

    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    selected = {
        key: value for key, value in registry.items()
        if value.get("needs_key") and value.get("probe_type") == "custom"
        and value.get("layer") != "deprecated"
    }
    assert selected

    def forbidden_http_probe(_url):
        pytest.fail("custom authenticated REST probe must not make a URL-only HTTP request")

    monkeypatch.setattr(source_health, "_http_probe", forbidden_http_probe)
    results = source_health.run_probe(selected)
    assert {result["key"] for result in results} == set(selected)
    assert all(result["status"] == "SKIPPED" for result in results)


def test_tinyfish_products_are_separated_by_capability():
    lines = CATALOG.read_text(encoding="utf-8").splitlines()
    discovery = next(line for line in lines if line.startswith("| **广域发现**"))
    extraction = next(line for line in lines if line.startswith("| **正文提取"))
    research = next(line for line in lines if line.startswith("| **研究代理"))
    assert "TinySearch" in discovery
    assert "TinyFetch" in extraction
    assert "TinyAgent" in research and "TinyBrowser" in research
    assert "TinySearch" not in research


def test_wechat_discovery_and_article_extraction_are_separate():
    text = CATALOG.read_text(encoding="utf-8")
    assert "ReadGZH" in text
    assert "canonical" in text
    assert "wechat-article-search" in text and "ReadGZH" in text
