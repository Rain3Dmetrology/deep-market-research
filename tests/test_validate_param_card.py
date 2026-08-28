"""Real unit tests for scripts/validate_param_card.py.

Guards the repo's most complex hand-written component (audit H6 / P1-6): the
restricted-YAML subset parser (_tokenize / _parse_map / _parse_seq) previously
shipped with zero tests, plus the main validation paths (R0-R6).

Run:  pytest tests/test_validate_param_card.py
"""
import io
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import validate_param_card as p  # noqa: E402


# --- tokenizer ----------------------------------------------------------------

def test_tokenize_skips_blanks_and_comments():
    toks = p._tokenize("a: 1\n\n   # 注释行\nb: 2\n")
    assert toks == [(0, "a: 1"), (0, "b: 2")]


def test_tokenize_records_indent():
    toks = p._tokenize("top:\n  child: v\n    leaf: 1\n")
    assert toks == [(0, "top:"), (2, "child: v"), (4, "leaf: 1")]


# --- _parse_map ---------------------------------------------------------------

def test_parse_map_flat_scalars():
    card = p.parse_card("课题: 测试课题\n模板: A\n")
    assert card["课题"] == "测试课题"
    assert card["模板"] == "A"


def test_parse_map_nested_blocks():
    text = "\n".join([
        "范围:",
        "  时间: 2024-2026",
        "  地域:",
        "    主: 全球",
        "课题: 外层键",
    ])
    card = p.parse_card(text)
    assert card["范围"] == {"时间": "2024-2026", "地域": {"主": "全球"}}
    assert card["课题"] == "外层键"  # 出栈后回到顶层缩进


def test_parse_map_empty_value_without_children_is_none():
    card = p.parse_card("空字段:\n下一键: v\n")
    assert card["空字段"] is None
    assert card["下一键"] == "v"


def test_parse_map_strips_quotes():
    card = p.parse_card("课题: \"带引号: 冒号保留\"\n状态: 'drafting'\n")
    assert card["课题"] == "带引号: 冒号保留"
    assert card["状态"] == "drafting"


def test_parse_map_value_with_url_colon():
    # 边界：值本身含冒号（URL），键只切第一个冒号
    card = p.parse_card("源URL: https://a.example/x\n")
    assert card["源URL"] == "https://a.example/x"


# --- _parse_seq ---------------------------------------------------------------

def test_parse_seq_scalar_items():
    card = p.parse_card("实体清单:\n  - 实体甲\n  - 实体乙\n")
    assert card["实体清单"] == ["实体甲", "实体乙"]


def test_parse_seq_map_items():
    text = "\n".join([
        "已收集来源池:",
        "  - 实体: 实体甲",
        "    源URL: https://a.example/x",
        "    层级: T1",
        "    日期: 2026-08-01",
        "    置信: Confirmed",
        "  - 实体: 实体乙",
        "    源URL: https://b.example/y",
        "    层级: T2",
        "    日期: 2026-08-02",
        "    置信: Corroborated",
    ])
    card = p.parse_card(text)
    pool = card["已收集来源池"]
    assert isinstance(pool, list) and len(pool) == 2
    assert pool[0]["实体"] == "实体甲"
    assert pool[0]["层级"] == "T1"
    assert pool[1]["置信"] == "Corroborated"


def test_parse_seq_item_with_nested_seq():
    # 嵌套序列：序列项映射内再挂子序列
    text = "\n".join([
        "池:",
        "  - 实体: X",
        "    标签:",
        "      - t1",
        "      - t2",
        "  - 实体: Y",
    ])
    card = p.parse_card(text)
    assert card["池"][0]["标签"] == ["t1", "t2"]
    assert card["池"][1]["实体"] == "Y"


def test_parse_seq_terminates_at_shallower_key():
    text = "\n".join([
        "实体清单:",
        "  - 实体甲",
        "课题: 回到顶层",
    ])
    card = p.parse_card(text)
    assert card["实体清单"] == ["实体甲"]
    assert card["课题"] == "回到顶层"


# --- boundary cases -------------------------------------------------------------

def test_parse_empty_text():
    assert p.parse_card("") == {}
    assert p.parse_card("# 仅注释\n   \n") == {}


def test_parse_file_not_found():
    rep = p.validate(os.path.join(REPO_ROOT, "tests", "__no_such_card__.yaml"), False)
    assert rep == {"error": "file_not_found", "file": rep["file"]}


# --- full validation path (R0-R6) -----------------------------------------------

VALID_CARD = "\n".join([
    "课题: 测试课题",
    "范围:",
    "  时间: 2024-2026",
    "  地域: 全球",
    "实体清单:",
    "  - 实体甲",
    "  - 实体乙",
    "已收集来源池:",
    "  - 实体: 实体甲",
    "    源URL: https://a.example/x",
    "    层级: T1",
    "    日期: 2026-08-01",
    "    置信: Confirmed",
    "模板: A",
    "状态: collecting",
])


