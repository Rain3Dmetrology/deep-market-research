# 可选模块、分析透镜与 Skill 方法论吸收

> 所有模块均为**可选叠加**，仅在查询意图匹配时启用。
> 绝不每篇报告硬塞全部数据源/学术引文/宏观解读/intel-brief 三元。
> 它们不替代 Step 0->8 主管线与模板 A/B/C 的质量根基。

---

## 1. 互补 Skill 方法论吸收 (v2.1.0)

对 9 个已安装、与本研究域重叠的研究类 skill 做了审计，择优吸收其方法论，**明确拒绝**各自的过度约束项。吸收均为**叠加**，不替换本流程主管线/主模板。

| 来源 Skill | 吸收的方法论 | 明确拒绝（防过度约束） |
|---|---|---|
| **intel-osint-daily** | 信息项"事实->影响->原因"三元（可作 intel-brief 输出风格）；"三方交叉验证"命名强化；`[矛盾]/[待核实]/[已证伪]` 标记（对齐本流程去重/去伪规则）；连续监测思路 | 其 `<=1450字 JSON、禁 Markdown/emoji` 硬格式；TrendRadar 专属变量 |
| **macro-monitor** | 宏观数据源清单（Trading Economics/FRED/国家统计局/央行/证监会/财联社/华尔街见闻）作可选"宏观监测"源；"每指标配白话解读 + 超预期/不及预期 vs 预期/前值"规则 | 其 `browser`/OpenClawCLI 路径在本环境不存在->改走 web-access |
| **news-summary**（v2.2.1 已永久删除，方法论已吸收）| RSS 源（BBC/Reuters/Al Jazeera/NPR）并入可选数据源 | 语音播报（超范围） |
| **deep-research**（v2.2.1 已永久删除，方法论已吸收）| 命令式入口（`/research`->outline->`/research-deep`并行->`/research-report`）；outline + 并行 per-item 搜索模式；学术/基准/技术选型/尽调模式->第 4 模板 | 不替换确定性 Step0->8 + 三级模板 |
| **agent-reach** | 补齐 UGC 平台覆盖（实测 6 社媒：X/Reddit/Facebook/Instagram/B站/小红书 + 5 基础：GitHub/V2EX/RSS/Web/YouTube + 3 可选：小宇宙/雪球/LinkedIn；**抖音/微博 走 web_search 兜底，公众号走 wechat-article-search skill，非 agent-reach 频道**） | 不引入其安装/代理复杂度；dmr 仅引用 |
| **wechat-article-search** | 新增"公众号**文章**检索"为具体中文信号源（补 UGC 评论之外的文章级缺口） | 不复制其 node 依赖规则 |
| **perplexity**（v2.2.1 已永久删除，方法论已吸收）| 注册为可选 AI 搜索源（仅当 `PERPLEXITY_API_KEY` 存在） | 不作强制入口，仍以 Tavily/WebSearch 为主 |
| **academic-research-hub**（v2.2.1 已永久删除，方法论已吸收）| 多源学术检索（arXiv/PubMed/Semantic Scholar/Google Scholar）+ 引文处理（BibTeX/RIS/JSON）作学术模块 | 其 OpenClawCLI 硬依赖；**许可 Proprietary**--嵌入脚本前须确认再分发权 |
| **literature-search** | 范围澄清步骤；学术源访问伦理；按引用数+时效去重；严格 `作者.题名.出处.年.DOI/URL` 引文格式 | 不重复实现去重（本流程已有） |

> 学术三件套 overlap 提示：`academic-research-hub` + `literature-search` + `google-scholar-search` 同覆盖学术细分；吸收前两者后第三者冗余。v2.2.1 已将 `academic-research-hub` 与 `google-scholar-search` 一并永久删除，仅留 `literature-search` 作方法论参考。

---

## 2. 学术与开放科研数据源模块（v2.2.0 大幅扩充）

当用户查询含"论文/SOTA/技术基准/学术/引用/文献/科研数据/开源模型"时，可启用学术检索分支。**核心原则（去粗取精）**：多数权威学术源都有**免费公开 REST API**，可经 WebFetch/curl **直调**--比抓 HTML 或依赖 Proprietary/需外部 CLI 的 skill 更稳、更可复现。

### A. 学术论文 / 元数据 / 引文溯源（免费 API 优先，均免 key）

