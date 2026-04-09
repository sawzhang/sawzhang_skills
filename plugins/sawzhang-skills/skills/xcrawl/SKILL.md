---
name: xcrawl
description: 网页抓取与搜索工具。当用户说"抓取网页"、"scrape"、"爬取"、"xcrawl"、"搜索网页"、"web search"、"站点地图"、"sitemap"、"crawl"时使用。
allowed-tools: Bash, Read
---

# XCrawl — 网页抓取与搜索

通过 xcrawl CLI 提供四大能力：单页抓取（scrape）、网页搜索（search）、站点地图（map）、深度爬取（crawl）。

## 前置检查

每次执行前先确认 xcrawl 可用：

```bash
which xcrawl || echo "ERROR: xcrawl 未安装，请运行 npm install -g @xcrawl/cli"
```

如果未安装，提示用户执行安装和登录：
1. `npm install -g @xcrawl/cli`
2. `xcrawl login --browser`
3. `xcrawl status` 确认额度

## 功能路由

根据用户意图选择对应命令：

| 意图 | 命令 | 典型场景 |
|------|------|----------|
| 抓取单个/多个网页内容 | `scrape` | "帮我抓取这个页面"、"读取这个网址的内容" |
| 搜索关键词 | `search` | "搜一下 XX"、"web search XX" |
| 获取网站所有链接 | `map` | "列出这个网站的页面"、"sitemap" |
| 深度爬取整站 | `crawl` | "爬取整个网站"、"crawl this site" |

## 1. 单页抓取 (scrape)

抓取一个或多个 URL 的内容，默认输出 markdown 格式。

```bash
# 单个 URL
xcrawl scrape "https://example.com" --format markdown

# 多个 URL
xcrawl scrape "https://a.com" "https://b.com" --format markdown

# 输出为 JSON（含结构化元数据）
xcrawl scrape "https://example.com" --format json --json

# 截图
xcrawl scrape "https://example.com" --format screenshot --output screenshot.png

# 等待动态内容加载
xcrawl scrape "https://example.com" --wait-for ".content-loaded"

# 从文件批量读取 URL
xcrawl scrape --input urls.txt --format markdown --output ./results/ --concurrency 3
```

**输出格式选项**: `markdown`（默认推荐）、`json`、`html`、`screenshot`

### 处理抓取结果

- 如果内容过长，用 `--output` 保存到文件，再用 Read 工具读取
- 如果用户需要提取特定信息，先抓取为 markdown，再从结果中解析

## 2. 网页搜索 (search)

搜索关键词，返回搜索结果列表。

```bash
# 基本搜索
xcrawl search "Claude Code skills" --json

# 限制结果数量
xcrawl search "site:github.com xcrawl" --limit 5 --json

# 指定语言和地区
xcrawl search "最新AI新闻" --language zh --country CN --json
```

**搜索技巧**:
- 用 `--json` 获取结构化结果（含 URL、标题、摘要）
- 用 `--limit` 控制结果数量，节省额度
- 支持 Google 搜索语法（`site:`、`intitle:` 等）

### 搜索 + 抓取组合

常见模式：先搜索找到目标 URL，再抓取详细内容。

```bash
# Step 1: 搜索
xcrawl search "topic" --limit 5 --json --output search_results.json

# Step 2: 从结果中选择 URL 抓取
xcrawl scrape "https://found-url.com" --format markdown
```

## 3. 站点地图 (map)

列出一个网站的所有可达链接。

```bash
# 基本用法
xcrawl map "https://example.com" --json

# 限制深度和数量
xcrawl map "https://docs.example.com" --max-depth 2 --limit 50 --json
```

**用途**: 了解网站结构、找到所有文档页面、为批量抓取准备 URL 列表。

## 4. 深度爬取 (crawl)

异步爬取整个网站，适合大规模数据采集。

```bash
# 启动爬取任务（异步）
xcrawl crawl start "https://example.com" --max-pages 20 --json

# 启动并等待完成
xcrawl crawl start "https://example.com" --max-pages 10 --wait --json

# 查询任务状态
xcrawl crawl status <job-id> --json
```

**注意**: crawl 是异步任务，用 `--wait` 可阻塞等待完成，或用 `crawl status` 轮询。

## 额度管理

xcrawl 按调用次数消耗额度。执行前可检查剩余额度：

```bash
xcrawl status
```

- 优先使用 `search`（消耗少）而非 `crawl`（消耗多）
- 批量抓取时用 `--concurrency` 控制并发但不减少总消耗
- 如果额度不足，提示用户充值或调整策略

## 输出处理规范

1. **短内容**（< 200 行）：直接在终端输出，提取关键信息回复用户
2. **长内容**（>= 200 行）：用 `--output` 保存到临时文件，再用 Read 工具按需读取
3. **JSON 输出**：解析后提取用户关心的字段，不要原样输出大段 JSON
4. **截图**：保存为文件，用 Read 工具展示给用户

## 错误处理

| 错误 | 处理 |
|------|------|
| `xcrawl: command not found` | 提示安装：`npm install -g @xcrawl/cli` |
| 认证失败 | 提示登录：`xcrawl login --browser` |
| 额度不足 | 运行 `xcrawl status` 查看额度，提示用户充值 |
| 超时 | 加 `--timeout 30000` 重试 |
| 页面需要 JS 渲染 | 加 `--wait-for` 等待特定元素 |
