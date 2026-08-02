# Changelog

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
