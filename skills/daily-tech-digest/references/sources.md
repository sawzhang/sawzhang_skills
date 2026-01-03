# Data Sources

技术日报数据来源说明。

## 主要数据源

### 1. Hacker News

**URL**: https://news.ycombinator.com/best

**特点**:
- 技术深度高，讨论质量好
- 开发者社区风向标
- 48小时内最热门文章

**提取字段**:
- 标题 (title)
- 链接 (url)
- 热度 (points)
- 评论数 (comments)
- 领域标签 (手动归类)

### 2. Product Hunt

**URL**: https://www.producthunt.com/

**特点**:
- 新产品发布的第一站
- 产品创新风向标
- 覆盖 B2B/B2C 各类产品

**提取字段**:
- 产品名 (name)
- 一句话介绍 (tagline)
- 品类 (category)
- 投票数 (upvotes)

### 3. AI Twitter/X

**搜索词**: `AI agent Claude OpenAI Anthropic Google Gemini`

**特点**:
- AI 领域最新动态
- 业内人士第一手观点
- 节奏最快，但噪音也多

**关注账号**（参考）:
- @AnthropicAI
- @OpenAI
- @GoogleAI
- @karpathy
- @ylecun
- @sama

## 补充数据源（按需）

| 来源 | 适用场景 |
|------|---------|
| TechCrunch | 融资、收购、战略动态 |
| The Verge | 消费电子、科技文化 |
| Ars Technica | 深度技术分析 |
| ArXiv | 学术论文、前沿研究 |
| GitHub Trending | 开源项目热度 |

## 数据采集注意事项

1. **时效性**: 优先抓取 24-48 小时内的内容
2. **去重**: 同一事件多个来源报道，合并处理
3. **验证**: 对于重大消息，尽量找官方来源确认
4. **偏见**: 注意来源的立场偏向，保持客观
