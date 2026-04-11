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

### twitter

Twitter/X 一站式工具 - 读推文、搜索话题、发帖、发 thread。整合了原 read-tweet 和 twitter-research，新增 X API v2 发帖能力。

- **触发词**: "读推文"、"搜Twitter"、"发推"、"发thread"、"twitter post"、"twitter search"、"read tweet"
- **四种模式**: read（fxtwitter API）、search（browser-use / fxtwitter）、post（X API v2 OAuth 1.0a）、thread（连续 post + reply）
- **发帖依赖**: `pip3 install requests-oauthlib` + 环境变量 `X_API_KEY`、`X_API_SECRET`、`X_ACCESS_TOKEN`、`X_ACCESS_SECRET`
- **路径**: `plugins/sawzhang-skills/skills/twitter/`

### cca

CCA 完整学习套件 - 将原 7 个 skill（cca + cca-domain1~5 + cca-quiz）合并为单一 skill，内置路由逻辑，覆盖全部 5 个考试领域 + 12 道模拟测验题。

- **触发词**: "CCA"、"学CCA"、"Claude架构师"、"学domain1~5"、"代理架构"、"工具设计"、"MCP集成"、"Claude Code配置"、"提示工程"、"上下文管理"、"CCA测验"、"模拟考试"
- **路径**: `plugins/sawzhang-skills/skills/cca/`

### harness

Harness 方法论工具箱 - 基于 [Anthropic harness 研究](https://www.anthropic.com/engineering/harness-design-long-running-apps)，内置三种模式的路由：构建（Planner→Generator→Evaluator 三阶段）、QA（独立评估）、规划（Sprint 分解）。

- **触发词**: "harness"、"harness build"、"harness qa"、"harness plan"、"用harness构建"、"独立评估"、"规划一下"
- **核心模式**: Sprint Contract + Context Reset + Generator↔Evaluator 循环
- **路径**: `plugins/sawzhang-skills/skills/harness/`

### xcrawl

网页抓取与搜索工具 - 通过 xcrawl CLI 提供单页抓取（scrape）、网页搜索（search）、站点地图（map）、深度爬取（crawl）四大能力。

- **触发词**: "抓取网页"、"scrape"、"爬取"、"xcrawl"、"搜索网页"、"web search"、"站点地图"、"crawl"
- **前置依赖**: `npm install -g @xcrawl/cli && xcrawl login --browser`
- **路径**: `plugins/sawzhang-skills/skills/xcrawl/`
