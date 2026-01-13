"""
MCP 工具测试脚本
用于测试 MCP 服务器的基本功能
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.mcp.mcp_tools import (
    get_wizard_config,
    get_modes,
    get_mode,
    get_components,
    get_component,
    get_server_info,
    reload_config,
    get_session_state,
    clear_session_state
)


async def test_mcp_tools():
    """测试 MCP 工具"""
    print("=" * 60)
    print("MCP 工具测试")
    print("=" * 60)
    print()

    # 测试 1: 获取服务器信息
    print("[测试 1] 获取服务器信息")
    result = await get_server_info()
    if result.get('success'):
        print(f"✓ 服务器名称: {result['info']['name']}")
        print(f"✓ 服务器版本: {result['info']['version']}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    print()

    # 测试 2: 获取配置
    print("[测试 2] 获取 Wizard 配置")
    result = await get_wizard_config()
    if result.get('success'):
        config = result['config']
        modes = config.get('modes', {})
        components = config.get('components', {})
        print(f"✓ 模式数量: {len(modes)}")
        print(f"✓ 组件数量: {len(components)}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    print()

    # 测试 3: 获取所有模式
    print("[测试 3] 获取所有模式")
    result = await get_modes()
    if result.get('success'):
        modes = result['modes']
        for mode_id, mode in modes.items():
            print(f"✓ 模式: {mode_id} - {mode.get('name')}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    print()

    # 测试 4: 获取指定模式
    print("[测试 4] 获取指定模式 (single)")
    result = await get_mode('single')
    if result.get('success'):
        mode = result['mode']
        steps = mode.get('steps', [])
        print(f"✓ 模式名称: {mode.get('name')}")
        print(f"✓ 步骤数量: {len(steps)}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    print()

    # 测试 5: 获取所有组件
    print("[测试 5] 获取所有组件")
    result = await get_components()
    if result.get('success'):
        components = result['components']
        for comp_id, comp in components.items():
            print(f"✓ 组件: {comp_id} - {comp.get('type')}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    print()

    # 测试 6: 获取指定组件
    print("[测试 6] 获取指定组件 (parameter_table)")
    result = await get_component('parameter_table')
    if result.get('success'):
        comp = result['component']
        print(f"✓ 组件类型: {comp.get('type')}")
        fields = comp.get('fields', [])
        print(f"✓ 字段数量: {len(fields)}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    print()

    # 测试 7: 获取会话状态
    print("[测试 7] 获取会话状态")
    result = await get_session_state()
    if result.get('success'):
        state = result['state']
        print(f"✓ 会话状态键数量: {len(state)}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    print()

    # 测试 8: 清除会话状态
    print("[测试 8] 清除会话状态")
    result = await clear_session_state()
    if result.get('success'):
        print(f"✓ {result.get('message')}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    print()

    # 测试 9: 重新加载配置
    print("[测试 9] 重新加载配置")
    result = await reload_config()
    if result.get('success'):
        print(f"✓ {result.get('message')}")
    else:
        print(f"✗ 失败: {result.get('error')}")
    print()

    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
