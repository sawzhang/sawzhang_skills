---
name: twitter-research
description: 搜索Twitter/X上特定话题的最新内容并汇总报告。当用户说"搜Twitter"、"查看Twitter上关于XX的讨论"、"twitter research"、"X上最近在聊什么"时使用。
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Twitter/X 话题搜索与汇总

通过多种方式搜索 Twitter/X 上的热门内容，汇总成结构化报告。

## 流程

### Step 1: 确定搜索关键词

根据用户给的话题，生成 3-5 组搜索关键词。关键词策略：

1. **核心关键词**: 用户原始话题（如 `AI Agent`）
2. **细分关键词**: 话题 + 限定词（如 `AI Agent framework 2026`、`AI Agent 开源`）
3. **关联产品/项目**: 话题相关的热门项目名（如 `Claude Code`、`Cursor`、`MCP server`）
4. **中英文双搜**: 同一话题分别用中文和英文搜索

告诉用户将要搜索的关键词列表，然后开始执行。

### Step 2: 搜索推文

优先级从高到低，使用第一个可用的方式：

#### 方式 A: Browser Use CLI（推荐，需已安装）

检查 `browser-use` 是否可用：

```bash
which browser-use 2>/dev/null && echo "AVAILABLE" || echo "NOT_AVAILABLE"
```

如果可用，对每个关键词：

```bash
# 打开 Twitter 搜索页（热门）
browser-use open "https://x.com/search?q={URL编码的关键词}&src=typed_query&f=top"

# 获取页面状态（可点击元素列表）
browser-use state

# 滚动加载更多
browser-use scroll down

# 再次获取状态
browser-use state
```

从 state 输出中提取推文内容。

#### 方式 B: fxtwitter API + WebSearch

如果 browser-use 不可用，使用 Bash 执行搜索：

```bash
# 1. 用 WebSearch 搜索 Twitter 上的内容
# （在 skill 流程中直接调用 WebSearch 工具，query 为: "{关键词} site:x.com"）

# 2. 对搜索到的推文 URL，用 fxtwitter API 获取详情
# 从 URL 提取 username 和 tweet_id，然后：
curl -s "https://api.fxtwitter.com/{username}/status/{tweet_id}"
```

解析 JSON 提取推文数据（正文、作者、互动数等）。

#### 方式 C: 纯 curl 搜索

如果以上都不可用，用 Nitter 实例或其他公开 API：

```bash
# 尝试 Nitter 搜索
curl -s "https://nitter.net/search?f=tweets&q={URL编码的关键词}"
```

### Step 3: 逐个关键词采集

对每个关键词重复 Step 2，收集所有推文数据：
- 作者（显示名 + @handle）
- 发布时间
- 推文正文
- 互动数据（回复、转帖、喜欢、书签、观看数）
- 是否包含图片/视频/引用

### Step 4: 汇总去重

将所有搜索结果合并，按以下规则处理：
- **去重**: 同一条推文可能在多个关键词下出现，按推文 URL 去重
- **排序**: 按互动量（喜欢 + 转帖 + 书签）降序排列
- **分类**: 按话题主题分组

### Step 5: 输出结构化报告

按以下格式输出汇总报告：

```markdown
# Twitter {话题} 热门内容汇总（{日期}）

> 搜索关键词：{关键词1}、{关键词2}、...
> 数据来源：Twitter/X 热门 + 最新标签
> 采集时间：{时间}

---

## 一、{主题分类1}

### 1. {推文标题/摘要}
**作者**: {display_name} (@{handle}) | **时间**: {time} | **互动**: {likes} likes, {views} views
> {推文正文摘要}

**要点**: {一句话总结核心信息}

### 2. ...

---

## 二、{主题分类2}
...

---

## 关键趋势总结

- **趋势1**: {描述}
- **趋势2**: {描述}
- ...

## 值得关注的项目/工具

| 项目名 | 类型 | 一句话描述 | 推荐来源 |
|--------|------|-----------|---------|
| ... | ... | ... | @handle |
```

## 注意事项

- 每次搜索之间适当等待（`sleep 1`），避免频率过高
- 长推文可能被截断，fxtwitter 通常能获取完整内容
- 引用推文（Quote Tweet）的内容也要提取
- 中文推特圈和英文推特圈的内容可能差异很大，建议都搜
- 如果某个搜索方式失败，自动降级到下一个方式
