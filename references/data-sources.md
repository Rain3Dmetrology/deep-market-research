# 可选数据源与增强 Skill 接入指南

> 本文档承载 README 中移出的完整数据源表。dmr 本身调用 Agent 内置联网工具（WebSearch / WebFetch）即可工作；以下 Skill / MCP 有则增强深度，**缺失时一律优雅降级，不会中断调研**。

---

## 推荐层级与接入方式图例

| 标记 | 含义 |
|------|------|
| 🥇 | 首选（默认增强） |
| 🥈 | 备选 |
| 🛟 | 兜底（含内置基座，免 key 即可用） |
| 🎯 | 个性化（平台专有 / 需 key） |
| ⚠️ | 不推荐通用 |
| 🟢 | 零配置（免 key / 免 token，装即用） |
| 🔴 | 需 API key（缺失优雅降级） |
| 🟡 | 需 Cookie / token / 平台授权 / 连接 MCP 服务器 |

---

## 完整数据源表

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

---

## 声明

- **诚实声明**：仅声明真实存在的连接器类型，不暴露个人环境连接状态；缺失即优雅降级、不中断调研。未提供的服务（如 Firecrawl 商业版、Crunchbase Pro、PitchBook）不虚假标注——若你所在平台提供，可在 Step 1 搜索入口追加。
- **路由不打包**：本表均为 dmr 主管线**外部可选 peer skill / MCP**，dmr 只做源路由与优雅降级、不复制 / 捆绑其实现；缺失即跳过并标注维度未覆盖，不中断调研。
- **接入方式**：🟢 零配置（免 key / 免 token，装即用：① LLM 自带 `web_search` / `web_fetch` ② dmr 直连的免 key 公共 REST API，如 OpenAlex / wallstreetcn / aihot）· 🔴 需 API key（缺失优雅降级）· 🟡 需 Cookie / token / 平台授权 / **连接 MCP 服务器**（即使免 key，如 DeepWiki / SearXNG / AgentKey 仍需配连接端点，非零配置）。

> Cross-validation snapshot 2026-07; search APIs drift quarterly — re-verify against vendor before production.
