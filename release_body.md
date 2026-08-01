# v2.3.2 — P0 密钥卫生 + 健壮性修复 + 依赖清理

> **2026-07-23** · 维护性小版本（基于 v2.3.0 增量修复 + 可选源吸收）
> 主管线（Step 0→8 + 三-B 深度研究闭环）零变动，仅 bug 修复 / 工具增强 / 可选源文档。

---

## 🐛 关键修复

- **MCP 鉴权前缀 BUG（全局）**：原 mcp.json 的 env 类 server 带 `APIKEY:` / `access token：` 前缀 → 上游 API **全 401 拒**。修正为裸 token 形式后 Exa / Firecrawl / HF / ModelScope / Tavily 全部 HTTP 200。
- **Tavily MCP 桥接策略**：从 mcp-remote（强制浏览器 OAuth）改用官方 `tavily-mcp` stdio 包 → 无头免 OAuth，自动化可用。
- **Zhihu MCP 端点路径**：URL 从 `/mcp/.../sse`（404/SPA）纠正为 `/api/mcp/.../v1/sse`，并强制 `--transport sse-only`（mcp-remote 默认 `http-first` 对纯 SSE 端点返 405/SPA）。3 个端点（搜索/可信全网/热榜）实测 initialize + tools/list + tools/call 全部返回**真实知乎数据**。
- **裸 key 文件解析兜底**：原 `extract_key` 仅识别带前缀行 → 修复为「无前缀时回退到首个非空行」，兼容 novada 类单行长 key。

---

## ✨ 新增能力

### 跨机器 MCP 同步（`scripts/setup_mcp.py`）
- **零硬编码 key**、读取使用者本地桌面 key 文件、自动剥前缀（Rule 1）、生成用户级 `mcp.json` 配置
- 同时输出 `~/.workbuddy/dmr_keys.env`（FRED/Novada 等非 MCP key），完成 dmr 全配置跨机器同步
- 隐私自查通过：无任何硬编码 key、无绝对路径泄露、GitHub 仓库 grep 无 key 泄露

### 新增可选源（`references/cross-platform-tools.md`）
| 源 | 类型 | 价值 | 决策 |
|---|---|---|---|
| **FRED**（美联储经济数据） | 结构化时间序列（GDP/CPI/利率/就业/M2 80万+ 系列） | 免费官方权威，补 dmr **结构化经济数据空白** | ✅ **吸收**（强烈建议） |
| **Novada Web Unblocker** | 住宅代理 / 反爬解锁 | 与 Firecrawl 反爬部分重叠 | ✅ 吸收为**兜底解锁层** |
| **Connected Papers** | 论文关联图谱（S2 ShaID → 研究邻里） | early-access，余 ~50 次构建 | ✅ 吸收为**深度尽调可选源** |
| **AnySearch** | 通用实时搜索聚合 | 与 exa/tavily/firecrawl 高度重叠 | ❌ 不吸收（仅存 APIKEY） |
| **agent-reach** | 实测 6 社媒 + 5 基础（Twitter/Reddit/Facebook/Instagram/B 站/小红书 + GitHub/V2EX/RSS/Web-Jina/YouTube）；抖音/微博→web_search 兜底，公众号→wechat-article-search / ReadGZH | 覆盖 MCP 未触及的社媒/UGC 另类数据 | ✅ 吸收为**社媒增强层**（已激活，实测 10/15 渠道） |
| **agent-browser** | 浏览器自动化 | 与 Firecrawl 重叠且更重 | ⚠️ 仅作交互兜底，不进核心 |
| **ReadGZH-Agent** | 微信公众号**全文提取**（远程 MCP `https://api.readgzh.site/mcp-server`，4 工具 read/search/list/get，免费 30 积分/日） | 补 wechat-article-search 仅有标题/摘要的缺口，稳定穿透反爬 | ✅ 吸收为**公众号全文可选源**（与 wechat-article-search 互补） |
| **midu-hotsearch** | 30+ 平台**热搜/榜单**（抖音热点榜 rankType=1、微博、知乎等） | 抖音趋势/舆情监测零爬取成本 | ❌ **已弃用**：新版 midu.com 蜜度 API 改用 OAuth（client_id+client_secret）+ 付费/申请权限（剩余权限 0 + 错误码 202005/203003），与原 skill 单 key 鉴权不兼容。**替代**：抖音热榜用 `douyinmcp.get_homefeed`（已 8/8 活）、财经热榜用 wallstreetcn（免费无 key） |
| **douyinmcp** | 抖音**深度内容 + 热榜**（搜索/评论/用户/视频/get_homefeed 首页流，本地 a_bogus 签名） | 抖音深度检索 + 实时热榜信号，免费本地 MCP | ✅ 吸收为**抖音深度可选源**（优先免费，需 Chrome 登录 Cookie；`get_homefeed` 已 8/8 工具激活，替代 midu 的抖音维度） |
| **wallstreetcn（华尔街见闻）** | **实时财经热榜/要闻/快讯**（A股/美股/港股/全球/外汇/黄金/原油/数字货币 5+ 频道） | 中文财经研究首选，替代 midu 的金融维度 | ✅ **吸收为财经热榜可选源**（免费、免 key，2026-07 实测 5 频道 + 4 端点全 HTTP 200） |
| **TikHub API** | 微信+抖音**结构化 JSON**（阅读/点赞/评论，稳定契约） | 付费稳定备用，规模化检索 | 🥈 备选（付费，按请求计费） |

