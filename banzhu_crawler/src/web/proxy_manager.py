import requests
import json
import time
import threading
from datetime import datetime, timedelta
import random

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.last_update = None
        self.update_interval = 3600  # 1小时更新一次
        self.test_url = "https://www.banzhu6666666.com/"
        self.lock = threading.Lock()
        
    def fetch_free_proxies(self):
        """从免费代理网站获取代理列表"""
        new_proxies = []
        
        # 方法1: 从API获取免费代理
        try:
            response = requests.get("https://www.proxy-list.download/api/v1/get?type=http", timeout=5)
            if response.status_code == 200:
                proxies_data = response.text.strip().split('\n')
                for proxy in proxies_data:
                    if proxy:
                        new_proxies.append({
                            'http': f'http://{proxy}',
                            'https': f'http://{proxy}'
                        })
        except Exception as e:
            print(f"获取代理API失败: {e}")
        
        # 方法2: 从ProxyScrape获取免费代理
        try:
            response = requests.get("https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=5000&country=all&ssl=all&anonymity=all", timeout=5)
            if response.status_code == 200:
                proxies_data = response.text.strip().split('\n')
                for proxy in proxies_data:
                    if proxy:
                        proxy = proxy.strip()
                        new_proxies.append({
                            'http': f'http://{proxy}',
                            'https': f'http://{proxy}'
                        })
        except Exception as e:
            print(f"获取ProxyScrape代理失败: {e}")
        
        # 方法3: 从其他源获取免费代理
        try:
            response = requests.get("https://www.proxy-list.download/api/v1/get?type=https", timeout=5)
            if response.status_code == 200:
                proxies_data = response.text.strip().split('\n')
                for proxy in proxies_data:
                    if proxy:
                        new_proxies.append({
                            'http': f'https://{proxy}',
                            'https': f'https://{proxy}'
                        })
        except Exception as e:
            print(f"获取HTTPS代理API失败: {e}")
        
        return new_proxies
    
    def validate_proxy(self, proxy):
        """验证代理是否有效"""
        try:
            # 使用移动设备User-Agent来测试代理
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
            }
            
            response = requests.get(
                self.test_url, 
                proxies=proxy, 
                headers=headers, 
                timeout=10
            )
            
            # 检查响应状态和内容
            if response.status_code == 200:
                # 检查是否是封禁页面
                content = response.text.lower()
                if "access denied" not in content and "ray id" not in content and "cloudflare" not in content:
                    return True
        except Exception as e:
            pass
        
        return False
    
    def filter_working_proxies(self, proxies_list):
        """过滤出有效的代理"""
        working_proxies = []
        
        for proxy in proxies_list:
            if self.validate_proxy(proxy):
                working_proxies.append(proxy)
                print(f"代理有效: {proxy}")
            else:
                print(f"代理无效: {proxy}")
        
        return working_proxies
    
    def update_proxy_list(self):
        """更新代理列表"""
        with self.lock:
            print("开始更新代理列表...")
            
            # 获取新的代理列表
            new_proxies = self.fetch_free_proxies()
            print(f"获取到 {len(new_proxies)} 个代理")
            
            # 验证代理有效性
            working_proxies = self.filter_working_proxies(new_proxies)
            print(f"验证后剩余 {len(working_proxies)} 个有效代理")
            
            # 更新代理列表
            self.proxies = working_proxies
            self.last_update = datetime.now()
            
            print("代理列表更新完成")
            return len(working_proxies)
    
    def get_random_proxy(self):
        """获取一个随机代理"""
        with self.lock:
            if not self.proxies:
                return None
            return random.choice(self.proxies)
    
    def get_all_proxies(self):
        """获取所有代理"""
        with self.lock:
            return self.proxies.copy()
    
    def start_auto_update(self):
        """启动自动更新线程"""
        def update_worker():
            while True:
                try:
                    self.update_proxy_list()
                    time.sleep(self.update_interval)
                except Exception as e:
                    print(f"自动更新代理时出错: {e}")
                    time.sleep(60)  # 出错后等待1分钟再试
        
        thread = threading.Thread(target=update_worker, daemon=True)
        thread.start()
        return thread
    
    def needs_update(self):
        """检查是否需要更新代理列表"""
        if not self.last_update:
            return True
        
        return datetime.now() - self.last_update > timedelta(seconds=self.update_interval)

# 创建全局代理管理器实例
proxy_manager = ProxyManager()