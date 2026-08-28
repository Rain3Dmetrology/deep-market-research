#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_report.py — deep-market-research (dmr) 程序化终稿机检门禁

定位
----
dmr SKILL.md「终稿纪律 · 5 输出前 lint 自检清单」的**可度量前置机检**。
把原本人工勾选的 6 项（或后续校验环节的 ①来源充分性 维度）升级为 PASS/FAIL 门禁，
输出覆盖率，供单 agent 模式交付前或 CI 拦截使用。

设计纪律（对齐 dmr 平台无关/零依赖护城河）
------------------------------------------
- **仅用 Python 标准库**（re / argparse / sys / json / urllib），不引入 pyyaml / 第三方包。
- **离线安全**：死链检查（lint 第6项）默认关闭，需显式 --check-links 才联网；无网环境不会误 FAIL。
- **不阻断主管线**：本脚本是「门禁建议」，不修改报告、不调用任何 agent / 进程。
- **机检≠语义证明**：凡涉及「论证是否充分」「是否真独立」之处，均为可解释启发式，
  输出会显式标注启发式边界，避免伪造确定性。
- **排版容差（防误报）**：章节标题带限定词（如「矛盾台账（证据冲突裁决记录）」）
  视为命中对应角色；「层级」格以 T1-T4 开头才算证据行（散文提及「T1-3」不误判）；
  R2 合格引用同时计入内联「源A(T1, 日期)」与证据表行（层级 + 日期 + URL/DOI/裸域名），
  对齐 §七 实体级证据缓存表形态；auto 模式检测到「本期变化总览」即按模板 E 角色集
  校验（模板 E 无独立矛盾台账章节，冲突由置信迁移/双方案并列承载）——
  机检不因 LLM 排版变体或模板形态误报 FAIL。
- **v2.8 校验器加固（审计 M4 + T-05 合并修复）**：R1「可识别来源」复用 R2 的
  `_source_id` 严格判定（URL>DOI>裸域名），杜绝旧分支「日期单元格本身即满足」
  的空操作；R2/Confirmed 由文档级启发式升级为断言级校验——每个 [Confirmed]
  标注断言须在局部窗口（同章节或 ±6 行）内有 >=2 个独立 T1-3 合格引用，
  大量无支撑 Confirmed 判 FAIL；无标签的 Confirmed 字样保留文档级容差，
  由测试守护（见 tests/test_validate_report.py）。

用法
----
    python scripts/validate_report.py <报告.md> [--template A|B|C|D|E|auto] [--strict] [--check-links] [--json]

退出码
------
    0 = 通过（无 FAIL；WARN 不致命，除非 --strict）
    1 = 未通过（至少一项 FAIL）
    2 = 用法 / 文件错误

作者：dmr v2.4.x 单 agent 验证路径（A 项落地）。不依赖任何团队协作协议。
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
# 裸域名（无 scheme，如 keyence.com.cn / overview.ai）：末位标签须为纯字母 2-6 位，
# 排除数值误报（83.0% / v2.6.1 / 2026.08.22 均不匹配）。
RE_BARE_DOMAIN = re.compile(r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,6}\b", re.IGNORECASE)
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
    """返回第一个命中该角色的节正文；未命中返回 None。

    标题装饰容差：先做精确匹配（任一候选完全相等）；无精确命中再做包含匹配——
    「矛盾台账（证据冲突裁决记录）」命中「矛盾台账」、「质量自检与方法论合规声明」
    命中「方法论与合规声明」。LLM 产出常给章节名追加限定词，机检不为此误报缺章节。
    """
    wanted = ROLE_TITLES[role]
    for title, body in sections:
        if title in wanted:
            return body
    for title, body in sections:
        if any(w in title for w in wanted):
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


def _source_id(s: str) -> Optional[str]:
    """从文本片段提取可识别来源：URL > DOI > 裸域名。

    裸域名（无 scheme）取域名部分（不含路径），同一站点不同路径不会
    被计为多个独立源；纯数字/版本号（83.0%、v2.6.1）不构成来源。
    """
    m = RE_URL.search(s)
    if m:
        return m.group(0)
    m = RE_DOI.search(s)
    if m:
        return m.group(0)
    m = RE_BARE_DOMAIN.search(s)
    if m:
        return m.group(0)
    return None


