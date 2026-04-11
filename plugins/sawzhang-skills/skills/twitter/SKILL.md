---
name: twitter
description: Twitter/X 一站式工具：读推文、搜索话题、发帖、发 thread。触发词："读推文"、"搜Twitter"、"发推"、"发thread"、"twitter post"、"twitter search"、"read tweet"、"post tweet"。
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Twitter/X 一站式 Skill

四种模式，根据用户指令自动判断：

| 触发词 | 模式 | 方式 |
|--------|------|------|
| 读推文、read tweet、看推文 + URL | **read** | fxtwitter API |
| 搜Twitter、twitter research、X上关于 | **search** | browser-use / fxtwitter |
| 发推、twitter post、发一条 | **post** | X API v2 OAuth 1.0a |
| 发thread、twitter thread | **thread** | X API v2 连续 post |

---

## 模式一：Read（读推文）

用户分享 Twitter/X 链接时触发。

### Step 1: 从 URL 提取用户名和推文 ID

支持的 URL 格式：
- `https://x.com/{username}/status/{tweet_id}`
- `https://twitter.com/{username}/status/{tweet_id}`

### Step 2: 通过 fxtwitter API 获取

```bash
curl -s "https://api.fxtwitter.com/{username}/status/{tweet_id}"
```

### Step 3: 格式化输出

```
**作者**: {name} (@{handle}) | **时间**: {time}
**互动**: {likes} 赞 | {retweets} 转 | {views} 浏览

{推文正文}
```

### 降级方案

fxtwitter 不可用时：
1. `curl -s "https://api.vxtwitter.com/{username}/status/{tweet_id}"`
2. WebSearch 搜索推文 ID

---

## 模式二：Search（搜索话题）

用户说"搜Twitter"、"X上关于XX的讨论"时触发。

### Step 1: 生成 3-5 组搜索关键词

中英文双搜，包括核心词 + 细分词 + 关联项目名。

### Step 2: 尝试 browser-use（首选）

```bash
# 定义 wrapper 清除代理
bu() { ALL_PROXY= HTTP_PROXY= HTTPS_PROXY= http_proxy= https_proxy= all_proxy= browser-use "$@"; }

# 安装检测
if ! which browser-use &>/dev/null; then
  uv tool install browser-use && browser-use install
fi

# 搜索
bu -b real open "https://x.com/search?q={关键词URL编码}&src=typed_query&f=top"
sleep 3
bu state 2>&1
```

**限速规则**：每次搜索间隔 8-10 秒，否则结果会一直转圈。

### Step 3: 降级到 fxtwitter

browser-use 不可用时，用 WebSearch 搜 `"{关键词} site:x.com"`，提取推文 URL 后用 fxtwitter API 获取详情。

### Step 4: 汇总输出

按互动量排序，分主题分组，输出结构化报告。

---

## 模式三：Post（发帖）

用户说"发推"、"tweet this"、"发一条推文"时触发。

### 前置条件

需要 X API v2 OAuth 1.0a 凭据（4 个环境变量）：

```bash
export X_API_KEY="your_consumer_key"
export X_API_SECRET="your_consumer_secret"
export X_ACCESS_TOKEN="your_access_token"
export X_ACCESS_SECRET="your_access_token_secret"
```

从 https://console.x.com 创建 App → Keys and Tokens 获取。
App permissions 必须设为 **Read and Write**。

### Step 1: 检查凭据

```bash
python3 -c "
from requests_oauthlib import OAuth1Session
import os
session = OAuth1Session(os.environ['X_API_KEY'], os.environ['X_API_SECRET'], os.environ['X_ACCESS_TOKEN'], os.environ['X_ACCESS_SECRET'])
r = session.get('https://api.x.com/2/users/me')
print(r.json() if r.status_code == 200 else f'ERROR {r.status_code}: {r.text[:200]}')
"
```

如果 401：凭据错误或过期。如果缺少依赖：`pip3 install --break-system-packages requests-oauthlib`

### Step 2: 发帖

使用 skill 目录下的 `post.py` 脚本：

```bash
# 找到 post.py 的路径
SKILL_DIR=$(find ~/.claude -path "*/skills/twitter/post.py" -exec dirname {} \; 2>/dev/null | head -1)

# 发单条
python3 "$SKILL_DIR/post.py" "推文内容"
```

或者直接用 Python：

```bash
python3 -c "
from requests_oauthlib import OAuth1Session
import os, json
session = OAuth1Session(os.environ['X_API_KEY'], os.environ['X_API_SECRET'], os.environ['X_ACCESS_TOKEN'], os.environ['X_ACCESS_SECRET'])
r = session.post('https://api.x.com/2/tweets', json={'text': '推文内容'})
print(json.dumps(r.json(), indent=2))
"
```

### 发帖注意事项（实测经验）

| 问题 | 原因 | 解决 |
|------|------|------|
| 403 duplicate content | 与近期推文完全相同 | 修改措辞或加时间戳 |
| 403 not permitted | 长文本含特殊组合触发 spam 检测 | 缩短到 200 字内，去掉 `#` 和密集 URL |
| 401 unauthorized | API Key 过期或权限不足 | 重新生成 token，确认 Read+Write 权限 |
| 429 rate limit | 15 分钟内发太多 | 等待 reset（查看 x-rate-limit-reset header） |

---

## 模式四：Thread（发 thread）

用户说"发thread"、"发9条thread"时触发。

### Step 1: 准备 thread 内容

让用户确认 thread 内容（JSON 数组格式），或根据上下文生成。每条控制在 200 字符内（中文）以避免 spam 检测。

### Step 2: 写入 JSON 文件

```bash
cat > /tmp/thread.json << 'EOF'
[
  "1/N 第一条内容",
  "2/N 第二条内容",
  "..."
]
EOF
```

### Step 3: 发送

```bash
SKILL_DIR=$(find ~/.claude -path "*/skills/twitter/post.py" -exec dirname {} \; 2>/dev/null | head -1)
python3 "$SKILL_DIR/post.py" --thread /tmp/thread.json
```

### Thread 策略（实测经验）

X API pay-per-use 层对 reply 操作有限制。`post.py` 内置了降级逻辑：

1. **首选**：reply 链（真正的 thread）
2. **降级**：reply 被 403 时自动切换为独立推文
3. **限速**：每条间隔 4 秒，避免触发 anti-automation
4. **去重**：每条推文内容必须唯一，否则 403 duplicate

---

## 凭据管理

推荐在 `~/.zshrc` 中设置：

```bash
# X API v2 (https://console.x.com)
export X_API_KEY="..."
export X_API_SECRET="..."
export X_ACCESS_TOKEN="..."
export X_ACCESS_SECRET="..."
```

Bearer Token（读取用，可选）：
```bash
export X_BEARER_TOKEN="..."
```

这些凭据不会被写入任何文件或日志。`post.py` 只从环境变量读取。

---

## 组合工作流示例

```
用户：搜一下 Twitter 上关于 Claude Code 降智的讨论，总结后发一条 thread

→ 模式二 search：搜索 "Claude Code degradation"、"Claude Code 降智"
→ 整理搜索结果为 thread 内容
→ 模式四 thread：发送 thread
```
