# 构建/修改一个Web应用

## 1. 环境准备

请拉取GitHub仓库：`https://github.com/jiangxiaoxuan0721/example_web_app.git`，并重命名为你的项目名称。

然后，预安装一些你可能会用到的依赖：

```bash
pip install flask # flask框架
pip install cloudpss # cloudpss api
```

## 2. 项目结构检查

确保以下目录结构存在：

```bash
z:\respos\example_web_app\
├── app.py                  # Flask应用入口
├── config.py               # 配置文件，用于配置Flask应用和其他参数，
├── backend/                # 后端模块
│   ├── data_generator/     # 在这个模块里编写cloudpss仿真代码，获取用户需要研究的仿真数据
│   └── data_processor/     # 数据处理模块，将数据处理成前端需要的格式
├── frontend/               # 前端资源
│   ├── templates/          # 前端模板
│   │   ├── index.html      # 主页模板，一般为单页面web应用，可以根据需要修改
│   │   └── *.html
│   └── static/ 
│       ├── css/            # 样式表，一个css文件一个组件
│       └── js/             # 脚本文件，一个js文件一个模块
└── output/                 # 数据输出目录
```

## 3. 运行应用

```bash
python app.py
```

## 4. 访问应用

请使用浏览器工具访问应用，查看应用是否正常运行。
**你无需过多查看界面，只需要确保应用正常运行即可。**
当用户发现界面有问题时，他会进行反馈，你需要根据反馈进行修改。

## 5. 文件编写原则

### config.py 配置示例

全局唯一的配置文件，一些全局的配置可以在这里进行配置，比如服务器地址，端口号，数据库地址，数据库用户名和密码等。
你不用担心安全问题，此文件仅用户本人使用，不会被其他人看到。所以请大胆的配置，不要担心泄露。

```python
import os

class Config:
    """应用配置"""

    # 项目目录配置
    BACKEND_DIR = os.path.join(os.path.dirname(__file__), 'backend')
    FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'frontend', 'templates')
    STATIC_DIR = os.path.join(os.path.dirname(__file__), 'frontend', 'static')

    # 服务器配置
    SERVER_HOST = '0.0.0.0' # 请确保这个IP地址可以被外界访问
    SERVER_PORT = 50890 # 请确保这个端口没有被占用，并且处于可以被外界访问的状态
    DEBUG = True

    # CloudPSS配置
    CLOUDPSS = {
        "TOKEN": "<CloudPSS Token>", # 请替换为当前用户的CloudPSS Token
        "API_URL": "https://cloudpss.net/"
    }

    # 其余配置请自行添加
```

### app.py 配置示例

app.py 是Flask应用的入口文件，**请不要在app.py中编写任何业务逻辑，这里仅配置Flask应用的路由**，为了避免文件过于复杂，请将实际执行的函数封装到backend模块中，在app.py中只需要调用。**推荐使用函数内import的方式来调用函数**，这样可以避免一些可能存在的引用问题。

```python
from flask import Flask, render_template, jsonify
from backend.data_processor import visualize_IEE3_table
from backend.data_processor import power_flow_visualizer
from config import Config # 导入配置文件,基本所有配置都应该从这里导入，以便统一管理

app = Flask(
    __name__, 
    template_folder=Config.TEMPLATE_DIR,
    static_folder=Config.STATIC_DIR
) # 尤其注意这里的template_folder和static_folder参数，请使用Config.TEMPLATE_DIR和Config.STATIC_DIR，和一般的flask应用有一些区别

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_IEEE3_table')
def generate_table():
    from backend.data_generator import generate_IEEE3_table as f
    return f.generate_IEEE3_table()

# API路由 - 为前端提供数据
@app.route('/api/table')
def get_table():
    return jsonify(visualize_IEE3_table.get_table_data())

@app.route('/api/power-flow-graph')
def get_power_flow_graph():
    return jsonify(power_flow_visualizer.get_power_flow_graph_data())

@app.route('/api/power-summary')
def get_power_summary():
    return jsonify(power_flow_visualizer.get_power_summary())

@app.route('/generate_IEEE3_table')
def generate_IEEE3_table():
    from backend.data_generator import generate_IEEE3_table as f
    return f.generate_IEEE3_table()


if __name__ == "__main__":
    app.run(
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        debug=Config.DEBUG
    )
```

### 其他文件编写原则

同样的，其他文件也应当呈现高度模块化的结构，以便于维护和扩展。每个模块应该：

- **单一职责**：只负责一个明确的功能领域
- **高内聚**：模块内部功能紧密相关
- **低耦合**：模块间依赖最小化

例如，在`index.html`中，所有的js和css文件都应该通过`<script>`和`<link>`标签引入，而不是直接在html中写死。

```html
    <!-- 引入模块化的JavaScript文件 -->
    <script src="/static/js/utils.js"></script>
    <script src="/static/js/api.js"></script>
    <script src="/static/js/table.js"></script>
    <script src="/static/js/graph.js"></script>
    <script src="/static/js/main.js"></script>
```

例如，在`frontend/static/js`和`frontend/static/css`中，每个js文件和css文件都应该是一个模块，而不是一个模块里面封装了多个不相干的组件。

在编写完成一个模块后，请检查：
  
模块化检查

- [ ] 每个文件是否只负责一个功能？
- [ ] 模块间依赖是否清晰？
- [ ] 是否存在循环依赖？
- [ ] 函数是否遵循单一职责原则？

命名检查

- [ ] 文件名是否符合约定？
- [ ] 函数/变量名是否清晰表达意图？
- [ ] 是否避免缩写和模糊命名？

代码质量检查

- [ ] 是否有适当的注释和文档？
- [ ] 是否有错误处理机制？
- [ ] 是否遵循代码风格指南？
- [ ] 是否有重复代码？

## 6. 代码管理注意事项

1、修改文件时，请**直接修改文件**，尽量不要新建文件或者重复开发。

2、请根据文件大小进行拆分，以便于维护和扩展。

- **< 200行**：保持单文件
- **200-500行**：考虑按功能拆分
- **> 500行**：必须拆分为多个文件

拆分示例：

```javascript
// 原始文件：table.js (600行)
// 拆分为：
// ├── table-core.js    (核心表格功能)
// ├── table-filter.js  (过滤功能)
// ├── table-sort.js    (排序功能)
// └── table-export.js  (导出功能)
```

3、界面请广泛使用自适应风格和极简的专业风格，拒绝使用过多的颜色和图标，以免影响用户的阅读和理解。

4、常用的组件可以使用一些组件库或自己实现对应的模块，以便于维护和后续使用。

5、**特别注意**：请确保你开放的应用端口处于外界可访问的区域，并且没有被其他应用占用。
