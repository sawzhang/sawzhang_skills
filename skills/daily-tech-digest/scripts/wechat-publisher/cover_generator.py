#!/usr/bin/env python3
"""
Tech Digest 封面图生成器
根据日报内容自动生成 900x383 的微信公众号封面图
"""

import os
import re
import random
from datetime import datetime
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont


class CoverGenerator:
    """封面图生成器"""

    # 默认尺寸（微信公众号推荐）
    WIDTH = 900
    HEIGHT = 383

    # 配色方案
    THEMES = {
        "tech_blue": {
            "bg_start": (15, 23, 42),      # 深蓝
            "bg_end": (25, 18, 60),         # 深紫
            "accent": (100, 200, 255),      # 亮蓝
            "text": (255, 255, 255),        # 白色
            "tag_bg": (60, 80, 120),        # 标签背景
            "tag_text": (200, 220, 255),    # 标签文字
        },
        "ai_purple": {
            "bg_start": (20, 10, 40),
            "bg_end": (40, 20, 60),
            "accent": (180, 100, 255),
            "text": (255, 255, 255),
            "tag_bg": (80, 40, 100),
            "tag_text": (220, 180, 255),
        },
        "dev_green": {
            "bg_start": (10, 25, 20),
            "bg_end": (15, 40, 35),
            "accent": (100, 255, 180),
            "text": (255, 255, 255),
            "tag_bg": (40, 80, 60),
            "tag_text": (180, 255, 220),
        },
    }

    # 系统字体路径（macOS）
    FONT_PATHS = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]

    def __init__(self, theme: str = "tech_blue"):
        self.theme = self.THEMES.get(theme, self.THEMES["tech_blue"])
        self._load_fonts()

    def _load_fonts(self):
        """加载字体"""
        self.title_font = None
        self.date_font = None
        self.tag_font = None

        for fp in self.FONT_PATHS:
            if os.path.exists(fp):
                try:
                    self.title_font = ImageFont.truetype(fp, 48)
                    self.date_font = ImageFont.truetype(fp, 28)
                    self.tag_font = ImageFont.truetype(fp, 20)
                    self.footer_font = ImageFont.truetype(fp, 18)
                    break
                except Exception:
                    continue

        if not self.title_font:
            self.title_font = ImageFont.load_default()
            self.date_font = self.title_font
            self.tag_font = self.title_font
            self.footer_font = self.title_font

    def _draw_gradient_background(self, draw: ImageDraw.Draw):
        """绘制渐变背景"""
        start = self.theme["bg_start"]
        end = self.theme["bg_end"]

        for y in range(self.HEIGHT):
            ratio = y / self.HEIGHT
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            draw.line([(0, y), (self.WIDTH, y)], fill=(r, g, b))

    def _draw_grid_overlay(self, draw: ImageDraw.Draw):
        """绘制科技感网格"""
        grid_color = (*self.theme["accent"][:3], 15)

        for i in range(0, self.WIDTH, 60):
            draw.line([(i, 0), (i, self.HEIGHT)], fill=grid_color, width=1)
        for i in range(0, self.HEIGHT, 60):
            draw.line([(0, i), (self.WIDTH, i)], fill=grid_color, width=1)

    def _draw_glow_particles(self, draw: ImageDraw.Draw, seed: int):
        """绘制发光粒子效果"""
        random.seed(seed)
        accent = self.theme["accent"]

        for _ in range(50):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            size = random.randint(1, 3)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=accent)

    def _draw_tags(self, draw: ImageDraw.Draw, tags: List[str], start_y: int = 200):
        """绘制主题标签"""
        tag_x = 60
        tag_y = start_y

        for tag in tags[:5]:  # 最多显示5个标签
            bbox = draw.textbbox((0, 0), tag, font=self.tag_font)
            tag_width = bbox[2] - bbox[0] + 24

            # 换行检查
            if tag_x + tag_width > self.WIDTH - 60:
                tag_x = 60
                tag_y += 40

            # 绘制标签背景
            draw.rounded_rectangle(
                [tag_x, tag_y, tag_x + tag_width, tag_y + 32],
                radius=16,
                fill=self.theme["tag_bg"]
            )

            # 绘制标签文字
            draw.text(
                (tag_x + 12, tag_y + 5),
                tag,
                font=self.tag_font,
                fill=self.theme["tag_text"]
            )

            tag_x += tag_width + 12

    def extract_keywords(self, markdown_content: str) -> List[str]:
        """从 Markdown 内容中提取关键词"""
        keywords = []

        # 查找 "本期主题词" 部分
        pattern = r'`([^`]+)`'
        matches = re.findall(pattern, markdown_content)
        keywords.extend(matches[:5])

        # 如果没找到，从标题提取
        if not keywords:
            title_pattern = r'^###\s+(.+)$'
            titles = re.findall(title_pattern, markdown_content, re.MULTILINE)
            keywords.extend([t[:15] for t in titles[:5]])

        return keywords or ["Tech", "AI", "Dev"]

    def extract_date(self, markdown_content: str) -> str:
        """从 Markdown 内容中提取日期"""
        # 查找标题中的日期
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        match = re.search(date_pattern, markdown_content)
        if match:
            return match.group(1)
        return datetime.now().strftime('%Y-%m-%d')

    def generate(
        self,
        markdown_content: str,
        output_path: str,
        title: str = "Tech Digest",
        custom_tags: Optional[List[str]] = None,
        theme: Optional[str] = None
    ) -> str:
        """
        根据日报内容生成封面图

        Args:
            markdown_content: Markdown 格式的日报内容
            output_path: 输出图片路径
            title: 封面标题
            custom_tags: 自定义标签（如果不提供，从内容中提取）
            theme: 配色主题（tech_blue, ai_purple, dev_green）

        Returns:
            生成的图片路径
        """
        # 切换主题
        if theme and theme in self.THEMES:
            self.theme = self.THEMES[theme]

        # 创建图像
        img = Image.new('RGB', (self.WIDTH, self.HEIGHT))
        draw = ImageDraw.Draw(img)

        # 提取信息
        date_str = self.extract_date(markdown_content)
        tags = custom_tags or self.extract_keywords(markdown_content)

        # 使用日期作为随机种子，保证同一天生成的图片一致
        seed = int(date_str.replace('-', ''))

        # 绘制背景
        self._draw_gradient_background(draw)
        self._draw_grid_overlay(draw)
        self._draw_glow_particles(draw, seed)

        # 绘制标题
        draw.text((60, 80), title, font=self.title_font, fill=self.theme["text"])

        # 绘制日期
        draw.text((60, 145), date_str, font=self.date_font, fill=self.theme["accent"])

        # 绘制标签
        self._draw_tags(draw, tags)

        # 底部装饰线
        draw.line(
            [(60, self.HEIGHT - 50), (self.WIDTH - 60, self.HEIGHT - 50)],
            fill=self.theme["accent"],
            width=2
        )

        # 底部文字
        footer = "HN · ProductHunt · AI News"
        draw.text((60, self.HEIGHT - 40), footer, font=self.footer_font, fill=self.theme["tag_text"])

        # 保存
        img.save(output_path, "PNG", quality=95)
        return output_path


def generate_cover(
    markdown_content: str,
    output_path: Optional[str] = None,
    theme: str = "tech_blue"
) -> str:
    """
    便捷函数：生成封面图

    Args:
        markdown_content: Markdown 格式的日报内容
        output_path: 输出路径（默认根据日期自动生成）
        theme: 配色主题

    Returns:
        生成的图片路径
    """
    generator = CoverGenerator(theme=theme)
    date_str = generator.extract_date(markdown_content)

    if not output_path:
        output_path = f"tech_digest_cover_{date_str}.png"

    return generator.generate(markdown_content, output_path, theme=theme)


if __name__ == "__main__":
    # 示例用法
    sample_content = """
# Tech Digest 2026-01-03

## 本期主题词
`Anthropic收购Bun` `AI务实化` `MCP标准` `三巨头IPO`

## 60秒速览
> 今日科技圈重大事件...
"""

    output = generate_cover(sample_content, "sample_cover.png")
    print(f"封面图已生成: {output}")
