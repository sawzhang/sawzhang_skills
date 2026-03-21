# Claude Code Skills

可复用的 Claude Code skills 集合。

## Skills 列表

| Skill | 描述 | 触发词 |
|-------|------|--------|
| [mcp-review](skills/mcp-review/) | MCP Server 工具设计审查，按 10 条准则输出结构化报告 | "review mcp tools"、"检查工具设计" |

## 使用方式

### 方式 1: 复制到 Claude Code skills 目录

```bash
# macOS/Linux
cp -r skills/<skill-name> ~/.claude/skills/

# 或创建软链接
ln -s $(pwd)/skills/<skill-name> ~/.claude/skills/<skill-name>
```

### 方式 2: 直接在对话中触发

在 Claude Code 中说出触发词即可执行对应 skill。

## 添加新 Skill

1. 在 `skills/` 下创建新目录
2. 添加 `SKILL.md`（必须），格式参考现有 skill
3. 添加相关脚本和配置

## 目录结构

```
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md           # Skill 定义（必须）
│       ├── config/            # 配置文件
│       ├── references/        # 参考资料
│       └── scripts/           # 脚本
├── requirements.txt
└── README.md
```
