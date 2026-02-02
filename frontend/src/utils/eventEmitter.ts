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
  TABLE_BUTTON_CLICK = 'TABLE_BUTTON_CLICK'
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
    params?: Record<string, unknown>;
    blockId?: string;  // 所属 block ID（用于 block 级别的 actions）
  };
}

export interface TableButtonClickEvent {
  type: EventType.TABLE_BUTTON_CLICK;
  payload: {
    buttonId: string;
    actionId?: string;
    rowData: any;
    rowIndex?: number;
    params?: Record<string, unknown>;
    blockId?: string;
    fieldKey?: string;
  };
}

export interface InstanceSwitchEvent {
  type: EventType.INSTANCE_SWITCH;
  payload: {
    instanceId: string;
  };
}

export type UIEvent = FieldChangeEvent | ActionClickEvent | InstanceSwitchEvent | TableButtonClickEvent;

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

    case EventType.TABLE_BUTTON_CLICK:
      await handleTableButtonClick(event.payload, instanceId);
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
  }, 300);
};

/**
 * 处理动作点击事件
 */
const handleActionClick = async (
  payload: ActionClickEvent['payload'],
  instanceId: string,
  schema: UISchema
): Promise<void> => {
  const { actionId, params, blockId } = payload;

  console.log('[EventEmitter] handleActionClick 被调用');
  console.log('[EventEmitter] 完整 schema:', schema);

  try {
    // 如果前端没有传 params，则从 schema 中获取所有 params
    const currentParams = params || schema.state?.params || {};

    console.log('[EventEmitter] 最终发送的 params:', currentParams);

    const response = await emitEvent('action:click', instanceId, {
      actionId,
      params: currentParams,
      blockId  // 传递 blockId 到后端
    });

    console.log('[EventEmitter] action:click 响应:', response);

    // 如果响应包含 patch，应用到 schema
    if (response.status === 'success' && response.patch) {
      const { applyPatch } = useSchemaStore.getState();
      applyPatch(response.patch, false, false);
      console.log('[EventEmitter] Patch 已应用:', response.patch);
    }

    // 如果响应包含 navigate_to，处理导航
    if (response.navigate_to) {
      const { emitInstanceSwitch } = await import('./eventEmitter');
      emitInstanceSwitch(response.navigate_to);
    }
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
 * 处理表格按钮点击事件
 */
const handleTableButtonClick = async (
  payload: TableButtonClickEvent['payload'],
  instanceId: string
): Promise<void> => {
  const { buttonId, actionId, rowData, rowIndex, params, blockId, fieldKey } = payload;

  console.log('[EventEmitter] Table button clicked:', {
    buttonId,
    actionId,
    rowIndex,
    rowData,
    params
  });

  try {
    // 构建最终参数：包含按钮配置的参数 + 行数据 + 自定义参数
    const finalParams = {
      ...params,
      rowData,           // 当前行数据
      rowIndex,          // 行索引
      fieldKey,          // 字段key（用于标识是哪个表格）
      ...(actionId ? { _actionId: actionId } : {})  // 关联的action ID
    };

    // 发送事件到后端
    const response = await emitEvent('table:button:click', instanceId, {
      buttonId,
      actionId,
      params: finalParams,
      blockId
    });

    console.log('[EventEmitter] Table button click response:', response);

    // 如果响应包含 patch，应用到 schema
    if (response.status === 'success' && response.patch) {
      const { applyPatch } = useSchemaStore.getState();
      applyPatch(response.patch, false, false);
      console.log('[EventEmitter] Patch applied:', response.patch);
    }

    // 如果响应包含 message，显示通知
    if (response.status === 'success' && response.message) {
      alert(response.message);
    }

    // 如果响应包含 navigate_to，处理导航
    if (response.navigate_to) {
      const { emitInstanceSwitch } = await import('./eventEmitter');
      emitInstanceSwitch(response.navigate_to);
    }

    // 如果响应包含确认提示
    if (response.confirm) {
      if (window.confirm(response.confirm)) {
        // 用户确认后，可能需要发送第二个请求
        if (response.confirmAction) {
          await emitEvent(response.confirmAction, instanceId, {
            buttonId,
            params: finalParams,
            confirmed: true
          });
        }
      }
    }
  } catch (err) {
    console.error('[EventEmitter] Failed to send table button click:', err);
    alert('操作失败，请重试');
  }
};

/**
 * 实例切换事件导出函数
 */
export const emitInstanceSwitch = (instanceId: string) => {
  return handleUIEvent({
    type: EventType.INSTANCE_SWITCH,
    payload: { instanceId }
  });
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
    emitActionClick: (actionId: string, params?: Record<string, unknown>) => {
      return handleUIEvent({
        type: EventType.ACTION_CLICK,
        payload: { actionId, params }
      });
    },

    // 动作点击事件（带 blockId）
    emitActionClickWithBlockId: (actionId: string, blockId?: string, params?: Record<string, unknown>) => {
      return handleUIEvent({
        type: EventType.ACTION_CLICK,
        payload: { actionId, blockId, params }
      });
    },

    // 实例切换事件
    emitInstanceSwitch,

    // 表格按钮点击事件（新增）
    emitTableButtonClick: (
      buttonId: string,
      actionId?: string,
      rowData?: any,
      rowIndex?: number,
      params?: Record<string, unknown>,
      blockId?: string,
      fieldKey?: string
    ) => {
      return handleUIEvent({
        type: EventType.TABLE_BUTTON_CLICK,
        payload: { buttonId, actionId, rowData, rowIndex, params, blockId, fieldKey }
      });
    }
  };
};