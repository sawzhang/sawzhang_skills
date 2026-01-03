---
name: daily-tech-digest
description: 每日技术情报智能摘要，支持一键发布到微信公众号。触发场景："今日技术日报"、"生成newsletter"、"技术趋势分析"、"发布到公众号"。聚合HN/ProductHunt/AI动态，进行跨源趋势归纳，输出结构化技术洞察。
allowed-tools: Read, Write, Edit, Bash, WebFetch, WebSearch, Glob, Grep
---

# Daily Tech Digest

智能聚合多源技术情报，提炼趋势，输出可行动洞察，支持一键发布到微信公众号。

## 执行流程

### Phase 1: 数据采集（并行）

使用 WebSearch + WebFetch 抓取三个数据源：

**Hacker News - 技术深度**
```bash
# 使用 WebFetch 抓取
WebFetch: https://news.ycombinator.com/best
提取: Top 15 文章（标题、URL、points、领域标签）
```

**Product Hunt - 产品创新**
```bash
# 使用 WebSearch 搜索
WebSearch: "site:producthunt.com products today [当前日期]"
提取: Top 10 产品（名称、tagline、领域、upvotes）
```

**AI 动态**
```bash
# 使用 WebSearch 搜索
WebSearch: "AI agent Claude OpenAI Anthropic [年份]"
提取: 5-8 条高影响力讨论
```

### Phase 2: 智能归纳（核心）

读取 `references/analysis-framework.md` 执行分析：

#### 2.1 主题聚类
- AI/ML（模型、Agent、工具链）
- DevTools（开发者工具、基础设施）
- Product/UX（产品设计、用户体验）
- Business（商业模式、融资、战略）
- Other（其他值得关注的）

#### 2.2 趋势识别
- **新兴信号**：首次出现或突然升温的话题
- **持续热点**：连续多日/周出现的主题
- **转折点**：重大发布、收购、政策变化

#### 2.3 洞察提炼
对每个重要趋势回答：
- **What**: 发生了什么？
- **Why**: 为什么重要？
- **Impact**: 对开发者/企业/用户的影响

### Phase 3: 输出生成

生成 Markdown 文件，结构见下方模板。保存到工作目录下的 `tech_digest_[日期].md`

### Phase 4: 微信公众号发布（可选）

当用户请求「发布到公众号」「同步到微信」时执行：

#### 4.1 环境准备

检查环境变量或配置文件 `config/wechat.yaml`：

```yaml
wechat:
  app_id: "wx..."           # 公众号 AppID
  app_secret: "..."         # 公众号 AppSecret（敏感信息）
  auto_publish: false       # 是否自动发布（建议 false）
```

#### 4.2 封面图自动生成

根据日报内容自动生成 900x383 高清封面图：

```python
from cover_generator import generate_cover

# 读取日报内容
with open('tech_digest_2026-01-03.md', 'r') as f:
    content = f.read()

# 自动生成封面图（从内容提取日期和主题词）
cover_path = generate_cover(
    content,
    output_path="cover.png",
    theme="tech_blue"  # 可选: tech_blue, ai_purple, dev_green
)
```

**封面图特性**：
- 尺寸：900x383（微信公众号推荐比例 2.35:1）
- 自动提取：从日报内容中提取日期和主题标签
- 科技风格：渐变背景 + 网格纹理 + 发光粒子
- 三种主题：tech_blue（默认蓝）、ai_purple（紫）、dev_green（绿）
- 同日一致：同一天生成的封面图样式一致（使用日期作为随机种子）

#### 4.3 执行发布

```bash
# 设置环境变量
export WECHAT_APP_ID="..."
export WECHAT_APP_SECRET="..."

# 完整发布流程（自动生成封面 + 上传 + 创建草稿）
cd [skill_directory]/scripts/wechat-publisher
python3 -c "
from wechat_client import WechatClient, WechatConfig
from md_converter import convert_markdown_to_wechat
from cover_generator import generate_cover
import os

# 读取日报
content = open('path/to/digest.md').read()

# 生成封面
cover_path = generate_cover(content, 'cover.png')

# 创建客户端
client = WechatClient(WechatConfig(
    app_id=os.environ['WECHAT_APP_ID'],
    app_secret=os.environ['WECHAT_APP_SECRET']
))

# 上传封面
cover_media_id = client.upload_image(cover_path)

# 创建草稿
draft_id = client.create_draft(
    title='Tech Digest 2026-01-03',
    content=convert_markdown_to_wechat(content),
    thumb_media_id=cover_media_id
)
print(f'草稿创建成功: {draft_id}')
"
```

