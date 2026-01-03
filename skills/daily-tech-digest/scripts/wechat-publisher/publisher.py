"""
微信公众号发布器
整合 Markdown 转换和微信 API，实现一键发布
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from .wechat_client import WechatClient, WechatConfig
from .md_converter import convert_markdown_to_wechat


@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    draft_media_id: Optional[str] = None
    publish_id: Optional[str] = None
    error: Optional[str] = None
    article_url: Optional[str] = None


class TechDigestPublisher:
    """技术日报发布器"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.client = WechatClient(WechatConfig(
            app_id=app_id,
            app_secret=app_secret
        ))
        self._cover_media_id: Optional[str] = None
    
    def set_cover_image(self, image_path: str) -> str:
        """设置封面图片"""
        self._cover_media_id = self.client.upload_image(image_path)
        return self._cover_media_id
    
    def set_cover_media_id(self, media_id: str):
        """直接设置封面 media_id（如果已经上传过）"""
        self._cover_media_id = media_id
    
    def publish_markdown(
        self,
        markdown_content: str,
        title: Optional[str] = None,
        author: str = "Tech Digest",
        digest: Optional[str] = None,
        auto_publish: bool = False,
        cover_image_path: Optional[str] = None
    ) -> PublishResult:
        """
        发布 Markdown 内容到微信公众号
        
        Args:
            markdown_content: Markdown 格式的文章内容
            title: 文章标题（如果不提供，会从内容中提取）
            author: 作者名
            digest: 文章摘要（如果不提供，会自动生成）
            auto_publish: 是否自动发布（False 则只创建草稿）
            cover_image_path: 封面图片路径
        
        Returns:
            PublishResult 对象
        """
        try:
            # 1. 提取/生成标题
            if not title:
                title = self._extract_title(markdown_content)
            
            # 2. 生成摘要
            if not digest:
                digest = self._generate_digest(markdown_content)
            
            # 3. 转换 Markdown 为微信 HTML
            html_content = convert_markdown_to_wechat(markdown_content)
            
            # 4. 处理封面图片
            if cover_image_path:
                self.set_cover_image(cover_image_path)
            
            if not self._cover_media_id:
                raise ValueError("请先设置封面图片（调用 set_cover_image 或 set_cover_media_id）")
            
            # 5. 创建草稿
            draft_media_id = self.client.create_draft(
                title=title,
                content=html_content,
                thumb_media_id=self._cover_media_id,
                author=author,
                digest=digest
            )
            
            result = PublishResult(
                success=True,
                draft_media_id=draft_media_id
            )
            
            # 6. 如果需要自动发布
            if auto_publish:
                publish_id = self.client.publish_draft(draft_media_id)
                result.publish_id = publish_id
            
            return result
            
        except Exception as e:
            return PublishResult(
                success=False,
                error=str(e)
            )
    
    def publish_file(
        self,
        markdown_file: str,
        **kwargs
    ) -> PublishResult:
        """
        从文件发布 Markdown 内容
        """
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.publish_markdown(content, **kwargs)
    
    def _extract_title(self, markdown: str) -> str:
        """从 Markdown 中提取标题"""
        lines = markdown.strip().split('\n')
        for line in lines:
            if line.startswith('# '):
                # 提取标题并清理 emoji
                title = line[2:].strip()
                # 移除日期中的 emoji
                title = title.replace('🗓️ ', '').replace('🗓', '')
                return title
        
        # 默认标题
        today = datetime.now().strftime('%Y-%m-%d')
        return f"Tech Digest {today}"
    
    def _generate_digest(self, markdown: str, max_length: int = 120) -> str:
        """生成文章摘要"""
        # 查找 "60秒速览" 部分
        lines = markdown.split('\n')
        in_summary = False
        summary_lines = []
        
        for line in lines:
            if '60秒速览' in line or '速览' in line:
                in_summary = True
                continue
            if in_summary:
                if line.startswith('#'):
                    break
                if line.startswith('>'):
                    summary_lines.append(line[1:].strip())
                elif line.strip():
                    summary_lines.append(line.strip())
        
        if summary_lines:
            digest = ' '.join(summary_lines)
        else:
            # 取前几段文字
            text_lines = [l.strip() for l in lines if l.strip() and not l.startswith('#') and not l.startswith('|')]
            digest = ' '.join(text_lines[:3])
        
        # 截断
        if len(digest) > max_length:
            digest = digest[:max_length - 3] + '...'
        
        return digest


def publish_tech_digest(
    markdown_content: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None,
    cover_image_path: Optional[str] = None,
    cover_media_id: Optional[str] = None,
    auto_publish: bool = False
) -> PublishResult:
    """
    便捷函数：发布技术日报
    
    Usage:
        # 方式1: 传入凭证
        result = publish_tech_digest(
            markdown_content,
            app_id="wx...",
            app_secret="...",
            cover_media_id="...",
            auto_publish=False  # 只创建草稿，不自动发布
        )
        
        # 方式2: 使用环境变量
        # export WECHAT_APP_ID=wx...
        # export WECHAT_APP_SECRET=...
        result = publish_tech_digest(markdown_content, cover_media_id="...")
    """
    # 获取凭证
    app_id = app_id or os.environ.get("WECHAT_APP_ID")
    app_secret = app_secret or os.environ.get("WECHAT_APP_SECRET")
    
    if not app_id or not app_secret:
        return PublishResult(
            success=False,
            error="请提供 app_id 和 app_secret，或设置环境变量 WECHAT_APP_ID / WECHAT_APP_SECRET"
        )
    
    publisher = TechDigestPublisher(app_id, app_secret)
    
    # 设置封面
    if cover_media_id:
        publisher.set_cover_media_id(cover_media_id)
    elif cover_image_path:
        publisher.set_cover_image(cover_image_path)
    else:
        return PublishResult(
            success=False,
            error="请提供封面图片路径（cover_image_path）或已上传的 media_id（cover_media_id）"
        )
    
    return publisher.publish_markdown(
        markdown_content,
        auto_publish=auto_publish
    )
