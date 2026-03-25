# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

可复用的 Claude Code skills 集合。每个 skill 是一个独立目录，包含 `SKILL.md` 定义和相关脚本。Skills 可复制到 `~/.claude/skills/` 或通过触发词直接使用。

## Versioning（必须遵守）

Claude Code plugin 系统用 **version + gitCommitSha** 双重判断是否需要重新安装。cache 按版本号缓存，如果 `plugin.json` 的 version 不变，`/plugin update` 即使拉到新代码也不会刷新 cache。

**规则：每次新增 skill、删除 skill、或对已有 skill 做重大修改时，必须 bump `plugins/sawzhang-skills/.claude-plugin/plugin.json` 的 `version` 字段。**

- 新增/删除 skill → minor bump（如 `1.0.0` → `1.1.0`）
- skill 内容重大修改 → patch bump（如 `1.1.0` → `1.1.1`）
- 纯 typo/注释修改 → 可不 bump

示例：
```json
{
  "name": "sawzhang-skills",
  "version": "1.1.0",
  ...
}
```

## Adding a New Skill

1. 在 `plugins/sawzhang-skills/skills/` 下创建新目录
2. 添加 `SKILL.md` 文件，遵循 frontmatter 格式：
   ```yaml
   ---
   name: skill-name
   description: 描述
   allowed-tools: Read, Write, Bash, ...
   ---
   ```
3. 将相关脚本和配置放入同目录
4. **注意**: `allowed-tools` 只能使用标准工具名（`Read, Write, Edit, Bash, Grep, Glob, Agent`），不支持 `WebFetch`、`WebSearch`、`mcp__*` 等扩展工具名，否则 skill 会静默加载失败
5. **Bump `plugins/sawzhang-skills/.claude-plugin/plugin.json` 的 version**（minor bump）

## Skills

### sdd

Harness Engineering 全流程开发 - 从 feature spec 到 PR 合并的完整自主开发 loop。所有「执行性质的工作」由 subagent 执行，Skill 负责编排，人工只在设计确认和 BLOCKED 时介入。

- **触发词**: "自主开发"、"帮我实现"、"sdd"、"harness 开发"
- **完整流程**: 设计（用户确认）→ 规划 → git worktree → TDD 实现 → spec/quality review → 质量关卡 → PR → Review 修复 → merge
- **Harness 四要素**: 约束（worktree 隔离）/ 观测（状态协议）/ 校验（测试+lint+review）/ 回退（失败即停止上报）
- **灵感来源**: @kasong2048 的 Harness Engineering 理念 + superpowers SDD + openclaw QA 策略
- **路径**: `plugins/sawzhang-skills/skills/sdd/`

### mcp-review

MCP Server 工具设计审查 - 按 10 条准则（Description 三段式、极简参数、扁平化、来源标注、命名规范、响应精简、格式一致、渐进式披露、写操作安全、敏感信息脱敏）逐一审查 tool 定义，输出结构化报告。

- **触发词**: "review mcp tools"、"检查工具设计"、"check一下工具设计"
- **设计准则**: `MCP_API_DESIGN_GUIDE.md`（同目录）
- **路径**: `plugins/sawzhang-skills/skills/mcp-review/`

### auto-iterate

自主迭代优化 - 在「修改 → 运行 → 评估 → 保留/回滚」循环中持续优化用户指定的指标。适用于 ML 训练、性能调优、Prompt 优化等场景。

- **触发词**: "自动迭代"、"auto iterate"、"帮我跑优化实验"
- **核心参数**: 目标文件、运行命令、指标名称、指标方向、时间预算
- **灵感来源**: [autoresearch](https://github.com/karpathy/autoresearch) 的自主实验循环

### read-tweet

阅读 Twitter/X 推文 - 通过 fxtwitter API 代理绕过 JS 渲染限制，获取推文完整内容（正文、作者、互动数据等）。

- **触发词**: "读一下这条推文"、"read tweet"、"看看这条X"
- **核心原理**: 将 `x.com` 域名替换为 `api.fxtwitter.com` 获取结构化数据
- **路径**: `plugins/sawzhang-skills/skills/read-tweet/`

### twitter-research

Twitter/X 话题搜索与汇总 - 通过 Browser Use CLI 操控真实 Chrome（`-b real` 模式，复用登录态）搜索多关键词推文，去重分类后输出结构化报告。

- **触发词**: "搜Twitter"、"查看Twitter上关于XX的讨论"、"twitter research"、"X上最近在聊什么"
- **搜索方式**: Browser Use CLI（`-b real`，优先） → fxtwitter API 降级
- **关键词策略**: 核心词、细分词、关联项目名、中英文双搜
- **前置依赖**: `uv tool install browser-use && browser-use install`
- **已知坑**: 系统代理需清除（`bu()` wrapper）、搜索间隔 5 秒防限速
- **路径**: `plugins/sawzhang-skills/skills/twitter-research/`

### cca

CCA 完整学习套件 - 将原 7 个 skill（cca + cca-domain1~5 + cca-quiz）合并为单一 skill，内置路由逻辑，覆盖全部 5 个考试领域 + 12 道模拟测验题。

- **触发词**: "CCA"、"学CCA"、"Claude架构师"、"学domain1~5"、"代理架构"、"工具设计"、"MCP集成"、"Claude Code配置"、"提示工程"、"上下文管理"、"CCA测验"、"模拟考试"
- **路径**: `plugins/sawzhang-skills/skills/cca/`

### harness-build

Harness 构建模式 - 基于 [Anthropic harness 方法论](https://www.anthropic.com/engineering/harness-design-long-running-apps)，用 Planner→Generator→Evaluator 三阶段循环完成复杂构建任务。

- **触发词**: "harness build"、"用harness构建"、"长任务构建"
- **核心模式**: Sprint Contract + Context Reset + Generator↔Evaluator 循环
- **路径**: `plugins/sawzhang-skills/skills/harness-build/`

### harness-qa

Harness QA 评估 - 独立 Evaluator 逐条验证验收标准，只评估不修复。

- **触发词**: "harness qa"、"独立评估"、"评估一下这个实现"、"qa check"
- **路径**: `plugins/sawzhang-skills/skills/harness-qa/`

### harness-plan

Harness 规划 - 将简短请求展开为 Sprint 合同列表，含可测试验收标准。

- **触发词**: "harness plan"、"规划一下"、"分解为sprint"
- **路径**: `plugins/sawzhang-skills/skills/harness-plan/`
