# MCP Tool Usage Contract

## 概述

这份文档定义了 UI Patch 工具的使用契约，确保 Agent 能够智能、高效地使用工具，避免过度修改和无发散。

## 工具使用原则

### 1. 操作前检查原则

**使用 `get_schema` 工具检查当前状态，避免重复或冲突操作**

```
// ❌ 错误：直接修改
patch_ui_state(instance_id="counter", patches=[...])

// ✅ 正确：先检查，再修改
get_schema(instance_id="counter")
// 分析结果后...
patch_ui_state(instance_id="counter", patches=[...])
```

### 2. 完成态评估原则

**使用 `validate_completion` 工具获取评估数据，让 Agent 自己判断是否完成**

```
// ✅ 正确：获取评估数据，Agent 自己决定
const evaluation = await validate_completion(
    instance_id="counter",
    intent="Create a counter with display and increment button",
    completion_criteria=[
        {"type": "field_exists", "path": "state.params.count"},
        {"type": "action_exists", "path": "increment"}
    ]
)

// Agent 根据评估数据自己决定是否停止
if (evaluation.evaluation.completion_ratio >= 1.0) {
    // Agent 决定：满足要求，停止修改
} else if (evaluation.evaluation.completion_ratio >= 0.75) {
    // Agent 决定：基本满足，可以根据需要继续或停止
} else {
    // Agent 决定：不满足要求，继续修改
    // 可以根据 evaluation.recommendations 进行针对性修改
}
```

### 3. 最小修改原则

**使用精准路径，避免覆盖整个结构**

```
// ❌ 错误：覆盖整个blocks数组
patch_ui_state(
    instance_id="form",
    patches=[{"op": "set", "path": "blocks", "value": [...blocks...]}]
)

// ✅ 正确：只修改需要的部分
patch_ui_state(
    instance_id="form",
    patches=[{"op": "add", "path": "blocks.0.fields", "value": newField}]
)
```

## 工具特定约束

### patch_ui_state 工具

#### 何时使用

- UI 结构需要改变时
- 字段值需要更新时
- 创建新实例时
- 删除实例时

#### 避免使用

- 连续重复修改同一路径（应合并为单次操作）
- 当只需要读取信息时（使用 get_schema）
- 修改未经验证的结构（先使用 validate_completion 检查）

#### 停止条件

- UI 满足 intent 描述
- validate_completion 返回 is_complete: true
- 修改开始影响其他功能

### get_schema 工具

#### 何时使用

- 修改前检查当前状态
- 验证修改是否生效
- 需要了解 UI 结构时

#### 停止条件

- 已经有足够的上下文信息进行下一步操作
- 已经验证了所需的信息

### validate_completion 工具

#### 何时使用

- 完成一个阶段的修改后
- 不确定 UI 是否满足需求时
- 需要量化完成度时

#### 必须使用的场景

- 完成一个完整的 UI 创建任务
- 在关闭任务前
- 当不确定是否应该继续修改时

#### 停止条件

- 返回 is_complete: true（停止修改）
- 返回清晰的未完成项（按建议继续）

## 意图 → 计划 → 补丁模式

### 意图 (Intent)

用户需求的高层描述，如：

- "创建一个计数器页面"
- "添加表单验证功能"
- "修改列表项的显示样式"

### 计划 (Plan)

结构级修改计划，分解意图为可执行的步骤：

```json
{
  "intent": "create_counter_ui",
  "plan": [
    "create instance counter",
    "add text block for counter display",
    "add increment button",
    "add decrement button",
    "set initial counter value to 0"
  ]
}
```

### 补丁 (Patch)

具体的编辑操作，实现计划的每个步骤：

```json
[
  {"op": "set", "path": "meta.pageKey", "value": "counter"},
  {"op": "set", "path": "state.params.count", "value": 0},
  {"op": "add", "path": "blocks", "value": {...}},
  {"op": "add", "path": "actions", "value": {...}}
]
```

## 常见使用模式

### 模式 1: 创建新 UI

1. **意图分析**: "创建一个XX类型的UI"
2. **计划制定**: 分解为步骤
3. **执行**: 使用 patch_ui_state 执行计划
4. **验证**: 使用 validate_completion 确认完成

### 模式 2: 修改现有 UI

1. **检查**: 使用 get_schema 了解当前状态
2. **对比**: 确定需要修改的部分
3. **执行**: 使用 patch_ui_state 进行精准修改
4. **验证**: 使用 validate_completion 确认修改效果

### 模式 3: 修复问题

1. **诊断**: 使用 get_schema 识别问题
2. **定位**: 确定问题所在的具体路径
3. **修复**: 使用最小化补丁修复问题
4. **验证**: 确认问题已解决且无副作用

## 错误示例和修正

