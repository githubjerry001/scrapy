import scrapy

class BaseBanzhuSpider(scrapy.Spider):
    """Banzhu爬虫的基类，包含通用功能"""
    
    allowed_domains = ['banzhu6666666.com']
    start_urls = ['https://www.banzhu6666666.com/']
    
    def save_page_content(self, response, filename):
        """保存页面内容到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
    
    def extract_title(self, response):
        """提取页面标题"""
        return response.css('title::text').get()
    
    def extract_links(self, response):
        """提取页面链接"""
        return response.css('a::attr(href)').getall()
    
    def log_page_info(self, response):
        """记录页面基本信息"""
        self.logger.info(f'Visited {response.url}')
        self.logger.info(f'Response status: {response.status}')
        
        title = self.extract_title(response)
        self.logger.info(f'Page title: {title}')
        
        links = self.extract_links(response)
        self.logger.info(f'Found {len(links)} links')
        
        return title, links
    
    def handle_antispider(self, response):
        """处理反爬虫机制"""
        if response.status == 403 or "captcha" in response.text.lower() or "blocked" in response.text.lower():
            self.logger.warning("可能遇到了反爬虫机制")
            return True
        return False