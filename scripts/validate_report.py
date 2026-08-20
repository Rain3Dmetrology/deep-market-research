#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_report.py — deep-market-research (dmr) 程序化终稿机检门禁

定位
----
dmr SKILL.md「终稿纪律 · 5 输出前 lint 自检清单」的**可度量前置机检**。
把原本人工勾选的 6 项（或团队 Phase N 的 ①来源充分性 维度）升级为 PASS/FAIL 门禁，
输出覆盖率，供单 agent 模式交付前或 CI 拦截使用。

设计纪律（对齐 dmr 平台无关/零依赖护城河）
------------------------------------------
- **仅用 Python 标准库**（re / argparse / sys / json / urllib），不引入 pyyaml / 第三方包。
- **离线安全**：死链检查（lint 第6项）默认关闭，需显式 --check-links 才联网；无网环境不会误 FAIL。
- **不阻断主管线**：本脚本是「门禁建议」，不修改报告、不调用任何 agent / 进程。
- **机检≠语义证明**：凡涉及「论证是否充分」「是否真独立」之处，均为可解释启发式，
  输出会显式标注启发式边界，避免伪造确定性。

用法
----
    python scripts/validate_report.py <报告.md> [--template A|B|C|D|E|auto] [--strict] [--check-links] [--json]

退出码
------
    0 = 通过（无 FAIL；WARN 不致命，除非 --strict）
    1 = 未通过（至少一项 FAIL）
    2 = 用法 / 文件错误

作者：dmr v2.4.x 单 agent 验证路径（A 项落地）。零团队耦合。
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 模板清单（manifest）：每个模板的「必含章节」归一化标题集合
# 归一化规则：去掉行首 "数字. " / "数字、" 前缀，转小写，去首尾空白。
# ---------------------------------------------------------------------------

# 章节角色 -> 候选归一化标题（命中任一即视为满足该角色）
ROLE_TITLES = {
    "exec": {"执行摘要", "executive summary"},
    "source_tier": {
        "信源分级一览", "信源分级",
        "7 字段结构化证据清单", "文献/技术证据清单",
        "变化项明细", "新证据",
    },
    "core": {
        "核心发现（带置信度）", "核心发现：五大板块", "核心发现",
        "四维度分析", "变化项明细",
    },
    "contradiction": {"矛盾台账（显式，不掩盖）", "矛盾台账"},
    "open": {"开放问题（未能验证，需人工/后续）", "开放问题", "开放问题演进"},
    "methodology": {"方法论与合规声明", "方法论"},
    "delta": {"本期变化总览（delta summary）", "本期变化总览"},
}

# 各模板必含角色（auto 取最小并集，并附加「若用矛盾标记则强制矛盾台账」）
TEMPLATE_REQUIRED: Dict[str, List[str]] = {
    "A": ["exec", "source_tier", "core", "contradiction", "open", "methodology"],
    "B": ["exec", "source_tier", "core", "contradiction", "open", "methodology"],
    "C": ["exec", "source_tier", "core", "open", "methodology"],
    "D": ["exec", "source_tier", "core", "contradiction", "open", "methodology"],
    "E": ["delta", "source_tier", "open", "methodology"],
}
TEMPLATE_REQUIRED["auto"] = ["exec", "source_tier", "open", "methodology"]

# ---------------------------------------------------------------------------
# 正则
# ---------------------------------------------------------------------------
RE_HEADER = re.compile(r"^##\s+(.*?)\s*$", re.MULTILINE)
RE_TIER = re.compile(r"\bT([1-4])\b")
RE_DATE = re.compile(r"\b(?:19|20)\d{2}(?:-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[12]\d|3[01]))?)?\b")
RE_URL = re.compile(r"https?://\S+", re.IGNORECASE)
RE_DOI = re.compile(r"(?:DOI:?\s*|doi\.org/)\s*10\.\S+", re.IGNORECASE)
RE_PAREN = re.compile(r"\(([^()]*)\)")
RE_CONFIRMED_TAG = re.compile(r"\[(Confirmed|Corroborated|Single-source|Unverified)\]", re.IGNORECASE)
RE_CONFLICT_WORD = re.compile(r"矛盾|Conflicting|conflicting", re.IGNORECASE)
RE_INFERENCE = re.compile(r"推断|解读|假设|推测|可能|估计|大概|也许|likely|may|might|assume|should", re.IGNORECASE)
RE_LOW = re.compile(r"\[?LOW\]?|低置信|low[- ]?confidence|（假设|假设）", re.IGNORECASE)
RE_ENV_LIMIT = re.compile(r"环境受限|未覆盖|未接入|未使用|受限|未连|coverag|未使用|未抓取", re.IGNORECASE)


