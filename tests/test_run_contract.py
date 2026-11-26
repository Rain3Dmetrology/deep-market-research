"""Budget admission and terminal state regression tests."""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_contract import BudgetLedger, validate_run


def ledger():
    return BudgetLedger({"a": ("USD", ".05"), "b": ("CNY", ".20")}, 4)


def test_budget_and_unknown():
    l = ledger()
    l.reserve("a1", "a", "USD", ".03")
    l.settle("a1", "unknown")
    with pytest.raises(ValueError):
        l.reserve("a2", "a", "USD", ".03")
    assert l.snapshot()["a1"]["actual"] is None
    assert l.snapshot()["a1"]["held"] == "0.03"
    l.reserve("b1", "b", "CNY", ".10")


def test_reject_unknown_or_mismatched_price():
    l = ledger()
    for bound in (None, "unknown", "-1", "NaN", "Infinity", True):
        with pytest.raises(ValueError):
            l.reserve("a", "a", "USD", bound)
    with pytest.raises(ValueError):
        l.reserve("a", "a", "CNY", ".01")


def test_reported_cost_and_overrun():
    l = ledger()
    l.reserve("a1", "a", "USD", ".04")
    with pytest.raises(ValueError):
        l.settle("a1", "reported", ".01")
    l.settle("a1", "reported", ".01", "billing-record")
    l.reserve("a2", "a", "USD", ".04")
    l.settle("a2", "reported", ".06", "billing-record")
    assert l.overrun
    with pytest.raises(ValueError):
        l.reserve("b1", "b", "CNY", ".01")


def test_concurrent_budget_no_double_spend():
    l = BudgetLedger({"a": ("USD", ".05")}, 8)
    def reserve(i):
        try:
            l.reserve(str(i), "a", "USD", ".03")
            return True
        except ValueError:
            return False
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(reserve, range(8))) == 1


def manifest():
    return {"run_contract_version":1, "run_id":"fixture", "query":"test",
            "component_versions":{"dmr":"2.9.0"}, "budget_enforcement":"not_applicable",
            "budget_overrun":False, "param_card":{}, "evidence_pool":[], "calls":[],
            "decisions":[], "degradation_events":[], "stop_reason":"acceptance_met",
            "acceptance":[{"id":"a","status":"pass"}], "outcome":"passed"}


def test_terminal_gate():
    m=manifest()
    assert validate_run(m)
    m["acceptance"][0]["status"]="fail"
    with pytest.raises(ValueError):
        validate_run(m)
    m["outcome"]="partial"
    assert validate_run(m)


def test_unknown_not_free():
    m=manifest()
    m["budget_enforcement"]="soft_limit"
    m["calls"]=[{"request_id":"q1","cost_status":"unknown","actual":0}]
    with pytest.raises(ValueError):
        validate_run(m)
    m["calls"][0]["actual"]=None
    assert validate_run(m)


def test_budget_overrun_cannot_pass():
    m=manifest()
    m["budget_overrun"]=True
    with pytest.raises(ValueError):
        validate_run(m)


def hard_manifest():
    m = manifest()
    m.update(budget_enforcement="hard_limit", max_calls=2,
             budget_limits={"a": {"currency": "USD", "cap": ".05"}},
             calls=[{"request_id": "r1", "provider": "a", "currency": "USD",
                     "upper_bound": ".03", "pricing_evidence": "fixture",
                     "cost_status": "unknown", "actual": None}])
    return m


def test_hard_budget_reconciliation():
    m = hard_manifest()
    assert validate_run(m)
    m["calls"].append(dict(m["calls"][0], request_id="r2"))
    with pytest.raises(ValueError, match="contradicts"):
        validate_run(m)
    m.update(budget_overrun=True, outcome="partial")
    assert validate_run(m)


@pytest.mark.parametrize("change", [
    {"provider": "unapproved"}, {"currency": "CNY"},
    {"pricing_evidence": ""}, {"upper_bound": None},
    {"actual": ".04", "cost_status": "reported", "cost_evidence": "fixture"},
])
def test_hard_budget_invalid_call(change):
    m = hard_manifest()
    m["calls"][0].update(change)
    with pytest.raises(ValueError):
        validate_run(m)


def test_hard_budget_requires_explicit_limits():
    m = hard_manifest()
    del m["budget_limits"]
    with pytest.raises(ValueError, match="explicit"):
        validate_run(m)


def test_hard_budget_call_limit():
    m = hard_manifest()
    m["max_calls"] = 0
    with pytest.raises(ValueError, match="contradicts"):
        validate_run(m)
