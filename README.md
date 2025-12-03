# 可扩展Web应用基础架构模板

基于Flask的模块化Web应用基础架构，专为快速开发和扩展而设计。本项目采用分层架构和模块化设计，提供了一套完整的前后端分离开发框架。

## 当前环境部署指南

### 环境要求

- **操作系统**: Windows (当前环境: win32)
- **Python版本**: 3.7+
- **Shell**: PowerShell (当前环境)
- **工作目录**: `z:\respos\example_web_app`

### 快速部署步骤

#### 1. 环境准备

```powershell
# 进入项目目录
cd z:\respos\example_web_app

# 创建Python虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 安装基础依赖
pip install flask flask-cors requests
```

#### 2. 项目结构检查

确保以下目录结构存在：

```bash
z:\respos\example_web_app\
├── app.py                           # Flask应用入口
├── config.py                        # 配置文件
├── backend/                         # 后端模块
│   ├── data_generator/
│   ├── data_processor/
│   └── data_visualizer/
├── frontend/                        # 前端资源
│   ├── templates/
│   └── static/
└── output/                          # 数据输出目录
```

#### 3. 运行应用

```powershell
# 直接运行Flask应用
python app.py

# 或使用Flask命令
flask run --host=0.0.0.0 --port=5000
```

#### 4. 访问应用

- **本地访问**: <http://localhost:5000>
- **网络访问**: http://[你的IP]:5000

### 当前环境配置

#### config.py 配置示例

```python
import os

class Config:
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 文件路径配置 (适配Windows环境)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    
    # 前端资源路径
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'frontend', 'templates')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'frontend', 'static')
    
    # 开发环境配置
    DEBUG = True
    TESTING = False
    
    # API配置
    API_BASE_URL = "http://localhost:5000/api"
    
    # 数据缓存配置
    CACHE_TIMEOUT = 300  # 5分钟
```

#### app.py 启动配置

```python
from flask import Flask, render_template, jsonify
import os

# 创建Flask应用
app = Flask(__name__,
    template_folder='frontend/templates',
    static_folder='frontend/static'
)

# 加载配置
app.config.from_object('config')

# 路由注册
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    # 数据处理逻辑
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    # Windows环境下启动配置
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
```

### 常见问题解决

#### 1. PowerShell执行策略问题

```powershell
# 如果出现无法执行脚本的问题
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. 端口占用问题

```powershell
# 查看端口占用
netstat -ano | findstr :5000

# 终止占用进程
taskkill /PID <进程ID> /F
```

#### 3. 模块导入问题

```powershell
# 确保在项目根目录运行
cd z:\respos\example_web_app

# 检查Python路径
python -c "import sys; print(sys.path)"
```

### 开发工作流

#### 1. 日常开发

```powershell
# 激活环境
.\venv\Scripts\Activate.ps1

# 启动开发服务器 (自动重载)
flask run --debug

# 查看日志
flask run --debug --log-level=DEBUG
```

#### 2. 模块开发

```powershell
# 创建新模块
mkdir backend\your_module
echo "" > backend\your_module\__init__.py

# 测试模块
python -c "from backend.your_module import *; print('模块导入成功')"
```

#### 3. 前端开发

```powershell
# 监控静态文件变化 (需要额外工具)
pip install watchdog
python -c "
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(('.html', '.css', '.js')):
            print('前端文件已更新，刷新浏览器查看效果')

observer = Observer()
observer.schedule(ReloadHandler(), 'frontend', recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
"
```

### 部署优化

#### 1. 生产环境配置

```python
# config.py 生产环境配置
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 性能配置
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1年缓存
```

#### 2. Windows服务部署

```python
# 使用pyinstaller打包
pip install pyinstaller
pyinstaller --onefile --add-data "frontend;frontend" app.py

# 或使用NSSM安装为Windows服务
# 1. 下载NSSM
# 2. nssm install YourApp "python z:\respos\example_web_app\app.py"
# 3. nssm start YourApp
```

#### 3. 反向代理配置 (IIS)

```xml
<!-- web.config -->
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Flask" stopProcessing="true">
          <match url="^(.*)$" />
          <action type="Rewrite" url="http://localhost:5000/{R:1}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

### 监控和调试

#### 1. 日志配置

```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

#### 2. 性能监控

```python
# 简单的请求时间监控
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    app.logger.info(f'请求耗时: {duration:.3f}s')
    return response
```

## 架构扩展建议

### 1. 数据库集成

- SQLite: 轻量级本地数据库
- SQL Server: Windows环境企业级数据库
- PostgreSQL: 开源关系型数据库

### 2. 缓存系统

- 内存缓存: Python内置缓存
- 文件缓存: 基于output目录的文件缓存
- Redis: 如需高性能缓存

### 3. 任务队列

- Celery + Redis: 异步任务处理
- Windows计划任务: 定时任务执行

### 4. 前端增强

- Vue.js/React: 现代前端框架
- TypeScript: 类型安全的JavaScript
- Webpack: 前端构建工具

## 技术栈总结

### 当前技术栈

- **后端**: Flask + Python
- **前端**: HTML5 + CSS3 + JavaScript
- **数据格式**: JSON
- **部署环境**: Windows + PowerShell

### 可选扩展

- **数据库**: SQLite/SQL Server/PostgreSQL
- **缓存**: Redis/Memory
- **前端框架**: Vue.js/React
- **部署方案**: Docker/IIS/Nginx

## 许可证

MIT License - 详见LICENSE文件
