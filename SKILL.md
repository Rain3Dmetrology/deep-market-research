---
name: deep-market-research
slug: deep-market-research
displayName: Deep Market Research
version: "2.3.2"
summary: 深度市场 / 竞品 / 技术趋势调研工作流，输出稳定、可复现、带引用溯源的研究报告。
description: |
  深度市场 / 竞品 / 技术趋势调研工作流，输出稳定、可复现、带引用溯源的研究报告。

  v2.3.2 核心能力：
  • 确定性 Step 0→8 流水线（意图路由 → 检索 → 去重 → 评分 → 对抗审计 → 沉淀）
  • NATO 式 4 级源分级 + ≥2 源交叉验证（关键竞品参数 ≥3 源）
  • 主动去重 / 去陈旧 / 去伪造 / 去矛盾 4 道过滤 + 置信标签
  • 平台无关：默认零依赖，可选 MCP/API 后端优雅降级
  • 中英双语 + 中英双文档，本地 / 仓库 / 发布包三端一致

  适用：市场调研、竞品分析、行业格局、技术趋势、竞品对位、尽调、产业链研究、投资机会发现。
license: MIT
compatibility: >
  Platform-agnostic: runs on ANY agent that loads skills / system prompts
  (WorkBuddy / CodeBuddy / Claude / Codex / Trae / qoder / Cursor and others).
  DEFAULT = ZERO local dependency: relies only on the agent's built-in web_search /
  web_fetch plus 🆓 free public REST APIs (OpenAlex etc.). No MCP config, no local
  process, no install required.
  Optional enhancement tools (Exa / Firecrawl / Tavily / Perplexity / GPT Researcher /
  ModelScope) are platform-specific and gracefully skipped when absent — see
  references/cross-platform-tools.md for per-platform setup. This skill NEVER assumes
  any specific platform's MCP file, agent-team protocol, or proprietary backend exists.
  Complementary research skills (web-access, agent-reach, wechat-article-search,
  literature-search, etc.) are absorbed methodologically where available; absent ones
  are skipped gracefully. v2.2.1 已永久删除重复冗余且已被吸收的 6 个 skill：
  google-scholar-search / academic-research-hub / deep-research / news-summary / perplexity /
  tavily（永久删除，不可逆）；其方法论已并入本流程。
  Search entry: built-in web_search / web_fetch (primary, zero-dependency); optional AI search
  backends (Tavily / Perplexity / AnySearch / 秘塔搜索, key-gated, NON-default, gracefully skip
  if absent) — AnySearch 76.4% benchmark is a [VENDOR CLAIM], do NOT treat as independent proof.
  Platform-specific optional tools (patents / finance / legal / enterprise-risk MCPs, GitHub,
  macro data, WeChat articles, knowledge bases, etc.) are listed per-platform in
  references/cross-platform-tools.md and degrade gracefully when absent.
  Scholarly / open-science sources — v2.2.0 expanded, FREE public REST APIs preferred
  (🆓 directly callable via WebFetch/curl, no key or DEMO_KEY, far more robust than scraping):
  OpenAlex (api.openalex.org — 250M+ works metadata, MAG successor), Semantic Scholar
  (api.semanticscholar.org/graph/v1 — citation graph + TLDR; **keyless but ~100 req/5min/IP, free key raises limit**), Crossref (api.crossref.org —
  authoritative DOI metadata + references → citation provenance), arXiv (export.arxiv.org/api —
  preprints), PubMed (eutils.ncbi.nlm.nih.gov — E-utilities, biomedical), bioRxiv/medRxiv
  (api.biorxiv.org — bio preprints), OpenCitations (opencitations.net/index/api/v1 — open
  citation network), EMBL-EBI / Europe PMC (ebi.ac.uk — bioinformatics + life-science lit).
  Research-data / output repositories (🆓 free API): Zenodo (zenodo.org/api — CERN, DOI-minted),
  Figshare (api.figshare.com/v2), Harvard Dataverse (dataverse.harvard.edu/api), NASA
  (api.nasa.gov + data.nasa.gov). Nature/Science + CNKI: authoritative but full-text mostly
  paywalled (abstracts public) — T1–T2 journals, cite DOI. Google Scholar: no official API,
  user-exports only (access-ethics). literature-search skill = cleanest methodology reference (kept);
  academic-research-hub (Proprietary + OpenClawCLI) and google-scholar-search (misnamed Semantic
  Scholar wrapper) were redundant → both uninstalled in v2.2.1 (permanently removed, irreversible).
  Grade papers/preprints as T3 (authoritative preprints may rise to T2).
  Code / AI-model platforms: GitHub search + Trending (gh CLI authenticated + web),
  Hugging Face Hub API (🆓 huggingface.co/api — 公频模型 metadata + 公开权重免 token；**gated 模型（如 Llama）需登录 + 接受 EULA 才能下载**), ModelScope /魔塔 (modelscope.cn — Chinese model
  hub; 可选 token 直调). Patents: patsnap-search MCP（可选）,
  Google Patents / USPTO / EPO / WIPO (public web).
  Engineering-discussion & UGC (cross-validation signals, T4 unless authoritative): Stack Overflow
  + Hacker News (🆓 free Algolia API; **Firebase 端点 2023 已停服**；部分网络出口 IP 可能被 Algolia WAF 屏蔽 → 回退 web_search), Reddit (2023 起需 OAuth → agent-reach / web_search 兜底), Zhihu (zhihu MCP，可选),
  CSDN, Product Hunt, TechCrunch, 36Kr, Bluesky, X, Wikipedia / Baidu Baike (background, T3),
  plus Xiaohongshu / Bilibili via agent-reach (实测 6 社媒 + 5 基础; 抖音/微博 走 web_search 兜底, 公众号 走 wechat-article-search skill).
  HONESTY RULE: only list skills/connectors actually available in the environment.
  Firecrawl (and any other absent service) is NOT bundled and must never be claimed as integrated.
metadata:
  version: "2.3.2"
  author: "Rain / WorkBuddy"
  adapted_from: "sota-research (Rain3Dmetrology) + RSSnewsnowTrendRadar (Rain3Dmetrology) 三方三角验证与联网查证注入机制 + 行业趋势深度调研五大板块模板 + 公司竞品深度调研四维框架/7字段证据清单/SWOT/情景推演 + market-researcher 的 TAM/SAM/SOM 市场测算/竞品4类法/2D定位图(作可选透镜) + material-organizer 的去重阈值与逐字引用铁律 + llm-wiki 的 Karpathy 增量沉淀/Lint 操作 + 黄益贺精英级分析咨询系统(Coze) 的 OPTIONAL 分析透镜库(波特五力/PESTEL/3C/BCG/价值链) + aihot/news-summary 注册为可选数据源 + NATO Admiralty source code + Cat-Research self-validation loop"
---

# Deep Market Research Workflow — 深度市场调研工作流

> 版本: 2.3.2 | 许可证: MIT
> 设计目标：**输出质量稳定、可复现、去重去旧去假去矛盾、并吸收真实用户热评**。对行业/赛道/产业链类查询，额外输出麦肯锡白皮书风格的五大板块结构；对公司/竞品尽调类查询，额外输出四维分析、7字段证据清单、SWOT 与情景推演。

---

## 〇、为什么是这套流程（质量稳定的根基）

质量不稳定来自三件事：**源不分级、无交叉验证、临场发挥**。本工作流用三条硬规则消除它们：

1. **确定性流水线**：每次都走 Step 0→8 同一套阶段，不跳步、不临场发明结构 → 可复现。
2. **生成/验证分离**：综合（写）与核查（验）分阶段进行；关键事实单元必须 ≥2 个独立源确认才标 `Confirmed`；**竞品关键参数（定价/版本号/MCP 支持/许可证/收购归属等可量化事实）须 ≥3 个独立源确认**（普通事实维持 ≥2 以控成本）。
3. **源分级 + 置信标签**：每条结论都带「源层级 + 置信度」，读者一眼知道能信到什么程度。

本流程吸收自以下已验证方法（含可卸载 skill 的择优吸收，详见 P0 吸收审计）：
- `sota-research` 的工程化（三层降级链、按标题去重、被引数交叉验证、100分评分 A+~D）
- `RSSnewsnowTrendRadar` 的**三方三角验证 + 联网查证注入**（热榜/大众情绪 × RSS/专家 × 实时搜索三方差异=认知套利点；验证查询库优先级化+成本封顶+优雅降级）
- **行业趋势深度调研**的五大板块模板与三段递进检索（行业定义与市场大局 → 产业链图谱与核心玩家 → 驱动力与痛点 → 1-2年趋势与红利 → 商业化建议与避坑；每板块至少一个非散文元素）
- **公司竞品深度调研**的四维证据框架、7字段证据清单、SWOT、五类情景推演与真实负面深度挖掘（知乎/小红书/黑猫投诉/脉脉/Glassdoor/Reddit/裁判文书；单一匿名不升置信度）
- **market-researcher**（P0 卸载项，择优吸收为可选透镜）：TAM/SAM/SOM 市场测算（top-down × bottom-up 交叉，差异>3x 重审）、竞品 4 类法（直接/间接/替代/潜在）、2D 定位图 —— 仅作分析透镜，不吸其一手调研方法（问卷/Van Westendorp 定价）
- **material-organizer**（P0 卸载项，择优吸收）：去重操作阈值（相似度>70% 或同源 或标题编辑距<3 合并；对立观点双方案保留）、逐字引用铁律（关键摘录原文 `>` 引用块，数字日期与源一致，缺口标"信息不足"不猜）
- **llm-wiki**（P0 卸载项，强吸收）：Karpathy 三层知识结构（raw 源页 / wiki 合成页 / schema）+ Lint 操作（重跑同主题扫描矛盾/过时/孤儿页）—— 填补"跨次矛盾/过时无人管"缺口，与用户第二大脑知识系对齐
- **aihot**（P0 卸载项，弱吸收）+ **news-summary**（P0 卸载项，弱吸收）：注册为可选数据源（aihot 免 key 中文 AI 资讯；BBC/Reuters/Al Jazeera 国际一手新闻；引用二手摘要须回溯源 URL）
- 黄益贺精英级分析咨询系统(Coze) 的 OPTIONAL 分析透镜库（波特五力/PESTEL/3C/BCG/价值链，仅作可选透镜）
- NATO Admiralty 信源评估码（A–F 可靠性 + 1–6 确认度）→ 适配为 4 级源分级
- Cat-Research / OpenClaw 自验证闭环（事实单元拆解 + 多源交叉验证 + 矛盾消解不强行共识）
- **版本演进（摘要）**：v2.0.0 竞争对位实测 → v2.1.0 吸收 9 个互补研究类 skill 的方法论（去其过度约束项）→ v2.2.0 大幅扩充学术与开放科研数据源（优先 🆓 免费 API 直调）→ v2.2.1 去粗取精执行（永久删除 6 个冗余 absorbed skill，GitHub MCP 集成）→ v2.2.2 / v2.2.3 文档准确性与一致性修正 → **v2.2.4 规范性增强（新增 FAQ / 完整示例 / 本附录，并补充"环境受限≠能力不足"质量规则）**。**完整更新史与每项细节见文末「附录 A」。** → **v2.2.5 方法论 sharpening（AnySearch 对齐）→ v2.2.6 对抗审计纪律（hyperresearch 吸收）** → **v2.2.7 P1 集成（可选后端 + 沉淀结构化）+ 去粗取精（Step1 意图路由）** → **v2.2.8 README 特性区重构（倒序 + 中英双语 + 去冗）** → **v2.2.9 全仓库审计修正（Qoder 拼写 / 去隐私注释 / AgentKey 重归类 / Google Drive / 中英双文档拆分）** → **v2.2.10 可选搜索后端附录补强（AnySearch / 秘塔搜索 CN 可选增强）** → **v2.3.0 平台无关 + 深度研究闭环（去粗取精、泛化优先）** → **v2.3.1 MCP 鉴权前缀修复 + 跨机器同步 + 可选源增补（FRED / Novada / Connected Papers / agent-reach）**。


