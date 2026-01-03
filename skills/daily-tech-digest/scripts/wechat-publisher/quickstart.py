#!/usr/bin/env python3
"""
微信公众号发布快速入门
交互式引导完成配置和首次发布
"""

import os
import sys


def print_header():
    print("=" * 60)
    print("🚀 微信公众号 Tech Digest 发布器 - 快速入门")
    print("=" * 60)
    print()


def print_menu():
    print("请选择操作：")
    print("  1. 测试 API 连通性")
    print("  2. 上传封面图片")
    print("  3. 发布 Markdown 文件")
    print("  4. 查看配置说明")
    print("  0. 退出")
    print()


def test_connection():
    """测试 API 连通性"""
    from wechat_client import WechatClient, WechatConfig
    
    app_id = os.environ.get("WECHAT_APP_ID") or input("请输入 AppID: ").strip()
    app_secret = os.environ.get("WECHAT_APP_SECRET") or input("请输入 AppSecret: ").strip()
    
    print()
    print("🔍 测试连接中...")
    
    try:
        client = WechatClient(WechatConfig(app_id=app_id, app_secret=app_secret))
        token = client.get_access_token()
        print(f"✅ 连接成功！")
        print(f"   access_token: {token[:20]}...{token[-10:]}")
        print()
        
        # 保存到环境变量提示
        print("💡 建议设置环境变量避免重复输入：")
        print(f"   export WECHAT_APP_ID={app_id}")
        print(f"   export WECHAT_APP_SECRET={app_secret}")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print()
        print("常见问题：")
        print("  - 40001: AppSecret 错误")
        print("  - 40013: AppID 无效")
        print("  - 40164: IP 不在白名单中")


def upload_cover():
    """上传封面图片"""
    from wechat_client import create_client_from_env
    
    print("📷 上传封面图片")
    print()
    
    # 检查环境变量
    if not os.environ.get("WECHAT_APP_ID"):
        print("⚠️ 请先设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        print("   或先运行选项 1 测试连接")
        return
    
    image_path = input("请输入封面图片路径: ").strip()
    
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return
    
    print()
    print("⏳ 上传中...")
    
    try:
        client = create_client_from_env()
        media_id = client.upload_image(image_path)
        print(f"✅ 上传成功！")
        print(f"   media_id: {media_id}")
        print()
        print("💡 请保存此 media_id，后续发布时使用：")
        print(f"   export WECHAT_COVER_ID={media_id}")
        
    except Exception as e:
        print(f"❌ 上传失败: {e}")


def publish_markdown():
    """发布 Markdown 文件"""
    from publisher import publish_tech_digest
    
    print("📄 发布 Markdown 文件")
    print()
    
    # 检查环境变量
    required_vars = ["WECHAT_APP_ID", "WECHAT_APP_SECRET", "WECHAT_COVER_ID"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    
    if missing:
        print("⚠️ 缺少环境变量：")
        for v in missing:
            print(f"   - {v}")
        print()
        print("请先设置环境变量或运行选项 1、2")
        return
    
    markdown_file = input("请输入 Markdown 文件路径: ").strip()
    
    if not os.path.exists(markdown_file):
        print(f"❌ 文件不存在: {markdown_file}")
        return
    
    auto_publish = input("是否自动发布？(y/N): ").strip().lower() == 'y'
    
    print()
    print("⏳ 处理中...")
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = publish_tech_digest(
        content,
        cover_media_id=os.environ.get("WECHAT_COVER_ID"),
        auto_publish=auto_publish
    )
    
    if result.success:
        print("✅ 操作成功！")
        print(f"   草稿 media_id: {result.draft_media_id}")
        if result.publish_id:
            print(f"   发布 publish_id: {result.publish_id}")
        print()
        print("💡 请到公众号后台查看草稿并确认发布")
        print("   https://mp.weixin.qq.com")
    else:
        print(f"❌ 操作失败: {result.error}")


def show_config_help():
    """显示配置说明"""
    print("""
📖 配置说明

1. 获取 AppID 和 AppSecret
   - 登录公众号后台: https://mp.weixin.qq.com
   - 进入: 开发 → 基本配置
   - 获取 AppID，重置并保存 AppSecret

2. 设置 IP 白名单
   - 在公众号后台 → 开发 → 基本配置 → IP 白名单
   - 添加你的服务器 IP

3. 设置环境变量
   export WECHAT_APP_ID=wx...
   export WECHAT_APP_SECRET=...
   export WECHAT_COVER_ID=...  # 上传封面图后获取

4. 封面图要求
   - 格式: JPG/PNG
   - 尺寸: 建议 900x383 或 2.35:1 比例
   - 大小: < 10MB

5. 发布流程
   - 默认只创建草稿，需要到公众号后台确认发布
   - 设置 auto_publish=True 可自动发布（不推荐）

⚠️ 安全提醒
   - AppSecret 不要硬编码到代码中
   - 使用环境变量或配置文件管理凭证
   - 定期轮换 AppSecret
""")


def main():
    print_header()
    
    while True:
        print_menu()
        choice = input("请选择 (0-4): ").strip()
        print()
        
        if choice == '0':
            print("👋 再见！")
            break
        elif choice == '1':
            test_connection()
        elif choice == '2':
            upload_cover()
        elif choice == '3':
            publish_markdown()
        elif choice == '4':
            show_config_help()
        else:
            print("❌ 无效选择，请重试")
        
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    # 添加当前目录到 path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
