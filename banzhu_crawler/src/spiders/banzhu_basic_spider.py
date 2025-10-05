import scrapy

class BanzhuBasicSpider(scrapy.Spider):
    name = 'banzhu_basic'
    allowed_domains = ['banzhu6666666.com']
    start_urls = ['https://www.banzhu6666666.com/']

    # 自定义设置，添加请求头来模拟浏览器
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 3,  # 设置下载延迟
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # 随机化下载延迟
    }

    def parse(self, response):
        self.logger.info(f'Visited {response.url}')
        self.logger.info(f'Response status: {response.status}')
        
        # 保存页面内容以便分析
        with open('banzhu_homepage.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # 尝试提取一些基本元素
        title = response.css('title::text').get()
        self.logger.info(f'Page title: {title}')
        
        # 提取所有链接
        links = response.css('a::attr(href)').getall()
        self.logger.info(f'Found {len(links)} links')
        
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
        with open(f'article_{filename}', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        # 尝试提取文章标题和内容
        title = response.css('title::text').get()
        content = response.css('body::text').getall()
        
        yield {
            'url': response.url,
            'title': title,
            'content_preview': content[:100] if content else None,
        }