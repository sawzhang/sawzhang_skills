---
name: harness
description: Harness 方法论工具箱（基于 Anthropic 研究）。当用户说"harness"、"harness build"、"harness qa"、"harness plan"、"用harness构建"、"独立评估"、"评估一下"、"qa check"、"规划一下"、"分解为sprint"时使用。包含三种模式：构建（Planner→Generator→Evaluator）、QA（独立评估）、规划（Sprint 分解）。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Agent
---

# Harness 方法论工具箱

基于 [Anthropic Harness 研究](https://www.anthropic.com/engineering/harness-design-long-running-apps)的多 Agent 编排方法论。根据用户请求路由到对应模式：

| 用户说 | 模式 |
|--------|------|
| "harness build"、"用harness构建"、"长任务构建" | → [构建模式](#构建模式) |
| "harness qa"、"独立评估"、"评估一下"、"qa check" | → [QA 模式](#qa-模式) |
| "harness plan"、"规划一下"、"分解为sprint" | → [规划模式](#规划模式) |
| "harness"（无子命令） | → 展示此路由表，询问用户需求 |

**核心理念**：生成者不能可靠评估自己的工作。分离 Generator 和 Evaluator 角色是质量保证的关键。

---

## 构建模式

完整的 Planner→Generator→Evaluator 三阶段循环。适用于多文件、多模块的复杂构建任务。

| 维度 | 直接构建 | Harness 构建 |
|------|---------|-------------|
| 规划 | 边做边想 | Planner 先输出完整规格 |
| 评估 | 自己判断"做完了" | 独立 Evaluator 逐条验证 |
| Context | 一个窗口塞满 | 每个 Sprint 独立 context |
| 失败处理 | 发现问题才修 | 每轮迭代自动检测+反馈 |

### Step 1 — 理解需求

用户输入: `$ARGUMENTS`

阅读构建请求，信息不足则追问：
- 要构建什么？
- 技术栈偏好？（已有项目则读代码判断）
- 什么算"完成"？

### Step 2 — Planner 阶段

以**项目规划师**身份展开请求为完整规格：

1. 输出项目概要（1 段话）
2. 分解为 Sprint 列表，每个含：标题、描述、验收标准、复杂度
3. Sprint 按依赖排序
4. 每个 Sprint 在一个聚焦会话内可完成

**规划原则**：
- 重产品上下文，轻技术细节（避免过度规格化导致级联错误）
- 每个 Sprint 只关注一个特性
- 验收标准必须具体可测试
- 主动寻找可织入 AI 功能的机会

### Step 3 — Sprint 循环

对每个 Sprint 执行以下循环（最多 3 轮精炼）：

#### 3a. Generator 阶段

以**实现者**身份工作：
- 聚焦当前 Sprint 验收标准
- 使用工具实际编写代码
- 完成后总结每个标准如何满足

**Context Reset**: 每个 Sprint 只携带之前的**摘要**，不是完整对话：

```
## 已完成工作

### Sprint 1: 用户认证 [PASSED]
实现了 JWT 登录、注册、密码重置。数据库用 SQLite。

### Sprint 2: REST API [PASSED]
实现了 /users CRUD、/posts CRUD。添加了权限中间件。
```

#### 3b. Evaluator 阶段

切换为**独立 QA 评估者**：
- 逐条检查验收标准
- 使用工具验证（运行测试、检查文件、执行命令）
- **严格**: 不给部分实现打分

输出结构化评估：

```
Sprint 2 评估:
- ✅ GET /users 返回 200 → 通过
- ❌ DELETE /users/:id 返回 404 → 路由未实现

总分: 2/4 (0.50) — 未通过
反馈: DELETE 路由缺失；权限中间件需在 app.py 中注册。
```

#### 3c. 决策

- **通过** → 进入下一个 Sprint
- **未通过** → 将反馈注入下一轮 Generator
- **达到最大轮次** → 记录未通过项，继续下一个 Sprint

### Step 4 — 最终报告

```
## 构建报告

| Sprint | 标题 | 状态 | 轮次 |
|--------|------|------|------|
| 1 | 用户认证 | ✅ PASSED | 1 |
| 2 | REST API | ✅ PASSED | 2 |
| 3 | 前端页面 | ⚠️ PARTIAL | 3 |

已完成: 2/3 Sprint 完全通过
```

---

## QA 模式

独立 Evaluator，只评估不修复。适用于代码审查、验收测试、质量评估。

### Step 1 — 确认验收标准

用户输入: `$ARGUMENTS`

如果用户提供了标准，直接使用。否则从以下来源推导：
- README / SPEC 文档
- 最近的 git commit
- 代码中的 TODO / FIXME
- 用户描述

输出标准列表，等用户确认后继续。

### Step 2 — 逐条验证

对每个标准独立验证：

1. 制定测试策略
2. 执行验证（实际运行，不是仅看代码）
3. 记录结果 + 证据

```bash
# 示例: 验证 "GET /users 返回 200"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/users
# 期望: 200，实际: 404 → ❌
```

### Step 3 — 评估报告

```
## QA 评估报告

| # | 标准 | 状态 | 证据 |
|---|------|------|------|
| 1 | 用户可以注册 | ✅ | POST /register 返回 201 |
| 2 | 登录获取 JWT | ✅ | POST /login 返回 token |
| 3 | 未登录返回 401 | ❌ | GET /profile 返回 200（应为 401） |

总分: 2/3 (0.67)

未通过项详细反馈:
- 标准 3: middleware 在 app.py:42 注册但路由顺序有误
- 建议: 将 add_middleware() 移到路由注册之前
```

### 评估框架

**前端/UI 项目**:

| 维度 | 权重 | 说明 |
|------|------|------|
| 设计质量 | 30% | 颜色、排版、布局的整体协调 |
| 原创性 | 25% | 自主决策 vs 模板默认值 |
| 工艺 | 20% | 字体层级、间距、对比度 |
| 功能性 | 25% | 用户能否完成任务 |

**后端/API 项目**:

| 维度 | 权重 | 说明 |
|------|------|------|
| 正确性 | 40% | 功能按预期工作 |
| 健壮性 | 25% | 错误处理、边界情况 |
| 安全性 | 20% | 认证、授权、输入验证 |
| 性能 | 15% | 响应时间、资源使用 |

---

## 规划模式

将简短请求展开为 Sprint 合同列表。适用于复杂项目规划、大任务分解。

### Step 1 — 理解上下文

用户输入: `$ARGUMENTS`

1. 阅读请求
2. 已有项目则读取 `package.json` / `pyproject.toml` / README
3. 识别约束条件

### Step 2 — 项目概要

一段话：要构建什么、目标用户、核心价值、技术栈。

### Step 3 — Sprint 合同

每个合同：

```
### Sprint N: 标题

**描述**: 这个 Sprint 要做什么（1-3 句）

**验收标准**:
- [ ] 具体可测试的标准 1
- [ ] 标准 2
- [ ] 标准 3

**复杂度**: low / medium / high
**依赖**: Sprint X（如有）
```

### Step 4 — 汇总

```
## 项目规划: {名称}

### Sprint 路线图

| Sprint | 标题 | 复杂度 | 依赖 | 标准数 |
|--------|------|--------|------|--------|
| 1 | ... | low | - | 3 |
| 2 | ... | medium | S1 | 4 |

### 详细合同
{...}

### 风险与注意事项
{...}
```

### 验收标准写法

**好** ✅:
- "GET /api/users 返回 JSON 数组，含 id、name、email"
- "运行 `pytest tests/` 全部通过，覆盖率 > 80%"

**差** ❌:
- "API 设计合理"
- "界面美观"

### Sprint 粒度

- 每个 Sprint 3-6 个标准
- 超过 6 个则拆分
- 排序：基础设施 → 核心功能 → 辅助功能 → 润色

---

## QA 调优注意事项

Anthropic 研究发现 Claude 做 QA 天然很差：
- 发现问题后会说服自己"其实没问题"
- 测试浅表，遗漏边缘情况
- 嵌套深处的 bug 会漏过

**对策**：
- Evaluator 必须**实际运行**代码验证，不能仅看代码推断
- 每个标准独立检查，不能笼统通过
- 反馈必须具体可操作（"POST /users 返回 500，错误是 missing column"）
- 不要因代码看起来合理就给通过

## 通用注意事项

- Sprint 之间通过摘要传递上下文，不累积完整对话
- Generator 和 Evaluator 是独立角色，不混用
- 简单任务（单文件、单功能）不需要 Harness，直接做
- Generator 最多 50 个工具调用轮次，Evaluator 最多 10 个
- 规划阶段只做读取和分析，不修改代码
