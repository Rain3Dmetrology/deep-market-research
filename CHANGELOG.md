# Changelog

## [2.8.0] - 2026-08-29

审计修复发布（四批次审计发现共 21 项（H1-H6 / M1-M8 / L1-L7）逐项修复 + AgentKey 源注册与 R2 断言级校验）；测试套件由 21 扩至 80 用例。

### Fixed
- **H1 · 自包含宣称修正**：frontmatter / 正文的「自包含 / 零依赖」表述改为「默认零依赖、可选后端优雅降级」，与实际降级行为对齐。
- **H2 · 安装清单补齐**：install.sh / install.ps1 分发清单补 `CHANGELOG.md` 与 `sources.registry.yaml`——此前安装器漏发运行时引用与信源注册表两文件。
- **H3 · 信号门限定**：信号门明确限定仅适用于热榜 / 情绪类信号流，不再泛化覆盖新闻 / 报告类流。
- **H4 · 基准评分口径声明**（benchmarks）：明确五维评分为本基准文档自定义口径，删除错误的「权重见 SKILL.md Step 7」引用，并与 Step 7 竞品评分卡、管线内部质量环（ratchet）口径划清边界。
- **H5 · 示例 Step 映射对齐**：references/example.md 端到端示例的 Step 映射与 SKILL.md Step 0->8 管线重新对齐。
- **H6 · 校验器补测试**：`validate_param_card.py` 与 `readme_drift_check.py` 补测试（新增 tests/test_validate_param_card.py、tests/test_readme_drift_check.py）。
- **M1 · 孤儿术语清理**：正文残留的无对应实体孤儿术语清除。
- **M2/T-07 · KNOWN_SOURCES 启发式 WARN**：source_health.py 的 KNOWN_SOURCES 匹配命中改为启发式 WARN，避免静默放行真实漂移。
- **M3 · twitter_x 探针修正**：探针改为 `api.x.com` 端点 + Bearer 头，对齐 X API v2 规范。
- **M4 · R1 判定去重**：validate_report.py R1 证据行判定复用已解析的 `_source_id`，消除重复解析。
- **M5 · 运行时声明**：明确 Python 3.10+ 要求与跨平台文件权限约定。
- **M6 · 安装目标对等**：install.sh / install.ps1 目标目录对齐（含补 `.trae-cn`）。
- **M7 · 用例数勘误（Amended 形式）**：v2.7.0 条目用例数表述失准处已以 Amended 勘误（test_validate_report.py 实测 13 用例，21 为两文件总数），语义同「勘误不打新 tag」。
- **M8 · 版本标记去硬编码**：脚本 / 文档中钉死的版本号改为参数化或动态读取，防版本漂移再发。
- **L1-L7 · 细节修正**：模板确认度列削减、词表标签修正、中英双语文案对齐、CI 补 Windows 矩阵、校验器异常处理补强。
- **CI Windows 编码热修（勘误级，不新增版本号不打新 tag）**：`readme_drift_check.py` 入口补 `_configure_stdio()`（对齐校验器既有方案），修复 windows-latest cp1252/GBK 控制台下打印中文错误明细触发的 UnicodeEncodeError；新增 3 条受限编码回归用例（套件 80 → 83）。

### Added
- **T-03 · AgentKey 源注册**：sources.registry.yaml optional 层注册 AgentKey（实测 2026-08-29）；MCP 型源健康检查走新增 `_mcp_probe` 通道，无凭据时探针按设计 SKIPPED。
- **T-05 · R2 断言级校验**：validate_report.py R2 由引用统计升级为断言级校验——无支撑断言占比 >20% 直接判 FAIL。
- **T-08 · 聚合器路由去重规则**：聚合器路由新增去重规则，同义源多路径不再重复注册。
- **T-09 · Reins 评估记录（观察项）**：记录 Reins 评估结论，列为观察项暂不升级层级。

### Added (终审自查披露层闭环 · 4 项)
- **L5 人工跟进标注**：source_health.py 默认层 DEAD 时 `open_issue+mark_uncovered` 仅为维护者人工跟进标签（无自动开 issue 动作），已在注释层显式标注。
- **P2-7 AgentEarth 观察记录落地**：cross-platform-tools.md 补 AgentEarth（agentearth.ai）2026-08-29 实测条目，结论暂不收编、列为观察项。
- **P2-5 Real Browser MCP 补全**：既有 Reins 评估记录追加 Real Browser MCP 对比，同列观察项。
- **披露口径勘误**：本条目用例数按 `pytest --collect-only` 实测修正为 21 → 80；「审计修复 19 项」按发现编号口径（6+8+7）统一为 21 项。

### Known Issues / Deferred
- **validate_param_card R1 `str(None)` 恒真怪癖**：空字段经 `str(None)` 后存在性校验恒过的怪癖——本版本语义保持不变，待后续单列处理。
- **AGENTKEY_API_KEY 未接入 CI secrets**：CI 环境无凭据时 AgentKey 探针按设计 SKIPPED，不阻塞门禁。后续接入需同时配置 secret 与 source-health.yml 的对应 env 行（本次已补）。

### Tests
- 测试套件 21 → 80 用例（pytest 80/80 PASS）；README 漂移门禁 R1–R7 PASS。

## [2.7.1] - 2026-08-22

热修复（installer-only，内核零变化）：install.sh 由 base64 blob 重写为可运行纯 bash，与 install.ps1 对齐。

