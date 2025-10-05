# -*- coding: utf-8 -*-
"""
Banzhu Crawler Middlewares
"""

import random

class BanzhuSpiderMiddleware:
    """Banzhu Spider Middleware"""
    
    def process_spider_input(self, response, spider):
        """处理响应输入"""
        return None

    def process_spider_output(self, response, result, spider):
        """处理爬虫输出"""
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        """处理爬虫异常"""
        pass

    def process_start_requests(self, start_requests, spider):
        """处理起始请求"""
        for r in start_requests:
            yield r


class BanzhuDownloaderMiddleware:
    """Banzhu Downloader Middleware"""
    
    def process_request(self, request, spider):
        """处理请求"""
        return None

    def process_response(self, request, response, spider):
        """处理响应"""
        return response

    def process_exception(self, request, exception, spider):
        """处理异常"""
        pass

    def get_random_user_agent(self):
        """返回随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        return random.choice(user_agents)