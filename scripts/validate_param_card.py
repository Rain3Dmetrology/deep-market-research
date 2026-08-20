#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_param_card.py — deep-market-research (dmr) 研究参数卡结构化机检

定位
----
dmr v2.5.0 的 B 项落地：把「研究参数卡」从自由散文升级为**可机检的结构化卡片**。
卡片字段定义以 `references/parameter-card-schema.md` 为**唯一权威**（dmr §三-B / 团队《研究参数卡》
/ orchestrator run-manifest 参数卡快照 均引用此 schema，杜绝三重字段定义漂移）。

设计纪律（对齐 dmr 平台无关/零依赖护城河）
------------------------------------------
- **仅用 Python 标准库**（re / argparse / sys / json）。**不引入 pyyaml**。
- 卡片用「受限 YAML 子集」书写，本脚本用**纯标准库正则递归解析**该子集（非通用 YAML 解析器）。
- **不阻断主管线**：脚本缺失或环境无 Python 则跳过；机检为启发式前置门禁。
- 支持 `--strict`（WARN 升 FAIL）、`--json`（CI 解析）；退出码 0/1/2。

用法
----
    python scripts/validate_param_card.py <卡片.yaml> [--strict] [--json]
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Tuple, Union

# ---------------------------------------------------------------------------
# 受限 YAML 子集解析器（仅覆盖 parameter-card-schema.md 规定的构造）
# 支持：缩进块映射、缩进块序列、序列中的映射项、标量（普通/引号）。不支持锚点/流式/多行。
# ---------------------------------------------------------------------------

RE_COMMENT = re.compile(r"^\s*#")
RE_MAP_KEY = re.compile(r"^([^\s:#][^:]*?):\s*(.*)$")
RE_SEQ_ITEM_MAP = re.compile(r"^([A-Za-z0-9_一-鿿]+)\s*:\s*(.*)$")  # 序列内映射项的首键


def _tokenize(text: str) -> List[Tuple[int, str]]:
    toks = []
    for raw in text.splitlines():
        if not raw.strip() or RE_COMMENT.match(raw):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        toks.append((indent, raw.strip()))
    return toks


def _parse_map(tokens: List[Tuple[int, str]], idx: int, indent: int):
    result: Dict[str, Union[str, dict, list]] = {}
    n = len(tokens)
    while idx < n:
        ind, content = tokens[idx]
        if ind < indent:
            break
        if ind > indent:
            idx += 1
            continue
        m = RE_MAP_KEY.match(content)
        if not m:
            idx += 1
            continue
        key = m.group(1).strip()
        val = m.group(2).strip()
        if val == "":
            if idx + 1 < n and tokens[idx + 1][0] > indent:
                child, idx = _parse_block(tokens, idx + 1, tokens[idx + 1][0])
                result[key] = child
            else:
                result[key] = None
                idx += 1
        else:
            result[key] = _strip_quotes(val)
            idx += 1
    return result, idx


def _parse_seq(tokens: List[Tuple[int, str]], idx: int, seq_indent: int):
    result: List[Union[str, dict]] = []
    item_indent = seq_indent + 2
    n = len(tokens)
    while idx < n:
        ind, content = tokens[idx]
        if ind < seq_indent:
            break
        if ind == seq_indent and content.startswith("- "):
            rest = content[2:].strip()
            if RE_SEQ_ITEM_MAP.match(rest):
                # 映射项：首键在同一条 `- ` 行，后续更深层行属此条目
                item_lines = [(item_indent, rest)]
                j = idx + 1
                while j < n and tokens[j][0] > seq_indent:
                    item_lines.append(tokens[j])
                    j += 1
                item_val, _ = _parse_map(item_lines, 0, item_indent) if item_lines else ({}, 0)
                result.append(item_val)
                idx = j
            else:
                # 标量项
                result.append(_strip_quotes(rest))
                idx += 1
        else:
            idx += 1
    return result, idx


def _parse_block(tokens: List[Tuple[int, str]], idx: int, indent: int):
    if idx < len(tokens) and tokens[idx][1].startswith("- "):
        return _parse_seq(tokens, idx, indent)
    return _parse_map(tokens, idx, indent)


def _strip_quotes(s: str) -> str:
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s


