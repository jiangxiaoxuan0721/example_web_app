# 表格按钮架构改进文档

## 问题分析

### 原有架构的问题

1. **事件处理不统一**
   - 全局按钮（block级别）使用 `ActionButton` 组件
   - 表格按钮（row级别）只是打印日志，没有实际功能

2. **扩展性差**
   - 按钮配置硬编码，难以支持复杂场景
   - 无法直接调用后端action
   - 缺少确认对话框等交互功能

3. **代码重复**
   - 事件处理逻辑分散在多个地方
   - 没有统一的事件流

## 改进方案

### 1. 统一事件系统

在 `eventEmitter.ts` 中新增 `TABLE_BUTTON_CLICK` 事件类型：

```typescript
export enum EventType {
  FIELD_CHANGE = 'FIELD_CHANGE',
  ACTION_CLICK = 'ACTION_CLICK',
  INSTANCE_SWITCH = 'INSTANCE_SWITCH',
  TABLE_BUTTON_CLICK = 'TABLE_BUTTON_CLICK'  // 新增
}

export interface TableButtonClickEvent {
  type: EventType.TABLE_BUTTON_CLICK;
  payload: {
    buttonId: string;
    actionId?: string;
    rowData: any;
    rowIndex: number;
    params?: Record<string, unknown>;
    blockId?: string;
    fieldKey?: string;
  };
}
```

### 2. 扩展按钮配置接口

表格按钮支持以下配置：

```typescript
interface TableButtonConfig {
  // 基础配置
  type: 'button';
  id: string;              // 按钮唯一标识
  buttonLabel: string;      // 按钮文本
  buttonStyle?: 'primary' | 'secondary' | 'danger';
  buttonSize?: 'small' | 'medium' | 'large';
  margin?: string;
  tooltip?: string;         // 鼠标悬停提示

  // 事件配置
  actionId?: string;        // 关联到schema中的action ID
  params?: Record<string, any>;  // 自定义参数

  // 交互配置
  confirmMessage?: string;  // 确认对话框消息
}
```

### 3. 后端处理

后端需要监听 `table:button:click` 事件：

```python
@app.post("/ui/event")
async def handle_table_button_click(
    instance_id: str,
    button_id: str,
    action_id: Optional[str],
    params: dict
):
    # params 包含：
    # - rowData: 当前行数据
    # - rowIndex: 行索引
    # - fieldKey: 表格字段key
    # - _actionId: 关联的action ID
    # - 自定义参数

    # 处理逻辑：
    # 1. 如果有 actionId，执行对应的action
    # 2. 否则，根据 buttonId 执行自定义逻辑

    return {
        "status": "success",
        "message": "操作成功",  # 可选：显示提示
        "patch": { ... },       # 可选：更新state
        "navigate_to": "...",  # 可选：导航到其他实例
        "confirm": "...",      # 可选：显示二次确认
        "confirmAction": "..."  # 可选：确认后的action
    }
```

## 使用示例

### 示例1：简单编辑按钮

```json
{
  "key": "actions",
  "renderType": "mixed",
  "components": [
    {
      "type": "button",
      "id": "edit_user",
      "buttonLabel": "编辑",
      "buttonStyle": "primary",
      "buttonSize": "small",
      "actionId": "edit_user_action",  // 关联到全局action
      "params": {
        "operation": "edit"
      }
    }
  ]
}
```

### 示例2：带确认的删除按钮

```json
{
  "key": "actions",
  "renderType": "mixed",
  "components": [
    {
      "type": "button",
      "id": "delete_user",
      "buttonLabel": "删除",
      "buttonStyle": "danger",
      "buttonSize": "small",
      "confirmMessage": "确定要删除此用户吗？",
      "actionId": "delete_user_action",
      "params": {
        "operation": "delete"
      }
    }
  ]
}
```

### 示例3：自定义处理

```json
{
  "key": "actions",
  "renderType": "mixed",
  "components": [
    {
      "type": "button",
      "id": "custom_action",
      "buttonLabel": "自定义操作",
      "buttonStyle": "secondary",
      "tooltip": "执行自定义逻辑",
      "params": {
        "customParam": "value"
      }
    }
  ]
}
```

## 架构优势

### 1. 统一事件流
- 所有按钮事件都通过 `eventEmitter` 处理
- 统一的错误处理和日志记录
- 易于调试和维护

### 2. 高度可扩展
- 支持关联全局 action
- 支持自定义参数传递
- 支持确认对话框
- 支持成功/失败提示

### 3. 类型安全
- TypeScript 接口定义完整
- 编译时类型检查
- 减少运行时错误

### 4. 后端解耦
- 前端只负责发送事件
- 后端统一处理事件
- 易于添加新的事件类型

## 迁移指南

### 前端迁移
1. 确保所有表格按钮都有 `id` 字段
2. 可选：添加 `actionId` 关联全局 action
3. 可选：添加 `confirmMessage` 实现确认对话框
4. 测试按钮点击事件是否正确发送

### 后端迁移
1. 在 FastAPI 中添加 `table:button:click` 事件处理
2. 根据请求参数执行相应操作
3. 返回合适的响应（patch、message、navigate_to等）
4. 更新相关的 action handler

## 注意事项

1. **按钮ID唯一性**
   - 同一表格中的按钮ID应该唯一
   - 建议使用有意义的命名，如 `edit_user`, `delete_user`

2. **性能考虑**
   - 事件发射已有防抖机制（750ms）
   - 避免快速重复点击
   - 大数据量时考虑优化处理

3. **错误处理**
   - 统一使用事件发射器的错误处理
   - 前端显示友好的错误提示
   - 后端返回详细的错误信息

4. **向后兼容**
   - 旧版本的按钮配置仍然支持
   - 只是功能受限（只有日志打印）
   - 建议逐步迁移到新架构
