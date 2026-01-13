"""
MCP 服务器主程序
提供 WebSocket 服务器和 MCP HTTP 服务器
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional
import websockets
from websockets.asyncio.server import ServerConnection
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from .mcp_tools import mcp, tool_registry

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ===========================
# WebSocket 连接管理
# ===========================
class BrowserConnectionManager:
    """管理与前端浏览器客户端的 WebSocket 连接"""

    def __init__(self):
        self.client: Optional[ServerConnection] = None
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.request_counter = 0
        self.event_queue: asyncio.Queue = asyncio.Queue()

    def is_connected(self) -> bool:
        """检查是否有活跃连接"""
        return self.client is not None

    def next_request_id(self) -> str:
        """生成请求 ID"""
        self.request_counter += 1
        return f"mcp_{self.request_counter:06d}"

    async def send_command(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送命令到浏览器并等待响应"""
        if not self.is_connected():
            return {
                "success": False,
                "error": "前端未连接"
            }

        request_id = self.next_request_id()
        command = {
            "id": request_id,
            "action": action,
            "params": params
        }

        future = asyncio.Future()
        self.pending_requests[request_id] = future

        try:
            if self.client is not None:
                await self.client.send(json.dumps(command, ensure_ascii=False))
                logger.info(f"[WS] 发送: {action} (ID: {request_id})")
            else:
                return {"success": False, "error": "前端未连接"}

            timeout = params.get("timeout", 30) if action == "tool:await_event" else 10
            response = await asyncio.wait_for(future, timeout=timeout)
            return response

        except asyncio.TimeoutError:
            logger.error(f"[WS] 命令超时: {action}")
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            logger.error(f"[WS] 发送失败: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.pending_requests.pop(request_id, None)

    async def handle_response(self, response_data: dict):
        """处理浏览器返回的响应"""
        request_id = response_data.get("id")
        if request_id and request_id in self.pending_requests:
            future = self.pending_requests[request_id]
            if not future.done():
                future.set_result(response_data)
                logger.info(f"[WS] 收到响应: {request_id}")

    async def handle_event(self, event_data: dict):
        """处理前端发送的事件"""
        logger.info(f"[WS] 收到事件: {event_data.get('type')}")
        await self.event_queue.put(event_data)

    async def wait_for_event(self, timeout: int = 30) -> Dict[str, Any]:
        """等待前端事件"""
        try:
            event = await asyncio.wait_for(self.event_queue.get(), timeout=timeout)
            logger.info(f"[WS] 返回事件: {event.get('type')}")
            return {
                "success": True,
                "event": event
            }
        except asyncio.TimeoutError:
            logger.error(f"[WS] 等待事件超时")
            return {"success": False, "error": "等待事件超时"}

    async def handle_client(self, websocket: ServerConnection):
        """处理浏览器客户端连接"""
        client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"

        if self.client is not None:
            logger.warning(f"[WS] 断开旧连接")
            try:
                await self.client.close()
            except:
                pass

        self.client = websocket
        logger.info(f"[WS] 浏览器已连接: {client_addr}")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # 判断是响应还是事件
                    if "id" in data:
                        await self.handle_response(data)
                    elif "type" in data:
                        await self.handle_event(data)
                    else:
                        logger.warning(f"[WS] 未知消息格式: {data}")
                        
                except json.JSONDecodeError:
                    logger.error(f"[WS] 无效 JSON: {message}")
                except Exception as e:
                    logger.error(f"[WS] 处理消息错误: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"[WS] 浏览器断开: {client_addr}")
        except Exception as e:
            logger.error(f"[WS] 连接错误: {e}", exc_info=True)
        finally:
            if self.client == websocket:
                self.client = None
                for future in self.pending_requests.values():
                    if not future.done():
                        future.set_result({"success": False, "error": "连接已断开"})
                self.pending_requests.clear()


# 全局连接管理器
browser_manager = BrowserConnectionManager()

# 设置到工具注册表
tool_registry.set_connection_manager(browser_manager)


async def start_websocket_server(host: str = "0.0.0.0", port: int = 8765):
    """启动 WebSocket 服务器"""
    async with websockets.serve(browser_manager.handle_client, host, port):
        logger.info(f"🌐 WebSocket 服务器启动: ws://{host}:{port}")
        logger.info("⏳ 等待前端连接...")
        await asyncio.Future()


async def main():
    """主函数：同时启动 WebSocket 和 MCP 服务器"""
    logger.info("🚀 MCP Server 启动中...")

    ws_task = asyncio.create_task(start_websocket_server(host="0.0.0.0", port=8765))
    await asyncio.sleep(0.5)

    logger.info("🎯 MCP HTTP 服务器启动: http://0.0.0.0:4445/mcp")

    loop = asyncio.get_event_loop()
    mcp_task = loop.run_in_executor(
        None,
        lambda: mcp.run(
            transport="sse",
            host="0.0.0.0",
            port=4445,
            path="/mcp",
        )
    )

    await asyncio.gather(ws_task, mcp_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⛔ 服务器关闭")