> **模式选择**（第四节提供三套模板）：
> - **通用深度调研模板**：通用主题、企业/产品/技术概览。
> - **行业赛道模式**：当用户查询含"行业/赛道/产业链/投资机会/趋势预测/商业化落地/市场规模"时，默认采用模板 B，强制利润穿透、反方观点、1–2 年趋势、每板块至少一个非散文元素。
> - **公司/竞品模式**：当用户查询含"公司/竞品/尽调/扒一下/挖一下/对位/对标/我们和 A/B/C"时，默认采用模板 C，强制四维分析（商业模式与基本盘、核心产品与卖点、营销与流量、真实负面与风险）、7 字段证据清单、SWOT、五类情景推演、真实负面多渠道交叉验证。
> - **学术/基准/技术选型/尽调模式**：当用户查询含"论文/SOTA/学术/基准/技术选型/文献综述/学术尽调"时，默认采用模板 D（源自 deep-research 吸收），在主管线基础上启用"学术数据源模块"与严格引文格式（`Authors. Title. Venue. Year. DOI/URL`）。

### 互补 Skill 方法论吸收 (v2.1.0)

对 9 个已安装、与本研究域重叠的研究类 skill 做了审计，择优吸收其方法论，**明确拒绝**各自的过度约束项。吸收均为**叠加**，不替换本流程主管线/主模板。

| 来源 Skill | 吸收的方法论 | 明确拒绝（防过度约束） |
|---|---|---|
| **intel-osint-daily** | 信息项"事实→影响→原因"三元（可作 intel-brief 输出风格）；"三方交叉验证"命名强化；`[矛盾]/[待核实]/[已证伪]` 标记（对齐本流程去重/去伪规则）；连续监测思路 | 其 `≤1450字 JSON、禁 Markdown/emoji` 硬格式；TrendRadar 专属变量 |
| **macro-monitor** | 宏观数据源清单（Trading Economics/FRED/国家统计局/央行/证监会/财联社/华尔街见闻）作可选"宏观监测"源；"每指标配白话解读 + 超预期/不及预期 vs 预期/前值"规则 | 其 `browser`/OpenClawCLI 路径在本环境不存在→改走 web-access |
| **news-summary**（v2.2.1 已永久删除，方法论已吸收）| RSS 源（BBC/Reuters/Al Jazeera/NPR）并入可选数据源 | 语音播报（超范围） |
| **deep-research**（v2.2.1 已永久删除，方法论已吸收）| 命令式入口（`/research`→outline→`/research-deep`并行→`/research-report`）；outline + 并行 per-item 搜索模式；学术/基准/技术选型/尽调模式→第 4 模板 | 不替换确定性 Step0→8 + 三级模板 |
| **agent-reach** | 补齐 UGC 平台覆盖（实测 6 社媒：X/Reddit/Facebook/Instagram/B站/小红书 + 5 基础：GitHub/V2EX/RSS/Web/YouTube + 3 可选：小宇宙/雪球/LinkedIn；**抖音/微博 走 web_search 兜底，公众号走 wechat-article-search skill，非 agent-reach 频道**） | 不引入其安装/代理复杂度；dmr 仅引用 |
| **wechat-article-search** | 新增"公众号**文章**检索"为具体中文信号源（补 UGC 评论之外的文章级缺口） | 不复制其 node 依赖规则 |
| **perplexity**（v2.2.1 已永久删除，方法论已吸收）| 注册为可选 AI 搜索源（仅当 `PERPLEXITY_API_KEY` 存在） | 不作强制入口，仍以 Tavily/WebSearch 为主 |
| **academic-research-hub**（v2.2.1 已永久删除，方法论已吸收）| 多源学术检索（arXiv/PubMed/Semantic Scholar/Google Scholar）+ 引文处理（BibTeX/RIS/JSON）作学术模块 | 其 OpenClawCLI 硬依赖；**许可 Proprietary**——嵌入脚本前须确认再分发权 |
| **literature-search** | 范围澄清步骤；学术源访问伦理；按引用数+时效去重；严格 `作者.题名.出处.年.DOI/URL` 引文格式 | 不重复实现去重（本流程已有） |

> 学术三件套 overlap 提示：`academic-research-hub` + `literature-search` + `google-scholar-search` 同覆盖学术细分；吸收前两者后第三者冗余。v2.2.1 已将 `academic-research-hub` 与 `google-scholar-search` 一并永久删除，仅留 `literature-search` 作方法论参考。

#### 新增模块 1：学术与开放科研数据源模块（v2.2.0 大幅扩充，去粗取精、优先免费 API）

当用户查询含"论文/SOTA/技术基准/学术/引用/文献/科研数据/开源模型"时，可启用学术检索分支。**核心原则（去粗取精）**：多数权威学术源都有**免费公开 REST API**，可经 WebFetch/curl **直调**——比抓 HTML 或依赖 Proprietary/需外部 CLI 的 skill 更稳、更可复现。故本模块以「🆓 免费 API 直调」为首选，「🌐 通用联网可达（抓取/导出）」为兜底。

**A. 学术论文 / 元数据 / 引文溯源（🆓 免费 API 优先，均免 key）**

| 源 | 入口 | 定位 | 层级 |
|----|------|------|------|
| **OpenAlex** | `api.openalex.org/works?search=` | 2.5 亿+ 论文/作者/机构元数据（MAG 继任者），学术元数据主库 | T3 |
| **Semantic Scholar** | `api.semanticscholar.org/graph/v1/paper/search` | 引用网络 + TLDR 摘要 + 影响力字段（**无 key 限 ~100 req/5min·IP，可申请免费 key 提额**） | T3 |
| **Crossref** | `api.crossref.org/works?query=` | 权威 DOI 元数据 + 参考文献 → **引文溯源**主库 | T2–T3 |
| **OpenCitations** | `opencitations.net/index/api/v1` | 开放引文网络（被引/引用关系）→ **引文溯源**补充 | T3 |
| **arXiv** | `export.arxiv.org/api/query?search_query=` | 预印本（CS/物理/数学/AI），Atom API | T3（权威预印本可升 T2） |
| **PubMed** | `eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed` | 生物医学文献库（E-utilities） | T3 |
| **bioRxiv / medRxiv** | `api.biorxiv.org/details/biorxiv/` | 生物/医学预印本 | T3 |
| **EMBL-EBI / Europe PMC** | `ebi.ac.uk` + `ebi.ac.uk/europepmc/webservices/rest/search` | 生物信息查询 + 生命科学文献 | T3 |
| **Nature / Science 等期刊** | 官网 / DOI | 顶刊一手（摘要公开，全文多需订阅） | **T1–T2**，引 DOI |
| **知网 CNKI** | 官网检索 | 中文核心文献（多需订阅） | T3 |
| **Google Scholar** | 无官方 API | **仅用户导出**使用（访问伦理，不自动抓取） | T3 线索 |

**B. 科研数据 / 成果仓库（🆓 免费 API，均带 DOI，可溯源）**

| 源 | 入口 | 定位 |
|----|------|------|
| **Zenodo** | `zenodo.org/api/records?q=` | CERN 综合科研数据/软件/成果（DOI-minted） |
| **Figshare** | `api.figshare.com/v2/articles?search_for=` | 学术成果/图表/数据集 |
| **Harvard Dataverse** | `dataverse.harvard.edu/api/search?q=` | 哈佛多学科研究数据源 |
| **NASA** | `api.nasa.gov` + `data.nasa.gov` | 航天/地球公共数据（DEMO_KEY 免费） |

**C. 专利 / 代码 / AI 模型**

| 源 | 入口 | 状态 |
|----|------|------|
| **智慧芽 PatSnap** | `patsnap-search` MCP | ✅ 真实可用（专利检索/家族/引用分析） |
| **Google Patents / USPTO / EPO / WIPO** | 公开检索 | 🌐 通用联网可达 |
| **GitHub 搜索 + Trending** | `github` MCP + `gh` CLI（已认证）+ web | 开源实现/技术栈/Star·PR 趋势（MCP 直连优先，gh CLI 兜底） |
| **Hugging Face** | `huggingface.co/mcp`（可选 MCP）| 🎯 可选（模型/数据集/Spaces/Papers，若平台已连） |
| **魔塔 ModelScope** | `modelscope` MCP（可选）| 🎯 可选（模型/数据集/论文，若平台已连） |

- **范围澄清（先问后搜，源自 literature-search）**：主题、子领域、综述 vs 奠基性、时间范围。
- **访问伦理**：不抓禁止自动访问或需登录的站点；Google Scholar 仅经用户导出；订阅库（Scopus/Web of Science）仅当用户提供 key/账号时启用，否则标"未覆盖"。
- **去重 / 分级**：按引用数 + 时效性去重，重复时保留期刊/会议正式版优先于预印本；论文/综述按 T3 处理（权威预印本可升 T2）。
- **引文格式（严格）**：`Authors. Title. Venue. Year. DOI/URL`；支持 BibTeX / RIS / JSON 导出；优先保留原文 DOI/URL，避免二手摘要失真。
- **技能取舍（优胜劣汰 · v2.2.1 落地）**：`literature-search`（纯方法论、官方 API 优先、无外部 CLI）为最优参考 → **保留**；`academic-research-hub`（Proprietary + 依赖 OpenClawCLI）、`google-scholar-search`（实为 Semantic Scholar 封装、命名误导）、`deep-research`（工作流已被吸收）、`news-summary`（RSS 已被吸收）、`perplexity`/`tavily`（与内置 WebSearch 重复的 AI 搜索）均属重复冗余且已被吸收 → **已于 v2.2.1 全部永久删除（不可逆）**。`agent-reach`/`wechat-article-search`/`intel-osint-daily`/`macro-monitor` 因独特能力或独立调度角色 → **保留**。

