"""
微信公众号 API 客户端
处理 access_token、素材上传、草稿创建、发布等操作
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class WechatConfig:
    """微信公众号配置"""
    app_id: str
    app_secret: str
    token_cache_file: str = None  # 默认为 None，自动设置到脚本目录

    def __post_init__(self):
        if self.token_cache_file is None:
            # 默认缓存到脚本所在目录
            script_dir = Path(__file__).parent
            self.token_cache_file = str(script_dir / ".wechat_token_cache.json")


class WechatClient:
    """微信公众号 API 客户端"""
    
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"
    
    def __init__(self, config: WechatConfig):
        self.config = config
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """获取 access_token，支持缓存"""
        # 检查内存缓存
        if not force_refresh and self._access_token and time.time() < self._token_expires_at - 300:
            return self._access_token
        
        # 检查文件缓存
        if not force_refresh and os.path.exists(self.config.token_cache_file):
            try:
                with open(self.config.token_cache_file, 'r') as f:
                    cache = json.load(f)
                    if cache.get('expires_at', 0) > time.time() + 300:
                        self._access_token = cache['access_token']
                        self._token_expires_at = cache['expires_at']
                        return self._access_token
            except (json.JSONDecodeError, KeyError):
                pass
        
        # 请求新 token
        url = f"{self.BASE_URL}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.config.app_id,
            "secret": self.config.app_secret
        }
        
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        
        if "access_token" not in result:
            raise Exception(f"获取 access_token 失败: {result.get('errmsg', 'unknown error')}")
        
        self._access_token = result["access_token"]
        self._token_expires_at = time.time() + result.get("expires_in", 7200)
        
        # 保存到文件缓存
        with open(self.config.token_cache_file, 'w') as f:
            json.dump({
                "access_token": self._access_token,
                "expires_at": self._token_expires_at
            }, f)
        
        return self._access_token
    
    def upload_image(self, image_path: str) -> str:
        """
        上传图片素材（永久素材）
        返回 media_id
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/material/add_material"
        params = {"access_token": token, "type": "image"}
        
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, params=params, files=files, timeout=30)
        
        result = response.json()
        if "media_id" not in result:
            raise Exception(f"上传图片失败: {result.get('errmsg', 'unknown error')}")
        
        return result["media_id"]
    
    def upload_article_image(self, image_path: str) -> str:
        """
        上传文章内图片（用于正文中的图片）
        返回图片 URL
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/media/uploadimg"
        params = {"access_token": token}
        
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, params=params, files=files, timeout=30)
        
        result = response.json()
        if "url" not in result:
            raise Exception(f"上传文章图片失败: {result.get('errmsg', 'unknown error')}")
        
        return result["url"]
    
    def create_draft(
        self,
        title: str,
        content: str,
        thumb_media_id: str,
        author: str = "",
        digest: str = "",
        content_source_url: str = ""
    ) -> str:
        """
        创建草稿
        返回 media_id
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/draft/add"
        params = {"access_token": token}
        
        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "content_source_url": content_source_url,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }
        
        data = {"articles": [article]}
        
        response = requests.post(
            url, 
            params=params, 
            data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        result = response.json()
        if "media_id" not in result:
            raise Exception(f"创建草稿失败: {result.get('errmsg', 'unknown error')}")
        
        return result["media_id"]
    
    def publish_draft(self, media_id: str) -> str:
        """
        发布草稿
        返回 publish_id
        """
        token = self.get_access_token()
        url = f"{self.BASE_URL}/freepublish/submit"
        params = {"access_token": token}
        data = {"media_id": media_id}
        
        response = requests.post(url, params=params, json=data, timeout=30)
        result = response.json()
        
        if result.get("errcode", 0) != 0:
            raise Exception(f"发布草稿失败: {result.get('errmsg', 'unknown error')}")
        
        return result.get("publish_id", "")
    
    def get_publish_status(self, publish_id: str) -> dict:
        """查询发布状态"""
        token = self.get_access_token()
        url = f"{self.BASE_URL}/freepublish/get"
        params = {"access_token": token}
        data = {"publish_id": publish_id}
        
        response = requests.post(url, params=params, json=data, timeout=30)
        return response.json()


# 便捷函数
def create_client_from_env() -> WechatClient:
    """从环境变量创建客户端"""
    app_id = os.environ.get("WECHAT_APP_ID")
    app_secret = os.environ.get("WECHAT_APP_SECRET")
    
    if not app_id or not app_secret:
        raise ValueError("请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
    
    return WechatClient(WechatConfig(app_id=app_id, app_secret=app_secret))
