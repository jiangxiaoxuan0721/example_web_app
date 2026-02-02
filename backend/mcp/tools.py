"""
MCP Tools for Agent Programmable UI Runtime
此文件现在作为入口点，导入并运行MCP工具。
工具定义在tool_definitions.py中，实现在tool_implements.py中。
"""

# 导入MCP服务器实例和工具定义
from backend.mcp.tool_definitions import mcp

# 启动MCP服务器（用于本地测试）
if __name__ == "__main__":
    print("🚀 Starting MCP Server for UI Patch Tool...")
    print("📝 Available tools:")
    print("  - patch_ui_state: Apply structured patches to modify UI (with field operation shortcuts)")
    print("  - get_schema: Get current UI Schema")
    print("  - list_instances: list all available instances")
    print("  - access_instance: Access a specific UI instance and mark it as active")
    print("  - validate_completion: Check if UI meets completion criteria (semantic control)")
    print()
    mcp.run(
        transport="streamable-http",
        port=8766,
        host="0.0.0.0",
        path="/mcp",
    )