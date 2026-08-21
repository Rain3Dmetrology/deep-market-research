# Changelog

## [2.6.1] - 2026-08-22

README 门面同步 + README 漂移 CI 守卫（v2.4.0 起累积的门面漂移修复，内核零变化）。

### Fixed
- 中英 README 特性清单同步至实际能力：补 plan-first 验收先行 / 程序化机检门禁 / 研究参数卡 / 季度基准自测；「三套模板」改正为五套（A–E，含销售与商业化分析与监测增量）。
- 中英 README FAQ 与端到端示例死链修复：由不存在的「SKILL.md 第八/九节」改指 references/faq.md（8 问）与 references/example.md。
- 中英 README 目录结构同步：移除已删的 release_body.md，补 benchmarks/ / tests/ / sources.registry.yaml 与 scripts 实际内容。
- 更新史行 v2.0.0 → v2.6.1；特性标题去除版本标签（防再漂移）。

### Added
- `scripts/readme_drift_check.py`：README 漂移守卫（零依赖、6 条检查：行数预算 / 模板数声明 / FAQ 指向 / 更新史对齐 CHANGELOG 顶行 / 已删文件禁列 / 版本化标题禁用），接入 test.yml CI。

## [2.6.0] - 2026-08-22

P1 批（全局最优 spec v1.2 · S1 + S5）：plan-first 验收先行 + 模板 B 销售与商业化分析（市场侧，零新数据源）。

### Added
- **S1 · plan-first 验收先行（内嵌终止条件）**：
  - SKILL.md 工作流全景图 Step 0 框新增「产出」行：验收标准（可验证目标，每条含度量锚点）＋ 终止条件（达标即停 / 预算耗尽即停 / 最多 N 轮）。
  - §三-B 新增「验收先行与终止条件」节：终止条件三态枚举**复用既有语义不新增循环**（达标即停 / 预算耗尽即停 / 最多 N 轮即停=复用「最多 3 轮第 3 轮强制通过」）；验收标准随参数卡整卡传递，终稿对抗审计与 lint 自检逐条对照。
  - `references/parameter-card-schema.md` 推荐字段新增 **`验收标准`**（字符串列表，每条含度量锚点；R0–R6 校验不变，含该字段卡片照常 PASS——三处字段口径一致，schema 为唯一权威）。
- **S5 · 模板 B 销售与商业化分析（市场侧二级研究，零新数据源）**：
  - `references/templates.md` 模板 B 新增 **§3.5 销售与商业化分析**（原「商业化落地建议与避坑指南」顺延为 §3.6）：销售规模与渠道结构 / 定价与毛利 / 销售门槛与准入 / GTM 打法 / 商业模式可持续性——5 小节各 >=1 非散文元素，数据全部来自既有源。
  - `references/optional-modules.md` §7 透镜库新增 4 行销售透镜（销售门槛与准入 / GTM 与渠道打法 / 定价与毛利结构 / 商业模式可持续性，均映射模板 B 3.5）；新增 §8「销售调研问题库」种子 4 问（国内外销售门槛与前景 / 商业模式可持续性 / 投资视角建议 / 创业视角差异化与销售策略）。
  - SKILL.md 模式选择（§〇/§四）与 §七 触发约定新增**销售模式**：查询含"销售/商业化/GTM/渠道/定价/生意模式"-> 模板 B 必含 §3.5。
  - `benchmarks/industrial-vision-baseline.md` 新增 **Q6 销售路由回归题**（不计入 5 题均分，保历史基线可比；分数演化表增「Q6 路由」列）。

### Discipline
- 零新数据源纪律：S5 全部内容来自既有源（官网/财报/招股书/研报/访谈），sources.registry.yaml 与连接器清单零变化。
- 不新增循环纪律（R3 红线）：终止条件三态全部复用既有语义，未新增任何无终止条件的验收循环。

## [2.5.0] - 2026-08-19

程序化可信度门禁（A/B 落地）+ 研究参数卡单一权威 schema。

### Added
- **报告机检门禁 `scripts/validate_report.py`**：零依赖（仅标准库）、离线安全（死链检查默认关闭）、不阻断 Step 0->8 主管线；校验 6 条 lint（R0 章节骨架 / R1 来源出处 / R2 `Confirmed` 须 ≥2 个 T1-3 独立源 / R3 矛盾台账 / R4 推断标注 LOW / R5 开放问题标注环境受限）——输出 PASS/FAIL + 覆盖率，退出码 0/1 供 CI 或 Phase N 拦截；支持 `--template` / `--strict` / `--json`。
- **研究参数卡 schema 校验 `scripts/validate_param_card.py`**：零依赖、离线安全；自定义 YAML 子集解析器（刻意不引入 pyyaml，守住平台无关/零依赖护城河）；校验必含字段（课题/范围/实体清单/已收集来源池）、范围子字段、来源池层级∈T1-T4、日期格式 `YYYY|YYYY-MM|YYYY-MM-DD`。
- **研究参数卡结构化 schema `references/parameter-card-schema.md`**：作为《研究参数卡》字段定义的**唯一权威**（调研分析专家团队《研究参数卡》、research-orchestrator `run-manifest.json` 参数卡快照 均引用此 schema，杜绝三重字段定义漂移）。

