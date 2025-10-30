# -*- coding: utf-8 -*-
"""
通用网页内容提取工具
用于批量提取网页文章并保存为Markdown格式，同时下载图片
"""

from .extractor import WebContentExtractor
from .config import ExtractionConfig, ConfigTemplates

__version__ = '1.0.0'
__all__ = ['WebContentExtractor', 'ExtractionConfig', 'ConfigTemplates']