#### 新增模块 2：intel-brief 输出风格（源自 intel-osint-daily，可选）

对"每日/每周监测"或"决策快报"类查询，可在模板 A 基础上叠加 intel-brief 风格——每条信息按三元素组织：

- **事实（Fact）**：发生了什么（带源层级 + 日期）。
- **影响（Impact）**：对决策者意味着什么（业务/投资/技术）。
- **原因（Cause / Why）**：为何发生（驱动因素/背景）。

并显式标注矛盾/待核实/已证伪：`[矛盾]`（与既有结论冲突）、`[待核实]`（单源待补）、`[已证伪]`（被 ≥2 权威源推翻，已从结论剔除）。本流程原有的"矛盾台账"可继续承载这些标记。

#### 新增模块 3：宏观监测源（源自 macro-monitor，可选）

当用户查询含"宏观/利率/通胀/GDP/政策/大宗"时，可接入宏观数据源（均通用联网可达，T3）：Trading Economics、FRED、国家统计局、央行/证监会官网、财联社、华尔街见闻。每条宏观指标须附**白话解读**与**超预期/不及预期判断**（对比一致预期值与前值）。

#### 新增模块 4：微信公众账号文章检索（源自 wechat-article-search）

中文 AI/科技/商业信号常首发于公众号文章。经 `wechat-article-search` skill 检索公众号文章，作为中文一手深度内容源（T3，视媒体属性）；与既有 UGC 评论（T4）互补，填补"文章级"缺口。

#### 新增模块 5：Perplexity AI 搜索（可选源，源自 perplexity）

当 `PERPLEXITY_API_KEY` 存在时，可将 Perplexity 作为带引用的 AI 搜索入口之一，与 Tavily/WebSearch 并列（不强制、不作唯一入口）。无 key 时优雅跳过。

### 分析透镜库（可选，按查询意图触发，非强制全套）

经典咨询框架是**分析透镜**而非研究管线。它们帮 AI 在「已验证的数据」上做更深入的结构化思考，但**不替代**本流程的采集/分级/交叉验证/去伪。仅当查询意图匹配时才调用，**禁止每篇报告硬塞 12 个框架**。

| 透镜 | 类型 | 触发场景 | 映射到模式 | 用途 |
|------|------|----------|-----------|------|
| **波特五力** | 行业结构 | 行业/赛道竞争强度分析 | 模板 B §3.2 | 供应商/买方议价、新进入者/替代品/同行竞争强度 |
| **PESTEL** | 宏观环境 | 行业大势、政策/技术驱动 | 模板 B §3.1/§3.3 | 政治/经济/社会/技术/环境/法律六维扫描 |
| **价值链 (Value Chain)** | 利润结构 | 利润穿透、成本卡点 | 模板 B §3.2（利润穿透底座） | 研发→生产→营销→售后各环节价值/成本归属 |
| **BCG 矩阵** | 产品组合 | 多产品线公司评估 | 模板 C §3.1 | 明星/金牛/问号/瘦狗，资源配置判断 |
| **3C 战略三角** | 竞争定位 | 竞品对位、差异化 | 模板 C §3.2/§6 | Company/Customer/Competitor 三角均衡 |
| **STP / 4P / AARRR** | 增长/营销 | 研究目标含"上市/增长/GTM" | 模板 C §3.3（可选） | 细分定位 / 营销组合 / 用户生命周期增长 |
| **MECE / 金字塔原理** | 思维原则 | 已内嵌 | 全模板 | 拆解无遗漏(MECE)、结论先行(金字塔)——无需显式调用 |
| **TAM/SAM/SOM** | 市场测算 | 市场规模/总量评估 | 模板 B §3.1 | top-down × bottom-up 交叉验证，差异>3x 重审（源自 market-researcher） |
| **竞品 4 类法** | 竞争分类 | 竞品格局梳理 | 模板 B §3.2 / 模板 C §6 | 直接/间接/替代/潜在竞争者分类（源自 market-researcher） |
| **2D 定位图** | 战略定位 | 差异化定位可视化 | 模板 C §6 | 二维矩阵呈现公司/竞品生态位（源自 market-researcher） |

> 规则：透镜是「分析深度」的加分项，不是「研究质量」的必需项。本流程的质量由源分级+交叉验证保证，透镜只在用户要"战略/竞争/增长/市场测算"视角时附加。market-researcher 的一手调研方法（问卷/Van Westendorp 定价）**不吸收**——本流程定位二手案头研究。

---

## 一、源分级体系（NATO Admiralty 适配）

每条采集到的信息都先评**源层级**与**确认度**，再决定决策权重。

| 层级 | 类型 | 典型来源 | 决策权重 | 用法 |
|------|------|----------|----------|------|
| **Tier 1** | 一手/官方 | 官方公告、财报、招股书、专利原文、政府/监管备案、企业官网产品页 | 决策级（可被直接引用定结论） | 终裁事实、关键数字 |
| **Tier 2** | 专家/HUMINT | 行业专家访谈、前员工/竞品客户、KOL 深度长文、G2/Capterra **已验证**评价 | 高（需三角验证） | 上下文、口碑、未公开历史 |
| **Tier 3** | 二手/官方记录 | 权威媒体（Reuters/彭博/36氪等）、行业研报、法院/工商记录、学术文献 | 事实地基 | 所有权、财务、诉讼、监管状态 |
| **Tier 4** | OSINT/社媒 UGC | 小红书/微博/Reddit/知乎/B站/YouTube 评论、匿名帖、第三方估算（如 Sensor Tower DAU） | 仅作线索 | 发现微弱信号、用户真实情绪；**不可单独定结论** |

**确认度（Confirmation）**：`1 已确认 / 2 很可能 / 3 可能 / 4 存疑 / 5 不太可能 / 6 无法判断`。
例：`B-2` = 通常可靠源 + 很可能为真；`E-5` = 不可靠源 + 不太可能。

> 规则：**Tier 4 单独支撑的结论，最多标 `Single-source / Unverified`，绝不标 `Confirmed`。** 只有 ≥2 个 **独立 Tier 1–3** 源一致，才标 `Confirmed`。

---

## 二、置信度标签（贯穿全文）

每条发现/结论必须带一个标签：

- ✅ **Confirmed** — ≥2 个独立 Tier 1–3 源一致确认（**竞品关键参数须 ≥3 个独立源**，见质量规则 18）
- 🟢 **Corroborated** — 1 个 Tier 1–3 源 + ≥1 个 Tier 4 源旁证，或 2 个 Tier 4 源高度一致
- 🟡 **Single-source** — 仅 1 个 Tier 1–3 源，无旁证（注明"待更多源确认"）
- 🔴 **Unverified / Conflicting** — 无可靠源，或源间矛盾且无法裁决（**显式标注，不强行共识**）

---

## 三、工作流全景图

