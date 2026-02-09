---
name: pta_n-1
type: knowledge
version: 0.37.0
agent: CodeActAgent
triggers:
  - n-1 PTA
  - n-1可视化
  - n-1画布
demand_mcp_tool_name: [initModelAndCreateSACanvas,power_flow_sample_simple_ramdom,getCurrentJob,getCurrentConfig,createOrUpdateJob,createOrUpdateConfig,runProject,generate_random_fault_params_set_N_1,setN_1_GroundFault,addComponentOutputMeasures,save_flow_emt_hdf5,extract_and_check_data,get_step_temp,get_default_config,submit_batch_simulation,query_batch_simulation_status,get_batch_simulation_result,list_batch_simulation_tasks,clear_batch_simulation_tasks,patch_ui_state,get_schema,validate_completion,switch_ui,list_instances]
belong_mcp_server: FastMCP
---

# N-1 仿真 PTA 交互指南

## 核心原则

1. **PTA 优先**：所有参数输入、配置修改、结果展示都通过 PTA 画布完成
2. **对话辅助**：对话框仅用于流程引导、状态说明和异常处理
3. **单一实例**：整个仿真过程只使用一个 PTA 实例
4. **全局 tabs 布局**：使用全局 `layout.type = "tabs"`，每个步骤独占一个标签页
5. **实时同步**：每次执行下一步前，必须调用 `validate_completion` 获取用户在界面上的实际修改值

---

## 仿真模式识别

在开始流程前，必须在对话框中明确询问用户希望执行哪种模式：

**对话模板**：
```
您好！欢迎使用 N-1 仿真系统。请选择仿真模式：
1. 单次 N-1 仿真 - 对单个故障场景进行详细仿真
2. 批量 N-1 仿真 - 对多个故障场景进行批量仿真

请回复 1 或 2，或直接描述您的需求。
```

根据用户回复，执行对应模式的流程：
- Model A：单次 N-1 仿真
- Model B：批量 N-1 仿真

---

## Model A：单次 N-1 仿真流程

### 步骤 0：PTA 实例初始化 `[自动执行]`

**操作**：创建 PTA 实例

**PTA 初始化**：
```json
{
  "instance_name": "__CREATE__",
  "new_instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "page_key", "value": "n1_simulation"},
    {"op": "set", "path": "state", "value": {"params": {}, "runtime": {}}},
    {"op": "set", "path": "layout", "value": {"type": "tabs"}},
    {"op": "set", "path": "blocks", "value": [
      {"id": "step1_init", "layout": "form", "title": "步骤1: 模型初始化", "props": {"fields": [], "actions": []}},
      {"id": "step2_powerflow", "layout": "form", "title": "步骤2: 潮流计算", "props": {"fields": [], "actions": []}},
      {"id": "step3_flow_result", "layout": "form", "title": "步骤3: 潮流计算结果", "props": {"fields": [], "actions": []}},
      {"id": "step4_fault", "layout": "form", "title": "步骤4: 故障参数", "props": {"fields": [], "actions": []}},
      {"id": "step5_emt", "layout": "form", "title": "步骤5: 电磁暂态计算", "props": {"fields": [], "actions": []}},
      {"id": "step6_measures", "layout": "form", "title": "步骤6: 量测信号", "props": {"fields": [], "actions": []}},
      {"id": "step7_run", "layout": "form", "title": "步骤7: 执行仿真", "props": {"fields": [], "actions": []}},
      {"id": "step8_result", "layout": "form", "title": "步骤8: 结果分析", "props": {"fields": [], "actions": []}}
    ]},
    {"op": "set", "path": "actions", "value": []}
  ]
}
```

**注意**：创建实例必须包含 `meta` 字段，用于设置 `page_key`。

---

### 步骤 1：模型初始化 `[自动执行]`

**操作**：调用 `initModelAndCreateSACanvas` 初始化仿真环境

**PTA 更新**：
```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.0.props.fields", "value": [
      {"key": "init_status", "label": "初始化状态", "type": "tag", "value": "completed", "options": [{"label": "已完成", "value": "completed"}]},
      {"key": "init_message", "label": "提示", "type": "html", "value": "<p>模型已成功初始化，请进入下一步进行潮流计算配置。</p>"}
    ]}
  ]
}
```

