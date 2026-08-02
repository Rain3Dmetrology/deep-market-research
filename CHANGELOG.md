# Changelog

## [2.3.4] - 2026-08-03

### Added
- **质量规则 21-23**（纯增量，不修改现有 1-20 条）：
  - 规则 21：源独立性判定 3 条规则（引用链去重 / 通讯社转载去重 / 企业自述区分）——填补规则 18 ">=3 个独立源"中"独立"未定义的缺陷。
  - 规则 22：外部审稿是质量增强层非质量必需——缺失时内置对抗审计仍生效，不降级。
  - 规则 23：收益递减饱和度判断是软指南非硬停——须确认核心事实点已覆盖后才可提前终止搜索。
- **终稿纪律第 6 条**：可选外部审稿钩子（gpt-researcher-team / consulting-analysis），增强非依赖，归入终稿纪律而非新建管线步骤。
- **研究参数卡结构化**：第 218 行散文描述替换为 8 字段结构化表（课题 / 查询类型 / 模板 / timeRange / 语言 / 已收集来源池 / 矛盾台账 / 已完成章节），Step 0 管线图追加"初始化研究参数卡"。
- **Step 1 饱和度指南**：查证库部分追加收益递减软指南（来源>=5 且最近 3 次搜索无新独立信息时可考虑提前进入 Step 4）。
- **runtime 探测行为说明**：质量规则 17 后追加 try-and-skip 行为说明（可选 skill 可用性判断=尝试调用并捕获失败，不预检）。
- **搜索后端透明度声明**：4 套模板（A/B/C/D）"方法论与合规声明"节各追加搜索后端类型 + 覆盖局限声明字段。

### Changed
- SKILL.md 版本号 v2.3.3 -> v2.3.4。
- SKILL.md 行数 355 -> 380（仍在 <=500 行目标内）。
- 参考文档索引中 CHANGELOG 描述更新为 v2.0.0 -> v2.3.4。

### Not Adopted
- **查询路由器 (Step 0.5)**：与第一条硬规则"不跳步"冲突；已有手动"快版"机制更安全。
- **新建 active_sources.yaml**：sources.registry.yaml + source_health.py 已覆盖维护侧；runtime 探测用 try-and-skip。

---

## [2.3.3] - 2026-08-03

### Changed
- **SKILL.md 模块化拆分**（845 行 -> ~380 行，核心文件 <=500 行）：
  - `references/templates.md`：提取 4 套输出模板（A 通用 / B 行业赛道 / C 公司竞品 / D 学术）。
  - `references/optional-modules.md`：提取可选模块（学术数据源 / intel-brief / 宏观监测 / 公众号 / Perplexity）+ 分析透镜库 + 9 个互补 skill 方法论吸收表。
  - `references/faq.md`：提取 8 条常见问题。
  - `references/example.md`：提取端到端完整示例（工业机器人赛道调研）。
  - `CHANGELOG.md`：附录 A 完整更新史（v2.0.0 -> v2.3.1）迁入本文件。
  - SKILL.md frontmatter `compatibility` 字段从 47 行压缩至 10 行（详细信源清单已在 Step 1 管线图 + 第五节工具表 + sources.registry.yaml 中覆盖，frontmatter 仅保留核心原则声明）。
  - SKILL.md 保留核心工作流（Step 0-8 管线图 + 源分级 + 置信标签 + 终稿纪律 + 三-B 深度研究闭环 + 工具分层 + 质量规则 20 条 + 触发约定 + 参考文档索引）。
  - 新增「参考文档索引」节，集中列出所有参考文件入口。

### Added
- `references/templates.md`、`references/optional-modules.md`、`references/faq.md`、`references/example.md` 四个新文件。

### Migration Notes
- SKILL.md 中被提取的章节均已添加指向对应 `references/*.md` 文件的指针。
- Agent 加载 SKILL.md 时，核心工作流完整可用；模板 / 可选模块 / FAQ / 示例按需加载。
- 版本号从 v2.3.2 升至 v2.3.3（结构性变更，非功能变更）。

---

## [2.3.2] - 2026-08-02