```
输入: 调研问题 / 主题 / 竞品名 (如 "工业 AI 3D 视觉测量 竞争格局")
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 0: 范围收敛 (引导式)                                  │
│  澄清: 决策用途? 竞品集(T1/T2/T3)? 地理/时间范围? 输出形态? │
│  中英文关键词映射 + 歧义消解 → 精确研究边界                │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 1: 多源采集 (分层降级链 + 三段递进搜索)                │
│  意图路由(Thin Router): 按查询意图选源——法律→威科/元典/北大法宝,   │
│    专利→智慧芽, 代码→GitHub, 学术→🆓API, 中文UGC→知乎/    │
│    小红书/公众号; 不每题全量扫所有源; 下方为可选菜单       │
│  搜索策略: 第一段宏观锚定(市场规模/CAGR/政策)            │
│           第二段产业链解剖(上下游利润分配/玩家格局/卡脖子) │
│           第三段趋势预测与避坑(红利/颠覆技术/失败案例/反向)│
│  搜索入口(基座并行): 内置 WebSearch/WebFetch 始终调用 + 若已配置 Tavily/Perplexity/AgentKey 并行增强(无 key 跳过); 多源以 Step 4 交叉验证裁决 │
│  专业数据库: 通达信(A股F10) 智慧芽(专利) 自选股/westock(财报) │
│             威科/元典/北大法宝(法律) 天眼查/企查查/启信慧眼(工商风险)    │
│             GitHub(gh CLI+web,Trending) ima(知识库)/notion              │
│  社媒/UGC: 知乎(MCP:search+热榜)/小红书/CSDN/Reddit/HN/SO/Bluesky/X/B站(信号,agent-reach实测6社媒+5基础;抖音/微博走web_search,公众号走wechat-article-search) │
│  学术论文(🆓免费API直调优先): OpenAlex/Semantic Scholar/arXiv/PubMed/bioRxiv/EMBL-EBI(Europe PMC) │
│  引文溯源: Crossref(DOI元数据+参考文献)/OpenCitations(开放引文网络)  │
│           顶刊: Nature/Science(引DOI,T1-2); CNKI/Google Scholar(仅导出) │
│  科研数据仓库(🆓免费API): Zenodo/Figshare/哈佛Dataverse/NASA(均带DOI) │
│  专利: 智慧芽/Google Patents/USPTO/EPO/WIPO              │
│  代码/模型: Hugging Face(🆓API)/魔塔ModelScope(用户有token)  │
│  百科/背景: Wikipedia/百度百科                             │
│  产品/创投: Product Hunt/TechCrunch/36氪/虎嗅
│  宏观监测: Trading Economics/FRED/统计局/央行/证监会/财联社/华尔街见闻 │
│  公众号文章: 经 wechat-article-search 检索(中文一手深度,补文章级缺口) │              │
│  文档:     markitdown 处理 PDF/财报/Word → Markdown         │
│  可选资讯: aihot(免key中文AI资讯) BBC/Reuters/Al Jazeera     │
│           (国际一手新闻; 引用二手摘要须回溯源URL)            │
│  降级:     主源失败自动切次源；每源记 (url, 日期, 层级)     │
│  可选深度抓取后端: hyperresearch(Claude Code 环境,          │
│    pip install 后作可选深度抓取; key-gated, 失败则跳过,    │
│    不阻断 Step 0→8 主管线)                                │
│  查证库:   维护优先级验证查询库(政策>人才>SOTA>社区反馈)，  │
│           ≤18查×≤3结果控成本；无搜索key则优雅跳过不阻断    │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 2: 去重 + 去旧 + 信号门 + URL 验活                    │
│  去重: 归一化标题/正文 → 内容哈希 → 同一信息只留最完整版   │
│        (信息密度优先: 同义结论优先取含数字/一手数据/        │
│         specifics 更密的一版);                            │
│        阈值: 相似度>70% 或 同源 或 标题编辑距<3 → 合并;    │
│        对立观点双方案保留(不强行合一, 见 Step 5);          │
│        合并后若某域仍聚簇多个同质结果,排序做多样性权重      │
│        (同源衰减),避免单域霸屏                            │
│  去旧: 市场/趋势类主张优先近 3–6 月；                      │
│        早于去年的数据强制标注 `outdated`（可作历史参考）  │
│        常青事实(官方文档/基本面)保留但标"evergreen"        │
│  排序准则: 语义相关度 × 时效 × 源层级 三轴混合——          │
│        先按与查询意图的相关度粗排,再按时效与源层级精排      │
│        (与 Step 5 冲突裁决轴 源层级>时效>详实度 互补)       │
│  信号门: 超新鲜窗口(默认>7天且非evergreen)丢弃；          │
│          低信号(<阈值)噪声项降级或剔除                     │
│  假源过滤: 清 SEO 站/内容农场/机器 spun 文(低信号高广告)   │
│  URL 验活: 输出前批量验证引用链接可访问，死链/失效源剔除   │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 3: 源分级 (逐条贴 Tier + 确认度)                     │
│  每条原始信息 → (Tier, Confirmation) → 进证据池           │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 4: 交叉验证 + 去假 + 强制反方观点 (生成/验证分离)     │
│  事实单元拆解: 把结论拆成不可再分的事实点(数字/事件/关系) │
│  三角验证: 大众情绪场(热榜) × 专家源(RSS/论文/官方) ×    │
│          实时联网查证 三方差异=认知套利点，冲突处重点标   │
│  强制反方: 行业赛道类问题必须主动检索反向观点/失败案例/   │
│          看空报告/踩坑经验，至少 1 个 contrarian 视角     │
│  每点需 ≥2 独立源确认才标 Confirmed(竞品关键参数须 ≥3)；    │
│  单源→Single-source；无源/矛盾→Unverified                 │
│  去假: 与 ≥2 权威源冲突的"事实"→标记为疑似虚假并剔除结论 │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 5: 矛盾消解 (不强行共识)                              │
│  源冲突时: 按 源层级↑ > 时效↑ > 证据详实度↑ 裁决          │
│  仍无法定 → 标 Conflicting，双方案并列 + 各自信源         │
│  严禁: 随机选一个 / 多数暴力表决掩盖分歧                  │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 6: 吸收真实用户热评 + 真实负面风险信号 (UGC 信号提取) │
│  通用社媒: 经 agent-reach/web-access 拉 小红书/知乎/Reddit/B站/YouTube│
│  公司/竞品专用负面渠道: 黑猫投诉(消费者投诉)、脉脉(员工匿名)、│
│                         Glassdoor(海外员工)、裁判文书(法律风险)    │
│  规则: 单一匿名爆料不升置信度；必须 ≥2 独立来源互证才进入报告主体    │
│  负面信息原文保留、不得软化；必须标注"匿名"风险与 Tier 4 定位      │
│  信号过滤: 高赞/高互动 + 实质性(具体经历/数据) 非情绪党同             │
│  重点挖: 真实落地口碑/踩坑/采用温差(Reddit/SO/知乎/CSDN/            │
│          Medium)，专盯"官方PR vs 用户实测"的 Gap                     │
│  分离: 用户真实反馈 vs 官方PR/水军；标注 平台+互动量                  │
│  定位: 作为"用户情绪/痛点信号"(Tier 4)，不混入硬事实                 │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 7: 综合 + 100分评分 (质量环 ratchet)                 │
│  评分维度(例: 竞品/技术): 市场存在感30 + 技术成熟度25      │
│           + 势头/动量20 + 用户口碑15 + 风险10 → A+~D       │
│  质量环: ≥2 轮(最多5)，Critic 多维打分，ratchet 保最优版  │
│  对抗审计: 终稿前跑 corpus critic + ≥2 类并行 critic        │
│    (事实一致性/源层级一致性/时效/反向观点遗漏)→ 缺陷回对应  │
│    Step 修补, 不整篇 regenerate 掩盖                        │
│  加权质量分 = 源25% + 事实35% + 结论40%                    │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 8: 结构化输出 (见第四节模板)                         │
│  含: 执行摘要 / 源分级表 / 带置信度发现 / 矛盾台账        │
│       / 用户热评洞察 / 评分 / 开放问题 / 方法论与免责     │
└──────────────────────────────────────────────────────────┘
```

---

### 三-B、深度研究闭环（平台无关，纯提示词编排）

> **本技能不依赖任何特定平台的 agent / team 编排协议。** 深度研究由 LLM 自身按以下闭环执行——任何加载本技能的 agent（WorkBuddy / Claude / Codex / Trae / qoder / Cursor 等）都能复现。此闭环与 Step 0–8 主管线正交，质量同样由源分级 + 交叉验证保证。
>
> 吸收自多平台深度研究 agent 团队的精华（多轮迭代、章节级审稿、研究参数卡跨阶段共享、进度通报），**去其平台专有约束**（Agent Team 协议、消息中转、特定 MCP 配置文件），做成纯提示词、可移植、零依赖。

**① 研究参数卡（跨阶段共享上下文）**
从 Step 0 起维护一张精简参数卡（研究课题 / 范围 / 已收集源池 / 大纲 / 已完成章节摘要）。每次阶段切换时**整卡传递**给下一阶段，避免跨阶段信息丢失——这是深度研究"不跑偏、不重复搜"的关键。

**② 五阶段闭环（深度研究专用）**
- **Phase 1 初始调研**：广泛初调生成研究摘要（覆盖定义背景 / 主流观点 / 争议焦点 / 关键数据 / 主要参与者 / 最新进展）。
- **Phase 2 规划大纲**：基于摘要规划 3–5 章大纲（逻辑递进、不重叠、无遗漏）。
- **Phase 3 逐章深度研究**：每章走 `检索 → 草稿 → 审稿 →（修订）→ 复审` 闭环。审稿按 6 维（来源充分性 / 事实准确性 / 观点均衡性 / 内容深度 / 结构清晰度 / 格式规范性）审查；最多 3 轮，第 3 轮强制通过并附「遗留改进建议」。
- **Phase 4 撰写框架**：引言 / 结论 / 目录 / 参考文献（APA 格式、去重排序）。
- **Phase 5 发布整合**：章节连续编号 + 分隔线 + 链接检查 + 参考文献去重。

**③ 章节级进度通报**：每完成一章按模板向用户通报（章节序号 / 来源数 / 审稿轮次），让用户感知进度、及时纠偏。

> 此闭环**完全由提示词驱动，不调用任何外部 agent / 进程**；可选工具（Exa / Firecrawl / GPT Researcher 等）只在 Step 1 采集阶段作为素材源接入，缺失则回退内置搜索，不影响闭环本身。

---

### 终稿纪律：对抗式审计 + 来源树 + lint 自检（吸收 hyperresearch 方法论，纯提示词零依赖）

> 以下为 Step 7→8 终稿阶段的质量纪律，**不新增工具、不新增数值门槛、不阻断 Step 0→8 主管线**。

- **① 对抗式审计（adversarial audit）**：终稿交付前，必须独立跑一轮「对抗式审计」——以一个 corpus critic 通读全篇找自相矛盾/无源结论，并至少并行 2 类 critic 角色挑战：
  - *事实一致性 critic*：每条结论是否都有对应 (源, 层级, 日期) 支撑？
  - *源层级 critic*：是否把 Tier 4 当成了硬事实？Confirmed 是否真有 ≥2 独立 Tier1–3？
  - *时效 critic*：趋势/市场类主张是否用了近 3–6 月？outdated 是否标了？
  - *反向观点 critic*：是否遗漏了 contrarian / 失败案例 / 看空视角（尤其行业赛道类）？
  - 发现缺陷 → **回到对应 Step 局部修补**，不整篇 regenerate 掩盖旧错。

- **② patch-never-regenerate 原则**：终稿只允许 surgical edit（局部 patch）；禁止为「修正一处」而整篇重新生成（regenerate 易丢失已验证事实、引入新错）。每次 patch 后重跑一次对抗审计确认未引入回归。

- **③ canonical query gospel（用户原话贯穿）**：Step 0 澄清出的「决策用途 / 竞品集 / 地理时间范围 / 输出形态」是 gospel，贯穿全篇；终稿必须可逐条回推到原始问题，**禁止临场偷换议题或扩大范围**。范围蔓延须显式标注「超出原定范围」。

- **④ provenance 来源树**：关键结论须能回溯到传导链——一手源(T1) → 二手源(T3) → 社媒信号(T4) 的来龙去脉，建议以「来源树」呈现（谁引用谁、哪级定结论），不可只抛结论无痕。与第二节置信标签互补。

- **⑤ 输出前 lint 自检清单**（交付前逐项勾，缺一项不交付）：
  1. 每条源带 (URL/DOI, 层级, 日期)；
  2. Confirmed 须 ≥2 独立 Tier1–3，否则降档；
  3. 矛盾未强行合一（Conflicting 双方案并列）；
  4. 推断/解读标 LOW 且注明假设；
  5. 开放问题已列「环境受限未覆盖」项（规则 15）；
  6. 无死链（Step 2 URL 验活通过）。

## 四、输出模板（每次调研都套用，保证稳定）

> **模板选择**：
> - 通用主题（企业/产品/技术概览）→ 用「通用深度调研模板」。
> - 行业/赛道/产业链/趋势预测/投资机会 → 用「行业赛道五大板块模板」，强制利润穿透、反方观点、1-2年趋势、每板块至少一个非散文元素。
> - 公司/竞品/尽调/对位分析 → 用「公司/竞品深度调研模板」，强制四维分析、7字段证据、SWOT、情景推演、真实负面多渠道验证。
> - 论文/SOTA/学术/基准/技术选型/文献综述 → 用「模板 D：学术/基准/技术选型/尽调模板」，启用学术数据源模块与严格引文格式。
>

### 模板 A：通用深度调研模板

