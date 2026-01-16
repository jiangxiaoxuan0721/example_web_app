/** Schema Hook */

import { useState, useEffect, useRef, useCallback } from 'react';
import type { UISchema } from '../types/schema';
import { loadSchema } from '../utils/api';
import { getInstanceIdFromUrl } from '../utils/url';

export function useSchema() {
  const [currentInstanceId, setCurrentInstanceId] = useState<string>(() => getInstanceIdFromUrl());
  const [schema, setSchema] = useState<UISchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const currentInstanceIdRef = useRef(currentInstanceId);

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
        setCurrentInstanceId(instanceId);
      }
    };

    // 监听storage事件（处理其他标签页的变化）
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === 'instanceId' && event.newValue !== currentInstanceIdRef.current) {
        console.log(`[前端] 实例ID变化 (跨标签页): ${event.newValue}`);
        setCurrentInstanceId(event.newValue || 'demo');
      }
    };

    window.addEventListener('popstate', handlePopState);
    window.addEventListener('instanceSwitch', handleInstanceSwitch as EventListener);
    window.addEventListener('storage', handleStorageChange);

    // 轮询检测 localStorage 变化（作为备用机制）
    const intervalId = setInterval(() => {
      const storedInstanceId = localStorage.getItem('instanceId');
      if (storedInstanceId && storedInstanceId !== currentInstanceIdRef.current) {
        // 使用防抖避免频繁更新
        if (debounceTimer) {
          clearTimeout(debounceTimer);
        }

        debounceTimer = setTimeout(() => {
          console.log(`[前端] 实例ID变化 (轮询检测): ${storedInstanceId}`);
          setCurrentInstanceId(storedInstanceId);
        }, 50); // 50ms 防抖
      }
    }, 200); // 降低轮询频率到每200ms一次，减少CPU占用

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
      
      const data = await loadSchema(currentInstanceId);
      console.log('[前端] Schema API 响应:', data);

      if (data.status === 'success' && data.schema) {
        setSchema(data.schema);
        console.log('[前端] Schema 加载成功:', data.schema);
      } else {
        console.error('[前端] Schema API 返回错误:', data);
        setError(data.error || '加载 Schema 失败');
      }
    } catch (err) {
      console.error('[前端] 加载 Schema 失败:', err);
      setError('加载 Schema 失败');
    } finally {
      setLoading(false);
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
    loadSchema: fetchSchema
  };
}
