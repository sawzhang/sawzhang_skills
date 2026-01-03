#!/usr/bin/env python3
"""
Tech Digest 定时任务脚本
每日自动生成技术日报并发布到微信公众号

使用方法：
    python3 daily_digest_cron.py

环境变量：
    WECHAT_APP_ID      - 微信公众号 AppID
    WECHAT_APP_SECRET  - 微信公众号 AppSecret
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加 wechat-publisher 模块路径
SCRIPT_DIR = Path(__file__).parent
PUBLISHER_DIR = SCRIPT_DIR / "wechat-publisher"
sys.path.insert(0, str(PUBLISHER_DIR))

from wechat_client import WechatClient, WechatConfig
from md_converter import convert_markdown_to_wechat
from cover_generator import generate_cover

# 配置日志
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"digest_{datetime.now().strftime('%Y%m')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============ 数据采集 ============

def fetch_hn_top_stories() -> list:
    """获取 Hacker News 热门文章"""
    import requests

    try:
        # 使用 HN API
        resp = requests.get("https://hacker-news.firebaseio.com/v0/beststories.json", timeout=10)
        story_ids = resp.json()[:15]

        stories = []
        for sid in story_ids[:10]:  # 只取前10个减少请求
            story_resp = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5)
            story = story_resp.json()
            if story:
                stories.append({
                    "title": story.get("title", ""),
                    "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                    "score": story.get("score", 0),
                    "comments": story.get("descendants", 0)
                })

        logger.info(f"获取 HN 文章: {len(stories)} 篇")
        return stories
    except Exception as e:
        logger.error(f"获取 HN 失败: {e}")
        return []


def fetch_producthunt_products() -> list:
    """获取 Product Hunt 热门产品（简化版）"""
    # 由于 PH 需要 API key，这里使用占位数据
    # 实际使用时可以接入 PH API
    logger.info("Product Hunt 数据使用占位（需配置 API key）")
    return [
        {"name": "待配置", "tagline": "配置 Product Hunt API 后自动获取", "upvotes": 0}
    ]


def search_ai_news() -> list:
    """搜索 AI 相关新闻（简化版）"""
    # 实际使用时可以接入新闻 API
    logger.info("AI 新闻使用占位（可接入新闻 API）")
    return [
        {"source": "AI News", "summary": "今日 AI 动态汇总"}
    ]


# ============ 内容生成 ============

def categorize_story(title: str) -> str:
    """根据标题分类"""
    title_lower = title.lower()

    if any(kw in title_lower for kw in ['ai', 'ml', 'gpt', 'llm', 'claude', 'openai', 'anthropic', 'model']):
        return "AI/ML"
    elif any(kw in title_lower for kw in ['rust', 'go', 'python', 'javascript', 'typescript', 'github', 'git', 'docker', 'kubernetes']):
        return "DevTools"
    elif any(kw in title_lower for kw in ['startup', 'funding', 'ipo', 'acquisition', 'billion', 'million']):
        return "Business"
    elif any(kw in title_lower for kw in ['design', 'ux', 'ui', 'product', 'user']):
        return "Product/UX"
    else:
        return "Other"


def generate_digest_content(hn_stories: list, ph_products: list, ai_news: list) -> str:
    """生成日报 Markdown 内容"""
    today = datetime.now().strftime('%Y-%m-%d')

    # 提取关键词
    keywords = []
    for story in hn_stories[:5]:
        title = story.get("title", "")
        # 简单提取：取标题中的重要词
        words = [w for w in title.split() if len(w) > 4 and w[0].isupper()]
        keywords.extend(words[:2])
    keywords = list(set(keywords))[:5] or ["Tech", "AI", "Dev"]

    # 生成速览
    top_stories = hn_stories[:3]
    summary_points = []
    for s in top_stories:
        summary_points.append(f"{s['title']}（{s['score']} points）")
    summary = "；".join(summary_points) + "。" if summary_points else "今日技术动态汇总。"

    # 构建 Markdown
    content = f"""# Tech Digest {today}

## 60秒速览

> {summary}

## 趋势雷达

### 本期主题词
{' '.join([f'`{kw}`' for kw in keywords])}

### 趋势矩阵

| 趋势 | 信号强度 | 阶段 | 影响范围 |
|------|---------|------|---------|
"""

    # 添加趋势
    seen_categories = set()
    for story in hn_stories[:5]:
        cat = categorize_story(story['title'])
        if cat not in seen_categories:
            seen_categories.add(cat)
            strength = "强" if story['score'] > 500 else ("中" if story['score'] > 200 else "弱")
            content += f"| {cat} | {strength} | 成长 | 广泛 |\n"

    content += """
