/**
 * WebSocket Hook - 连接到后端 WebSocket 接收实时 Patch 推送
 */

/// <reference path="../../vite-env.d.ts" />

import { useEffect, useRef, useState, useCallback } from 'react';
import { useSchema } from './useSchema';

interface WSMessage {
  type: 'patch' | 'switch_instance';
  instance_id: string;
  patch_id?: number;
  patch?: Record<string, any>;
  schema?: Record<string, any>;
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
    const port = (import.meta.env as any).VITE_API_PORT || 8001;
    const wsUrl = `ws://localhost:${port}/ui/ws/${currentInstanceId}`;
    console.log('[WS] 连接到:', wsUrl);

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
        } else if (message.type === 'switch_instance' && message.instance_id) {
          console.log('[WS] 切换实例到:', message.instance_id);
          if (onSwitchInstanceRef.current) {
            onSwitchInstanceRef.current(message.instance_id, message.schema);
          }
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

      // 如果不是主动切换实例，则重连
      if (instanceIdRef.current === currentInstanceId) {
        console.log('[WS] 5秒后尝试重连...');
        reconnectTimerRef.current = setTimeout(() => {
          console.log('[WS] 尝试重连...');
          connect();
        }, 5000);
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