def _write_card(tmp_path, text):
    path = tmp_path / "card.yaml"
    path.write_text(text, encoding="utf-8")
    return str(path)


def _rule(rep, rule_id):
    return next(r for r in rep["rules"] if r["id"] == rule_id)


def test_valid_card_passes(tmp_path):
    rep = p.validate(_write_card(tmp_path, VALID_CARD), False)
    assert rep["overall"] == "PASS", rep["rules"]
    assert rep["coverage"]["source_pool_complete_pct"] == 100.0


def test_r0_missing_required_field_fails(tmp_path):
    rep = p.validate(_write_card(tmp_path, VALID_CARD.replace("课题: 测试课题", "课题:")), False)
    assert _rule(rep, "R0-required")["status"] == "FAIL"
    assert rep["overall"] == "FAIL"


def test_r1_missing_scope_fails(tmp_path):
    # 范围整体缺失（键不在）-> R1 FAIL
    lines = [l for l in VALID_CARD.splitlines()
             if not (l.startswith("范围") or l.startswith("  时间") or l.startswith("  地域"))]
    rep = p.validate(_write_card(tmp_path, "\n".join(lines)), False)
    assert _rule(rep, "R1-scope")["status"] == "FAIL"


def test_r1_scope_with_content_passes(tmp_path):
    rep = p.validate(_write_card(tmp_path, VALID_CARD), False)
    assert _rule(rep, "R1-scope")["status"] == "PASS"


def test_r4_bad_tier_fails(tmp_path):
    rep = p.validate(_write_card(tmp_path, VALID_CARD.replace("层级: T1", "层级: T9")), False)
    assert _rule(rep, "R4-tier")["status"] == "FAIL"


def test_r5_bad_date_fails(tmp_path):
    rep = p.validate(_write_card(tmp_path, VALID_CARD.replace("日期: 2026-08-01", "日期: 2026-13-40")), False)
    assert _rule(rep, "R5-date")["status"] == "FAIL"


def test_r3_incomplete_pool_entry_fails(tmp_path):
    rep = p.validate(_write_card(tmp_path, VALID_CARD.replace("    置信: Confirmed", "    置信:")), False)
    assert _rule(rep, "R3-pool")["status"] == "FAIL"


def test_r6_warn_on_bad_template_and_strict_upgrades(tmp_path):
    text = VALID_CARD.replace("模板: A", "模板: Z")
    rep = p.validate(_write_card(tmp_path, text), False)
    assert _rule(rep, "R6-recommended")["status"] == "WARN"
    assert rep["overall"] == "PASS"  # WARN 非致命
    rep = p.validate(_write_card(tmp_path, text), True)
    assert rep["overall"] == "FAIL"  # --strict 升格


def test_r6_warn_on_unknown_confidence_label(tmp_path):
    rep = p.validate(_write_card(tmp_path, VALID_CARD.replace("置信: Confirmed", "置信: 拍脑袋")), False)
    assert _rule(rep, "R6-recommended")["status"] == "WARN"


# --- Windows GBK 控制台回归 -------------------------------------------------
# 守护场景：人类可读输出含 ✔(U+2714) 等非 GBK 字符，Windows 默认 GBK 控制台裸跑时
# print 抛 UnicodeEncodeError、进程以退出码 1 崩溃；main() 入口的 _configure_stdio()
# （同 setup_mcp.py 语义）修复后不得再抛。

def test_gbk_limited_stdout_does_not_crash_human_render(tmp_path, monkeypatch):
    card_path = _write_card(tmp_path, VALID_CARD)
    gbk_out = io.TextIOWrapper(io.BytesIO(), encoding="gbk", errors="strict")
    monkeypatch.setattr(sys, "stdout", gbk_out)
    rc = p.main([card_path])  # 修复前：print 渲染 ✔ 抛 UnicodeEncodeError（pytest 视为失败）
    assert rc == 0
    gbk_out.flush()  # TextIOWrapper 缓冲须显式冲刷才落入底层 BytesIO
    rendered = gbk_out.buffer.getvalue().decode("utf-8", errors="replace")
    assert "总判定: PASS" in rendered


def test_json_output_is_ascii_safe(tmp_path, monkeypatch):
    # --json 路径保证机器可读：即使 stdout 为 GBK strict 流也不抛、输出纯 ASCII 可解析。
    import json as _json
    card_path = _write_card(tmp_path, VALID_CARD)
    gbk_out = io.TextIOWrapper(io.BytesIO(), encoding="gbk", errors="strict")
    monkeypatch.setattr(sys, "stdout", gbk_out)
    rc = p.main([card_path, "--json"])
    assert rc == 0
    gbk_out.flush()  # TextIOWrapper 缓冲须显式冲刷才落入底层 BytesIO
    raw = gbk_out.buffer.getvalue()
    assert raw.isascii()
    assert _json.loads(raw.decode("ascii"))["overall"] == "PASS"
