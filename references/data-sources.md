# DMR 搜索路由与多信息源目录

> **唯一权威路由目录。** 本文件定义“什么任务用什么能力、何时扩源、如何判断证据独立”。
> cross-platform-tools.md 只记录各平台的接入方式；sources.registry.yaml 只服务于健康探针，不是路由排名表。

## 1. 路由原则

1. **先看目标市场，再看查询语言。** 中文提问不等于只查中国；按研究对象、业务范围和证据所属市场选 CN / Global。
2. **每个广域查询簇默认一个 owner。** 优先宿主内置 web_search；需要专用索引时，从候选中选一个最匹配的，不把已连接工具全部并发。
3. **第二个广域 owner 必须有理由。** 仅在首轮遗漏必需证据域、独立发布者过少、时效不足、关键事实冲突或用户明确要求独立交叉发现时追加。
4. **专业证据域可以并行。** 官方披露、监管数据、论文、专利、法律资料、GitHub 原始记录和 UGC 是不同任务，不因有一个广域 owner 而禁止调用。
5. **发现、读取、综合、聚合是不同能力。** 搜索命中是线索；提取器读取已知 URL；研究代理执行多步研究；聚合器转发第三方工具。它们不能混成“多一个搜索源”。

## 2. 能力分类

| 能力类别 | 代表工具 / 来源 | 正确定位与调用规则 |
|---|---|---|
| **广域发现** | 宿主 web_search；Metaso Web、Bocha Web、Octen Search / Broad、Exa Search、Tavily Search、TinySearch、Brave Search、DuckDuckGo、AnySearch（垂直试点） | 默认只选一个 owner。CN 可从 Metaso / Bocha 中择一；Global 可从 Octen / Exa 中择一；Tavily / Brave / DuckDuckGo / Novada 仅在任务适配时补位，不构成固定并行组。AnySearch 仍是垂直检索试点。 |
| **引擎 / 网关回退** | Search1API（如 Baidu）、SerpAPI（Google / Bing / Baidu） | 需要指定 SERP 引擎、主入口缺失或诊断时才用。Search1API 是网关，不按兼容端点数量重复计 Provider；其 OAuth 由 Magpie 管理，不复制到通用环境变量。bingcn 因已有低相关样例暂不进入默认路由，不宣告整个服务失效。 |
| **垂直与一手证据** | SEC EDGAR、FRED、企业 IR、政府 / 监管 / 统计机构、OpenAlex、Semantic Scholar、Crossref、OpenCitations、arXiv、PubMed、USPTO / EPO / WIPO、GitHub API / MCP | 按必需证据域直接查询，可与一个广域 owner 并行。SEC / FRED 是结构化数据，不是搜索引擎；SEC User-Agent 是访问身份标识。DeepWiki 用于公开仓库导航，版本事实仍回到不可变 commit、原始文件、PR 或 CI。 |
| **社区 / UGC** | 知乎、Reddit、Hacker News（HN）、Stack Overflow、CSDN、小红书、B 站、X 等；已接入的 agent-reach 社媒频道 | 用于痛点、体验、技术讨论与反方线索。匿名 UGC 通常按 T4 信号处理；多个搜索工具重复发现同一帖子不构成独立佐证。 |
| **正文提取 / 站点采集** | Firecrawl Scrape / Extract / Map / Crawl（Search 仅按需）、Tavily Extract / Crawl / Map、Exa Contents、TinyFetch、ReadGZH | 已知 URL 后选择一个提取器；失败或覆盖不足再换另一个。ReadGZH 只用于已取得的 canonical mp.weixin.qq.com 原文 URL；其缓存搜索不等于全网公众号发现。 |
| **研究代理 / 浏览器执行** | Exa Agent、Tavily Research、Perplexity Sonar / Agent、TinyAgent / TinyBrowser、GPT Researcher；agent-browser / web-access | 研究代理负责多步搜索与综合，浏览器执行器负责动态页面或交互。只有任务确实需要时启用；同一研究任务最多选一个研究代理，不与 Broad Search 无条件叠加。GPT Researcher 等本地重型方案不进通用默认管线。TinyFish 的 Search、Fetch、Agent、Browser 按能力分别归类，不将整个品牌整体视作单一搜索源。 |
| **元搜索 / 多引擎聚合** | SearXNG（优先可信自托管实例） | 汇总多个上游时可作为单一发现入口或特殊环境兜底；不得与多个上游搜索再叠加，也不能把转发结果重复计为独立来源。 |
| **多功能托管平台** | Novada 的 Search / SERP / Extract / Crawl / Map 等工具 | 只在明确能力缺口时选其中一个工具；先核对其实际上游和数据路径，不默认并发整个工具集，也不将转发结果视为独立索引。 |
| **工具聚合器** | AgentKey；AgentEarth（观察项） | 默认关闭。只有直连来源不能覆盖所需专业域时才考虑；调用前核对上游、费用、数据流向并取得必要授权。记录真实上游；聚合器本身不是独立证据来源。 |