```markdown
# 深度调研报告：<主题>

> 生成时间: <ISO> ｜ 调研范围: <地理/时间/竞品集> ｜ 质量分: <0–100>
> 方法论: deep-market-research v2.3.1（源分级 + 三方三角验证 + ≥2源交叉验证 + 矛盾显式标注 + 增量Lint）

## 1. 执行摘要
- 三句话结论 + 最高置信度的 3 个关键发现 + 最大不确定性。

## 2. 信源分级一览
| 源 | 层级 | 确认度 | 日期 | 用途 |
|----|------|--------|------|------|
| ... | T1/T2/T3/T4 | A-1.. | | |

## 3. 核心发现（带置信度）
### 3.1 <子主题>
- **发现**：... ［Confirmed/Corroborated/Single-source/Unverified］
  - 证据：源A(T1, 日期) + 源B(T3, 日期)

## 4. 矛盾台账（显式，不掩盖）
| 争议点 | 说法A(源/层级) | 说法B(源/层级) | 裁决 | 置信 |
|--------|---------------|---------------|------|------|
| ... | | | 采纳A(层级更高/更新) / 并存待核 | |

## 5. 真实用户热评洞察（Tier 4 信号）
- **痛点**：<高赞具体反馈，平台+互动量> — 作为情绪信号，非硬事实
- **好评**：...
- **水军/PR 识别**：已剔除的疑似营销内容说明

## 6. 评分卡（竞品/技术）
| 对象 | 市场存在感 | 技术成熟度 | 势头 | 用户口碑 | 风险 | 总分 | 评级 |
|------|-----------|-----------|------|---------|------|------|------|
| ... | /30 | /25 | /20 | /15 | /10 | /100 | A+.. |

## 7. 开放问题（未能验证，需人工/后续）
- ...

## 8. 方法论与合规声明
- 源分级与交叉验证规则简述；Tier 4 内容仅作信号。
- 合规：商业版默认不启用 cookie 爬取；本报告含社媒内容仅作个人研究参考。
```

### 模板 B：行业赛道五大板块模板（麦肯锡白皮书风格）

```markdown
# 行业趋势深度调研：<赛道/行业>

> 生成时间: <ISO> ｜ 调研范围: <地理/时间> ｜ 质量分: <0–100>
> 方法论: deep-market-research v2.3.1 行业赛道模式

## 1. 执行摘要
- 三句话结论 + 3 个最高置信度发现 + 最大不确定性。

## 2. 信源分级一览

## 3. 核心发现：五大板块
### 3.1 行业定义与当年市场大局观
- 定义、市场规模（多源对比表）、CAGR、区域分布、当年关键事件。
- 每个数字带 [Confirmed/Corroborated/Single-source] 标签。

### 3.2 产业链图谱与核心玩家格局
- 产业链 Mermaid 图（上游零部件 → 中游设备 → 下游应用）。
- 利润分配：钱/利润卡在哪一层？卡脖子环节在哪？
- 核心玩家表格（梯队、定位、关键数据）。

### 3.3 核心驱动力与行业发展痛点
- 驱动力（≥3 条，带置信度）。
- 痛点（≥3 条，优先真实用户反馈）。

### 3.4 1–2 年趋势预测与红利爆发点
- 只覆盖 1–2 年，拒绝 5 年+ 大饼。
- 趋势表：趋势 / 置信度 / 红利爆发点 / 时间窗口。
- 每趋势至少一个非散文元素（趋势表/预测图/象限图）。

### 3.5 商业化落地建议与避坑指南
- 针对不同决策角色（创业者/投资者/企业战略）给出分层建议。
- 决策树或风险矩阵（非散文元素）。
- 避坑：失败案例、反向观点、常见误区。

## 4. 矛盾台账（显式，不掩盖）

## 5. 真实用户热评洞察（Tier 4 信号）
- 重点挖"官方 PR vs 用户实测" Gap。

## 6. 评分卡（核心玩家/技术路线）

## 7. 开放问题

## 8. 方法论与合规声明
```

### 模板 C：公司/竞品深度调研模板

```markdown
# 公司/竞品深度调研：<目标公司> [vs <竞品 A/B/C>]

> 生成时间: <ISO> ｜ 调研范围: <地理/时间> ｜ 质量分: <0–100>
> 方法论: deep-market-research v2.3.1 公司/竞品模式

## 0. 决策卡片（一页纸给决策者）
- **一句话定位**: <公司在产业链中的核心位置>
- **关键数字**: 营收/估值/市占率/员工数（带源和置信度）
- **最大优势**: <经 ≥2 源确认>
- **最大风险**: <经 ≥2 源确认，或来自 Tier 1 单一源>
- **3 个可执行建议**: 1) ... 2) ... 3) ...

## 1. Executive Summary
- 三句话结论 + 3 个最高置信度发现 + 最大不确定性。

## 2. 7 字段结构化证据清单
| 证据 ID | 事实陈述 | 来源 URL | 原文摘录 | 层级 | 确认度 | 置信度 | 日期 |
|---------|---------|----------|----------|------|--------|--------|------|
| F001 | ... | | | T1/T2/T3/T4 | A-1.. | Confirmed/... | |

> 规则：每条进入主体报告的结论必须先在证据清单中找到支撑；冲突证据双条保留并标注矛盾性质。

## 3. 四维度分析

### 3.1 商业模式与基本盘
- 盈利模式、收入结构、核心客户、成本结构、护城河。
- 关键数据：营收、毛利率、融资/市值、员工规模、核心股东。

### 3.2 核心产品与杀手级卖点
- 产品线、核心技术/专利、差异化卖点、定价区间。
- 与竞品的功能/性能/价格对标表（至少 1 张表）。

### 3.3 营销与流量操盘策略
- 获客渠道、品牌定位、内容/活动/投放策略、渠道策略。
- 流量/口碑数据来源（如 SimilarWeb、App 排名、社媒互动量）。

### 3.4 真实负面与风险事件（必须多渠道交叉）
- 消费者端：黑猫投诉、小红书/微博吐槽、知乎差评。
- 员工端：脉脉、Glassdoor（海外）。
- 法律/监管：裁判文书、行政处罚、威科/元典法律检索。
- 媒体/做空：看空报告、 investigative 报道、失败案例。
- 规则：单一匿名爆料不升置信度；≥2 独立来源互证才写入主体；负面原文保留、不软化。

## 4. SWOT 分析（事实 / 解读 / 推断 三层分离）
| 维度 | 事实（带证据 ID） | 解读（基于事实的合理推论） | 推断（需额外假设，标 LOW 置信） |
|------|------------------|---------------------------|-------------------------------|
| 优势(S) | | | |
| 劣势(W) | | | |
| 机会(O) | | | |
| 威胁(T) | | | |

> 规则：禁止把推断当事实陈述；事实层必须绑定 7 字段证据 ID。

## 5. 情景推演（覆盖五类场景，每类给出触发条件与可执行预案）
| 场景 | 触发条件（可观察） | 影响评估 | 可执行预案 |
|------|-------------------|----------|-----------|
| 价格竞争 | 竞品降价 X% / 发布低价版 | | |
| 产品突袭 | 竞品发布突破性产品/技术 | | |
| 资本动作 | 融资/并购/IPO/撤资 | | |
| 市场扩张 | 进入新区域/新行业 | | |
| 风险事件 | 监管处罚/重大舆情/核心人员变动 | | |

## 6. 横向对比矩阵（多家报告必含）
| 维度 | 本公司 | 竞品 A | 竞品 B | 竞品 C |
|------|--------|--------|--------|--------|
| 定位 | | | | |
| 核心产品 | | | | |
| 定价区间 | | | | |
| 优势 | | | | |
| 风险 | | | | |
| 综合评级 | | | | |

## 7. 评分卡（100分制）
| 对象 | 商业模式清晰度 | 产品力 | 市场/品牌 | 财务健康 | 风险/负面 | 总分 | 评级 |
|------|--------------|--------|----------|----------|-----------|------|------|
| ... | /20 | /25 | /20 | /20 | /15 | /100 | A+.. |

## 8. 开放问题（未能验证，需人工/后续）
- ...

## 9. 方法论与合规声明
- 源分级、≥2源交叉验证、真实负面多渠道验证规则简述。
- 合规：Tier 4 匿名内容仅作信号；商业使用需确认各数据源 ToS。
```

---

### 模板 D：学术 / 基准 / 技术选型 / 尽调模板（源自 deep-research 吸收）

```markdown
# 学术 / 基准 / 技术选型调研：<主题>

> 生成时间: <ISO> ｜ 调研范围: <地理/时间/文献集> ｜ 质量分: <0–100>
> 方法论: deep-market-research v2.3.1 学术/基准模式（启用学术数据源模块 + 严格引文格式）

## 1. 执行摘要
- 三句话结论 + 3 个最高置信度发现 + 最大不确定性。

## 2. 研究范围澄清
- 主题、子领域、综述 vs 奠基性、时间范围（源自 literature-search 的范围澄清步骤）。

## 3. 文献 / 技术证据清单（带置信度）
| 证据 ID | 事实陈述 | 来源(OpenAlex/Semantic Scholar/Crossref/arXiv/PubMed/bioRxiv/Zenodo/HF/GitHub) | 原文摘录 | 层级 | 确认度 | 置信度 | 日期 | 引用(DOI/URL) |
|---------|---------|----------|----------|------|--------|--------|------|---------------|
| F001 | ... | | | T3 | A-1.. | Confirmed/... | | |

> 规则：论文/综述按 T3 处理；权威预印本可升 T2；每条结论须 ≥2 独立源确认才标 Confirmed。

## 4. 核心发现
### 4.1 <子主题 / 技术路线>
- **发现**：... ［Confirmed/Corroborated/Single-source/Unverified］
  - 证据：源A(T3, 日期) + 源B(T3, 日期)

## 5. 矛盾台账（显式，不掩盖）
| 争议点 | 说法A(源/层级) | 说法B(源/层级) | 裁决 | 置信 |
|--------|---------------|---------------|------|------|

## 6. 技术 / 基准对比矩阵（技术选型 / 基准类必含）
| 维度 | 方案/模型 A | 方案/模型 B | 方案/模型 C |
|------|------------|------------|------------|
| 定位 | | | |
| 核心能力 | | | |
| 局限/风险 | | | |
| 综合评级 | | | |

## 7. 引用文献（严格格式 + 可导出）
- `Authors. Title. Venue. Year. DOI/URL`（每条必带原文 DOI/URL，避免二手摘要失真）
- 支持 BibTeX / RIS / JSON 导出（源自 academic-research-hub / literature-search）

## 8. 开放问题（未能验证，需人工/后续）

## 9. 方法论与合规声明
- 学术源访问伦理：不抓禁止自动访问或需登录站点；Google Scholar 仅经用户导出。
- 去重：按引用数 + 时效性去重；本流程已有去重铁律，不重复实现。
```

---

## 五、工具分层（默认零依赖，可选工具按平台接入）

> **默认层（零安装）**：LLM 内置 `web_search` / `web_fetch` + 🆓 免费 REST API（OpenAlex 等）；主力入口，不依赖 MCP / 本地进程。
> **可选增强层（缺失则优雅跳过，非质量必需）**：Firecrawl / DeepWiki / Exa / Tavily / Brave / Perplexity / 秘塔 / AnySearch / ModelScope / SearXNG / Novada 等按平台接入；GPT Researcher 等本地进程依赖重，仅高级用户按需部署。各平台接入见 **references/cross-platform-tools.md**。
> 推荐层级：🥇 首选 · 🥈 备选 · 🥉 备选 · 🛟 兜底 · 🎯 个性化（平台专有 / 需 key）· ⚠️ 不推荐通用。

