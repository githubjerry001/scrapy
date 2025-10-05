# Banzhu小说爬虫系统

这是一个专业的Web爬虫系统，专门用于从Banzhu网站抓取小说内容。本系统基于Scrapy框架开发，具有强大的反爬虫机制和数据处理能力。

## 目录结构

```
banzhu_crawler/
├── README.md                   # 项目说明文档
├── start.bat                   # Windows启动脚本
├── start.ps1                   # PowerShell启动脚本
├── quick_start.bat             # 快速启动脚本
├── scrapy.cfg                  # Scrapy配置文件
├── data/                       # 爬取数据存储目录
├── templates/                  # Web界面模板
└── src/                        # 源代码目录
    ├── __init__.py
    ├── main.py                 # 主入口程序
    ├── config/                 # 配置文件
    │   ├── __init__.py
    │   └── settings.py         # Scrapy设置
    ├── spiders/                # 爬虫实现
    │   ├── __init__.py
    │   ├── banzhu_basic_spider.py
    │   └── banzhu_advanced_spider.py
    ├── middlewares/            # 中间件
    │   ├── __init__.py
    │   └── banzhu_middleware.py
    ├── pipelines/              # 数据管道
    │   ├── __init__.py
    │   └── banzhu_pipeline.py
    ├── utils/                  # 工具函数
    │   ├── __init__.py
    │   └── encoding_utils.py
    └── web/                    # Web控制界面
        ├── __init__.py
        ├── app.py              # 增强版Web应用
        └── simple_app.py       # 简易版Web应用
```

## 功能特点

1. **多爬虫支持**：
   - 基础爬虫：简单的页面抓取实现
   - 高级爬虫：具备更强的反爬虫机制和数据提取能力

2. **反爬虫策略**：
   - User-Agent伪装
   - 请求延迟和随机化
   - Cookie支持
   - 请求头模拟
   - 自定义重试机制

3. **Web控制界面**：
   - 通过浏览器控制爬虫的启动和停止
   - 实时状态监控和输出显示
   - 友好的结果展示界面

4. **数据处理**：
   - 自动保存为JSON格式
   - 支持多种数据导出方式
   - 编码自动检测和处理

## 安装依赖

```bash
pip install scrapy flask requests beautifulsoup4 chardet
```

## 使用方法

### 命令行方式

```bash
# 进入banzhu_crawler目录
cd banzhu_crawler

# 运行基础爬虫
python -m scrapy crawl banzhu_basic

# 运行高级爬虫
python -m scrapy crawl banzhu_advanced
```

### Web界面方式

```bash
# 启动Web控制系统
python src/web/app.py

# 访问 http://127.0.0.1:5000 使用Web界面
```

### 脚本方式

```bash
# Windows批处理脚本
start.bat

# PowerShell脚本
start.ps1

# 快速启动脚本
quick_start.bat
```

## 配置说明

在[settings.py](file:///c%3A/Users/Jerry/Downloads/GitHub/scrapy/banzhu_crawler/src/config/settings.py)中可以修改以下设置：

- 请求延迟：`DOWNLOAD_DELAY`
- 并发请求数：`CONCURRENT_REQUESTS`
- User-Agent：`USER_AGENT`
- 请求头：`DEFAULT_REQUEST_HEADERS`

## 注意事项

1. **网站限制**：目标网站可能有反爬虫机制，可能需要进一步调整策略
2. **访问频率**：已设置延迟以避免对网站造成过大压力
3. **法律合规**：请确保遵守网站的使用条款和相关法律法规
4. **数据使用**：抓取的数据仅用于学习和研究目的

## 扩展功能

### 添加新爬虫

```bash
cd banzhu_crawler
python -m scrapy genspider spider_name website.com
```

### 数据存储

可以在[settings.py](file:///c%3A/Users/Jerry/Downloads/GitHub/scrapy/banzhu_crawler/src/config/settings.py)中修改`FEEDS`配置来改变数据存储方式。