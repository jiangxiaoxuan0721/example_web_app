---
name: solo_app
type: knowledge
version: 2.0.0
agent: CodeActAgent
triggers:
- App
- app
- 应用
- Web
- web
- 网站
- 数据分析
- analysis
---

if you are asking to build a web app, refer to following guidelines:

<Quick_start>

1. 拉取项目模板：

   ```bash
   git clone https://github.com/jiangxiaoxuan0721/example_web_app.git your-app
   cd your-app
   ```

2. 启动应用：

   ```bash
   python app.py
   ```

3. 验证应用：
   使用 [browser: goto] 访问 `http://<IP>:50890`，确保应用正常运行。
   **注意**：不要使用 localhost 或 127.0.0.1，默认 IP 为 192.168.130.30，端口需确保可被外部访问。

</Quick_start>

<Project_features>

**技术栈**: Flask + 原生JS组件化 + CSS变量主题 + 深蓝-蓝-白配色

**核心特性**:

- 组件化架构（一个组件 = 一个CSS + 一个JS）
- CSS变量主题系统
- 环境变量配置
- 统一静态文件路由
- 响应式设计

</Project_features>

<Project_structure>

```bash
├── app.py              # Flask入口（仅路由）
├── config.py           # 配置（pathlib + 环境变量）
├── backend/
│   ├── data_generator/   # CloudPSS仿真
│   └── data_processor/  # 数据处理
├── frontend/
│   ├── main.css        # 全局样式 + CSS变量
│   ├── components/     # 组件目录
│   │   ├── kpi_cards/
│   │   ├── tables/
│   │   ├── drawer/
│   │   └── ...
│   └── pages/         # 页面模板
└── output/            # 数据输出
```

</Project_structure>

<Development_standards>

### config.py

```python
import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).resolve().parent
    TEMPLATE_DIR = BASE_DIR / 'frontend' / 'pages'
    STATIC_DIR = BASE_DIR / 'frontend'
    
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 50890))
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1')
    
    CLOUDPSS = {
        "TOKEN": os.getenv('CLOUDPSS_TOKEN', ''),
        "API_URL": os.getenv('CLOUDPSS_API_URL', 'https://cloudpss.net/')
    }
```

### app.py

**原则**: 仅配置路由，业务逻辑放backend

```python
from flask import Flask, render_template, jsonify, send_from_directory
from config import Config

app = Flask(__name__, template_folder=str(Config.TEMPLATE_DIR), 
            static_folder=str(Config.STATIC_DIR))

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(str(Config.STATIC_DIR), filename)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/<endpoint>')
def api(endpoint):
    # 调用 backend 模块处理
    return jsonify(result)

@app.errorhandler(404)
def not_found(_):
    return render_template('not_support.html'), 404

app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=Config.DEBUG)
```

### 组件规范

```bash
components/your_component/
├── your_component.css  # 组件样式
└── your_component.js   # 组件逻辑
```

```javascript
class YourComponent {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = options;
        this.init();
    }
    
    init() { this.render(); this.bindEvents(); }
    render() { /* 渲染逻辑 */ }
    bindEvents() { /* 事件绑定 */ }
}
```

### CSS变量系统

全局变量在 `main.css`，组件使用CSS变量：

```css
:root {
    --primary-color: #1890ff;
    --success-color: #52c41a;
    --text-main: #333;
    --card-bg: #fff;
}
```

</Development_standards>

<Component_library>

- **kpi_cards**: KPI指标展示
- **tables**: 数据表格（搜索/排序/分页）
- **drawer**: 侧边详情面板
- **picture**: 图片/HTML内容展示
- **buttons**: 按钮组件
- **function_cards**: 功能卡片
- **informations**: 信息展示组件

</Component_library>

<Programming_standards>

1、修改文件时：**直接修改文件**，而不是每次都新建文件。

2、界面设计原则：响应式风格 + 深蓝-蓝-白配色 + 极简专业风格，拒绝过多颜色和动画。

3、组件复用原则：优先使用现有组件库或实现可复用模块。

4、路由设计原则：API路由统一使用 `/api/` 前缀，静态文件统一处理。

5、代码质量原则：单一职责、无重复代码、适当注释。

</Programming_standards>
