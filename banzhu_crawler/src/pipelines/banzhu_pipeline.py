# -*- coding: utf-8 -*-
"""
Banzhu Crawler Pipelines
"""

import json
import os

class BanzhuPipeline:
    """Banzhu Pipeline for processing items"""
    
    def open_spider(self, spider):
        """爬虫启动时调用"""
        # 确保数据目录存在
        data_dir = 'data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 打开输出文件
        self.file = open(f'data/{spider.name}_items.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True

    def close_spider(self, spider):
        """爬虫关闭时调用"""
        # 关闭输出文件
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        """处理每个item"""
        # 添加逗号分隔符（除了第一个item）
        if not self.first_item:
            self.file.write(',\n')
        else:
            self.first_item = False
        
        # 写入item数据
        line = json.dumps(dict(item), ensure_ascii=False, indent=2)
        self.file.write(line)
        
        # 刷新文件缓冲区
        self.file.flush()
        
        return item