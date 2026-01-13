import { useCallback, useEffect } from 'react';
import { eventEmitter } from '../utils/event';
import { UIEvent } from '../types/schema';

/**
 * 事件 Hook
 * 提供事件发射和监听功能
 */
export const useEvent = () => {
  /**
   * 发射事件
   */
  const emit = useCallback((eventType: string, payload?: any) => {
    eventEmitter.emit(eventType, payload);
  }, []);

  /**
   * 监听事件（自动清理）
   */
  const on = useCallback((eventType: string, handler: (event: UIEvent) => void) => {
    return eventEmitter.on(eventType, handler);
  }, []);

  /**
   * 监听事件 Hook（用于组件内）
   */
  const useEventListener = (eventType: string, handler: (event: UIEvent) => void) => {
    useEffect(() => {
      const cleanup = eventEmitter.on(eventType, handler);
      return cleanup;
    }, [eventType, handler]);
  };

  return {
    emit,
    on,
    useEventListener,
  };
};
