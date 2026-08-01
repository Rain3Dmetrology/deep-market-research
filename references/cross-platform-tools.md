# 跨平台可选工具接入指南（deep-market-research v2.3.1）

> 本文件是 `SKILL.md` 的**可选补充**。核心调研流程（Step 0–8 + 三-B 深度研究闭环）**零依赖、零安装**即可运行，只用 LLM 内置 `web_search` / `web_fetch` + 🆓 免费 REST API。
> 本文档仅说明：如何为**有需要的用户**在各自平台上接入**可选增强工具**以丰富素材来源。
> **缺失任何工具都不影响主流程**——未接入则自动回退默认层，输出质量不降。

---

## 0. 通用原则

1. **可选 ≠ 必需**：所有工具仅作素材源增强；主检索永远由内置搜索 + 免费 API 兜底（基座始终并行调用，增强层并行叠加，结论以 Step 4 交叉验证裁决）。
2. **优雅降级**：某工具未配置 / 无 key / 调用失败 → 跳过并在报告注明"未覆盖该维度"，绝不报错中断。
3. **不绑死平台**：SKILL.md 主管线不引用任何平台的 MCP 文件名、agent-team 协议或专有后端。换平台无需改技能。
4. **远程优先**：优先用官方远程 MCP（URL 形式，零安装）；本地进程仅作"最强深度"可选项。
5. **交叉验证来源**：下列免费额度为 2026-07 通过多家第三方定价聚合站 + 官方文档交叉验证后的快照；搜索 API 季度漂移，生产前请回源官网复核。

---

## 1. 可选工具清单（按推荐层级分类）

> 推荐层级：🥇 首选（keyless 零配置）· 🥈 备选 · 🥉 备选 · 🛟 兜底（缺 key 也能跑）· 🎯 个性化（需 key / 账号 / 特定平台）· ⚠️ 不推荐通用。免费额度为 2026-07 交叉验证快照，搜索 API 季度漂移，生产前请回源官网复核。

### 1.1 默认层 · 零依赖零安装（质量基座 · 🛟 兜底）

| 工具 | 能力 | 接入方式 | 费用 | 推荐层级 | 备注 |
|------|------|----------|------|----------|------|
| LLM 内置搜索 | 通用网页搜索 / 网页抓取 | 无需配置 | 含模型订阅/额度 | 🛟 兜底（基座） | 各平台实现不同，质量取决于模型 |
| 免费 REST API | 学术/代码/开放数据 | 直调 OpenAlex / arXiv / Crossref / GitHub API 等 | 免费 | 🛟 兜底（基座） | 优先用于论文、DOI、开源项目 |
| DuckDuckGo | 通用网页搜索 | 社区 MCP（stdio）或 WebFetch | 免费、免 key | 🛟 兜底 | HTML 前端抓取，无 SLA，偶发解析失效；低频兜底 |

### 1.2 可选增强层 · 按需接入