**切换标签页**：
```python
switch_ui({"instance_name": "n1_simulation", "block_id": "step2_powerflow"})
```

---

### 步骤 2：潮流计算配置 `[自动执行 + 等待确认]`

**操作**：
1. 调用 `getCurrentJob` 和 `getCurrentConfig` 获取当前潮流计算配置
2. 在 PTA 中展示可编辑的配置表格
3. **用户确认后必须获取修改后的配置**：

```python
result = validate_completion({"instance_name": "n1_simulation"})
config_table = result['state_summary']['params']['powerflow_config']
createOrUpdateConfig({"config_data": config_table})
```

**PTA 更新**：
```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.1.props.fields", "value": [
      {
        "key": "powerflow_config",
        "label": "潮流计算配置（可编辑）",
        "type": "table",
        "tableEditable": true,
        "showPagination": false,
        "columns": [
          {"key": "param", "title": "参数名", "width": "200px"},
          {"key": "value", "title": "参数值", "width": "150px", "editable": true},
          {"key": "description", "title": "说明", "width": "300px"}
        ],
        "value": [
          {"param": "iterations", "value": "10", "description": "迭代次数"},
          {"param": "tolerance", "value": "1e-6", "description": "收敛容差"},
          {"param": "algorithm", "value": "Newton-Raphson", "description": "求解算法"}
        ]
      }
    ]},
    {"op": "set", "path": "blocks.1.props.actions", "value": [
      {
        "id": "confirm_powerflow",
        "label": "确认配置并继续",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.powerflow_confirmed", "value": true}]
      }
    ]}
  ]
}
```

---

### 步骤 3：生成随机潮流样本并执行潮流计算 `[询问后执行]`

**对话引导**：
```
当前潮流计算配置已确认。
是否立即生成随机潮流样本并执行潮流计算？
回复「执行」开始计算，或「重新配置」返回步骤 2 修改配置。
```

**操作**：调用 `power_flow_sample_simple_ramdom` 生成样本并执行

**PTA 更新**：
```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.2.props.fields", "value": [
      {"key": "flow_status", "label": "潮流计算状态", "type": "tag", "value": "completed", "options": [{"label": "已完成", "value": "completed"}]},
      {"key": "flow_message", "label": "说明", "type": "html", "value": "<p>潮流计算已完成，请进入下一步配置故障参数。</p>"}
    ]}
  ]
}
```

**切换标签页**：
```python
switch_ui({"instance_name": "n1_simulation", "block_id": "step4_fault"})
```

---

### 步骤 4：N-1 故障参数配置 `[询问后执行]`

**对话引导**：
```
请选择故障参数生成方式：
1. 随机生成 - 系统自动生成随机故障参数
2. 自定义输入 - 手动指定故障类型和位置

请回复 1 或 2。
```

**操作**：根据用户选择调用 `generate_random_fault_params_set_N_1` 或 `setN_1_GroundFault`

**重要**：在调用工具前，必须获取用户在界面上的实际输入：
```python
result = validate_completion({"instance_name": "n1_simulation"})
fault_mode = result['state_summary']['params']['fault_mode']
fault_params = result['state_summary']['params']['fault_params']

if fault_mode == 'custom':
    setN_1_GroundFault({"fault_params": fault_params})
else:
    generate_random_fault_params_set_N_1({})
```

**PTA 更新**：
```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.3.props.fields", "value": [
      {
        "key": "fault_mode",
        "label": "故障参数生成方式",
        "type": "radio",
        "options": [
          {"label": "随机生成", "value": "random", "description": "系统自动生成随机故障参数"},
          {"label": "自定义输入", "value": "custom", "description": "手动指定故障类型和位置"}
        ],
        "value": "random"
      },
      {
        "key": "fault_params",
        "label": "故障参数",
        "type": "textarea",
        "placeholder": "选择「随机生成」后点击按钮生成，或选择「自定义输入」后手动填写",
        "value": ""
      }
    ]},
    {"op": "set", "path": "blocks.3.props.actions", "value": [
      {
        "id": "generate_fault",
        "label": "生成故障参数",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.fault_generated", "value": true}]
      },
      {
        "id": "confirm_fault",
        "label": "确认并继续",
        "style": "secondary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.fault_confirmed", "value": true}]
      }
    ]}
  ]
}
```

