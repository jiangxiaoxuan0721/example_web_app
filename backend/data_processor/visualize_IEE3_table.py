import json
import os
from config import Config

def get_table_data():
    """直接读取原始JSON数据并返回"""
    bus_file = os.path.join(Config.OUTPUT_DIR, 'IEEE3_bus.json')
    branch_file = os.path.join(Config.OUTPUT_DIR, 'IEEE3_branch.json')
    
    result = {
        'buses': None,
        'branches': None
    }
    
    try:
        if os.path.exists(bus_file):
            with open(bus_file, 'r', encoding='utf-8') as f:
                bus_data = json.load(f)
                result['buses'] = bus_data[0] if bus_data else None
    except Exception as e:
        print(f"读取bus数据失败: {e}")
    
    try:
        if os.path.exists(branch_file):
            with open(branch_file, 'r', encoding='utf-8') as f:
                branch_data = json.load(f)
                result['branches'] = branch_data[0] if branch_data else None
    except Exception as e:
        print(f"读取branch数据失败: {e}")
    
    return result