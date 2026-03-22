---
name: twitter-research
description: 搜索Twitter/X上特定话题的最新内容并汇总报告。当用户说"搜Twitter"、"查看Twitter上关于XX的讨论"、"twitter research"、"X上最近在聊什么"时使用。
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Twitter/X 话题搜索与汇总

通过 Browser Use CLI 操控真实 Chrome 搜索 Twitter/X，抓取热门推文并汇总成结构化报告。如果 browser-use 不可用则降级到 fxtwitter API。

## 流程

### Step 1: 确定搜索关键词

根据用户给的话题，生成 3-5 组搜索关键词：

1. **核心关键词**: 用户原始话题（如 `AI Agent`）
2. **细分关键词**: 话题 + 限定词（如 `AI Agent framework 2026`）
3. **关联产品/项目**: 热门项目名（如 `Claude Code`、`Cursor`）
4. **中英文双搜**: 同一话题分别用中文和英文搜索

告诉用户关键词列表后开始执行。

### Step 2: 初始化浏览器环境

#### 2a. 定义 wrapper 函数（消除代理干扰）

系统 SOCKS/HTTP 代理会破坏 browser-use 的 CDP 连接，必须清除。在 session 开始时定义一次：

```bash
bu() { ALL_PROXY= HTTP_PROXY= HTTPS_PROXY= http_proxy= https_proxy= all_proxy= browser-use "$@"; }
```

后续所有 browser-use 调用改用 `bu`。

#### 2b. 检测并自动安装 browser-use

```bash
if ! which browser-use &>/dev/null; then
  echo "INSTALLING browser-use..."
  uv tool install browser-use && browser-use install
fi
# 验证
which browser-use &>/dev/null && echo "READY" || echo "INSTALL_FAILED"
```

**注意**: 安装方式必须是 `uv tool install browser-use`。`curl install.sh` 只装 cookie 同步工具 `profile-use`，不是浏览器自动化 CLI。

#### 2c. 清理旧 session 并启动

```bash
bu close 2>/dev/null; sleep 1
bu -b real open "https://x.com" 2>&1
```

如果报 `CDP connection` 错误，说明代理变量没清干净或 Chrome 未运行。`-b real` 需要本机 Chrome 已启动且已登录 Twitter。

### Step 3: 逐个关键词搜索

对每个关键词执行：

```bash
# 导航到搜索页
bu open "https://x.com/search?q={URL编码的关键词}&src=typed_query&f=top"
sleep 3

# 获取热门标签内容
bu state 2>&1
```

**解析 state 输出的方法**:

state 返回 accessibility tree，推文结构如下：
- `<article role=article>` — 每条推文的容器
- `<a role=link>` 内含作者名 — 如 `阿绎 AYi`
- `@handle` — 紧跟作者名后面
- `<a aria-label=X月X日>` — 发布时间
- `<span>` 连续多个 — 推文正文（被拆成多段）
- `<div aria-label="X 回复、X 次转帖、X 喜欢、X 书签、X 次观看">` — 互动数据汇总

提取时按 `article` 分块，从每块中收集上述字段。

**滚动加载更多（可选）**:

```bash
bu scroll down && sleep 2 && bu state 2>&1
```

**切换到"最新"标签**:

从 state 中找到 `<a role=tab>最新</a>` 的索引号，然后：
```bash
bu click {索引号} && sleep 3 && bu state 2>&1
```

#### 搜索下一个关键词

直接导航到新 URL（不要用搜索框填充，容易出错）：

```bash
sleep 5  # Twitter 限速间隔
bu open "https://x.com/search?q={下一个关键词}&src=typed_query&f=top"
sleep 3
bu state 2>&1
```

#### 限速恢复

如果页面显示"出错了"或 state 输出只有空 div：
1. 等待更长时间：`sleep 10`
2. 刷新页面：`bu eval "location.reload()"` 然后 `sleep 5`
3. 如果连续两次限速，停止 browser-use 搜索，降级到方式 B

### Step 4: 降级方案 — fxtwitter API

如果 browser-use 不可用、未安装、或被 Twitter 限速：

```bash
# 1. 用 WebSearch 搜索（在 skill 中调用 WebSearch 工具）
#    query: "{关键词} site:x.com" 或 "{关键词} Twitter"

# 2. 从搜索结果提取推文 URL，用 fxtwitter API 获取详情
#    URL 格式: https://x.com/{username}/status/{tweet_id}
curl -s "https://api.fxtwitter.com/{username}/status/{tweet_id}"

# 3. fxtwitter 不可用时尝试 vxtwitter
curl -s "https://api.vxtwitter.com/{username}/status/{tweet_id}"
```

### Step 5: 清理

搜索结束后关闭 browser-use 会话：

```bash
bu close 2>/dev/null
```

### Step 6: 汇总去重

将所有搜索结果合并：
- **去重**: 按推文 URL 去重（同一条可能在多个关键词下出现）
- **排序**: 按互动量（喜欢 + 转帖 + 书签）降序
- **分类**: 按话题主题分组

### Step 7: 输出结构化报告

```markdown
# Twitter {话题} 热门内容汇总（{日期}）

> 搜索关键词：{关键词1}、{关键词2}、...
> 数据来源：Twitter/X 热门 + 最新
> 采集方式：Browser Use CLI / fxtwitter API
> 采集时间：{时间}

---

## 一、{主题分类1}

### 1. {推文标题/摘要}
**作者**: {display_name} (@{handle}) | **时间**: {time} | **互动**: {likes} likes, {retweets} RT, {views} views
> {推文正文}

**要点**: {一句话总结}

---

## 关键趋势总结

- **趋势1**: {描述}
- ...

## 值得关注的项目/工具

| 项目名 | 类型 | 一句话描述 | 推荐来源 |
|--------|------|-----------|---------|
| ... | ... | ... | @handle |
```

## 常见问题排查

| 症状 | 原因 | 解决 |
|------|------|------|
| `socksio package not installed` | 系统 SOCKS 代理干扰 CDP | 用 `bu()` wrapper 清除代理 |
| `CDP connection: invalid HTTP response` | 旧 session 残留 | `bu close` 后重试 |
| `Browser startup timeout` | Chromium 未安装 | `browser-use install` |
| state 只有空 div | 无登录态 | 用 `-b real` 模式 |
| "出错了" 页面 | Twitter 限速 | 等 10 秒后 `eval "location.reload()"` |
| `curl install.sh` 没装到 browser-use | 那个脚本只装 profile-use | 用 `uv tool install browser-use` |