**切换标签页**：
```python
switch_ui({"instance_name": "n1_simulation", "block_id": "step5_emt"})
```

---

### 步骤 5：电磁暂态计算配置 `[自动执行 + 等待确认]`

**操作**：
1. 调用 `getCurrentConfig` 获取电磁暂态计算配置
2. 在 PTA 中展示可编辑的配置表格
3. **用户确认后必须获取修改后的配置**：

```python
result = validate_completion({"instance_name": "n1_simulation"})
emt_config = result['state_summary']['params']['emt_config']
createOrUpdateConfig({"config_data": emt_config})
```

**PTA 更新**：
```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.4.props.fields", "value": [
      {
        "key": "emt_config",
        "label": "电磁暂态计算配置（可编辑）",
        "type": "table",
        "tableEditable": true,
        "columns": [
          {"key": "param", "title": "参数名", "width": "200px"},
          {"key": "value", "title": "参数值", "width": "150px", "editable": true},
          {"key": "description", "title": "说明", "width": "300px"}
        ],
        "value": [
          {"param": "t_start", "value": "0", "description": "仿真起始时间 (s)"},
          {"param": "t_end", "value": "5", "description": "仿真结束时间 (s)"},
          {"param": "dt", "value": "0.001", "description": "仿真步长 (s)"}
        ]
      }
    ]},
    {"op": "set", "path": "blocks.4.props.actions", "value": [
      {
        "id": "confirm_emt",
        "label": "确认配置并继续",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.emt_confirmed", "value": true}]
      }
    ]}
  ]
}
```

---

### 步骤 6：添加量测信号 `[询问后执行]`

**对话引导**：
```
将为您添加以下量测信号（按顺序）：
1. 母线电压（rid: `model/CloudPSS/_newBus_3p`, key: `Vrms`）
2. 发电机功率（rid: `model/CloudPSS/SyncGeneratorRouter`, key: `PT_o`）
3. 发电机转速（rid: `model/CloudPSS/SyncGeneratorRouter`, key: `wr_o`）
4. 发电机攻角（rid: `model/CloudPSS/SyncGeneratorRouter`, key: `theta_o`）

确认添加？回复「确认」继续，或「修改」调整量测信号。
```

**PTA 更新**：
```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.5.props.fields", "value": [
      {
        "key": "measures_intro",
        "label": "说明",
        "type": "html",
        "value": "<p>将按顺序添加以下量测信号，绘图名称已自动生成。</p>"
      },
      {
        "key": "measures",
        "label": "量测信号列表",
        "type": "table",
        "tableEditable": false,
        "columns": [
          {"key": "order", "title": "序号", "width": "60px"},
          {"key": "name", "title": "量测名称", "width": "150px"},
          {"key": "rid", "title": "RID", "width": "280px"},
          {"key": "key", "title": "Key", "width": "120px"}
        ],
        "value": [
          {"order": 1, "name": "母线电压", "rid": "model/CloudPSS/_newBus_3p", "key": "Vrms"},
          {"order": 2, "name": "发电机功率", "rid": "model/CloudPSS/SyncGeneratorRouter", "key": "PT_o"},
          {"order": 3, "name": "发电机转速", "rid": "model/CloudPSS/SyncGeneratorRouter", "key": "wr_o"},
          {"order": 4, "name": "发电机攻角", "rid": "model/CloudPSS/SyncGeneratorRouter", "key": "theta_o"}
        ]
      }
    ]},
    {"op": "set", "path": "blocks.5.props.actions", "value": [
      {
        "id": "add_measures",
        "label": "添加量测信号",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.measures_confirmed", "value": true}]
      }
    ]}
  ]
}
```

**操作**：调用 `addComponentOutputMeasures` 添加量测（注意：必须按顺序，不设置 dim 参数）

