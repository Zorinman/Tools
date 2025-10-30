# WebContentExtractor - 通用网页内容提取工具

一个强大的、可配置的网页内容提取工具，用于批量提取网页文章并保存为Markdown格式，支持自动下载图片。

## ✨ 特性

- 🚀 **批量提取** - 支持批量提取多篇文章
- 📝 **格式保留** - 完整保留粗体、斜体、代码、链接等格式
- 🖼️ **图片下载** - 自动下载文章图片并更新引用
- ⚙️ **高度可配置** - 灵活的配置系统，适应不同网站
- 📦 **预设模板** - 内置常用网站的配置模板
- 🔍 **CSS选择器** - 支持CSS选择器和标签名选择
- 📊 **索引生成** - 自动生成文章索引
- 🛡️ **错误处理** - 完善的错误处理和失败记录

## 📦 安装依赖

```bash
pip install requests beautifulsoup4
```

## 🚀 快速开始

> 💡 **新用户推荐**: 查看 [单篇文章提取指南.md](./单篇文章提取指南.md) 获取更简单的入门教程  
> 🧹 **任务完成后**: 查看 [清理说明.md](./清理说明.md) 了解如何清理临时文件

### 提取单篇文章（最简单）

```python
from WebContentExtractor import WebContentExtractor, ConfigTemplates

# 1. 选择预设配置
config = ConfigTemplates.aliyun_developer()  # 阿里云开发者社区
config.output_dir = "我的文章"

# 2. 提取文章
extractor = WebContentExtractor(config)
results = extractor.extract_articles([
    {
        "title": "Kubernetes架构详解",
        "url": "https://developer.aliyun.com/article/1635071"
    }
])

print(f"成功: {results['success_count']} 篇")
```

**输出结构**:
```
我的文章/
└── Kubernetes架构详解/
    ├── Kubernetes架构详解.md
    └── imgs/
        ├── image_1.png
        └── ...
```

### 批量提取多篇文章

```python
from WebContentExtractor import WebContentExtractor, ConfigTemplates

# 1. 使用预设配置
config = ConfigTemplates.golangstar()
config.output_dir = "我的文章"

# 2. 准备文章列表
articles = [
    {
        "title": "文章标题1",
        "url": "https://example.com/article1.html"
    },
    {
        "title": "文章标题2", 
        "url": "https://example.com/article2.html"
    }
]

# 3. 创建提取器并执行
extractor = WebContentExtractor(config)
results = extractor.extract_articles(articles)

print(f"成功: {results['success_count']} 篇")
print(f"失败: {results['fail_count']} 篇")
```

### 自定义配置

```python
from WebContentExtractor import WebContentExtractor, ExtractionConfig

# 创建自定义配置
config = ExtractionConfig(
    base_url="https://myblog.com",           # 网站基础URL
    output_dir="extracted_articles",          # 输出目录
    main_content_selector="article.post",     # 主内容选择器
    title_selector="h1.title",                # 标题选择器
    skip_selectors=['nav', '.sidebar'],       # 要跳过的元素
    download_images=True,                     # 下载图片
    image_skip_keywords=['icon', 'logo'],     # 跳过的图片关键词
    timeout=30,                               # 请求超时
    delay=1.0,                                # 请求间隔(秒)
)

extractor = WebContentExtractor(config)
```

## 📚 详细配置说明

### ExtractionConfig 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | str | "" | 网站基础URL，用于处理相对路径 |
| `output_dir` | str | "extracted_articles" | 输出目录路径 |
| `main_content_selector` | str | "main" | 主内容区域的CSS选择器或标签名 |
| `title_selector` | str | "h1" | 标题选择器 |
| `skip_selectors` | List[str] | ['nav', 'aside', 'footer'] | 要跳过的元素选择器列表 |
| `download_images` | bool | True | 是否下载图片 |
| `image_skip_keywords` | List[str] | ['icon', 'avatar', 'logo'] | 跳过包含这些关键词的图片 |
| `images_folder_name` | str | "images" | 图片文件夹名称 |
| `preserve_bold` | bool | True | 保留粗体格式 |
| `preserve_italic` | bool | True | 保留斜体格式 |
| `preserve_code` | bool | True | 保留代码格式 |
| `preserve_links` | bool | True | 保留链接 |
| `timeout` | int | 30 | HTTP请求超时时间(秒) |
| `delay` | float | 1.0 | 请求间隔时间(秒) |
| `headers` | Dict | 默认User-Agent | HTTP请求头 |
| `file_encoding` | str | 'utf-8' | 文件编码 |
| `create_index` | bool | True | 是否创建索引文件 |
| `verbose` | bool | True | 是否输出详细信息 |
| `save_failed_urls` | bool | True | 是否保存失败的URL列表 |

## 🎯 使用场景

### 场景1: 提取技术博客文章

```python
config = ExtractionConfig(
    base_url="https://techblog.com",
    main_content_selector="article.post-content",
    title_selector="h1.post-title",
    download_images=True,
)
```

### 场景2: 只提取纯文本（不下载图片）

```python
config = ExtractionConfig(
    download_images=False,  # 关闭图片下载
    main_content_selector=".content",
)
```

### 场景3: 从JSON文件批量提取

```python
import json

# articles.json 格式:
# [
#   {"title": "文章1", "url": "https://..."},
#   {"title": "文章2", "url": "https://..."}
# ]

with open('articles.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

config = ExtractionConfig(base_url="https://example.com")
extractor = WebContentExtractor(config)
results = extractor.extract_articles(articles)
```

