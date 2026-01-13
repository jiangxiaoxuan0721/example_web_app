/**
 * MCP WebSocket 客户端
 * 用于与后端 MCP 服务器通信
 */

interface MCPMessage {
  id?: string;
  action?: string;
  params?: Record<string, any>;
  type?: string;
  payload?: Record<string, any>;
  pageKey?: string;
}

export class MCPClient {
  private ws: WebSocket | null = null;
  private pendingRequests: Map<string, {
    resolve: (value: any) => void;
    reject: (reason: any) => void;
    timeout: ReturnType<typeof setTimeout>;
  }> = new Map();
  private requestCounter = 0;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private eventListeners: Map<string, ((data: any) => void)[]> = new Map();

  /**
   * 连接到 MCP WebSocket 服务器
   */
  connect(url: string = 'ws://localhost:8765'): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          console.log('[MCP Client] 已连接到服务器');
          this.reconnectAttempts = 0;
          
          // 发送客户端信息
          this.ws?.send(JSON.stringify({
            type: 'client_info',
            client: 'schema-ui-frontend',
            version: '1.0.0'
          }));
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data: MCPMessage = JSON.parse(event.data);
            
            // 判断是响应还是事件
            if (data.id) {
              // 处理响应
              this.handleResponse(data);
            } else if (data.type) {
              // 处理事件
              this.handleEvent(data);
            }
          } catch (error) {
            console.error('[MCP Client] 解析消息失败:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('[MCP Client] 连接已关闭');
          this.cleanup();
          
          // 自动重连
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
              this.reconnectAttempts++;
              console.log(`[MCP Client] 尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
              this.connect(url).catch(console.error);
            }, this.reconnectDelay);
          }
        };

        this.ws.onerror = (error) => {
          console.error('[MCP Client] 连接错误:', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.cleanup();
  }

  /**
   * 清理资源
   */
  private cleanup(): void {
    // 清理所有待处理请求
    this.pendingRequests.forEach(({ reject, timeout }) => {
      clearTimeout(timeout);
      reject(new Error('连接已断开'));
    });
    this.pendingRequests.clear();
  }

  /**
   * 发送命令并等待响应
   */
  async sendCommand(action: string, params: Record<string, any> = {}, timeout: number = 10000): Promise<any> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket 未连接');
    }

    this.requestCounter++;
    const requestId = `mcp_${this.requestCounter.toString().padStart(6, '0')}`;

    const message: MCPMessage = {
      id: requestId,
      action,
      params
    };

    return new Promise((resolve, reject) => {
      const timeoutHandle = setTimeout(() => {
        this.pendingRequests.delete(requestId);
        reject(new Error(`命令超时: ${action}`));
      }, timeout);

      this.pendingRequests.set(requestId, {
        resolve,
        reject,
        timeout: timeoutHandle
      });

      this.ws?.send(JSON.stringify(message));
      console.log(`[MCP Client] 发送命令: ${action} (ID: ${requestId})`);
    });
  }

  /**
   * 发送前端事件到 MCP
   */
  sendEvent(eventType: string, payload: Record<string, any>, pageKey?: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[MCP Client] WebSocket 未连接，无法发送事件');
      return;
    }

    const message: MCPMessage = {
      type: eventType,
      payload,
      pageKey
    };

    this.ws.send(JSON.stringify(message));
    console.log(`[MCP Client] 发送事件: ${eventType}`);
  }

  /**
   * 处理服务器响应
   */
  private handleResponse(data: MCPMessage): void {
    const requestId = data.id;
    if (!requestId) return;
    
    const pending = this.pendingRequests.get(requestId);
    
    if (pending) {
      clearTimeout(pending.timeout);
      this.pendingRequests.delete(requestId);
      
      if ((data as any).success) {
        pending.resolve(data);
      } else {
        pending.reject(new Error((data as any).error || '命令执行失败'));
      }
    }
  }

  /**
   * 处理服务器发送的事件
   */
  private handleEvent(data: MCPMessage): void {
    const eventType = data.type;
    if (!eventType) return;
    
    // 触发对应的事件监听器
    const listeners = this.eventListeners.get(eventType) || [];
    listeners.forEach(listener => {
      try {
        listener(data);
      } catch (error) {
        console.error(`[MCP Client] 事件监听器错误 (${eventType}):`, error);
      }
    });
  }

  /**
   * 注册事件监听器
   */
  on(eventType: string, callback: (data: any) => void): () => void {
    if (!this.eventListeners.has(eventType)) {
      this.eventListeners.set(eventType, []);
    }
    
    this.eventListeners.get(eventType)!.push(callback);
    
    // 返回取消监听的函数
    return () => {
      const listeners = this.eventListeners.get(eventType);
      if (listeners) {
        const index = listeners.indexOf(callback);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      }
    };
  }

  /**
   * 获取连接状态
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// 导出单例实例
export const mcpClient = new MCPClient();
