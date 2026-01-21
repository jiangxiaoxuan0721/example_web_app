# WebSocket 推送更新问题分析文档

## 问题总结

WebSocket 推送 patch 后，前端 state 虽然更新了，但页面没有自动刷新，需要手动刷新才能看到更新。

---

## 完整数据流

### 1. WebSocket 推送流程

```
后端 → WebSocket Message → useWebSocket.onmessage → onPatchRef.current(patch)
```

**代码位置：** `frontend/src/hooks/useWebSocket.ts:75-77`

```typescript
if (message.type === 'patch' && message.patch) {
  console.log('[WS] 应用 Patch:', message.patch);
  onPatchRef.current(message.patch);  // ✅ 调用回调
}
```

### 2. App 层接收 Patch

```
useWebSocket.onPatch → App.tsx 的 onPatch 回调 → applyPatch(patch)
```

**代码位置：** `frontend/src/App.tsx:68-74`

```typescript
const { connected: wsConnected } = useWebSocket(
  // 处理 Patch
  (patch) => {
    console.log('[App] 通过 WebSocket 收到 Patch:', patch);
    applyPatch(patch);  // ✅ 调用 store 的 applyPatch
    // 刷新 Patch 历史记录
    loadPatches();
  },
  // ...
);
```

### 3. Store 层更新 Schema

```
applyPatch(patch) → set((state) => { ... })
```

**代码位置：** `frontend/src/store/schemaStore.ts:34-55`

```typescript
applyPatch: (patch) => set((state) => {
  if (!state.schema) return state;

  // Deep clone schema and apply patches
  const newSchema = JSON.parse(JSON.stringify(state.schema));

  for (const [path, value] of Object.entries(patch)) {
    // ... 应用 patch
  }

  return { schema: newSchema };  // ✅ 返回新的 schema 引用
}),
```

### 4. 组件订阅 Store

```
useFieldValue(bindPath, field.key) → useSchemaStore(selector)
```

**代码位置：** `frontend/src/store/schemaStore.ts:72-77`

```typescript
export const useFieldValue = (bindPath: string, fieldKey: string) => {
  return useSchemaStore((state) => {
    // ❌ 问题：返回整个 state，而不是特定值
    return state;
  });
};
```

### 5. 组件渲染

```
GenericFieldRenderer → useFieldValue → useMemo 提取值 → 渲染
```

**代码位置：** `frontend/src/components/GenericFieldRenderer.tsx:376-393`

```typescript
// 从 Store 获取 state（订阅整个 state）
const storeState = useFieldValue(bindPath, field.key);

// 从 state.schema 中提取值
const storedValue = useMemo(() => {
  if (!storeState?.schema) return undefined;
  // ... 提取值
}, [storeState?.schema, bindPath, field.key]);

// 当 Store 中的值变化时，同步到本地状态
useEffect(() => {
  setLocalValue(storedValue);
}, [storedValue]);
```

---

## 问题根源分析

### 问题 1：Zustand Selector 的浅比较机制

Zustand 的 selector 默认使用**浅比较 (Shallow Comparison)**：

```typescript
// selector 返回值比较
previousResult === currentResult
```

当 `applyPatch` 执行时：
- `schema` 引用变化了 ✅
- 但 `state` 作为整体对象引用也变化了
- selector 每次返回新的 `state` 对象
- Zustand 认为"有变化"，触发重渲染 ✅

**所以 Store 层是正常的！**

### 问题 2：`useMemo` 的依赖检查

```typescript
const storedValue = useMemo(() => {
  // ...
}, [storeState?.schema, bindPath, field.key]);
```

**关键问题：** 当 `storeState.schema` 引用变化时，`useMemo` 重新计算值，这是正确的 ✅

### 问题 3：`useEffect` 的同步逻辑

```typescript
useEffect(() => {
  setLocalValue(storedValue);
}, [storedValue]);
```

**潜在问题：**

1. **乐观更新冲突**
   - 用户输入 → `handleChange` → `setLocalValue(newValue)` → `fieldPatch`
   - WebSocket 推送相同的 patch → `storedValue` 变化 → `setLocalValue(storedValue)`
   - 如果 WebSocket 推送延迟，可能会覆盖用户的输入

