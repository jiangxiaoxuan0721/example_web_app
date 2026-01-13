/**
 * MCP Hook
 * 提供 MCP 相关的 React Hooks
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { mcpClient } from '../utils/mcpClient';

export function useMCPConnection(autoConnect: boolean = true) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(async () => {
    try {
      setIsConnecting(true);
      setError(null);
      await mcpClient.connect('ws://localhost:8765');
      setIsConnected(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '连接失败');
      setIsConnected(false);
    } finally {
      setIsConnecting(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    mcpClient.disconnect();
    setIsConnected(false);
  }, []);

  // 自动连接
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    isConnected,
    isConnecting,
    error,
    connect,
    disconnect,
    sendCommand: mcpClient.sendCommand.bind(mcpClient),
    sendEvent: mcpClient.sendEvent.bind(mcpClient)
  };
}

export function useMCPEvent(eventType: string, callback: (data: any) => void) {
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  useEffect(() => {
    const unsubscribe = mcpClient.on(eventType, (data) => {
      callbackRef.current(data);
    });

    return unsubscribe;
  }, [eventType]);
}

export function useMCPCommand() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendCommand = useCallback(async (action: string, params: Record<string, any> = {}) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await mcpClient.sendCommand(action, params);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '命令执行失败';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    sendCommand,
    isLoading,
    error
  };
}
