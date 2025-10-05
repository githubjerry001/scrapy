import scrapy

class BanzhuSpider(scrapy.Spider):
    name = "banzhu"
    allowed_domains = ["www.banzhu6666666.com"]
    start_urls = ["https://www.banzhu6666666.com/"]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'COOKIES_ENABLED': True,
        'ROBOTSTXT_OBEY': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'FEEDS': {
            'articles.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 2,
            },
        },
    }

    def parse(self, response):
        # 由于网站返回403错误，我们在这里添加处理逻辑
        self.logger.info(f'访问 {response.url} 状态码: {response.status}')
        
        # 检查是否被阻止
        if response.status == 403:
            self.logger.warning("网站阻止了访问请求，可能需要更高级的反爬虫策略")
            return
            
        # 尝试提取页面信息
        title = response.css('title::text').get()
        self.logger.info(f'页面标题: {title}')
        
        # 保存页面内容以供分析
        with open('homepage.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        # 尝试提取链接
        links = response.css('a::attr(href)').getall()
        self.logger.info(f'找到 {len(links)} 个链接')
        
        # 提取文章信息（使用通用选择器）
        articles = []
        # 尝试多种选择器来提取内容
        content_selectors = [
            'article',
            '.content',
            '.post',
            '.entry',
            'div'
        ]
        
        for selector in content_selectors:
            elements = response.css(selector)
            if elements:
                for element in elements[:5]:  # 限制数量
                    title = element.css('h1::text, h2::text, h3::text, .title::text').get()
                    content = element.css('p::text, .text::text, .content::text').getall()
                    
                    if title or content:
                        yield {
                            'url': response.url,
                            'title': title,
                            'content': content[:100] if content else [],
                            'status': response.status
                        }
                break
                
        # 如果没有找到内容，返回基本信息
        if not articles:
            yield {
                'url': response.url,
                'title': title,
                'content': [f"页面状态: {response.status}", f"链接数量: {len(links)}"],
                'status': response.status
            }