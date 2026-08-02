# v2.3.4 — SKILL.md 模块化拆分 + 质量增强

> **2026-08-03** · 结构性拆分 + 功能增强（v2.3.3 拆分 + v2.3.4 增强，合并发布）

---

## Highlights

- SKILL.md 模块化拆分：845 行 → 380 行（核心文件 <=500 行目标）
- 质量规则 21-23：源独立性判定 / 外部审稿定位 / 收益递减软指南
- 研究参数卡结构化：8 字段表替换散文描述
- 4 套模板追加搜索后端透明度声明
- runtime 探测行为说明：try-and-skip

## What's Changed

### Added
- 质量规则 21：源独立性判定 3 条规则（引用链去重 / 通讯社转载去重 / 企业自述区分）
- 质量规则 22：外部审稿是质量增强层非质量必需，缺失不降级
- 质量规则 23：收益递减饱和度判断是软指南非硬停
- 终稿纪律第 6 条：可选外部审稿钩子（gpt-researcher-team / consulting-analysis）
- 研究参数卡结构化：8 字段表，Step 0 追加初始化入口
- Step 1 饱和度指南：来源>=5 且最近 3 次搜索无新独立信息时可考虑提前进入 Step 4
- runtime 探测行为说明：try-and-skip（尝试调用并捕获失败，不预检）
- 4 套模板各追加搜索后端类型 + 覆盖局限声明字段
- references/templates.md、optional-modules.md、faq.md、example.md 四个新文件

### Changed
- SKILL.md 模块化拆分：845 → 380 行，frontmatter compatibility 从 47 行压缩至 10 行
- 新增参考文档索引节集中列出所有参考文件入口

### Not Adopted
- 查询路由器 (Step 0.5)：与"不跳步"硬规则冲突
- 新建 active_sources.yaml：sources.registry.yaml + source_health.py 已覆盖