import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "dmr_search_benchmark_eval_test",
    ROOT / "scripts" / "evaluate_search_benchmark.py",
)
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)


def baseline():
    return EVAL.load_baseline()


def make_record(provider_id, query, results=None, status="success"):
    return {
        "run_id": "synthetic-run-001",
        "requested_at": "2026-11-22T12:00:00Z",
        "query_id": query["id"],
        "query_text": query["query"],
        "provider_id": provider_id,
        "provider_parameters": {},
        "raw_results_sha256": "a" * 64 if status == "success" else None,
        "request_status": status,
        "latency_ms": 500 if status == "success" else None,
        "result_limit": 10,
        "cost_status": "unknown",
        "billed_cost": None,
        "cost_currency": None,
        "fallback_attempted": False,
        "fallback_provider": None,
        "fallback_status": "not_attempted",
        "results": results or [],
    }


def make_result(rank, url, publisher="Synthetic Publisher", relevance=2, tier="T1"):
    return {
        "rank": rank,
        "title": "Synthetic result " + str(rank),
        "url": url,
        "canonical_url": url,
        "publisher": publisher,
        "publisher_group": publisher.lower().replace(" ", "-"),
        "upstream_group": "unknown",
        "published_at": None,
        "event_date": None,
        "event_date_verified": None,
        "source_tier": tier,
        "relevance": relevance,
        "content_hash": None,
    }


def complete_records():
    data = baseline()
    rows = []
    urls = {
        "CN-01": "https://www.hikrobotics.com/cn/machinevision/",
        "CN-02": "https://www.optmv.com/content/details187_357603.html",
        "CN-03": "https://example.cn/paper-or-patent",
        "CN-04": "https://www.optmv.com/content/details81_372303.html",
        "GL-01": "https://www.keyence.com/products/measure/laser-2d/lj-x8000/",
        "GL-02": "https://www.keyence.com/products/measure/laser-2d/lj-x8000/specs/",
        "GL-03": "https://www.sciencedirect.com/science/article/abs/pii/S0143816626000679",
        "GL-04": "https://example.org/reflective-metrology-failure",
    }
    for provider_id, provider in data["providers"].items():
        for query in data["queries"]:
            if query["market"] != provider["market"]:
                continue
            publisher = "Synthetic Publisher " + provider_id
            rows.append(make_record(
                provider_id,
                query,
                [make_result(1, urls[query["id"]], publisher=publisher)],
            ))
    return rows


def test_baseline_is_fixed_eight_queries_and_sixteen_requests():
    data = baseline()
    assert len(data["queries"]) == 8
    assert sum(item["market"] == "CN" for item in data["queries"]) == 4
    assert sum(item["market"] == "Global" for item in data["queries"]) == 4
    assert data["execution"]["total_expected_search_requests"] == 16
    for provider in data["providers"].values():
        assert sum(item["market"] == provider["market"] for item in data["queries"]) == 4


def test_url_normalization_removes_tracking_and_fragments():
    url = "HTTPS://WWW.Example.com/a/?utm_source=x&id=7#section"
    assert EVAL.normalize_url(url) == "https://example.com/a?id=7"


def test_evaluator_computes_precision_and_primary_anchor_recall():
    data = baseline()
    rows = complete_records()
    row = next(
        item for item in rows
        if item["provider_id"] == "metaso_web" and item["query_id"] == "CN-02"
    )
    row["results"] = [make_result(
        1,
        "https://www.optmv.com/content/details187_357603.html",
        publisher="OPT",
        relevance=2,
    )]
    summary = EVAL.evaluate(rows, data)
    metric = summary["query_metrics"]["metaso_web:CN-02"]
    assert metric["expected_anchor_recall_at_10"] == 1.0
    assert metric["precision_at_5"] == 0.2
    assert metric["strict_precision_at_5"] == 0.2
    assert summary["winner"] is None
    assert summary["quality_pass"] is None


def test_unknown_cost_is_not_reported_as_zero():
    summary = EVAL.evaluate(complete_records())
    for provider_summary in summary["provider_summaries"].values():
        assert provider_summary["cost"]["status"] == "unknown_or_mixed"
        assert provider_summary["cost"]["amount"] is None