2. **值相同但引用不同**
   - `storedValue` 从 `"old"` 变为 `"new"`
   - `localValue` 已经是 `"new"`（通过乐观更新）
   - `setLocalValue(storedValue)` 设置相同值，可能不触发重渲染

### 问题 4：真正的核心问题 - **WebSocket 推送的 patch 格式不对**

让我们检查后端推送的 patch 格式：

**用户修改字段：** `input` 输入 → `fieldPatch` → `emitFieldChange` → 后端

**后端处理：** 后端应该推送 patch：`{ "state.params.fieldKey": "newValue" }`

**前端接收：** `applyPatch({ "state.params.fieldKey": "newValue" })`

**但是！** 在 `GenericFieldRenderer` 中，每个字段都有自己的 `bindPath`：

```typescript
const { field, schema, bindPath, ... } = props;
// bindPath 可能是 "blocks.0.props.fields" 或 "state.params"
```

**如果后端推送的 patch 是：**
```json
{ "state.params.username": "newvalue" }
```

**但前端的 `bindPath` 是：**
```typescript
bindPath = "blocks.0.props.fields"  // 或其他路径
```

**那么 `useFieldValue(bindPath, field.key)` 会查找：**
```javascript
// 如果 bindPath = "blocks.0.props.fields"
// field.key = "username"
// 实际查找路径：blocks[0].props.fields.username

// 但后端更新的路径是：state.params.username
```

---

## 真正的问题所在

### 问题：**Patch 路径与组件订阅的路径不匹配**

假设场景：
1. 用户修改 `blocks[0].props.fields[0].key = "username"` 的字段
2. 后端收到事件，推送 patch：`{ "state.params.username": "newValue" }`
3. 前端组件订阅：`useFieldValue("blocks.0.props.fields", "username")`
4. 组件从 `storeState.schema.blocks[0].props.fields.username` 读取值
5. **但后端更新的是 `storeState.schema.state.params.username`**

**路径不匹配！组件读取的路径没有被更新！**

---

## 解决方案

### 方案 1：统一 Patch 路径（推荐）

**检查后端推送的 patch 路径格式**，确保与前端 `bindPath` 匹配：

```typescript
// 后端应该推送
{
  "blocks.0.props.fields.0.username": "newValue"
}

// 而不是
{
  "state.params.username": "newValue"
}
```

### 方案 2：组件订阅正确的路径

修改 `GenericFieldRenderer`，确保 `bindPath` 指向正确的数据源：

```typescript
// 如果字段绑定到 state.params
if (field.binding?.startsWith('state.')) {
  bindPath = 'state';  // 只订阅 state
  // 然后在 useMemo 中正确解析
}
```

### 方案 3：调试日志 - 验证 Patch 路径

添加详细日志，对比 WebSocket 推送的 patch 和组件订阅的路径：

```typescript
// 在 App.tsx
(patch) => {
  console.log('[App] 收到 Patch:', patch);  // 查看推送的路径
  console.log('[App] 当前 Schema:', state.schema);  // 查看 schema 结构
  applyPatch(patch);
}

// 在 GenericFieldRenderer.tsx
const storeState = useFieldValue(bindPath, field.key);
console.log('[GenericFieldRenderer] bindPath:', bindPath, 'fieldKey:', field.key);
console.log('[GenericFieldRenderer] 当前值:', storedValue);
```

---

## 验证步骤

1. **查看浏览器控制台**
   - WebSocket 收到的 patch 路径是什么？
   - Schema 的结构是什么样的？

2. **对比路径**
   - 后端推送：`{ "XXX": "value" }`
   - 组件订阅：`bindPath = "YYY"`, `fieldKey = "ZZZ"`
   - 实际查找：`schema.YYY.ZZZ`
   - 是否匹配？

3. **检查后端代码**
   - 查看 `backend/fastapi/routes/patch_routes.py`
   - 确认 WebSocket 推送的 patch 格式

---

## 结论

**WebSocket 推送更新失败的核心原因是：Patch 路径与组件订阅的数据路径不匹配。**

需要：
1. ✅ 检查后端推送的 patch 路径格式
2. ✅ 检查前端 `bindPath` 和 `field.key` 的组合
3. ✅ 确保两者指向同一个数据位置
4. ✅ 添加日志验证数据流

**不是 React 或 Zustand 的问题，而是数据路径映射的问题！**
