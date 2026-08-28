# Contributing to Deep Market Research Skill

感谢你考虑贡献！本仓库遵循 [Agent Skills 开放标准](https://agentskills.io/)，保持 Skill 自包含、跨平台。

## 开发约定

1. **单一 `SKILL.md` 入口**：核心方法论与规则写在 `SKILL.md` 内；5 套输出模板外置于 `references/templates.md`；`scripts/` 为可选运行时校验钩子（缺失不阻断主管线），不依赖必选的外部脚本或配置文件。
2. **frontmatter 兼容**：`SKILL.md` 顶部 YAML 至少包含 `name` 和 `description`（`description` 用于 Agent 判断何时触发，请写清触发场景与关键词）。
3. **质量优先**：任何方法论改动都需保持「源分级 + ≥2 源交叉验证 + 矛盾显式标注」的硬规则。
4. **防过度约束**：新增分析透镜/数据源必须可选、按意图触发，不引入数量 KPI（如“≥N 轮检索”“≥N 图”）。
5. **版本号**：改动后递增 `metadata.version`（语义化），并在 commit 说明中记录变更。

## 提交流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feat/your-change`)
3. 提交改动 (`git commit -m "feat: ..."`)
4. 推送并创建 Pull Request

## 兼容性

改动需确保 Skill 仍能被 Claude Code / OpenAI Codex / TRAE / Qoder / WorkBuddy 等 agentskills 兼容平台正常加载。

## 许可证

贡献即表示你同意以 [MIT License](LICENSE) 发布你的贡献。
