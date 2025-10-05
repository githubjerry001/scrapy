from .base_banzhu_spider import BaseBanzhuSpider
import scrapy
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import random

class BanzhuAdvancedSpider(BaseBanzhuSpider):
    name = 'banzhu_advanced'
    
    # 更详细的自定义设置
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 5,  # 增加延迟
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'COOKIES_ENABLED': True,  # 启用cookies
        'ROBOTSTXT_OBEY': False,  # 不遵守robots.txt
        
        # 增加请求头
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        
        # 重试设置
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 403, 404, 408],
        
        # 下载超时
        'DOWNLOAD_TIMEOUT': 30,
        
        # 并发设置
        'CONCURRENT_REQUESTS': 1,  # 降低并发请求数
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }

    def start_requests(self):
        """重写start_requests方法以更好地控制初始请求"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        """解析主页"""
        # 使用基类方法检查反爬虫机制
        if self.handle_antispider(response):
            return
            
        # 使用基类方法记录页面信息
        title, links = self.log_page_info(response)
        
        # 保存页面内容以便分析
        self.save_page_content(response, 'banzhu_advanced_homepage.html')
        
        # 尝试提取文章链接
        # 由于我们无法直接查看网站结构，我们将尝试常见的选择器
        article_links = response.css('a::attr(href)').re(r'.*/\d+\.html')  # 匹配可能的文章链接
        if not article_links:
            # 尝试其他可能的选择器
            article_links = links
            
        self.logger.info(f'Found {len(article_links)} potential article links')
        
        # 跟进前几个链接进行测试
        for link in article_links[:3]:
            if link.startswith('http'):
                yield scrapy.Request(url=link, callback=self.parse_article)
            elif link.startswith('/'):
                yield response.follow(link, self.parse_article)
            else:
                # 相对链接
                yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        """解析文章页面"""
        # 使用基类方法检查反爬虫机制
        if self.handle_antispider(response):
            return
            
        # 保存文章页面内容
        filename = response.url.split('/')[-1] or 'article_page.html'
        self.save_page_content(response, f'advanced_article_{filename}')
            
        # 尝试提取文章信息（使用通用选择器）
        title = self.extract_title(response) or response.css('h1::text').get()
        
        # 尝试提取文章内容（多种可能的选择器）
        content_selectors = [
            'article p::text',
            '.content p::text',
            '.post-content p::text',
            '.article-content p::text',
            'p::text',
            'div p::text'
        ]
        
        content = []
        for selector in content_selectors:
            content = response.css(selector).getall()
            if content:
                break
                
        # 如果还找不到内容，尝试获取所有文本
        if not content:
            content = response.css('body::text').getall()
            
        yield {
            'url': response.url,
            'title': title,
            'content_preview': content[:100] if content else None,
            'status': response.status,
        }

# 自定义重试中间件
class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
            
        # 如果是403状态码，尝试更换User-Agent
        if response.status in [403]:
            reason = response_status_message(response.status)
            # 更换User-Agent
            new_headers = request.headers.copy()
            new_headers['User-Agent'] = self.get_random_user_agent()
            new_request = request.replace(headers=new_headers)
            return self._retry(new_request, reason, spider) or response
            
        return super().process_response(request, response, spider)
        
    def get_random_user_agent(self):
        """返回随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        return random.choice(user_agents)