**重要**：在调用工具前，必须获取用户在界面上的确认状态：
```python
result = validate_completion({"instance_name": "n1_simulation"})
measures_confirmed = result['state_summary']['params']['measures_confirmed']

if measures_confirmed:
    addComponentOutputMeasures({"rid": "model/CloudPSS/_newBus_3p", "key": "Vrms"})
    addComponentOutputMeasures({"rid": "model/CloudPSS/SyncGeneratorRouter", "key": "PT_o"})
    addComponentOutputMeasures({"rid": "model/CloudPSS/SyncGeneratorRouter", "key": "wr_o"})
    addComponentOutputMeasures({"rid": "model/CloudPSS/SyncGeneratorRouter", "key": "theta_o"})
```

**切换标签页**：
```python
switch_ui({"instance_name": "n1_simulation", "block_id": "step7_run"})
```

---

### 步骤 7：执行仿真 `[询问后执行]`

**PTA 更新**：
```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.6.props.fields", "value": [
      {"key": "simulation_status", "label": "仿真状态", "type": "tag", "value": "ready", "options": [{"label": "准备就绪", "value": "ready"}]},
      {"key": "simulation_info", "label": "仿真信息", "type": "html", "value": "<p>配置已完成，点击下方按钮开始仿真。</p>"}
    ]},
    {"op": "set", "path": "blocks.6.props.actions", "value": [
      {
        "id": "run_simulation",
        "label": "开始仿真",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.run_simulation", "value": true}]
      }
    ]}
  ]
}
```

**对话引导**：
```
所有配置已完成，点击「开始仿真」按钮执行仿真。
```

**操作**：
1. 调用 `runProject` 执行仿真
2. 调用 `save_flow_emt_hdf5` 保存结果

**重要**：在执行仿真前，必须获取用户确认状态：
```python
result = validate_completion({"instance_name": "n1_simulation"})
run_simulation = result['state_summary']['params']['run_simulation']

if run_simulation:
    runProject({})
    save_flow_emt_hdf5({})
```

---

### 步骤 8：结果分析与输出 `[自动执行]`

**操作**：
1. 调用 `extract_and_check_data` 检查稳定性
2. 获取结果图片路径和文件路径
3. 在 PTA 中展示结果

**PTA 更新**：
```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.7.props.fields", "value": [
      {"key": "stability_result", "label": "稳定性分析", "type": "tag", "value": "stable", "options": [{"label": "系统稳定", "value": "stable"}]},
      {"key": "voltage_chart", "label": "母线电压曲线", "type": "image", "value": "https://minio.example.com/voltage.png", "showFullscreen": true, "showDownload": true},
      {"key": "power_chart", "label": "发电机功率曲线", "type": "image", "value": "https://minio.example.com/power.png", "showFullscreen": true, "showDownload": true},
      {"key": "speed_chart", "label": "发电机转速曲线", "type": "image", "value": "https://minio.example.com/speed.png", "showFullscreen": true, "showDownload": true},
      {"key": "angle_chart", "label": "发电机攻角曲线", "type": "image", "value": "https://minio.example.com/angle.png", "showFullscreen": true, "showDownload": true},
      {"key": "result_files", "label": "结果文件", "type": "html", "value": "<p><a href=\"https://minio.example.com/results.hdf5\" target=\"_blank\">下载完整结果文件 (results.hdf5)</a></p>"}
    ]}
  ]
}
```

**对话引导**：
```
仿真已完成！结果如下：

| 序号 | 稳定性 | 结果文件 | 电压曲线 | 功率曲线 | 转速曲线 | 攻角曲线 |
|------|--------|----------|----------|----------|----------|----------|
| 1 | 稳定 | ![下载](https://minio.example.com/results.hdf5) | ![电压](https://minio.example.com/voltage.png) | ![功率](https://minio.example.com/power.png) | ![转速](https://minio.example.com/speed.png) | ![攻角](https://minio.example.com/angle.png) |

在「步骤8: 结果分析」标签页中也可查看所有结果。
```

---

## Model B：批量 N-1 仿真流程

