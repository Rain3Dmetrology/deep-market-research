# 常见问题（FAQ）

---

**Q1：这个 skill 和普通的 WebSearch / WebFetch 有什么区别？**

A：WebSearch / WebFetch 是"检索工具"，本 skill 是"调研工作流"--在检索之上叠加源分级（T1-T4）、>=2 源交叉验证、去重去旧去假去矛盾、置信标签、模板化输出与增量沉淀。单条 WebSearch 不会自动产出带置信度的可复现报告。

---

**Q2：核心数据源（OpenAlex / 知乎 MCP / 学术 API）连不上怎么办？**

A：按质量规则 15 处理--显式标注"该维度因环境受限未覆盖"，列入「开放问题」，绝不降级为低置信结论或编造；并换用兜底源（web 抓取 / 其他 API / 已连 MCP），注明降级路径。环境限制 != 能力不足。

---

**Q3：什么时候用模板 B / C / D？**

A：按查询意图路由：行业赛道 -> 模板 B（含销售触发词时必含 §3.5）；公司/竞品 -> 模板 C（四维 + SWOT + 情景）；论文/学术 -> 模板 D（学术引文）；纯概览 -> 模板 A；持续监测且有上期快照 -> 模板 E。触发词与强制项以 SKILL.md 第四节「模板选择」为唯一权威；模式可叠加。

---

**Q4：需要付费 API key 或本地安装吗？**

A：**都不需要**。本技能默认零依赖、零安装--只用 LLM 内置 `web_search` / `web_fetch` + 免费公开 REST API（OpenAlex / Semantic Scholar / Crossref / arXiv / PubMed 等无需 key）。Exa / Firecrawl / Tavily / Perplexity / GPT Researcher / ModelScope 等是**可选增强**：有 key 且平台支持才启用，无则优雅跳过，质量不降。一份 SKILL.md 即可在 WorkBuddy / Claude / Codex / Trae / qoder / Cursor 等任意平台使用，无需改代码。各平台可选工具接入方式见 references/cross-platform-tools.md。

---

**Q5：源之间矛盾怎么办？**

A：不随机选、不多数暴力。按源层级（T1>T2>T3>T4）、时效（近 3-6 月优先）、详实度裁决；无法裁决则多方案并存并标注矛盾。绝不强行共识（Cat-Research 自验证闭环）。

---

**Q6：报告会不会太长？**

A：默认跑完整 Step 0-8；用户要"快版"时至少保留 Step1 + Step4 + Step8，并在报告注明"快版，未全覆盖质量环"。模板 B / C 强制非散文元素（矩阵 / 图表 / 清单），避免纯散文堆字。

---

**Q7：增量知识沉淀一定要用 ima 吗？**

A：ima-mcp 是首选，notion / Obsidian / 本地 wiki / 任意知识库均可；关键是三层结构（raw / wiki / schema）+ 重跑 Lint。不强制。

---

**Q8：中文 / CJK 源（公众号、知乎、小红书、CNKI 等）能正常处理吗？**

A：能，且是 dmr 的差异化优势。dmr 原生支持中文源采集与中文报告输出；对比竞品 hyperresearch 的已知缺陷（issue #37：其 `looks_like_junk()` 把**所有中文 / CJK 页面当 junk 直接丢弃**），dmr 明确保留中文页并视为一等信源（T3 / T4 按属性分级）。中文市场 / 竞品调研请放心使用，无需 workaround。
