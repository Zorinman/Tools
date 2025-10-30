# -*- coding: utf-8 -*-
"""
使用示例
演示如何使用WebContentExtractor提取不同网站的内容
"""

from WebContentExtractor import WebContentExtractor, ExtractionConfig, ConfigTemplates


def example_1_golangstar():
    """示例1: 提取golangstar.cn的文章"""
    print("示例1: 提取golangstar.cn文章")
    print("="*60)
    
    # 使用预设配置
    config = ConfigTemplates.golangstar()
    config.output_dir = "golangstar_articles"
    config.download_images = True
    
    # 文章列表
    articles = [
        {
            "title": "如何设计一个十亿级的URL短链系统",
            "url": "https://golangstar.cn/backend_series/advanced_interview/tinyurl.html"
        },
        {
            "title": "如何设计一个百万QPS的限流器",
            "url": "https://golangstar.cn/backend_series/advanced_interview/rate_limiter.html"
        },
    ]
    
    # 创建提取器并提取
    extractor = WebContentExtractor(config)
    results = extractor.extract_articles(articles)
    
    print(f"\n结果: {results}")


def example_2_custom_config():
    """示例2: 使用自定义配置"""
    print("\n示例2: 使用自定义配置")
    print("="*60)
    
    # 自定义配置
    config = ExtractionConfig(
        base_url="https://example.com",
        output_dir="custom_articles",
        main_content_selector="article",  # 使用CSS选择器
        title_selector="h1.post-title",
        skip_selectors=['nav', '.sidebar', '#comments'],
        download_images=True,
        image_skip_keywords=['icon', 'avatar', 'ads'],
        timeout=30,
        delay=2.0,  # 慢速爬取
    )
    
    articles = [
        {"title": "文章标题", "url": "https://example.com/post/1"},
    ]
    
    extractor = WebContentExtractor(config)
    # results = extractor.extract_articles(articles)


def example_3_batch_from_file():
    """示例3: 从文件读取文章列表"""
    print("\n示例3: 从JSON文件读取文章列表")
    print("="*60)
    
    import json
    
    # 假设有一个articles.json文件
    # 格式: [{"title": "标题", "url": "URL"}, ...]
    
    config = ConfigTemplates.generic_blog()
    config.output_dir = "batch_articles"
    
    # 读取文章列表
    with open('articles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    extractor = WebContentExtractor(config)
    # results = extractor.extract_articles(articles)


def example_4_no_image_download():
    """示例4: 只提取内容，不下载图片"""
    print("\n示例4: 只提取文本内容")
    print("="*60)
    
    config = ExtractionConfig(
        base_url="https://blog.example.com",
        output_dir="text_only_articles",
        download_images=False,  # 不下载图片
        main_content_selector=".post-content",
    )
    
    articles = [
        {"title": "示例文章", "url": "https://blog.example.com/post/1"},
    ]
    
    extractor = WebContentExtractor(config)
    # results = extractor.extract_articles(articles)


def example_5_single_article():
    """示例5: 提取单篇文章"""
    print("\n示例5: 提取单篇文章")
    print("="*60)
    
    config = ConfigTemplates.golangstar()
    config.output_dir = "single_article"
    
    # 只提取一篇
    articles = [
        {
            "title": "Go程序数据库连接池耗尽如何排查",
            "url": "https://golangstar.cn/backend_series/advanced_interview/go_connection_pool.html"
        }
    ]
    
    extractor = WebContentExtractor(config)
    results = extractor.extract_articles(articles)


if __name__ == '__main__':
    # 运行示例1
    example_1_golangstar()
    
    # 取消注释运行其他示例
    # example_2_custom_config()
    # example_3_batch_from_file()
    # example_4_no_image_download()
    # example_5_single_article()