### Changed
- **§三-B 研究参数卡**：原 8 字段散文表替换为指向 `references/parameter-card-schema.md` 的单一权威指针；必含 `课题` / `范围` / `实体清单` / **`已收集来源池`**（强制，跨阶段复用唯一证据入口），推荐 `决策用途` / `模板` / `状态` / `语言` / `查询类型`。
- **§终稿纪律**：追加第 0 条——可选程序化机检门禁（validate_report.py），交付前启发式前置拦截，不替代人工对抗审计，绝不阻断主管线。

### Discipline
- 严守平台无关/零依赖护城河：两个校验脚本仅用标准库，自定义 YAML 子集解析，不引入 pyyaml 等第三方依赖。
- 单一权威纪律：参数卡字段只在一处（parameter-card-schema.md）定义，团队与编排器仅引用、不复写。

## [2.4.0] - 2026-08-19

审计跟进（dmr-RAT 2026 audit C8 / D3 / D4）：监测场景模板化、知识沉淀强制化、质量回归可测量。

### Added
- **模板 E（监测增量版）**：周报/月报/持续监测/增量更新场景专用——对账基准 + 变化项明细（新增/更新/降级/移除）+ 新证据 + 置信迁移 + 开放问题演进；强制纪律：只报 delta、禁止全量重写、无变化显式声明不注水；无上期快照时不适用（先走 A-D 建基线）。
- **§七 监测增量模式触发**：含"周报/月报/持续监测/盯/增量更新"且存在上期快照 -> 模板 E。
- **季度基准自测**：`benchmarks/industrial-vision-baseline.md` 5 题固定基准集（工业视觉域：行业格局/竞品参数/技术趋势/负面挖掘/监测增量），100 分制评分卡 + 分数演化记录表，季度或大版本变更时执行——质量回归从"不可见"变为"可测量"。

### Changed
- **知识沉淀升级为强制实体级证据缓存**（D3）：沉淀 note 必含实体级证据缓存表（实体|字段|值|源URL|层级|日期|置信）；重跑同主题**必须先读历史 note**（消费缓存、避免重复拉取），跳过预读直接全网重采视为违反预算纪律——从软性建议升级为硬性规则，跨会话复利有据可依。

### Changed (CI)
- workflows 升级 actions/checkout@v5 + actions/setup-python@v6（消除 Node 20 弃用警告）。

### Fixed
- install.ps1 仓库文件此前为 base64 文本而非可执行源码——重写为 PowerShell 源码；安装清单补 `benchmarks/`（否则 D4 基准集不会被安装）；安装目标补 `.trae-cn\skills`（TRAE 中文版平台）；安装时打印源版本号便于核验。

## [2.3.4] - 2026-08-03

### Added
- 质量规则 21：源独立性判定 3 条规则（引用链去重 / 通讯社转载去重 / 企业自述区分）
- 质量规则 22：外部审稿是质量增强层非质量必需，缺失时内置对抗审计不降级
- 质量规则 23：收益递减饱和度判断是软指南非硬停，须确认核心事实点已覆盖
- 终稿纪律第 6 条：可选外部审稿钩子（gpt-researcher-team / consulting-analysis）
- 研究参数卡结构化：8 字段表替换散文描述，Step 0 追加初始化入口
- Step 1 饱和度指南：来源>=5 且最近 3 次搜索无新独立信息时可考虑提前进入 Step 4
- runtime 探测行为说明：规则 17 后追加 try-and-skip 行为描述
- 4 套模板各追加搜索后端类型 + 覆盖局限声明字段

### Changed
- SKILL.md 版本号 v2.3.3 -> v2.3.4，行数 355 -> 380（<=500 目标内）
- 参考文档索引中 CHANGELOG 描述更新为 v2.0.0 -> v2.3.4
- README.md / README_EN.md 精简：363/364 行 -> 134/134 行（<=200 目标），数据源表移至 references/data-sources.md

### Added
- references/data-sources.md：完整可选数据源表（30+ 维度）从 README 迁入

---

## [2.3.3] - 2026-08-03

