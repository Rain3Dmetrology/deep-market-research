# Run Contract v1（DMR 唯一定义，ResearchTeam 消费）

适用于新增本机可持久化的研究执行与 Team 会话。宿主无文件能力时可输出同构记录，明确未持久化，不得宣称已归档。既有报告 lint 不是运行验收证明。

## 预算契约

- 先核实具体 Provider、操作、报价/账户额度和授权上限；按币种/credit 分账，禁止把不同币种或不同 Provider 的 credit 相加为账单。
- 调用前预留有依据的费用上界及调用次数；无法确定有授权且可控的上界时，不发起可能计费的调用。所有搜索、读取、探测、回退、重试均计数，超时/未知费用保留预留，禁止重置已发出请求。
- `scripts/run_contract.py` 的 BudgetLedger 是单进程线程安全的离线准入参考。跨进程/Agent 要由唯一拥有者核发不重叠额度或通过同一准入器；否则仅可标 soft_limit。hard_limit 仅在确实控制所有受限调用且上界可信时使用。
- 实际费用仅在有账单/使用记录时标 reported；明确免费且有依据标 free_confirmed；unknown/included 的 actual 为 null。标价、估价不是实际账单。实际超过预留上界时停止新增调用并记 overrun。

## run-manifest.json

| 字段 | 约束 |
|---|---|
| run_contract_version / run_id | 1 / 本次唯一标识 |
| query / param_card | 原始问题与 Evidence Contract v1 参数卡 |
| component_versions | DMR 版本/提交；Team 模式附 Team 版本/提交 |
| budget_enforcement / budget_overrun | hard_limit / soft_limit / not_applicable；是否超额，未知为 null |
| max_calls / budget_limits | hard_limit 必填；非负整数调用上限、按 Provider 分列的 currency 和 cap |
| calls | 请求 ID、Provider、操作、脱敏参数、upper_bound/currency/pricing_evidence、耗时、cost_status、actual、cost_evidence、响应快照引用及失败/回退状态；hard_limit 必须对账，未知/含额费用按上界保留 |
| evidence_pool / decisions | 原始文档与主张、支持/反证、去重裁决与降级 |
| degradation_events | 降级、未执行项、错误与环境限制 |
| acceptance | 非空列表，每项 id 与 pass/fail/unverified 状态，附可核实证据 |
| stop_reason | 达标、轮次耗尽、预算耗尽、阻塞、中止等实际原因 |
| outcome | passed / partial / failed / cancelled；有未通过、未核验或预算超额/未知不得 passed |

所有记录不写密钥、请求授权头、含凭据 URL 或私有响应到公开仓库；使用本地受保护目录，原始响应先完整落盘再解析、哈希，不得用截断文本代替。按任务授权决定是否持久化知识。

`python scripts/run_contract.py <manifest.json>` 为元数据门禁。PASS 仅代表字段和终态一致；不能证明实际账单、历史准入或主张正确。
