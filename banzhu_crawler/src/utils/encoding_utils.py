# -*- coding: utf-8 -*-
"""
Encoding utilities for Banzhu Crawler
"""

import chardet

def detect_encoding(content):
    """检测内容编码"""
    try:
        detected = chardet.detect(content)
        return detected['encoding']
    except Exception as e:
        print(f"Error detecting encoding: {e}")
        return 'utf-8'

def convert_to_utf8(content, source_encoding=None):
    """将内容转换为UTF-8编码"""
    if source_encoding:
        try:
            return content.decode(source_encoding).encode('utf-8')
        except Exception as e:
            print(f"Error converting from {source_encoding}: {e}")
    
    # 如果没有指定源编码或转换失败，尝试自动检测
    try:
        encoding = detect_encoding(content)
        if encoding:
            return content.decode(encoding).encode('utf-8')
    except Exception as e:
        print(f"Error converting to UTF-8: {e}")
    
    # 最后的备选方案
    try:
        return content.decode('utf-8', errors='ignore').encode('utf-8')
    except Exception as e:
        print(f"Error in fallback conversion: {e}")
        return content