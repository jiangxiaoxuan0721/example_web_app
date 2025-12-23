"""
main app module
"""
from flask import Flask, render_template, jsonify, send_from_directory
from config import Config

app = Flask(
    __name__,
    template_folder=str(Config.TEMPLATE_DIR),
    static_folder=str(Config.STATIC_DIR)
)

# 静态文件路由 - 统一处理所有静态资源
@app.route('/<path:filename>')
def serve_static(filename):
    """服务静态文件（CSS、JS、组件文件等）"""
    return send_from_directory(str(Config.STATIC_DIR), filename)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/not-supported')
def not_supported():
    return render_template('not_support.html')

@app.route('/batch-n1')
def batch_n1():
    return render_template('batch_n_1/batch_n_1.html')

# API路由示例
@app.route('/api/status')
def get_status():
    """API: 获取系统状态"""
    return jsonify({
        'status': 'running',
        'message': '电力系统分析平台运行正常'
    })

@app.errorhandler(404)
def not_found(_):
    """404错误处理"""
    return render_template('not_support.html'), 404

@app.errorhandler(500)
def internal_error(_):
    """500错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == "__main__":
    app.run(
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        debug=Config.DEBUG
    )
    