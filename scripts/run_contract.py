"""Offline budget ledger and run acceptance gate; no network or credential access."""
from decimal import Decimal, InvalidOperation
from threading import Lock


def money(value):
    try:
        if isinstance(value, bool):
            raise ValueError("invalid monetary value")
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0:
            raise ValueError("invalid monetary value")
        return amount
    except InvalidOperation as exc:
        raise ValueError("invalid monetary value") from exc


class BudgetLedger:
    """In-process shared admission ledger; hard enforcement requires all calls to use it."""
    def __init__(self, limits, max_calls):
        if not isinstance(max_calls, int) or isinstance(max_calls, bool) or max_calls < 0:
            raise ValueError("invalid max_calls")
        self.limits = {p: (currency, money(cap)) for p, (currency, cap) in limits.items()}
        self.max_calls = max_calls
        self.entries = {}
        self.lock = Lock()
        self.overrun = False

    def reserve(self, request_id, provider, currency, upper_bound):
        bound = money(upper_bound)
        with self.lock:
            if self.overrun or len(self.entries) >= self.max_calls:
                raise ValueError("budget closed")
            if request_id in self.entries or not request_id:
                raise ValueError("duplicate or missing request id")
            if provider not in self.limits or currency != self.limits[provider][0]:
                raise ValueError("provider or currency not authorized")
            used = sum((e["held"] for e in self.entries.values() if e["provider"] == provider), Decimal(0))
            if used + bound > self.limits[provider][1]:
                raise ValueError("provider cap exceeded")
            self.entries[request_id] = {"provider": provider, "currency": currency, "upper_bound": bound,
                                        "held": bound, "status": "reserved", "actual": None}

    def settle(self, request_id, status, actual=None, evidence=None):
        with self.lock:
            entry = self.entries[request_id]
            if entry["status"] != "reserved":
                raise ValueError("already settled")
            if status == "reported":
                if not evidence:
                    raise ValueError("actual cost needs billing evidence")
                value = money(actual)
                if value > entry["upper_bound"]:
                    self.overrun = True
                entry.update(status=status, actual=value, held=value, cost_evidence=evidence)
            elif status == "unknown" and actual is None:
                entry["status"] = "unknown"  # retain full reservation, including timeouts
            else:
                raise ValueError("invalid settlement")

    def snapshot(self):
        with self.lock:
            return {key: {k: str(v) if isinstance(v, Decimal) else v for k, v in row.items()}
                    for key, row in self.entries.items()}


def validate_run(manifest):
    """Validate terminal acceptance, not the truth of claims or provider billing."""
    if manifest.get("run_contract_version") != 1:
        raise ValueError("run_contract_version must be 1")
    if not isinstance(manifest.get("run_id"), str) or not manifest["run_id"].strip():
        raise ValueError("missing run_id")
    versions = manifest.get("component_versions")
    if not isinstance(versions, dict) or not versions.get("dmr"):
        raise ValueError("missing DMR version")
    if manifest.get("budget_enforcement") not in {"hard_limit", "soft_limit", "not_applicable"}:
        raise ValueError("missing enforcement mode")
    acceptance = manifest.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        raise ValueError("missing acceptance criteria")
    if any(not isinstance(item, dict) or not item.get("id") or item.get("status") not in {"pass","fail","unverified"} for item in acceptance):
        raise ValueError("invalid acceptance criterion")
    if len({item["id"] for item in acceptance}) != len(acceptance):
        raise ValueError("duplicate acceptance criterion")
    if manifest.get("outcome") not in {"passed","partial","failed","cancelled"}:
        raise ValueError("invalid terminal outcome")
    if manifest["outcome"] == "passed" and (manifest.get("budget_overrun") is not False or
            any(item["status"] != "pass" for item in acceptance)):
        raise ValueError("cannot pass with failed/unverified criteria or unknown/overrun budget")
    for key in ("query", "stop_reason"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise ValueError(f"missing {key}")
    if not isinstance(manifest.get("param_card"), dict):
        raise ValueError("missing parameter card")
    for key in ("calls", "evidence_pool", "decisions", "degradation_events"):
        if not isinstance(manifest.get(key), list):
            raise ValueError(f"missing {key}")
    ids = set()
    for call in manifest["calls"]:
        if not isinstance(call, dict) or not call.get("request_id") or call["request_id"] in ids:
            raise ValueError("invalid or duplicate request id")
        ids.add(call["request_id"])
        status = call.get("cost_status")
        if status not in {"reported", "unknown", "included", "free_confirmed"}:
            raise ValueError("invalid cost status")
        if status in {"reported", "free_confirmed"}:
            amount = money(call.get("actual"))
            if not call.get("cost_evidence") or not call.get("currency"):
                raise ValueError("cost requires billing evidence and currency")
            if status == "free_confirmed" and amount != 0:
                raise ValueError("free cost must be zero")
        elif call.get("actual") is not None:
            raise ValueError("unknown/included actual must be null")
    if manifest["budget_enforcement"] == "not_applicable" and manifest["calls"]:
        raise ValueError("calls require budget enforcement classification")
    if manifest["budget_enforcement"] == "hard_limit":
        _validate_hard_budget(manifest)
    return True


def _validate_hard_budget(manifest):
    """Reconcile terminal reservations and actuals; not proof of dispatch history."""
    max_calls = manifest.get("max_calls")
    limits = manifest.get("budget_limits")
    if type(max_calls) is not int or max_calls < 0 or not isinstance(limits, dict) or not limits:
        raise ValueError("hard limit requires explicit call and provider caps")
    caps = {}
    for provider, limit in limits.items():
        if not isinstance(limit, dict) or not isinstance(limit.get("currency"), str) or not limit["currency"].strip():
            raise ValueError("invalid provider limit")
        caps[provider] = (limit["currency"], money(limit.get("cap")))
    totals = {provider: Decimal(0) for provider in caps}
    overrun = len(manifest["calls"]) > max_calls
    for call in manifest["calls"]:
        provider = call.get("provider")
        if provider not in caps or call.get("currency") != caps[provider][0]:
            raise ValueError("unauthorized provider or currency")
        if not isinstance(call.get("pricing_evidence"), str) or not call["pricing_evidence"].strip():
            raise ValueError("missing price upper-bound evidence")
        bound = money(call.get("upper_bound"))
        actual = call.get("actual")
        if actual is not None:
            actual = money(actual)
            overrun = overrun or actual > bound
            totals[provider] += actual
        else:
            totals[provider] += bound
        overrun = overrun or bound > caps[provider][1]
    overrun = overrun or any(total > caps[p][1] for p, total in totals.items())
    if manifest.get("budget_overrun") is not overrun:
        raise ValueError("declared budget outcome contradicts reconciliation")


def main(argv=None):
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Validate a DMR run manifest offline")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        validate_run(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"RUN CONTRACT FAIL: {exc}")
        return 1
    print("RUN CONTRACT PASS (metadata only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