| 工具 | 能力 | 接入方式 | 免费额度（2026-07 交叉验证） | 推荐层级 | 备注 |
|------|------|----------|------------------------------|----------|------|
| Firecrawl | 网页抓取 / 搜索 / 页面交互 | 远程 MCP `https://mcp.firecrawl.dev/v2/mcp`（keyless）或 API key | keyless 1,000 积分/月 | 🥇 首选 | 官方 keyless MCP，开箱即用；额度耗尽可绑 key |
| DeepWiki | GitHub 仓库研究 | 远程 MCP `https://mcp.deepwiki.com/mcp`（keyless） | 免费（仅公共仓库） | 🥇 首选 | Cognition 官方，免登录；技术仓库调研极有价值 |
| Exa | 神经/垂直索引搜索 | 远程 MCP `https://mcp.exa.ai/mcp` 需 API key | 1,000 请求/月（免费层） | 🥈 备选 | 神经搜索质量高；免费层较小 |
| Tavily | AI 搜索 API | 远程 MCP `https://mcp.tavily.com/mcp` 或 API key | 1,000 积分/月 | 🥈 备选 | 2026-02 被 Nebius 收购（$275M–$400M），长期独立性待观察 |
| Brave Search | 独立索引搜索 | API key 直调 | $5 月度赠金 ≈ 1,000 次 | 🥉 备选 | 独立索引、隐私优先；需绑卡/验证 |
| Novada | 网页搜索/SERP/抓取/提取/地图/爬取/深度研究（25+ 工具） | 托管 Streamable-HTTP MCP，`npx novada-mcp` | 免费 1,000 次/月 | 🥈 备选 | 新兴 SaaS，免安装，覆盖 195 国；长期可用性待观察 |
| Novada Web Unblocker | 住宅代理 / 反爬解锁，抓取地理封锁 / 反 bot 受保护的页面 | 代理网关（用户名+密码，或 `NOVADA_API_KEY`）| 付费（按流量）| 🛟 兜底（解锁层）| 与 Firecrawl 反爬能力部分重叠；Firecrawl 已覆盖多数解锁场景。仅作「Firecrawl/WebFetch 仍被墙」的兜底解锁层，不进核心管线；key 本地仅存 |
| SearXNG | 元搜索引擎（多引擎聚合） | 自托管实例 / 公共实例 MCP | 免费、免 key（自托管） | 🛟 兜底（自托管 keyless） | 元搜索聚合；需自托管或可信公共实例 |
| Perplexity Sonar | 带引用一站式答案 | API key 直调 | 无永久免费层；Pro 订阅含 $5/月 API 额度 | 🎯 个性化 | 答案质量高，成本随 token 叠加；非纯免费场景 |
| ModelScope 魔塔 | 中文模型/数据集/推理 | API token 直调 | 2,000 次/天（需阿里云账号 + 实名认证） | 🎯 个性化 | 国内首选；适合 Qwen/DeepSeek 等中文模型推理 |
| AnySearch | 统一实时搜索（23 垂直领域） | 远程 MCP `https://api.anysearch.com/mcp`（keyless 匿名）或 API key | 匿名 1,000 次/天；免费 key 更高 | 🎯 个性化 | 新兴工具，垂直领域有特色；质量稳定性待验证。**⚠️ 已评估：与 exa/tavily/firecrawl 通用搜索高度重叠，不进核心管线；本地未装 skill（仅存 anysearchAPIKEY.txt），仅作匿名兜底可选** |
| 秘塔搜索 Metaso | 中文 AI 搜索 / 学术搜索 | Web 免费；API 按次计费 | Web 搜索免费；API 约 ¥0.03/次，新用户 50 次试用 | 🎯 个性化 | 中文搜索体验好；API 非免费，轻量 CN 增强 |
| Connected Papers | 论文关联图谱 / 引文网络（S2 ShaID → 研究邻里图） | API key（`connectedpapers-py` 客户端）| 早期访问，限量（用户 key 余 ~50 次图谱构建，5 次/分钟）| 🎯 个性化 | 与 dmr 既有 S2/OpenAlex 引文覆盖重叠；仅作深度技术尽调可选源，**不进核心管线**；key 本地仅存 |
| FRED（美联储经济数据） | 美国经济/金融**结构化时间序列**（GDP/CPI/利率/就业/M2 等 80 万+ 系列） | API key 直调 `api.stlouisfed.org`（或 `scripts/fred_query.py`）| 免费、官方、无限额（需免费 api_key）| 🥈 备选【建议采纳】 | 官方权威宏观数据源，补 dmr **结构化经济数据空白**（exa/tavily 是搜索、非结构化）；免费稳定，强烈建议作为金融/经济深度研究核心可选源；不进核心管线（主流程零依赖），作增强层 |
| ReadGZH-Agent | 微信公众号**全文**提取（标题/作者/时间/正文 Markdown，50–87% Token 压缩） | 远程 MCP `https://api.readgzh.site/mcp-server`（keyless；Pro 需 Bearer） | 30 次/日免费（注册领取）；Pro ¥39/月 2000 次 | 🥇 首选（公众号全文） | 99.89% 反爬穿透、零安装、永久缓存；与 `wechat-article-search` **互补**（后者只搜元数据，本工具提全文）。缺失→回退 web_search。文章全球共享缓存，勿提交私密链接；AGPL-3.0（自托管须开源）；国内访问需实测 |
| midu-hotsearch | 抖音/微博/百度/知乎/今日头条等 **30+ 平台热搜/榜单** | WorkBuddy 技能市场安装（原生 skill） | 免费（但新版蜜度 API 已不兼容）| ❌ **已弃用** | **新版 midu.com 蜜度 API 改用 OAuth（client_id+client_secret→token）且需付费/申请接口权限**，与原 skill 单 key 鉴权不兼容；剩余权限 0 + 错误码 202005/203003 双重卡死。**替代见 § 2.y**：抖音热榜用 `douyinmcp.get_homefeed`（已 8/8 活）、财经热榜用 wallstreetcn（免费无 key）、综合用 web_search+zhihu MCP。不进核心管线 |
| douyinmcp | 抖音**深度内容 + 热榜**（搜索/视频详情/评论/用户/首页流 + `get_homefeed`） | 本地 MCP（需 `cookies.txt` 登录 Cookie + `a_bogus` 本地 V8 签名） | 免费（需自维护 Cookie） | 🎯 个性化（抖音深度 + 热榜） | 本地 `py_mini_racer` 生成 `a_bogus` 签名，免外部签名服务；需有效抖音登录 Cookie（频繁失效）+ Python 3.14+/uv。Cookie 含敏感信息，只存本地，绝不进云端。**优先免费方案**；规模化稳定需求见 TikHub。**🆕 `get_homefeed` 工具可作抖音实时热榜信号源（已 8/8 工具激活，替代 midu 的抖音维度）** |
| wallstreetcn（华尔街见闻） | **实时财经热榜/要闻/快讯**（A股/美股/港股/全球/外汇/黄金/原油/数字货币等 5+ 频道） | REST API `https://api-one.wallstcn.com/apiv1/content/{articles,lives,hots,hot-rank}?channel=...&limit=...` | 免费、免 key、无频率声明 | 🛟 兜底（财经热榜信号）| 2026-07 实测 5 频道 + 4 端点全 HTTP 200，实时数据（文章/快讯/热榜）。**替代 midu-hotsearch 的金融维度**，中文财经研究首选；与 douyinmcp 互补（抖音用 douyinmcp、财经用本源）。不进核心管线 |
| TikHub API | 微信+抖音**结构化数据**（公众号文章+阅读数/赞/评论；抖音视频/评论/搜索/榜单/星图） | REST API（`api.tikhub.io`，大陆用 `api.tikhub.dev`） | $0.001/请求（首充 $0.05≈50 次） | 🎯 个性化（稳定契约） | 付费但稳定（99.9% SLA，10 RPS），免中国开发者资质；主域大陆被墙→用 `.dev`。key 本地仅存。**优先用免费 douyinmcp/ReadGZH**，规模化/高稳定需求再上 TikHub |

