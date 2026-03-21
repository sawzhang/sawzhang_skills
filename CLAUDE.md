# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

可复用的 Claude Code skills 集合。每个 skill 是一个独立目录，包含 `SKILL.md` 定义和相关脚本。Skills 可复制到 `~/.claude/skills/` 或通过触发词直接使用。

## Adding a New Skill

1. 在 `skills/` 下创建新目录
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
- **注意**: 审查路径引用 `.claude/skills/mcp-review/`，使用前需确认实际路径