| 源 | 入口 | 定位 | 层级 |
|----|------|------|------|
| **OpenAlex** | `api.openalex.org/works?search=` | 2.5 亿+ 论文/作者/机构元数据（MAG 继任者），学术元数据主库 | T3 |
| **Semantic Scholar** | `api.semanticscholar.org/graph/v1/paper/search` | 引用网络 + TLDR 摘要 + 影响力字段（**无 key 限 ~100 req/5min/IP，可申请免费 key 提额**） | T3 |
| **Crossref** | `api.crossref.org/works?query=` | 权威 DOI 元数据 + 参考文献 -> **引文溯源**主库 | T2-T3 |
| **OpenCitations** | `opencitations.net/index/api/v1` | 开放引文网络（被引/引用关系）-> **引文溯源**补充 | T3 |
| **arXiv** | `export.arxiv.org/api/query?search_query=` | 预印本（CS/物理/数学/AI），Atom API | T3（权威预印本可升 T2） |
| **PubMed** | `eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed` | 生物医学文献库（E-utilities） | T3 |
| **bioRxiv / medRxiv** | `api.biorxiv.org/details/biorxiv/` | 生物/医学预印本 | T3 |
| **EMBL-EBI / Europe PMC** | `ebi.ac.uk` + `ebi.ac.uk/europepmc/webservices/rest/search` | 生物信息查询 + 生命科学文献 | T3 |
| **Nature / Science 等期刊** | 官网 / DOI | 顶刊一手（摘要公开，全文多需订阅） | **T1-T2**，引 DOI |
| **知网 CNKI** | 官网检索 | 中文核心文献（多需订阅） | T3 |
| **Google Scholar** | 无官方 API | **仅用户导出**使用（访问伦理，不自动抓取） | T3 线索 |

### B. 科研数据 / 成果仓库（免费 API，均带 DOI，可溯源）

| 源 | 入口 | 定位 |
|----|------|------|
| **Zenodo** | `zenodo.org/api/records?q=` | CERN 综合科研数据/软件/成果（DOI-minted） |
| **Figshare** | `api.figshare.com/v2/articles?search_for=` | 学术成果/图表/数据集 |
| **Harvard Dataverse** | `dataverse.harvard.edu/api/search?q=` | 哈佛多学科研究数据源 |
| **NASA** | `api.nasa.gov` + `data.nasa.gov` | 航天/地球公共数据（DEMO_KEY 免费） |

### C. 专利 / 代码 / AI 模型

| 源 | 入口 | 状态 |
|----|------|------|
| **智慧芽 PatSnap** | `patsnap-search` MCP | 可选（专利检索/家族/引用分析） |
| **Google Patents / USPTO / EPO / WIPO** | 公开检索 | 通用联网可达 |
| **GitHub 搜索 + Trending** | `github` MCP + `gh` CLI（已认证）+ web | 开源实现/技术栈/Star/PR 趋势 |
| **Hugging Face** | `huggingface.co/mcp`（可选 MCP）| 可选（模型/数据集/Spaces/Papers） |
| **魔塔 ModelScope** | `modelscope` MCP（可选）| 可选（模型/数据集/论文） |

### 学术模块规则

- **范围澄清（先问后搜，源自 literature-search）**：主题、子领域、综述 vs 奠基性、时间范围。
- **访问伦理**：不抓禁止自动访问或需登录的站点；Google Scholar 仅经用户导出；订阅库仅当用户提供 key/账号时启用，否则标"未覆盖"。
- **去重 / 分级**：按引用数 + 时效性去重，重复时保留期刊/会议正式版优先于预印本；论文/综述按 T3 处理（权威预印本可升 T2）。
- **引文格式（严格）**：`Authors. Title. Venue. Year. DOI/URL`；支持 BibTeX / RIS / JSON 导出；优先保留原文 DOI/URL。

---

## 3. intel-brief 输出风格（源自 intel-osint-daily，可选）

对"每日/每周监测"或"决策快报"类查询，可在模板 A 基础上叠加 intel-brief 风格--每条信息按三元素组织：

- **事实（Fact）**：发生了什么（带源层级 + 日期）。
- **影响（Impact）**：对决策者意味着什么（业务/投资/技术）。
- **原因（Cause / Why）**：为何发生（驱动因素/背景）。

并显式标注矛盾/待核实/已证伪：`[矛盾]`（与既有结论冲突）、`[待核实]`（单源待补）、`[已证伪]`（被 >=2 权威源推翻，已从结论剔除）。

---

## 4. 宏观监测源（源自 macro-monitor，可选）

当用户查询含"宏观/利率/通胀/GDP/政策/大宗"时，可接入宏观数据源（均通用联网可达，T3）：Trading Economics、FRED、国家统计局、央行/证监会官网、财联社、华尔街见闻。每条宏观指标须附**白话解读**与**超预期/不及预期判断**（对比一致预期值与前值）。

---

## 5. 微信公众账号文章检索（源自 wechat-article-search）

中文 AI/科技/商业信号常首发于公众号文章。经 `wechat-article-search` skill 检索公众号文章，作为中文一手深度内容源（T3，视媒体属性）；与既有 UGC 评论（T4）互补，填补"文章级"缺口。

