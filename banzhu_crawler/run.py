#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Banzhu小说爬虫系统主入口
=======================

这是一个专业的Web爬虫系统，专门用于从Banzhu网站抓取小说内容。
本系统基于Scrapy框架开发，具有强大的反爬虫机制和数据处理能力。

作者: Qoder AI Assistant
版本: 1.0.0
"""

import os
import sys
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def run_spider(spider_name):
    """运行指定的爬虫"""
    try:
        # 获取设置
        settings = get_project_settings()
        
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        
        # 添加爬虫到进程
        process.crawl(spider_name)
        
        # 启动爬虫
        process.start()
        
        print(f"爬虫 {spider_name} 运行完成")
        return True
    except Exception as e:
        print(f"运行爬虫 {spider_name} 时出错: {e}")
        return False

def run_web_app():
    """运行Web应用程序"""
    try:
        # 添加src/web到Python路径
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'web'))
        
        # 导入并运行Web应用
        from src.web.banzhu_web import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
        print("Web应用程序已启动，访问 http://127.0.0.1:5000")
        return True
    except Exception as e:
        print(f"运行Web应用程序时出错: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Banzhu小说爬虫系统')
    parser.add_argument('--spider', choices=['banzhu_basic', 'banzhu_advanced'], 
                        help='要运行的爬虫名称')
    parser.add_argument('--web', action='store_true', 
                        help='启动Web控制界面')
    parser.add_argument('--list-spiders', action='store_true', 
                        help='列出所有可用的爬虫')
    
    args = parser.parse_args()
    
    # 如果没有提供参数，显示帮助信息
    if not any([args.spider, args.web, args.list_spiders]):
        parser.print_help()
        return
    
    # 列出所有爬虫
    if args.list_spiders:
        print("可用的爬虫:")
        print("  banzhu_basic    - 基础爬虫")
        print("  banzhu_advanced - 高级爬虫")
        return
    
    # 运行指定的爬虫
    if args.spider:
        success = run_spider(args.spider)
        sys.exit(0 if success else 1)
    
    # 启动Web应用
    if args.web:
        success = run_web_app()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()