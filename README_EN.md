# Deep Market Research — Deep Market Research Skill



> 🌐 语言 / Language：**[🇨🇳 中文](README.md)** · [🇺🇸 English](README_EN.md)



> A cross-platform AI-agent research workflow: source tiering + ≥2-source cross-validation + dedupe / stale / fake / contradiction removal + real user-review absorption, producing stable, reproducible, confidence-labeled research reports.



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Follows the [Agent Skills open standard](https://agentskills.io/) (initiated by Anthropic; natively supported by 50+ platforms including Claude Code / OpenAI Codex / TRAE / Qoder / WorkBuddy).



---



## ✨ Features (v2.3.4)



> Core difference vs generic AI search / deep-research skills: **dmr is not a search wrapper — it is a reproducible, confidence-labeled research pipeline with adversarial final-draft auditing.**



### Version evolution

- Full changelog: see [CHANGELOG.md](CHANGELOG.md).


### Unique advantages



- **Deterministic pipeline**: fixed Step 0–8, reproducible and comparable every run.

- **Source-tier confidence**: T1 official / T2 expert / T3 secondary / T4 social; every conclusion carries a confidence label.

- **≥2-source cross-validation**: facts are decomposed, conflicts are explicitly flagged, no forced consensus.

- **Adversarial final-draft audit**: an independent critic challenges the draft before delivery; local patches, never full regeneration.

- **Native Chinese/CJK support**: WeChat official accounts, Zhihu, Xiaohongshu, CNKI and other Chinese sources are never dropped or treated as junk.

- **Zero-install skill**: pure methodology calling the agent's built-in tools, no extra Python dependency.

- **Optional tools never block**: Exa / Firecrawl / Tavily / Perplexity / GPT Researcher / ModelScope enhance when present, gracefully degrade when absent.

- **Platform-agnostic**: no assumption of any MCP config / agent-team protocol / proprietary backend; works on WorkBuddy / Claude / Codex / Trae / qoder / Cursor; optional tools degrade gracefully when absent.



### Output capabilities



- **Three templates**: general research / industry track (McKinsey-style) / company competitive (SWOT + scenario simulation).

- **intel-brief style**: fact → impact → cause triad organization.

- **Academic modules**: arXiv / PubMed / OpenAlex / Semantic Scholar / CNKI, free 🆓 APIs preferred.

- **Analysis lenses**: Porter's Five Forces / PESTEL / BCG / 3C / TAM-SOM, triggered by intent, never piled on.

- **Incremental accumulation**: structured markdown note (YAML frontmatter), integrates with ima / Obsidian / local wiki.



---





### Tech stack & pipeline (visual)



**Research pipeline** - the Step 0-8 main line and the Three-B deep-research loop are orthogonal; quality is guaranteed by methodology, not by any single search API:



![调研流水线](assets/pipeline.svg)



**Tech stack** - default layer is zero-dependency, zero-install; the optional enhancement layer degrades gracefully when absent and only enriches source material:



![技术栈](assets/stack.svg)



---



## 🌐 Supported platforms



This repo follows the [Agent Skills open standard](https://agentskills.io/). The platforms below support it natively and **will auto-discover and trigger the skill once installed**:



| Platform | Skills directory | Trigger |

|----------|------------------|---------|

| **Claude Code / Claude** | `~/.claude/skills/` | auto-discover + `/deep-market-research` |

| **OpenAI Codex** | `~/.codex/skills/` | auto-discover |

| **TRAE** | `~/.trae/skills/` | auto-discover |

| **Qoder** | `~/.qoder/skills/` | auto-discover |

| **WorkBuddy / CodeBuddy** | `~/.workbuddy/skills/` | auto-discover |

| Other agentskills-compatible platforms | the platform's `skills/` directory | auto-discover |



> See the full client list at [agentskills.io/clients](https://agentskills.io/clients).



---



## 📦 Installation



### Option 1: One-click install script (recommended)



After cloning, run the install script — it auto-detects installed agent platforms on this machine and copies the skill into the corresponding `skills/` directory:



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



The script detects and installs into **existing** directories among `~/.claude`, `~/.codex`, `~/.trae`, `~/.qoder`, `~/.workbuddy`; uninstalled ones are skipped automatically.



### Option 2: Manual installation



Copy the entire `deep-market-research/` folder into the target platform's skills directory:



```bash

git clone https://github.com/Rain3Dmetrology/deep-market-research.git

# Claude Code / Codex / Cursor / Windsurf / Gemini CLI, etc.

cp -r deep-market-research ~/.claude/skills/

# WorkBuddy

cp -r deep-market-research ~/.workbuddy/skills/

# TRAE

cp -r deep-market-research ~/.trae/skills/

# Qoder

cp -r deep-market-research ~/.qoder/skills/

```



After installation, **restart the agent** (or run the skill-refresh command) to load it.



---



## 🚀 Usage



Just tell the agent (auto-matched to `SKILL.md`'s `description` trigger):



- "Research the competitive landscape of industrial AI 3D vision metrology"

- "Competitive analysis: Hikrobot vs DEEPVISION vs Techman Robot"

- "Industry trend: investment opportunities in China's machine-vision supply chain"

- "Dig into Keyence China's background"



The agent executes the fixed SKILL.md flow: scope convergence → multi-source collection → dedupe/stale-removal → source tiering → cross-validation/fake-removal → contradiction resolution → user-review absorption → 100-point scoring → structured output.



---



## 📂 Directory structure



```

deep-market-research/

├── SKILL.md                      # Core: metadata + complete workflow instructions (Step 0–8 + three templates + analysis lenses + quality rules)

├── README.md                     # Chinese documentation (this repo's home page)

├── README_EN.md                  # English documentation

├── assets/

│   ├── pipeline.svg              # Research pipeline visualization

│   └── stack.svg                 # Tech stack visualization

├── references/

│   └── cross-platform-tools.md   # Optional: six-platform enhancement-tool setup guide (absence does not affect main flow)

├── LICENSE                       # MIT

├── CONTRIBUTING.md               # Contribution guide

├── install.sh                    # Unix install script

├── install.ps1                   # Windows install script

└── .gitignore

```



> The skill's core is **self-contained**: all workflows, templates, and rules are embedded in `SKILL.md`; no extra scripts or config files are needed. `references/` is only an optional enhancement-tool guide; its absence does not affect the main flow.



---



## ⚙️ Optional data sources & enhancement skills (plug in as needed, graceful degradation)



The skill itself works using the agent's built-in web tools (WebSearch / WebFetch). If your agent has the following skills installed or the following MCPs connected, it automatically gains deeper coverage; **when absent, it always degrades gracefully and never interrupts the research**:




| Dimension | Data source / Skill | Purpose | Recommendation | Access |
|-----------|---------------------|---------|-----------------|--------|
| **Search entry** | built-in WebSearch/WebFetch (preferred) + **Firecrawl** (keyless MCP) + **Tavily** (key, direct API) + **SearXNG** (key-free metasearch) + **Novada** (free 1000/mo) + **AgentKey** (aggregated API) | general web retrieval, verification, aggregated data | 🛟 Built-in base (always) · 🥇 Firecrawl · 🥈 Tavily/Novada · 🛟 SearXNG/AgentKey (parallel) | 🟢 Built-in base (web_search/web_fetch) · 🔴 Firecrawl/Exa/Tavily/Novada need key · 🟡 SearXNG(self-host)/AgentKey(connector) need MCP/account connection |
| **AI search (optional)** | **Perplexity** / **Tavily** (key) / **AnySearch** / **Metaso (秘塔)** | cited AI search; skipped without key | 🎯 Perplexity/Metaso · 🥈 Tavily · 🎯 AnySearch | 🔴 All need API key (skipped without key) |
| **Social / reviews** | **agent-reach** / **agent-browser** / web-access | Xiaohongshu/Zhihu/Reddit/Bluesky/X/comments (agent-reach measured 6 social + 5 base; **Douyin/Weibo → web_search fallback; WeChat OA → wechat-article-search skill, NOT agent-reach**) | 🎯 Platform-specific | 🟡 agent-reach / agent-browser / web-access need skill install (web-access needs Node22 + local Chrome CDP) · 🟢 web_search built-in (LLM native, zero-config) |
| **Zhihu (tech + feedback)** | **zhihu MCP** | Chinese tutorials, user feedback, cross-validation | 🎯 Platform-specific | 🟡 Built-in auth (30-day renewal) |
| **WeChat official-account articles** | **wechat-article-search** (search) + **ReadGZH-Agent MCP** (full-text, keyless remote) | first-hand Chinese deep articles: search via skill, full-text via MCP; complements | 🥇 ReadGZH(full) · 🎯 wechat-article-search(search) | 🟡 Install wechat-article-search skill · 🔴 ReadGZH needs READGZH_API_KEY |
| **Douyin (short video)** | **douyinmcp MCP** (get_homefeed hot-list + deep content, free preferred) / **TikHub API** (paid stable fallback) | Douyin trends & deep content; strict anti-bot, free-first, web_search fallback when absent | 🎯 douyinmcp(free) · 🥈 TikHub(paid) | 🟡 Needs Cookie (Chrome login state) |
| **Document cleanup** | **markitdown** | PDF/Word/financial-reports → Markdown | 🎯 Platform-specific | 🟡 Needs skill install |
| **A-share finance** | **Tongdaxin tdx-connector** | listed-company F10 / shareholders / fund flows | 🎯 Platform-specific | 🟡 Needs platform auth |
| **Patents** | **Patsnap MCP** | barriers, patent families, citation analysis | 🎯 Platform-specific | 🟡 Needs internal token |
| **Code / projects** | GitHub search + Trending (`github` MCP + `gh` CLI + web) | OSS implementations, tech stacks, Star/PR trends | 🥇 DeepWiki · 🥈 GitHub/gh | 🟡 DeepWiki needs keyless MCP connection (no key, but MCP endpoint config required) · 🟡 github MCP/gh needs auth |
| **Academic papers / metadata** | **OpenAlex** / **Semantic Scholar** / **arXiv** / **PubMed** / **bioRxiv** / **EMBL-EBI·Europe PMC**; `literature-search` as methodology ref (not a callable API) | metadata, citation networks, TLDR, preprints | 🛟 Free API | 🟢 All key-free (Semantic Scholar: keyless but ~100 req/5min/IP; free key raises limit) |
| **Citation tracing** | **Crossref** / **OpenCitations** | DOI metadata, cited/citing relations | 🛟 Free API | 🟢 Key-free |
| **Research data repos** | **Zenodo** / **Figshare** / **Harvard Dataverse** / **NASA** | datasets/software, DOI-traceable | 🛟 Free API | 🟢 Key-free (NASA can use DEMO_KEY) |
| **AI models / datasets** | **Hugging Face Hub API** / **ModelScope** | models, code, docs, datasets | 🛟 HF Free API · 🎯 ModelScope | 🟡 HF needs `HF_TOKEN` (private/high-quota/write/download gated models; public browse + public weights key-free) · 🟡 ModelScope needs token |
| **Developer communities** | **Stack Overflow** (SE API key-free) + **Hacker News** (Algolia API; Firebase endpoint deprecated 2023) / Reddit (OAuth required since 2023 → agent-reach / web_search fallback) / CSDN (unofficial API) | tech-selection, real-world pitfalls | 🛟 Free API | 🟢 Key-free (Reddit via fallback; HN may be IP-blocked by Algolia WAF on some egress IPs → web_search fallback) |
| **Finance / hot-list** | Tencent self-selected / westock-mcp · **wallstreetcn** (free finance hot-list + flash, key-free) | fundamentals, quotes, research, real-time hot-list signal | 🎯 Platform-specific · 🟢 wallstreetcn | 🟢 wallstreetcn key-free · 🟡 self-selected/westock needs auth |
| **Legal / compliance** | Wolters Kluwer / YuanDian / **pkulaw** | litigation, penalties, laws | 🎯 Platform-specific | 🟡 Needs platform auth |
| **Enterprise registry / risk** | Tianyancha / Qichacha / **qixinhuiyan** | equity, judiciary, risk | 🎯 Platform-specific | 🟡 Needs platform auth |
| **Top journals / Chinese literature** | Nature / Science (DOI) / CNKI / Google Scholar (export) | first-hand top-journal | 🌐 General web | 🟢 Abstract key-free · 🟡 CNKI/subscription needs auth |
| **Macroeconomics** | Trading Economics / FRED / NBS / PBOC·CSRC / Cailian / Wallstreetcn | macro indicators | 🌐 General web | 🟡 FRED needs `FRED_API_KEY` (free signup, **strict requirement**: no key → HTTP 400 `Variable api_key is not set`) · 🌐 Others via general web |
| **Patents (public)** | Google Patents / USPTO / EPO / WIPO | patent text, legal status | 🌐 General web | 🟢 Key-free |
| **Open encyclopedias** | Wikipedia / Baidu Baike | concept intro, background | 🌐 General web | 🟢 Key-free |
| **Products / VC** | Product Hunt / TechCrunch / 36Kr / Huxiu | launches, funding, market heat | 🌐 General web | 🟢 Key-free |
| **Chinese communities** | Cnblogs / V2EX / Xiaohongshu / Bilibili | feedback, tutorials | 🌐 General web | 🟢 Key-free (Xiaohongshu/Bilibili via web_search) |
| **International social** | Bluesky / X / YouTube / LinkedIn | official updates, KOL, sentiment | 🌐 General web | 🟢 Key-free (via web_search/agent-reach) |
| **News / info** | **aihot** (key-free) / BBC / Reuters / Al Jazeera | industry briefs, first-hand news | 🛟 aihot built-in · 🌐 others | 🟢 aihot key-free · 🌐 Others via general web |
| **Knowledge base** | ima-mcp / Obsidian / local wiki / **notion** | own materials, incremental Lint | 🎯 Platform-specific | 🟡 Needs platform auth |
| **Cloud storage / files** | **Baidu Netdisk** / **Google Drive** | own files, archiving &amp; delivery | 🎯 Platform-specific | 🟡 Needs platform auth |

> **Recommendation**: 🥇 first-choice (default enhancement) · 🥈 alternative · 🛟 fallback (keyless default layer, works without key) · 🎯 personalized (needs key / account / specific platform) · ⚠️ not recommended for general use. Cross-validation snapshot 2026-07; search APIs drift quarterly — re-verify against vendor before production.

> **Honesty statement**: Only connector types that genuinely exist are declared; the connection state of any personal environment is never exposed. Missing sources degrade gracefully and never interrupt research. Services not provided (e.g. Crunchbase Pro, PitchBook) are never falsely labeled — if your platform provides them, append them to the Step 1 search entry yourself.
> **Routing, not bundling**: all entries above are **external optional peer skills / MCPs**; dmr only routes sources and degrades gracefully — it never bundles their implementations. Missing entries are skipped with the uncovered dimension noted; research never stops.
> **Access**: 🟢 Zero-config (key-free / token-free, works out of the box: ① LLM built-in `web_search` / `web_fetch` ② dmr's keyless public REST API direct calls, e.g. OpenAlex / wallstreetcn / aihot) · 🔴 Needs API key (degrades gracefully if missing) · 🟡 Needs Cookie / token / platform auth / **MCP server connection** (even if keyless, e.g. DeepWiki / SearXNG / AgentKey still need connection endpoints, NOT zero-config).




---



## ❓ FAQ & full examples



- **FAQ (7 questions)**: how this skill differs from WebSearch, what to do when core sources are unreachable, how to choose templates B/C/D, whether a paid key is needed, how to handle contradictory sources, report length, whether incremental accumulation must use ima — see SKILL.md [Section 8 · FAQ](SKILL.md).

- **End-to-end example**: from the user query "Research China's industrial-robot track + reducer localization + Estun/Inovance positioning" to the per-step outputs of Step 0→8 (collection / dedupe / validation / contradiction resolution / tiering / template / scorecard) — see SKILL.md [Section 9 · Full Example](SKILL.md).

- **Full changelog**: every change detail from v2.0.0 → v2.3.4 — see [CHANGELOG.md](CHANGELOG.md).



---



## 📜 License



[MIT License](LICENSE)

