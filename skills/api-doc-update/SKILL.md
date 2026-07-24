---
name: api-doc-update
description: 更新/生成接口文档。运行 pnpm api:generate 拉取最新 OpenAPI 并留存历史快照，对比上一版生成中文变更报告（含破坏性标注）与代码影响分析。当用户表达「更新接口文档 / 生成接口 / 更新接口 / 对比接口变动 / openapi 更新」等意图时使用。
---

# Skill：更新接口文档（api-doc-update）

> **权威流程唯一来源**：本技能的完整步骤以 [`.kiro/skills/api-doc-update/SKILL.md`](../../../.kiro/skills/api-doc-update/SKILL.md) 为准。
> 请先读取该文件并严格按其步骤执行；本文件仅为 Claude Code 的技能入口与摘要，避免多处维护导致不一致。

## 何时触发

用户表达「更新接口文档 / 重新生成接口 / 看看接口有哪些变动 / openapi 更新」等意图时。

## 流程摘要（详情见权威来源）

1. **前置校验**：确认 `SWAGGER_URL` 已在 `env/.env.*` 配置；未配置则中止并中文提示。
2. **运行脚本**：执行 `pnpm api:generate`。脚本会拉取 OpenAPI 原文、与最新快照做规范化等价比较，**仅在有变化时**新建 `docs/api-history/{时间戳}/openapi.json` 并更新索引，同时生成 `api/generated/Api.ts`。失败则中止并中文汇报。
3. **解析结果**：读取脚本输出末尾 `[generate-api:result] {json}` 行，得到 `changed` / `isFirst` / `versionDir` / `prevDir` / `source`。
4. **分支**：
   - `changed=false`：中文汇报「接口无变化，未新建版本」，结束。
   - `changed=true & isFirst=true`：写「首个版本，无对比基线」报告到 `{versionDir}/changes.md`。
   - `changed=true & isFirst=false`：对比 `{versionDir}/openapi.json` 与 `{prevDir}/openapi.json` 生成完整报告。
5. **变更清单**：按「新增 / 删除 / 修改接口」三类逐条列出（方法 + 路径），修改项 diff 参数/请求/响应结构，按破坏性判定表标注 `⚠️ **[破坏性]**`。
6. **影响分析**：operationId → `Api.ts` 方法名（camelCase，如 `charactersList`）→ grep `.<方法名>(` 调用点（聚焦 `@/api` 的 `clientApi` / `serverApi` / `useApiClient()`），列出受影响文件与影响类型。
7. **回填索引**：将 `docs/api-history/README.md` 中该版本行「变更摘要」列的占位 `_（待生成）_` 回填为实际摘要。
8. **汇报**：中文汇报新增/修改/删除数量、破坏性条数、受影响文件与 `changes.md` 路径。

## 约束

- 只快照源头 `openapi.json`，不快照 `Api.ts`（后者由脚本生成、禁止手改，且已在 git 有历史）。
- 报告与汇报一律中文。破坏性判定表与 `changes.md` 模板见权威来源文件。
- 最多保留最新 10 个版本，超出由脚本自动清理。