#### 4.4 发布流程

```
Markdown 内容
    ↓
cover_generator.py（自动生成封面图）
    ↓
md_converter.py（转换为微信 HTML，内联样式）
    ↓
wechat_client.py（上传封面 + 创建草稿）
    ↓
公众号后台草稿箱（人工审核）
    ↓
发布
```

## 输出模板

```markdown
# Tech Digest [日期]

## 60秒速览
> 用3-5句话概括今日最值得关注的动态，直击要点。

## 趋势雷达

### 本期主题词
`关键词1` `关键词2` `关键词3`

### 趋势矩阵
| 趋势 | 信号强度 | 阶段 | 影响范围 |
|------|---------|------|---------|
| [趋势名] | 强/中/弱 | 新兴/成长/成熟 | 广泛/垂直/小众 |

## 深度解读

### [趋势1名称]
**现象**: 一句话描述
**本质**: 背后逻辑
**信号来源**: HN #xxx, PH #xxx
**影响**: 对开发者/企业/用户的影响

## 值得关注
基于本期内容的推荐事项（1-3条）

## 原始素材
### Hacker News Top 10
| # | 热度 | 标题 | 领域 |
|---|------|------|------|

### Product Hunt 精选
| 产品 | 一句话 | 亮点 |
|------|-------|------|

### AI 动态
| 来源 | 核心观点 |
|------|---------|

---
*Generated at [时间] | Sources: HN, ProductHunt, X/Twitter*
```

## 目录结构

```
daily-tech-digest/
├── SKILL.md                      # 本文件
├── config/
│   └── wechat.yaml.example       # 微信配置模板
├── references/
│   ├── analysis-framework.md     # 分析框架
│   └── sources.md                # 数据源说明
└── scripts/
    └── wechat-publisher/         # 微信发布模块
        ├── __init__.py
        ├── wechat_client.py      # 微信 API 客户端
        ├── md_converter.py       # Markdown 转换器
        ├── cover_generator.py    # 封面图自动生成器
        ├── publisher.py          # 发布流程
        └── quickstart.py         # 快速入门脚本
```

## 触发词

| 触发词 | 执行阶段 |
|--------|---------|
| "今日技术日报" | Phase 1-3 |
| "生成 newsletter" | Phase 1-3 |
| "技术趋势分析" | Phase 1-3 |
| "HN 热门" | Phase 1-3 |
| "发布到公众号" | Phase 4 |
| "同步到微信" | Phase 4 |
| "生成日报并发布" | Phase 1-4 |

## 首次配置指南

### 1. 安装依赖

```bash
pip install requests pyyaml pillow
```

### 2. 获取微信公众号凭证

```bash
# 登录公众号后台
https://mp.weixin.qq.com

# 进入: 开发 → 基本配置
# 获取: AppID, AppSecret
# 设置: IP 白名单（添加你的服务器 IP）
```

### 3. 设置环境变量

```bash
export WECHAT_APP_ID="wx..."
export WECHAT_APP_SECRET="..."
```

### 4. 测试发布

```bash
# 生成日报并发布（封面图自动生成）
"今日技术日报发布到公众号"
```

封面图会根据日报内容自动生成，无需手动上传。

## 质量标准

1. **趋势归纳**：识别跨源共性，不是简单罗列
2. **洞察深度**：每个趋势有 Why 和 Impact
3. **信息密度**：60秒速览控制在 60 秒内
4. **溯源清晰**：观点可追溯到具体来源
5. **客观中立**：陈述事实，不带主观偏见
6. **发布安全**：默认创建草稿，人工审核后发布

## 注意事项

- **凭证安全**: AppSecret 使用环境变量，不要硬编码
- **审核机制**: 建议 `auto_publish: false`，人工审核后发布
- **标题限制**: 避免使用「第X章」等字样，会被微信拦截
- **图片处理**: 外链图片需上传到微信服务器才能显示
