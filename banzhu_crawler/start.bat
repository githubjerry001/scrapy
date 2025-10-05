@echo off
REM Banzhu爬虫程序快速启动脚本
REM 作者: Qoder AI Assistant
REM 日期: %date%

title Banzhu爬虫程序启动器

echo ================================
echo   Banzhu爬虫程序快速启动脚本
echo ================================
echo.

REM 检查是否在正确的目录
if not exist "enhanced_banzhu_app.py" (
    echo 错误: 未找到 enhanced_banzhu_app.py 文件
    echo 请确保此脚本位于scrapy项目根目录下
    echo 当前目录: %cd%
    echo.
    pause
    exit /b 1
)

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    echo 请确保已安装Python并添加到系统PATH中
    echo.
    pause
    exit /b 1
)

REM 检查必要的依赖包
echo 检查必要的依赖包...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装Flask...
    pip install flask
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装requests...
    pip install requests
)

python -c "import chardet" >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装chardet...
    pip install chardet
)

python -c "import bs4" >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装beautifulsoup4...
    pip install beautifulsoup4
)

echo.
echo 所有依赖包检查完成。
echo.

REM 启动Banzhu爬虫程序
echo 启动Banzhu爬虫程序...
echo 程序将在 http://127.0.0.1:5000 上运行
echo 按 Ctrl+C 可以停止程序
echo.

REM 使用开发模式启动，方便调试
set FLASK_ENV=development
set FLASK_APP=enhanced_banzhu_app.py

python enhanced_banzhu_app.py

echo.
echo 程序已退出。
pause