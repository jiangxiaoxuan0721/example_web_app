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

  // 监听 URL 变化（使用轮询检测 URL 变化，添加防抖）
  useEffect(() => {
    let lastSearch = window.location.search;
    let debounceTimer: number | null = null;

    // 监听 popstate（浏览器后退/前进）
    const handlePopState = () => {
      const newSearch = window.location.search;
      if (newSearch !== lastSearch) {
        lastSearch = newSearch;
        const newInstanceId = getInstanceIdFromUrl();
        console.log(`[前端] URL 变化 (popstate): ${newInstanceId}`);
        setCurrentInstanceId(newInstanceId);
      }
    };

    window.addEventListener('popstate', handlePopState);

    // 轮询检测 URL 变化（处理链接点击等场景），使用防抖
    const intervalId = setInterval(() => {
      const currentSearch = window.location.search;
      if (currentSearch !== lastSearch) {
        lastSearch = currentSearch;
        const newInstanceId = getInstanceIdFromUrl();

        // 使用防抖避免频繁更新
        if (debounceTimer) {
          clearTimeout(debounceTimer);
        }

        debounceTimer = setTimeout(() => {
          console.log(`[前端] URL 变化 (polling): ${newInstanceId}`);
          setCurrentInstanceId(newInstanceId);
        }, 50); // 50ms 防抖
      }
    }, 50); // 每 50ms 检查一次，但实际更新会被防抖

    return () => {
      window.removeEventListener('popstate', handlePopState);
      clearInterval(intervalId);
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
    };
  }, []);

  // 加载 Schema
  const fetchSchema = useCallback(async () => {
    try {
      setLoading(true);
      console.log(`[前端] 加载 Schema (instanceId: ${currentInstanceId})...`);
      const data = await loadSchema(currentInstanceId);

      if (data.status === 'success' && data.schema) {
        setSchema(data.schema);
        console.log('[前端] Schema 加载成功:', data.schema);
      } else {
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