| 步骤 | 默认层（零依赖，所有平台通用） | 可选增强层（按平台接入，缺失则跳过 · 标注推荐层级） |
|------|----------------|-------------------------------|
| 搜索入口 | 内置 `web_search` / `web_fetch`（首选）+ 🆓 免费 REST API（OpenAlex 等） | Firecrawl 🥇 / DeepWiki 🥇（keyless MCP）/ Exa 🥈 / Tavily 🥈 / Brave 🥉 / Perplexity 🎯 / Novada 🥈（免费 1000/月，npx）/ SearXNG 🛟（自托管 keyless） |
| 社媒/热评 | `web_search` 通用社媒（Reddit / X / 知乎 / 微博 / 小红书等）+ WebFetch | agent-reach / agent-browser 🎯（平台特定，复用登录态抓评论）；UGC 仅作 T4 信号 |
| 专利 | WebSearch 公开库（Google Patents / USPTO / EPO / WIPO） | patsnap-search MCP 🎯（若平台已连） |
| 财经/财报 | WebSearch 公司官网 / 财报 / 财经媒体 | westock-mcp / tdx-connector MCP + markitdown 🎯（平台特定） |
| 企业工商/风险 | WebSearch 工商/司法公开信息 | tyc-mcp / qcc-company / qixinhuiyan-mcp 🎯（平台特定） |
| 法律/合规 | WebSearch 法规/裁判文书公开信息 | wk-workbuddy / yuandian-mcp / pkulaw 🎯（平台特定） |
| 代码/项目 | WebSearch + WebFetch GitHub Trending / Hugging Face | DeepWiki 🥇（keyless，仓库研究）/ github MCP + gh CLI 🥈（平台特定） |
| 学术论文(🆓免费API优先) | WebFetch/curl 直调：OpenAlex / Semantic Scholar / arXiv / PubMed / bioRxiv / EMBL-EBI·Europe PMC（免 key、可复现） | — （已是免费 API，无需增强） |
| 引文溯源 | WebFetch 直调：Crossref / OpenCitations（DOI 元数据 + 引文网络） | — |
| 科研数据仓库(🆓免费API) | WebFetch 直调：Zenodo / Figshare / 哈佛 Dataverse / NASA（均带 DOI） | — |
| 知乎(技术+反馈) | WebSearch 知乎（WebFetch 抓页） | zhihu MCP 🎯（平台特定，若已连） |
| AI 搜索(可选) | 内置 `web_search`（带引用优先） | Perplexity 🎯 / Tavily 🥈 / AnySearch 🎯 / 秘塔搜索 🎯（需 key 则跳过） |
| 微信公众账号文章 | WebSearch 公众号文章（搜索） | wechat-article-search skill 🎯（搜索发现）+ **ReadGZH-Agent MCP** 🥇（全文提取，远程 MCP 零安装，4 工具）|
| 抖音(短视频) | WebSearch 抖音（web_search 兜底） | **douyinmcp MCP** 🎯（get_homefeed 热榜 + 深度内容，免费优先）/ **TikHub API** 🎯（付费稳定备选，深度内容）|
| 宏观经济 | WebSearch（Trading Economics / FRED / 统计局 / 央行 / 财联社） | — |
| AI 模型/代码/数据集 | Hugging Face Hub API（🆓）/ ModelScope web（可选 token 直调） | ModelScope 🎯（平台特定，若已连） |
| 开放百科 | WebSearch（Wikipedia / 百度百科） | — |
| 产品/创投 | WebSearch + WebFetch（Product Hunt / TechCrunch / 36氪） | agent-reach 🎯（平台特定） |
| 开发者社区 | WebSearch（Stack Overflow / HN / Reddit / CSDN；HN 走 Algolia 端点，Firebase 2023 已停服；Reddit 2023 需 OAuth → agent-reach / web_search 兜底） | agent-reach 🎯（平台特定） |
| 知识库 | — | ima-mcp / notion / Obsidian / 本地 wiki 🎯（用户自有） |
| 云存储 / 文件 | — | baidu-netdisk MCP 🎯（平台特定） |
| 文档净化 | WebFetch 原文 + LLM 提取 | markitdown 🎯（PDF/Word→Markdown） |
| 交叉验证 | 本工作流内 LLM 比对（同一事实多源描述喂模型问"是否矛盾"） | — |
| URL 验活 | WebSearch 重新索引 / WebFetch HEAD | web-access 🎯（平台特定） |
| 长报告分块 | 输出 >4k tokens 时按板块分块生成后 LLM 拼接 | — |
> 降级原则：默认层失败 → 换另一默认源（web_search ↔ 免费 API）；可选层未连/无 key → 跳过并注明"未覆盖该维度"，绝不阻断 Step 0–8 主管线。
> **路由不打包**：dmr 主管线只做"源路由 + 优雅降级"，不复制 / 捆绑任何可选工具的实现；上表可选层均为**外部 peer skill / MCP**，由用户平台按需在 Step 1 接入，缺失则跳过并注明维度未覆盖。
> 专业数据源（宏观/工商/行情/法律）可按平台在 Step 1 接入对应可选工具；无则标注未覆盖，不编造。
> **深度研究专用工具（GPT Researcher，非通用推荐）**：GPT Researcher 提供自动化深度研究闭环，但需 `git clone` + `pip install` + 多 API key 配置，依赖重、启动慢，不符合本 skill "大多数人开箱即用"的目标。纯提示词驱动的三-B 闭环已能独立完成高质量深度研究。GPT Researcher 仅建议高级用户在独立 venv/容器中按需部署。详见 references/cross-platform-tools.md。

---

## 六、质量规则（Anti-patterns，必须避免）

1. ❌ 单源定结论 → 必须 ≥2 独立 Tier1–3 才 `Confirmed`。
2. ❌ 矛盾时随机选一个或多数暴力 → 按层级/时效/详实度裁决，否则并存标注。
3. ❌ 把用户热评当硬事实 → Tier 4 永远标"信号"，与 Tier1–3 事实分开。
4. ❌ 把推断当事实 → 严格区分 **事实/解读/推断**；推断必须标 LOW 置信并说明依赖假设。
5. ❌ 不标日期 → 每条源必须带采集/发布日期，趋势类优先近 3–6 月。
6. ❌ 重复信息堆叠 → Step 2 去重，同一信息只留最完整一版。
7. ❌ SEO/内容农场当信源 → 低信号高广告站点在 Step 2 过滤。
8. ❌ 临场换结构 → 永远套用第四节模板，保证跨次可对比、可复现。
9. ❌ 掩盖不确定性 → 无法验证的写进"开放问题"，绝不编造填坑。
10. ❌ 透镜堆砌 → 波特五力/PESTEL/BCG/TAM-SOM 等经典框架是**可选分析透镜**，按查询意图触发，绝不每篇报告强制全套；它们不替代源分级与交叉验证（见「分析透镜库」）。
11. ❌ 间接引用/数字失真 → **逐字引用铁律**（源自 material-organizer）：关键结论的摘录必须原文 `>` 引用块呈现，数字/日期/百分比与源完全一致；缺口标"信息不足"绝不猜测填充。
12. ❌ 范围蔓延 → 本流程只做**二手案头研究**；不吸一手调研方法（问卷/Van Westendorp 定价/用户访谈），超范围能力不并入（market-researcher 一手部分已明确排除）。
13. ❌ 强制新模块 → v2.1.0 的 intel-brief 输出风格、学术数据源模块、宏观监测、微信文章检索、Perplexity、模板 D，以及 v2.2.0 扩充的学术/开放科研数据源、引文溯源、科研数据仓库、工程化讨论源，均为**可选叠加**，仅在查询意图匹配时启用；绝不每篇报告硬塞全部数据源/学术引文/宏观解读/intel-brief 三元。它们不替代 Step 0→8 主管线与模板 A/B/C 的质量根基，且与各来源 Skill 的过度约束项（硬格式/专属变量/外部 CLI 依赖）保持隔离。
14. ❌ 优先抓 HTML 而非用免费 API → v2.2.0 去粗取精原则：凡有免费公开 REST API 的学术/数据源（OpenAlex/Semantic Scholar/Crossref/arXiv/PubMed/bioRxiv/OpenCitations/EMBL-EBI/Zenodo/Figshare/Dataverse/NASA/Hugging Face/Stack Exchange/HN），一律**优先经 WebFetch/curl 直调 API**（稳、可复现、可溯源），仅在无 API 或受限时才退回网页抓取/用户导出（Google Scholar/CNKI/Nature 全文）。绝不硬依赖 Proprietary 或需外部 CLI 的 skill。
15. ❌ 把「环境受限」误判为「能力不足」 → 当核心数据源（OpenAlex / Semantic Scholar / 知乎 MCP / 学术论文 🆓 API 等）因网络/区域不可达而失败时，必须**显式标注该维度"因环境受限未覆盖"**，并在「开放问题」中单列，绝不将其降格为低置信结论或编造填充；换用兜底源（web 抓取 / 其他 API / 已连 MCP）时须注明降级路径。严格区分"Skill 能力边界"与"运行环境限制"——这是输出准确性的前提，也是避免被误判为结论质量缺陷的关键。

16. ❌ 终稿不经对抗审计 / 整篇 regenerate 掩盖 / 偷换议题 → 必须跑对抗式审计（corpus critic + ≥2 类并行 critic），仅做 surgical patch，canonical query 贯穿全篇，关键结论可回溯来源树，交付前勾 lint 自检清单（见「终稿纪律」小节）。这是输出可信度的最后一道闸门，与 Step 0–8 主管线互补，不新增工具/门槛。

17. ❌ 把可选后端当必需 → hyperresearch / Tavily / Perplexity / web-access / agent-reach / agent-browser 均为**可选**增强：缺 key / 未安装 / 失败一律优雅跳过，绝不阻断 Step 0→8 主管线或报「无法完成」。主检索永远由内置 WebSearch / WebFetch + 🆓 免费 API 兜底（规则 14）。

18. ❌ 竞品关键参数单源下定论 → **定价 / 版本号 / MCP 支持 / 许可证 / 收购归属**等可量化事实，交叉验证源数由 ≥2 升 **≥3 个独立源**（普通事实维持 ≥2 控成本，避免成本爆炸）；不足 3 源须标 `Single-source` 并列入开放问题。

