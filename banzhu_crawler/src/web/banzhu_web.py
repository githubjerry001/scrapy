from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import os
import json
import threading
import time
import requests
from urllib.parse import urljoin, urlparse
import re
import random
from itertools import cycle

# 添加项目根目录到Python路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入代理管理器
try:
    from proxy_manager import proxy_manager
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from proxy_manager import proxy_manager

app = Flask(__name__, template_folder='../../templates')

# 存储爬虫进程状态
crawler_process = None
crawler_status = "idle"  # idle, running, finished, error
crawler_output = []

# 存储文章信息
selected_articles = []
downloaded_articles = []

def get_chapters_from_article(article_url):
    """从文章页面提取章节链接"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # 添加延迟以避免触发反爬虫机制
        import time
        time.sleep(2)
        
        response = requests.get(article_url, headers=headers, timeout=15)
                
        # 智能编码检测和处理
        import chardet
        detected_encoding = chardet.detect(response.content)
        detected_enc = detected_encoding.get('encoding', '').lower() if detected_encoding else ''
        
        # 中文网站优先使用GB系列编码
        encoding_candidates = ['gb2312', 'gbk', 'gb18030', detected_enc, 'utf-8']
        
        content = ''
        for encoding in encoding_candidates:
            if not encoding:
                continue
            try:
                response.encoding = encoding
                content = response.text
                if '锟斤拷' not in content and '�' not in content:
                    print(f"Article page decoded with: {encoding}")
                    break
            except:
                continue
        
        if not content:
            content = response.content.decode('gb2312', errors='ignore')
        
        # 保存页面内容以供分析
        with open('article_page.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 尝试提取章节链接（这里需要根据实际网站结构调整）
        chapters = []
        
        # 常见的章节链接选择器
        import re
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找可能的章节链接
        chapter_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            # 匹配章节链接的常见模式
            if re.search(r'(第?.*?[章节]|\d+)', text) or re.search(r'chapter|section', href, re.I):
                full_url = urljoin(article_url, href)
                chapter_links.append({
                    'url': full_url,
                    'title': text
                })
        
        # 如果没找到明确的章节链接，尝试其他方法
        if not chapter_links:
            # 查找所有链接
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().strip()
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    full_url = urljoin(article_url, href)
                    chapter_links.append({
                        'url': full_url,
                        'title': text
                    })
        
        return chapter_links[:50]  # 限制数量
        
    except Exception as e:
        print(f"Error extracting chapters: {e}")
        return []

def download_chapter_content(chapter_url):
    """下载章节内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # 添加延迟以避免触发反爬虫机制
        import time
        time.sleep(3)
        
        response = requests.get(chapter_url, headers=headers, timeout=15)
        
        # 智能编码检测和处理
        import chardet
        detected_encoding = chardet.detect(response.content)
        detected_enc = detected_encoding.get('encoding', '').lower() if detected_encoding else ''
        
        # 中文网站优先使用GB系列编码
        encoding_candidates = ['gb2312', 'gbk', 'gb18030', detected_enc, 'utf-8']
        
        content = ''
        for encoding in encoding_candidates:
            if not encoding:
                continue
            try:
                response.encoding = encoding
                content = response.text
                if '锟斤拷' not in content and '�' not in content:
                    print(f"Chapter decoded with: {encoding}")
                    break
            except:
                continue
        
        if not content:
            content = response.content.decode('gb2312', errors='ignore')
        
        # 使用BeautifulSoup解析内容
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # 尝试提取正文内容
        content = ""
        
        # 移除脚本和样式标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 尝试常见的内容选择器
        content_selectors = [
            '.content',
            '.article-content',
            '.post-content',
            '.entry-content',
            '#content',
            'article',
            '.article',
            '.post'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = elements[0].get_text(strip=True)
                break
        
        # 如果没找到，尝试获取body文本
        if not content:
            content = soup.get_text(strip=True)
        
        return content[:2000]  # 限制内容长度
        
    except Exception as e:
        print(f"Error downloading chapter: {e}")
        return f"Error downloading chapter: {e}"

@app.route('/')
def index():
    """主页 - 嵌入目标网站"""
    return render_template('index.html')

@app.route('/proxy')
def proxy():
    """代理访问目标网站"""
    url = request.args.get('url', 'https://www.banzhu6666666.com/')
    
    try:
        # 确保URL包含协议
        if not url.startswith('http'):
            url = 'https://' + url
            
        # 使用移动设备User-Agent来绕过限制
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        import time
        import chardet
        import random
        
        # 创建会话并设置重试策略
        session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 使用随机User-Agent池来避免被识别
        user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        ]
        
        # 获取随机代理服务器
        proxy = proxy_manager.get_random_proxy()
        
        # 随机选择User-Agent
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        session.headers.update(headers)
        
        # 添加随机延迟以避免触发反爬虫机制
        time.sleep(random.uniform(2, 5))
        
        # 如果没有自动获取到代理，则使用预定义的代理池
        if not proxy:
            # 代理服务器池（用户可以在这里添加自己的代理服务器）
            predefined_proxies = [
                # 格式: {'http': 'http://user:password@ip:port', 'https': 'http://user:password@ip:port'}
                # 示例: {'http': 'http://proxyuser:proxypass@1.2.3.4:8080', 'https': 'http://proxyuser:proxypass@1.2.3.4:8080'}
                # 免费代理示例（请替换为有效的代理服务器）:
                # {'http': 'http://1.2.3.4:8080', 'https': 'http://1.2.3.4:8080'},
                # {'http': 'http://5.6.7.8:3128', 'https': 'http://5.6.7.8:3128'}
            ]
            proxy = random.choice(predefined_proxies) if predefined_proxies else None
        
        # 发送请求
        if proxy:
            response = session.get(url, timeout=30, proxies=proxy)
        else:
            response = session.get(url, timeout=30)
        
        # 检查是否被封禁IP
        if response.status_code == 403 or "Access denied" in response.text or " Ray ID:" in response.text:
            print(f"IP被封禁，状态码: {response.status_code}")
            # 如果使用了代理仍然被封禁，尝试不使用代理
            if proxy:
                try:
                    response = session.get(url, timeout=30)
                    if response.status_code != 403 and "Access denied" not in response.text and " Ray ID:" not in response.text:
                        # 不使用代理成功了，继续处理
                        pass
                    else:
                        return f"<!DOCTYPE html><html><head><title>访问被拒绝</title></head><body><h2>访问被拒绝</h2><p>您的IP地址已被目标网站封禁。</p><p>错误信息: {response.status_code}</p><p>解决方案:</p><ol><li>等待一段时间后再尝试访问</li><li>使用不同的网络环境</li><li>联系系统管理员</li><li>系统正在自动获取新的代理服务器，请稍后再试</li></ol><p>提示：系统已自动获取免费代理服务器，如问题持续存在，请稍后再试。</p></body></html>", 200, {'Content-Type': 'text/html; charset=utf-8'}
                except Exception as e:
                    return f"<!DOCTYPE html><html><head><title>访问被拒绝</title></head><body><h2>访问被拒绝</h2><p>您的IP地址已被目标网站封禁。</p><p>错误信息: {response.status_code}</p><p>解决方案:</p><ol><li>等待一段时间后再尝试访问</li><li>使用不同的网络环境</li><li>联系系统管理员</li><li>系统正在自动获取新的代理服务器，请稍后再试</li></ol><p>提示：系统已自动获取免费代理服务器，如问题持续存在，请稍后再试。</p></body></html>", 200, {'Content-Type': 'text/html; charset=utf-8'}
            else:
                return f"<!DOCTYPE html><html><head><title>访问被拒绝</title></head><body><h2>访问被拒绝</h2><p>您的IP地址已被目标网站封禁。</p><p>错误信息: {response.status_code}</p><p>解决方案:</p><ol><li>等待一段时间后再尝试访问</li><li>使用不同的网络环境</li><li>联系系统管理员</li><li>系统正在自动获取新的代理服务器，请稍后再试</li></ol><p>提示：系统已自动获取免费代理服务器，如问题持续存在，请稍后再试。</p></body></html>", 200, {'Content-Type': 'text/html; charset=utf-8'}
        
        # 智能编码检测和降级处理机制
        import chardet
        detected_encoding = chardet.detect(response.content)
        detected_enc = detected_encoding.get('encoding', '').lower() if detected_encoding else ''
        confidence = detected_encoding.get('confidence', 0) if detected_encoding else 0
        
        print(f"Detected encoding: {detected_enc}, confidence: {confidence}")
        
        # 编码优先级策略：响应头 > meta标签 > chardet检测 > 降级备选
        encoding_candidates = []
        
        # 1. 检查HTTP响应头
        content_type = response.headers.get('content-type', '').lower()
        if 'charset=' in content_type:
            header_encoding = content_type.split('charset=')[1].split(';')[0].strip()
            encoding_candidates.append(header_encoding)
        
        # 2. 对于中文网站，优先考虑GB系列编码
        if 'banzhu' in url.lower() or 'zh' in url.lower():
            encoding_candidates.extend(['gb2312', 'gbk', 'gb18030'])
        
        # 3. 添加检测到的编码（如果置信度足够高）
        if detected_enc and confidence > 0.7:
            encoding_candidates.append(detected_enc)
        
        # 4. 添加常见编码作为备选
        encoding_candidates.extend(['utf-8', 'gb2312', 'gbk', 'gb18030', 'big5'])
        
        # 去重并保持顺序
        unique_encodings = []
        for enc in encoding_candidates:
            if enc and enc not in unique_encodings:
                unique_encodings.append(enc)
        
        # 尝试不同编码直到成功
        final_encoding = 'utf-8'  # 默认备选
        content = ''
        
        for encoding in unique_encodings:
            try:
                response.encoding = encoding
                content = response.text
                # 简单验证：检查是否包含明显的乱码字符
                if '锟斤拷' not in content and '' not in content:
                    final_encoding = encoding
                    print(f"Successfully decoded with encoding: {encoding}")
                    break
            except (UnicodeDecodeError, LookupError) as e:
                print(f"Failed to decode with {encoding}: {e}")
                continue
        
        # 如果所有编码都失败，使用原始字节并尝试UTF-8
        if not content or '锟斤拷' in content:
            try:
                content = response.content.decode('utf-8', errors='ignore')
                final_encoding = 'utf-8'
                print("Using UTF-8 with error handling")
            except:
                content = response.content.decode('gb2312', errors='ignore')
                final_encoding = 'gb2312'
                print("Using GB2312 with error handling")
        
        # 修改内容中的相对链接为绝对链接
        from urllib.parse import urljoin
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 处理链接
        for link in soup.find_all('a', href=True):
            link['href'] = urljoin(url, link['href'])
            
        # 处理图片
        for img in soup.find_all('img', src=True):
            img['src'] = urljoin(url, img['src'])
            
        # 处理CSS链接
        for link in soup.find_all('link', href=True):
            link['href'] = urljoin(url, link['href'])
            
        # 处理脚本链接
        for script in soup.find_all('script', src=True):
            script['src'] = urljoin(url, script['src'])
        
        # 移除可能阻止iframe嵌入的头部
        if soup.head:
            for meta in soup.find_all('meta'):
                if meta.get('http-equiv') and ('X-Frame-Options' in meta.get('http-equiv') or 'Content-Security-Policy' in meta.get('http-equiv')):
                    meta.decompose()
        
        # 修改或添加正确的meta标签以确保编码一致
        if soup.head:
            # 移除所有现有的charset相关的meta标签
            for meta in soup.find_all('meta'):
                # 检查http-equiv属性
                if meta.get('http-equiv') == 'Content-Type':
                    meta.decompose()
                # 检查content属性中是否包含charset
                elif meta.get('content') and 'charset' in meta.get('content').lower():
                    meta.decompose()
                # 检查charset属性
                elif meta.get('charset'):
                    meta.decompose()
            
            # 添加新的meta标签，使用最终确定的编码
            new_meta = soup.new_tag('meta')
            new_meta['charset'] = final_encoding
            soup.head.insert(0, new_meta)
        
        # 添加base标签以确保相对链接正确解析
        if soup.head:
            base_tag = soup.new_tag('base', href=url)
            soup.head.insert(0, base_tag)
        
        # 返回内容时指定最终编码
        return str(soup), 200, {'Content-Type': f'text/html; charset={final_encoding}'}
        
    except Exception as e:
        print(f"Proxy error: {str(e)}")  # 打印错误日志
        return f"<!DOCTYPE html><html><head><title>加载错误</title></head><body><h2>无法加载网站内容</h2><p>错误信息: {str(e)}</p><p>请尝试以下解决方案:</p><ol><li>点击上方的刷新按钮重试</li><li>在地址栏中输入其他网址</li><li>如果问题持续存在，请联系系统管理员</li></ol></body></html>", 200, {'Content-Type': 'text/html; charset=utf-8'}

