/** Schema Hook */

import { useState, useEffect } from 'react';
import type { UISchema } from '../types/schema';
import { loadSchema } from '../utils/api';
import { getInstanceIdFromUrl } from '../utils/url';

export function useSchema() {
  const [currentInstanceId, setCurrentInstanceId] = useState<string>(() => getInstanceIdFromUrl());
  const [schema, setSchema] = useState<UISchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 监听 URL 变化（使用轮询检测 URL 变化）
  useEffect(() => {
    let lastSearch = window.location.search;

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

    // 轮询检测 URL 变化（处理链接点击等场景）
    const intervalId = setInterval(() => {
      const currentSearch = window.location.search;
      if (currentSearch !== lastSearch) {
        lastSearch = currentSearch;
        const newInstanceId = getInstanceIdFromUrl();
        console.log(`[前端] URL 变化 (polling): ${newInstanceId}`);
        setCurrentInstanceId(newInstanceId);
      }
    }, 100); // 每 100ms 检查一次

    return () => {
      window.removeEventListener('popstate', handlePopState);
      clearInterval(intervalId);
    };
  }, []);

  // 加载 Schema
  useEffect(() => {
    const fetchSchema = async () => {
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
    };

    fetchSchema();
  }, [currentInstanceId]);

  return {
    currentInstanceId,
    schema,
    loading,
    error
  };
}