def parse_card(text: str) -> dict:
    toks = _tokenize(text)
    if not toks:
        return {}
    val, _ = _parse_map(toks, 0, 0)
    return val if isinstance(val, dict) else {}


# ---------------------------------------------------------------------------
# 校验规则
# ---------------------------------------------------------------------------

REQUIRED = ["课题", "范围", "实体清单", "已收集来源池"]
POOL_SUBFIELDS = ["实体", "源URL", "层级", "日期", "置信"]
TIERS = {"T1", "T2", "T3", "T4"}
CONFIDENCE = {"Confirmed", "Corroborated", "Single-source", "Unverified"}
TEMPLATES = {"A", "B", "C", "D", "E"}
STATES = {"drafting", "collecting", "adjudicating", "assembling"}
RE_DATE = re.compile(r"^\d{4}(?:-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[12]\d|3[01]))?)?$")


def validate(path: str, strict: bool) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return {"error": "file_not_found", "file": path}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e), "file": path}

    card = parse_card(text)
    rules = []

    # R0 必含字段
    missing = [k for k in REQUIRED if k not in card or card[k] in (None, "")]
    if missing:
        rules.append({"id": "R0-required", "desc": "必含字段（课题/范围/实体清单/已收集来源池）",
                      "status": "FAIL", "detail": "缺失：" + ", ".join(missing)})
    else:
        rules.append({"id": "R0-required", "desc": "必含字段（课题/范围/实体清单/已收集来源池）",
                      "status": "PASS", "detail": "全部命中"})

    # R1 范围非空
    scope = card.get("范围")
    scope_ok = False
    if isinstance(scope, dict):
        scope_ok = any(str(v).strip() for v in scope.values())
    elif isinstance(scope, str):
        scope_ok = bool(scope.strip())
    if scope_ok:
        rules.append({"id": "R1-scope", "desc": "范围非空（建议含 时间）", "status": "PASS",
                      "detail": "范围已填"})
    else:
        rules.append({"id": "R1-scope", "desc": "范围非空（建议含 时间）", "status": "FAIL",
                      "detail": "范围为空或未填子字段"})

    # R2 实体清单非空
    ents = card.get("实体清单")
    if isinstance(ents, list) and len(ents) > 0 and all(str(e).strip() for e in ents):
        rules.append({"id": "R2-entities", "desc": "实体清单非空", "status": "PASS",
                      "detail": "共 %d 个实体" % len(ents)})
    else:
        rules.append({"id": "R2-entities", "desc": "实体清单非空", "status": "FAIL",
                      "detail": "实体清单为空或非列表"})

    # R3-R5 已收集来源池条目完整性 + 层级 + 日期
    pool = card.get("已收集来源池")
    pool_total = 0
    pool_complete = 0
    tier_bad = 0
    date_bad = 0
    conf_warn = 0
    if not isinstance(pool, list):
        rules.append({"id": "R3-pool", "desc": "已收集来源池为列表", "status": "FAIL",
                      "detail": "已收集来源池缺失或非列表（强制字段）"})
    else:
        bad_incomplete = 0
        for entry in pool:
            if not isinstance(entry, dict):
                bad_incomplete += 1
                continue
            pool_total += 1
            miss = [f for f in POOL_SUBFIELDS if entry.get(f) is None or not str(entry.get(f)).strip()]
            if miss:
                bad_incomplete += 1
                continue
            pool_complete += 1
            tier = str(entry.get("层级", "")).strip()
            if tier not in TIERS:
                tier_bad += 1
            date = str(entry.get("日期", "")).strip()
            if not RE_DATE.match(date):
                date_bad += 1
            conf = str(entry.get("置信", "")).strip()
            if conf and conf not in CONFIDENCE:
                conf_warn += 1
        if bad_incomplete == 0:
            rules.append({"id": "R3-pool", "desc": "来源池条目完整（实体/源URL/层级/日期/置信 齐全）",
                          "status": "PASS", "detail": "%d/%d 条完整" % (pool_complete, pool_total)})
        else:
            rules.append({"id": "R3-pool", "desc": "来源池条目完整（实体/源URL/层级/日期/置信 齐全）",
                          "status": "FAIL", "detail": "%d 条缺子字段" % bad_incomplete})
        if tier_bad == 0:
            rules.append({"id": "R4-tier", "desc": "层级 ∈ {T1,T2,T3,T4}", "status": "PASS",
                          "detail": "全部合规"})
        else:
            rules.append({"id": "R4-tier", "desc": "层级 ∈ {T1,T2,T3,T4}", "status": "FAIL",
                          "detail": "%d 条层级非法" % tier_bad})
        if date_bad == 0:
            rules.append({"id": "R5-date", "desc": "日期格式 YYYY/YYYY-MM/YYYY-MM-DD", "status": "PASS",
                          "detail": "全部合规"})
        else:
            rules.append({"id": "R5-date", "desc": "日期格式 YYYY/YYYY-MM/YYYY-MM-DD", "status": "FAIL",
                          "detail": "%d 条日期格式错误" % date_bad})

    # R6 推荐字段（WARN 级）
    warns = []
    tpl = str(card.get("模板", "")).strip()
    if tpl and tpl not in TEMPLATES:
        warns.append("模板值 '%s' 不在 {A,B,C,D,E}" % tpl)
    st = str(card.get("状态", "")).strip()
    if st and st not in STATES:
        warns.append("状态值 '%s' 不在推荐枚举" % st)
    if conf_warn:
        warns.append("%d 条置信标签不在推荐集合（Confirmed/Corroborated/Single-source/Unverified）" % conf_warn)
    if warns:
        rules.append({"id": "R6-recommended", "desc": "推荐字段（模板/状态/置信）合规", "status": "WARN",
                      "detail": "；".join(warns)})
    else:
        rules.append({"id": "R6-recommended", "desc": "推荐字段（模板/状态/置信）合规", "status": "PASS",
                      "detail": "推荐字段均合规或省略"})

    coverage = None
    if pool_total > 0:
        coverage = round(pool_complete / pool_total * 100, 1)

    fails = [r for r in rules if r["status"] == "FAIL"]
    warns_only = [r for r in rules if r["status"] == "WARN"]
    if fails:
        overall = "FAIL"
    elif warns_only and strict:
        overall = "FAIL"
    else:
        overall = "PASS"

    return {
        "file": path,
        "strict": strict,
        "overall": overall,
        "rules": rules,
        "counts": {"pass": len([r for r in rules if r["status"] == "PASS"]),
                   "warn": len(warns_only),
                   "fail": len(fails)},
        "coverage": {"source_pool_complete_pct": coverage},
    }