def qualified_citations_in(text: str) -> List[Tuple[str, str, str]]:
    """
    提取「合格引用」：含 T1-T3 层级 + 日期 + 可识别来源。
    覆盖两种形态：
      (a) 源A(T1, 2025-03) —— 来源令牌在括号外（dmr 主流写法）；
      (b) (https://... T1 2025-03) —— URL/DOI/裸域名在括号内（兜底）。
    返回 [(tier, date, source_id)]，source_id 取 URL/DOI 或裸域名。
    用于 lint 第2项（Confirmed 需 >=2 独立 T1-3）。
    """
    out = []
    # 形态 (a)
    for src_tok, tier, date in RE_CITE.findall(text):
        if len(src_tok) < 1:
            continue
        out.append((tier, date, src_tok))
    # 形态 (b)：括号内同时含 T1-3 + 日期 + URL/DOI/裸域名
    for grp in RE_PAREN.findall(text):
        tier_m = RE_TIER.search(grp)
        if not tier_m:
            continue
        tier = "T" + tier_m.group(1)
        if tier not in ("T1", "T2", "T3"):
            continue
        dm = RE_DATE.search(grp)
        if not dm:
            continue
        src = _source_id(grp)
        if src:
            out.append((tier, dm.group(0), src))
    return out


def evidence_tables(text: str):
    """产出 (rows, tier_idx, date_idx)：表头同时含「层级」与「日期」的证据表。"""
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
        yield rows, tier_idx, date_idx


def table_citations_in(text: str) -> List[Tuple[str, str, str]]:
    """证据表行引用：行内同时含 T1-3 层级（层级格以 T 开头）、日期与 URL/DOI/裸域名。

    dmr §七 强制「实体级证据缓存表」（实体 | 字段 | 值 | 源URL | 层级 | 日期 | 置信），
    以表格承载证据的报告同样给 R2 计入合格引用，而非只认内联「源A(T1, 日期)」形态。
    源列写裸域名（keyence.com.cn，无 scheme）同样视为可识别来源。
    """
    out: List[Tuple[str, str, str]] = []
    for rows, tier_idx, date_idx in evidence_tables(text):
        for r in rows[2:]:
            if len(r) <= max(tier_idx, date_idx):
                continue
            tm = RE_TIER.match(r[tier_idx])
            if not tm or tm.group(1) not in ("1", "2", "3"):
                continue
            dm = RE_DATE.search(r[date_idx])
            if not dm:
                continue
            src = None
            for c in r:
                src = _source_id(c)
                if src:
                    break
            if src:
                out.append(("T" + tm.group(1), dm.group(0), src))
    return out


def check_rule1_evidence(text: str) -> Tuple[str, str, int]:
    """
    lint 第1项：每条 T 层级证据行须带 层级 + 日期 + 可识别来源。
    只在「表头含 层级 且含 日期」的证据表中检查数据行；层级格须以 T1-T4 开头
    才算证据行（散文中提及「T1-3」不误判）。
    """
    violations = 0
    total_tiered = 0
    for rows, tier_idx, date_idx in evidence_tables(text):
        for r in rows[2:]:  # 跳过表头 + 分隔
            if len(r) <= max(tier_idx, date_idx):
                continue
            tier_cell = r[tier_idx]
            tm = RE_TIER.match(tier_cell)
            if not tm:
                continue
            total_tiered += 1
            date_ok = bool(RE_DATE.search(r[date_idx]))
            # M4 修复（v2.8）：「可识别来源」复用 R2 的 _source_id 严格判定
            # （URL>DOI>裸域名）。旧分支 `(len>=2 and not RE_TIER.match)` 会被日期单元格
            # 本身满足，使 R1 实际只检查了日期（空操作），故废弃。
            has_source = any(_source_id(c) for c in r)
            if not (date_ok and has_source):
                violations += 1
    if total_tiered == 0:
        return ("WARN", "未发现带层级的证据表行（报告可能用纯内联引用；第1项无法机检，建议人工核对）", 0)
    if violations == 0:
        return ("PASS", f"全部 {total_tiered} 行带层级证据均含 层级+日期+可识别来源", total_tiered)
    return ("FAIL", f"{violations}/{total_tiered} 行带层级证据缺 日期 或 可识别来源", total_tiered)


# T-05 修复（v2.8）：R2 断言级校验的启发式参数。
# 局部窗口 = 同章节 ∪ 断言行 ±R2_BACKING_WINDOW 行；无支撑断言占比 <= 该阈值时
# 仅 WARN（排版变体容差），超过则 FAIL（极端情况：大量无支撑 Confirmed 不得放行）。
# 容差行为的守护场景：审计 T-05（文档级启发式下 30 条 Confirmed 中 29 条无支撑仍 PASS）。
R2_BACKING_WINDOW = 6
R2_UNBACKED_WARN_RATIO = 0.2


def confirmed_assertion_lines(text: str) -> List[Tuple[int, str]]:
    """返回带 [Confirmed] 类置信标签的断言行 [(行号, 行文本)]。
    断言级校验的入口：只对有显式标签的断言逐条求支撑。
    """
    out = []
    for i, line in enumerate(text.splitlines()):
        if RE_CONFIRMED_TAG.search(line):
            out.append((i, line))
    return out