### 错误 1: 重复修改同一路径

```javascript
// 错误：多次修改同一字段
patch_ui_state(..., [{"op": "set", "path": "state.params.count", "value": 1}])
patch_ui_state(..., [{"op": "set", "path": "state.params.count", "value": 2}])
patch_ui_state(..., [{"op": "set", "path": "state.params.count", "value": 3}])

// 修正：合并为单次操作
patch_ui_state(..., [{"op": "set", "path": "state.params.count", "value": 3}])
```

### 错误 2: 过度修改

```javascript
// 错误：覆盖整个结构
const currentSchema = await get_schema("instance")
currentSchema.blocks[0].fields[0].label = "新标签"
patch_ui_state(..., [{"op": "set", "path": "blocks", "value": currentSchema.blocks}])

// 修正：只修改需要的部分
patch_ui_state(..., [{"op": "set", "path": "blocks.0.fields.0.label", "value": "新标签"}])
```

### 错误 3: 缺少完成验证

```javascript
// 错误：修改后不验证是否完成
patch_ui_state(..., patches) // 然后就认为任务完成了

// 修正：使用完成态验证
patch_ui_state(..., patches)
const result = await validate_completion(...)
if (result.is_complete) {
    // 任务完成
} else {
    // 继续修改
}
```

## 完整示例：Agent 自主决策流程

下面是一个完整示例，展示 Agent 如何使用评估工具获取数据，然后自主决定是否继续修改：

```javascript
// 步骤1：创建计数器UI的基本结构
await patch_ui_state(
    instance_id="__CREATE__",
    new_instance_id="counter",
    patches=[
        {"op": "set", "path": "meta.pageKey", "value": "counter"},
        {"op": "set", "path": "state.params.count", "value": 0},
        {"op": "add", "path": "blocks", "value": {
            "id": "display",
            "type": "text",
            "content": "Count: ${count}"
        }}
    ]
)

// 步骤2：评估当前状态，获取客观数据
const evaluation1 = await validate_completion(
    instance_id="counter",
    intent="Create a counter with display and increment button",
    completion_criteria=[
        {"type": "field_exists", "path": "state.params.count", "description": "计数器字段存在"},
        {"type": "block_count", "count": 1, "description": "只有一个显示块"},
        {"type": "action_exists", "path": "increment", "description": "增加按钮存在"}
    ]
)

// Agent分析评估数据：
// evaluation1.evaluation.passed_criteria = 2 (字段和块存在)
// evaluation1.evaluation.total_criteria = 3
// evaluation1.evaluation.completion_ratio = 0.67

// Agent自主决策：虽然completion_ratio为0.67，但缺少重要功能（增加按钮）
// 决定继续修改
if (evaluation1.evaluation.completion_ratio < 1.0) {
    // 根据recommendations添加缺失的功能
    await patch_ui_state(
        instance_id="counter",
        patches=[
            {"op": "add", "path": "actions", "value": {
                "id": "increment",
                "label": "增加",
                "action": "state.params.count += 1"
            }}
        ]
    )
    
    // 再次评估
    const evaluation2 = await validate_completion(
        instance_id="counter",
        intent="Create a counter with display and increment button",
        completion_criteria=[
            {"type": "field_exists", "path": "state.params.count", "description": "计数器字段存在"},
            {"type": "block_count", "count": 1, "description": "只有一个显示块"},
            {"type": "action_exists", "path": "increment", "description": "增加按钮存在"}
        ]
    )
    
    // evaluation2.evaluation.completion_ratio = 1.0
    
    // Agent再次自主决策：现在所有条件都满足，但还可以添加减少按钮
    // 即使工具返回completion_ratio为1.0，Agent仍然可以决定继续优化
    if (evaluation2.evaluation.completion_ratio >= 1.0) {
        // Agent决定：基本功能已完成，但可以添加额外功能
        const shouldAddDecrement = await evaluate_user_intent("是否需要减少按钮？")
        if (shouldAddDecrement) {
            await patch_ui_state(
                instance_id="counter",
                patches=[
                    {"op": "add", "path": "actions", "value": {
                        "id": "decrement",
                        "label": "减少",
                        "action": "state.params.count -= 1"
                    }}
                ]
            )
        }
        // 最终决定：无论是否添加额外功能，现在停止修改
    }
}
```

## 总结

这份契约的核心思想是：**深思熟虑，精准执行，自主决策**。

- **深思熟虑**：在操作前使用 get_schema 了解现状
- **精准执行**：使用最小化、精准的补丁操作
- **自主决策**：使用 validate_completion 获取评估数据，但由 Agent 自己判断是否完成

遵循这些原则，Agent 的 UI 操作将更加可控、高效，并且能够智能地决定"何时停止"，而不是被动接受工具的判断。