def handle_cloudflare_challenge(url, headers):
    """处理Cloudflare挑战"""
    try:
        # 尝试使用session保持连接
        session = requests.Session()
        session.headers.update(headers)
        
        # 第一次请求
        response = session.get(url, timeout=30)
        
        # 统一使用UTF-8编码
        encoding = 'utf-8'
        response.encoding = encoding
        
        # 如果仍然返回挑战页面，尝试添加更多延迟
        if "Just a moment" in response.text or "cloudflare" in response.text.lower():
            import time
            time.sleep(5)
            response = session.get(url, timeout=30)
            response.encoding = 'utf-8'
        
        # 获取内容
        content = response.text
        
        # 修改内容中的相对链接为绝对链接
        from urllib.parse import urljoin
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 处理链接
        for link in soup.find_all('a', href=True):
            link['href'] = urljoin(url, link['href'])
            
        # 处理图片
        for img in soup.find_all('img', src=True):
            img['src'] = urljoin(url, img['src'])
            
        # 处理CSS链接
        for link in soup.find_all('link', href=True):
            link['href'] = urljoin(url, link['href'])
            
        # 处理脚本链接
        for script in soup.find_all('script', src=True):
            script['src'] = urljoin(url, script['src'])
        
        # 移除可能阻止iframe嵌入的头部
        if soup.head:
            for meta in soup.find_all('meta'):
                if meta.get('http-equiv') and ('X-Frame-Options' in meta.get('http-equiv') or 'Content-Security-Policy' in meta.get('http-equiv')):
                    meta.decompose()
        
        # 添加base标签以确保相对链接正确解析
        if soup.head:
            base_tag = soup.new_tag('base', href=url)
            soup.head.insert(0, base_tag)
        
        # 返回内容时指定UTF-8编码
        return str(soup), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        print(f"Cloudflare challenge error: {str(e)}")
        return f"<!DOCTYPE html><html><head><title>安全验证</title></head><body><h2>网站需要安全验证</h2><p>目标网站启用了安全防护机制，需要完成人机验证。</p><p>请稍后重试或联系系统管理员。</p></body></html>", 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/crawler')
