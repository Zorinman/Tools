# -*- coding: utf-8 -*-
"""
核心提取器类
实现网页内容提取的主要逻辑
"""

import os
import time
import json
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Tuple
from .config import ExtractionConfig


class WebContentExtractor:
    """通用网页内容提取器"""
    
    def __init__(self, config: ExtractionConfig):
        """
        初始化提取器
        
        Args:
            config: 提取配置对象
        """
        self.config = config
        self.failed_urls = []
        self.success_count = 0
        self.fail_count = 0
    
    def extract_articles(self, article_list: List[Dict[str, str]]) -> Dict:
        """
        批量提取文章
        
        Args:
            article_list: 文章列表，格式: [{"title": "标题", "url": "URL"}, ...]
        
        Returns:
            提取结果统计
        """
        # 创建输出目录
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        self._log(f"开始提取 {len(article_list)} 篇文章...")
        self._log("="*60)
        
        for i, article in enumerate(article_list, 1):
            title = article.get('title', f'Article_{i}')
            url = article.get('url', '')
            
            if not url:
                self._log(f"[{i}/{len(article_list)}] 跳过: {title} (无URL)")
                self.fail_count += 1
                continue
            
            self._log(f"\n[{i}/{len(article_list)}] 处理: {title}")
            
            # 提取文章内容
            success = self._extract_single_article(url, title)
            
            if success:
                self.success_count += 1
            else:
                self.fail_count += 1
                self.failed_urls.append({"title": title, "url": url})
            
            # 延迟，避免请求过快
            if i < len(article_list):
                time.sleep(self.config.delay)
        
        # 保存结果
        results = self._save_results()
        
        self._log("\n" + "="*60)
        self._log(f"提取完成!")
        self._log(f"成功: {self.success_count} 篇")
        self._log(f"失败: {self.fail_count} 篇")
        self._log("="*60)
        
        return results
    
    def _extract_single_article(self, url: str, title: str) -> bool:
        """
        提取单篇文章
        
        Args:
            url: 文章URL
            title: 文章标题
        
        Returns:
            是否成功
        """
        try:
            # 获取网页内容
            response = requests.get(
                url, 
                timeout=self.config.timeout,
                headers=self.config.headers
            )
            response.encoding = self.config.file_encoding
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取主内容
            main_content = soup.select_one(self.config.main_content_selector)
            if not main_content:
                main_content = soup.find(self.config.main_content_selector)
            
            if not main_content:
                self._log(f"  ✗ 未找到主内容区域 (选择器: {self.config.main_content_selector})")
                return False
            
            # 生成Markdown内容
            markdown = self._generate_markdown(main_content, title, url)
            
            # 创建文章文件夹
            article_folder = os.path.join(self.config.output_dir, self._sanitize_filename(title))
            os.makedirs(article_folder, exist_ok=True)
            
            # 保存Markdown文件
            md_file = os.path.join(article_folder, f"{self._sanitize_filename(title)}.md")
            with open(md_file, 'w', encoding=self.config.file_encoding) as f:
                f.write(markdown)
            
            self._log(f"  ✓ 已保存: {md_file}")
            
            # 下载图片（如果配置启用）
            if self.config.download_images:
                self._download_images(main_content, article_folder, title)
            
            return True
            
        except Exception as e:
            self._log(f"  ✗ 错误: {e}")
            if self.config.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _generate_markdown(self, content_element, title: str, url: str) -> str:
        """
        生成Markdown内容
        
        Args:
            content_element: 内容元素
            title: 标题
            url: 原文URL
        
        Returns:
            Markdown文本
        """
        markdown = f"# {title}\n\n"
        markdown += f"> 原文链接: [{url}]({url})\n\n"
        
        # 遍历所有内容元素
        processed_elements = set()  # 记录已处理的元素，避免重复
        for element in content_element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'img', 'blockquote', 'table']):
            # 跳过已处理的元素
            if id(element) in processed_elements:
                continue
            
            # 跳过指定的元素
            if self._should_skip_element(element):
                continue
            
            tag_name = element.name
            
            # 标记当前元素为已处理
            processed_elements.add(id(element))
            
            # 如果是容器元素（blockquote, ul, ol, pre, table），标记其所有子元素为已处理
            if tag_name in ['blockquote', 'ul', 'ol', 'pre', 'table']:
                for child in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'img', 'blockquote', 'table']):
                    processed_elements.add(id(child))
            
            # 处理标题
            if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(tag_name[1])
                text = self._process_text_with_format(element)
                markdown += f"\n{'#' * level} {text}\n\n"
            
            # 处理段落
            elif tag_name == 'p':
                text = self._process_text_with_format(element).strip()
                if text:
                    markdown += f"{text}\n\n"
            
            # 处理列表
            elif tag_name in ['ul', 'ol']:
                for li in element.find_all('li', recursive=False):
                    li_text = self._process_text_with_format(li).strip()
                    markdown += f"- {li_text}\n"
                markdown += '\n'
            
            # 处理代码块
            elif tag_name == 'pre':
                code = element.find('code')
                if code:
                    lang = self._extract_code_language(code)
                    markdown += f"```{lang}\n{code.get_text()}\n```\n\n"
            
            # 处理图片
            elif tag_name == 'img':
                img_md = self._process_image(element)
                if img_md:
                    markdown += f"{img_md}\n\n"
            
            # 处理引用
            elif tag_name == 'blockquote':
                text = self._process_text_with_format(element).strip()
                lines = text.split('\n')
                for line in lines:
                    if line.strip():
                        markdown += f"> {line.strip()}\n"
                markdown += '\n'
            
            # 处理表格
            elif tag_name == 'table':
                table_md = self._process_table(element)
                if table_md:
                    markdown += f"{table_md}\n\n"
        
        return markdown
    
    def _process_text_with_format(self, element) -> str:
        """
        处理文本，保留格式
        
        Args:
            element: HTML元素
        
        Returns:
            格式化的文本
        """
        result = ""
        
        for child in element.children:
            if isinstance(child, NavigableString):
                result += str(child)
            elif child.name in ['strong', 'b'] and self.config.preserve_bold:
                result += f"**{child.get_text()}**"
            elif child.name in ['em', 'i'] and self.config.preserve_italic:
                result += f"*{child.get_text()}*"
            elif child.name == 'code' and self.config.preserve_code:
                result += f"`{child.get_text()}`"
            elif child.name == 'a' and self.config.preserve_links:
                href = child.get('href', '')
                text = child.get_text()
                # 转换为绝对URL
                if href and not href.startswith(('http://', 'https://', '#')):
                    href = urljoin(self.config.base_url, href)
                result += f"[{text}]({href})"
            else:
                # 递归处理嵌套元素
                result += self._process_text_with_format(child)
        
        return result
    
    def _process_image(self, img_element) -> Optional[str]:
        """
        处理图片元素
        
        Args:
            img_element: 图片元素
        
        Returns:
            Markdown格式的图片
        """
        src = img_element.get('src', '')
        alt = img_element.get('alt', 'image')
        
        # 跳过特定关键词的图片
        if any(keyword in src.lower() for keyword in self.config.image_skip_keywords):
            return None
        
        if not src:
            return None
        
        # 转换为绝对URL
        if not src.startswith(('http://', 'https://')):
            src = urljoin(self.config.base_url, src)
        
        return f"![{alt}]({src})"
    
    def _process_table(self, table_element) -> str:
        """处理表格"""
        markdown = ""
        
        # 处理表头
        thead = table_element.find('thead')
        if thead:
            headers = [th.get_text().strip() for th in thead.find_all(['th', 'td'])]
            markdown += "| " + " | ".join(headers) + " |\n"
            markdown += "|" + "|".join(["---" for _ in headers]) + "|\n"
        
        # 处理表体
        tbody = table_element.find('tbody') or table_element
        for tr in tbody.find_all('tr'):
            cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
            if cells:
                markdown += "| " + " | ".join(cells) + " |\n"
        
        return markdown
    
    def _extract_code_language(self, code_element) -> str:
        """提取代码语言"""
        lang = ''
        if code_element.get('class'):
            for cls in code_element.get('class'):
                if cls.startswith('language-'):
                    lang = cls.replace('language-', '')
                    break
        return lang
    
    def _should_skip_element(self, element) -> bool:
        """判断是否应该跳过元素"""
        for selector in self.config.skip_selectors:
            if element.find_parent(selector) or element.select_one(selector):
                return True
        return False
    
    def _download_images(self, content_element, article_folder: str, title: str):
        """
        下载文章中的所有图片
        
        Args:
            content_element: 内容元素
            article_folder: 文章文件夹路径
            title: 文章标题
        """
        images = content_element.find_all('img')
        valid_images = []
        
        for img in images:
            src = img.get('src', '')
            if src and not any(kw in src.lower() for kw in self.config.image_skip_keywords):
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(self.config.base_url, src)
                valid_images.append(src)
        
        if not valid_images:
            return
        
        # 创建图片文件夹
        images_folder = os.path.join(article_folder, self.config.images_folder_name)
        os.makedirs(images_folder, exist_ok=True)
        
        self._log(f"  下载图片: {len(valid_images)} 张")
        
        for i, img_url in enumerate(valid_images, 1):
            try:
                response = requests.get(img_url, timeout=self.config.timeout)
                response.raise_for_status()
                
                # 生成文件名
                ext = os.path.splitext(urlparse(img_url).path)[1] or '.png'
                filename = f"image_{i}{ext}"
                filepath = os.path.join(images_folder, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # 更新Markdown中的图片引用
                self._update_image_reference(article_folder, title, img_url, filename)
                
            except Exception as e:
                if self.config.verbose:
                    self._log(f"    图片下载失败: {img_url} - {e}")
            
            time.sleep(0.3)  # 短暂延迟
    
    def _update_image_reference(self, article_folder: str, title: str, old_url: str, new_filename: str):
        """更新Markdown中的图片引用"""
        md_file = os.path.join(article_folder, f"{self._sanitize_filename(title)}.md")
        
        try:
            with open(md_file, 'r', encoding=self.config.file_encoding) as f:
                content = f.read()
            
            # 替换图片URL为本地路径
            new_path = f"./{self.config.images_folder_name}/{new_filename}"
            content = content.replace(f"]({old_url})", f"]({new_path})")
            
            with open(md_file, 'w', encoding=self.config.file_encoding) as f:
                f.write(content)
        except Exception as e:
            if self.config.verbose:
                self._log(f"    更新图片引用失败: {e}")
    
    def _save_results(self) -> Dict:
        """保存提取结果"""
        results = {
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "failed_urls": self.failed_urls
        }
        
        # 保存失败的URL列表
        if self.config.save_failed_urls and self.failed_urls:
            failed_file = os.path.join(self.config.output_dir, "failed_urls.json")
            with open(failed_file, 'w', encoding=self.config.file_encoding) as f:
                json.dump(self.failed_urls, f, ensure_ascii=False, indent=2)
            self._log(f"\n失败URL已保存: {failed_file}")
        
        # 创建索引文件
        if self.config.create_index:
            self._create_index()
        
        return results
    
    def _create_index(self):
        """创建文章索引"""
        index_file = os.path.join(self.config.output_dir, "README.md")
        
        folders = [f for f in os.listdir(self.config.output_dir) 
                  if os.path.isdir(os.path.join(self.config.output_dir, f))]
        
        content = f"# 提取的文章索引\n\n"
        content += f"总计: {len(folders)} 篇文章\n\n"
        content += f"## 文章列表\n\n"
        
        for i, folder in enumerate(sorted(folders), 1):
            md_files = [f for f in os.listdir(os.path.join(self.config.output_dir, folder))
                       if f.endswith('.md')]
            if md_files:
                content += f"{i}. [{folder}](./{folder}/{md_files[0]})\n"
        
        with open(index_file, 'w', encoding=self.config.file_encoding) as f:
            f.write(content)
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        import re
        # 移除Windows不允许的字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 限制长度
        if len(filename) > 200:
            filename = filename[:200]
        return filename.strip()
    
    def _log(self, message: str):
        """输出日志"""
        if self.config.verbose:
            print(message)