19. ❌ 把可选工具当质量前提 → Exa / Firecrawl / GPT Researcher / ModelScope 等可选工具**只丰富素材来源，不是质量必需**；缺失时回退默认层（内置搜索 + 免费 API），输出质量由 Step 0–8 + 三-B 闭环保证，不降档。

20. ❌ 绑定特定平台机制 → 本技能**不假设任何平台的 MCP 配置文件、agent-team 编排协议或专有后端存在**。默认走 LLM 内置 `web_search` / `web_fetch`；可选工具按 references/cross-platform-tools.md 分平台接入，缺失即优雅降级。移植到 Claude / Codex / Trae / qoder / Cursor 等平台时无需改动主管线与质量规则。

---

## 七、触发与执行约定

- 用户说"调研/分析/竞品/格局/趋势/深度调研/公司尽调/扒一下/挖一下/对位/对标"等即触发本流程。
- **行业赛道模式**：当查询含"行业趋势/赛道/产业链/投资机会/商业化落地/市场规模"时，默认采用模板 B（五大板块），并强制：利润穿透、至少 1 个反方观点、1–2 年趋势窗口、每板块 1 个非散文元素。
- **公司/竞品模式**：当查询含"公司/竞品/尽调/扒一下/挖一下/对位/对标/我们和 A/B/C"时，默认采用模板 C，并强制：四维分析、7 字段证据清单、真实负面多渠道验证、SWOT、五类情景推演。多家对位时必含横向对比矩阵。
- 默认跑完整 Step 0–8；若用户要"快版"，至少保留 Step1(采集) + Step4(交叉验证) + Step8(模板)，但必须在报告注明"快版，未全覆盖质量环"。
- **增量知识沉淀（Karpathy 模式，源自 llm-wiki）**：每次完成后，把「评分卡 + 开放问题 + 核心证据」沉淀为**结构化 markdown note**（带 YAML frontmatter：topic / players / rating / date / sources[] / confidence，便于检索与跨次复用），落点三选一或并存：**ima 知识库（首选）/ Obsidian（PARA 结构，适配本地第二大脑）/ 本地 wiki**，采用三层结构——① raw 源页（不可变，存原始 URL/摘录）② wiki 合成页（本次结论，绑定证据 ID）③ schema（统一字段：主题/玩家/评级/日期）。重跑同主题时先读历史 wiki 页，执行 **Lint 操作**扫描：矛盾论断（与旧页冲突）、过时论断（早于去年且未标 outdated）、孤儿页（源失效无新支撑）→ 在报告中显式标注"更新/推翻/维持"。避免重复采集、跨次矛盾无人管；建议维护一份**可检索索引**（按 topic 聚合 note 路径），让调研资产跨会话复利（不内建 SQLite，复用你已有 PARA / Obsidian 体系）。

## 八、常见问题（FAQ）

**Q1：这个 skill 和普通的 WebSearch / WebFetch 有什么区别？**
A：WebSearch / WebFetch 是"检索工具"，本 skill 是"调研工作流"——在检索之上叠加源分级（T1–T4）、≥2 源交叉验证、去重去旧去假去矛盾、置信标签、模板化输出与增量沉淀。单条 WebSearch 不会自动产出带置信度的可复现报告。

**Q2：核心数据源（OpenAlex / 知乎 MCP / 学术 API）连不上怎么办？**
A：按质量规则 15 处理——显式标注"该维度因环境受限未覆盖"，列入「开放问题」，绝不降级为低置信结论或编造；并换用兜底源（web 抓取 / 其他 API / 已连 MCP），注明降级路径。环境限制 ≠ 能力不足。

**Q3：什么时候用模板 B / C / D？**
A：查询含"行业 / 赛道 / 产业链 / 趋势 / 市场规模"→ 模板 B（五大板块）；含"公司 / 竞品 / 尽调 / 对位 / 对标"→ 模板 C（四维 + SWOT + 情景）；含"论文 / SOTA / 文献综述 / 技术选型"→ 模板 D（学术引文）。纯概览用模板 A。模式可叠加。

**Q4：需要付费 API key 或本地安装吗？**
A：**都不需要**。本技能默认零依赖、零安装——只用 LLM 内置 `web_search` / `web_fetch` + 🆓 免费公开 REST API（OpenAlex / Semantic Scholar / Crossref / arXiv / PubMed 等无需 key）。Exa / Firecrawl / Tavily / Perplexity / GPT Researcher / ModelScope 等是**可选增强**：有 key 且平台支持才启用，无则优雅跳过，质量不降。一份 SKILL.md 即可在 WorkBuddy / Claude / Codex / Trae / qoder / Cursor 等任意平台使用，无需改代码。各平台可选工具接入方式见 references/cross-platform-tools.md。

**Q5：源之间矛盾怎么办？**
A：不随机选、不多数暴力。按源层级（T1>T2>T3>T4）、时效（近 3–6 月优先）、详实度裁决；无法裁决则多方案并存并标注矛盾。绝不强行共识（Cat-Research 自验证闭环）。

**Q6：报告会不会太长？**
A：默认跑完整 Step 0–8；用户要"快版"时至少保留 Step1 + Step4 + Step8，并在报告注明"快版，未全覆盖质量环"。模板 B / C 强制非散文元素（矩阵 / 图表 / 清单），避免纯散文堆字。

**Q7：增量知识沉淀一定要用 ima 吗？**
A：ima-mcp 是首选，notion / Obsidian / 本地 wiki / 任意知识库均可；关键是三层结构（raw / wiki / schema）+ 重跑 Lint。不强制。

**Q8：中文 / CJK 源（公众号、知乎、小红书、CNKI 等）能正常处理吗？**
A：能，且是 dmr 的差异化优势。dmr 原生支持中文源采集与中文报告输出；对比竞品 hyperresearch 的已知缺陷（issue #37：其 `looks_like_junk()` 把**所有中文 / CJK 页面当 junk 直接丢弃**），dmr 明确保留中文页并视为一等信源（T3 / T4 按属性分级）。中文市场 / 竞品调研请放心使用，无需 workaround。

---

## 九、完整示例（端到端：从用户提问到报告）

以下以一个真实查询演示 Step 0→8 如何落地。**加粗 = Agent 动作**，**引用块 = 产出物**。

**用户**：「帮我调研一下中国工业机器人赛道，重点看减速器国产化机会，以及和埃斯顿、汇川怎么对标。」

**Step 0 — 意图解析与模式选择**

> 模式：行业赛道（模板 B）+ 公司 / 竞品（模板 C 叠加）。
> 关键实体：工业机器人、减速器（RV / 谐波）、埃斯顿、汇川技术。
> 输出要求：五大板块 + 四维对位矩阵 + SWOT + 情景推演。

**Step 1 — 采集（多源并行）**

- 🆓 API 直调：OpenAlex（`industrial robot China`）、Semantic Scholar（RV reducer）、Crossref（国产替代文献）。
- 🌐 联网：WebSearch「工业机器人 减速器 国产化 2025」、WebFetch 埃斯顿 / 汇川年报摘要。
- 用到的 MCP：zhihu（「国产 RV 减速器 体验」）、wechat-article-search（行业深度文）、patsnap-search（减速器专利）。
- 兜底：agent-reach（小红书 / 脉脉 工程师口碑）。

**Step 2 — 去重 / 去旧 / 过滤**

> 合并 3 篇重复的「谐波减速器市场」报道，仅留最完整版；剔除 2021 年前且无更新的旧文；过滤 2 个广告型内容农场。

**Step 3 — 事实单元拆解**

> 单元样例：「2024 中国工业机器人密度 470 台 / 万人（IFR）」「RV 减速器国产化率 < 30%（纳博特斯克垄断）」「埃斯顿 2024 营收 ≈ 45 亿（年报）」。

**Step 4 — ≥2 源交叉验证**

> 「RV 国产化率 < 30%」：Crossref 论文 + 年报 + 行业研报 三源 → `Confirmed`。
> 「谐波减速器价格年降 8%」：仅 1 源 → 标 `Unconfirmed`，列入开放问题。

**Step 5 — 矛盾消解**

> 两家机构对「2025 市场增速」给出 12% vs 18%：按时效（近 6 月研报优先）+ 方法论标注并存，不强行平均。

**Step 6 — 分级与置信标注**

> 每条结论带 `Tier + 置信`：如「减速器是国产替代核心卡点」T2 `Confirmed`；「某创业公司份额跃升」T4 信号（小红书口碑），与事实分离。

**Step 7 — 模板渲染（B + C 叠加）**

> 五大板块：① 赛道定义与市场规模（470 台 / 万人密度 + TAM 测算）② 产业链图谱（上游 RV / 谐波 → 中游本体 → 下游集成）③ 驱动力与痛点（国产化政策 + 卡脖子）④ 1–2 年趋势（人形机器人拉动谐波需求）⑤ 商业化建议（避开纳博正面战，切谐波 / 售后）。
> 对位矩阵：埃斯顿 vs 汇川（营收 / 产品 / 渠道 / SWOT）。
> 情景推演：乐观（政策加码）/ 基准 / 悲观（需求疲软）/ 技术突变 / 监管。

**Step 8 — 评分卡 + 开放问题 + 沉淀**

> 评分卡：证据强度 A-，覆盖度 B+，矛盾 1 处已标注。
> 开放问题：谐波价格年降幅度待第二源；RV 国产化率最新季度数据受限（环境受限未覆盖，已注明降级路径）。
> 沉淀：回写 ima 知识库三层结构，Lint 标记本次为「基线版」。

**最终交付**：带置信标签、含对位矩阵与情景推演的 Markdown 报告 + 评分卡。

---

## 附录 A：完整更新史（v2.0.0 → v2.3.2）

