# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code Skills 仓库 - 存放可复用的 Claude Code skills。每个 skill 是一个独立目录，包含 `SKILL.md` 定义和相关脚本。

## Repository Structure

```
├── .gitignore
├── requirements.txt
├── README.md
└── skills/
    └── daily-tech-digest/      # 每日技术日报 skill
        ├── SKILL.md            # Skill 定义（触发词、流程、输出模板）
        ├── config/
        ├── references/
        └── scripts/
```

## Adding a New Skill

1. 在 `skills/` 下创建新目录
2. 添加 `SKILL.md` 文件，遵循格式：
   ```yaml
   ---
   name: skill-name
   description: 描述
   allowed-tools: Read, Write, Bash, ...
   ---
   # Skill Name
   ...
   ```
3. 将相关脚本和配置放入同目录

---

## Skill: daily-tech-digest

每日技术日报 - 聚合 HN/ProductHunt/AI 动态，生成结构化分析，可发布到微信公众号。

### Commands

```bash
# 安装依赖
pip install -r requirements.txt

# 运行日报生成
python3 skills/daily-tech-digest/scripts/daily_digest_cron.py

# 交互式微信发布配置
python3 skills/daily-tech-digest/scripts/wechat-publisher/quickstart.py
```

### Architecture

```
skills/daily-tech-digest/
├── SKILL.md                    # Skill 定义
├── config/wechat.yaml.example  # 微信凭证模板
├── references/
│   └── analysis-framework.md   # 趋势分析框架
└── scripts/
    ├── daily_digest_cron.py    # 主入口
    └── wechat-publisher/
        ├── wechat_client.py    # 微信 API 客户端
        ├── md_converter.py     # Markdown → 微信 HTML
        ├── cover_generator.py  # 封面图生成
        └── publisher.py        # 发布流程
```

### Key Patterns

- **凭证管理**: 使用环境变量 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`
- **Token 缓存**: 自动缓存到 `.wechat_token_cache.json`，过期前 5 分钟刷新
- **封面生成**: 使用日期作为随机种子，同日封面样式一致
- **内容结构**: 60秒速览 → 趋势雷达 → 深度解读 → 原始素材