def norm(title: str) -> str:
    """归一化章节标题：去行首序号、转小写、去空白。"""
    t = re.sub(r"^\d+[\.、]\s*", "", title).strip().lower()
    return t


def split_sections(text: str) -> List[Tuple[str, str]]:
    """返回 [(归一化标题, 该节正文)]，含末尾到文件尾。"""
    matches = list(RE_HEADER.finditer(text))
    sections = []
    for i, m in enumerate(matches):
        title = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((norm(title), text[start:end]))
    return sections


def find_section(sections, role: str) -> Optional[str]:
    """返回第一个命中该角色的节正文；未命中返回 None。"""
    wanted = ROLE_TITLES[role]
    for title, body in sections:
        if title in wanted:
            return body
    return None


def parse_tables(text: str) -> List[List[List[str]]]:
    """返回 markdown 表格列表，每个表格为 [行][单元格]，已 strip。"""
    lines = text.splitlines()
    tables = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.lstrip().startswith("|") and i + 1 < n and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1] or ""):
            rows = []
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                rows.append(cells)
                j += 1
            if len(rows) >= 2:  # 表头 + 分隔
                tables.append(rows)
            i = j
        else:
            i += 1
    return tables


# dmr 常见引用形态：源A(T1, 2025-03) / 源B(T3, 2025-05)（来源令牌在括号外）
RE_CITE = re.compile(r"([\w./\-·]+?)\s*\(\s*(T[1-3])\s*,\s*(\d{4}(?:-\d{1,2}){0,2})\s*\)")


def qualified_citations_in(text: str) -> List[Tuple[str, str, str]]:
    """
    提取「合格引用」：含 T1-T3 层级 + 日期 + 可识别来源。
    覆盖两种形态：
      (a) 源A(T1, 2025-03) —— 来源令牌在括号外（dmr 主流写法）；
      (b) (https://... T1 2025-03) —— URL/DOI 在括号内（兜底）。
    返回 [(tier, date, source_id)]，source_id 取 URL/DOI 或来源令牌。
    用于 lint 第2项（Confirmed 需 >=2 独立 T1-3）。
    """
    out = []
    # 形态 (a)
    for src_tok, tier, date in RE_CITE.findall(text):
        if len(src_tok) < 1:
            continue
        out.append((tier, date, src_tok))
    # 形态 (b)：括号内同时含 T1-3 + 日期 + URL/DOI
    for grp in RE_PAREN.findall(text):
        tier_m = RE_TIER.search(grp)
        if not tier_m:
            continue
        tier = "T" + tier_m.group(1)
        if tier not in ("T1", "T2", "T3"):
            continue
        if not RE_DATE.search(grp):
            continue
        url_m = RE_URL.search(grp)
        doi_m = RE_DOI.search(grp)
        if url_m:
            out.append((tier, RE_DATE.search(grp).group(0), url_m.group(0)))
        elif doi_m:
            out.append((tier, RE_DATE.search(grp).group(0), doi_m.group(0)))
    return out