## 深度解读

"""

    # 添加深度解读
    for i, story in enumerate(hn_stories[:3], 1):
        cat = categorize_story(story['title'])
        content += f"""### {story['title'][:50]}{'...' if len(story['title']) > 50 else ''}

**领域**: {cat}
**热度**: {story['score']} points, {story['comments']} comments
**链接**: {story['url']}

---

"""

    content += """## 原始素材

### Hacker News Top 10

| # | 热度 | 标题 | 领域 |
|---|------|------|------|
"""

    for i, story in enumerate(hn_stories[:10], 1):
        cat = categorize_story(story['title'])
        title = story['title'][:40] + ('...' if len(story['title']) > 40 else '')
        content += f"| {i} | {story['score']} | {title} | {cat} |\n"

    content += f"""
---
*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')} | Sources: HN, ProductHunt, AI News*
"""

    return content


# ============ 发布流程 ============

def publish_to_wechat(content: str, output_dir: Path) -> dict:
    """发布到微信公众号"""

    # 检查环境变量
    app_id = os.environ.get("WECHAT_APP_ID")
    app_secret = os.environ.get("WECHAT_APP_SECRET")

    if not app_id or not app_secret:
        return {"success": False, "error": "缺少环境变量 WECHAT_APP_ID 或 WECHAT_APP_SECRET"}

    try:
        today = datetime.now().strftime('%Y-%m-%d')

        # 生成封面图
        cover_path = output_dir / f"cover_{today}.png"
        generate_cover(content, str(cover_path))
        logger.info(f"封面图已生成: {cover_path}")

        # 创建客户端
        client = WechatClient(WechatConfig(app_id=app_id, app_secret=app_secret))

        # 上传封面
        cover_media_id = client.upload_image(str(cover_path))
        logger.info(f"封面已上传: {cover_media_id}")

        # 转换内容
        html_content = convert_markdown_to_wechat(content)

        # 提取标题
        title = f"Tech Digest {today}"
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break

        # 提取摘要
        digest = ""
        in_summary = False
        for line in content.split('\n'):
            if '60秒速览' in line:
                in_summary = True
                continue
            if in_summary and line.startswith('>'):
                digest = line[1:].strip()[:120]
                break

        # 创建草稿
        draft_media_id = client.create_draft(
            title=title,
            content=html_content,
            thumb_media_id=cover_media_id,
            author="Tech Digest",
            digest=digest or "今日技术动态汇总"
        )

        logger.info(f"草稿创建成功: {draft_media_id}")

        return {
            "success": True,
            "draft_media_id": draft_media_id,
            "cover_media_id": cover_media_id
        }

    except Exception as e:
        logger.error(f"发布失败: {e}")
        return {"success": False, "error": str(e)}


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("Tech Digest 定时任务开始")
    logger.info("=" * 50)

    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    try:
        # 1. 采集数据
        logger.info("Phase 1: 采集数据")
        hn_stories = fetch_hn_top_stories()
        ph_products = fetch_producthunt_products()
        ai_news = search_ai_news()

        if not hn_stories:
            logger.warning("未获取到 HN 数据，使用备用内容")
            hn_stories = [{"title": "数据获取失败", "url": "#", "score": 0, "comments": 0}]

        # 2. 生成内容
        logger.info("Phase 2: 生成内容")
        content = generate_digest_content(hn_stories, ph_products, ai_news)

        # 保存 Markdown
        md_path = output_dir / f"tech_digest_{today}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"日报已保存: {md_path}")

        # 3. 发布到微信
        logger.info("Phase 3: 发布到微信")
        result = publish_to_wechat(content, output_dir)

        if result["success"]:
            logger.info(f"发布成功! Draft ID: {result['draft_media_id']}")
            logger.info("请到公众号后台确认发布: https://mp.weixin.qq.com")
        else:
            logger.error(f"发布失败: {result['error']}")

        # 保存结果
        result_path = output_dir / f"result_{today}.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump({
                "date": today,
                "md_path": str(md_path),
                "result": result
            }, f, ensure_ascii=False, indent=2)

        logger.info("=" * 50)
        logger.info("Tech Digest 定时任务完成")
        logger.info("=" * 50)

        return 0 if result["success"] else 1

    except Exception as e:
        logger.exception(f"任务执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
