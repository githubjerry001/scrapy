# 更新日志

## [1.0.10] - 2025-10-05

### 增强
- 实现代理服务器自动获取和更新功能
- 创建代理管理器模块，支持从免费代理源获取代理列表
- 添加自动验证机制，确保代理服务器的有效性
- 实现代理服务器的自动轮询和更新

## [1.0.9] - 2025-10-05

### 增强
- 实现代理服务器池支持，允许用户配置多个代理服务器以绕过IP封禁
- 添加前端代理配置界面，方便用户管理代理设置
- 改进IP封禁检测和处理机制，增强反爬虫能力
- 更新错误提示信息，提供更详细的解决方案

## [1.0.8] - 2025-10-05

### 增强
- 增强代理功能以更好地处理IP封禁和访问拒绝情况
- 添加随机User-Agent池以避免被识别为爬虫
- 改进反爬虫策略，增加随机延迟和重试机制
- 更新HTML模板以更好地检测和处理IP封禁情况

## [1.0.7] - 2025-10-05

### 优化
- 重命名web目录下的app.py为banzhu_web.py，提高文件命名的专业性和描述性
- 更新Flask应用的模板文件夹配置，确保正确指向项目根目录的templates文件夹
- 保持所有__init__.py文件以确保Python包结构的完整性

## [1.0.6] - 2025-10-05

### 修复
- 修复Flask模板路径配置问题，解决TemplateNotFound错误
- 将HTML模板文件移至项目根目录的templates文件夹中
- 更新Flask应用的template_folder配置以正确指向模板文件夹

## [1.0.5] - 2025-10-05

### 优化
- 创建爬虫基类BaseBanzhuSpider，减少代码重复
- 重构所有爬虫文件以继承基类，提高代码复用性
- 保持三个独立的爬虫文件以满足不同使用场景需求

## [1.0.4] - 2025-10-05

### 优化
- 将website_browser.html重命名为index.html，作为程序首页更符合惯例

## [1.0.3] - 2025-10-05

### 优化
- 重命名HTML模板文件，提高可读性和专业性：
  - enhanced_index.html → website_browser.html
  - crawler_control.html → crawler_manager.html

## [1.0.2] - 2025-10-05

### 优化
- 删除无用的源代码文件(src/main.py, src/web/simple_app.py)
- 删除未使用的模板文件(src/web/templates/index.html, src/web/templates/results.html)
- 移除空的静态资源目录(src/web/static)

## [1.0.1] - 2025-10-05

### 修复
- 修正目录结构，移除重复的banzhu_crawler目录
- 更新Scrapy配置，确保正确识别爬虫模块路径

## [1.0.0] - 2025-10-05

### 新增
- 重新设计项目目录结构，提高代码组织性和可维护性
- 添加主入口文件run.py，统一项目启动方式
- 添加requirements.txt文件，明确项目依赖
- 创建docs目录用于存放文档

### 改进
- 优化目录结构，将Web模板文件移动到src/web/templates目录
- 重命名爬虫文件，使其命名更加规范
- 移除重复和无用的启动脚本

### 删除
- 移除多余的启动脚本文件(quick_start.bat, start.bat, start.ps1, start_enhanced.bat)
- 删除重复的enhanced_banzhu_app.py文件