def check_rule1_evidence(text: str) -> Tuple[str, str, int]:
    """
    lint 第1项：每条 T 层级证据行须带 层级 + 日期 + 可识别来源。
    只在「表头含 层级 且含 日期」的证据表中检查数据行。
    """
    violations = 0
    total_tiered = 0
    for rows in parse_tables(text):
        header = [c.lower() for c in rows[0]]
        if not any("层级" in h or h == "tier" for h in header):
            continue
        if not any("日期" in h or h == "date" for h in header):
            continue
        try:
            tier_idx = next(k for k, h in enumerate(header) if "层级" in h or h == "tier")
            date_idx = next(k for k, h in enumerate(header) if "日期" in h or h == "date")
        except StopIteration:
            continue
        for r in rows[2:]:  # 跳过表头 + 分隔
            if len(r) <= max(tier_idx, date_idx):
                continue
            tier_cell = r[tier_idx]
            tm = RE_TIER.search(tier_cell)
            if not tm:
                continue
            total_tiered += 1
            date_ok = bool(RE_DATE.search(r[date_idx]))
            has_source = any(
                (RE_URL.search(c) or RE_DOI.search(c) or (len(c.strip()) >= 2 and not RE_TIER.match(c.strip())))
                for c in r
            )
            if not (date_ok and has_source):
                violations += 1
    if total_tiered == 0:
        return ("WARN", "未发现带层级的证据表行（报告可能用纯内联引用；第1项无法机检，建议人工核对）", 0)
    if violations == 0:
        return ("PASS", f"全部 {total_tiered} 行带层级证据均含 层级+日期+可识别来源", total_tiered)
    return ("FAIL", f"{violations}/{total_tiered} 行带层级证据缺 日期 或 可识别来源", total_tiered)


def check_rule2_confirmed(text: str) -> Tuple[str, str]:
    """
    lint 第2项：Confirmed 须 >=2 独立 T1-3 合格引用。
    文档级启发式：若报告出现 Confirmed 断言，则全篇合格 T1-3 引用去重后须 >=2。
    """
    has_confirmed = bool(re.search(r"Confirmed", text, re.IGNORECASE)) or bool(RE_CONFIRMED_TAG.search(text))
    quals = qualified_citations_in(text)
    distinct = set((t, s) for (t, _, s) in quals)
    if not has_confirmed:
        return ("PASS", "报告未使用 Confirmed 断言，第2项不适用")
    if len(distinct) >= 2:
        return ("PASS", f"Confirmed 断言由 {len(distinct)} 个独立 T1-3 合格引用支撑（>=2）")
    return ("FAIL", f"Confirmed 断言仅由 {len(distinct)} 个独立 T1-3 合格引用支撑（要求 >=2）；请补充交叉源或降档")


def check_rule3_contradiction(text: str, sections) -> Tuple[str, str]:
    """
    lint 第3项：矛盾未强行合一（双方案并列）。
    - 若报告出现矛盾标记但未设 矛盾台账 章节 -> FAIL。
    - 若设了 矛盾台账 章节但为空/无双方案 -> WARN。
    """
    has_conflict_word = bool(RE_CONFLICT_WORD.search(text))
    ledger = find_section(sections, "contradiction")
    if has_conflict_word and ledger is None:
        return ("FAIL", "报告出现矛盾/Conflicting 标记，但缺少「矛盾台账」章节显式并列双方案")
    if ledger is not None:
        has_two_sides = bool(re.search(r"说法[AB]|方案[AB]|A\(|B\(|并存|双方案", ledger)) or "|" in ledger
        if not has_two_sides:
            return ("WARN", "存在「矛盾台账」章节但未见双方案并列（可能为空或仅单边）")
        return ("PASS", "矛盾台账章节存在且含双方案并列")
    return ("PASS", "未检测到矛盾标记，第3项不适用")


def check_rule4_inference(text: str) -> Tuple[str, str]:
    """
    lint 第4项：推断/解读须标 LOW 且注明假设。
    启发式：含推断关键词且像事实断言（带置信标签或强动词）的行，若未标 LOW/低置信 -> WARN。
    """
    warns = 0
    for line in text.splitlines():
        if not RE_INFERENCE.search(line):
            continue
        # 仅检查「像结论」的行：带置信标签，或含「是/为/达到/占」等断言动词
        looks_factual = bool(RE_CONFIRMED_TAG.search(line)) or re.search(r"(是|为|达到|占|预计|将|共)", line)
        if not looks_factual:
            continue
        if not RE_LOW.search(line):
            warns += 1
    if warns == 0:
        return ("PASS", "推断/解读类断言均已标注 LOW/低置信（或无可疑裸推断）")
    return ("WARN", f"发现 {warns} 处含推断关键词的疑似事实断言未标 LOW/低置信（启发式，建议人工复核）")


def check_rule5_open(sections) -> Tuple[str, str]:
    """
    lint 第5项：开放问题须列「环境受限未覆盖」项（dmr 规则15）。
    """
    open_body = find_section(sections, "open")
    if open_body is None:
        return ("FAIL", "缺少「开放问题」章节（已在必含章节中拦截）；第5项无法核对")
    if RE_ENV_LIMIT.search(open_body):
        return ("PASS", "开放问题章节已声明环境受限/未覆盖维度（规则15）")
    return ("WARN", "开放问题章节未见「环境受限未覆盖」声明（建议补一条规则15 覆盖局限）")


