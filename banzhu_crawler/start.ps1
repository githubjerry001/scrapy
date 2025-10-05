# Banzhu爬虫程序启动脚本 (PowerShell版本)
# 作者: Qoder AI Assistant

Write-Host "================================" -ForegroundColor Green
Write-Host "  Banzhu爬虫程序启动脚本" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $ScriptDir

# 检查是否在正确的目录
if (-not (Test-Path "enhanced_banzhu_app.py")) {
    Write-Host "错误: 未找到 enhanced_banzhu_app.py 文件" -ForegroundColor Red
    Write-Host "请确保此脚本位于scrapy项目根目录下" -ForegroundColor Red
    Write-Host "当前目录: $((Get-Location).Path)" -ForegroundColor Red
    Write-Host ""
    pause
    exit 1
}

# 检查Python是否可用
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python未找到"
    }
    Write-Host "Python版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到Python环境" -ForegroundColor Red
    Write-Host "请确保已安装Python并添加到系统PATH中" -ForegroundColor Red
    Write-Host ""
    pause
    exit 1
}

# 检查必要的依赖包
Write-Host "检查必要的依赖包..." -ForegroundColor Yellow

# 检查并安装Flask
try {
    python -c "import flask" 2>&1 > $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "安装Flask..." -ForegroundColor Yellow
        pip install flask
    } else {
        Write-Host "Flask已安装" -ForegroundColor Green
    }
} catch {
    Write-Host "安装Flask..." -ForegroundColor Yellow
    pip install flask
}

# 检查并安装requests
try {
    python -c "import requests" 2>&1 > $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "安装requests..." -ForegroundColor Yellow
        pip install requests
    } else {
        Write-Host "requests已安装" -ForegroundColor Green
    }
} catch {
    Write-Host "安装requests..." -ForegroundColor Yellow
    pip install requests
}

# 检查并安装chardet
try {
    python -c "import chardet" 2>&1 > $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "安装chardet..." -ForegroundColor Yellow
        pip install chardet
    } else {
        Write-Host "chardet已安装" -ForegroundColor Green
    }
} catch {
    Write-Host "安装chardet..." -ForegroundColor Yellow
    pip install chardet
}

# 检查并安装beautifulsoup4
try {
    python -c "import bs4" 2>&1 > $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "安装beautifulsoup4..." -ForegroundColor Yellow
        pip install beautifulsoup4
    } else {
        Write-Host "beautifulsoup4已安装" -ForegroundColor Green
    }
} catch {
    Write-Host "安装beautifulsoup4..." -ForegroundColor Yellow
    pip install beautifulsoup4
}

Write-Host ""
Write-Host "所有依赖包检查完成。" -ForegroundColor Green
Write-Host ""

# 启动Banzhu爬虫程序
Write-Host "启动Banzhu爬虫程序..." -ForegroundColor Yellow
Write-Host "程序将在 http://127.0.0.1:5000 上运行" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 可以停止程序" -ForegroundColor Cyan
Write-Host ""

# 设置环境变量
$env:FLASK_ENV = "development"
$env:FLASK_APP = "enhanced_banzhu_app.py"

# 启动应用
python enhanced_banzhu_app.py