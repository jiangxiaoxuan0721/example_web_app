/** 本地存储工具函数 */

/**
 * 获取本地存储中的 instanceId
 */
export function getInstanceIdFromStorage(): string {
  try {
    const instanceId = localStorage.getItem('instanceId');
    console.log(`[URL工具] localStorage中的instanceId: ${instanceId}`);
    return instanceId || 'demo';
  } catch (err) {
    console.error('[URL工具] 从localStorage获取instanceId失败:', err);
    return 'demo'; // 返回默认值
  }
}

/**
 * 设置本地存储中的 instanceId
 */
export function setInstanceIdToStorage(instanceId: string): void {
  try {
    console.log(`[URL工具] 设置localStorage中的instanceId: ${instanceId}`);
    localStorage.setItem('instanceId', instanceId);
  } catch (err) {
    console.error('[URL工具] 设置localStorage中的instanceId失败:', err);
  }
}

/**
 * 从 URL 参数获取 instanceId（已弃用，保留用于向后兼容）
 * @deprecated 请使用 getInstanceIdFromStorage
 */
export function getInstanceIdFromUrl(): string {
  try {
    const params = new URLSearchParams(window.location.search);
    const urlInstanceId = params.get('instanceId');
    
    // 如果URL中有instanceId，迁移到localStorage并清理URL
    if (urlInstanceId) {
      console.log(`[URL工具] 从URL迁移instanceId到localStorage: ${urlInstanceId}`);
      setInstanceIdToStorage(urlInstanceId);
      // 清理URL参数
      const url = new URL(window.location.href);
      url.searchParams.delete('instanceId');
      window.history.replaceState({}, '', url.toString());
      return urlInstanceId;
    }
    
    const storageInstanceId = getInstanceIdFromStorage();
    console.log(`[URL工具] 从localStorage获取instanceId: ${storageInstanceId}`);
    return storageInstanceId;
  } catch (err) {
    console.error('[URL工具] 获取instanceId失败:', err);
    return 'demo'; // 返回默认值
  }
}

/**
 * 构建带 instanceId 的 URL（已弃用，保留用于向后兼容）
 * @deprecated 请使用 setInstanceIdToStorage
 */
export function buildUrlWithInstanceId(instanceId: string): string {
  // 不再构建URL，而是直接设置localStorage
  setInstanceIdToStorage(instanceId);
  return window.location.href;
}
