from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import os
import json
import threading
import time

app = Flask(__name__)

# 存储爬虫进程状态
crawler_process = None
crawler_status = "idle"  # idle, running, finished, error
crawler_output = []

def run_crawler():
    """运行爬虫的函数"""
    global crawler_status, crawler_output
    crawler_status = "running"
    crawler_output = []
    
    try:
        # 运行Scrapy爬虫
        process = subprocess.Popen(
            ["python", "-m", "scrapy", "crawl", "banzhu"],
            cwd=os.path.join(os.path.dirname(__file__), "banzhu_crawler"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时读取输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                crawler_output.append(output.strip())
                print(output.strip())
        
        # 等待进程结束
        process.wait()
        
        if process.returncode == 0:
            crawler_status = "finished"
        else:
            crawler_status = "error"
            # 读取错误输出
            stderr_output = process.stderr.read()
            crawler_output.append(f"Error: {stderr_output}")
            
    except Exception as e:
        crawler_status = "error"
        crawler_output.append(f"Exception: {str(e)}")

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', status=crawler_status)

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

@app.route('/results')
def results():
    """显示爬虫结果"""
    results_data = []
    try:
        # 尝试读取爬虫结果文件
        results_file = os.path.join(os.path.dirname(__file__), "banzhu_crawler", "articles.json")
        if os.path.exists(results_file):
            with open(results_file, 'r', encoding='utf-8') as f:
                results_data = json.load(f)
    except Exception as e:
        print(f"Error reading results: {e}")
    
    return render_template('results.html', results=results_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)