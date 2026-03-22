# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

可复用的 Claude Code skills 集合。每个 skill 是一个独立目录，包含 `SKILL.md` 定义和相关脚本。Skills 可复制到 `~/.claude/skills/` 或通过触发词直接使用。

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

Twitter/X 话题搜索与汇总 - 多关键词搜索推文，去重分类后输出结构化报告。支持 Browser Use CLI / fxtwitter API / curl 多级降级。

- **触发词**: "搜Twitter"、"查看Twitter上关于XX的讨论"、"twitter research"、"X上最近在聊什么"
- **搜索方式**: Browser Use CLI（优先） → WebSearch + fxtwitter API → curl 降级
- **关键词策略**: 核心词、细分词、关联项目名、中英文双搜
- **路径**: `plugins/sawzhang-skills/skills/twitter-research/`
