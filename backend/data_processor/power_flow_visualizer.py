import json
import os
from config import Config

def load_branch_data():
    """加载支路数据"""
    branch_file = os.path.join(Config.OUTPUT_DIR, 'IEEE3_branch.json')
    
    if not os.path.exists(branch_file):
        return None
    
    with open(branch_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data[0] if data else None

def parse_branch_data():
    """解析支路数据，提取功率流信息"""
    branch_data = load_branch_data()
    
    if not branch_data or not branch_data.get('data', {}).get('columns'):
        return None
    
    columns = branch_data['data']['columns']
    
    # 提取各列数据
    branch_ids = columns[0]['data']  # Branch ID
    from_buses = columns[1]['data']  # From bus
    pij_values = columns[2]['data']  # Pij / MW (有功功率)
    qij_values = columns[3]['data']  # Qij / MVar (无功功率)
    to_buses = columns[4]['data']    # To bus
    pji_values = columns[5]['data']  # Pji / MW
    qji_values = columns[6]['data']  # Qji / MVar
    ploss_values = columns[7]['data']  # Ploss / MW (有功损耗)
    qloss_values = columns[8]['data']  # Qloss / MVar (无功损耗)
    
    branches = []
    for i in range(len(branch_ids)):
        branch = {
            'id': branch_ids[i],
            'from_bus': from_buses[i],
            'to_bus': to_buses[i],
            'active_power_from': float(pij_values[i]),
            'reactive_power_from': float(qij_values[i]),
            'active_power_to': float(pji_values[i]),
            'reactive_power_to': float(qji_values[i]),
            'active_power_loss': float(ploss_values[i]),
            'reactive_power_loss': float(qloss_values[i]),
            'total_active_power': abs(float(pij_values[i])),
            'total_reactive_power': abs(float(qij_values[i]))
        }
        branches.append(branch)
    
    return branches

def get_power_flow_graph_data():
    """获取功率流图数据，用于前端可视化"""
    branches = parse_branch_data()
    
    if not branches:
        return {'nodes': [], 'edges': []}
    
    # 提取所有节点
    nodes = {}
    for branch in branches:
        from_bus = branch['from_bus']
        to_bus = branch['to_bus']
        
        if from_bus not in nodes:
            nodes[from_bus] = {
                'id': from_bus,
                'label': from_bus.split('_')[-1],  # 提取数字部分
                'x': 0,
                'y': 0
            }
        
        if to_bus not in nodes:
            nodes[to_bus] = {
                'id': to_bus,
                'label': to_bus.split('_')[-1],
                'x': 0,
                'y': 0
            }
    
    # 横向布局初始位置
    node_list = list(nodes.values())
    for i, node in enumerate(node_list):
        node['x'] = 100 + i * 250  # 横向排列，间距250px
        node['y'] = 200             # 固定在中间位置
    
    # 创建边（支路）
    edges = []
    for branch in branches:
        # 计算功率大小用于边的粗细
        power_magnitude = branch['total_active_power']
        
        # 根据功率大小设置边的样式
        if power_magnitude > 100:
            width = 5
            color = '#ff4444'  # 高功率 - 红色
        elif power_magnitude > 50:
            width = 3
            color = '#ffaa00'  # 中功率 - 橙色
        else:
            width = 2
            color = '#4444ff'  # 低功率 - 蓝色
        
        edge = {
            'id': branch['id'],
            'from': branch['from_bus'],
            'to': branch['to_bus'],
            'label': f"P: {branch['active_power_from']:.1f}MW\nQ: {branch['reactive_power_from']:.1f}MVar",
            'width': width,
            'color': color,
            'arrows': 'to',
            'data': {
                'active_power': branch['active_power_from'],
                'reactive_power': branch['reactive_power_from'],
                'power_loss': branch['active_power_loss']
            }
        }
        edges.append(edge)
    
    return {
        'nodes': list(nodes.values()),
        'edges': edges
    }

def get_power_summary():
    """获取功率流统计信息"""
    branches = parse_branch_data()
    
    if not branches:
        return None
    
    total_active_power = sum(b['total_active_power'] for b in branches)
    total_reactive_power = sum(b['total_reactive_power'] for b in branches)
    total_active_loss = sum(b['active_power_loss'] for b in branches)
    total_reactive_loss = sum(b['reactive_power_loss'] for b in branches)
    
    max_power_branch = max(branches, key=lambda b: b['total_active_power'])
    min_power_branch = min(branches, key=lambda b: b['total_active_power'])
    
    return {
        'total_branches': len(branches),
        'total_active_power': total_active_power,
        'total_reactive_power': total_reactive_power,
        'total_active_loss': total_active_loss,
        'total_reactive_loss': total_reactive_loss,
        'max_power_branch': {
            'id': max_power_branch['id'],
            'power': max_power_branch['total_active_power'],
            'from': max_power_branch['from_bus'],
            'to': max_power_branch['to_bus']
        },
        'min_power_branch': {
            'id': min_power_branch['id'],
            'power': min_power_branch['total_active_power'],
            'from': min_power_branch['from_bus'],
            'to': min_power_branch['to_bus']
        }
    }