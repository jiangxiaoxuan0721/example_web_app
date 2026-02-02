/** API 工具函数 */

// 导入 multiInstanceStore（在模块顶层导入，避免循环依赖）
import { useMultiInstanceStore } from '../store/multiInstanceStore';

// Schema缓存，加速实例切换
const schemaCache = new Map<string, any>();
const CACHE_TTL = 5 * 60 * 1000; // 5分钟缓存
const cacheTimestamps = new Map<string, number>();

/**
 * 加载 Schema（带缓存）
 * @param instanceId - 实例 ID
 * @returns Schema 响应
 */
export async function loadSchema(instanceId: string) {
  // 检查缓存
  const now = Date.now();
  const cachedTimestamp = cacheTimestamps.get(instanceId);
  const cachedSchema = schemaCache.get(instanceId);

  if (cachedSchema && cachedTimestamp && (now - cachedTimestamp < CACHE_TTL)) {
    console.log(`[API] 从缓存加载 Schema，instanceId: ${instanceId}`);
    return {
      status: 'success',
      instance_name: instanceId,
      schema: cachedSchema
    };
  }

  console.log(`[API] 从服务器加载 Schema，instanceId: ${instanceId}`);
  const url = `/ui/schema?instanceId=${instanceId}`;
  console.log(`[API] 请求 URL: ${url}`);

  try {
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000); // 3秒超时

    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Cache-Control': 'no-cache',
      }
    });
    clearTimeout(timeoutId);

    console.log(`[API] 响应状态: ${response.status}`);

    if (!response.ok) {
      console.error(`[API] 响应错误: ${response.status} ${response.statusText}`);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log(`[API] 响应数据:`, data);

    // 更新缓存
    if (data.status === 'success' && data.schema) {
      schemaCache.set(instanceId, data.schema);
      cacheTimestamps.set(instanceId, now);
    }

    return data;
  } catch (error) {
    console.error(`[API] 请求失败:`, error);
    // 如果请求失败但有缓存，返回缓存数据
    if (cachedSchema) {
      console.log(`[API] 请求失败，使用缓存数据，instanceId: ${instanceId}`);
      return {
        status: 'success',
        instance_name: instanceId,
        schema: cachedSchema,
        cached: true // 标记为缓存数据
      };
    }
    throw error;
  }
}

/**
 * 预加载所有实例的Schema并保存到多实例Store
 * @param instanceIds - 实例ID列表
 * @returns Promise
 */
export async function preloadSchemas(instanceIds: string[]) {
  console.log(`[API] 预加载实例Schemas: ${instanceIds.join(', ')}`);
  const promises = instanceIds.map(async (id) => {
    try {
      const result = await loadSchema(id);
      if (result.status === 'success' && result.schema) {
        // 保存到 multiInstanceStore
        const setInstance = useMultiInstanceStore.getState().setInstance;
        setInstance(id, result.schema);
        console.log(`[API] 预加载并保存实例: ${id}`);
      }
      return result;
    } catch (error) {
      console.error(`[API] 预加载实例 ${id} 失败:`, error);
      return null;
    }
  });

  try {
    await Promise.all(promises);
    console.log(`[API] 预加载完成`);
  } catch (error) {
    console.error(`[API] 预加载过程中出错:`, error);
  }
}

/**
 * 清除Schema缓存
 * @param instanceId - 可选，指定实例ID，不指定则清除所有
 */
export function clearSchemaCache(instanceId?: string) {
  if (instanceId) {
    schemaCache.delete(instanceId);
    cacheTimestamps.delete(instanceId);
  } else {
    schemaCache.clear();
    cacheTimestamps.clear();
  }
}

/**
 * 发送事件
 * @param eventType - 事件类型
 * @param instanceId - 实例 ID
 * @param payload - 事件载荷
 * @returns 事件响应
 */
export async function emitEvent(eventType: string, instanceId: string, payload: any) {
  const response = await fetch('/ui/event', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type: eventType,
      pageKey: instanceId,
      payload,
    }),
  });
  return await response.json();
}

/**
 * 加载 Patch 历史记录
 * @param instanceId - 实例 ID
 * @returns Patch 历史记录
 */
export async function loadPatchHistory(instanceId: string) {
  const response = await fetch(`/ui/patches?instanceId=${instanceId}`);
  const data = await response.json();
  return data.status === 'success' ? data.patches : [];
}

/**
 * 重放 Patch
 * @param patchId - Patch ID
 * @param instanceId - 实例 ID
 * @returns Patch 响应
 */
export async function replayPatch(patchId: number, instanceId: string) {
  const response = await fetch(`/ui/patches/replay/${patchId}?instanceId=${instanceId}`);
  return await response.json();
}