def check_rule6_links(text: str, do_check: bool) -> Tuple[str, str]:
    """
    lint 第6项：无死链。默认关闭（离线安全）；--check-links 时才联网 HEAD 验活。
    """
    if not do_check:
        return ("SKIP", "死链检查默认关闭（离线安全）；需显式 --check-links 才联网验活")
    urls = RE_URL.findall(text)
    dead = []
    for u in set(urls):
        try:
            import urllib.request
            req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "dmr-validate/1.0"})
            urllib.request.urlopen(req, timeout=8)
        except Exception:
            dead.append(u)
    if not dead:
        return ("PASS", f"已验活 {len(set(urls))} 个 URL，无死链")
    return ("FAIL", f"{len(dead)} 个 URL 验活失败（死链）：{', '.join(dead[:5])}")


def required_sections_check(sections, template: str) -> Tuple[List[str], List[str]]:
    """返回 (缺失角色列表, 命中角色列表)。"""
    roles = TEMPLATE_REQUIRED.get(template, TEMPLATE_REQUIRED["auto"])
    missing, present = [], []
    for role in roles:
        if find_section(sections, role) is None:
            missing.append(role)
        else:
            present.append(role)
    # auto 模式附加：若用矛盾标记则强制矛盾台账
    if template == "auto" and find_section(sections, "contradiction") is None:
        if RE_CONFLICT_WORD.search("".join(b for _, b in sections)):
            missing.append("contradiction")
    return missing, present


def validate(path: str, template: str, strict: bool, check_links: bool) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    sections = split_sections(text)
    missing, present = required_sections_check(sections, template)

    rules = []

    # 必含章节（前置硬门禁）
    if missing:
        rules.append({
            "id": "R0-sections",
            "desc": "必含章节（模板 %s）" % template,
            "status": "FAIL",
            "detail": "缺失角色：" + ", ".join(missing) + "；命中：" + ", ".join(present),
        })
    else:
        rules.append({
            "id": "R0-sections",
            "desc": "必含章节（模板 %s）" % template,
            "status": "PASS",
            "detail": "全部命中：" + ", ".join(present),
        })

    # lint 1-6
    s1, d1, _ = check_rule1_evidence(text)
    rules.append({"id": "R1-provenance", "desc": "每条源带 (URL/DOI, 层级, 日期)", "status": s1, "detail": d1})
    s2, d2 = check_rule2_confirmed(text)
    rules.append({"id": "R2-confirmed", "desc": "Confirmed 须 >=2 独立 T1-3", "status": s2, "detail": d2})
    s3, d3 = check_rule3_contradiction(text, sections)
    rules.append({"id": "R3-contradiction", "desc": "矛盾未强行合一（双方案并列）", "status": s3, "detail": d3})
    s4, d4 = check_rule4_inference(text)
    rules.append({"id": "R4-inference-low", "desc": "推断/解读标 LOW 且注明假设", "status": s4, "detail": d4})
    s5, d5 = check_rule5_open(sections)
    rules.append({"id": "R5-open-env", "desc": "开放问题列环境受限未覆盖项", "status": s5, "detail": d5})
    s6, d6 = check_rule6_links(text, check_links)
    rules.append({"id": "R6-links", "desc": "无死链（默认关闭）", "status": s6, "detail": d6})

    # 覆盖率指标（可解释）
    provenance_cov = _provenance_coverage(text)
    confirmed_backing = _confirmed_backing(text)
    coverage = {
        "provenance_coverage_pct": provenance_cov,
        "confirmed_backing_pct": confirmed_backing,
    }

    fails = [r for r in rules if r["status"] == "FAIL"]
    warns = [r for r in rules if r["status"] == "WARN"]
    passed = [r for r in rules if r["status"] == "PASS"]
    skipped = [r for r in rules if r["status"] == "SKIP"]

    if fails:
        overall = "FAIL"
    elif warns and strict:
        overall = "FAIL"
    else:
        overall = "PASS"

    return {
        "file": path,
        "template": template,
        "strict": strict,
        "overall": overall,
        "rules": rules,
        "counts": {"pass": len(passed), "warn": len(warns), "fail": len(fails), "skip": len(skipped)},
        "coverage": coverage,
    }


