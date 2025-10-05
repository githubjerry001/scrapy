# -*- coding: utf-8 -*-
"""
Main entry point for Banzhu Crawler
"""

import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_spider(spider_name):
    """Run a specific spider by name"""
    # Get settings
    settings = get_project_settings()
    
    # Update settings for this specific run
    settings.set('FEEDS', {
        f'data/{spider_name}_articles.json': {
            'format': 'json',
            'encoding': 'utf8',
            'store_empty': False,
            'indent': 2,
        },
    })
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Add spider to process
    process.crawl(spider_name)
    
    # Start crawling
    process.start()

if __name__ == '__main__':
    # Default spider name
    spider_name = 'banzhu_basic'
    
    # Check if a spider name was provided as a command line argument
    if len(sys.argv) > 1:
        spider_name = sys.argv[1]
    
    run_spider(spider_name)