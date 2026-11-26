#!/usr/bin/env python3
"""Offline evaluator for the DMR CN/Global search-provider pilot. Never calls providers."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "benchmarks" / "search-provider-baseline.yaml"
TRACKING_KEYS = {"fbclid", "gclid", "ref", "source", "ref_src", "mc_cid", "mc_eid"}
SENSITIVE_FIELD_NAMES = {
    re.sub(r"[^a-z0-9]", "", name.lower())
    for name in {
        "authorization", "cookie", "set-cookie", "api_key", "apiKey",
        "access_token", "refresh_token", "bearer_token", "secret",
        "secret_value", "token", "password", "headers", "request_headers",
        "response_headers",
    }
}


def load_baseline(path: Path = BASELINE_PATH) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Baseline must be a YAML mapping")
    return data


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlsplit(str(url).strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        lower = key.lower()
        if lower.startswith("utm_") or lower in TRACKING_KEYS:
            continue
        query.append((key, value))
    query.sort()
    return urlunsplit((parsed.scheme.lower(), host, path, urlencode(query), ""))


def document_key(result: dict[str, Any]) -> str | None:
    content_hash = result.get("content_hash")
    if content_hash:
        return "hash:" + str(content_hash).strip().lower()
    canonical = normalize_url(result.get("canonical_url") or result.get("url"))
    if canonical:
        return "url:" + canonical
    return None


def domain_from_url(url: str | None) -> str | None:
    normalized = normalize_url(url)
    return urlsplit(normalized).netloc if normalized else None


def target_matches(result: dict[str, Any], target: dict[str, Any]) -> bool:
    result_url = normalize_url(result.get("canonical_url") or result.get("url"))
    if not result_url:
        return False
    target_url = target.get("url")
    if target_url and result_url == normalize_url(target_url):
        return True
    target_domain = target.get("domain")
    if target_domain:
        host = domain_from_url(result_url) or ""
        wanted = str(target_domain).lower().removeprefix("www.")
        return host == wanted or host.endswith("." + wanted)
    return False


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator <= 0:
        return None
    return round(float(numerator) / float(denominator), 4)


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return round(ordered[0], 2)
    position = (len(ordered) - 1) * pct
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(ordered[lower], 2)
    value = ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)
    return round(value, 2)


def _reject_sensitive_fields(value: Any, path: str = "record") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized_key = re.sub(r"[^a-z0-9]", "", str(key).lower())
            if normalized_key in SENSITIVE_FIELD_NAMES:
                raise ValueError(f"{path}: sensitive field is not allowed: {key}")
            _reject_sensitive_fields(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_sensitive_fields(item, f"{path}[{index}]")


def _parse_timestamp(value: str, field: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{field} must be ISO-8601 with timezone") from exc
    if not ("Z" in value or re.search(r"[+-]\d{2}:\d{2}$", value)):
        raise ValueError(f"{field} must include a UTC offset or Z")


def _load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"Line {line_number} must be a JSON object")
        records.append(record)
    return records


def preflight_request(provider_id, query_id, query_text, result_limit, baseline=None):
    """Call before dispatch: validate frozen provider/market/query/limit."""
    baseline = baseline or load_baseline()
    provider = baseline["providers"].get(provider_id)
    query = next((q for q in baseline["queries"] if q["id"] == query_id), None)
    if provider is None or query is None or provider["market"] != query["market"]:
        raise ValueError(f"Provider/query market mismatch: {(provider_id, query_id)}")
    if query_text != query["query"]:
        raise ValueError("query_text must exactly match the frozen baseline")
    if result_limit != baseline["execution"]["result_limit"]:
        raise ValueError("result_limit must match the frozen baseline")


def verify_snapshot(record, snapshot_root):
    """Verify bytes under the supplied snapshot root, not arbitrary paths."""
    path = record.get("raw_results_path")
    digest = record.get("raw_results_sha256")
    if snapshot_root is None or not isinstance(path, str) or not path.strip():
        raise ValueError("raw_results_path and snapshot_root required")
    root = Path(snapshot_root).resolve(strict=True)
    relative = Path(path)
    if relative.is_absolute() or relative.drive or ".." in relative.parts:
        raise ValueError("unsafe raw_results_path")
    resolved = (root / relative).resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("raw_results_path outside snapshot root or not a file")
    with resolved.open("rb") as stream:
        computed = hashlib.file_digest(stream, "sha256").hexdigest()
    if computed != digest:
        raise ValueError("raw_results_sha256 mismatch")
    return resolved


def validate_records(records: list[dict[str, Any]], baseline: dict[str, Any], snapshot_root=None) -> None:
    providers = baseline["providers"]
    queries = {item["id"]: item for item in baseline["queries"]}
    expected = {
        (provider_id, query["id"])
        for provider_id, provider in providers.items()
        for query in baseline["queries"]
        if query["market"] == provider["market"]
    }
    seen = set()
    run_ids = set()
    snapshots = set()

    for record in records:
        _reject_sensitive_fields(record)
        provider_id = record.get("provider_id")
        query_id = record.get("query_id")
        pair = (provider_id, query_id)
        if provider_id not in providers:
            raise ValueError(f"Unknown provider_id: {provider_id}")
        if query_id not in queries:
            raise ValueError(f"Unknown query_id: {query_id}")
        if pair not in expected:
            raise ValueError(f"Provider/query market mismatch: {pair}")
        if pair in seen:
            raise ValueError(f"Duplicate provider/query record: {pair}")
        seen.add(pair)

        run_id = record.get("run_id")
        if not run_id:
            raise ValueError(f"{pair}: run_id is required")
        run_ids.add(run_id)
        _parse_timestamp(record.get("requested_at"), f"{pair}.requested_at")

        preflight_request(provider_id, query_id, record.get("query_text"), record.get("result_limit"), baseline)
        if not isinstance(record.get("provider_parameters"), dict):
            raise ValueError(f"{pair}: provider_parameters must be a non-sensitive mapping")
        snapshot_hash = record.get("raw_results_sha256")
        if record.get("request_status") == "success":
            if not isinstance(snapshot_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", snapshot_hash):
                raise ValueError(f"{pair}: successful requests require raw_results_sha256 (64 lowercase hex chars)")
        elif snapshot_hash is not None and not re.fullmatch(r"[0-9a-f]{64}", str(snapshot_hash)):
            raise ValueError(f"{pair}: raw_results_sha256 must be null or a 64-character SHA-256")
        if snapshot_hash is not None:
            try:
                snapshot = verify_snapshot(record, snapshot_root)
            except OSError as exc:
                raise ValueError(f"{pair}: snapshot missing or unreadable") from exc
            if snapshot in snapshots:
                raise ValueError(f"{pair}: snapshot path reused across requests")
            snapshots.add(snapshot)
        elif record.get("raw_results_path") is not None:
            raise ValueError(f"{pair}: snapshot path without hash")
        if record.get("request_status") not in {"success", "failed", "skipped"}:
            raise ValueError(f"{pair}: invalid request_status")
        if record.get("result_limit") != baseline["execution"]["result_limit"]:
            raise ValueError(f"{pair}: result_limit must be {baseline['execution']['result_limit']}")
        latency = record.get("latency_ms")
        if latency is not None and (
            not isinstance(latency, (int, float)) or isinstance(latency, bool) or latency < 0
        ):
            raise ValueError(f"{pair}: latency_ms must be non-negative or null")

        results = record.get("results", [])
        if not isinstance(results, list):
            raise ValueError(f"{pair}: results must be a list")
        if record["request_status"] == "success" and len(results) > record["result_limit"]:
            raise ValueError(f"{pair}: result count exceeds result_limit")
        if record["request_status"] != "success" and results:
            raise ValueError(f"{pair}: failed/skipped request cannot carry results")
        ranks = set()
        for result in results:
            if not isinstance(result, dict):
                raise ValueError(f"{pair}: each result must be an object")
            rank = result.get("rank")
            if not isinstance(rank, int) or not 1 <= rank <= record["result_limit"]:
                raise ValueError(f"{pair}: every result needs a valid integer rank")
            if rank in ranks:
                raise ValueError(f"{pair}: duplicate result rank {rank}")
            ranks.add(rank)
            relevance = result.get("relevance")
            if isinstance(relevance, bool) or relevance not in {0, 1, 2}:
                raise ValueError(f"{pair}: relevance must be manually labeled 0, 1 or 2")
            if result.get("source_tier") not in {"T1", "T2", "T3", "T4", "unknown"}:
                raise ValueError(f"{pair}: invalid source_tier")
            if not (result.get("url") or result.get("canonical_url")):
                raise ValueError(f"{pair}: result needs url or canonical_url")
            if not isinstance(result.get("publisher"), str) or not result["publisher"].strip():
                raise ValueError(f"{pair}: publisher must be recorded or explicitly set to unknown")
            if not isinstance(result.get("publisher_group"), str) or not result["publisher_group"].strip():
                raise ValueError(f"{pair}: publisher_group must be recorded or explicitly set to unknown")
            if not isinstance(result.get("upstream_group"), str) or not result["upstream_group"].strip():
                raise ValueError(f"{pair}: upstream_group must be recorded or explicitly set to unknown")
            for date_field in ("published_at", "event_date"):
                value = result.get(date_field)
                if value is not None:
                    try:
                        date.fromisoformat(str(value)[:10])
                    except ValueError as exc:
                        raise ValueError(f"{pair}: invalid {date_field}") from exc
            verified = result.get("event_date_verified")
            if verified is not None and not isinstance(verified, bool):
                raise ValueError(f"{pair}: event_date_verified must be boolean or null")

        cost_status = record.get("cost_status")
        if cost_status not in {"reported", "unknown", "included", "free_confirmed"}:
            raise ValueError(f"{pair}: invalid cost_status")
        billed_cost = record.get("billed_cost")
        if cost_status == "reported":
            try:
                amount = Decimal(str(billed_cost))
            except Exception as exc:
                raise ValueError(f"{pair}: reported cost must be numeric") from exc
            if isinstance(billed_cost, bool) or not amount.is_finite() or amount < 0:
                raise ValueError(f"{pair}: reported cost requires a finite non-negative billed_cost")
            if not record.get("cost_currency"):
                raise ValueError(f"{pair}: reported cost requires cost_currency")
        elif cost_status == "free_confirmed":
            if billed_cost != 0 or not record.get("cost_evidence"):
                raise ValueError(f"{pair}: free_confirmed requires billed_cost=0 and cost_evidence")
        elif billed_cost is not None:
            raise ValueError(f"{pair}: unknown/included cost must not be coerced to a number")

        if record.get("fallback_attempted"):
            if record.get("fallback_status") not in {"success", "failed"}:
                raise ValueError(f"{pair}: attempted fallback needs success/failed status")
            if not record.get("fallback_provider"):
                raise ValueError(f"{pair}: attempted fallback needs fallback_provider")
        elif record.get("fallback_status") not in {None, "not_attempted"}:
            raise ValueError(f"{pair}: fallback_status conflicts with fallback_attempted=false")

    if len(run_ids) > 1:
        raise ValueError("All rows in one evaluation must share the same run_id")
    missing = expected - seen
    if missing:
        raise ValueError(f"Missing {len(missing)} provider/query records: {sorted(missing)}")


def _cost_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = {row["cost_status"] for row in records}
    reported_currencies = {
        row.get("cost_currency") for row in records if row["cost_status"] == "reported"
    }
    if statuses <= {"reported", "free_confirmed"} and len(reported_currencies) <= 1:
        total = sum(
            (Decimal(str(row.get("billed_cost", 0))) for row in records),
            Decimal("0"),
        )
        return {
            "status": "confirmed",
            "amount": str(total),
            "currency": next(iter(reported_currencies), None),
        }
    if statuses == {"included"}:
        return {"status": "included_marginal_cost_unknown", "amount": None, "currency": None}
    return {"status": "unknown_or_mixed", "amount": None, "currency": None}


def evaluate(records: list[dict[str, Any]], baseline: dict[str, Any] | None = None, snapshot_root=None) -> dict[str, Any]:
    baseline = baseline or load_baseline()
    validate_records(records, baseline, snapshot_root)
    query_by_id = {item["id"]: item for item in baseline["queries"]}
    records_by_pair = {(row["provider_id"], row["query_id"]): row for row in records}
    providers = baseline["providers"]
    metrics: dict[tuple[str, str], dict[str, Any]] = {}

    for provider_id, provider in providers.items():
        for query in baseline["queries"]:
            if query["market"] != provider["market"]:
                continue
            row = records_by_pair[(provider_id, query["id"])]
            results = sorted(row.get("results", []), key=lambda item: item["rank"])
            top5 = [result for result in results if result["rank"] <= 5]
            relevant = sum(result["relevance"] >= 1 for result in top5)
            strictly_relevant = sum(result["relevance"] == 2 for result in top5)
            unique_keys = [document_key(result) for result in results]
            known_keys = [key for key in unique_keys if key is not None]
            unique_key_set = set(known_keys)
            publishers = {
                str(result["publisher_group"])
                for result in results
                if result.get("publisher_group") and result["publisher_group"] != "unknown"
            }
            targets = query["expected_targets"]
            matched = {
                target["id"]
                for target in targets
                if any(target_matches(result, target) for result in results)
            }
            dated_results = [result for result in results if result.get("published_at")]
            freshness = None
            freshness_window = query.get("freshness_days")
            if freshness_window is not None:
                as_of = date.fromisoformat(baseline["as_of_date"])
                fresh = 0
                for result in dated_results:
                    published = date.fromisoformat(str(result["published_at"])[:10])
                    age = (as_of - published).days
                    if 0 <= age <= int(freshness_window):
                        fresh += 1
                freshness = ratio(fresh, len(results)) if results else None
            event_checks = [
                result for result in results
                if result.get("event_date") and result.get("event_date_verified") is not None
            ]
            event_accuracy = ratio(
                sum(result["event_date_verified"] is True for result in event_checks),
                len(event_checks),
            )
            metrics[(provider_id, query["id"])] = {
                "request_status": row["request_status"],
                "result_count": len(results),
                "top5_result_count": len(top5),
                "precision_at_5": round(relevant / 5, 4),
                "strict_precision_at_5": round(strictly_relevant / 5, 4),
                "expected_anchor_recall_at_10": ratio(len(matched), len(targets)) if targets else None,
                "matched_anchor_ids": sorted(matched),
                "t1_result_rate": ratio(
                    sum(result["source_tier"] == "T1" for result in results), len(results)
                ),
                "unique_document_count": len(unique_key_set),
                "unresolved_document_identity_count": sum(key is None for key in unique_keys),
                "duplicate_rate": ratio(len(known_keys) - len(unique_key_set), len(known_keys)),
                "independent_publisher_count": len(publishers),
                "publisher_groups": sorted(publishers),
                "published_date_coverage": ratio(len(dated_results), len(results)),
                "freshness_compliance": freshness,
                "dated_result_count": len(dated_results),
                "event_date_accuracy": event_accuracy,
                "event_date_checked_count": len(event_checks),
                "latency_ms": row.get("latency_ms"),
                "cost_status": row["cost_status"],
                "billed_cost": row.get("billed_cost"),
                "cost_currency": row.get("cost_currency"),
                "fallback_attempted": bool(row.get("fallback_attempted")),
                "fallback_status": row.get("fallback_status", "not_attempted"),
            }

    # A failed or unattempted request is missing data, not zero-quality evidence.
    quality_keys = ("precision_at_5", "strict_precision_at_5", "expected_anchor_recall_at_10",
                    "matched_anchor_ids", "t1_result_rate", "unique_document_count",
                    "unresolved_document_identity_count", "duplicate_rate",
                    "independent_publisher_count", "publisher_groups",
                    "published_date_coverage", "freshness_compliance", "dated_result_count",
                    "event_date_accuracy", "event_date_checked_count")
    for metric in metrics.values():
        if metric["request_status"] != "success":
            for key in quality_keys:
                metric[key] = None

    # Compare the paired provider on the same query. Unknown document identities are excluded.
    for provider_id, provider in providers.items():
        peer_ids = [
            peer_id for peer_id, peer in providers.items()
            if peer_id != provider_id and peer["market"] == provider["market"]
        ]
        if not peer_ids:
            continue
        peer_id = peer_ids[0]
        for query in baseline["queries"]:
            if query["market"] != provider["market"]:
                continue
            this_row = records_by_pair[(provider_id, query["id"])]
            peer_row = records_by_pair[(peer_id, query["id"])]
            if this_row["request_status"] != "success" or peer_row["request_status"] != "success":
                metric = metrics[(provider_id, query["id"])]
                metric["cross_provider_jaccard_overlap"] = None
                metric["new_publisher_groups_vs_peer"] = None
                continue
            this_keys = {
                document_key(result) for result in this_row.get("results", [])
                if document_key(result) is not None
            }
            peer_keys = {
                document_key(result) for result in peer_row.get("results", [])
                if document_key(result) is not None
            }
            this_publishers = {
                str(result["publisher_group"])
                for result in this_row.get("results", [])
                if result.get("publisher_group") and result["publisher_group"] != "unknown"
            }
            peer_publishers = {
                str(result["publisher_group"])
                for result in peer_row.get("results", [])
                if result.get("publisher_group") and result["publisher_group"] != "unknown"
            }
            intersection = len(this_keys & peer_keys)
            union = len(this_keys | peer_keys)
            metric = metrics[(provider_id, query["id"])]
            metric["cross_provider_jaccard_overlap"] = ratio(intersection, union)
            metric["new_publisher_groups_vs_peer"] = sorted(this_publishers - peer_publishers)

    summaries = {}
    for provider_id, provider in providers.items():
        query_rows = [
            query for query in baseline["queries"]
            if query["market"] == provider["market"]
        ]
        per_query = [metrics[(provider_id, query["id"])] for query in query_rows]
        latency = [item["latency_ms"] for item in per_query if item["latency_ms"] is not None]
        precisions = [item["precision_at_5"] for item in per_query if item["request_status"] == "success"]
        strict = [item["strict_precision_at_5"] for item in per_query if item["request_status"] == "success"]
        anchors = [
            item["expected_anchor_recall_at_10"]
            for item in per_query
            if item["request_status"] == "success" and item["expected_anchor_recall_at_10"] is not None
        ]
        freshness = [
            item["freshness_compliance"]
            for item in per_query
            if item["request_status"] == "success" and item["freshness_compliance"] is not None
        ]
        successful = [item for item in per_query if item["request_status"] == "success"]
        publisher_total = sum(item["independent_publisher_count"] for item in successful)
        paired = [item for item in per_query if item.get("new_publisher_groups_vs_peer") is not None]
        new_publishers = sum(len(item["new_publisher_groups_vs_peer"]) for item in paired) if paired else None
        provider_rows = [records_by_pair[(provider_id, query["id"])] for query in query_rows]
        summaries[provider_id] = {
            "market": provider["market"],
            "successful_queries": sum(row["request_status"] == "success" for row in provider_rows),
            "failed_queries": sum(row["request_status"] == "failed" for row in provider_rows),
            "skipped_queries": sum(row["request_status"] == "skipped" for row in provider_rows),
            "precision_at_5_macro": ratio(sum(precisions), len(precisions)),
            "strict_precision_at_5_macro": ratio(sum(strict), len(strict)),
            "expected_anchor_recall_macro": ratio(sum(anchors), len(anchors)),
            "mean_unique_publishers_per_query": round(publisher_total / len(successful), 3) if successful else None,
            "paired_successful_queries": len(paired),
            "new_publisher_groups_vs_peer_total": new_publishers,
            "freshness_compliance_macro": ratio(sum(freshness), len(freshness)),
            "latency_sample_count": len(latency),
            "latency_p50_ms": percentile(latency, 0.50),
            "latency_p95_ms": percentile(latency, 0.95),
            "cost": _cost_summary(provider_rows),
            "quality_decision": "REVIEW_REQUIRED",
        }

    return {
        "benchmark_id": baseline["benchmark_id"],
        "run_id": records[0]["run_id"] if records else None,
        "status": "PILOT_EVALUATED" if all(row["request_status"] == "success" for row in records) else "PILOT_INCOMPLETE",
        "comparison_only": True,
        "winner": None,
        "quality_pass": None,
        "provider_summaries": summaries,
        "query_metrics": {
            f"{provider_id}:{query_id}": item
            for (provider_id, query_id), item in sorted(metrics.items())
        },
        "notes": [
            "Pilot results are diagnostic only and do not promote a default provider.",
            "Unknown or subscription-included costs are not converted to zero.",
            "Independent publishers are counted by publisher_group, not by domain or search-provider brand.",
            "Latency percentiles use only four pilot samples per provider and are not an SLA.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Provider result JSONL")
    parser.add_argument("--output", type=Path, help="Optional JSON summary output")
    parser.add_argument("--snapshot-root", required=True, type=Path, help="Directory containing raw response snapshots")
    parser.add_argument("--baseline", type=Path, default=BASELINE_PATH)
    args = parser.parse_args()
    try:
        summary = evaluate(_load_records(args.input), load_baseline(args.baseline), args.snapshot_root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
