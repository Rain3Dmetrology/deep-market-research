# Deep Market Research — 深度市场调研 Skill



> 🌐 语言 / Language：**[🇨🇳 中文](README.md)** · [🇺🇸 English](README_EN.md)



> 跨平台 AI Agent 调研工作流：源分级 + ≥2 源交叉验证 + 去重/去旧/去假/去矛盾 + 吸收真实用户热评，输出质量稳定、可复现、带置信度标签的调研报告。



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

遵循 [Agent Skills 开放标准](https://agentskills.io/)（Anthropic 发起，Claude Code / OpenAI Codex / TRAE / Qoder / WorkBuddy 等 50+ 平台原生支持）。



---



## ✨ 特性（v2.3.4）



> 与通用 AI 搜索 / 深度研究 skill 的核心差异：**dmr 不是搜索包装，而是一条可复现、带置信标签、终稿对抗审计的调研流水线。**



### 版本演进

- 完整版本变更明细见 [CHANGELOG.md](CHANGELOG.md)。


### 独有优势



- **确定性流水线**：固定 Step 0–8，每次可复现、可对比。

- **源分级置信**：T1 官方 / T2 专家 / T3 二手 / T4 社媒，每条结论带置信标签。

- **≥2 源交叉验证**：事实拆解，冲突显式标注，不强行共识。

- **终稿对抗审计**：终稿前独立 critic 挑战，局部修补，不整篇重写。

- **中文/CJK 原生支持**：公众号、知乎、小红书、CNKI 等中文源不丢弃、不当 junk。

- **零安装 Skill**：纯方法论，调用 Agent 内置工具，无需额外 Python 依赖。

- **可选工具永不阻断**：Exa / Firecrawl / Tavily / Perplexity / GPT Researcher / ModelScope 有则增强，缺失优雅降级。

- **平台无关**：不绑定任何 MCP 配置 / agent-team 协议 / 专有后端，WorkBuddy / Claude / Codex / Trae / qoder / Cursor 通用；可选工具缺失即优雅降级。



### 输出能力



- **三套模板**：通用调研 / 行业赛道（麦肯锡风）/ 公司竞品（SWOT + 情景推演）。

- **intel-brief 风格**：事实 → 影响 → 原因三元组织。

- **学术模块**：arXiv / PubMed / OpenAlex / Semantic Scholar / CNKI，优先 🆓 免费 API。

- **分析透镜**：波特五力 / PESTEL / BCG / 3C / TAM-SOM，按意图触发，不堆砌。

- **增量沉淀**：结构化 markdown note（YAML frontmatter），对接 ima / Obsidian / 本地 wiki。



### 技术栈与流水线（可视化）



**调研流水线（Pipeline）** — 主管线 Step 0–8 与三-B 深度研究闭环正交，质量由方法论保证而非某个搜索 API：



![调研流水线](assets/pipeline.svg)



**技术栈（Stack）** — 默认层零依赖零安装；可选增强层缺失即优雅降级，仅丰富素材来源：



![技术栈](assets/stack.svg)



---



## 🌐 支持的平台



本仓库遵循 [Agent Skills 开放标准](https://agentskills.io/)，以下平台原生支持，**直接安装即可被自动发现并触发**：



| 平台 | Skills 目录 | 触发方式 |

|------|------------|---------|

| **Claude Code / Claude** | `~/.claude/skills/` | 自动发现 + `/deep-market-research` |

| **OpenAI Codex** | `~/.codex/skills/` | 自动发现 |

| **TRAE** | `~/.trae/skills/` | 自动发现 |

| **Qoder** | `~/.qoder/skills/` | 自动发现 |

| **WorkBuddy / CodeBuddy** | `~/.workbuddy/skills/` | 自动发现 |

| 其他 agentskills 兼容平台 | 对应 `skills/` 目录 | 自动发现 |



> 完整的兼容平台列表见 [agentskills.io/clients](https://agentskills.io/clients)。



---



## 📦 安装



### 方式一：一键安装脚本（推荐）



克隆后运行安装脚本，会自动检测本机已安装的 Agent 平台并复制到对应 `skills/` 目录：



```bash

# Unix / macOS / Git Bash

git clone https://github.com/Rain3Dmetrology/deep-market-research.git

cd deep-market-research

./install.sh



# Windows (PowerShell)

git clone https://github.com/Rain3Dmetrology/deep-market-research.git

cd deep-market-research

powershell -ExecutionPolicy Bypass -File install.ps1

```



脚本会检测 `~/.claude`、`~/.codex`、`~/.trae`、`~/.qoder`、`~/.workbuddy` 中**已存在**的目录并安装，未安装的自动跳过。



### 方式二：手动安装



将整个 `deep-market-research/` 文件夹复制到目标平台的 skills 目录：



```bash

git clone https://github.com/Rain3Dmetrology/deep-market-research.git

# Claude Code / Codex / Cursor / Windsurf / Gemini CLI 等

cp -r deep-market-research ~/.claude/skills/

# WorkBuddy

cp -r deep-market-research ~/.workbuddy/skills/

# TRAE

cp -r deep-market-research ~/.trae/skills/

# Qoder

cp -r deep-market-research ~/.qoder/skills/

```



安装后**重启 Agent**（或执行 skill 刷新指令）即可加载。



---



## 🚀 使用



直接对 Agent 说（自动匹配 `SKILL.md` 的 `description` 触发）：



- 「调研一下工业 AI 3D 视觉测量的竞争格局」

- 「竞品分析：海康机器人 vs 深视智能 vs 天准科技」

- 「行业趋势：中国机器视觉产业链投资机会」

- 「扒一下 Keyence 中国的底」



Agent 会按 SKILL.md 的固定流程执行：范围收敛 → 多源采集 → 去重去旧 → 源分级 → 交叉验证去假 → 矛盾消解 → 吸收热评 → 100 分评分 → 结构化输出。



---



## 📂 目录结构



```

deep-market-research/

├── SKILL.md                      # 核心：元数据 + 完整工作流指令（Step 0–8 + 三套模板 + 分析透镜 + 质量规则）

├── README.md                     # 中文说明（本文件）

├── README_EN.md                  # English documentation

├── release_body.md               # GitHub Release 描述（发布时由 `gh release edit` 引用）

├── assets/

│   ├── pipeline.svg              # 调研流水线可视化图

│   └── stack.svg                 # 技术栈可视化图

├── references/

│   └── cross-platform-tools.md   # 可选：六平台可选增强工具接入指南（缺失不影响主流程）

├── LICENSE                       # MIT

├── CONTRIBUTING.md               # 贡献指南

├── install.sh                    # Unix 安装脚本

├── install.ps1                   # Windows 安装脚本

├── icon.png                      # Skill 图标

├── scripts/                      # 可选辅助：跨机器 MCP 同步 (setup_mcp.py) + FRED 宏观数据查询 (fred_query.py)

└── .gitignore

```



> Skill 核心**自包含**：所有工作流、模板、规则都内嵌在 `SKILL.md` 中，无需额外脚本或配置文件；`references/` 仅是可选项增强工具接入指南，缺失不影响主流程。



---



## ⚙️ 可选数据源与增强 Skill（按需接入，优雅降级）



Skill 本身调用 Agent 内置联网工具（WebSearch / WebFetch）即可工作。若你的 Agent 已装以下 Skill 或连以下 MCP，会自动获得更强深度；**缺失时一律优雅降级，不会中断调研**：




| 维度 | 数据源 / Skill | 用途 | 推荐 | 接入方式 |
| ------ | -------- | ------ | ------ | ------ |
| **搜索入口** | 内置 WebSearch/WebFetch · Firecrawl · **Exa** · Tavily · SearXNG · Novada · AgentKey | 通用联网检索、查证、聚合数据（可替代缺失的专业 MCP） | 🛟 内置基座(始终) · 🥇 Firecrawl · 🥈 Exa/Tavily/Novada · 🛟 SearXNG/AgentKey（并行增强） | 🟢 内置基座(web_search/web_fetch) · 🔴 Firecrawl/Exa/Tavily/Novada 需 key · 🟡 SearXNG(自托管)/AgentKey(连接器) 需连 MCP/账号 |
| **AI 搜索（可选）** | Perplexity · Tavily · AnySearch · 秘塔搜索 | 带引用的 AI 搜索，无 key 跳过 | 🎯 Perplexity/秘塔 · 🥈 Tavily · 🎯 AnySearch | 🔴 均需 API key（无 key 跳过） |
| **社媒 / 热评** | **agent-reach** / **agent-browser** / **web-access**（CDP 浏览器自动化 skill，可选） | 小红书/知乎/Reddit/Bluesky/X/评论抓取（agent-reach 实测 6 社媒 + 5 基础；**抖音/微博 走 web_search 兜底，公众号走 wechat-article-search skill，非 agent-reach 频道**） | 🎯 平台专有 | 🟡 agent-reach / agent-browser / web-access 需装 skill（web-access 需 Node22 + 本地 Chrome CDP）· 🟢 web_search 内置（LLM 自带，零配置，新装即用） |
| **知乎（技术+反馈）** | **zhihu MCP**（search_content + hot_list） | 中文技术教程、用户反馈、产品体验交叉验证 | 🎯 平台专有 | 🟡 内置授权（30 天续期） |
| **微信公众号文章** | **wechat-article-search**（搜索发现）+ **ReadGZH-Agent MCP**（全文提取，远程零安装） | 中文一手深度文章检索：搜索用 skill、全文用 MCP，互补；补 UGC 评论之外的文章级缺口 | 🥇 ReadGZH(全文) · 🎯 wechat-article-search(搜索) | 🟡 装wechat-article-search skill · 🔴 ReadGZH 需 READGZH_API_KEY |
| **抖音（短视频）** | **douyinmcp MCP**（get_homefeed 热榜 + 深度内容，免费优先）/ **TikHub API**（付费稳定备选） | 抖音趋势与深度内容；反爬极严，优先免费方案，缺失回退 web_search | 🎯 douyinmcp(免费) · 🥈 TikHub(付费) | 🟡 需 Cookie（Chrome 登录态） |
| **文档净化** | **markitdown** | PDF/Word/财报 → Markdown | 🎯 平台专有 | 🟡 需装skill |
| **A 股财务** | **通达信 tdx-connector** | 上市公司 F10 财报/股东/资金流 | 🎯 平台专有 | 🟡 需平台授权 |
| **专利** | **智慧芽 PatSnap MCP** | 技术壁垒、专利家族、引用分析 | 🎯 平台专有 | 🟡 需内部 token |
| **代码 / 项目** | GitHub 搜索 + Trending（`github` MCP + `gh` CLI 已认证 + web） | 开源实现、技术栈、Star/PR 趋势（MCP 直连优先，gh CLI 兜底） | 🥇 DeepWiki · 🥈 GitHub/gh | 🟡 DeepWiki 需连 keyless MCP（无 key，但需配 mcp 端点）· 🟡 github MCP/gh 需授权 |
| **学术论文 / 元数据** | **OpenAlex** / **Semantic Scholar** / **arXiv** / **PubMed** / **bioRxiv** / **EMBL-EBI·Europe PMC**；`literature-search` skill 作方法论参考（非可调用 API） | 论文元数据、引用网络、TLDR 摘要、预印本 | 🛟 免费 API | 🟢 全部免 key（Semantic Scholar 无 key 限 ~100 req/5min·IP，可申请免费 key 提额） |
| **引文溯源** | **Crossref**（DOI 元数据+参考文献）/ **OpenCitations**（开放引文网络） | DOI 权威元数据、被引/引用关系 | 🛟 免费 API | 🟢 免 key |
| **科研数据仓库** | **Zenodo** / **Figshare** / **哈佛 Dataverse** / **NASA** | 数据集/软件/成果，均带 DOI 可溯源 | 🛟 免费 API | 🟢 免 key（NASA 可用 DEMO_KEY） |
| **AI 模型 / 数据集** | **Hugging Face Hub API** / 魔塔 ModelScope | AI 模型、代码、应用文档、数据集 | 🛟 HF 免费 API · 🎯 ModelScope | 🟡 HF 需 `HF_TOKEN`（私频/高配额/写操作/下载 gated 模型；公频浏览与公开权重可免 token）· 🟡 ModelScope 需 token |
| **开发者社区** | **Stack Overflow**（SE API 免 key）+ **Hacker News**（Algolia API；Firebase 端点 2023 已停服）/ Reddit（2023 起需 OAuth，dmr 走 agent-reach / web_search 兜底）/ CSDN（非官方 API） | 技术选型讨论、真实踩坑反馈 | 🛟 免费 API | 🟢 免 key（Reddit 需走兜底；HN 部分网络出口 IP 被 Algolia WAF 屏蔽时回退 web_search） |
| **财经 / 热榜** | 腾讯自选股 / westock-mcp · **wallstreetcn**（免费财经热榜+快讯，免 key） | 上市公司基本面、行情、研报、实时热榜信号 | 🎯 平台专有 · 🟢 wallstreetcn | 🟢 wallstreetcn 免 key · 🟡 自选股/westock 需授权 |
| **法律 / 合规** | 威科先行 / 元典 / **北大法宝（pkulaw）** | 诉讼、资质、行政处罚、法律法规检索 | 🎯 平台专有 | 🟡 需平台授权 |
| **企业工商 / 风险** | 天眼查 MCP / 企查查 MCP / **启信慧眼（qixinhuiyan）** | 股权、司法、经营异常、知识产权、企业风险洞察 | 🎯 平台专有 | 🟡 需平台授权 |
| **顶刊 / 中文文献** | Nature / Science（引 DOI）/ CNKI / Google Scholar（仅用户导出） | 顶刊一手（摘要公开，全文多需订阅）；访问伦理 | 🌐 通用联网 | 🟢 摘要免 key · 🟡 CNKI/订阅需授权 |
| **宏观经济** | Trading Economics / FRED / 国家统计局 / 央行·证监会 / 财联社 / 华尔街见闻 | 宏观指标 + 超预期/不及预期判断 | 🌐 通用联网 | 🟡 FRED 需 `FRED_API_KEY`（免费申请，**强需**：无 key 直接 HTTP 400 `Variable api_key is not set`）· 🌐 其余通用联网 |
| **专利（公开库）** | Google Patents / USPTO / EPO / WIPO | 专利原文、法律状态 | 🌐 通用联网 | 🟢 免 key |
| **开放百科** | Wikipedia / 百度百科 | 概念科普、背景知识 | 🌐 通用联网 | 🟢 免 key |
| **产品 / 创投** | Product Hunt / TechCrunch / 36氪 / 虎嗅 | 新品发布、融资、市场热度 | 🌐 通用联网 | 🟢 免 key |
| **中文社区** | 博客园 / V2EX / 小红书 / B站 | 用户反馈、产品体验、教程 | 🌐 通用联网 | 🟢 免 key（小红书/B站走 web_search） |
| **国际社媒** | Bluesky / X(Twitter) / YouTube / LinkedIn | 官方动态、KOL 评论、用户情绪 | 🌐 通用联网 | 🟢 免 key（走 web_search/agent-reach） |
| **新闻 / 资讯** | aihot（免 key 中文 AI 资讯）/ BBC / Reuters / Al Jazeera | 行业快讯、国际一手新闻 | 🛟 aihot 内置 · 🌐 其它 | 🟢 aihot 免 key · 🌐 其它通用联网 |
| **知识库** | ima-mcp / Obsidian / 本地 wiki / **notion** | 用户自有资料、增量 Lint 沉淀 | 🎯 平台专有 | 🟡 需平台授权 |
| **云存储 / 文件** | **百度网盘（baidu-netdisk）/ Google Drive（海外用户可选）** | 用户自有文件、报告归档与投递 | 🎯 平台专有 | 🟡 需平台授权 |

> **诚实声明**：仅声明真实存在的连接器类型，不暴露个人环境连接状态；缺失即优雅降级、不中断调研。未提供的服务（如 Firecrawl 商业版、Crunchbase Pro、PitchBook）不虚假标注——若你所在平台提供，可在 Step 1 搜索入口追加。
> 推荐层级：🥇 首选 · 🥈 备选 · 🥉 备选 · 🛟 兜底（含内置基座）· 🎯 个性化（平台专有 / 需 key）· ⚠️ 不推荐通用。
> **路由不打包**：本表均为 dmr 主管线**外部可选 peer skill / MCP**，dmr 只做源路由与优雅降级、不复制 / 捆绑其实现；缺失即跳过并标注维度未覆盖，不中断调研。
> **接入方式**：🟢 零配置（免 key / 免 token，装即用：① LLM 自带 `web_search` / `web_fetch` ② dmr 直连的免 key 公共 REST API，如 OpenAlex / wallstreetcn / aihot）· 🔴 需 API key（缺失优雅降级）· 🟡 需 Cookie / token / 平台授权 / **连接 MCP 服务器**（即使免 key，如 DeepWiki / SearXNG / AgentKey 仍需配连接端点，非零配置）。




---



## ❓ 常见问题与完整示例



- **FAQ（7 问）**：本 skill 与 WebSearch 的区别、核心源不可达怎么办、模板 B/C/D 如何选择、是否需要付费 key、矛盾源如何处理、报告长度、增量沉淀是否必须 ima —— 见 SKILL.md [第八节 · 常见问题（FAQ）](SKILL.md#八常见问题faq)。

- **端到端示例**：从「调研中国工业机器人赛道 + 减速器国产化 + 埃斯顿/汇川对位」用户提问，到 Step 0→8 逐环产出物（采集 / 去重 / 验证 / 矛盾消解 / 分级 / 模板 / 评分卡）—— 见 SKILL.md [第九节 · 完整示例](SKILL.md#九完整示例端到端从用户提问到报告)。

- **完整更新史**：v2.0.0 → v2.3.4 每项变更细节 —— 见 [CHANGELOG.md](CHANGELOG.md)。



---



## 📜 许可证



[MIT License](LICENSE)

