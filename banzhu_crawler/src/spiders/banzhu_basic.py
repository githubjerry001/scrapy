from .base_banzhu_spider import BaseBanzhuSpider
import scrapy

class BanzhuBasicSpider(BaseBanzhuSpider):
    name = 'banzhu_basic'
    
    # 自定义设置，添加请求头来模拟浏览器
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 3,  # 设置下载延迟
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # 随机化下载延迟
    }

    def parse(self, response):
        # 使用基类方法记录页面信息
        title, links = self.log_page_info(response)
        
        # 保存页面内容以便分析
        self.save_page_content(response, 'banzhu_homepage.html')
        
        # 如果有分页链接，可以跟进
        for link in links[:5]:  # 只跟进前5个链接作为测试
            if link.startswith('http'):
                yield scrapy.Request(url=link, callback=self.parse_article)
            elif link.startswith('/'):
                yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        self.logger.info(f'Visited article page: {response.url}')
        self.logger.info(f'Response status: {response.status}')
        
        # 保存文章页面内容
        filename = response.url.split('/')[-1] or 'article_page.html'
        self.save_page_content(response, f'article_{filename}')
            
        # 尝试提取文章标题和内容
        title = self.extract_title(response)
        content = response.css('body::text').getall()
        
        yield {
            'url': response.url,
            'title': title,
            'content_preview': content[:100] if content else None,
        }