### Added
- 源健康监控原型（maintainer-side CI）：
  - `scripts/source_health.py`：探测各信源存活 + 静态 PR 一致性门禁（双向 parity）。
  - `sources.registry.yaml`：信源注册表；`fred` 标 `layer: optional`（宏观维度已由 WebSearch 无 key 覆盖，其死亡不计入 `dimensions_uncovered`）。
  - `.github/workflows/source-health.yml`：每日 06:00 UTC 运行；DEPRECATED 源仍被引用为活跃路由则阻断 CI，盲区/孤儿探针仅告警。
- `tests/test_source_health.py`：首个真实单元测试（8 测全过），覆盖 fred-optional 门禁、`dimensions_uncovered` 聚合、双向 parity、DEPRECATED 阻断、URL 掩码。

### Docs
- 审查局限处置（对应工程审查报告 8）：
  - **ADR 编号冲突**：审计评估 lineage 与编排 lineage 的两个 "ADR-2" 已用 `A-`/`O-` 前缀消歧（见报告 2）。
  - **LLM-eval 质量带**：需 golden 语料 + judge 模型，属后续投入，**非阻塞**，列入 backlog。
  - **仓库零测试**：已通过建立 `tests/` 脚手架 + CI 解决；其余模块（SKILL 编排 / 各 MCP 连接器）测试仍待补，列入 backlog。

### Deprecated
- **midu-hotsearch 弃用原因**（从 README 迁出，遵循 Rule 5）：新版 midu.com 改为 OAuth + 付费墙，原 `MIDU_APP_SECRET` 失效（错误码 202005/203003），故不进 README 终态清单；已由 **wallstreetcn** 免费财经热榜（免 key）替代。

### Fixed
- 密钥卫生：`.gitignore` 新增忽略 `dmr_keys.env` / `mcp.json` / `*.env`；`scripts/setup_mcp.py` 写入 `mcp.json` 与 `dmr_keys.env` 后改为 `chmod 600`，并增加"输出落入 git 工作树则告警"守卫。
- Bug 修复：`fred_query.py` 前缀正则对齐 `setup_mcp.py`（新增 `API\w*KEY` 分支）、`load_key()` env 路径剥前缀、observations URL 对 `series_id` 做 URL 编码；`source_health.py` 确认使用 `yaml.safe_load` 且无 eval/exec/shell。

### Removed
- **sec-edgar-mcp 生成块移除**：上游 `stefanoamorelli/sec-edgar-mcp` 经 `git ls-remote` 实测 404 失效，生成的 server 无法安装；本机暂不需要 SEC EDGAR 维度，故整体移除 `scripts/setup_mcp.py` 中的常量声明、`sec-edgar-mcp` 生成块与桌面 `SECEDGAR_UA.txt` UA key 加载逻辑（共 26 行），全仓无残留引用。`dmr` 美股结构化申报维度继续由 `web_search` 兜底，不影响核心管线。

---

## [2.3.1] - MCP 鉴权前缀修复 + 跨机器同步 + 可选源增补

- MCP 鉴权前缀 BUG 修复（全局）：原 mcp.json 的 env 类 server 带 `APIKEY:` / `access token：` 前缀 -> 上游 API 全 401 拒；修正为裸 token 后 Exa / Firecrawl / HF / ModelScope / Tavily 全部 HTTP 200。
- Tavily MCP 从 mcp-remote（强制浏览器 OAuth）改用官方 `tavily-mcp` stdio 包 -> 无头免 OAuth。
- Zhihu MCP 端点纠正 + `--transport sse-only`，3 端点实测全通。
- 跨机器同步 `scripts/setup_mcp.py`：零硬编码 key、自动剥前缀、生成 mcp.json + dmr_keys.env。
- 新增可选源：FRED / Novada / Connected Papers / agent-reach / agent-browser / wallstreetcn 免费财经热榜。
- midu-hotsearch 弃用（新版改 OAuth + 付费墙）。
- 新增 `scripts/fred_query.py`。
- 学术/社区源文档精度修正（无功能变动）。

---

## [2.3.0] - 平台无关 + 深度研究闭环

