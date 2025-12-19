"""
main app module
"""
from flask import Flask, render_template, jsonify, send_from_directory
from config import Config
import os

app = Flask(
    __name__, 
    template_folder=Config.TEMPLATE_DIR,
    static_folder=Config.STATIC_DIR
)

# 自定义静态文件路由
@app.route('/<path:filename>')
def serve_static(filename):
    """服务静态文件"""
    # 检查是否是CSS或JS文件
    if filename.endswith(('.css', '.js')):
        return send_from_directory(Config.STATIC_DIR, filename)
    # 检查是否是组件文件
    elif filename.startswith('components/') or filename.startswith('pages/'):
        return send_from_directory(Config.STATIC_DIR, filename)
    else:
        return send_from_directory(Config.STATIC_DIR, filename)

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
    return jsonify({
        'status': 'running',
        'message': '电力系统分析平台运行正常'
    })

@app.route('/api/batch-n1/data')
def get_batch_n1_data():
    # 模拟批量N-1分析数据
    data = {
        'kpi': {
            'total': 1250,
            'voltage_errors': 23,
            'frequency_errors': 8,
            'angle_errors': 15
        },
        'cases': [
            {
                'caseId': 'CASE_001',
                'transKey': 'TRANSFORMER_001',
                'faultType': 'N-1',
                'minVoltage': 0.95,
                'maxFreqDeviation': 0.2,
                'maxAngleDiff': 45.5,
                'stability': '电压越限',
                'status': 'error'
            },
            {
                'caseId': 'CASE_002',
                'transKey': 'TRANSFORMER_002',
                'faultType': 'N-1',
                'minVoltage': 0.98,
                'maxFreqDeviation': 0.1,
                'maxAngleDiff': 32.1,
                'stability': '系统稳定',
                'status': 'success'
            }
        ]
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        debug=Config.DEBUG
    )
    