/** URL 工具函数 */

/**
 * 从 URL 参数获取 instanceId
 */
export function getInstanceIdFromUrl(): string {
  const params = new URLSearchParams(window.location.search);
  return params.get('instanceId') || 'demo';
}

/**
 * 构建带 instanceId 的 URL
 */
export function buildUrlWithInstanceId(instanceId: string): string {
  const url = new URL(window.location.href);
  url.searchParams.set('instanceId', instanceId);
  return url.toString();
}
