"""Real unit tests for scripts/validate_report.py.

Guards the layout-tolerance behavior (exposed by the Q6 benchmark report):
  T1  decorated section headings (qualifier suffixes) still satisfy roles
  T2  evidence-table rows (T1-3 + date + URL) back Confirmed for R2
  T3  T4-only table rows do NOT back Confirmed
  T4  a tier-cell prose mention ("无 T1-3 源") is not an evidence row
  T5  a genuinely missing section still fails R0 (no over-tolerance)
  T6  end-to-end: a decorated-heading report passes full validation

Guards the Q2/Q5 benchmark fixes:
  T7  bare-domain source cells (keyence.com.cn, no scheme) back Confirmed
  T8  numeric-only cells (83.0% / v2.6.1) are NOT sources
  T9  auto mode detects template E (delta) and uses the E role set
  T10 template E conflicts pass R3 via 置信迁移/双方案并列 (no ledger section)
  T11 template E conflict without dual-scheme markers still fails R3
  T12 non-E auto report with conflict marks still requires the ledger

Run:  pytest tests/test_validate_report.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import validate_report as v  # noqa: E402


# --- decorated headings -------------------------------------------------------

def test_decorated_headings_satisfy_roles():
    text = "\n".join([
        "## 1. 执行摘要",
        "- 三句话结论。",
        "## 2. 信源分级一览",
        "## 3. 核心发现（五大板块 · 销售视角）",
        "## 6. 矛盾台账（证据冲突裁决记录）",
        "| a | b |",
        "## 7. 开放问题与信息缺口",
        "## 10. 质量自检与方法论合规声明",
    ])
    sections = v.split_sections(text)
    for role in ("exec", "source_tier", "core", "contradiction", "open", "methodology"):
        assert v.find_section(sections, role) is not None, f"role {role} not found"


def test_missing_section_not_fabricated():
    text = "\n".join([
        "## 1. 执行摘要",
        "## 2. 信源分级一览",
        "## 3. 核心发现",
        "## 7. 开放问题",
        "## 8. 方法论与合规声明",
    ])
    missing, _ = v.required_sections_check(v.split_sections(text), "B")
    assert "contradiction" in missing


# --- table-backed citations (R2) ----------------------------------------------

def test_table_rows_back_confirmed():
    text = "\n".join([
        "## 1. 执行摘要",
        "结论 A [Confirmed]。",
        "## 2. 信源分级一览",
        "| 源 | 层级 | 日期 | 用途 |",
        "|----|------|------|------|",
        "| https://a.example/x | T1 | 2026-08-01 | 事实A |",
        "| https://b.example/y | T3 | 2026-08-02 | 事实B |",
    ])
    status, detail = v.check_rule2_confirmed(text)
    assert status == "PASS", detail


def test_t4_only_table_rows_do_not_back_confirmed():
    text = "\n".join([
        "## 1. 执行摘要",
        "结论 A [Confirmed]。",
        "## 2. 信源分级一览",
        "| 源 | 层级 | 日期 | 用途 |",
        "|----|------|------|------|",
        "| https://a.example/x | T4 | 2026-08-01 | 信号A |",
        "| https://b.example/y | T4 | 2026-08-02 | 信号B |",
    ])
    status, _ = v.check_rule2_confirmed(text)
    assert status == "FAIL"


# --- tier-cell prose mention (R1) ----------------------------------------------

def test_prose_tier_mention_not_evidence_row():
    text = "\n".join([
        "| 源 | 层级 | 日期 | 用途 |",
        "|----|------|------|------|",
        "| https://a.example | T1 | 2026-08-01 | 事实 |",
        "| 中国机器视觉整体 | （推断，无 T1-3 全口径源） | — | Unverified |",
    ])
    status, detail, total = v.check_rule1_evidence(text)
    assert status == "PASS", detail
    assert total == 1  # 推断行不计入证据行


# --- end-to-end -----------------------------------------------------------------

def test_end_to_end_decorated_report_passes(tmp_path):
    report = "\n".join([
        "# 报告",
        "## 1. 执行摘要",
        "- 三句话结论。",
        "## 2. 信源分级一览",
        "| 源 | 层级 | 日期 | 用途 |",
        "|----|------|------|------|",
        "| https://a.example | T1 | 2026-08-01 | 定位 |",
        "| https://b.example | T3 | 2026-08-02 | 旁证 |",
        "## 3. 核心发现（五大板块）",
        "- 发现 [Confirmed]，源A(T1, 2026-08-01) + 源B(T3, 2026-08-02)。",
        "## 6. 矛盾台账（证据冲突裁决记录）",
        "| 争议点 | 说法A | 说法B | 裁决 |",
        "|--------|-------|-------|------|",
        "| 定价 | 高 | 低 | 并存待核 |",
        "## 7. 开放问题与信息缺口",
        "- 因环境受限未覆盖：专利维度。",
        "## 10. 质量自检与方法论合规声明",
        "- 方法论简述。",
    ])
    p = tmp_path / "report.md"
    p.write_text(report, encoding="utf-8")
    out = v.validate(str(p), "B", False, False)
    assert out["overall"] == "PASS", out["rules"]


# --- bare-domain citations (Q2 fix) ---------------------------------------------

def test_bare_domain_table_rows_back_confirmed():
    text = "\n".join([
        "## 1. 执行摘要",
        "结论 A [Confirmed]。",
        "## 2. 信源分级一览",
        "| 源 | 层级 | 日期 | 用途 |",
        "|----|------|------|------|",
        "| keyence.com.cn 产品页 | T1 | 2026-08-01 | 定价制 |",
        "| cognex.com 询价页 | T1 | 2026-08-02 | 定价制 |",
    ])
    status, detail = v.check_rule2_confirmed(text)
    assert status == "PASS", detail


def test_numeric_cells_are_not_sources():
    text = "\n".join([
        "## 1. 执行摘要",
        "结论 A [Confirmed]。",
        "## 2. 信源分级一览",
        "| 指标 | 层级 | 日期 | 数值 |",
        "|----|------|------|------|",
        "| 毛利率 83.0% | T1 | 2026-08-01 | v2.6.1 |",
        "| 增速 15.95% | T3 | 2026-08-02 | 2026.08.22 |",
    ])
    status, _ = v.check_rule2_confirmed(text)
    assert status == "FAIL"


def test_bare_domain_dedup_same_site_counts_once():
    rows = [
        "| 源 | 层级 | 日期 | 用途 |",
        "|----|------|------|------|",
        "| keyence.com.cn/a | T1 | 2026-08-01 | 事实A |",
        "| keyence.com.cn/b | T1 | 2026-08-02 | 事实B |",
        "| cognex.com | T3 | 2026-08-02 | 事实C |",
    ]
    quals = v.table_citations_in("\n".join(rows))
    distinct = set((t, s) for (t, _, s) in quals)
    # 同一裸域名不同路径只计 1 个独立源
    assert distinct == {("T1", "keyence.com.cn"), ("T3", "cognex.com")}


# --- template E auto-detection (Q5 fix) -------------------------------------------

E_REPORT = "\n".join([
    "# 监测增量报告",
    "## 1. 本期变化总览（Delta Summary）",
    "- 本期 7 项变化。",
    "## 2. 变化项明细",
    "| # | 变化 | 层级 | 日期 |",
    "|---|------|------|------|",
    "| 1 | 事实X | T1 | 2026-08-01 |",
    "| 2 | 事实Y | T3 | 2026-08-02 |",
    "## 3. 开放问题演进",
    "- 仍开放。",
    "## 4. 置信迁移",
    "- 冲突条目 C9（Conflicting）：方案A 说出货 2 万台，方案B 说产量 4 万台，并存待核。",
    "## 5. 方法论与合规声明",
    "- 监测口径简述。",
])


def test_auto_detects_template_e_roles():
    sections = v.split_sections(E_REPORT)
    missing, present = v.required_sections_check(sections, "auto")
    assert missing == []
    assert "delta" in present


def test_template_e_conflict_passes_r3_via_dual_scheme():
    sections = v.split_sections(E_REPORT)
    status, detail = v.check_rule3_contradiction(E_REPORT, sections)
    assert status == "PASS", detail


def test_template_e_conflict_without_dual_scheme_fails():
    report = E_REPORT.replace(
        "冲突条目 C9（Conflicting）：方案A 说出货 2 万台，方案B 说产量 4 万台，并存待核。",
        "冲突条目 C9（Conflicting）：口径分歧，已合一采信其一。",
    )
    sections = v.split_sections(report)
    status, _ = v.check_rule3_contradiction(report, sections)
    assert status == "FAIL"


def test_non_e_auto_report_with_conflict_requires_ledger():
    text = "\n".join([
        "## 1. 执行摘要",
        "- 结论与某来源存在矛盾。",
        "## 2. 信源分级一览",
        "## 3. 开放问题",
        "## 4. 方法论与合规声明",
    ])
    sections = v.split_sections(text)
    missing, _ = v.required_sections_check(sections, "auto")
    assert "contradiction" in missing
