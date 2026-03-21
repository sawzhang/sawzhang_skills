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
