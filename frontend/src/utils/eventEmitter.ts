/** 事件发射器 - 统一事件流 */

import { useSchemaStore } from '../store/schemaStore';
import { UISchema } from '../types/schema';
import { emitEvent } from './api';

// 防抖定时器存储
const debounceTimers: Record<string, number> = {};

// 事件类型定义
export enum EventType {
  FIELD_CHANGE = 'FIELD_CHANGE',
  ACTION_CLICK = 'ACTION_CLICK',
  INSTANCE_SWITCH = 'INSTANCE_SWITCH',
}

// 事件载荷接口
export interface FieldChangeEvent {
  type: EventType.FIELD_CHANGE;
  payload: {
    fieldKey: string;
    value: any;
    bindPath: string;
  };
}

export interface ActionClickEvent {
  type: EventType.ACTION_CLICK;
  payload: {
    actionId: string;
    params?: Record<string, any>;
  };
}

export interface InstanceSwitchEvent {
  type: EventType.INSTANCE_SWITCH;
  payload: {
    instanceId: string;
  };
}

export type UIEvent = FieldChangeEvent | ActionClickEvent | InstanceSwitchEvent;

/**
 * 事件处理函数 - 统一处理所有UI事件
 */
export const handleUIEvent = async (event: UIEvent): Promise<void> => {
  const { schema } = useSchemaStore.getState();
  const { instanceId } = useSchemaStore.getState();
  
  if (!schema || !instanceId) {
    console.warn('[EventEmitter] Schema or instanceId is missing');
    return;
  }
  
  console.log('[EventEmitter] Handling event:', event);
  
  switch (event.type) {
    case EventType.FIELD_CHANGE:
      await handleFieldChange(event.payload, instanceId);
      break;
      
    case EventType.ACTION_CLICK:
      await handleActionClick(event.payload, instanceId, schema);
      break;
      
    case EventType.INSTANCE_SWITCH:
      await handleInstanceSwitch(event.payload);
      break;
      
    default:
      console.warn('[EventEmitter] Unknown event type:', (event as any).type);
  }
};

/**
 * 处理字段变更事件
 */
const handleFieldChange = async (
  payload: FieldChangeEvent['payload'],
  instanceId: string
): Promise<void> => {
  const { fieldKey, value, bindPath } = payload;
  
  // 创建唯一键来标识这个字段实例
  const timerKey = `${instanceId}-${fieldKey}`;
  
  // 清除之前的定时器
  if (debounceTimers[timerKey]) {
    clearTimeout(debounceTimers[timerKey]);
  }
  
  // 设置新的防抖定时器（300ms）
  debounceTimers[timerKey] = window.setTimeout(async () => {
    try {
      // 发送事件到后端
      await emitEvent('field:change', instanceId, {
        fieldKey,
        value,
        bindPath
      });
      
      // 后端会通过WebSocket推送patch，不需要本地乐观更新
      console.log(`[EventEmitter] Field change sent: ${fieldKey} = ${value}`);
    } catch (err) {
      console.error('[EventEmitter] Failed to send field change:', err);
    } finally {
      // 清除定时器记录
      delete debounceTimers[timerKey];
    }
  }, 750);
};

/**
 * 处理动作点击事件
 */
const handleActionClick = async (
  payload: ActionClickEvent['payload'],
  instanceId: string,
  schema: UISchema
): Promise<void> => {
  const { actionId, params } = payload;
  
  try {
    // 发送事件到后端，携带当前所有params
    const currentParams = schema.state?.params || {};
    
    await emitEvent('action:click', instanceId, {
      actionId,
      params: params || currentParams
    });
    
    console.log(`[EventEmitter] Action click sent: ${actionId}`);
  } catch (err) {
    console.error('[EventEmitter] Failed to send action click:', err);
  }
};

/**
 * 处理实例切换事件
 */
const handleInstanceSwitch = async (
  payload: InstanceSwitchEvent['payload']
): Promise<void> => {
  const { instanceId } = payload;
  
  // 更新localStorage而不是URL
  localStorage.setItem('instanceId', instanceId);
  
  // 触发自定义事件通知useSchema钩子
  window.dispatchEvent(new CustomEvent('instanceSwitch', { detail: { instanceId } }));
  
  console.log(`[EventEmitter] Instance switch to: ${instanceId}`);
};

/**
 * React Hook - 创建事件发射器
 */
export const useEventEmitter = () => {
  return {
    // 字段变更事件
    emitFieldChange: (fieldKey: string, value: any, bindPath?: string) => {
      return handleUIEvent({
        type: EventType.FIELD_CHANGE,
        payload: { fieldKey, value, bindPath: bindPath || 'state.params' }
      });
    },
    
    // 动作点击事件
    emitActionClick: (actionId: string, params?: Record<string, any>) => {
      return handleUIEvent({
        type: EventType.ACTION_CLICK,
        payload: { actionId, params }
      });
    },
    
    // 实例切换事件
    emitInstanceSwitch: (instanceId: string) => {
      return handleUIEvent({
        type: EventType.INSTANCE_SWITCH,
        payload: { instanceId }
      });
    }
  };
};