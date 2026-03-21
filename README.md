# Claude Code Skills

可复用的 Claude Code skills 集合。

## Skills 列表

| Skill | 描述 | 触发词 |
|-------|------|--------|
| [mcp-review](skills/mcp-review/) | MCP Server 工具设计审查，按 10 条准则输出结构化报告 | "review mcp tools"、"检查工具设计" |

## 安装 mcp-review

```bash
# 1. 克隆仓库
git clone https://github.com/sawzhang/sawzhang_skills.git
cd sawzhang_skills

# 2. 复制到 Claude Code skills 目录
cp -r skills/mcp-review ~/.claude/skills/

# 或创建软链接（方便后续 git pull 自动同步更新）
ln -s $(pwd)/skills/mcp-review ~/.claude/skills/mcp-review
```

安装完成后，在 Claude Code 中说 "review mcp tools" 或 "检查工具设计" 即可触发审查。

## 添加新 Skill

1. 在 `skills/` 下创建新目录
2. 添加 `SKILL.md`（必须），格式参考现有 skill
3. 添加相关脚本和配置
