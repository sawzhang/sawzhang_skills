---
name: sdd
description: Harness Engineering 全流程开发 - 从 feature spec 到 PR 合并，Agent 自主完成 设计→规划→TDD 实现→代码审查→修复→PR 的完整 loop，全程使用 subagent 隔离执行，人工只在设计确认和 BLOCKED 时介入。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Agent
---

# SDD — Subagent-Driven Development (Harness Engineering)

完整的 Harness Engineering 软件开发 loop。所有「执行性质的工作」都由 subagent 完成，本 Skill 只做编排。

## Harness Engineering vs. Vibe Coding

**核心判断标准**（来自 @kasong2048）：

> 你有没有一个完整的环境，可以对 Agent 的行为进行**约束、观测、校验、回退**？
>
> - 有 → Harness Engineering（Agent 自主完成全部编码）
> - 没有 → Vibe Coding（需要人工介入）

本 Skill 就是这个「完整环境」：

| Harness 属性 | 在本 Skill 中的体现 |
|------------|-----------------|
| **约束** | Subagent 在 git worktree 中工作，任务边界由 plan 明确定义，不能触碰范围外的文件 |
| **观测** | 每个 subagent 返回 `DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED` 状态，审查 subagent 输出结构化报告 |
| **校验** | 测试必须通过 → lint/format 必须通过 → spec compliance review → code quality review → CI 验证 |
| **回退** | 测试失败 → rollback worktree；review 3 次不过 → 上报用户；BLOCKED → 暂停等待 |

## 触发时机

- 用户提供 feature/bug 描述，希望 Agent 自主完成全部开发
- 用户说"自主开发"、"帮我实现"、"sdd"、"harness 开发"
- 有清晰的任务范围，不需要每步都确认

**不适用场景**：
- 需要频繁探索性讨论 → 先用 brainstorming
- 任务范围极不清晰 → 先澄清再启动
- 纯修改 SKILL/文档（自然语言无法完整验证）→ 人工 Vibe Coding

## 完整流程

```
Feature Spec
    │
    ▼
Phase 1: 设计          → dispatch design-subagent
    │ ← 用户确认（唯一强制人工介入点）
    ▼
Phase 2: 规划          → dispatch planning-subagent
    │
    ▼
Phase 3: 建立 Worktree → git worktree + 环境初始化
    │
    ▼
Phase 4: 实现循环      → 每个 task: impl-subagent → spec-review → quality-review
    │
    ▼
Phase 5: 质量关卡      → 测试套件 + lint + coverage 检查
    │
    ▼
Phase 6: PR 创建       → gh pr create，等待 CI
    │
    ▼
Phase 7: Review 修复   → dispatch fix-subagent per review comment → push → merge
```

---

## Phase 1：设计

**dispatch design-subagent（最强模型）**

给 subagent 的上下文：
- feature/bug 的完整描述
- 相关代码文件路径（不是内容，让 subagent 自己读）
- 项目约束（CLAUDE.md / AGENTS.md 中的规则）
- 输出路径：`docs/specs/YYYY-MM-DD-<feature>.md`

设计文档应包含：
- 目标与非目标（scope 边界）
- 架构方案（2-3 个备选 + 推荐）
- 关键接口定义
- 边界情况处理
- 不做哪些事（明确排除）

**人工确认**：设计文档完成后，向用户展示摘要，等待确认或修改意见。这是整个流程唯一的强制人工介入点。

---

## Phase 2：规划

**dispatch planning-subagent（标准模型）**

给 subagent 的上下文：
- 已确认的设计文档全文
- 项目结构（通过 glob 获取文件列表）
- 技术栈和测试框架信息

输出：`docs/plans/YYYY-MM-DD-<feature>.md`

规划文档格式：
```markdown
## 任务列表

### Task 1: <名称>
**文件**: src/foo/bar.ts, src/foo/bar.test.ts
**描述**: ...
**验证步骤**: pnpm test src/foo/bar.test.ts
**依赖**: 无

### Task 2: <名称>
...
```

每个 task 要求：
- 粒度：2-5 分钟实现，单一职责
- 包含明确的测试文件路径
- 包含可执行的验证命令
- 标注依赖关系（串行 vs. 可并行）

---

## Phase 3：建立 Worktree

