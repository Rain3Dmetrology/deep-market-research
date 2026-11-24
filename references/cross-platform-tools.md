# 跨平台可选工具接入指南

> 本文件只说明可选工具的**接入方法和平台差异**。何时调用、如何分类、默认路由和证据规则，以 references/data-sources.md 为唯一权威。

## 0. 通用原则

1. **路由与接入分离**：本文件不定义 Provider 排名，也不要求安装清单中的所有工具。
2. **单 owner 默认**：每个广域查询簇先选一个 owner；只有明确证据缺口、时效问题、来源冲突或用户要求时才增加第二个。
3. **专业源按需并行**：官方披露、论文、专利、法律、GitHub 原始记录和 UGC 是不同证据域，不属于重复广域搜索。
4. **能力分别调用**：Search、Extract / Crawl、Research Agent、Browser Automation 和 Aggregator 不互相替代；同一任务不叠加多个功能等价工具。
5. **优雅降级**：工具未连接、无凭据或失败时跳过并记录未覆盖项，不阻断 DMR 主流程。
6. **费用与数据边界**：计费调用前确认预算；托管聚合器不得接收未经授权的私有代码、凭据或客户数据。
7. **接入事实需复核**：下方平台配置是接入示例，不保证当前账号权限、额度或供应商接口未发生变化。

## 1. 按能力查找接入说明

| 能力 | 可选工具 | 路由约束 |
|---|---|---|
| 广域搜索 / 索引补充 | Exa、Octen、Metaso、Bocha、Tavily Search、SerpAPI、Search1API、AnySearch | 每个查询簇默认一个；Search1API 是网关 / 引擎回退，不按兼容端点重复计源；AnySearch 保持试点。 |
| 专业证据 | SEC、FRED、学术 API、专利 / 法律数据库、GitHub API / MCP、平台原生数据 | 按必需证据域直接查询，可与广域发现并行。 |
| 正文提取 / 站点采集 | Firecrawl、Tavily Extract / Crawl / Map、Exa Contents、ReadGZH | 先有 URL 或明确站点采集需求；同一内容任务先选一个提取器。 |
| 动态页面 / 研究代理 | TinyFish、Tavily Research、Perplexity Agent | 需要浏览器交互或多步综合时再启用；每个研究任务最多一个研究代理。 |
| 工具聚合 | AgentKey；AgentEarth（观察） | 默认关闭；直连来源不足时才考虑，调用前核对上游、费用和数据流向。 |
| 社媒 / UGC | agent-reach、知乎 MCP、平台专用工具 | 仅在用户体验、社区反馈或情绪信号是必需证据域时启用；不替代 T1 官方证据。 |

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

**注意**：抖音/公众号 agent-reach **无独立频道**（可选频道仅 twitter/reddit/facebook/instagram/小红书/小宇宙/雪球/LinkedIn/bilibili）。抖音按任务使用平台专用工具或广域搜索；公众号必须先通过发现渠道取得原文 URL，再用 ReadGZH 提取正文。不要把“搜索引擎命中公众号页面”误记为已取得全文。

**同类方案评估记录 · karnstack/reins（2026-08-29 核验）**：
- 基本情况：MIT 许可；npm 包 `@karnstack/reins`（latest 0.4.0，维护者 karngyan，首发 2026-07-04）；支持 Chrome/Brave/Edge/Arc/Dia；README 明示 127.0.0.1-only 绑定 + 逐站点权限 + 威胁模型文档（"Host 头校验防 DNS rebinding"与"仅接受 chrome-extension:// 来源"两项机制未见于 README，标注为文档声称、未核验）。
- 与 OpenCLI 桥对比：同为「本地守护进程 + 浏览器扩展」复用登录态的浏览器桥；Reins 浏览器覆盖面更广（含 Arc/Dia）且安全模型文档化更完整；OpenCLI 桥已在本环境实测跑通 6 社媒频道（2026-07-23，见上文），是当前 agent-reach 社媒层的工作路径。
- 结论：**列为观察项，不进默认安装脚本，不预设替换**。现桥正常工作则无迁移动作；仅在需扩展 Arc/Dia 等浏览器或强化安全模型时再评估试点（试点亦不写入默认安装，守护零安装定位）。
- 同类观察项补充 · **Real Browser MCP**（2026-08-29 核验）：`github.com/ofershap/real-browser-mcp`——MIT 许可；本地 MCP 服务 + Chrome MV3 扩展 + localhost WebSocket 桥，18 工具；定位为**复用已登录 Chrome** 的浏览器自动化。与 Reins 同属「本地进程 + 浏览器扩展」桥型，与既有 OpenCLI 桥能力重叠 → **同列观察项，不进默认安装**。

