# Claude Code Skills

可复用的 Claude Code skills 集合，通过 Plugin Marketplace 分发。

## Skills 列表

| Skill | 描述 | 触发词 |
|-------|------|--------|
| [mcp-review](skills/mcp-review/) | MCP Server 工具设计审查，按 10 条准则输出结构化报告 | "review mcp tools"、"检查工具设计" |
| [auto-iterate](skills/auto-iterate/) | 自主迭代优化，持续改进指定指标 | "自动迭代"、"auto iterate" |

## 安装

在 Claude Code 中执行以下命令：

```
# 1. 添加 Marketplace
/plugin marketplace add sawzhang/sawzhang_skills

# 2. 安装插件
/plugin install sawzhang-skills@sawzhang-skills

# 3. 重载插件
/reload-plugins
```

安装完成后，说 "review mcp tools" 或 "检查工具设计" 即可触发 MCP 工具审查。

## 团队配置

在项目的 `.claude/settings.json` 中添加，团队成员打开项目时自动提示安装：

```json
{
  "extraKnownMarketplaces": {
    "sawzhang-skills": {
      "source": {
        "source": "github",
        "repo": "sawzhang/sawzhang_skills"
      }
    }
  },
  "enabledPlugins": {
    "sawzhang-skills@sawzhang-skills": true
  }
}
```

## 添加新 Skill

1. 在 `skills/` 下创建新目录
2. 添加 `SKILL.md`（必须），格式参考现有 skill
3. 在 `.claude-plugin/plugin.json` 中注册新 skill
4. 添加相关脚本和配置