- 平台无关化：默认零依赖零安装，不假设任何平台 MCP 配置文件 / agent-team 编排协议 / 专有后端。
- 新增「三-B 深度研究闭环（平台无关，纯提示词编排）」：吸收多平台深度研究 agent 团队精华，去其平台专有约束。
- 竞品关键参数交叉验证 >=2 -> >=3（质量规则 18）。
- 质量规则增 19（可选工具非质量前提）/ 20（不绑定特定平台机制）。
- 新增 references/cross-platform-tools.md（六平台可选工具接入指南）。
- 隐私修正：云端 SKILL.md 移除个人 MCP 连接状态声明。

---

## [2.2.10] - 可选搜索后端附录补强

- 在工具映射表 + frontmatter 增列 AnySearch（厂商自称 76.4% 标 [VENDOR CLAIM]）、秘塔搜索为 CN 场景可选增强。

---

## [2.2.9] - 全仓库审计与修正

- Qoder 拼写修正（Qodo->Qoder）。
- 去除个人环境连接状态注释（隐私修正）。
- AgentKey 重归类为搜索入口聚合兜底。
- 云存储新增 Google Drive（海外用户可选）。
- README 拆为中英双文档。

---

## [2.2.8] - README 特性区重构

- 按「最新在前」重排版本演进；新增折叠式 English Version；压缩特性清单。

---

## [2.2.7] - P1 集成 + 去粗取精

- 增量沉淀升级为结构化 markdown note（YAML frontmatter + 可检索索引）。
- hyperresearch 注册为可选深度抓取后端。
- Step 1 加意图路由 hint（thin router 思想）。
- FAQ Q8 文档化中文/CJK 优势。

---

## [2.2.6] - 对抗式审计纪律

- 新增「终稿纪律」小节：对抗式审计 + patch-never-regenerate + canonical query gospel + provenance 来源树 + lint 自检清单。
- 新增质量规则 16。

---

## [2.2.5] - 方法论 sharpening

- Step 2 去重补「信息密度优先」+ 「同源多样性权重（同源衰减）」。
- Step 2 新增「语义相关度 x 时效 x 源层级 三轴混合」排序准则。
- AnySearch 厂商自称标 [VENDOR CLAIM]。

---

## [2.2.4] - 规范性增强

- 新增 FAQ、完整端到端示例、附录 A（完整更新史）。
- 补充质量规则 15「环境受限!=能力不足」。
- 〇 节冗长更新史压缩为摘要 + 附录指针。

---

## [2.2.3] - 文档一致性修正

- 消除 SKILL.md 兼容性块英文 stale 措辞 `(archived, recoverable)` -> `(permanently removed, irreversible)`。
- 本地 / 仓库 / 发布包三端统一为 v2.2.3。

---

## [2.2.2] - 文档准确性修正

- 将 6 个 skill 由「归档(可恢复)」更正为「永久删除(不可逆)」，消除与 v2.2.1 主题的残留矛盾。

---

## [2.2.1] - 技能去粗取精执行

- GitHub MCP 集成（mcp__github__* 可用）。
- 永久删除 6 个重复冗余且已被吸收的 skill（google-scholar-search / academic-research-hub / deep-research / news-summary / perplexity / tavily，不可逆），其方法论并入主管线。

---

## [2.2.0] - 去粗取精、优先免费 API

- 大幅扩充学术与开放科研数据源（OpenAlex / Semantic Scholar / Crossref / arXiv / PubMed / bioRxiv / OpenCitations / EMBL-EBI / Zenodo / Figshare / Harvard Dataverse / NASA）。
- 工程化讨论源（Stack Overflow / HN / Reddit / 知乎 / CSDN / Product Hunt / TechCrunch / Bluesky / X）。
- 代码与模型平台（GitHub Trending / Hugging Face / 魔塔 ModelScope）。
- 区分「免费 API 直调」与「通用联网可达」。

---

## [2.1.0] - 吸收 9 个互补研究类 skill

- 吸收 9 个互补研究类 skill 的方法论（去其过度约束项，叠加不替换）。
- 新增 intel-brief 输出风格、宏观监测源、微信公众号文章检索、Perplexity AI 搜索、第 4 套学术/基准/技术选型/尽调模板 D。

---

## [2.0.0] - 竞争对位实测

- 验证 Step 0-8 主管线与源分级框架。
- 确立 NATO Admiralty 4 级源分级与 >=2 源交叉验证硬规则。