def render_human(report: dict) -> str:
    if "error" in report:
        return "错误: %s -> %s" % (report.get("error"), report.get("file"))
    lines = []
    lines.append("=" * 60)
    lines.append("dmr 研究参数卡机检 · 严格=%s" % report["strict"])
    lines.append("文件: %s" % report["file"])
    lines.append("=" * 60)
    sym = {"PASS": "✔ PASS", "FAIL": "✘ FAIL", "WARN": "⚠ WARN"}
    for r in report["rules"]:
        lines.append("[%s] %s — %s" % (sym.get(r["status"], r["status"]), r["id"], r["desc"]))
        lines.append("        %s" % r["detail"])
    cov = report["coverage"]["source_pool_complete_pct"]
    cov_s = "N/A" if cov is None else ("%.1f%%" % cov)
    lines.append("-" * 60)
    lines.append("覆盖率: 来源池条目完整率=%s" % cov_s)
    lines.append("统计: PASS=%d WARN=%d FAIL=%d" % (
        report["counts"]["pass"], report["counts"]["warn"], report["counts"]["fail"]))
    lines.append(">>> 总判定: %s <<<" % report["overall"])
    lines.append("=" * 60)
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="dmr 研究参数卡结构化机检（零依赖，离线安全）")
    p.add_argument("card", help="待检参数卡 yaml 路径")
    p.add_argument("--strict", action="store_true", help="WARN 也视为失败")
    p.add_argument("--json", action="store_true", help="输出 JSON（供 CI 解析）")
    args = p.parse_args(argv)

    report = validate(args.card, args.strict)
    if "error" in report:
        sys.stderr.write(render_human(report) + "\n")
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_human(report))
    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
