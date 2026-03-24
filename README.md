# sawzhang-skills

**Plug-and-play skills that make Claude Code smarter — MCP review, Twitter research, auto-iteration, and CCA exam prep.**

> 即装即用的 Claude Code 技能包 — MCP 工具审查、Twitter 调研、自动迭代优化、CCA 认证备考。

[![Skills](https://img.shields.io/badge/skills-11-blue)]()
[![ClawHub](https://img.shields.io/badge/ClawHub-published-green)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

## Why This Exists

Claude Code is a general-purpose agent. But for specific workflows — reviewing MCP tool designs, researching Twitter trends, or studying for the CCA exam — you need **specialized instructions** that encode domain expertise. That's what skills are: reusable prompt packages that turn Claude into a domain specialist.

## Skills (11)

### Developer Tools

| Skill | Description | Trigger |
|-------|-------------|---------|
| **mcp-review** | Audit MCP server tool designs against 10 best-practice rules, output a structured report with scores | "review mcp tools", "检查工具设计" |
| **auto-iterate** | Autonomous optimization loop — set a metric, let Claude iterate until it improves | "自动迭代", "auto iterate", "overnight experiment" |

### Twitter / X Research

| Skill | Description | Trigger |
|-------|-------------|---------|
| **twitter-research** | Search Twitter/X for a topic, summarize key discussions and sentiment | "搜Twitter", "twitter research" |
| **read-tweet** | Read and analyze a specific tweet by URL | "读一下这条推文", "read tweet" |

### CCA Exam Prep (Claude Certified Architect)

| Skill | Description | Trigger |
|-------|-------------|---------|
| **cca** | Study overview and navigation across all 5 CCA domains | "学CCA", "CCA学习" |
| **cca-domain1** | Domain 1: Agent Architecture & Orchestration (27%) | "代理架构", "agent编排" |
| **cca-domain2** | Domain 2: Tool Design & MCP Integration (18%) | "工具设计", "MCP集成" |
| **cca-domain3** | Domain 3: Claude Code Configuration & Workflows (20%) | "Claude Code配置" |
| **cca-domain4** | Domain 4: Prompt Engineering & Structured Output (20%) | "提示工程", "structured output" |
| **cca-domain5** | Domain 5: Context Management & Reliability (15%) | "上下文管理", "可靠性" |
| **cca-quiz** | Mock exam — 12 scenario-based questions across all 5 domains | "CCA测验", "模拟考试" |

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

### Via ClawHub

```bash
clawhub install mcp-review
clawhub install twitter-research
clawhub install cca
# ... or install any skill individually
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
│       │   └── plugin.json      # Plugin metadata
│       └── skills/
│           ├── mcp-review/      # MCP tool design audit
│           ├── auto-iterate/    # Autonomous optimization loop
│           ├── twitter-research/# Twitter/X topic research
│           ├── read-tweet/      # Single tweet reader
│           ├── cca/             # CCA study overview
│           ├── cca-domain1/     # Agent Architecture (27%)
│           ├── cca-domain2/     # Tool Design & MCP (18%)
│           ├── cca-domain3/     # Claude Code Config (20%)
│           ├── cca-domain4/     # Prompt Engineering (20%)
│           ├── cca-domain5/     # Context Management (15%)
│           └── cca-quiz/        # Mock exam (12 questions)
└── README.md
```

## Adding a New Skill

1. Create a directory under `plugins/sawzhang-skills/skills/`
2. Add a `SKILL.md` with YAML frontmatter (name, description, allowed-tools)
3. Optionally add supporting files (scripts, configs, templates)
4. Publish to ClawHub: `clawhub publish ./skills/my-skill --slug my-skill --version 1.0.0`

## License

MIT