def _section_line_ranges(text: str) -> List[Tuple[int, int]]:
    """各 ## 章节的行区间 [(start, end)]，供断言级局部窗口定位同章节引用。"""
    heads = [text.count("\n", 0, m.start()) for m in RE_HEADER.finditer(text)]
    n = text.count("\n") + 1
    return [(heads[k], heads[k + 1] if k + 1 < len(heads) else n) for k in range(len(heads))]


def _citation_lines(text: str) -> Dict[int, List[Tuple[str, str]]]:
    """行号 -> 该行承载的 [(tier, source_id)]（仅 T1-3）。

    覆盖两种形态：内联「源A(T1, 日期)」/「(https://... T1 2025-03)」，以及证据表
    数据行（行内同时含 T1-3 层级格 + 日期 + URL/DOI/裸域名）。与
    qualified_citations_in/table_citations_in 同一套判定语义，仅多了行号定位。
    """
    out: Dict[int, List[Tuple[str, str]]] = {}
    for i, line in enumerate(text.splitlines()):
        cites: List[Tuple[str, str]] = []
        for src_tok, tier, _date in RE_CITE.findall(line):
            if src_tok:
                cites.append((tier, src_tok))
        for grp in RE_PAREN.findall(line):
            tm = RE_TIER.search(grp)
            if not tm:
                continue
            tier = "T" + tm.group(1)
            if tier not in ("T1", "T2", "T3"):
                continue
            if not RE_DATE.search(grp):
                continue
            src = _source_id(grp)
            if src:
                cites.append((tier, src))
        stripped = line.strip()
        if stripped.startswith("|") and not cites:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            tier_cell = None
            for c in cells:
                tm = RE_TIER.match(c)
                if tm and tm.group(1) in ("1", "2", "3"):
                    tier_cell = "T" + tm.group(1)
                    break
            if tier_cell and any(RE_DATE.search(c) for c in cells):
                for c in cells:
                    src = _source_id(c)
                    if src:
                        cites.append((tier_cell, src))
                        break
        if cites:
            out.setdefault(i, []).extend(cites)
    return out


def _assertion_backing(text: str) -> Dict[int, bool]:
    """逐条 [Confirmed] 断言求局部支撑：窗口 = 同章节 ∪ ±R2_BACKING_WINDOW 行。

    返回 {断言行号: 窗口内独立 (tier, source_id) >=2}。启发式边界：窗口外但同文档的
    引用不计入——这正是相对旧版文档级启发式的收紧点（审计 T-05）。
    """
    cit = _citation_lines(text)
    cit_idxs = sorted(cit.keys())
    ranges = _section_line_ranges(text)
    result: Dict[int, bool] = {}
    for i, _line in confirmed_assertion_lines(text):
        local = set()
        for j in cit_idxs:
            if abs(j - i) <= R2_BACKING_WINDOW:
                local.update(cit[j])
        for (a, b) in ranges:
            if a <= i < b:
                for j in cit_idxs:
                    if a <= j < b:
                        local.update(cit[j])
                break
        result[i] = len(local) >= 2
    return result


def check_rule2_confirmed(text: str) -> Tuple[str, str]:
    """
    lint 第2项：Confirmed 须 >=2 独立 T1-3 合格引用。
    v2.8（审计 T-05）升级为断言级校验：每个 [Confirmed] 标签断言须在局部窗口
    （同章节或 ±R2_BACKING_WINDOW 行）内有 >=2 独立支撑；无支撑占比超过阈值判 FAIL。
    向后兼容容差：无标签的 Confirmed 字样（散文/历史形态）仍走文档级启发式，
    由 test_tagless_confirmed_mention_keeps_doc_level_tolerance 守护。
    """
    quals = qualified_citations_in(text) + table_citations_in(text)
    distinct = set((t, s) for (t, _, s) in quals)
    tags = confirmed_assertion_lines(text)
    if not tags:
        if not re.search(r"Confirmed", text, re.IGNORECASE):
            return ("PASS", "报告未使用 Confirmed 断言，第2项不适用")
        if len(distinct) >= 2:
            return ("PASS", f"Confirmed 字样由 {len(distinct)} 个独立 T1-3 合格引用支撑（>=2，文档级容差）")
        return ("FAIL", f"Confirmed 字样仅由 {len(distinct)} 个独立 T1-3 合格引用支撑（要求 >=2）；请补充交叉源或降档")
    backing = _assertion_backing(text)
    total = len(backing)
    unbacked = sum(1 for ok in backing.values() if not ok)
    if unbacked == 0:
        return ("PASS", f"全部 {total} 条 [Confirmed] 断言均有局部窗口内 >=2 独立 T1-3 合格引用支撑")
    pct = unbacked / total
    if pct <= R2_UNBACKED_WARN_RATIO:
        return ("WARN", f"{unbacked}/{total} 条 [Confirmed] 断言未在局部窗口（同章节或 ±{R2_BACKING_WINDOW} 行）找到 >=2 独立支撑（启发式，建议人工复核）")
    return ("FAIL", f"{unbacked}/{total} 条 [Confirmed] 断言缺局部支撑（要求 >=2 独立 T1-3）；无支撑占比 {pct:.0%} 超容差 {R2_UNBACKED_WARN_RATIO:.0%}，请降档或补引用")


