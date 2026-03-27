# sawzhang-skills

**Plug-and-play skills that make Claude Code smarter — MCP review, Twitter research, auto-iteration, CCA exam prep, and Harness Engineering workflows.**

> 即装即用的 Claude Code 技能包 — MCP 工具审查、Twitter 调研、自动迭代优化、CCA 认证备考、Harness Engineering 全流程开发。

[![Skills](https://img.shields.io/badge/skills-7-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

## Why This Exists

Claude Code is a general-purpose agent. But for specific workflows — reviewing MCP tool designs, researching Twitter trends, or studying for the CCA exam — you need **specialized instructions** that encode domain expertise. That's what skills are: reusable prompt packages that turn Claude into a domain specialist.

## Skills (7)

### Developer Tools

| Skill | Description | Trigger |
|-------|-------------|---------|
| **mcp-review** | Audit MCP server tool designs against 10 best-practice rules, output a structured report with scores | "review mcp tools", "检查工具设计" |
| **auto-iterate** | Autonomous optimization loop — set a metric, let Claude iterate until it improves | "自动迭代", "auto iterate", "overnight experiment" |
| **sdd** | Harness Engineering full dev loop — design → plan → TDD → code review → PR, fully autonomous | "自主开发", "sdd", "harness 开发" |

### Harness Methodology (based on [Anthropic research](https://www.anthropic.com/engineering/harness-design-long-running-apps))

| Skill | Description | Trigger |
|-------|-------------|---------|
| **harness** | 3-in-1 harness toolkit: build (Planner→Generator→Evaluator), QA (independent eval), plan (Sprint decomposition) | "harness build", "harness qa", "harness plan" |

### Twitter / X Research

| Skill | Description | Trigger |
|-------|-------------|---------|
| **twitter-research** | Search Twitter/X for a topic, summarize key discussions and sentiment | "搜Twitter", "twitter research" |
| **read-tweet** | Read and analyze a specific tweet by URL | "读一下这条推文", "read tweet" |

### CCA Exam Prep (Claude Certified Architect)

| Skill | Description | Trigger |
|-------|-------------|---------|
| **cca** | Complete CCA study kit — all 5 domains (27%+18%+20%+20%+15%) + 12-question mock exam, built-in routing | "学CCA", "代理架构", "工具设计", "提示工程", "CCA测验" |

## Install

### Via Claude Code Plugin Marketplace

```bash
# 1. Add marketplace
/plugin marketplace add sawzhang/sawzhang_skills

# 2. Install plugin
/plugin install sawzhang-skills@sawzhang-skills

# 3. Reload
/reload-plugins
```

## Team Setup

Add to your project's `.claude/settings.json` — team members get auto-prompted to install:

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

## Project Structure

```
sawzhang_skills/
├── .claude-plugin/
│   └── marketplace.json         # Marketplace definition
├── plugins/
│   └── sawzhang-skills/
│       ├── .claude-plugin/
│       │   └── plugin.json      # Plugin metadata (v1.4.0)
│       └── skills/
│           ├── mcp-review/      # MCP tool design audit
│           ├── auto-iterate/    # Autonomous optimization loop
│           ├── sdd/             # Harness Engineering dev loop
│           ├── harness/          # Harness methodology toolkit (build/qa/plan)
│           ├── twitter-research/# Twitter/X topic research
│           ├── read-tweet/      # Single tweet reader
│           └── cca/             # CCA complete study kit (5 domains + mock exam)
└── README.md
```

## Adding a New Skill

1. Create a directory under `plugins/sawzhang-skills/skills/`
2. Add a `SKILL.md` with YAML frontmatter (`allowed-tools` must use standard tool names only)
3. Bump `plugins/sawzhang-skills/.claude-plugin/plugin.json` version (new skill → minor bump)

## License

MIT
