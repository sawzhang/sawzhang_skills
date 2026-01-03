# Claude Code Skills

可复用的 Claude Code skills 集合。

## 安装

```bash
pip install -r requirements.txt
```

## Skills 列表

| Skill | 描述 | 触发词 |
|-------|------|--------|
| [daily-tech-digest](skills/daily-tech-digest/) | 每日技术日报，聚合 HN/PH/AI 动态 | "今日技术日报"、"生成 newsletter" |

## 使用方式

### 方式 1: 复制到 Claude Code skills 目录

```bash
# macOS/Linux
cp -r skills/daily-tech-digest ~/.claude/skills/

# 或创建软链接
ln -s $(pwd)/skills/daily-tech-digest ~/.claude/skills/daily-tech-digest
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
