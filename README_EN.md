# Deep Market Research Skill

> 🌐 Language / 语言：[🇨🇳 中文](README.md) · **[🇺🇸 English](README_EN.md)**
>
> A cross-platform AI-agent research workflow: source tiering + ≥2-source cross-validation + dedupe / stale / fake / contradiction removal + real user-review absorption, producing stable, reproducible, confidence-labeled research reports.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Follows the [Agent Skills open standard](https://agentskills.io/) (initiated by Anthropic; natively supported by 50+ platforms including Claude Code / OpenAI Codex / TRAE / Qoder / WorkBuddy).

---

## ✨ Features

> Core difference vs generic AI search / deep-research skills: **dmr is not a search wrapper — it is a reproducible, confidence-labeled research pipeline with adversarial final-draft auditing.**

- Full changelog: see [CHANGELOG.md](CHANGELOG.md)

### Unique advantages

- **Deterministic pipeline**: fixed Step 0–8, reproducible and comparable every run
- **plan-first acceptance**: Step 0 produces acceptance criteria (each with a measurable anchor) + three-state termination conditions (stop on criteria met / budget exhausted / max N rounds), checked item-by-item at final delivery
- **Deterministic skeleton, selective execution**: keeps the reproducible Step 0–8 structure while running only the steps justified by task complexity
- **Source-tier confidence**: T1 official / T2 expert / T3 secondary / T4 social; every conclusion carries a confidence label
- **≥2-source cross-validation**: facts are decomposed, conflicts are explicitly flagged, no forced consensus; competitor key parameters require ≥3 sources
- **Adversarial final-draft audit**: an independent critic challenges the draft before delivery; local patches, never full regeneration
- **Programmatic lint gate**: `validate_report.py` (6 lint rules) + `validate_param_card.py` (param-card validation) — zero-dependency, offline-safe, runnable before delivery
- **Native Chinese/CJK support**: WeChat official accounts, Zhihu, Xiaohongshu, CNKI and other Chinese sources are never dropped or treated as junk
- **Zero-install skill**: pure methodology calling the agent's built-in tools, no extra Python dependency
- **Optional tools never block**: Exa / TinyFish / Firecrawl / Tavily Research / Perplexity / GPT Researcher / ModelScope are used only when their distinct capability is needed, with graceful fallback when absent
- **Platform-agnostic**: no assumption of any MCP config / agent-team protocol / proprietary backend; works on WorkBuddy / Claude / Codex / Trae / qoder / Cursor

### Output capabilities

- **Five templates**: general / industry track (McKinsey-style, incl. sales & commercialization) / company competitive (SWOT + scenario simulation) / academic / monitoring-increment
- **intel-brief style**: fact → impact → cause triad organization
- **Academic modules**: arXiv / PubMed / OpenAlex / Semantic Scholar / CNKI, free APIs preferred
- **Analysis lenses**: Porter's Five Forces / PESTEL / BCG / 3C / TAM-SOM + sales lenses, triggered by intent, never piled on
- **Research parameter card**: single-authority structured schema (mandatory source pool + recommended acceptance criteria), passed whole across stages
- **Incremental accumulation**: structured markdown note (YAML frontmatter) + entity-level evidence cache, integrates with ima / Obsidian / local wiki
- **Quarterly benchmark**: 5 fixed baseline questions + Q6 sales-routing regression, score evolution guards against quality regressions
- **Opt-in incremental accumulation**: writes structured markdown notes (YAML frontmatter) only when the user requests it or the workspace defines persistence; integrates with ima / Obsidian / local wiki

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
| **TRAE CN** | `~/.trae-cn/skills/` | auto-discover |
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

The script auto-detects existing directories among `~/.claude`, `~/.codex`, `~/.trae`, `~/.trae-cn`, `~/.qoder`, `~/.workbuddy` and installs into them; uninstalled ones are skipped. **Restart the agent** after installation to load the skill.

> **Manual install**: copy the entire `deep-market-research/` folder into the target platform's `skills/` directory.

---

## 🚀 Usage

Just tell the agent (auto-matched to `SKILL.md`'s `description` trigger):

- "Research the competitive landscape of industrial AI 3D vision metrology"
- "Competitive analysis: Hikrobot vs DEEPVISION vs TZTEK"
- "Industry trend: investment opportunities in China's machine-vision supply chain"
- "Dig into Keyence China's background"

The agent uses the SKILL.md flow as a deterministic skeleton and executes only the stages justified by the task: scope convergence → collection → dedupe/stale-removal → source tiering → cross-validation → contradiction handling → user-review signals → scoring → structured output.

---

## 📂 Directory structure

```
deep-market-research/
├── SKILL.md                      # Core: metadata + complete workflow instructions (Step 0–8 + templates + lenses + quality rules)
├── README.md / README_EN.md     # Chinese / English documentation
├── assets/                       # pipeline.svg + stack.svg visualizations
├── references/                   # Templates + FAQ + example + param-card schema + data sources + optional-tool guides
├── scripts/                      # Lint gates (validate_report / validate_param_card) + README drift guard + source health + MCP sync + FRED
├── benchmarks/                   # 5 fixed baseline questions + Q6 sales-routing regression + score-evolution log
├── tests/                        # pytest tests
├── sources.registry.yaml         # Source registry (default / optional / deprecated tiers)
├── install.sh / install.ps1      # One-click install scripts (Unix / Windows)
├── LICENSE                       # MIT
├── CONTRIBUTING.md               # Contribution guide
└── .gitignore
```

> The skill's core is **self-contained**: the core methodology, workflow, and quality rules are embedded in `SKILL.md`; the five output templates (A–E) live externally in [references/templates.md](references/templates.md); `scripts/` provides optional runtime validation hooks whose absence never blocks the main pipeline.

---

## ⚙️ Optional data sources & enhancement skills

The skill works with the agent's built-in web tools (WebSearch / WebFetch). Extra skills or MCPs are selected only when the task needs their distinct capability, following a single-owner escalation chain; **if unavailable or failing, the workflow degrades gracefully without interrupting research**.

> **Full data-source table (30+ dimensions: search entry, social/reviews, academic papers, finance, legal, patents, etc.) has been moved to [references/data-sources.md](references/data-sources.md)**

---

## ❓ FAQ & full examples

- **FAQ (8 questions)**: see [references/faq.md](references/faq.md)
- **End-to-end example**: see [references/example.md](references/example.md) (industrial-robotics track research)
- **Full changelog**: v2.0.0 → v2.9.0 — see [CHANGELOG.md](CHANGELOG.md) (v2.8.0 = audit-fix release)

---

## 🔁 Release checklist (maintainers)

1. Local gates: `python scripts/readme_drift_check.py` (R1–R7) + `python -m pytest tests/` all green.
2. Version parity: SKILL.md frontmatter + body header + reference index + README/README_EN changelog line == CHANGELOG top entry (R4/R7 enforced).
3. Smoke both installers: `install.ps1` on Windows; `install.sh` in a Linux container or Git Bash (verify scripts/ + benchmarks/ placement and `__pycache__` cleanup).
4. Push main → CI green (Ubuntu pytest).
5. Benchmark regression when the kernel changes: benchmarks 5 questions + Q6 sales routing (docs-only errata exempt).
6. Tag `vX.Y.Z` and push the tag.
7. GitHub Release: notes quote the CHANGELOG entry; rebuild tar.gz + zip assets; errata merge as `Amended` into the existing entry, no new tag.
8. Re-run the installer; verify every platform skill copy matches the new version.

---

## 📜 License

[MIT License](LICENSE)
