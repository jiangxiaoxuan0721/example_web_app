/** Schema Hook */

import { useState, useEffect, useRef, useCallback } from 'react';
import type { UISchema } from '../types/schema';
import { loadSchema, preloadSchemas, clearSchemaCache } from '../utils/api';
import { getInstanceIdFromUrl } from '../utils/url';

export function useSchema() {
  const [currentInstanceId, setCurrentInstanceId] = useState<string>(() => getInstanceIdFromUrl());
  const [schema, setSchema] = useState<UISchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingText, setLoadingText] = useState<string>('加载中...');
  const currentInstanceIdRef = useRef(currentInstanceId);
  const initializedRef = useRef(false); // 标记是否已初始化

  // 更新 ref
  useEffect(() => {
    currentInstanceIdRef.current = currentInstanceId;
  }, [currentInstanceId]);

  // 监听 localStorage 变化、URL 迁移和自定义事件
  useEffect(() => {
    let debounceTimer: number | null = null;

    // 监听 popstate（浏览器后退/前进，用于处理旧的URL）
    const handlePopState = () => {
      const newInstanceId = getInstanceIdFromUrl(); // 这会检查并迁移URL中的instanceId
      if (newInstanceId !== currentInstanceIdRef.current) {
        console.log(`[前端] 实例ID变化 (popstate): ${newInstanceId}`);
        setCurrentInstanceId(newInstanceId);
      }
    };

    // 监听自定义实例切换事件
    const handleInstanceSwitch = (event: CustomEvent) => {
      const { instanceId } = event.detail;
      if (instanceId !== currentInstanceIdRef.current) {
        console.log(`[前端] 实例ID变化 (自定义事件): ${instanceId}`);
        setLoadingText('切换实例中...');
        setCurrentInstanceId(instanceId);
      }
    };

    // 监听storage事件（处理其他标签页的变化）
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === 'instanceId' && event.newValue !== currentInstanceIdRef.current) {
        console.log(`[前端] 实例ID变化 (跨标签页): ${event.newValue}`);
        setLoadingText('切换实例中...');
        setCurrentInstanceId(event.newValue || 'demo');
      }
    };

    window.addEventListener('popstate', handlePopState);
    window.addEventListener('instanceSwitch', handleInstanceSwitch as EventListener);
    window.addEventListener('storage', handleStorageChange);

    // 降低轮询频率，减少CPU占用
    const intervalId = setInterval(() => {
      const storedInstanceId = localStorage.getItem('instanceId');
      if (storedInstanceId && storedInstanceId !== currentInstanceIdRef.current) {
        // 使用防抖避免频繁更新
        if (debounceTimer) {
          clearTimeout(debounceTimer);
        }

        debounceTimer = setTimeout(() => {
          console.log(`[前端] 实例ID变化 (轮询检测): ${storedInstanceId}`);
          setLoadingText('切换实例中...');
          setCurrentInstanceId(storedInstanceId);
        }, 50); // 50ms 防抖
      }
    }, 500); // 降低轮询频率到每500ms一次

    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('instanceSwitch', handleInstanceSwitch as EventListener);
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(intervalId);
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
    };
  }, []); // 移除 currentInstanceId 依赖，使用 ref 来避免无限循环

  // 加载 Schema
  const fetchSchema = useCallback(async () => {
    try {
      setLoading(true);
      console.log(`[前端] 加载 Schema (instanceId: ${currentInstanceId})...`);

      // 检查 instanceId 是否有效
      if (!currentInstanceId) {
        console.error('[前端] instanceId 为空');
        setError('instanceId 为空');
        setLoading(false);
        return;
      }

      // 如果不是第一次加载，显示更具体的加载状态
      if (initializedRef.current) {
        setLoadingText('切换实例中...');
      } else {
        setLoadingText('加载中...');
      }

      const data = await loadSchema(currentInstanceId);
      console.log('[前端] Schema API 响应:', data);

      if (data.status === 'success' && data.schema) {
        setSchema(data.schema);
        console.log('[前端] Schema 加载成功:', data.schema);

        // 如果是第一次加载，预加载其他实例
        if (!initializedRef.current) {
          initializedRef.current = true;
          // 获取所有可用实例
          try {
            const instancesResponse = await fetch('/ui/instances');
            const instancesData = await instancesResponse.json();
            if (instancesData.status === 'success' && instancesData.instances) {
              const instanceIds = instancesData.instances
                .map((inst: any) => inst.instance_id)
                .filter((id: string) => id !== currentInstanceId);

              // 预加载其他实例（不等待完成）
              if (instanceIds.length > 0) {
                console.log(`[前端] 预加载其他实例: ${instanceIds.join(', ')}`);
                preloadSchemas(instanceIds);
              }
            }
          } catch (error) {
            console.warn('[前端] 预加载其他实例失败:', error);
          }
        }
      } else {
        console.error('[前端] Schema API 返回错误:', data);
        setError(data.error || '加载 Schema 失败');
      }
    } catch (err) {
      console.error('[前端] 加载 Schema 失败:', err);
      setError('加载 Schema 失败');
    } finally {
      setLoading(false);
      setLoadingText('加载中...');
    }
  }, [currentInstanceId]);

  useEffect(() => {
    fetchSchema();
  }, [fetchSchema]);

  return {
    currentInstanceId,
    schema,
    loading,
    error,
    loadingText,
    clearCache: clearSchemaCache,
    loadSchema: fetchSchema
  };
}
