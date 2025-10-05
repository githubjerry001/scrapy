@echo off
REM 增强版Banzhu爬虫程序启动脚本
REM 作者: Qoder AI Assistant

title Banzhu爬虫程序启动器

:menu
cls
echo ================================
echo   Banzhu爬虫程序启动菜单
echo ================================
echo.
echo 1. 启动Banzhu爬虫程序
echo 2. 检查并安装依赖
echo 3. 查看程序状态
echo 4. 停止所有Python进程
echo 5. 退出
echo.
set /p choice=请选择操作 (1-5): 

if "%choice%"=="1" goto start_app
if "%choice%"=="2" goto install_deps
if "%choice%"=="3" goto check_status
if "%choice%"=="4" goto stop_python
if "%choice%"=="5" goto exit_script
goto menu

:start_app
cls
echo 启动Banzhu爬虫程序...
echo 确保您在scrapy项目根目录下
cd /d "%~dp0"
echo 当前目录: %cd%

REM 检查必要文件
if not exist "enhanced_banzhu_app.py" (
    echo 错误: 未找到 enhanced_banzhu_app.py 文件
    pause
    goto menu
)

echo.
echo 程序将在 http://127.0.0.1:5000 上运行
echo 按 Ctrl+C 可以停止程序
echo.
set FLASK_ENV=development
set FLASK_APP=enhanced_banzhu_app.py
python enhanced_banzhu_app.py
pause
goto menu

:install_deps
cls
echo 检查并安装必要的依赖包...
cd /d "%~dp0"

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    pause
    goto menu
)

echo Python环境检查通过

REM 安装/检查依赖
echo.
echo 安装Flask...
pip install flask

echo.
echo 安装requests...
pip install requests

echo.
echo 安装chardet...
pip install chardet

echo.
echo 安装beautifulsoup4...
pip install beautifulsoup4

echo.
echo 所有依赖包安装完成。
pause
goto menu

:check_status
cls
echo 检查程序状态...
echo.

REM 检查Python进程
echo 正在运行的Python进程:
tasklist /fi "imagename eq python.exe"
echo.

REM 检查端口占用
echo 检查5000端口占用情况:
netstat -ano | findstr :5000
echo.

pause
goto menu

:stop_python
cls
echo 停止所有Python进程...
echo.

tasklist /fi "imagename eq python.exe"
echo.
set /p confirm=确定要停止所有Python进程吗? (y/N): 

if /i "%confirm%"=="y" (
    echo 正在停止所有Python进程...
    taskkill /f /im python.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo Python进程已停止。
    ) else (
        echo 没有找到Python进程或停止失败。
    )
) else (
    echo 操作已取消。
)

pause
goto menu

:exit_script
cls
echo 感谢使用Banzhu爬虫程序！
echo.
pause
exit /b 0