def crawler_control():
    """爬虫控制页面"""
    return render_template('crawler_manager.html', status=crawler_status)

@app.route('/select_article', methods=['POST'])
def select_article():
    """选择文章"""
    try:
        data = request.get_json()
        article_url = data.get('url')
        article_title = data.get('title', 'Unknown')
        
        # 获取章节列表
        chapters = get_chapters_from_article(article_url)
        
        article_info = {
            'url': article_url,
            'title': article_title,
            'chapters': chapters
        }
        
        selected_articles.append(article_info)
        
        return jsonify({
            "status": "success",
            "article": article_info
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route('/download_article', methods=['POST'])
def download_article():
    """下载选中的文章"""
    try:
        data = request.get_json()
        article_index = data.get('index')
        
        if article_index >= len(selected_articles):
            return jsonify({
                "status": "error",
                "message": "Article not found"
            })
        
        article = selected_articles[article_index]
        chapters = article.get('chapters', [])
        
        # 下载所有章节
        full_content = f"# {article['title']}\n\n"
        
        for i, chapter in enumerate(chapters):
            crawler_output.append(f"正在下载章节 {i+1}/{len(chapters)}: {chapter['title']}")
            content = download_chapter_content(chapter['url'])
            full_content += f"\n\n## {chapter['title']}\n\n{content}\n"
            time.sleep(1)  # 避免请求过快
        
        # 保存为TXT文件
        # 清理文件名中的非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '', article['title'])
        if not filename:
            filename = f"article_{int(time.time())}"
        
        txt_filename = f"{filename}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        # 记录已下载的文章
        downloaded_articles.append({
            'title': article['title'],
            'filename': txt_filename,
            'chapter_count': len(chapters)
        })
        
        return jsonify({
            "status": "success",
            "filename": txt_filename,
            "chapter_count": len(chapters)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route('/selected_articles')
def get_selected_articles():
    """获取已选择的文章列表"""
    return jsonify(selected_articles)

@app.route('/downloaded_articles')
def get_downloaded_articles():
    """获取已下载的文章列表"""
    return jsonify(downloaded_articles)

@app.route('/start_crawler', methods=['POST'])
def start_crawler():
    """启动爬虫"""
    global crawler_process, crawler_status
    
    if crawler_status == "idle" or crawler_status == "finished" or crawler_status == "error":
        # 在新线程中运行爬虫
        thread = threading.Thread(target=run_crawler)
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already_running"})

@app.route('/stop_crawler', methods=['POST'])
def stop_crawler():
    """停止爬虫"""
    global crawler_process, crawler_status
    
    if crawler_process and crawler_process.poll() is None:
        crawler_process.terminate()
        crawler_status = "idle"
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "not_running"})

@app.route('/status')
def status():
    """获取爬虫状态"""
    return jsonify({
        "status": crawler_status,
        "output": crawler_output[-20:] if crawler_output else []  # 只返回最后20行
    })

def run_crawler():
    """运行爬虫的函数"""
    global crawler_status, crawler_output
    crawler_status = "running"
    crawler_output = []
    
    try:
        # 这里可以实现自动爬取逻辑
        crawler_output.append("自动爬虫功能正在开发中...")
        time.sleep(5)
        crawler_status = "finished"
    except Exception as e:
        crawler_status = "error"
        crawler_output.append(f"Exception: {str(e)}")

if __name__ == '__main__':
    # 启动代理自动更新
    proxy_manager.start_auto_update()
    # 初始化更新一次代理列表
    proxy_manager.update_proxy_list()
    
    app.run(debug=True, host='0.0.0.0', port=5000)