### 1.3 不推荐 / 仅特定场景

| 工具 | 推荐层级 | 原因 |
|------|----------|------|
| GPT Researcher（本地进程） | ⚠️ 不推荐通用 | 需 git clone + pip install + 多 API key，依赖重、启动慢；仅高级用户在独立 venv/容器部署 |
| local-deep-researcher / local-deep-research | ⚠️ 不推荐通用 | 依赖本地 Ollama/LMStudio，与"零本地、泛化优先"定位冲突；仅涉密/离线场景单独考虑 |
| agent-browser | 🎯 平台专有（已评估） | WorkBuddy 专有浏览器自动化。**抓取/JS 渲染能力与 Firecrawl 重叠且更重**（需 Chromium 500MB+GUI daemon、冷启慢、非无头）。dmr 场景下 Firecrawl 更优 → **不进核心管线**，仅保留为「需登录/点击/表单的交互式高墙源」最后兜底 |
| agent-reach | 🎯 平台专有（已评估·建议采纳为可选社媒层） | WorkBuddy 专有 15 频道聚合（实测 **6 社媒**：Twitter/X·Reddit·Facebook·Instagram·Bilibili·小红书 + **5 基础**：GitHub·V2EX·RSS·Web·YouTube + **3 可选未装**：小宇宙·雪球·LinkedIn）。**覆盖 8 个 MCP + 默认层均未触及的社媒/草根另类数据**，对深度市场研究情绪/趋势信号价值高 → 建议采纳为可选社交/UGC 增强层。注意：(a) 默认 `disable:true`，需改元数据 `disable:false` 并 `agent-reach doctor` 配置频道；(b) 其 Exa/web 频道与现有 exa/tavily/firecrawl 冗余——只取其社媒频道；(c) 社媒频道经 **OpenCLI 浏览器桥**复用 Chrome 登录态（无需导 cookie / 关浏览器；Windows 需修 `localhost`→IPv4 解析，见 2.1.1）；(d) **抖音/微博 非 agent-reach 频道**——走默认 web_search 兜底；**公众号走 wechat-article-search skill**（非 agent-reach）；(e) 不进核心管线 |


---

## 2. 平台接入速查

### 2.1 WorkBuddy

**远程 MCP（零安装，推荐）**：编辑 `~/.workbuddy/mcp.json`（或 `.mcp.json`）加入：

