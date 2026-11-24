# CN / Global 搜索 Provider 固定基准（Pilot）

> 状态：**基准规格已固定，真实 Provider 执行待逐项授权**。本基准评估搜索检索质量，不评估 DMR 最终报告质量。
> 机器可读题目和 Provider 矩阵见 search-provider-baseline.yaml。

## 1. 范围与首轮对象

首轮只验证当前路由最重要的两组候选：

| 市场 | 候选 A | 候选 B | 固定查询数 | 请求数 |
|---|---|---|---:|---:|
| CN | Metaso Web | Bocha Web Search | 4 | 8 |
| Global | Octen Search | Exa Search | 4 | 8 |
| **合计** | 4 Provider | 同题对照 | **8** | **16** |

每个 Provider 对其市场的 4 个 query 各搜索一次，每次最多返回 10 个结果。首轮不测 Search1API、Tavily、SerpAPI 或 Firecrawl；这些是缺口驱动的条件补充，不扩大首轮矩阵。

**能力与可调用性边界：**当前 ChatGPT 会话有 Octen / Exa 连接器，没有可直接调用的 Metaso / Bocha 工具。因此本会话不能声称已完成 CN Provider 实测。CN 两家需在 DMR 宿主已连接的 Provider 环境执行。无论在哪里执行，都保存同一份 JSONL Run Record。

## 2. 固定查询集

| ID | 市场 | 任务类型 | 主要检验点 |
|---|---|---|---|
| CN-01 | 中国 | 厂商格局 | 中文召回、国内厂商覆盖、官方产品页与案例 |
| CN-02 | 中国 | 官方产品规格 | 精确型号命中、官方参数完整性 |
| CN-03 | 中国 | 技术论文 / 专利 | 原始专利、论文元数据与全文的区分 |
| CN-04 | 中国 | 新品 / 时效 | 2025-11-22 至 2026-11-22 的发布时间和事件时间 |
| GL-01 | Global | 厂商格局 | 全球厂商覆盖，不局限单一市场 |
| GL-02 | Global | 官方产品规格 | KEYENCE / Cognex 原始规格、精确参数 |
| GL-03 | Global | 技术论文 | DOI、作者、期刊、出版日期、原始出版页 |
| GL-04 | Global | 负面 / 现场限制 | 反光、镜面、透明件测量失败模式与独立发布者 |

查询原文、金标准 URL / 域名和适用性说明锁定在 YAML 中。若要修改题目，必须提升 benchmark 版本并保留旧版本，不得悄悄换题后横向比较。

## 3. 请求参数约束

- 使用 YAML 中完全相同的 query 文本；不能按 Provider 改写成不同意思。
- 每次请求 result_limit = 10，只使用普通 Web Search 能力。
- Metaso 使用 webpage scope；不得混入 Document / Scholar AI 答案模式。
- Bocha 使用普通 Web Search，不使用 AI Search 答案模式或额外 Reranker。
- Octen 使用单次 search，不使用 broad_search。
- Exa 使用普通 Search，最多 10 条，不使用 Agent / Deep Research。
- 不添加域名过滤，不抓取全文，不调用 Extract / Crawl，不做二次搜索，不自动重试。
- 记录每次请求开始时间（UTC）、总延迟、结果条数、Provider 状态、实际用量和原始结果快照哈希。
- 不同 Provider 难以完全统一的语言、地理和新鲜度参数必须在 Run Record 披露。不能单独给某家增加过滤条件后仍声称严格同参数对照。

上述设置把首轮上限固定为 16 次搜索请求，不会因为 Broad Search 再展开额外子查询。

## 4. 评分口径

每个结果由人工按同一 rubric 标注：

| 字段 | 取值 | 判断方式 |
|---|---|---|
| relevance | 0 / 1 / 2 | 0 无关；1 部分相关；2 直接支持题目 |
| source_tier | T1 / T2 / T3 / T4 / unknown | 沿用 DMR 证据分级 |
| publisher_group | 稳定发布者集团 ID / unknown | 同一母公司、机构或作者体系只计一个独立发布者 |
| upstream_group | 已知上游 ID / unknown | 未知不得根据搜索品牌猜测 |
| published_at | ISO 日期或 null | 原始内容发布日期，不是抓取日期 |
| event_date | ISO 日期或 null | 事件发生日期，和发布日期分开 |
| event_date_verified | true / false / null | 有原始时间线或一手来源支持才标 true |