---

## 6. Perplexity AI 搜索（可选源）

当 `PERPLEXITY_API_KEY` 存在时，可将 Perplexity 作为带引用的 AI 搜索入口之一，与 Tavily/WebSearch 并列（不强制、不作唯一入口）。无 key 时优雅跳过。

---

## 7. 分析透镜库（可选，按查询意图触发，非强制全套）

经典咨询框架是**分析透镜**而非研究管线。它们帮 AI 在「已验证的数据」上做更深入的结构化思考，但**不替代**本流程的采集/分级/交叉验证/去伪。仅当查询意图匹配时才调用，**禁止每篇报告硬塞 12 个框架**。

| 透镜 | 类型 | 触发场景 | 映射到模式 | 用途 |
|------|------|----------|-----------|------|
| **波特五力** | 行业结构 | 行业/赛道竞争强度分析 | 模板 B 3.2 | 供应商/买方议价、新进入者/替代品/同行竞争强度 |
| **PESTEL** | 宏观环境 | 行业大势、政策/技术驱动 | 模板 B 3.1/3.3 | 政治/经济/社会/技术/环境/法律六维扫描 |
| **价值链 (Value Chain)** | 利润结构 | 利润穿透、成本卡点 | 模板 B 3.2（利润穿透底座） | 研发->生产->营销->售后各环节价值/成本归属 |
| **BCG 矩阵** | 产品组合 | 多产品线公司评估 | 模板 C 3.1 | 明星/金牛/问号/瘦狗，资源配置判断 |
| **3C 战略三角** | 竞争定位 | 竞品对位、差异化 | 模板 C 3.2/6 | Company/Customer/Competitor 三角均衡 |
| **STP / 4P / AARRR** | 增长/营销 | 研究目标含"上市/增长/GTM" | 模板 C 3.3（可选） | 细分定位 / 营销组合 / 用户生命周期增长 |
| **MECE / 金字塔原理** | 思维原则 | 已内嵌 | 全模板 | 拆解无遗漏(MECE)、结论先行(金字塔)--无需显式调用 |
| **TAM/SAM/SOM** | 市场测算 | 市场规模/总量评估 | 模板 B 3.1 | top-down x bottom-up 交叉验证，差异>3x 重审（源自 market-researcher） |
| **竞品 4 类法** | 竞争分类 | 竞品格局梳理 | 模板 B 3.2 / 模板 C 6 | 直接/间接/替代/潜在竞争者分类（源自 market-researcher） |
| **2D 定位图** | 战略定位 | 差异化定位可视化 | 模板 C 6 | 二维矩阵呈现公司/竞品生态位（源自 market-researcher） |
| **销售门槛与准入** | 销售策略 | 研究目标含"销售/渠道/准入" | 模板 B 3.5 | 客户切换成本、认证/资质/标杆案例壁垒、渠道锁定 |
| **GTM 与渠道打法** | 销售策略 | 研究目标含"GTM/获客/转化" | 模板 B 3.5 | 客群分层、获客路径、销售周期与转化漏斗 |
| **定价与毛利结构** | 销售策略 | 研究目标含"定价/毛利/盈利" | 模板 B 3.5 | 定价模式（一次性/订阅/消耗制）、毛利率区间、价格带 |
| **商业模式可持续性** | 销售策略 | 研究目标含"商业模式/LTV/CAC/生意模式" | 模板 B 3.5 | LTV/CAC 逻辑、复购/续费/耗材绑定、现金流特征 |

> 规则：透镜是「分析深度」的加分项，不是「研究质量」的必需项。本流程的质量由源分级+交叉验证保证，透镜只在用户要"战略/竞争/增长/市场测算/销售"视角时附加。market-researcher 的一手调研方法（问卷/Van Westendorp 定价）**不吸收**--本流程定位二手案头研究。

---

## 8. 销售调研问题库（种子 4 问）

模板 B §3.5「销售与商业化分析」的问题种子（用户原始规划沉淀）。按查询意图触发，不强制每篇全问：

1. **国内外销售的核心门槛与发展前景**？——准入资质、标杆案例壁垒、渠道锁定、客户切换成本。
2. **商业模式是否可持续、是否好生意**？——LTV/CAC 逻辑、复购/续费/耗材绑定、现金流特征。
3. **投资角度看赛道企业的建议**？——梯队分层、估值锚、风险对冲、退出路径。
4. **创业角度看差异化竞争与销售策略**？——客群切口、定价带选择、获客路径、避开正面战。

> 全部问题用**既有源**即可回答（官网/财报/招股书/研报/访谈/真实用户反馈）——零新数据源纪律，不新增任何 MCP/连接器/API 依赖（自有销售数据侧的分析属 L3 数据子流，待用户提供数据后另行立项）。
