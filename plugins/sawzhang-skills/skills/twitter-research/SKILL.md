---
name: twitter-research
description: 搜索Twitter/X上特定话题的最新内容并汇总报告。当用户说"搜Twitter"、"查看Twitter上关于XX的讨论"、"twitter research"、"X上最近在聊什么"时使用。
allowed-tools: Bash, Read, Write, WebFetch, WebSearch, mcp__chrome_devtools__navigate_page, mcp__chrome_devtools__take_snapshot, mcp__chrome_devtools__wait_for, mcp__chrome_devtools__evaluate_script, mcp__chrome_devtools__fill, mcp__chrome_devtools__click, mcp__exa__web_search_exa
---

# Twitter/X 话题搜索与汇总

通过 Chrome DevTools MCP 在已登录的 Chrome 浏览器中搜索 Twitter/X，抓取多个关键词的热门和最新推文，汇总成结构化报告。

## 前置条件

- Chrome DevTools MCP server 已连接（通过 `mcp__chrome_devtools__*` 工具）
- Chrome 浏览器已登录 Twitter/X 账号

## 流程

### Step 1: 确定搜索关键词

根据用户给的话题，生成 3-5 组搜索关键词。关键词策略：

1. **核心关键词**: 用户原始话题（如 `AI Agent`）
2. **细分关键词**: 话题 + 限定词（如 `AI Agent framework 2026`、`AI Agent 开源`）
3. **关联产品/项目**: 话题相关的热门项目名（如 `OpenClaw`、`Claude Code`、`MCP server`）
4. **中英文双搜**: 同一话题分别用中文和英文搜索

告诉用户将要搜索的关键词列表，然后开始执行。

### Step 2: 逐个关键词搜索

对每个关键词执行以下操作：

#### 2a. 导航到搜索页

```
使用 mcp__chrome_devtools__navigate_page 导航到:
https://x.com/search?q={URL编码的关键词}&src=typed_query&f=top
```

如果导航超时但 URL 已变化，继续下一步。

#### 2b. 检查登录状态

使用 `mcp__chrome_devtools__wait_for` 等待页面加载，检查是否出现登录弹窗。
- 如果出现登录页面：通知用户需要手动登录，暂停
- 如果直接显示搜索结果：继续

#### 2c. 抓取"热门"标签内容

使用 `mcp__chrome_devtools__take_snapshot` 获取页面快照。
从快照中提取每条推文的：
- 作者（显示名 + @handle）
- 发布时间
- 推文正文
- 互动数据（回复、转帖、喜欢、书签、观看数）
- 是否包含图片/视频/引用

#### 2d. 切换到"最新"标签

点击"最新"标签（通常是 tab 元素），获取最新推文快照。

#### 2e. 滚动加载更多（可选）

如果内容不够丰富，使用 `evaluate_script` 执行 `window.scrollBy(0, 2000)` 滚动加载更多内容，然后再次截取快照。

#### 2f. 搜索下一个关键词

使用 `mcp__chrome_devtools__fill` 填充搜索框新关键词，按 Enter 搜索。
或直接导航到新的搜索 URL。

### Step 3: 汇总去重

将所有搜索结果合并，按以下规则处理：
- **去重**: 同一条推文可能在多个关键词下出现，按推文 URL 去重
- **排序**: 按互动量（喜欢 + 转帖 + 书签）降序排列
- **分类**: 按话题主题分组

### Step 4: 输出结构化报告

按以下格式输出汇总报告：

```markdown
# Twitter AI Agent 热门内容汇总（{日期}）

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

- Twitter 搜索需要登录状态，Chrome 必须已登录
- 每次搜索之间适当等待，避免频率过高
- 长推文可能被截断，snapshot 中会显示"显示更多"按钮
- 引用推文（Quote Tweet）的内容也要提取
- 如果 Chrome DevTools 不可用，降级方案：使用 WebSearch 搜索 `site:x.com {关键词}`
- 中文推特圈和英文推特圈的内容可能差异很大，建议都搜

## 降级方案

如果 Chrome DevTools MCP 不可用或未登录：

1. 使用 `WebSearch` 搜索 `{话题} site:x.com` 或 `{话题} Twitter`
2. 对搜索到的推文 URL，使用 read-tweet skill 的 fxtwitter 方法读取内容
3. 用 `mcp__exa__web_search_exa` 搜索话题获取更广泛的网络内容作为补充
