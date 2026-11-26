"""Offline adversarial tests for Evidence Contract v1."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evidence_contract import evidence_errors
from validate_param_card import validate


def row(publisher, upstream, document, **kwargs):
    return dict({"实体": "X", "源URL": f"https://example.org/{document}",
                 "层级": "T1", "日期": "2026-11-22", "置信": "Confirmed"},
                claim_id="C1", claim_kind="normal", document_id=document,
                canonical_url=f"https://example.org/{document}", publisher_group=publisher,
                upstream_group=upstream, stance="support", provenance_verified="true",
                published_at="unknown", retrieved_at="2026-11-22", content_hash="unknown",
                **kwargs)


def test_same_domain_independent():
    assert not evidence_errors([row("lab-a","study-a","a"), row("lab-b","study-b","b")])


@pytest.mark.parametrize("records", [
    [row("a","origin","a"), row("b","origin","b")],
    [row("a","study-a","a"), row("b","unknown","b")],
    [row("a","a","a"), row("b","b","a")],
    [row("a","study-a","a"), row("a","study-b","b"), row("c","study-b","c")],
])
def test_duplicate_or_unknown_cannot_confirm(records):
    assert evidence_errors(records)


def test_hash_duplicate():
    a,b = row("a","a","a"), row("b","b","b")
    a["content_hash"] = b["content_hash"] = "a" * 64
    assert evidence_errors([a,b])


def test_key_parameter_requires_three():
    records = [row(x,x,x) for x in "abc"]
    for r in records:
        r["claim_kind"] = "key_parameter"
    assert evidence_errors(records[:2])
    assert not evidence_errors(records)


def test_refutation_and_downgrade():
    records = [row(x,x,x) for x in "abc"]
    records[-1]["stance"] = "refute"
    assert evidence_errors(records)
    for r in records:
        r["置信"] = "Conflicting"
    assert not evidence_errors(records)


def test_unverified_and_invalid_dates():
    a,b = row("a","a","a"),row("b","b","b")
    b["provenance_verified"] = "false"
    assert evidence_errors([a,b])
    b["provenance_verified"] = "true"
    b["retrieved_at"] = "2026-02-30"
    assert evidence_errors([a,b])


def test_card_integration(tmp_path):
    header = "课题: X\n范围: 全球\n实体清单:\n  - X\n"
    path = tmp_path / "card.yaml"
    path.write_text(header+"已收集来源池: []\n",encoding="utf-8")
    assert validate(str(path),True,True)["overall"] == "FAIL"
    path.write_text(header+"evidence_contract_version: 1\n已收集来源池: []\n",encoding="utf-8")
    assert validate(str(path),True,True)["overall"] == "PASS"
    records = [row("a","origin","a"),row("b","origin","b")]
    def card(records):
        lines = [header+"evidence_contract_version: 1\n已收集来源池:"]
        for record in records:
            lines += [f"  - 实体: {record['实体']}"]
            lines += [f"    {k}: {v}" for k,v in record.items() if k != "实体"]
        return "\n".join(lines)
    path.write_text(card(records),encoding="utf-8")
    assert validate(str(path),True,True)["overall"] == "FAIL"
    records[1]["upstream_group"] = "independent"
    path.write_text(card(records),encoding="utf-8")
    assert validate(str(path),True,True)["overall"] == "PASS"
