# Deep Market Research — 深度市场调研 Skill

> 🌐 语言 / Language：**[🇨🇳 中文](README.md)** · [🇺🇸 English](README_EN.md)
>
> 跨平台 AI Agent 调研工作流：源分级 + ≥2 源交叉验证 + 去重/去旧/去假/去矛盾 + 吸收真实用户热评，输出质量稳定、可复现、带置信度标签的调研报告。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

遵循 [Agent Skills 开放标准](https://agentskills.io/)（Anthropic 发起，Claude Code / OpenAI Codex / TRAE / Qoder / WorkBuddy 等 50+ 平台原生支持）。

---

## ✨ 特性

> 与通用 AI 搜索 / 深度研究 skill 的核心差异：**dmr 不是搜索包装，而是一条可复现、带置信标签、终稿对抗审计的调研流水线。**

- 完整版本变更明细见 [CHANGELOG.md](CHANGELOG.md)

### 独有优势

- **确定性流水线**：固定 Step 0–8，每次可复现、可对比
- **plan-first 验收先行**：Step 0 即产出验收标准（每条含度量锚点）＋ 终止条件三态（达标即停 / 预算耗尽即停 / 最多 N 轮），终稿逐条对照
- **源分级置信**：T1 官方 / T2 专家 / T3 二手 / T4 社媒，每条结论带置信标签
- **≥2 源交叉验证**：事实拆解，冲突显式标注，不强行共识；竞品关键参数须 ≥3 源
- **终稿对抗审计**：终稿前独立 critic 挑战，局部修补，不整篇重写
- **程序化机检门禁**：`validate_report.py`（6 条 lint）＋ `validate_param_card.py`（参数卡校验），零依赖、离线安全，交付前可机检
- **中文/CJK 原生支持**：公众号、知乎、小红书、CNKI 等中文源不丢弃、不当 junk
- **零安装 Skill**：纯方法论，调用 Agent 内置工具，无需额外 Python 依赖
- **可选工具永不阻断**：Exa / Firecrawl / Tavily / Perplexity / GPT Researcher / ModelScope 有则增强，缺失优雅降级
- **平台无关**：不绑定任何 MCP 配置 / agent-team 协议 / 专有后端，WorkBuddy / Claude / Codex / Trae / qoder / Cursor 通用

### 输出能力

- **五套模板**：通用 / 行业赛道（麦肯锡风，含销售与商业化分析）/ 公司竞品（SWOT + 情景推演）/ 学术 / 监测增量
- **intel-brief 风格**：事实 → 影响 → 原因三元组织
- **学术模块**：arXiv / PubMed / OpenAlex / Semantic Scholar / CNKI，优先免费 API
- **分析透镜**：波特五力 / PESTEL / BCG / 3C / TAM-SOM + 销售透镜，按意图触发，不堆砌
- **研究参数卡**：结构化 schema 单一权威（必含来源池 + 推荐验收标准），跨阶段整卡传递
- **增量沉淀**：结构化 markdown note（YAML frontmatter）+ 实体级证据缓存，对接 ima / Obsidian / 本地 wiki
- **季度基准自测**：5 题固定基准 + Q6 销售路由回归题，分数演化防质量回归

### 技术栈与流水线（可视化）

**调研流水线** — 主管线 Step 0–8 与三-B 深度研究闭环正交，质量由方法论保证而非某个搜索 API：

![调研流水线](assets/pipeline.svg)

**技术栈** — 默认层零依赖零安装；可选增强层缺失即优雅降级，仅丰富素材来源：

![技术栈](assets/stack.svg)

---

## 🌐 支持的平台

| 平台 | Skills 目录 | 触发方式 |
|------|------------|---------|
| **Claude Code / Claude** | `~/.claude/skills/` | 自动发现 + `/deep-market-research` |
| **OpenAI Codex** | `~/.codex/skills/` | 自动发现 |
| **TRAE** | `~/.trae/skills/` | 自动发现 |
| **Qoder** | `~/.qoder/skills/` | 自动发现 |
| **WorkBuddy / CodeBuddy** | `~/.workbuddy/skills/` | 自动发现 |

> 完整兼容平台列表见 [agentskills.io/clients](https://agentskills.io/clients)。

---

## 📦 安装

```bash
git clone https://github.com/Rain3Dmetrology/deep-market-research.git
cd deep-market-research

# Unix / macOS / Git Bash
./install.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File install.ps1
```

脚本自动检测 `~/.claude`、`~/.codex`、`~/.trae`、`~/.qoder`、`~/.workbuddy` 中已存在的目录并安装，未安装的自动跳过。安装后**重启 Agent** 即可加载。

> **手动安装**：将整个 `deep-market-research/` 文件夹复制到目标平台的 `skills/` 目录。

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
├── SKILL.md                      # 核心：元数据 + 完整工作流指令（Step 0–8 + 模板 + 透镜 + 质量规则）
├── README.md / README_EN.md     # 中英文说明
├── assets/                       # pipeline.svg + stack.svg 可视化图
├── references/                   # 模板 + FAQ + 示例 + 参数卡 schema + 数据源表 + 可选工具指南
├── scripts/                      # 机检门禁（validate_report / validate_param_card）+ README 漂移守卫 + 信源健康 + MCP 同步 + FRED
├── benchmarks/                   # 5 题固定基准 + Q6 销售路由回归题 + 分数演化记录
├── tests/                        # pytest 测试
├── sources.registry.yaml         # 信源注册表（default / optional / deprecated 三层）
├── install.sh / install.ps1      # 一键安装脚本（Unix / Windows）
├── LICENSE                       # MIT
├── CONTRIBUTING.md               # 贡献指南
└── .gitignore
```

> Skill 核心**自包含**：所有工作流、模板、规则都内嵌在 `SKILL.md` 中，无需额外脚本或配置文件；`references/` 仅是可选项增强工具接入指南，缺失不影响主流程。

---

## ⚙️ 可选数据源与增强 Skill

Skill 本身调用 Agent 内置联网工具（WebSearch / WebFetch）即可工作。若 Agent 已装以下 Skill 或连以下 MCP，会自动获得更强深度；**缺失时一律优雅降级，不会中断调研**。

> **完整数据源表（30+ 维度：搜索入口、社媒热评、学术论文、财经、法律、专利等）已移至 [references/data-sources.md](references/data-sources.md)**

---

## ❓ 常见问题与完整示例

- **FAQ（8 问）**：见 [references/faq.md](references/faq.md)
- **端到端示例**：见 [references/example.md](references/example.md)（工业机器人赛道调研）
- **完整更新史**：v2.0.0 → v2.7.1 — 见 [CHANGELOG.md](CHANGELOG.md)（v2.7.1 为 install.sh 热修复）

---

## 📜 许可证

[MIT License](LICENSE)
