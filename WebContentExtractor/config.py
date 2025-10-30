# -*- coding: utf-8 -*-
"""
提取配置类
定义网页提取的各种配置参数
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ExtractionConfig:
    """网页内容提取配置"""
    
    # 基本配置
    base_url: str = ""  # 网站基础URL，如 https://example.com
    output_dir: str = "extracted_articles"  # 输出目录
    
    # 选择器配置
    main_content_selector: str = "main"  # 主内容区域选择器（CSS或标签名）
    title_selector: str = "h1"  # 标题选择器
    
    # 跳过的元素
    skip_selectors: List[str] = field(default_factory=lambda: ['nav', 'aside', 'footer'])
    
    # 图片配置
    download_images: bool = True  # 是否下载图片
    image_skip_keywords: List[str] = field(default_factory=lambda: ['icon', 'avatar', 'logo'])
    images_folder_name: str = "imgs"  # 图片文件夹名称（默认使用imgs）
    
    # 格式配置
    preserve_bold: bool = True  # 保留粗体
    preserve_italic: bool = True  # 保留斜体
    preserve_code: bool = True  # 保留代码格式
    preserve_links: bool = True  # 保留链接
    
    # 请求配置
    timeout: int = 30  # 请求超时时间（秒）
    delay: float = 1.0  # 请求间隔（秒）
    headers: Dict[str, str] = field(default_factory=lambda: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # 文件配置
    file_encoding: str = 'utf-8'  # 文件编码
    create_index: bool = True  # 是否创建索引文件
    
    # 调试配置
    verbose: bool = True  # 是否输出详细信息
    save_failed_urls: bool = True  # 是否保存失败的URL列表


# 预设配置模板
class ConfigTemplates:
    """常用网站的预设配置模板"""
    
    @staticmethod
    def golangstar():
        """golangstar.cn 配置"""
        return ExtractionConfig(
            base_url="https://golangstar.cn",
            main_content_selector="main",
            title_selector="h1",
            skip_selectors=['nav', 'aside', 'footer', '.VPDocFooter', '.VPSidebar'],
            image_skip_keywords=['icon', 'avatar'],
        )
    
    @staticmethod
    def generic_blog():
        """通用博客配置"""
        return ExtractionConfig(
            base_url="",
            main_content_selector="article",
            title_selector="h1",
            skip_selectors=['nav', 'aside', 'footer', 'header'],
        )
    
    @staticmethod
    def juejin():
        """掘金配置示例"""
        return ExtractionConfig(
            base_url="https://juejin.cn",
            main_content_selector="article",
            title_selector="h1.article-title",
            skip_selectors=['nav', 'aside', 'footer', '.author-info'],
        )
    
    @staticmethod
    def aliyun_developer():
        """阿里云开发者社区配置"""
        return ExtractionConfig(
            base_url="https://developer.aliyun.com",
            main_content_selector=".article-content",
            title_selector="h1",
            skip_selectors=['nav', 'aside', 'footer', 'header', '.comment', '.related', '.author-info'],
            image_skip_keywords=['icon', 'avatar', 'logo', 'qrcode'],
        )