def _provenance_coverage(text: str) -> Optional[float]:
    """带层级证据行中「含 日期+可识别来源」的比例。无证据表 -> None（N/A）。"""
    total = 0
    ok = 0
    for rows in parse_tables(text):
        header = [c.lower() for c in rows[0]]
        if not any("层级" in h or h == "tier" for h in header):
            continue
        if not any("日期" in h or h == "date" for h in header):
            continue
        try:
            tier_idx = next(k for k, h in enumerate(header) if "层级" in h or h == "tier")
            date_idx = next(k for k, h in enumerate(header) if "日期" in h or h == "date")
        except StopIteration:
            continue
        for r in rows[2:]:
            if len(r) <= max(tier_idx, date_idx):
                continue
            if not RE_TIER.search(r[tier_idx]):
                continue
            total += 1
            date_ok = bool(RE_DATE.search(r[date_idx]))
            has_source = any(
                (RE_URL.search(c) or RE_DOI.search(c) or (len(c.strip()) >= 2 and not RE_TIER.match(c.strip())))
                for c in r
            )
            if date_ok and has_source:
                ok += 1
    if total == 0:
        return None
    return round(ok / total * 100, 1)


def _confirmed_backing(text: str) -> Optional[float]:
    """Confirmed 断言是否有 >=2 独立 T1-3 合格引用：有则 100，无则 0；无 Confirmed -> None。"""
    if not (re.search(r"Confirmed", text, re.IGNORECASE) or RE_CONFIRMED_TAG.search(text)):
        return None
    distinct = set((t, s) for (t, _, s) in qualified_citations_in(text))
    return 100.0 if len(distinct) >= 2 else 0.0


def render_human(report: dict) -> str:
    lines = []
    lines.append("=" * 64)
    lines.append("dmr 终稿机检门禁 · 模板 %s · 严格=%s" % (report["template"], report["strict"]))
    lines.append("文件: %s" % report["file"])
    lines.append("=" * 64)
    sym = {"PASS": "✔ PASS", "FAIL": "✘ FAIL", "WARN": "⚠ WARN", "SKIP": "· SKIP"}
    for r in report["rules"]:
        lines.append("[%s] %s — %s" % (sym.get(r["status"], r["status"]), r["id"], r["desc"]))
        lines.append("        %s" % r["detail"])
    cov = report["coverage"]
    pc = "N/A" if cov["provenance_coverage_pct"] is None else ("%.1f%%" % cov["provenance_coverage_pct"])
    cb = "N/A" if cov["confirmed_backing_pct"] is None else ("%.1f%%" % cov["confirmed_backing_pct"])
    lines.append("-" * 64)
    lines.append("覆盖率: 来源充分性(provenance)=%s | Confirmed支撑=%s" % (pc, cb))
    lines.append("统计: PASS=%d WARN=%d FAIL=%d SKIP=%d" % (
        report["counts"]["pass"], report["counts"]["warn"],
        report["counts"]["fail"], report["counts"]["skip"]))
    lines.append(">>> 总判定: %s <<<" % report["overall"])
    lines.append("=" * 64)
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="dmr 终稿程序化机检门禁（零依赖，离线安全）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("report", help="待检报告 markdown 路径")
    p.add_argument("--template", default="auto", choices=["A", "B", "C", "D", "E", "auto"],
                   help="模板类型（默认 auto：最小必含章节并集）")
    p.add_argument("--strict", action="store_true", help="WARN 也视为失败（用于 CI 硬门禁）")
    p.add_argument("--check-links", action="store_true", help="联网验活 URL（默认关闭，离线安全）")
    p.add_argument("--json", action="store_true", help="输出 JSON（供 CI 解析）")
    args = p.parse_args(argv)

    try:
        report = validate(args.report, args.template, args.strict, args.check_links)
    except FileNotFoundError:
        sys.stderr.write("错误: 文件不存在 -> %s\n" % args.report)
        return 2
    except Exception as e:  # noqa: BLE001
        sys.stderr.write("错误: 解析失败 -> %s\n" % e)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_human(report))

    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