### 新增脚本
- **`scripts/fred_query.py`**：轻量 FRED 查询工具（按系列 ID 查观测 / 按关键词搜索系列），自动读桌面 key（Rule 1 剥前缀）。

---

## 📊 已集成的检索源

- **本地 MCP 连接器（脚本化管理）**：exa / firecrawl / tavily / huggingface / modelscope / zhihu（search · global · hotlist）/ readgzh（远程 MCP）+ keyless deepwiki 远程 MCP
- **默认层**：LLM 内置 web_search / web_fetch
- **可选增强源（路由不打包 · 优雅降级）**：FRED（结构化经济数据）、agent-reach（社媒/UGC，实测 10/15 渠道）、Novada（兜底解锁层）、ReadGZH-Agent（公众号全文）、douyinmcp（抖音深度 + `get_homefeed` 热榜，免费优先）、wallstreetcn（财经实时热榜/快讯，免费无 key）、TikHub（微信+抖音结构化，付费备用）、**midu-hotsearch 已弃用**（新版蜜度 API 不兼容 + 付费门槛）
- **原则**：dmr 只做**路由编排 + 优雅降级**，不捆绑任何外部 peer skill / MCP；未连接或缺失 key 时自动回退 `web_search` 并注明「未覆盖该维度」，绝不阻断 Step 0→8 主管线。

---

## ⚠️ 已知 / 待用户手动

- **agent-reach 频道配置**：已实测 10/15 渠道可用；详见 cross-platform-tools §2.1.1。
- **ReadGZH-Agent（公众号全文）**：需 API key（免费档 30 积分/日，控制台领取）；`mcp.json` 加 `url: https://api.readgzh.site/mcp-server` + `headers.Authorization: Bearer <key>` 即生效（已实测 HTTP 200 + 4 工具全回）。
- **midu-hotsearch（抖音热搜）**：❌ **已弃用** — 新版 midu.com API 不兼容 + 付费门槛。替代：抖音热榜走 `douyinmcp.get_homefeed`，财经热榜走 wallstreetcn，其余 web_search+zhihu MCP 兜底。
- **douyinmcp（抖音深度 + 热榜）**：需从已登录 Chrome 导出 `cookies.txt`；`get_homefeed` 工具可作抖音实时热榜信号（已 8/8 工具激活）。未配置则抖音检索回退 web_search。Chrome 登录态经 OpenCLI 浏览器桥已确认可达。
- **wallstreetcn（财经热榜）**：🆕 免费无 key REST API（`https://api-one.wallstcn.com/apiv1/content/{articles,lives,hots,hot-rank}?channel=...&limit=...`），已实测 5 频道全 HTTP 200。

---

## 📝 文档准确性修正（README / SKILL）

- **README 可选数据源表新增「接入方式」列**：以 🟢 零配置 / 🔴 需 API key（优雅降级）/ 🟡 需 Cookie·token·平台授权·连 MCP 三态折叠呈现，仍单表、信息密度↑、篇幅不变。图例铁律：🟢 仅含 ① LLM 自带 web 工具 ② dmr 直连免 key 公共 REST API；**MCP 服务器即使免 key 也归 🟡**（免 key ≠ 零配置）。
- **关键修正（避免「免 key = 零配置」误判）**：FRED 实为**强需 key**（无 key 直接 HTTP 400，免费申请 32 字符小写字母数字）；HuggingFace 公频浏览免 token、私频/写操作需 `HF_TOKEN`；搜索入口补列 **Exa**；**web-access** 实为独立 CDP 浏览器自动化 skill（非 LLM 内置，需 Node22 + 本地 Chrome）；**DeepWiki / SearXNG / AgentKey** 虽免 key 但仍需连 MCP/账号 → 均归 🟡。
- **弃用项只进版本说明**：midu-hotsearch 从 README 终态清单删除，原因仅留本文件 + SKILL 附录A + README 版本演进 bullet；英文 README 同步（抖音行删 midu、财经行加 wallstreetcn）。
- **学术 / 社区源文档精度修正（无功能变动）**：Semantic Scholar 补"无 key 限 ~100 req/5min·IP，可申请免费 key 提额"、literature-search 注明"非可调用 API，仅方法论参考"、Hugging Face 补"gated 模型（如 Llama）需登录 + 接受 EULA 才能下载，公频浏览/公开权重免 token"、Hacker News 注明"Algolia 端点（Firebase 端点 2023 已停服）"、Reddit 注明"2023 起需 OAuth → agent-reach / web_search 兜底"；并标注 HN 部分出口 IP 被 Algolia WAF 屏蔽时回退 web_search。中英 README + SKILL 学术模块表同步。

---

## 🔐 隐私红线

- 本仓库**零真实 key**、**零个人 MCP 连接状态**、**零绝对路径泄露**
- 仅含：连接器类型、官方端点 URL（keyless 远程 MCP）、Rule-1 剥前缀脚本、公开文档
- 所有密钥仅存于使用者本地环境，由 `scripts/setup_mcp.py` 在本地生成配置，绝不进入仓库
- 跨机器同步 = 跑 `scripts/setup_mcp.py` + WorkBuddy MCP 管理页对每个 server 点 Trust