### Changed
- SKILL.md 模块化拆分：845 行 -> ~380 行，核心文件 <=500 行
- frontmatter compatibility 字段从 47 行压缩至 10 行
- 保留核心工作流（Step 0-8 + 源分级 + 置信标签 + 终稿纪律 + 三-B 闭环 + 工具分层 + 质量规则 20 条）
- 新增参考文档索引节集中列出所有参考文件入口

### Added
- references/templates.md：4 套输出模板（A 通用 / B 行业赛道 / C 公司竞品 / D 学术）
- references/optional-modules.md：可选模块 + 分析透镜库 + 9 skill 方法论吸收表
- references/faq.md：8 条常见问题
- references/example.md：端到端完整示例（工业机器人赛道调研）

---

## [2.3.2] - 2026-08-02

### Added
- scripts/source_health.py：信源存活探测 + 静态 PR 一致性门禁（双向 parity）
- sources.registry.yaml：信源注册表（fred 标 layer: optional）
- .github/workflows/source-health.yml：每日 06:00 UTC 运行 CI
- tests/test_source_health.py：8 个单元测试全过

### Deprecated
- midu-hotsearch 弃用：新版改 OAuth + 付费墙，由 wallstreetcn 免费替代

### Fixed
- 密钥卫生：.gitignore 新增 dmr_keys.env / mcp.json / *.env；setup_mcp.py 写后 chmod 600
- fred_query.py 前缀正则对齐 + load_key() env 剥前缀 + observations URL 编码

### Removed
- sec-edgar-mcp 生成块移除：上游 404 失效，美股维度回退 web_search

---

## [2.3.1] - MCP 鉴权前缀修复 + 跨机器同步 + 可选源增补

- MCP 鉴权前缀 BUG 修复：裸 token 后 Exa/Firecrawl/HF/ModelScope/Tavily 全 200
- Tavily 改用官方 stdio 包免 OAuth；Zhihu 端点纠正 + sse-only 实测全通
- 新增 scripts/setup_mcp.py 跨机器同步（零硬编码 key）
- 新增可选源：FRED / Novada / Connected Papers / agent-reach / wallstreetcn
- midu-hotsearch 弃用；新增 scripts/fred_query.py

---

## [2.3.0] - 平台无关 + 深度研究闭环

- 默认零依赖零安装，不假设任何平台 MCP / agent-team 协议 / 专有后端
- 新增三-B 深度研究闭环（平台无关，纯提示词编排）
- 竞品关键参数交叉验证 >=2 -> >=3；质量规则增 19 / 20
- 新增 references/cross-platform-tools.md 六平台接入指南

---

## [2.2.10] - 可选搜索后端附录补强

- AnySearch / 秘塔搜索登记为 CN 可选增强，无 key 优雅降级

---

## [2.2.9] - 全仓库审计与修正

- Qoder 拼写修正；去除个人环境连接状态注释；README 拆为中英双文档

---

## [2.2.8] - README 特性区重构

- 按最新在前重排版本演进；新增折叠式 English Version；压缩特性清单

---

## [2.2.7] - P1 集成 + 去粗取精

- 增量沉淀升级为结构化 markdown note；hyperresearch 注册为可选深度抓取后端
- Step 1 加意图路由 hint；FAQ Q8 文档化中文/CJK 优势

---

## [2.2.6] - 对抗式审计纪律

- 新增终稿纪律小节：对抗式审计 + patch-never-regenerate + 来源树 + lint 自检清单
- 新增质量规则 16

---

## [2.2.5] - 方法论 sharpening

- Step 2 去重补信息密度优先 + 同源多样性权重；新增三轴混合排序准则

---

## [2.2.4] - 规范性增强

- 新增 FAQ、端到端示例、附录 A；补充质量规则 15

---

## [2.2.3] - 文档一致性修正

- stale 措辞修正：archived -> permanently removed, irreversible；三端统一 v2.2.3

---

## [2.2.2] - 文档准确性修正

- 6 个 skill 由归档可恢复更正为永久删除不可逆

---

## [2.2.1] - 技能去粗取精执行

- GitHub MCP 集成；永久删除 6 个冗余 absorbed skill（不可逆），方法论并入主管线

---

## [2.2.0] - 去粗取精、优先免费 API

- 扩充学术与开放科研数据源（OpenAlex / Semantic Scholar / Crossref / arXiv 等）
- 工程化讨论源与代码模型平台；区分免费 API 直调与通用联网可达

---

## [2.1.0] - 吸收 9 个互补研究类 skill

- 吸收 9 skill 方法论；新增 intel-brief / 宏观监测 / 公众号 / Perplexity / 模板 D

---

## [2.0.0] - 竞争对位实测

- 验证 Step 0-8 主管线与源分级框架；确立 NATO Admiralty 4 级源分级与 >=2 源交叉验证