主要指标：

1. **Precision@5**：前 5 个名次中 relevance ≥ 1 的数量 / 5；同时报告严格相关率（relevance = 2 / 5）。不足 5 条结果时缺失名次也占分母。
2. **Official / primary anchor recall@10**：YAML 金标准 URL / domain 在前 10 条中的命中比例。没有锚点的题目记 N/A，不人为补造。
3. **Unique documents / independent publishers**：按 canonical URL、内容 hash 和 publisher_group 去重；unknown 不计为已证实的独立发布者。
4. **Incremental publisher coverage**：相对同市场另一个候选新增的 publisher_group 数；不能把同集团多个域名算成多个发布者。
5. **Duplicate rate**：相同 canonical URL / 内容指纹在单一 Provider 结果中的重复率；另报两个 Provider 的跨源 URL 交集率。
6. **Freshness / date accuracy**：只对有日期要求的题目统计发布日期窗口合规率，同时报告发布日期覆盖率；事件时间另行核验。
7. **Latency**：记录单次请求延迟。每家只有 4 个样本，p50 / p95 只能作小样本描述，不是稳定 SLA。
8. **Cost**：只记录实际 Provider usage / 账单 / 余额差值。无法确认时标 unknown；订阅含量标 included，不得写成 0。
9. **Failure / fallback**：保留失败状态和错误分类；本轮不自动重试。只有路由明确触发时才记录 fallback，并注明是否成功。

不生成隐藏权重总分，不因为返回条数多或耗时短就判 Provider 更优。

## 5. Run Record 最小结构

每行 JSONL 对应一个 query_id + provider_id；每次执行需保留完整 16 行（失败和跳过也必须记录）：

    {
      "run_id": "2026-11-22-pilot-01",
      "requested_at": "2026-11-22T12:00:00Z",
      "query_id": "CN-01",
      "provider_id": "metaso_web",
      "provider_parameters": {},
      "raw_results_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "request_status": "success",
      "latency_ms": 820,
      "result_limit": 10,
      "cost_status": "unknown",
      "billed_cost": null,
      "cost_currency": null,
      "fallback_attempted": false,
      "fallback_provider": null,
      "fallback_status": "not_attempted",
      "results": [
        {
          "rank": 1,
          "title": "Example title",
          "url": "https://example.com/product",
          "canonical_url": "https://example.com/product",
          "publisher": "Example Corp",
          "publisher_group": "example-corp",
          "upstream_group": "unknown",
          "published_at": null,
          "event_date": null,
          "event_date_verified": null,
          "source_tier": "T1",
          "relevance": 2,
          "content_hash": null
        }
      ]
    }

以上是字段结构示例，不是实际 Provider 结果。不要保存 Authorization、Cookie、API key、完整请求头或不必要的原始响应。原始结果可另存脱敏文件并记录 SHA-256。

## 6. 完成与晋级门槛

**Pilot 完成：**
- 16 个请求都有一行记录；失败、跳过也如实记录。
- 每个成功结果的前 5 条都完成人工相关性标注。
- 金标准命中、publisher_group、日期与成本均有核验依据；未知值不补猜。
- 评估脚本报告每 Provider / 每 query 指标、请求失败和跨 Provider 重复命中。
- 不产生自动 winner / quality-pass 结论。

**晋级为默认优先 Provider：**这 8 条 Pilot query 只用于初筛，不足以证明长期质量优势。只有候选在至少 20 条独立固定查询、不同时间复跑后，持续提高相关性和独立发布者覆盖，同时成本、延迟和失败率满足预算，才可考虑调整默认路由。

## 7. 当前执行授权状态

| Provider | 当前可调用性 | 提议请求数 | 授权状态 |
|---|---|---:|---|
| Metaso Web | 本会话没有直连工具；需 DMR 宿主连接 | 4 | 待单独授权 |
| Bocha Web | 本会话没有直连工具；需 DMR 宿主连接 | 4 | 待单独授权 |
| Octen Search | 本会话有连接器 | 4 | 待单独授权 |
| Exa Search | 本会话有连接器 | 4 | 待单独授权 |

没有逐 Provider 的请求次数和成本上限前，不发起可能计费请求。当前阶段只完成基准设计和离线评分器，不把协议握手或文档检索写成真实搜索质量通过。