### 场景4: 慢速爬取（避免被封）

```python
config = ExtractionConfig(
    delay=3.0,  # 每次请求间隔3秒
    timeout=60,  # 超时时间60秒
    headers={
        'User-Agent': 'Mozilla/5.0 ...',
        'Referer': 'https://example.com',
    }
)
```

## 📁 输出结构

提取后的文件结构：

```
output_dir/
├── README.md                    # 自动生成的索引文件
├── failed_urls.json            # 失败的URL列表（如有）
├── 文章1/
│   ├── 文章1.md
│   └── imgs/                   # 图片文件夹（默认名称为imgs）
│       ├── image_1.png
│       ├── image_2.png
│       └── ...
├── 文章2/
│   ├── 文章2.md
│   └── imgs/
│       └── ...
└── ...
```

> 💡 **提示**: 图片文件夹名称可通过 `config.images_folder_name` 自定义

## 🔧 预设配置模板

### 使用预设模板

```python
from WebContentExtractor import ConfigTemplates

# 阿里云开发者社区配置
config = ConfigTemplates.aliyun_developer()

# golangstar.cn 配置
config = ConfigTemplates.golangstar()

# 通用博客配置
config = ConfigTemplates.generic_blog()

# 掘金配置
config = ConfigTemplates.juejin()
```

### 支持的网站

| 网站 | 配置方法 | 域名 |
|------|---------|------|
| 阿里云开发者社区 | `ConfigTemplates.aliyun_developer()` | developer.aliyun.com |
| golangstar.cn | `ConfigTemplates.golangstar()` | golangstar.cn |
| 掘金 | `ConfigTemplates.juejin()` | juejin.cn |
| 通用博客 | `ConfigTemplates.generic_blog()` | 适用于大多数博客 |

### 添加自定义模板

在 `config.py` 的 `ConfigTemplates` 类中添加：

```python
@staticmethod
def my_blog():
    """我的博客配置"""
    return ExtractionConfig(
        base_url="https://myblog.com",
        main_content_selector="article",
        # ... 其他配置
    )
```

## 📋 完整示例

```python
from WebContentExtractor import WebContentExtractor, ExtractionConfig

# 1. 创建配置
config = ExtractionConfig(
    base_url="https://golangstar.cn",
    output_dir="后端面试场景题",
    main_content_selector="main",
    skip_selectors=['nav', 'aside', 'footer'],
    download_images=True,
    delay=1.0,
    verbose=True
)

# 2. 准备文章列表
articles = [
    {
        "title": "如何设计一个十亿级的URL短链系统",
        "url": "https://golangstar.cn/backend_series/advanced_interview/tinyurl.html"
    },
    {
        "title": "如何设计一个百万QPS的限流器",
        "url": "https://golangstar.cn/backend_series/advanced_interview/rate_limiter.html"
    },
    # ... 更多文章
]

# 3. 执行提取
extractor = WebContentExtractor(config)
results = extractor.extract_articles(articles)

# 4. 查看结果
print(f"提取完成!")
print(f"成功: {results['success_count']} 篇")
print(f"失败: {results['fail_count']} 篇")

if results['failed_urls']:
    print(f"失败的文章:")
    for item in results['failed_urls']:
        print(f"  - {item['title']}: {item['url']}")
```

## ⚠️ 注意事项

1. **遵守robots.txt** - 请遵守网站的爬虫协议
2. **控制频率** - 设置合理的 `delay` 避免对服务器造成压力
3. **选择器准确性** - 不同网站的HTML结构不同，需要调整选择器
4. **网络环境** - 确保网络连接稳定
5. **法律合规** - 仅用于个人学习，不要用于商业用途
6. **清理临时脚本** - 提取任务完成后，建议删除临时创建的提取脚本（如 `extract_xxx.py`），保持工作区整洁

## 🐛 故障排除

### 问题1: 找不到主内容区域

**解决方案**: 使用浏览器开发者工具检查网页结构，调整 `main_content_selector`

```python
# 尝试不同的选择器
config.main_content_selector = "article"  # 标签名
config.main_content_selector = ".content"  # class
config.main_content_selector = "#main-content"  # id
config.main_content_selector = "div.post-body"  # 组合选择器
```

### 问题2: 提取的内容格式不正确

**解决方案**: 检查 `skip_selectors`，确保跳过了不需要的元素

```python
config.skip_selectors = ['nav', 'aside', 'footer', '.comments', '.sidebar']
```

### 问题3: 图片下载失败

**解决方案**: 检查网络连接，或关闭图片下载

```python
config.download_images = False  # 暂时关闭图片下载
config.timeout = 60  # 增加超时时间
```

## 📝 更新日志

### v1.0.0 (2025-10-30)
- ✨ 初始版本发布
- ✅ 支持批量文章提取
- ✅ 支持图片自动下载
- ✅ 支持多种格式保留
- ✅ 内置预设配置模板

## 📄 License

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 💡 使用提示

1. **首次使用**: 建议先用1-2篇文章测试配置是否正确
2. **调试模式**: 设置 `verbose=True` 查看详细输出
3. **备份数据**: 重要数据请做好备份
4. **性能优化**: 大批量提取时可以关闭图片下载，提高速度
5. **任务完成后**: 删除临时提取脚本和 `__pycache__` 目录，仅保留提取的文章内容

---

**享受使用! 如有问题请提Issue.**
