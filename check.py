"""服务连接诊断工具"""

import asyncio
import httpx
import os
import sys

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "localhost")
FASTAPI_PORT = os.getenv("FASTAPI_PORT", "8001")
FASTAPI_BASE_URL = f"http://{FASTAPI_HOST}:{FASTAPI_PORT}"


async def check_fastapi_health():
    """检查 FastAPI 健康状态"""
    print(f"🔍 检查 FastAPI 健康状态: {FASTAPI_BASE_URL}/health")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FASTAPI_BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FastAPI 正常运行")
                print(f"   响应: {data}")
                return True
            else:
                print(f"❌ FastAPI 返回异常状态码: {response.status_code}")
                return False
    except httpx.ConnectError as e:
        print(f"❌ 无法连接到 FastAPI")
        print(f"   错误: {str(e)}")
        print(f"   提示: 请确保 FastAPI 运行在 {FASTAPI_BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return False


async def check_schema_endpoint():
    """检查 Schema 端点"""
    print(f"\n🔍 检查 Schema 端点: {FASTAPI_BASE_URL}/ui/schema")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FASTAPI_BASE_URL}/ui/schema", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Schema 端点正常")
                print(f"   实例: {data.get('meta', {}).get('pageKey', 'unknown')}")
                return True
            else:
                print(f"❌ Schema 端点返回异常状态码: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


async def check_patch_endpoint():
    """检查 Patch 端点"""
    print(f"\n🔍 检查 Patch 端点: {FASTAPI_BASE_URL}/ui/patch")
    try:
        async with httpx.AsyncClient() as client:
            # 发送测试 patch
            payload = {
                "instance_id": "demo",
                "patches": [
                    {
                        "op": "set",
                        "path": "state.params.test",
                        "value": "診断测试"
                    }
                ]
            }
            response = await client.post(
                f"{FASTAPI_BASE_URL}/ui/patch",
                json=payload,
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Patch 端点正常")
                print(f"   响应: {data}")
                return True
            else:
                print(f"❌ Patch 端点返回异常状态码: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


async def check_instances_endpoint():
    """检查实例列表端点"""
    print(f"\n🔍 检查实例列表: {FASTAPI_BASE_URL}/ui/instances")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FASTAPI_BASE_URL}/ui/instances", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 实例列表端点正常")
                print(f"   可用实例: {data.get('instances', [])}")
                return True
            else:
                print(f"❌ 实例列表端点返回异常状态码: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


async def main():
    """运行所有诊断"""
    print("=" * 60)
    print("🏥 FastAPI 服务诊断工具")
    print("=" * 60)
    print(f"目标地址: {FASTAPI_BASE_URL}")
    print()

    results = []
    
    # 运行诊断
    results.append(("健康检查", await check_fastapi_health()))
    results.append(("Schema 端点", await check_schema_endpoint()))
    results.append(("Patch 端点", await check_patch_endpoint()))
    results.append(("实例列表", await check_instances_endpoint()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 诊断结果汇总")
    print("=" * 60)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("🎉 所有检查通过！MCP 应该能够正常连接到 FastAPI")
        return 0
    else:
        print("⚠️  部分检查失败，请修复后再试")
        print()
        print("💡 常见问题:")
        print("  1. FastAPI 是否已启动？运行: python -m uvicorn backend.fastapi.main:app")
        print("  2. 端口是否正确？检查环境变量 FASTAPI_PORT")
        print("  3. 防火墙是否阻止？检查本地防火墙设置")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)