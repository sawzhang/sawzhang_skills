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

### CCA 系列（Claude Certified Architect 学习套件）

基于 Anthropic 官方 CCA 考试指南构建的交互式学习 skills，覆盖全部 5 个考试领域 + 模拟测验。

#### cca

CCA 学习总览与导航 - 展示考试全貌、5 大领域权重分布、推荐学习路径。

- **触发词**: "CCA"、"学CCA"、"Claude架构师"
- **路径**: `plugins/sawzhang-skills/skills/cca/`

#### cca-domain1

领域 1：代理架构与编排（27% 权重，最高）- 代理循环、协调器-子代理编排、hooks、session 管理。

- **触发词**: "学domain1"、"代理架构"、"agent编排"
- **路径**: `plugins/sawzhang-skills/skills/cca-domain1/`

#### cca-domain2

领域 2：工具设计与 MCP 集成（18%）- 工具描述、tool_choice、MCP 配置、内置工具选择。

- **触发词**: "学domain2"、"工具设计"、"MCP集成"
- **路径**: `plugins/sawzhang-skills/skills/cca-domain2/`

#### cca-domain3

领域 3：Claude Code 配置与工作流（20%）- CLAUDE.md 层级、rules/、commands/、skills、计划模式、CI/CD。

- **触发词**: "学domain3"、"Claude Code配置"、"CLAUDE.md"
- **路径**: `plugins/sawzhang-skills/skills/cca-domain3/`

#### cca-domain4

领域 4：提示工程与结构化输出（20%）- few-shot、tool_use JSON Schema、批处理 API、多遍审查。

- **触发词**: "学domain4"、"提示工程"、"structured output"
- **路径**: `plugins/sawzhang-skills/skills/cca-domain4/`

#### cca-domain5

领域 5：上下文管理与可靠性（15%）- 上下文保留、升级模式、错误传播、信息溯源。

- **触发词**: "学domain5"、"上下文管理"、"可靠性"
- **路径**: `plugins/sawzhang-skills/skills/cca-domain5/`

#### cca-quiz

CCA 模拟测验 - 12 道场景化单选题，按考试权重分配，含详细答案讲解和薄弱领域分析。

- **触发词**: "CCA测验"、"模拟考试"、"cca quiz"
- **路径**: `plugins/sawzhang-skills/skills/cca-quiz/`