### 重要约束

- **禁止**调用任何 Model A 的工具（如 `createOrUpdateConfig`、`createOrUpdateJob`）
- **禁止**直接执行仿真，仅配置和提交批量任务

---

### 步骤 0：PTA 实例初始化 `[自动执行]`

**PTA 初始化**：
```json
{
  "instance_name": "__CREATE__",
  "new_instance_name": "n1_simulation_batch",
  "patches": [
    {"op": "set", "path": "page_key", "value": "n1_simulation_batch"},
    {"op": "set", "path": "state", "value": {"params": {}, "runtime": {}}},
    {"op": "set", "path": "layout", "value": {"type": "tabs"}},
    {"op": "set", "path": "blocks", "value": [
      {"id": "step1_default_config", "layout": "form", "title": "步骤1: 默认配置", "props": {"fields": [], "actions": []}},
      {"id": "step2_flow_template", "layout": "form", "title": "步骤2: 流程模板", "props": {"fields": [], "actions": []}},
      {"id": "step3_params_explanation", "layout": "form", "title": "步骤3: 参数说明", "props": {"fields": [], "actions": []}},
      {"id": "step4_batch_config", "layout": "form", "title": "步骤4: 批量配置", "props": {"fields": [], "actions": []}},
      {"id": "step5_batch_count", "layout": "form", "title": "步骤5: 批量次数", "props": {"fields": [], "actions": []}},
      {"id": "step6_submit_task", "layout": "form", "title": "步骤6: 提交任务", "props": {"fields": [], "actions": []}},
      {"id": "step7_query_result", "layout": "form", "title": "步骤7: 结果查询", "props": {"fields": [], "actions": []}}
    ]},
    {"op": "set", "path": "actions", "value": []}
  ]
}
```

**注意**：创建实例必须包含 `meta` 字段，用于设置 `page_key`。

---

### 步骤 1-3：配置收集与确认

依次展示默认配置、流程模板、参数说明，并在每个步骤后调用 `validate_completion` 获取用户的确认状态。

### 步骤 4：生成批量配置 JSON

**操作**：根据前面步骤收集的信息，生成批量仿真配置 JSON

**重要**：在生成配置前，必须获取用户在前面的步骤中修改的参数：
```python
result = validate_completion({"instance_name": "n1_simulation_batch"})
step1_confirmed = result['state_summary']['params']['step1_confirmed']
step2_confirmed = result['state_summary']['params']['step2_confirmed']
step3_confirmed = result['state_summary']['params']['step3_confirmed']

if step1_confirmed and step2_confirmed and step3_confirmed:
    batch_config = generate_batch_config()
```

### 步骤 5：提交批量任务

**重要**：在提交前，必须获取用户在界面上的最终确认：
```python
result = validate_completion({"instance_name": "n1_simulation_batch"})
step4_confirmed = result['state_summary']['params']['step4_confirmed']
batch_count = result['state_summary']['params'].get('batch_count', 9)

if step4_confirmed:
    submit_batch_simulation({
        "batch_config": batch_config,
        "batch_count": batch_count
    })
```

### 步骤 6：结果查询

调用 `query_batch_simulation_status` 和 `get_batch_simulation_result` 查询和获取结果。

---

## PTA 使用技巧

### 状态管理

**获取用户输入**：
```python
result = validate_completion({"instance_name": "n1_simulation"})
state = result['state_summary']['params']
```

**切换标签页**：
```python
switch_ui({"instance_name": "n1_simulation", "block_id": "step2_powerflow"})
```

---

## 总结

关键要点：
- 所有交互都通过 PTA 完成，对话框仅用于流程引导
- 使用表格的 `tableEditable` 属性实现可编辑配置
- **每次执行下一步前都必须调用 `validate_completion` 获取用户在界面上的实际修改值**
- **不能假设用户没有修改界面上的参数，必须同步最新的配置到系统**
- 使用 `image` 组件展示仿真结果图片
- 使用 `switch_ui` 在不同步骤间切换
- Model A 和 Model B 的工具禁止混用
- Model B 禁止直接执行仿真计算
