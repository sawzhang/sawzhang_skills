"""
Markdown 转微信公众号 HTML 转换器
将 Markdown 转换为微信公众号兼容的带内联样式 HTML
"""

import re
from typing import Optional


class WechatMDConverter:
    """Markdown 转微信 HTML 转换器"""
    
    # 微信公众号样式配置
    STYLES = {
        # 整体容器
        "container": """
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            font-size: 16px;
            line-height: 1.8;
            color: #333;
            padding: 10px;
        """,
        # 标题样式
        "h1": """
            font-size: 24px;
            font-weight: bold;
            color: #1a1a1a;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #07c160;
        """,
        "h2": """
            font-size: 20px;
            font-weight: bold;
            color: #1a1a1a;
            margin: 25px 0 15px 0;
            padding-left: 10px;
            border-left: 4px solid #07c160;
        """,
        "h3": """
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin: 20px 0 10px 0;
        """,
        # 段落
        "p": """
            margin: 15px 0;
            text-align: justify;
        """,
        # 引用块（用于60秒速览等）
        "blockquote": """
            margin: 20px 0;
            padding: 15px 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 100%);
            border-left: 4px solid #07c160;
            border-radius: 4px;
            color: #555;
            font-size: 15px;
        """,
        # 代码块
        "code_block": """
            display: block;
            margin: 15px 0;
            padding: 15px;
            background: #1e1e1e;
            color: #d4d4d4;
            border-radius: 6px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 14px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        """,
        # 行内代码
        "code_inline": """
            background: #f3f4f6;
            color: #e83e8c;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 14px;
        """,
        # 表格
        "table": """
            width: 100%;
            margin: 20px 0;
            border-collapse: collapse;
            font-size: 14px;
        """,
        "th": """
            background: #07c160;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: bold;
        """,
        "td": """
            padding: 10px 8px;
            border-bottom: 1px solid #e5e5e5;
        """,
        "tr_even": """
            background: #f9f9f9;
        """,
        # 列表
        "ul": """
            margin: 15px 0;
            padding-left: 25px;
        """,
        "ol": """
            margin: 15px 0;
            padding-left: 25px;
        """,
        "li": """
            margin: 8px 0;
        """,
        # 链接
        "a": """
            color: #07c160;
            text-decoration: none;
        """,
        # 加粗
        "strong": """
            color: #1a1a1a;
            font-weight: bold;
        """,
        # 标签样式（用于关键词）
        "tag": """
            display: inline-block;
            background: linear-gradient(135deg, #07c160 0%, #06ae56 100%);
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 13px;
            margin: 3px;
        """,
        # 分隔线
        "hr": """
            margin: 30px 0;
            border: none;
            border-top: 1px dashed #ddd;
        """,
        # 图片
        "img": """
            max-width: 100%;
            height: auto;
            display: block;
            margin: 15px auto;
            border-radius: 6px;
        """,
        # 脚注
        "footer": """
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #eee;
            font-size: 13px;
            color: #888;
            text-align: center;
        """
    }
    
    def __init__(self, custom_styles: Optional[dict] = None):
        self.styles = self.STYLES.copy()
        if custom_styles:
            self.styles.update(custom_styles)
    
    def _clean_style(self, style: str) -> str:
        """清理样式字符串，移除换行和多余空格"""
        return ' '.join(style.split())
    
    def convert(self, markdown: str) -> str:
        """将 Markdown 转换为微信 HTML"""
        html = markdown
        
        # 1. 处理代码块（先处理，避免内部内容被误转换）
        html = self._convert_code_blocks(html)
        
        # 2. 处理表格
        html = self._convert_tables(html)
        
        # 3. 处理标题
        html = self._convert_headings(html)
        
        # 4. 处理引用块
        html = self._convert_blockquotes(html)
        
        # 5. 处理列表
        html = self._convert_lists(html)
        
        # 6. 处理行内元素
        html = self._convert_inline_elements(html)
        
        # 7. 处理段落
        html = self._convert_paragraphs(html)
        
        # 8. 处理分隔线
        html = self._convert_hr(html)
        
        # 9. 处理标签样式的关键词（`keyword` 格式）
        html = self._convert_tags(html)
        
        # 包装在容器中
        container_style = self._clean_style(self.styles["container"])
        html = f'<section style="{container_style}">{html}</section>'
        
        return html
    
    def _convert_code_blocks(self, html: str) -> str:
        """转换代码块"""
        code_style = self._clean_style(self.styles["code_block"])
        
        def replace_code_block(match):
            lang = match.group(1) or ""
            code = match.group(2)
            # HTML 转义
            code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return f'<pre style="{code_style}"><code>{code}</code></pre>'
        
        # 匹配 ```lang\ncode\n```
        html = re.sub(r'```(\w*)\n(.*?)\n```', replace_code_block, html, flags=re.DOTALL)
        
        return html
    
    def _convert_tables(self, html: str) -> str:
        """转换表格"""
        table_style = self._clean_style(self.styles["table"])
        th_style = self._clean_style(self.styles["th"])
        td_style = self._clean_style(self.styles["td"])
        tr_even_style = self._clean_style(self.styles["tr_even"])
        
        lines = html.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 检测表格开始（包含 | 的行）
            if '|' in line and i + 1 < len(lines) and re.match(r'^\s*\|[\s\-:|]+\|\s*$', lines[i + 1]):
                # 解析表头
                headers = [cell.strip() for cell in line.strip().strip('|').split('|')]
                
                # 跳过分隔行
                i += 2
                
                # 构建表格
                table_html = f'<table style="{table_style}">'
                table_html += '<thead><tr>'
                for header in headers:
                    table_html += f'<th style="{th_style}">{header}</th>'
                table_html += '</tr></thead><tbody>'
                
                # 解析数据行
                row_count = 0
                while i < len(lines) and '|' in lines[i]:
                    cells = [cell.strip() for cell in lines[i].strip().strip('|').split('|')]
                    row_style = tr_even_style if row_count % 2 == 1 else ""
                    table_html += f'<tr style="{row_style}">'
                    for cell in cells:
                        table_html += f'<td style="{td_style}">{cell}</td>'
                    table_html += '</tr>'
                    row_count += 1
                    i += 1
                
                table_html += '</tbody></table>'
                result.append(table_html)
            else:
                result.append(line)
                i += 1
        
        return '\n'.join(result)
    
    def _convert_headings(self, html: str) -> str:
        """转换标题"""
        h1_style = self._clean_style(self.styles["h1"])
        h2_style = self._clean_style(self.styles["h2"])
        h3_style = self._clean_style(self.styles["h3"])
        
        # H1
        html = re.sub(r'^# (.+)$', f'<h1 style="{h1_style}">\\1</h1>', html, flags=re.MULTILINE)
        # H2
        html = re.sub(r'^## (.+)$', f'<h2 style="{h2_style}">\\1</h2>', html, flags=re.MULTILINE)
        # H3
        html = re.sub(r'^### (.+)$', f'<h3 style="{h3_style}">\\1</h3>', html, flags=re.MULTILINE)
        
        return html
    
    def _convert_blockquotes(self, html: str) -> str:
        """转换引用块"""
        blockquote_style = self._clean_style(self.styles["blockquote"])
        
        lines = html.split('\n')
        result = []
        quote_buffer = []
        in_quote = False
        
        for line in lines:
            if line.startswith('> '):
                in_quote = True
                quote_buffer.append(line[2:])
            else:
                if in_quote:
                    quote_content = '<br>'.join(quote_buffer)
                    result.append(f'<blockquote style="{blockquote_style}">{quote_content}</blockquote>')
                    quote_buffer = []
                    in_quote = False
                result.append(line)
        
        # 处理末尾的引用
        if quote_buffer:
            quote_content = '<br>'.join(quote_buffer)
            result.append(f'<blockquote style="{blockquote_style}">{quote_content}</blockquote>')
        
        return '\n'.join(result)
    
    def _convert_lists(self, html: str) -> str:
        """转换列表"""
        ul_style = self._clean_style(self.styles["ul"])
        ol_style = self._clean_style(self.styles["ol"])
        li_style = self._clean_style(self.styles["li"])
        
        lines = html.split('\n')
        result = []
        list_buffer = []
        list_type = None
        
        for line in lines:
            # 无序列表
            ul_match = re.match(r'^[\s]*[-*+] (.+)$', line)
            # 有序列表
            ol_match = re.match(r'^[\s]*\d+\. (.+)$', line)
            
            if ul_match:
                if list_type != 'ul':
                    if list_buffer:
                        result.append(self._build_list(list_buffer, list_type, ul_style, ol_style, li_style))
                        list_buffer = []
                    list_type = 'ul'
                list_buffer.append(ul_match.group(1))
            elif ol_match:
                if list_type != 'ol':
                    if list_buffer:
                        result.append(self._build_list(list_buffer, list_type, ul_style, ol_style, li_style))
                        list_buffer = []
                    list_type = 'ol'
                list_buffer.append(ol_match.group(1))
            else:
                if list_buffer:
                    result.append(self._build_list(list_buffer, list_type, ul_style, ol_style, li_style))
                    list_buffer = []
                    list_type = None
                result.append(line)
        
        if list_buffer:
            result.append(self._build_list(list_buffer, list_type, ul_style, ol_style, li_style))
        
        return '\n'.join(result)
    
    def _build_list(self, items: list, list_type: str, ul_style: str, ol_style: str, li_style: str) -> str:
        """构建列表 HTML"""
        tag = 'ul' if list_type == 'ul' else 'ol'
        style = ul_style if list_type == 'ul' else ol_style
        items_html = ''.join([f'<li style="{li_style}">{item}</li>' for item in items])
        return f'<{tag} style="{style}">{items_html}</{tag}>'
    
    def _convert_inline_elements(self, html: str) -> str:
        """转换行内元素"""
        strong_style = self._clean_style(self.styles["strong"])
        code_style = self._clean_style(self.styles["code_inline"])
        a_style = self._clean_style(self.styles["a"])
        
        # 加粗 **text** 或 __text__
        html = re.sub(r'\*\*(.+?)\*\*', f'<strong style="{strong_style}">\\1</strong>', html)
        html = re.sub(r'__(.+?)__', f'<strong style="{strong_style}">\\1</strong>', html)
        
        # 斜体 *text* 或 _text_
        html = re.sub(r'\*([^*]+)\*', '<em>\\1</em>', html)
        html = re.sub(r'_([^_]+)_', '<em>\\1</em>', html)
        
        # 行内代码 `code`（但不处理已经转换的代码块）
        html = re.sub(r'`([^`]+)`', f'<code style="{code_style}">\\1</code>', html)
        
        # 链接 [text](url)
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', f'<a href="\\2" style="{a_style}">\\1</a>', html)
        
        # 图片 ![alt](url)
        img_style = self._clean_style(self.styles["img"])
        html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', f'<img src="\\2" alt="\\1" style="{img_style}">', html)
        
        return html
    
    def _convert_paragraphs(self, html: str) -> str:
        """转换段落"""
        p_style = self._clean_style(self.styles["p"])
        
        lines = html.split('\n')
        result = []
        
        for line in lines:
            stripped = line.strip()
            # 跳过已经是 HTML 标签的行
            if (stripped and 
                not stripped.startswith('<') and 
                not stripped.startswith('|')):
                result.append(f'<p style="{p_style}">{stripped}</p>')
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _convert_hr(self, html: str) -> str:
        """转换分隔线"""
        hr_style = self._clean_style(self.styles["hr"])
        html = re.sub(r'^---+$', f'<hr style="{hr_style}">', html, flags=re.MULTILINE)
        html = re.sub(r'^\*\*\*+$', f'<hr style="{hr_style}">', html, flags=re.MULTILINE)
        return html
    
    def _convert_tags(self, html: str) -> str:
        """转换标签样式的关键词"""
        # 这个在行内代码转换后处理特殊的标签格式
        # 暂时保留原样，因为行内代码已经有样式了
        return html


def convert_markdown_to_wechat(markdown: str, custom_styles: Optional[dict] = None) -> str:
    """便捷函数：将 Markdown 转换为微信 HTML"""
    converter = WechatMDConverter(custom_styles)
    return converter.convert(markdown)
