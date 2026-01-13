import { UIEvent } from '../types/schema';

/**
 * 创建事件发射器
 */
export class EventEmitter {
  private listeners: Map<string, Set<Function>> = new Map();

  /**
   * 监听事件
   */
  on(eventType: string, handler: (event: UIEvent) => void): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(handler);

    // 返回取消监听函数
    return () => this.off(eventType, handler);
  }

  /**
   * 取消监听事件
   */
  off(eventType: string, handler: (event: UIEvent) => void): void {
    const handlers = this.listeners.get(eventType);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.listeners.delete(eventType);
      }
    }
  }

  /**
   * 发射事件
   */
  emit(eventType: string, payload?: any): void {
    const handlers = this.listeners.get(eventType);
    if (handlers) {
      const event: UIEvent = {
        type: eventType,
        pageKey: window.location.pathname,
        payload,
        timestamp: Date.now(),
      };
      handlers.forEach(handler => handler(event));
    }
  }

  /**
   * 清除所有监听器
   */
  clear(): void {
    this.listeners.clear();
  }
}

// 创建全局事件发射器实例
export const eventEmitter = new EventEmitter();