```bash
# 检查 worktree 目录配置（优先 .worktrees/，其次 worktrees/）
# 验证已在 .gitignore 中
git worktree add .worktrees/<feature-name> -b feat/<feature-name>

# 自动检测并初始化环境
# Node.js: npm/pnpm/yarn install
# Python: uv sync / pip install -e .
# Rust: cargo build

# 验证干净基线：运行测试，确认全部通过
```

---

## Phase 4：实现循环

**对每个 task 串行执行**（注意：不并行，防止文件冲突）：

### Step 4a：dispatch implementation-subagent

**关键原则**：subagent 不继承你的上下文，你需要构造完整的任务包。

给 implementation-subagent 的 prompt 模板：
```
## 任务
<task 完整文本，从 plan 文件提取>

## 场景
你在实现 <feature 名称> 的一部分。
设计文档在 <路径>，你可以读取它了解整体方向。

## 工作目录
<worktree 绝对路径>

## 要求
1. 遵循 TDD：先写失败的测试，再写实现，确认测试通过
2. 完成后运行：<验证命令>
3. 提交代码（使用 conventional commit 格式）
4. 如遇到阻碍，立即上报，不要猜测

## 返回状态
完成后以下列格式回复：
STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
SUMMARY: <一句话总结>
CONCERNS: <如有，列出>
QUESTIONS: <如有，列出>
COMMIT: <commit sha>
```

### Step 4b：处理 subagent 状态

| 状态 | 处理方式 |
|------|---------|
| `DONE` | 进入 spec compliance review |
| `DONE_WITH_CONCERNS` | 先读 concerns，判断是否影响正确性，再决定是否先修复还是直接进 review |
| `NEEDS_CONTEXT` | 提供缺失的上下文，重新 dispatch（同模型） |
| `BLOCKED` | 评估原因：上下文问题→补充上下文重 dispatch；任务太大→拆分；plan 有误→上报用户 |

**永远不要** ignore BLOCKED 或强迫同一 subagent 重试而不做任何改变。

### Step 4c：dispatch spec-reviewer-subagent

给 reviewer 的上下文：
- 设计文档全文
- plan 中该 task 的完整文本
- commit sha 和变更的文件列表（用 `git diff <base>..<commit>` 输出）

reviewer 检查：
- 实现是否覆盖了 spec 要求的全部功能
- 是否有多余实现（超出 spec 的功能）
- 测试是否覆盖了 spec 描述的场景

返回：`✅ SPEC_PASS` 或 `❌ SPEC_FAIL: <具体缺失/多余项列表>`

### Step 4d：dispatch quality-reviewer-subagent

**只在 spec review PASS 后才启动**（顺序不能错）。

给 reviewer 的上下文：
- code diff（完整内容）
- 项目的 lint/format 规则（从配置文件读取）
- 项目的 code style 样例（从同类文件读取 2-3 个）

reviewer 检查：
- 代码质量（可读性、命名、单一职责）
- 测试质量（非 mock 实现细节、测试边界情况）
- 性能和安全（明显问题）
- 格式规范（lint/format）

返回结构：
```
DECISION: APPROVED | CHANGES_REQUESTED
CRITICAL: <阻塞合并的问题>
IMPORTANT: <强烈建议修改的问题>
MINOR: <可选改进>
```

### Step 4e：修复循环

如果 review 返回 `CHANGES_REQUESTED`：
1. dispatch fix-subagent，提供：review 报告全文 + 原始 task 上下文 + diff
2. fix-subagent 修复后提交
3. 重新进行对应阶段的 review
4. 最多 **3 轮修复**（spec 和 quality 各自独立计数）
5. 3 轮后仍不过 → 上报用户，暂停

完成一个 task 后，更新 TodoWrite 标记该 task 完成，再进入下一个。

---

## Phase 5：质量关卡

所有 tasks 完成后，在 worktree 中运行完整质量检查。**全部通过才能进入 Phase 6。**

### 必须通过的检查

```bash
# 1. 完整测试套件（优先运行，失败直接 rollback）
pnpm test           # 或 npm test / pytest / cargo test

# 2. Lint 和格式检查
pnpm lint           # 或对应命令
pnpm format:check   # 或 prettier --check

# 3. 类型检查（TypeScript 项目）
pnpm tsgo           # 或 tsc --noEmit

# 4. 构建验证（如有 dist 变化）
pnpm build
```

### 可选检查（项目有配置才运行）