- **v2.0.0**：竞争对位实测，验证 Step 0–8 主管线与源分级框架；确立 NATO Admiralty 4 级源分级与 ≥2 源交叉验证硬规则。
- **v2.1.0**：吸收 9 个互补研究类 skill 的方法论（去其过度约束项，叠加不替换）；新增 intel-brief 输出风格（事实→影响→原因 + [矛盾] / [待核实] / [已证伪]）、宏观监测源、微信公众号文章检索、Perplexity AI 搜索、第 4 套学术 / 基准 / 技术选型 / 尽调模板 D。
- **v2.2.0**：去粗取精、优先免费 API。大幅扩充学术与开放科研数据源（OpenAlex / Semantic Scholar / Crossref / arXiv / PubMed / bioRxiv / OpenCitations / EMBL-EBI / Zenodo / Figshare / Harvard Dataverse / NASA），工程化讨论源（Stack Overflow / HN / Reddit / 知乎 / CSDN / Product Hunt / TechCrunch / Bluesky / X），代码与模型平台（GitHub Trending / Hugging Face / 魔塔 ModelScope）；区分「🆓 免费 API 直调」与「🌐 通用联网可达」。
- **v2.2.1**：技能去粗取精执行。GitHub MCP 集成（mcp__github__* 可用）；永久删除 6 个重复冗余且已被吸收的 skill（google-scholar-search / academic-research-hub / deep-research / news-summary / perplexity / tavily，不可逆），其方法论并入主管线。
- **v2.2.2**：文档准确性修正——将 6 个 skill 由「归档(可恢复)」更正为「永久删除(不可逆)」，消除与 v2.2.1 主题的残留矛盾。
- **v2.2.3**：文档一致性修正——消除 SKILL.md 兼容性块英文 stale 措辞 `(archived, recoverable)` → `(permanently removed, irreversible)`；本地 skill / 仓库 / 发布包三端统一为 v2.2.3，无隐私泄露。
- **v2.2.4**：规范性增强（回应 SkillHub TRACE 测评 Convention 4.3 短板）。新增**常见问题 FAQ**、**完整端到端示例（Step 0→8 落地）**、**本附录 A（完整更新史）**；补充质量规则 15「环境受限≠能力不足」（核心源不可达时显式标注未覆盖，不降级为低置信结论）；并将 〇 节的冗长更新史压缩为摘要 + 附录指针，降低文档密度。本地 / 仓库 / 发布包三端统一为 v2.2.4。
- **v2.2.5**：方法论 sharpening（仅措辞显式化，零新工具 / 零新硬门槛，回应 anysearch 方法论对齐审计）。Step 2 去重补「**信息密度优先**」选择准则 + 「**同源多样性权重（同源衰减）**」防单域霸屏；Step 2 新增「**语义相关度 × 时效 × 源层级 三轴混合**」排序准则（与 Step 5 冲突裁决轴互补）。不替 WebSearch、不动 Step 0→8 主管线、不接 anysearch 工具、不新设数值门槛；anysearch 厂商自称 76.4% 准确率 / 快 31% 属 [VENDOR CLAIM]，不写进 dmr 质量声明。本地 / 仓库 / 发布包三端统一为 v2.2.5。
- **v2.2.6**：对抗式审计纪律（吸收 hyperresearch 方法论，纯提示词零依赖）。新增「终稿纪律」小节——① 对抗式审计(corpus critic + ≥2 类并行 critic：事实一致性/源层级一致性/时效/反向观点遗漏) ② patch-never-regenerate（终稿只 surgical edit）③ canonical query gospel（用户原话贯穿）④ provenance 来源树 ⑤ 输出前 lint 自检清单(6 项)；Step 7 质量环补对抗审计线；新增质量规则 16。不替 WebSearch、不动 Step 0→8 主管线、不新增工具/数值门槛、不降搜索/输出质量。本地 / 仓库 / 发布包三端统一为 v2.2.6。
- **v2.2.7**：P1 集成 + 去粗取精（吸收 hyperresearch，集成 > 自造）。① 增量沉淀升级为**结构化 markdown note**（YAML frontmatter + 可检索索引），显式对接 ima / Obsidian(PARA) / 本地 wiki（不内建 SQLite）；② hyperresearch 注册为**可选深度抓取后端**（Claude Code 环境，key-gated，失败跳过不阻断主管线，镜像 Tavily 处理）+ 质量规则 17；③ Step 1 加**意图路由 hint（thin router 思想）**——按查询意图选源、catalog 保留为可选菜单不删，去粗取精不降搜索质量；④ FAQ Q8 文档化**中文/CJK 优势**（对比 hyperresearch #37 CJK junk bug，明确不吸收）。本地 / 仓库 / 发布包三端统一为 v2.2.7。
- **v2.2.8**：README 特性区重构（倒序排列 + 中英双语切换 + 去冗精炼）。按「最新在前」重排 v2.2.7→4 四段版本演进；新增折叠式 **English Version**；将原有 20+ 条冗长特性清单压缩为「版本演进 / 独有优势 / 输出能力」三层，突出与通用 AI 搜索 / 深度研究 skill 的差异化（确定性流水线、源分级置信、≥2 源交叉验证、终稿对抗审计、中文/CJK 原生、零安装、可选后端不阻断）。本地 / 仓库 / 发布包三端统一为 v2.2.8。
- **v2.2.9**：全仓库审计与修正。① Qoder 拼写修正（Qodo→Qoder，阿里云产品，技能目录 `~/.qoder/skills/`；同步 install.sh/install.ps1/CONTRIBUTING）；② 去除「已连/已连未启用」等个人环境连接状态注释（README 诚实声明 + SKILL.md 源表/Connected MCPs/FAQ），仅声明连接器类型不暴露隐私；③ AgentKey 重归类为**搜索入口聚合兜底**（不单独列维度，可替代缺失的专业 MCP）；④ 云存储新增 **Google Drive（海外用户可选）**；⑤ README 拆为**中英双文档**（README.md 中文 + README_EN.md 英文 + 顶部语言切换）。本地 / 仓库 / 发布包三端统一为 v2.2.9。
- **v2.2.10**：可选搜索后端附录补强（源自《Agent搜索工具调研报告》审计，纯目录引用、零新硬依赖）。在「工具映射」表 AI 搜索(可选) 行 + frontmatter Search entry 增列 **AnySearch**（前置去重 + RRF，厂商自称 76.4% 标 [VENDOR CLAIM] 不写进质量声明）、**秘塔搜索**（国内 AI 搜索，含事实检验，按次计费，需 key）为 CN 场景可选增强；均标注「可选 / 需 Key / 非默认 / 无 key 优雅跳过」，不替 WebSearch、不动 Step 0→8 主管线、不接专有后端、不降搜索质量。本地 / 仓库 / 发布包三端统一为 v2.2.10。
- **v2.3.0**：平台无关 + 深度研究闭环（去粗取精、泛化优先）。① **平台无关化**：默认零依赖零安装（仅 LLM 内置 `web_search` / `web_fetch` + 🆓 免费公开 REST API，如 OpenAlex / Semantic Scholar / Crossref / arXiv / PubMed 等免 key 直调），不假设任何平台 MCP 配置文件 / agent-team 编排协议 / 专有后端；可选工具（Exa / Firecrawl / Tavily / Perplexity / GPT Researcher / ModelScope 等）按平台接入、缺失即优雅降级。② **新增「三-B 深度研究闭环（平台无关，纯提示词编排）」**：吸收多平台深度研究 agent 团队精华（多轮迭代 / 章节级审稿 / 研究参数卡跨阶段共享 / 进度通报），去其平台专有约束，做成任意 agent 可复现的纯提示词闭环。③ **竞品关键参数交叉验证 ≥2 → ≥3**（质量规则 18，普通事实维持 ≥2 控成本）。④ **质量规则增 19（可选工具非质量前提）/ 20（不绑定特定平台机制）**。⑤ **新增 references/cross-platform-tools.md**（WorkBuddy / Claude / Codex / Trae / qoder / Cursor 六平台可选工具接入指南）。⑥ **隐私修正**：云端 SKILL.md 移除个人 MCP 连接状态声明（GitHub / ModelScope / 知乎等的"已连"表述、个人 token 等个人状态），云端仅声明连接器类型、缺失即优雅降级，个人连接状态仅留本地 skill；本地 / 仓库 / 发布包三端统一为 v2.3.0。
- **v2.3.1**：MCP 鉴权前缀修复 + 跨机器同步 + 可选源增补（维护性小版本，主管线零变动）。① **MCP 鉴权前缀 BUG 修复（全局）**：原 mcp.json 的 env 类 server 带 `APIKEY:` / `access token：` 前缀 → 上游 API 全 401 拒；修正为裸 token 后 Exa / Firecrawl / HF / ModelScope / Tavily 全部 HTTP 200。② **Tavily MCP** 从 mcp-remote（强制浏览器 OAuth）改用官方 `tavily-mcp` stdio 包 → 无头免 OAuth。③ **Zhihu MCP 端点** 从 `/mcp/.../sse` 纠正为 `/api/mcp/.../v1/sse` 并强制 `--transport sse-only`，3 端点（搜索/可信全网/热榜）实测 initialize + tools/list + tools/call 全部返回真实知乎数据。④ **跨机器同步 `scripts/setup_mcp.py`**：零硬编码 key、自动剥前缀（Rule 1）、生成 mcp.json + dmr_keys.env。⑤ **新增可选源**：FRED（结构化经济数据，✅ 吸收）/ Novada（兜底解锁层，✅）/ Connected Papers（深度尽调可选源，✅）/ agent-reach（实测 6 社媒+5 基础 社媒增强层，✅ 已激活；**抖音/微博 走 web_search 兜底，公众号走 wechat-article-search skill**）/ agent-browser（⚠️ 仅交互兜底）/ AnySearch（❌ 不吸收，重叠）；⑥ **midu-hotsearch 弃用**（新版 midu.com 改 OAuth + 付费墙，原 `MIDU_APP_SECRET` 失效，错误码 202005/203003，不进 README 终态清单）；⑦ **新增 wallstreetcn 免费财经热榜**（免 key，替代蜜度热榜）；⑧ **新增 `scripts/fred_query.py`**；⑨ **新增 SEC EDGAR MCP**（美股官方申报/财报 XBRL/内幕交易 Form 4，免 API key 仅需 `SEC_EDGAR_USER_AGENT`；`stefanoamorelli/sec-edgar-mcp` 经 uvx 运行，补 dmr 美股结构化申报空白，归 🟡 需连 MCP）；⑩ **学术/社区源文档精度修正**（无功能变动，仅文档准确性）：Semantic Scholar 补"无 key 限 ~100 req/5min·IP，免费 key 提额"、literature-search 注明"非可调用 API"、Hugging Face 补"gated 模型需登录+接受 EULA 才能下载"、Hacker News 注明"Algolia 端点（Firebase 2023 已停服）"、Reddit 注明"2023 起需 OAuth 走 agent-reach/web_search 兜底"，并标注 HN 部分出口 IP 被 Algolia WAF 屏蔽时回退 web_search。本地 / 仓库 / 发布包三端统一为 v2.3.1。
- **v2.3.2**：P0 密钥卫生 + 健壮性修复 + 依赖清理（维护性补丁，主管线零变动）。① 密钥卫生：`.gitignore` 忽略 `dmr_keys.env`/`mcp.json`/`*.env`，`setup_mcp.py` 写后 `chmod 600` + 仓库内告警守卫；② `fred_query.py` 前缀正则对齐 `setup_mcp.py`、`load_key()` env 剥前缀、observations URL 编码；③ 源健康监控原型 + 首个真实测试（8 测全过）；④ 移除失效的 SEC EDGAR MCP 生成块（上游 404，美股结构化维度回退 `web_search`）。本地 / 仓库 / 发布包三端统一为 v2.3.2。
