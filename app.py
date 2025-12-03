"""
main app module
"""
from flask import Flask, render_template, jsonify
from backend.data_processor import visualize_IEE3_table
from backend.data_processor import power_flow_visualizer
from config import Config

app = Flask(
    __name__, 
    template_folder=Config.TEMPLATE_DIR,
    static_folder=Config.STATIC_DIR
)

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
    