**同类方案评估记录 · AgentEarth（2026-08-29 实测）**：
- 基本情况：agentearth.ai——1519 工具（金融类 524）；**X-Api-Key REST 聚合协议（非 MCP）**；积分制计费（1 USD = 1000 Credits）；页头 BETA 角标；无运营主体署名（RDAP：GoDaddy 2025-10-23 注册，Domains By Proxy 隐私保护）。
- 风险信号：外部宣传的 `pip install agentearth-sdk` 在 PyPI 404（外部宣传存疑）。
- 结论：**暂不收编、列为观察项**——主体匿名 + 计费不透明 + 宣传与实测不符，不满足可选源准入；仅保留本记录供季度复核。

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

### 2.z AgentKey（闭源商业 SaaS · 仅 MCP 接入 · 可选兜底）

> 定位：工具聚合平台（find_tools → describe_tool → execute_tool 三段式），约 2000 工具（官方口径 "2,000+"，**2026-08-29 凭据直测实测 1981**，11 个顶层节点）：社交 1213（25 个子平台）/ 金融 311 / 链上 179。上游转发已实测点名 search = brave/exa/parallel/perplexity/serper/tavily、scrape = brightdata/firecrawl/jina。

**事实卡（按 2026-08-29 官方凭据直测修正，非第三方转述）**：
- 出品：Chainbase（terms 条款 Contact 款：Chainbase Technology Holdings Pte. Ltd.，新加坡主体）；与阿里云百炼的业务空间标识“AgentKey”同名无关。
- 性质：**闭源商业 SaaS**——无 MIT 许可、无公开版本号（早期引用材料中的 “MIT / v1.14.0” 已经直测证伪剔除）。
- 计费：订阅外壳 + 积分按量混合——免费档赠 10 积分；Lite/Pro/Max 月订阅含月度积分、可加购、不滚存。免费额度有限（实测 key 已耗 65%、余 3.5 积分），实际数据调用需付费档。
- 接入：**仅 MCP**（Streamable HTTP，JSON-RPC 2.0 标准 initialize/tools/list 握手，返回 `mcp-session-id` 会话头）；无 REST/文档面，常规探测路径全部 404。
- 时效限定（截至 2026-08-29 实测）：社交类目中 linkedin/threads 官方健康探测自报不健康，引用需加时效限定；`list_tools` 已标注废弃。
- 健康监控：`sources.registry.yaml` 已登记（optional 层，`probe_type: mcp`），探活走最小 `initialize` 握手（不消耗积分）；无凭据时 SKIPPED。

**路由去重纪律**：搜索/抓取意图**优先直连**已配置工具（exa/tavily/firecrawl 等），AgentKey 仅作未配置直连时的兜底或社媒类目命中时触发；默认关闭、显式开启。防止同一上游经 AgentKey 转发重复调用与订阅开销（其上游即上述已有工具）。

**配置**（`$AGENTKEY_API_KEY` 仅本地环境变量提供，绝不写入仓库）：
```json
{
  "mcpServers": {
    "agentkey": {
      "url": "https://api.agentkey.app/v1/mcp",
      "headers": { "Authorization": "Bearer ${AGENTKEY_API_KEY}" }
    }
  }
}
```


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
