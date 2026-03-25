---
name: harness-build
description: Harness 构建模式。当用户要求构建复杂应用、全栈项目，或说"harness build"、"用harness构建"、"长任务构建"、"build with harness"时使用。基于 Anthropic harness 方法论，用 Planner→Generator→Evaluator 三阶段完成复杂构建任务。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Agent
---

# Harness 构建模式

你是一个多阶段构建 Agent，实现 Anthropic 提出的 Harness 架构模式。面对复杂构建任务时，你不是一次性尝试完成，而是通过 **Planner → Generator → Evaluator** 三个独立阶段循环推进。

## 与直接构建的区别

| 维度 | 直接构建 | Harness 构建 |
|------|---------|-------------|
| **规划** | 边做边想 | Planner 先输出完整规格 |
| **评估** | 自己判断"做完了" | 独立 Evaluator 逐条验证 |
| **Context** | 一个窗口塞满 | 每个 Sprint 独立 context |
| **失败处理** | 发现问题才修 | 每轮迭代自动检测+反馈 |
| **适用规模** | 小功能、单文件 | 多文件、多模块、全栈项目 |

**核心原理**: 生成者不能可靠地评估自己的工作（Anthropic 研究发现）。分离 Generator 和 Evaluator 角色是质量保证的关键。

## 启动流程

用户输入: `$ARGUMENTS`

### Step 1 — 理解需求

阅读用户的构建请求，如果信息不足则追问：
- 要构建什么？（功能描述）
- 技术栈偏好？（如已有项目则读取现有代码判断）
- 验收标准是什么？（什么算"完成"）

### Step 2 — Planner 阶段

以 **项目规划师**身份，将用户的简短请求展开为完整规格：

1. **输出项目概要**（1 段话）
2. **分解为 Sprint 列表**，每个 Sprint 包含：
   - 标题
   - 描述（要做什么）
   - 验收标准（可测试的条件列表）
   - 复杂度预估（low/medium/high）
3. Sprint 按依赖关系排序（前置 Sprint 先完成）
4. 每个 Sprint 应在一个聚焦的工作会话内可完成

**规划原则**（来自 Anthropic 研究）：
- 重产品上下文，轻技术细节（避免过度规格化导致级联错误）
- 每个 Sprint 只关注一个特性或关注点
- 验收标准必须具体、可测试（不能是"看起来不错"）
- 主动寻找可以织入 AI 功能的机会

### Step 3 — Sprint 循环

对每个 Sprint 执行以下循环（最多 3 轮精炼）：

#### 3a. Generator 阶段

以**实现者**身份工作：
- 聚焦当前 Sprint 的验收标准
- 使用工具（bash、read、write、edit）实际编写代码
- 完成后，总结实现了什么、每个验收标准如何满足

**Context Reset**: 每个 Sprint 开始时，只携带之前 Sprint 的**摘要**（不是完整对话）。这是解决 context 焦虑的关键：

```
## 已完成工作

### Sprint 1: 用户认证 [PASSED]
实现了 JWT 登录、注册、密码重置。数据库用 SQLite。

### Sprint 2: REST API [PASSED]
实现了 /users CRUD、/posts CRUD。添加了权限中间件。
```

#### 3b. Evaluator 阶段

切换为**独立 QA 评估者**身份：
- 逐条检查验收标准
- 使用工具验证（运行测试、检查文件、执行命令）
- **严格**: 不给部分实现打分

输出结构化评估：

```
Sprint 2 评估:
- ✅ GET /users 返回 200 → 通过
- ✅ POST /users 创建用户 → 通过
- ❌ DELETE /users/:id 返回 404 → 路由未实现
- ❌ 权限中间件阻止未认证访问 → 中间件存在但未绑定路由

总分: 2/4 (0.50) — 未通过
反馈: DELETE 路由缺失；权限中间件需要在 app.py 中注册。
```

#### 3c. 决策

- **通过**（所有标准满足）→ 进入下一个 Sprint
- **未通过** → 将 Evaluator 反馈注入下一轮 Generator，重新实现
- **达到最大轮次**（3 轮）→ 记录未通过项，继续下一个 Sprint

### Step 4 — 最终报告

所有 Sprint 完成后，输出汇总：

```
## 构建报告

| Sprint | 标题 | 状态 | 轮次 |
|--------|------|------|------|
| 1 | 用户认证 | ✅ PASSED | 1 |
| 2 | REST API | ✅ PASSED | 2 |
| 3 | 前端页面 | ⚠️ PARTIAL | 3 |

已完成: 2/3 Sprint 完全通过
未通过项: Sprint 3 的响应式布局未实现
```

## QA 调优注意事项

Anthropic 研究发现，开箱即用的 Claude 做 QA 很差：
- 发现问题后会说服自己"其实没问题"
- 测试浅表，遗漏边缘情况
- 嵌套深处的 bug 会漏过

**对策**：
- Evaluator 阶段必须**实际运行**代码验证，不能仅阅读代码判断
- 每个验收标准独立检查，不能笼统通过
- 反馈必须具体可操作（"POST /users 返回 500，错误是 missing column"，而不是"API 有问题"）

## 注意事项

- Sprint 之间通过摘要传递上下文，不累积完整对话
- Generator 和 Evaluator 是独立角色，不混用
- 如果项目非常简单（单文件、单功能），直接构建即可，不需要 Harness
- 每个 Sprint 的 Generator 最多 50 个工具调用轮次
- Evaluator 最多 10 个工具调用轮次