```bash
# 测试覆盖率（如有 coverage 配置）
pnpm test:coverage
# 失败条件：新增代码的行覆盖率 < 项目配置的阈值

# 架构边界检查（如有自定义 scripts）
pnpm check:boundaries   # 或等效命令

# 重复代码检测
pnpm dup:check
```

### 检查失败的处理

| 失败类型 | 处理方式 |
|---------|---------|
| 测试失败 | dispatch debug-subagent，根因分析后修复，重新运行全部测试 |
| Lint 失败 | dispatch fix-subagent，自动修复（通常可 `lint:fix` 解决） |
| 类型错误 | dispatch fix-subagent，修复类型问题，重新类型检查 |
| 覆盖率不足 | dispatch test-subagent，补充测试用例，重跑 |
| 构建失败 | 分析错误，dispatch fix-subagent，重新构建 |

---

## Phase 6：PR 创建

```bash
# 推送分支
git push -u origin feat/<feature-name>

# 创建 PR
gh pr create \
  --title "<conventional commit 风格标题，<70字符>" \
  --body "$(cat <<'EOF'
## 变更摘要
<3-5 bullet points>

## 实现细节
<关键设计决策>

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过（如有）
- [ ] 覆盖率满足阈值（如有）

## 验证步骤
<人工验证的步骤（如有）>

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

等待 CI 结果：
- CI 通过 → 进入 Phase 7（等待 review）或直接 merge（如无 review 要求）
- CI 失败 → 分析失败日志，dispatch fix-subagent，push fix commit

---

## Phase 7：Review 修复循环

收到 PR review 反馈后：

1. 对每个 reviewer comment，评估严重程度：
   - **CRITICAL**（阻塞合并）→ 必须修复
   - **IMPORTANT**（强烈建议）→ 评估后决定
   - **MINOR**（可选）→ 可 defer

2. 对需要修复的 comment，dispatch fix-subagent：
   - 提供 comment 全文 + 被评论的代码上下文
   - 修复后 push，reply comment 说明修改

3. 等待 reviewer approve，merge PR。

---

## 模型选择策略

| 角色 | 推荐模型 | 原因 |
|------|---------|------|
| design-subagent | 最强（opus） | 需要架构判断力 |
| planning-subagent | 标准（sonnet） | 结构化分解任务 |
| implementation-subagent（简单 task，1-2 文件） | 快速（haiku） | 机械实现 |
| implementation-subagent（复杂 task，多文件协调） | 标准（sonnet） | 集成判断 |
| spec/quality reviewer | 标准（sonnet） | 需要理解上下文 |
| debug-subagent | 最强（opus） | 根因分析 |

---

## 人工介入点

| 时机 | 原因 | 如何处理 |
|------|------|---------|
| Phase 1 完成后（设计确认） | 确保方向正确，避免后续全部返工 | 展示设计摘要，等待 confirm |
| subagent 状态为 BLOCKED | 超出 subagent 能力范围 | 分析 blocker，决策后继续 |
| 质量关卡 3 次修复后仍失败 | 可能是根本性问题 | 上报，暂停，等待用户决策 |
| CI 持续失败（3 次） | 可能是环境/基础设施问题 | 上报 CI 失败详情，等待 |

---

## Red Flags

**永远不要**：
- 在 main/master 分支直接工作（必须用 worktree + feature branch）
- 跳过 spec compliance review 直接做 quality review（顺序固定）
- 并行派发多个 implementation-subagent（会产生文件冲突）
- 让 subagent 继承主 session 上下文（每次构造完整任务包）
- quality review 有 CRITICAL 问题时继续创建 PR
- ignore BLOCKED 状态，强迫重试
- 3 轮修复后仍继续循环（上报用户）
- 在 Phase 5 质量关卡失败时直接创建 PR

**注意**：
- Subagent 问题 → 回答后重 dispatch（不是继续当前 subagent）
- 修复用 fix-subagent，不要主 session 手动改代码（context pollution）
- 每次给 subagent 的 prompt 要自包含（subagent 不会看到主 session 的历史）

---

## 与 Superpowers 的集成

如果项目已安装 superpowers：
- `superpowers:brainstorming` → 替代 Phase 1 的 design-subagent
- `superpowers:writing-plans` → 替代 Phase 2 的 planning-subagent
- `superpowers:using-git-worktrees` → Phase 3 的 worktree 创建
- `superpowers:test-driven-development` → implementation-subagent 内部遵循
- `superpowers:finishing-a-development-branch` → Phase 6 的 PR 创建
