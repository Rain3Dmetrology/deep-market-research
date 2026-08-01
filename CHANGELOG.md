# Changelog

## [Unreleased]

### Added
- 源健康监控原型（maintainer-side CI）：
  - `scripts/source_health.py`：探测各信源存活 + 静态 PR 一致性门禁（双向 parity）。
  - `sources.registry.yaml`：信源注册表；`fred` 标 `layer: optional`（宏观维度已由 WebSearch 无 key 覆盖，其死亡不计入 `dimensions_uncovered`）。
  - `.github/workflows/source-health.yml`：每日 06:00 UTC 运行；DEPRECATED 源仍被引用为活跃路由则阻断 CI，盲区/孤儿探针仅告警。
- `tests/test_source_health.py`：首个真实单元测试（8 测全过），覆盖 fred-optional 门禁、`dimensions_uncovered` 聚合、双向 parity、DEPRECATED 阻断、URL 掩码。

### Docs
- 审查局限处置（对应工程审查报告 §8）：
  - **ADR 编号冲突**：审计评估 lineage 与编排 lineage 的两个 "ADR-2" 已用 `A-`/`O-` 前缀消歧（见报告 §2）。
  - **LLM-eval 质量带**：需 golden 语料 + judge 模型，属后续投入，**非阻塞**，列入 backlog。
  - **仓库零测试**：已通过建立 `tests/` 脚手架 + CI 解决；其余模块（SKILL 编排 / 各 MCP 连接器）测试仍待补，列入 backlog。

> 注：本次为局部增强，未升版本号（仍为 v2.3.1）。
