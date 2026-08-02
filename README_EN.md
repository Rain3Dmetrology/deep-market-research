# Deep Market Research — Deep Market Research Skill

> 🌐 Language / 语言：[🇨🇳 中文](README.md) · **[🇺🇸 English](README_EN.md)**
>
> A cross-platform AI-agent research workflow: source tiering + ≥2-source cross-validation + dedupe / stale / fake / contradiction removal + real user-review absorption, producing stable, reproducible, confidence-labeled research reports.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Follows the [Agent Skills open standard](https://agentskills.io/) (initiated by Anthropic; natively supported by 50+ platforms including Claude Code / OpenAI Codex / TRAE / Qoder / WorkBuddy).

---

## ✨ Features (v2.3.4)

> Core difference vs generic AI search / deep-research skills: **dmr is not a search wrapper — it is a reproducible, confidence-labeled research pipeline with adversarial final-draft auditing.**

- Full changelog: see [CHANGELOG.md](CHANGELOG.md)

### Unique advantages

- **Deterministic pipeline**: fixed Step 0–8, reproducible and comparable every run
- **Source-tier confidence**: T1 official / T2 expert / T3 secondary / T4 social; every conclusion carries a confidence label
- **≥2-source cross-validation**: facts are decomposed, conflicts are explicitly flagged, no forced consensus
- **Adversarial final-draft audit**: an independent critic challenges the draft before delivery; local patches, never full regeneration
- **Native Chinese/CJK support**: WeChat official accounts, Zhihu, Xiaohongshu, CNKI and other Chinese sources are never dropped or treated as junk
- **Zero-install skill**: pure methodology calling the agent's built-in tools, no extra Python dependency
- **Optional tools never block**: Exa / Firecrawl / Tavily / Perplexity / GPT Researcher / ModelScope enhance when present, gracefully degrade when absent
- **Platform-agnostic**: no assumption of any MCP config / agent-team protocol / proprietary backend; works on WorkBuddy / Claude / Codex / Trae / qoder / Cursor

### Output capabilities

- **Three templates**: general research / industry track (McKinsey-style) / company competitive (SWOT + scenario simulation)
- **intel-brief style**: fact → impact → cause triad organization
- **Academic modules**: arXiv / PubMed / OpenAlex / Semantic Scholar / CNKI, free APIs preferred
- **Analysis lenses**: Porter's Five Forces / PESTEL / BCG / 3C / TAM-SOM, triggered by intent, never piled on
- **Incremental accumulation**: structured markdown note (YAML frontmatter), integrates with ima / Obsidian / local wiki

### Tech stack & pipeline (visual)

**Research pipeline** — the Step 0-8 main line and the Three-B deep-research loop are orthogonal; quality is guaranteed by methodology, not by any single search API:

![调研流水线](assets/pipeline.svg)

**Tech stack** — default layer is zero-dependency, zero-install; the optional enhancement layer degrades gracefully when absent and only enriches source material:

![技术栈](assets/stack.svg)

---

## 🌐 Supported platforms

| Platform | Skills directory | Trigger |
|----------|------------------|---------|
| **Claude Code / Claude** | `~/.claude/skills/` | auto-discover + `/deep-market-research` |
| **OpenAI Codex** | `~/.codex/skills/` | auto-discover |
| **TRAE** | `~/.trae/skills/` | auto-discover |
| **Qoder** | `~/.qoder/skills/` | auto-discover |
| **WorkBuddy / CodeBuddy** | `~/.workbuddy/skills/` | auto-discover |

> See the full client list at [agentskills.io/clients](https://agentskills.io/clients).

---

## 📦 Installation

```bash
git clone https://github.com/Rain3Dmetrology/deep-market-research.git
cd deep-market-research

# Unix / macOS / Git Bash
./install.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File install.ps1
```

The script auto-detects existing directories among `~/.claude`, `~/.codex`, `~/.trae`, `~/.qoder`, `~/.workbuddy` and installs into them; uninstalled ones are skipped. **Restart the agent** after installation to load the skill.

> **Manual install**: copy the entire `deep-market-research/` folder into the target platform's `skills/` directory.

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
├── SKILL.md                      # Core: metadata + complete workflow instructions (Step 0–8 + templates + lenses + quality rules)
├── README.md / README_EN.md     # Chinese / English documentation
├── release_body.md               # GitHub Release description
├── assets/                       # pipeline.svg + stack.svg visualizations
├── references/                   # Optional enhancement tools + templates + FAQ + example + data sources
├── scripts/                      # Optional helpers: cross-machine MCP sync + FRED macro data query
├── install.sh / install.ps1      # One-click install scripts (Unix / Windows)
├── LICENSE                       # MIT
├── CONTRIBUTING.md               # Contribution guide
└── .gitignore
```

> The skill's core is **self-contained**: all workflows, templates, and rules are embedded in `SKILL.md`; no extra scripts or config files are needed. `references/` is only an optional enhancement-tool guide; its absence does not affect the main flow.

---

## ⚙️ Optional data sources & enhancement skills

The skill itself works using the agent's built-in web tools (WebSearch / WebFetch). If your agent has the following skills installed or the following MCPs connected, it automatically gains deeper coverage; **when absent, it always degrades gracefully and never interrupts the research**.

> **Full data-source table (30+ dimensions: search entry, social/reviews, academic papers, finance, legal, patents, etc.) has been moved to [references/data-sources.md](references/data-sources.md)**

---

## ❓ FAQ & full examples

- **FAQ (7 questions)**: see SKILL.md [Section 8 · FAQ](SKILL.md)
- **End-to-end example**: see SKILL.md [Section 9 · Full Example](SKILL.md)
- **Full changelog**: v2.0.0 → v2.3.4 — see [CHANGELOG.md](CHANGELOG.md)

---

## 📜 License

[MIT License](LICENSE)
