/** API 工具函数 */

/**
 * 加载 Schema
 * @param instanceId - 实例 ID
 * @returns Schema 响应
 */
export async function loadSchema(instanceId: string) {
  const response = await fetch(`/ui/schema?instanceId=${instanceId}`);
  return await response.json();
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