## 2.1 专业证据域索引

| 证据域 | 来源目录 | 用途与边界 |
|---|---|---|
| 公司 / 市场 / 财务 | 公司 IR、SEC EDGAR、国家统计局、央行 / 证监会、FRED、Trading Economics；A 股通达信 F10 / westock；华尔街见闻、财联社 | 官方披露与结构化指标优先；新闻热榜只提供线索，不替代财报和原始数据。 |
| 法律 / 专利 / 企业风险 | 威科先行、元典、北大法宝；Google Patents、USPTO、EPO、WIPO、PatSnap；天眼查、企查查、启信慧眼 | 法规、裁判文书、专利原文和企业登记信息按具体司法辖区 / 数据所有者选择；付费库需平台授权。 |
| 学术 / 引文 / 科研数据 | OpenAlex、Semantic Scholar、arXiv、PubMed、bioRxiv、Europe PMC / EMBL-EBI；Crossref、OpenCitations；Zenodo、Figshare、Harvard Dataverse、NASA | 元数据、论文、引用关系和数据集分开处理；结论引用论文或数据原文。Nature / Science 以 DOI 溯源；CNKI / Google Scholar 仅使用可合法访问或用户导出的资料。 |
| 代码 / 模型 / 开发者 | GitHub API / MCP / gh、DeepWiki、Hugging Face Hub、ModelScope；Stack Overflow、Hacker News、CSDN | GitHub 原始仓库 / commit / issue / PR 是版本事实来源；DeepWiki 是导航辅助；论坛回答作为经验线索。 |
| 社区 / 社媒 / 平台内容 | 知乎、Reddit、X、Bluesky、YouTube、LinkedIn、小红书、B 站；Douyin MCP / TikHub；agent-reach | 只在用户反馈、技术讨论、趋势或情绪确属研究目标时采集；按发布者身份和上下文确定证据等级。旧 midu-hotsearch 已弃用；Douyin 和财经热榜应分别用对应专用来源，不再用一个泛热榜工具包办。 |
| 新闻 / 产品 / 创投 | Reuters、BBC、Al Jazeera、aihot；Product Hunt、TechCrunch、36氪、虎嗅 | 发现事件、产品发布和融资线索；事件时间与发布时间分开核对，并回到企业 / 监管 / 原始公告。 |
| 背景知识 | Wikipedia、百度百科 | 仅作术语与背景导航，不单独支撑关键事实。 |
| 用户自有资料 | Obsidian、Notion、ima、Local Wiki、Google Drive、百度网盘 | 属于用户提供的内部材料 / 知识库输入，不是公开搜索源；仅按授权访问和引用。 |
| 文档转换 | MarkItDown 等 PDF / Word / 财报转 Markdown 工具 | 属于内容预处理，不是数据源，也不产生新的独立证据。 |

补充边界：ReadGZH 是公众号正文提取器，不是全网搜索引擎；FRED / SEC 是结构化官方数据源；Connected Papers 暂列观察 / 隔离，引用关系优先走 OpenAlex、Crossref、OpenCitations。

## 3. 最小路由表