### Fixed
- **install.sh 分发 scripts/ 与 benchmarks/ ＋ 排除 __pycache__**：v2.7.0 的 install.sh 为 base64 blob 且缺 `scripts`/`benchmarks` 分发——Linux/macOS 安装后技能目录缺 SKILL.md 运行时引用的机检脚本。重写为纯 bash 并固定 LF（`.gitattributes`），补齐 `.trae-cn` 目标。
- **真机冒烟验证**：在 ubuntu:22.04 容器内以真实 bash 执行修复后 install.sh —— scripts×2 / benchmarks / SKILL.md 全部落位、`__pycache__` 清除，PASS（补上此前缺失的 Linux 实机验证）。

### Amended (2026-08-24 · 治理规范 v2.2 对齐审计勘误，docs-only)
- **SKILL.md 正文版本对齐 2.7.1**（审计 F1）：正文头 `> 版本:` 与参考索引 `CHANGELOG.md` 行两处残留 2.7.0——v2.7.1 热修复仅覆盖 frontmatter 两种格式，正文格式不同未命中；README 漂移守卫新增 R7（SKILL.md 版本一致性）防复发。
- **规则 20 补分工边界**（审计 F9）：尾部加「多智能体编排由上层编排层（如 RAT）承担，本内核保持协议无关」。
- **参数卡 schema 验收标准补「假设失效」语义**（审计 M3）：核心前置假设被证伪时达标即停不适用——显式披露并复用介入窗口请用户重定界；不新增第四态（守住三态封闭枚举与「不新增循环」原则）。
- **README/README_EN 补发布清单**（维护者 8 步，中英双语）：本地门禁（漂移 R1–R7 ＋ pytest）→ 版本对齐 → 双安装脚本冒烟 → CI → 内核变化时基准回归 → tag → GitHub Release（勘误 Amended 不打新 tag）→ 平台副本核对。

## [2.7.0] - 2026-08-22

P1 瘦身（基准首跑建基线后执行，内核零变化）：模式选择三处重复收敛至 §四唯一权威 + 考古句清理 + 校验器排版/模板容差（scripts/，SKILL.md 零改动）。

### Fixed
- **机检门禁排版容差（Q6 基准暴露）**：`validate_report.py` 章节匹配支持标题限定词（「矛盾台账（证据冲突裁决记录）」命中「矛盾台账」角色）；R1 证据行判定改为层级格以 T1-T4 开头（散文提及「无 T1-3 全口径源」不再误判）；R2 合格引用同时计入内联「源A(T1, 日期)」与证据表行（对齐 §七 实体级证据缓存表形态）。新增 `tests/test_validate_report.py`（21 用例）。
- **裸域名引用识别（Q2 基准暴露）**：R2 可识别来源扩展为 URL > DOI > 裸域名（`keyence.com.cn` 无 scheme 写法）；裸域名取域名部分去路径（同站不同路径不重复计独立源）；末位标签纯字母 2-6 位排除数值误报（`83.0%` / `v2.6.1` / `2026.08.22` 不构成来源）。
- **模板 E 机检兼容（Q5 基准暴露）**：auto 模式检测到「本期变化总览」（delta）即按模板 E 角色集校验（delta/信源/开放问题/方法论），不再套用 A-D 角色集误报缺执行摘要；R3 对模板 E 以全文双方案并列标记（并存/方案A|B/双口径）替代独立矛盾台账章节存在性检查（模板 E 冲突由置信迁移承载，templates.md 规范结构本无该章节）。
- **install.ps1 分发 scripts/**：`$Files` 补 `scripts` 目录——SKILL.md §三-B 与终稿纪律两处运行时引用 `python scripts/*.py`，此前平台技能副本缺机检脚本（WorkBuddy 残留旧版构成版本漂移）；拷贝后清除 `__pycache__`。已验证 4 平台（.claude/.codex/.trae-cn/.workbuddy）落位 v2.7.0 + 6 脚本，分发副本独立运行 PASS。
- 验证结果：6/6 基准报告机检 PASS（Q1-Q6），pytest 21/21，README 漂移守卫 PASS。

### Changed
- **模式路由收敛为唯一权威**：SKILL.md §四「模板选择」扩为完整路由表，合并 §〇/§七/references/templates.md/references/faq.md 四份副本的全部触发词与强制项（B 行业赛道补「商业化落地/市场规模」、C 补「扒一下/挖一下/对标」、E 补「盯」与「历史沉淀 note」回退语义）；§〇 模式选择收敛为单行指针（5 行 -> 1 行）、§七 删除四条模式复写（9 行 -> 4 条）、templates.md 删除第四份路由表改指针、faq.md Q3 改指针——触发词从此只在一处维护，杜绝多副本漂移。
- 「五大板块」标签精化（Q6 探针 cosmetic 项）：路由标签由「模板 B（五大板块）」改为「模板 B（行业赛道五大板块）」，销售触发独立成行显式标注 §3.5 必含，消除「5 板块 vs 5+1 小节」歧义；模板 B §3 小节名「核心发现：五大板块」与 benchmark 锚点不变（validate_report.py 机检兼容）。
- 模板方法论行版本参数化：templates.md 四处「deep-market-research v2.3.2」钉死改为「v<版本>」占位符，报告按实际运行版本填写。

### Removed
- 考古句清理：SKILL.md frontmatter「v2.2.1 已永久删除 6 个冗余 absorbed skill」；references/ 四处「本文件从 SKILL.md v2.3.2 提取」；SKILL.md 与 references/ 正文散布的（v2.4.0）（v2.6.0）版本标记——版本叙事只留在 CHANGELOG，正文只描述当前能力。

### Amended (2026-08-29 · 用例数勘误，docs-only，不打新 tag)
- **用例数勘误（审计 M7）**：上方 Fixed 条目「新增 `tests/test_validate_report.py`（21 用例）」表述失准——该文件实测 13 个用例；21 为两文件总数（`test_validate_report.py` 13 + `test_source_health.py` 8，与「验证结果：pytest 21/21」一致）。

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