def check_rule3_contradiction(text: str, sections) -> Tuple[str, str]:
    """
    lint 第3项：矛盾未强行合一（双方案并列）。
    - 若报告出现矛盾标记但未设 矛盾台账 章节 -> FAIL。
    - 若设了 矛盾台账 章节但为空/无双方案 -> WARN。
    - 模板 E（监测增量）无独立矛盾台账章节：冲突由「置信迁移/变化项明细」承载，
      以全文双方案并列标记（并存/方案A|B/双口径）替代章节存在性检查。
    """
    has_conflict_word = bool(RE_CONFLICT_WORD.search(text))
    ledger = find_section(sections, "contradiction")
    is_e_style = find_section(sections, "delta") is not None
    if has_conflict_word and ledger is None:
        if is_e_style:
            if re.search(r"说法[AB]|方案[AB]|并存|双方案|双口径", text):
                return ("PASS", "模板 E 监测报告：冲突经置信迁移/双方案并列显式标注（模板 E 无独立矛盾台账章节）")
            return ("FAIL", "模板 E 报告出现矛盾标记，但未见双方案并列（并存/方案A|B/双口径）")
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
    """返回 (缺失角色列表, 命中角色列表)。

    auto 模式模板识别：检测到「本期变化总览」（delta 角色）即按模板 E 角色集校验——
    模板 E 监测增量报告无执行摘要/矛盾台账独立章节，套用 A-D 角色集会误报缺章节。
    """
    roles = TEMPLATE_REQUIRED.get(template, TEMPLATE_REQUIRED["auto"])
    is_e_style = find_section(sections, "delta") is not None
    if template == "auto" and is_e_style:
        roles = TEMPLATE_REQUIRED["E"]
    missing, present = [], []
    for role in roles:
        if find_section(sections, role) is None:
            missing.append(role)
        else:
            present.append(role)
    # auto 模式附加：若用矛盾标记则强制矛盾台账（模板 E 除外：冲突由置信迁移承载）
    if template == "auto" and not is_e_style and find_section(sections, "contradiction") is None:
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
    for rows, tier_idx, date_idx in evidence_tables(text):
        for r in rows[2:]:
            if len(r) <= max(tier_idx, date_idx):
                continue
            if not RE_TIER.match(r[tier_idx]):
                continue
            total += 1
            date_ok = bool(RE_DATE.search(r[date_idx]))
            has_source = any(_source_id(c) for c in r)  # M4 修复：同 R1 严格判定
            if date_ok and has_source:
                ok += 1
    if total == 0:
        return None
    return round(ok / total * 100, 1)


def _confirmed_backing(text: str) -> Optional[float]:
    """Confirmed 支撑覆盖率（断言级，v2.8/T-05）：获局部支撑的 [Confirmed] 断言百分比。
    无标签的 Confirmed 字样退回旧文档级语义（100/0）；无 Confirmed -> None。"""
    tags = confirmed_assertion_lines(text)
    if tags:
        backing = _assertion_backing(text)
        if not backing:
            return 0.0
        return round(100.0 * sum(1 for ok in backing.values() if ok) / len(backing), 1)
    if not re.search(r"Confirmed", text, re.IGNORECASE):
        return None
    distinct = set((t, s) for (t, _, s) in qualified_citations_in(text) + table_citations_in(text))
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


def _configure_stdio() -> None:
    """把 stdout/stderr 设为 UTF-8，避免 Windows 默认 GBK 控制台无法输出 ✔/✘/⚠ 等字符时
    print 抛 UnicodeEncodeError、进程以退出码 1 崩溃（合法样例也拿不到 PASS 退出码）。
    与 scripts/setup_mcp.py 入口适配同语义；按「脚本独立可运行」惯例各脚本自包含，
    不提取共享模块。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main(argv=None) -> int:
    _configure_stdio()
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
        # ensure_ascii=True：JSON（机器可读）路径输出纯 ASCII，即使 stdout 编码受限
        # 也不受 errors="replace" 破坏；json.loads 对 \uXXXX 转义无损还原。
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_human(report))

    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