| 研究场景 | 首轮路由 | 条件补充 / 专业并行 |
|---|---|---|
| 单点事实 / 普通对比 | 宿主内置搜索，或一个最匹配的广域 owner | 只有原始来源缺失、结果冲突或时效不足才追加第二个 owner。 |
| 中国市场 / 中文资料 | 内置搜索，或 Metaso **或** Bocha | Search1API Baidu / Octen 只在特定缺口时补充；TinySearch 仅作第二索引；不强制三源齐跑。 |
| 海外 / 国际市场 | 内置搜索，或 Octen **或** Exa | Exa 偏语义、长尾和技术资料；Octen 用于一般发现 / 多角度查询；Tavily 或 SerpAPI 仅在需要时补位。 |
| 中外跨境研究 | 只在研究范围确实跨境时，CN 与 Global 各选一个 owner | 各市场证据不足时再局部扩源；不因中文提问而漏掉海外一手资料。 |
| 学术 / 专利 / 法律 / 财务 / 监管 | 直接查询相应数据库、官方记录或原始披露 | 广域搜索负责找线索；专业源负责支持结论，两者可并行。 |
| GitHub / 技术项目 | GitHub 原始文件、API、PR、Issue、Release、CI | DeepWiki 用于导航和理解；历史 / 版本判断必须回到不可变 GitHub 证据。 |
| 微信公众号 | 搜索工具或 wechat-article-search 负责发现 | 取得原文 canonical URL 后再用 ReadGZH 读取；发现失败与正文提取失败分开记录。 |
| 已知网页 / 动态网站 | 对已知 URL 选择 Firecrawl、Tavily Extract 或 Exa Contents | 需要登录、点击或动态交互时再用浏览器执行器；不要额外启动一轮通用搜索。 |
| 多步深度研究 | 一个广域 owner；必要时选一个 Broad Search **或** 一个 Research Agent | 官方 / 学术 / 财务 / 专利 / UGC 等所需证据域并行；聚合器仍需单独门控。 |

## 4. 证据计数与可信度

必须区分：

- provider hits：多少个检索工具发现了材料；
- unique documents：多少份不同的原始文档；
- independent publishers：多少个独立发布者 / 机构；
- upstream providers：能够确认的独立底层索引或数据提供方。

同一篇文章被五个搜索工具命中仍是一份文档证据。未知上游标为 unknown，不因工具品牌不同而推断独立。

证据分级沿用 DMR 既有规则：**T1** 官方 / 监管 / 原始披露 / 专利原文；**T2** 身份可核实的专家、客户或业内人士材料；**T3** 权威媒体、行业报告、学术研究；**T4** 匿名社媒、论坛和未核实用户反馈。搜索 API、AI 答案、MCP 握手和 Research Agent 摘要本身都不是新的证据发布者。

## 5. 状态口径

default / optional / pilot / paused / watch 描述路由地位，不代表当前机器连接状态。运行状态应另外区分 configured、protocol-ready、functional smoke 和 quality benchmark。

当前外部报告中的 Provider 成功结果只记作**第三方报告的功能性实测**；没有相同查询集、独立来源覆盖、成本和可复现记录，不升级为 DMR quality_benchmarked。Octen Broad Search 若一次展开多个子查询，应视为高扇出调用，同轮不再无条件叠加另一个广域 Provider。Exa MCP 在本机遇到的 Cloudflare 403 属于当时环境级故障，应按 REST fallback 处理，不外推为服务整体失效。Search1API WeChat / Sogou 若遇 antispider，只能记录发现失败，不等于公众号全文已覆盖。bingcn 暂停当前路由是基于已有样例的局部决定，不等于判定服务整体失效。AnySearch 仍是试点；AgentEarth 仍是观察项；Connected Papers 不进入活动路由，学术引用关系优先用 OpenAlex / Crossref / OpenCitations 等可追溯数据。

## 6. 与其他文件的边界

- SKILL.md：只描述路由原则和工作流，不重复维护 Provider 排名表。
- references/cross-platform-tools.md：只说明如何接入，不决定何时调用。
- sources.registry.yaml：只登记健康探针。当前通用探针只支持 URL GET 和 MCP initialize；未实现安全请求适配器的认证 REST 源标为 custom 并跳过探测，不得伪造 PASS。
- scripts/source_health.py：探针结果只代表探针层级，不代表搜索质量或证据质量。

> 官方接口和产品能力会变化。接入前应回源检查官方文档；不要将本目录中的能力分类视为当前账号额度、已连接状态或实时质量保证。