```json
{
  "mcpServers": {
    "firecrawl": { "url": "https://mcp.firecrawl.dev/v2/mcp" },
    "deepwiki":  { "url": "https://mcp.deepwiki.com/mcp" },
    "exa":       { "url": "https://mcp.exa.ai/mcp",
                    "headers": { "Authorization": "Bearer ${EXA_API_KEY}" } },
    "tavily":    { "url": "https://mcp.tavily.com/mcp",
                    "headers": { "Authorization": "Bearer ${TAVILY_API_KEY}" } }
  }
}
```

**API key 直调**（Brave / Perplexity / ModelScope）：在环境变量或配置中提供 key，技能按 `BRAVE_API_KEY` / `PERPLEXITY_API_KEY` / `MODELSCOPE_API_KEY` 等探测。

**WorkBuddy 专有 skill**（非跨平台，本地已装）：
- `agent-browser`：浏览器自动化。**与 Firecrawl 重叠且更重，不进 dmr 核心管线**；仅作需交互/登录的高墙源兜底。
- `agent-reach`：**建议采纳为可选社媒/UGC 增强层**（实测 6 社媒：Twitter/Reddit/Facebook/Instagram/Bilibili/小红书 + 5 基础：GitHub/V2EX/RSS/Web/YouTube；**抖音/微博 走 web_search 兜底，公众号走 wechat-article-search skill**）。默认 `disable:true`，需改 `disable:false` + `agent-reach doctor` 配频道；只取其社媒频道（Exa/web 频道冗余已有）。**实战配置见 [2.1.1](#2111-agent-reach-社媒频道实战opencli-浏览器桥)**。

### 2.1.1 agent-reach 社媒频道实战（OpenCLI 浏览器桥）

> 经验结论（2026-07-23 实测）：社媒频道**不要走 cookie 导出路**（Chrome cookie DB 被 SQLite 锁 + DPAPI 需管理员 + rookiepy 需 Rust，全部阻塞）。**正确路径是 OpenCLI 浏览器桥**——直接复用你 Chrome 当前登录态，无需关浏览器、无需导 cookie。

**架构**：OpenCLI = Chrome 扩展（客户端）+ 本地守护进程（WebSocket 服务端，固定端口 `127.0.0.1:19825`）。社媒频道（Twitter/Reddit/Facebook/Instagram/Bilibili/小红书）经 OpenCLI 复用浏览器登录态。

**安装与连通步骤**：
1. 装 agent-reach CLI：`pip install https://github.com/Panniantong/agent-reach/archive/main.zip`（建议隔离 venv）
2. `agent-reach install --env=auto` → 零配置 5 频道（GitHub/V2EX/RSS/Web-Jina/Bilibili basic）
3. `agent-reach install --channels=twitter,reddit,facebook,xiaohongshu,instagram` → 装 OpenCLI 等后端
4. Chrome 装 **OpenCLI 扩展**（Chrome Web Store 搜 `opencli`）
5. **关键修复**：若扩展显示 `Reconnecting...` / daemon 报 `Extension: disconnected`，根因是 **Windows `localhost` 解析为 `::1`(IPv6) 优先，而 daemon 只绑 IPv4 `127.0.0.1:19825`**。修复（管理员 PowerShell 一次）：
   ```powershell
   Add-Content -Path "$env:SystemRoot\System32\drivers\etc\hosts" -Value "`n127.0.0.1 localhost" -Encoding ASCII
   ```
   改完扩展自动重连 → `Connected`。**无需重装扩展、无需重启 Chrome**。
6. 验证：`opencli doctor`（应 `[OK] Extension: connected`）+ `agent-reach doctor`（应 `10/15 渠道可用`）

**实测结果（2026-07-23）**：Twitter/Reddit/Facebook/Instagram/Bilibili/小红书 全部返回真实数据；doctor 终态 `10/15 渠道可用`（5 基础 + 6 社媒）。

**注意**：抖音/公众号 agent-reach **无独立频道**（可选频道仅 twitter/reddit/facebook/instagram/小红书/小宇宙/雪球/LinkedIn/bilibili），其内容由 exa/tavily/firecrawl 通用检索覆盖，不构成硬缺口。

### 2.x 公众号全文提取（ReadGZH-Agent · 可选 MCP）

> 定位：dmr 已引用 `wechat-article-search` skill 做**公众号文章搜索**（返回标题/摘要/时间/账号/链接，**不含全文**）。本工具补齐**全文提取**缺口，二者互补、不重叠。缺失则回退 `web_search`。

**ReadGZH-Agent**（远程 MCP，零安装）：
- 端点：`https://api.readgzh.site/mcp-server`（HTTP 传输，URL 即连，无需 Docker / 浏览器）
- 4 个工具：`readgzh.read`（URL 抓全文）/ `readgzh.search`（搜已缓存）/ `readgzh.list`（最近缓存）/ `readgzh.get`（按 slug 取）
- 能力：99.89% 反爬穿透、50–87% Token 压缩、永久缓存（首次抓取后零成本复读）、支持图文（小绿书）格式
- 费用：30 次/日免费（注册领取）；Pro ¥39/月 2000 次（含 AI 摘要）
- 配置（WorkBuddy `~/.workbuddy/mcp.json`）：

```json
{
  "mcpServers": {
    "readgzh": {
      "url": "https://api.readgzh.site/mcp-server",
      "headers": { "Authorization": "Bearer ${READGZH_API_KEY}" }
    }
  }
}
```

> `${READGZH_API_KEY}` 仅本地环境变量 / 配置提供，**绝不写进仓库 / SkillHub**。免费档无需 key，但匿名限额更低（10/IP/日）。
> 风险：文章**全球共享缓存**（勿提交私密 / 敏感链接）；AGPL-3.0（自托管须开源）；国内访问需实测。与 `wechat-article-search` 互补——搜索用 skill、全文用本 MCP；任一缺失 → `web_search` 兜底。

### 2.y 抖音 / 财经热榜检索（douyinmcp / wallstreetcn / TikHub · 可选）

> 定位：抖音反爬极严（`a_bogus` 签名），`web_search` 覆盖弱；财经热榜是结构化市场情绪信号，web_search 覆盖不全。dmr 路由到下列可选工具增强；**优先免费**，缺失则回退 `web_search`。
> ⚠️ **midu-hotsearch 已弃用**：新版 midu.com 蜜度 API 改用 OAuth（client_id+client_secret→token）且需付费/申请接口权限（剩余权限 0 + 错误码 202005/203003），与原 skill 单 key 鉴权不兼容。其"抖音热榜"能力由 **douyinmcp.get_homefeed** 替代，"财经热榜"由 **wallstreetcn** 替代，其他平台走 web_search + zhihu MCP。

**① wallstreetcn（华尔街见闻 · 免费 · 财经热榜信号）**
- 能力：实时财经热榜 / 要闻 / 快讯，5+ 频道（A股 / 美股 / 港股 / 全球 / 外汇 / 黄金 / 原油 / 数字货币）
- 端点：`https://api-one.wallstcn.com/apiv1/content/{articles,lives,hots,hot-rank}?channel=<频道>&limit=<N>`
- 费用：免费、免 key、无频率声明（2026-07 实测 5 频道 + 4 端点全 HTTP 200）
- 用途：财经 / 市场情绪热榜信号，中文财经研究首选；**替代 midu-hotsearch 的金融维度**

**② douyinmcp（本地 MCP · 免费 · 抖音深度 + 热榜）**
- 能力：搜索视频 / 视频详情 / 评论 / 子评论 / 用户信息 / 用户作品 / 首页流（8 工具）
- 🆕 `get_homefeed` = 抖音首页推荐流，即**实时热榜信号**（已 8/8 工具激活，替代 midu-hotsearch 的抖音维度）
- 机制：内置 `py_mini_racer`（V8）本地生成 `a_bogus` 签名，免外部签名服务
- 依赖：有效**抖音登录 Cookie**（`cookies.txt`）+ Python 3.14+ / uv
- 风险：Cookie 频繁失效、签名随平台更新可能失效（持续维护负担）；**Cookie 含敏感信息，只存本地，绝不进云端**

**③ TikHub 抖音 API（REST · 付费 · 稳定契约 · 规模化备用）**
- 能力：视频 / 评论 / 搜索 / 热榜 / 星图（创作者市场）/ 电商，结构化 JSON
- 费用：$0.001/请求（首充 $0.05≈50 次）；10 RPS 默认
- 端点：`https://api.tikhub.io`（大陆用 `https://api.tikhub.dev`，主域被墙）；key 本地仅存
- 适用：免费方案（douyinmcp）维护成本过高、或需高稳定 / 大规模时再上

**配置（douyinmcp · 本地 MCP）**：
```json
{
  "mcpServers": {
    "douyinmcp": {
      "command": "uv",
      "args": ["--directory", "/abs/path/to/douyinmcp", "run", "douyin-mcp-server"],
      "env": { "DOUYIN_COOKIE": "${DOUYIN_COOKIE}" }
    }
  }
}
```
> Cookie / key 仅本地；缺失任一工具 → 回退 `web_search`，不中断主管线。


### 2.2 Claude（Claude CLI / Desktop）

**远程 MCP**：

```bash
claude mcp add firecrawl --transport http https://mcp.firecrawl.dev/v2/mcp
claude mcp add deepwiki  --transport http https://mcp.deepwiki.com/mcp
```

需 key 的工具：

```bash
claude mcp add exa --transport http https://mcp.exa.ai/mcp --header "Authorization: Bearer ${EXA_API_KEY}"
claude mcp add tavily --transport http https://mcp.tavily.com/mcp --header "Authorization: Bearer ${TAVILY_API_KEY}"
```

**API key 直调**：在对话中提供 `EXA_API_KEY` / `TAVILY_API_KEY` / `PERPLEXITY_API_KEY` 等，或写入 shell profile 供 Claude Code 读取。

---

### 2.3 Codex（OpenAI Codex CLI）

Codex CLI 支持 MCP 配置（与 Claude 类似）。

**远程 MCP**：在 Codex 的 MCP 配置（通常 `~/codex/config.toml` 或 `--mcp` 参数）中加入上述 URL。

**API key 直调**：Codex 原生可读取 `OPENAI_API_KEY`；其他 key 通过环境变量注入。

---

### 2.4 Trae（字节 Trae IDE）

Trae 支持 MCP 设置面板 / 配置文件（`~/.trae/mcp.json` 或项目内）。

**远程 MCP**：在 MCP 设置中添加 Firecrawl / DeepWiki / Exa / Tavily 的 URL（HTTP 传输）。

**API key 直调**：在 Trae 设置或环境变量中提供 key。

---

### 2.5 qoder（阿里云 qoder）

qoder 技能目录位于 `~/.qoder/skills/`，MCP 配置见其设置。

**远程 MCP**：在 qoder 的 MCP 配置中加入上述 URL。

**API key 直调**：通过环境变量或 qoder 设置面板提供。

---

### 2.6 Cursor

Cursor 通过项目根目录 `.cursor/mcp.json` 或全局 `~/.cursor/mcp.json` 配置 MCP。

**远程 MCP**：

```json
{
  "mcpServers": {
    "firecrawl": { "url": "https://mcp.firecrawl.dev/v2/mcp" },
    "deepwiki":  { "url": "https://mcp.deepwiki.com/mcp" },
    "exa":       { "url": "https://mcp.exa.ai/mcp",
                    "headers": { "Authorization": "Bearer ${EXA_API_KEY}" } },
    "tavily":    { "url": "https://mcp.tavily.com/mcp",
                    "headers": { "Authorization": "Bearer ${TAVILY_API_KEY}" } }
  }
}
```

**API key 直调**：在 Cursor 设置或 `.env` 中提供 key，技能按环境变量探测。

---

## 3. 降级与故障处理

| 场景 | 处理 |
|------|------|
| 远程 MCP 不可达 | 跳过该工具，回退内置搜索 + 免费 API；报告注明未覆盖 |
| API key 缺失 / 失效 | 跳过该工具，回退默认层；不报错 |
| keyless 额度耗尽 | 自动切换需 key 工具或回退默认层 |
| 本地进程未装 / 启动失败 | 回退纯提示词深度研究闭环（三-B），质量不降 |

> **关键认知**：本技能的质量由 Step 0–8 + 三-B 闭环的方法论保证，而非由某个搜索 API 决定。即使所有可选工具都缺失，输出仍是带源分级、交叉验证、置信标签的可复现报告。可选工具只是"更快 / 更广 / 更深"的加速器。

---

## 4. 安全与隐私提示

- 远程 MCP 的 keyless 端点（Firecrawl / DeepWiki）无需任何密钥，复制 URL 即用。
- 需 key 的工具：key 只存在你本机环境变量 / MCP 配置中，**不要**写进 SKILL.md 或提交到仓库。
- 本地进程（GPT Researcher / ModelScope 服务端）仅在你本机运行，数据不出本地（若用云端 LLM key 则检索/生成走云端，符合"非涉密"前提）。
- 涉密 / 隐私敏感调研请走纯本地 LLM（Ollama 等）方案，本技能默认云端路径不假设该场景。