def test_duplicate_urls_and_publishers_are_deduplicated():
    rows = complete_records()
    row = next(
        item for item in rows
        if item["provider_id"] == "octen_search" and item["query_id"] == "GL-02"
    )
    row["results"] = [
        make_result(
            1,
            "https://www.keyence.com/products/measure/laser-2d/lj-x8000/specs/?utm_source=search",
            publisher="Keyence Group",
        ),
        make_result(
            2,
            "https://keyence.com/products/measure/laser-2d/lj-x8000/specs/",
            publisher="Keyence Group",
        ),
    ]
    summary = EVAL.evaluate(rows)
    metric = summary["query_metrics"]["octen_search:GL-02"]
    assert metric["unique_document_count"] == 1
    assert metric["duplicate_rate"] == 0.5
    assert metric["independent_publisher_count"] == 1


def test_missing_or_duplicate_provider_query_rows_are_rejected():
    rows = complete_records()
    with pytest.raises(ValueError, match="Missing"):
        EVAL.evaluate(rows[:-1])
    with pytest.raises(ValueError, match="Duplicate"):
        EVAL.evaluate(rows + [rows[0]])


def test_successful_request_requires_raw_result_snapshot_hash():
    rows = complete_records()
    rows[0]["raw_results_sha256"] = None
    with pytest.raises(ValueError, match="raw_results_sha256"):
        EVAL.evaluate(rows)


def test_query_text_must_match_frozen_baseline():
    rows = complete_records()
    rows[0]["query_text"] = "silently modified query"
    with pytest.raises(ValueError, match="exactly match"):
        EVAL.evaluate(rows)


def test_failed_request_is_retained_without_results():
    rows = complete_records()
    failed = next(
        item for item in rows
        if item["provider_id"] == "exa_search" and item["query_id"] == "GL-04"
    )
    failed["request_status"] = "failed"
    failed["latency_ms"] = 2200
    failed["results"] = []
    summary = EVAL.evaluate(rows)
    provider = summary["provider_summaries"]["exa_search"]
    assert provider["failed_queries"] == 1
    assert provider["successful_queries"] == 3


def test_free_confirmed_cost_requires_evidence_and_partial_cost_is_unknown():
    rows = complete_records()
    rows[0]["cost_status"] = "free_confirmed"
    rows[0]["billed_cost"] = 0
    with pytest.raises(ValueError, match="free_confirmed"):
        EVAL.evaluate(rows)
    rows[0]["cost_evidence"] = "Synthetic billing evidence for unit test."
    summary = EVAL.evaluate(rows)
    cost = summary["provider_summaries"]["metaso_web"]["cost"]
    assert cost["status"] == "unknown_or_mixed"
    assert cost["amount"] is None


def test_evaluator_has_no_network_client_imports():
    import ast
    tree = ast.parse((ROOT / "scripts" / "evaluate_search_benchmark.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert imported.isdisjoint({"requests", "httpx", "aiohttp", "urllib3", "socket", "http", "ftplib"})


def test_sensitive_request_headers_and_tokens_are_rejected():
    rows = complete_records()
    rows[0]["request_headers"] = {"Authorization": "Bearer synthetic"}
    with pytest.raises(ValueError, match="sensitive field"):
        EVAL.evaluate(rows)


def test_invalid_latency_and_duplicate_result_ranks_are_rejected():
    rows = complete_records()
    rows[0]["latency_ms"] = -1
    with pytest.raises(ValueError, match="latency_ms"):
        EVAL.evaluate(rows)
    rows = complete_records()
    duplicate = dict(rows[0]["results"][0])
    duplicate["rank"] = 1
    rows[0]["results"].append(duplicate)
    with pytest.raises(ValueError, match="duplicate result rank"):
        EVAL.evaluate(rows)


def test_published_date_coverage_and_freshness_are_separate_metrics():
    rows = complete_records()
    row = next(
        item for item in rows
        if item["provider_id"] == "metaso_web" and item["query_id"] == "CN-04"
    )
    row["results"][0]["published_at"] = "2025-11-29"
    summary = EVAL.evaluate(rows)
    metric = summary["query_metrics"]["metaso_web:CN-04"]
    assert metric["published_date_coverage"] == 1.0
    assert metric["freshness_compliance"] == 1.0
