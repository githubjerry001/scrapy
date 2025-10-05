from .base_banzhu_spider import BaseBanzhuSpider
import scrapy

class BanzhuSpider(BaseBanzhuSpider):
    name = "banzhu"
    
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
        # 使用基类方法检查反爬虫机制
        if self.handle_antispider(response):
            return
            
        # 使用基类方法记录页面信息
        title, links = self.log_page_info(response)
        
        # 保存页面内容以供分析
        self.save_page_content(response, 'homepage.html')
        
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