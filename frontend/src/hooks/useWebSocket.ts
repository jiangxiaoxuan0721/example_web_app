/**
 * WebSocket Hook - 连接到后端 WebSocket 接收实时 Patch 推送
 */

/// <reference path="../../vite-env.d.ts" />

import { useEffect, useRef, useState, useCallback } from 'react';
import { useSchema } from './useSchema';

interface WSMessage {
  highlight: any;
  type: 'patch' | 'switch_instance' | 'schema_update' | 'access_instance';
  instance_name: string;
  patch_id?: number;
  patch?: Record<string, any>;
  schema?: Record<string, any> & { highlight?: any };
  redirect_url?: string;
}

export function useWebSocket(onPatch: (patch: Record<string, any>) => void, onSwitchInstance?: (instanceId: string, schema?: Record<string, any>) => void) {
  const { currentInstanceId } = useSchema();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const onPatchRef = useRef(onPatch);
  const onSwitchInstanceRef = useRef(onSwitchInstance);
  const instanceIdRef = useRef(currentInstanceId);
  const [connected, setConnected] = useState(false);

  // 始终保持 onPatchRef 和 onSwitchInstanceRef 的最新值
  useEffect(() => {
    onPatchRef.current = onPatch;
    onSwitchInstanceRef.current = onSwitchInstance;
  }, [onPatch, onSwitchInstance]);

  // 连接函数
  const connect = useCallback(() => {
    if (!currentInstanceId) return;

    // 如果 instanceId 没变，不需要重连
    if (instanceIdRef.current === currentInstanceId && wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('[WS] instanceId 未变化，保持现有连接');
      return;
    }

    // 关闭现有连接
    if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
      console.log('[WS] 关闭旧连接');
      wsRef.current.close();
    }

    // 连接到 WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ui/ws/${currentInstanceId}`;
    console.log('[WS] 连接到:', wsUrl);

    // 使用快速连接模式
    wsRef.current = new WebSocket(wsUrl);
    instanceIdRef.current = currentInstanceId;

    wsRef.current.onopen = () => {
      console.log('[WS] 已连接到服务器');
      setConnected(true);
      // 清除重连定时器
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    wsRef.current.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);
        console.log('[WS] 收到消息:', message);

        if (message.type === 'patch' && message.patch) {
          console.log('[WS] 应用 Patch:', message.patch);
          onPatchRef.current(message.patch);
        } else if (message.type === 'schema_update' && message.schema) {
          // 直接设置整个schema，适用于add操作后的更新
          if (onSwitchInstanceRef.current) {
            // 将 highlight 信息附加到 schema 对象上，以便 App.tsx 可以访问
            const schemaWithHighlight = { ...message.schema, highlight: message.highlight };
            onSwitchInstanceRef.current(instanceIdRef.current, schemaWithHighlight);
          }

          // 检查是否有跳转链接
          if (message.redirect_url) {
            console.log('[WS] 跳转到:', message.redirect_url);
            window.location.href = message.redirect_url;
          }
        } else if (message.type === 'switch_instance' && message.instance_name) {
          console.log('[WS] 切换实例到:', message.instance_name);
          if (onSwitchInstanceRef.current) {
            // switch_instance 不再返回 schema，前端需要通过 API 获取
            onSwitchInstanceRef.current(message.instance_name, undefined);
          }
        } else if (message.type === 'access_instance' && message.instance_name) {
          console.log('[WS] 访问实例:', message.instance_name);
          // 构建URL
          const url = new URL(window.location.href);
          url.searchParams.set('instanceId', message.instance_name);
          window.location.href = url.toString();
        }
      } catch (err) {
        console.error('[WS] 解析消息失败:', err);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('[WS] 错误:', error);
      setConnected(false);
    };

    wsRef.current.onclose = () => {
      console.log('[WS] 连接已断开');
      setConnected(false);

      // 如果不是主动切换实例，则快速重连
      if (instanceIdRef.current === currentInstanceId) {
        console.log('[WS] 1秒后尝试重连...');
        reconnectTimerRef.current = setTimeout(() => {
          console.log('[WS] 尝试重连...');
          connect();
        }, 1000); // 减少重连延迟
      }
    };
  }, [currentInstanceId]);

  // 当 instanceId 改变时重连
  useEffect(() => {
    connect();

    return () => {
      // 清理连接和定时器
      if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
        console.log('[WS] 清理：关闭连接');
        wsRef.current.close();
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      // 重置连接状态
      setConnected(false);
    };
  }, [connect]);

  return {
    connected,
  };
}
