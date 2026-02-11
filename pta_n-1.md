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

本文档提供使用 PTA（Prompt To App）可视化组件与用户交互完成 N-1 仿真的完整指南。

## 核心原则

1. **PTA 优先**：所有参数输入、配置修改、结果展示都通过 PTA 画布完成
2. **对话辅助**：对话框仅用于流程引导、状态说明和异常处理
3. **单一实例**：整个仿真过程只使用一个 PTA 实例，使用 tabs 布局
4. **无全局 Action**：所有操作按钮都放在各自的 block 内

## PTA 实例初始化模板

在开始任何仿真流程前，必须先创建 PTA 实例：

```json
{
  "instance_name": "__CREATE__",
  "new_instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "page_key", "value": "n1_simulation"},
    {"op": "set", "path": "state", "value": {
      "params": {},
      "runtime": {}
    }},
    {"op": "set", "path": "layout", "value": {"type": "tabs"}},
    {"op": "set", "path": "blocks", "value": [
      {"id": "step1_model","title": "步骤1: 模型初始化","layout": "form","props": {"fields": [], "actions": []}},
      {"id": "step2_powerflow","title": "步骤2: 潮流计算","layout": "form","props": {"fields": [], "actions": []}},
      {"id": "step3_fault","title": "步骤3: 故障参数","layout": "form","props": {"fields": [], "actions": []}},
      {"id": "step4_emt","title": "步骤4: 电磁暂态计算","layout": "form","props": {"fields": [], "actions": []}},
      {"id": "step5_measures","title": "步骤5: 量测信号","layout": "form","props": {"fields": [], "actions": []}},
      {"id": "step6_run","title": "步骤6: 执行仿真","layout": "form","props": {"fields": [], "actions": []}},
      {"id": "step7_result","title": "步骤7: 结果分析","layout": "form","props": {"fields": [], "actions": []}}
    ]},
    {"op": "set", "path": "actions", "value": []}
  ]
}
```

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

### 步骤 1：模型初始化 `[自动执行]`

**操作**：调用 `initModelAndCreateSACanvas` 初始化仿真环境

**PTA 更新**：在 step1_model block 中显示初始化状态

```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.0.props.fields", "value": [
      {"key": "init_status","label": "初始化状态","type": "tag","value": "已完成","options": [{"label": "已完成", "value": "completed"}]},
      {"key": "init_message","label": "提示","type": "html","value": "<p>模型已成功初始化，请进入下一步进行潮流计算配置。</p>"}
    ]}
  ]
}
```

**对话引导**：使用 `switch_ui` 切换到步骤 2

---

### 步骤 2：潮流计算配置 `[自动执行 + 等待确认]`

**操作**：
1. 调用 `getCurrentJob` 和 `getCurrentConfig` 获取当前潮流计算配置
2. 将配置转换为可编辑的表格展示在 PTA 中

**PTA 更新**：创建可编辑的配置表格

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

**对话引导**：
```
已在「步骤2: 潮流计算」标签页中展示当前配置。
您可以直接在表格中编辑参数值，点击「确认配置并继续」按钮完成配置。
或者直接在对话框中回复「下一步」使用默认配置继续。
```

**获取用户修改**：用户点击按钮或回复「下一步」后，调用 `validate_completion` 获取表格数据：

```python
result = validate_completion({"instance_name": "n1_simulation"})
config_table = result['state']['params']['powerflow_config']

# 如果用户修改了配置，调用 createOrUpdateConfig 更新
if config_modified:
    createOrUpdateConfig({"config": config_table})
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

**PTA 更新**：在 step3_fault block 中显示计算结果摘要

---

### 步骤 4：N-1 故障参数配置 `[询问后执行]`

**PTA 更新**：提供两种选择方式

```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.2.props.fields", "value": [
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
    {"op": "set", "path": "blocks.2.props.actions", "value": [
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

**对话引导**：
```
请在「步骤3: 故障参数」标签页中选择故障参数生成方式。
- 随机生成：点击「生成故障参数」按钮自动生成
- 自定义输入：手动填写故障参数

完成后点击「确认并继续」。
```

**操作**：根据用户选择调用 `generate_random_fault_params_set_N_1` 或 `setN_1_GroundFault`

---

### 步骤 5：电磁暂态计算配置 `[自动执行 + 等待确认]`

**操作**：类似步骤 2，获取电磁暂态计算配置并展示可编辑表格

```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.3.props.fields", "value": [
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
    {"op": "set", "path": "blocks.3.props.actions", "value": [
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

**对话引导**：类似步骤 2

---

### 步骤 6：添加量测信号 `[询问后执行]`

**PTA 更新**：展示预设的量测信号列表，允许用户修改

```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.4.props.fields", "value": [
      {
        "key": "measures_intro",
        "label": "说明",
        "type": "html",
        "value": "<p>已为您预设以下量测信号，可在表格中修改参数。</p>"
      },
      {
        "key": "measures",
        "label": "量测信号配置（可编辑）",
        "type": "table",
        "tableEditable": true,
        "columns": [
          {"key": "name", "title": "量测名称", "width": "200px", "editable": true},
          {"key": "rid", "title": "RID", "width": "300px"},
          {"key": "key", "title": "Key", "width": "150px"},
          {"key": "enabled", "title": "启用", "width": "80px", "editable": true}
        ],
        "value": [
          {"name": "母线电压", "rid": "model/CloudPSS/_newBus_3p", "key": "Vrms", "enabled": true},
          {"name": "发电机功率", "rid": "model/CloudPSS/SyncGeneratorRouter", "key": "PT_o", "enabled": true},
          {"name": "发电机转速", "rid": "model/CloudPSS/SyncGeneratorRouter", "key": "wr_o", "enabled": true},
          {"name": "发电机攻角", "rid": "model/CloudPSS/SyncGeneratorRouter", "key": "theta_o", "enabled": true}
        ]
      }
    ]},
    {"op": "set", "path": "blocks.4.props.actions", "value": [
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

**对话引导**：
```
预设了以下量测信号：
- 母线电压 (Vrms)
- 发电机功率 (PT_o)
- 发电机转速 (wr_o)
- 发电机攻角 (theta_o)

您可以在表格中修改量测名称或启用/禁用量测。
点击「添加量测信号」继续。
```

**操作**：调用 `addComponentOutputMeasures` 添加量测

---

### 步骤 7：执行仿真 `[询问后执行]`

**PTA 更新**：显示仿真执行按钮和进度

```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.5.props.fields", "value": [
      {
        "key": "simulation_status",
        "label": "仿真状态",
        "type": "tag",
        "value": "ready",
        "options": [{"label": "准备就绪", "value": "ready"}]
      },
      {
        "key": "simulation_info",
        "label": "仿真信息",
        "type": "html",
        "value": "<p>配置已完成，点击下方按钮开始仿真。</p>"
      }
    ]},
    {"op": "set", "path": "blocks.5.props.actions", "value": [
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

---

### 步骤 8：结果分析 `[自动执行]`

**操作**：
1. 调用 `extract_and_check_data` 检查稳定性
2. 获取结果图片路径和文件路径

**PTA 更新**：展示仿真结果

```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {
      "op": "set",
      "value": {
        "actions": [
          {
            "patches": [
              {
                "op": "set",
                "value": "正在导出...",
                "path": "state.params.export_status"
              }
            ],
            "label": "导出结果",
            "style": "primary",
            "id": "export_results",
            "action_type": "apply_patch"
          },
          {
            "id": "new_simulation",
            "style": "secondary",
            "action_type": "apply_patch",
            "patches": [
              {
                "path": "state.params.new_sim",
                "value": true,
                "op": "set"
              }
            ],
            "label": "新建仿真"
          }
        ],
        "fields": [
          {
            "type": "tag",
            "key": "stability_result",
            "label": "稳定性分析",
            "value": "unstable",
            "options": [
              {
                "value": "stable",
                "label": "系统稳定"
              },
              {
                "label": "系统不稳定",
                "value": "unstable"
              }
            ]
          },
          {
            "label": "母线电压曲线",
            "type": "image",
            "showDownload": true,
            "subtitle": "母线电压有效值变化曲线",
            "showFullscreen": true,
            "key": "voltage_chart",
            "value": "http://192.168.130.30:9100/slxng/a39/n_1/Waveform/2026/2/5/wave_2026_02_05_02_53_02_508db5.html"
          },
          {
            "label": "发电机功率曲线",
            "showDownload": true,
            "key": "power_chart",
            "subtitle": "发电机有功功率变化曲线",
            "showFullscreen": true,
            "value": "http://192.168.130.30:9100/slxng/a39/n_1/Waveform/2026/2/5/wave_2026_02_05_02_53_05_1a76cb.html",
            "type": "image"
          },
          {
            "value": "http://192.168.130.30:9100/slxng/a39/n_1/Waveform/2026/2/5/wave_2026_02_05_02_53_05_0b5b6e.html",
            "label": "发电机转速曲线",
            "type": "image",
            "showDownload": true,
            "showFullscreen": true,
            "key": "speed_chart",
            "subtitle": "发电机转速变化曲线"
          },
          {
            "key": "angle_chart",
            "label": "发电机功角曲线",
            "showFullscreen": true,
            "type": "image",
            "showDownload": true,
            "subtitle": "发电机功角变化曲线",
            "value": "http://192.168.130.30:9100/slxng/a39/n_1/Waveform/2026/2/5/wave_2026_02_05_02_53_05_0dab8e.html"
          },
          {
            "type": "html",
            "label": "结果文件",
            "key": "result_files",
            "value": "<p><strong>仿真结果文件：</strong></p><ul><li><a href=\"http://192.168.130.30:9100/slxng/a39/n_1/Waveform/2026/2/5/wave_2026_02_05_02_53_02_508db5.html\" target=\"_blank\">母线电压曲线</a></li><li><a href=\"http://192.168.130.30:9100/slxng/a39/n_1/Waveform/2026/2/5/wave_2026_02_05_02_53_05_1a76cb.html\" target=\"_blank\">发电机功率曲线</a></li><li><a href=\"http://192.168.130.30:9100/slxng/a39/n_1/Waveform/2026/2/5/wave_2026_02_05_02_53_05_0b5b6e.html\" target=\"_blank\">发电机转速曲线</a></li><li><a href=\"http://192.168.130.30:9100/slxng/a39/n_1/Waveform/2026/2/5/wave_2026_02_05_02_53_05_0dab8e.html\" target=\"_blank\">发电机功角曲线</a></li></ul>"
          }
        ]
      },
      "path": "blocks.6.props"
    }
  ]
}
```

**对话引导**：
```
仿真已完成！
在「步骤7: 结果分析」标签页中查看：
- 稳定性分析结果
- 电压/功率/转速/攻角曲线图
- 结果文件下载链接
```

---

## Model B：批量 N-1 仿真流程

### 重要约束

- **禁止**调用任何 Model A 的工具（如 `createOrUpdateConfig`、`createOrUpdateJob`）
- **禁止**直接执行仿真，仅配置和提交批量任务
- 所有配置展示都在 PTA 中完成

---

### 步骤 1：查看默认配置 `[自动执行 + 等待确认]`

**操作**：调用 `get_default_config` 获取默认配置

**PTA 更新**：展示配置表格

```json
{
  "instance_name": "n1_simulation_batch",
  "patches": [
    {"op": "set", "path": "blocks.0.props.fields", "value": [
      {
        "key": "default_config",
        "label": "默认批量仿真配置（可编辑）",
        "type": "table",
        "tableEditable": true,
        "columns": [
          {"key": "tool", "title": "工具名称", "width": "200px"},
          {"key": "param", "title": "参数名", "width": "150px"},
          {"key": "default_value", "title": "默认值", "width": "150px"},
          {"key": "description", "title": "说明", "width": "250px"}
        ],
        "value": [
          {"tool": "load_data", "param": "case_name", "default_value": "IEEE14", "description": "系统案例名称"},
          {"tool": "run_power_flow", "param": "iterations", "default_value": "10", "description": "迭代次数"}
        ]
      }
    ]},
    {"op": "set", "path": "blocks.0.props.actions", "value": [
      {
        "id": "next_step",
        "label": "下一步",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.step1_confirmed", "value": true}]
      }
    ]}
  ]
}
```

**对话引导**：
```
展示了默认的批量仿真配置，您可以在表格中修改默认值。
完成后点击「下一步」继续。
```

**注意**：此处仅记录用户的修改意图，不实际调用修改工具

---

### 步骤 2：确认单次仿真流程模板 `[自动执行 + 等待确认]`

**PTA 更新**：展示单次仿真的流程模板和工具列表

```json
{
  "instance_name": "n1_simulation_batch",
  "patches": [
    {"op": "set", "path": "blocks.1.props.fields", "value": [
      {
        "key": "flow_template",
        "label": "单次仿真流程模板",
        "type": "json",
        "value": "{\"steps\": [\"load_data\", \"run_power_flow\", \"fault_analysis\", \"run_emt\", \"save_results\"]}"
      },
      {
        "key": "tool_list",
        "label": "涉及的工具",
        "type": "multiselect",
        "options": [
          {"label": "加载系统数据", "value": "load_data"},
          {"label": "执行潮流计算", "value": "run_power_flow"},
          {"label": "故障分析", "value": "fault_analysis"},
          {"label": "电磁暂态仿真", "value": "run_emt"},
          {"label": "保存结果", "value": "save_results"}
        ],
        "value": ["load_data", "run_power_flow", "fault_analysis", "run_emt", "save_results"]
      }
    ]},
    {"op": "set", "path": "blocks.1.props.actions", "value": [
      {
        "id": "confirm_flow",
        "label": "确认流程",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.step2_confirmed", "value": true}]
      }
    ]}
  ]
}
```

**对话引导**：
```
展示了单次仿真的流程模板，请在表格中查看流程步骤和涉及的工具。
确认无误后点击「确认流程」继续。
```

---

### 步骤 3：工具参数说明 `[自动执行 + 等待确认]`

**PTA 更新**：仅展示参数说明，不执行任何操作

```json
{
  "instance_name": "n1_simulation_batch",
  "patches": [
    {"op": "set", "path": "blocks.2.props.fields", "value": [
      {
        "key": "params_explanation",
        "label": "工具参数说明",
        "type": "table",
        "tableEditable": false,
        "columns": [
          {"key": "tool", "title": "工具", "width": "150px"},
          {"key": "param", "title": "参数名", "width": "120px"},
          {"key": "type", "title": "类型", "width": "100px"},
          {"key": "range", "title": "取值范围", "width": "150px"},
          {"key": "default", "title": "默认值", "width": "100px"},
          {"key": "description", "title": "说明", "width": "200px"}
        ],
        "value": [
          {"tool": "load_data", "param": "case_name", "type": "string", "range": "系统案例名", "default": "IEEE14", "description": "要加载的系统案例"},
          {"tool": "run_power_flow", "param": "iterations", "type": "int", "range": "1-100", "default": "10", "description": "最大迭代次数"}
        ]
      }
    ]},
    {"op": "set", "path": "blocks.2.props.actions", "value": [
      {
        "id": "next_step",
        "label": "下一步",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.step3_confirmed", "value": true}]
      }
    ]}
  ]
}
```

**对话引导**：
```
已展示各工具的参数说明，请查看参数类型、取值范围和默认值。
点击「下一步」继续生成批量配置。
```

**注意**：此处仅记录用户的参数配置意图，不执行任何工具

---

### 步骤 4：生成批量配置 JSON `[自动执行 + 等待确认]`

根据前面步骤收集的信息，生成批量仿真配置 JSON

**PTA 更新**：展示生成的 JSON 配置

```json
{
  "instance_name": "n1_simulation_batch",
  "patches": [
    {"op": "set", "path": "blocks.3.props.fields", "value": [
      {
        "key": "batch_config",
        "label": "批量仿真配置（可编辑）",
        "type": "json",
        "value": "{\n  \"steps\": [\n    {\n      \"name\": \"load_data\",\n      \"params\": {\"case_name\": \"IEEE14\"}\n    },\n    {\n      \"name\": \"run_power_flow\",\n      \"params\": {\"iterations\": {\"range\": {\"start\": 5, \"end\": 15, \"step\": 5}}}\n    },\n    {\n      \"name\": \"fault_analysis\",\n      \"params\": {\n        \"fault_bus\": {\"choices\": [1, 2, 3]},\n        \"fault_type\": {\"choices\": [\"a\", \"b\", \"c\"]}\n      }\n    }\n  ],\n  \"zip\": [[\"fault_analysis.fault_bus\", \"fault_analysis.fault_type\"]]\n}",
        "description": "可直接编辑 JSON 配置，参数取值方式支持：固定值、choices、range、random"
      }
    ]},
    {"op": "set", "path": "blocks.3.props.actions", "value": [
      {
        "id": "edit_config",
        "label": "修改配置",
        "style": "secondary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.config_editing", "value": true}]
      },
      {
        "id": "confirm_config",
        "label": "确认配置",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.step4_confirmed", "value": true}]
      }
    ]}
  ]
}
```

**对话引导**：
```
已生成批量仿真配置 JSON，您可以直接在 JSON 编辑器中修改。
支持以下参数取值方式：
- 固定值：直接赋值，如 "case_name": "IEEE14"
- choices（枚举）：从列表中选择，如 {"choices": [1, 2, 3]}
- range（范围）：按步长遍历，如 {"range": {"start": 5, "end": 15, "step": 5}}
- random（随机）：在范围内随机采样，如 {"random": {"low": 0.8, "high": 1.2, "count": 10}}

确认无误后点击「确认配置」继续。
```

---

### 步骤 5：参数检查与批量次数确认 `[自动执行 + 等待确认]`

**操作**：检查配置是否使用了 choices、range 或 random

**PTA 更新**：
- 如果有变参数，显示预计批量次数
- 如果全是固定值，询问用户指定批量次数

```json
{
  "instance_name": "n1_simulation_batch",
  "patches": [
    {"op": "set", "path": "blocks.4.props.fields", "value": [
      {
        "key": "batch_info",
        "label": "批量仿真信息",
        "type": "html",
        "value": "<p><strong>预计批量次数：</strong>9 次</p><p><strong>变参数：</strong>iterations (3个值) × fault_bus (3个值)</p>"
      }
    ]},
    {
      "key": "batch_count",
      "label": "批量次数",
      "type": "number",
      "value": 9,
      "description": "如需修改批量次数，请在此处输入",
      "editable": true
    },
    {"op": "set", "path": "blocks.4.props.actions", "value": [
      {
        "id": "confirm_batch",
        "label": "确认并提交",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.step5_confirmed", "value": true}]
      }
    ]}
  ]
}
```

**对话引导**：
```
配置检查完成：
- 预计执行 9 次批量仿真
- 变参数：iterations (3个值) × fault_bus (3个值)

确认后点击「确认并提交」提交批量仿真任务。
```

---

### 步骤 6：提交批量仿真任务 `[询问后执行]`

**对话引导**：
```
准备提交批量仿真任务。
确认提交？回复「确认」或「取消」。
```

**操作**：调用 `submit_batch_simulation` 提交任务

**PTA 更新**：显示任务 ID

```json
{
  "instance_name": "n1_simulation_batch",
  "patches": [
    {"op": "set", "path": "blocks.5.props.fields", "value": [
      {
        "key": "task_id",
        "label": "任务 ID",
        "type": "text",
        "value": "batch_20250204_001",
        "description": "请保存此任务 ID 用于后续查询"
      },
      {
        "key": "task_status",
        "label": "任务状态",
        "type": "tag",
        "value": "submitted",
        "options": [{"label": "已提交", "value": "submitted"}]
      }
    ]}
  ]
}
```

**对话引导**：
```
✅ 批量仿真任务已成功提交！
任务 ID：batch_20250204_001

您可以使用以下命令查询任务状态和结果：
- 查询状态：查询任务状态
- 获取结果：获取仿真结果
- 查看所有任务：查看批量任务列表
```

---

### 步骤 7：结果查询与结构化输出 `[询问后执行]`

**操作**：
1. 调用 `query_batch_simulation_status` 查询状态
2. 如完成，调用 `get_batch_simulation_result` 获取结果

**PTA 更新**：以表格形式展示所有结果

```json
{
  "instance_name": "n1_simulation_batch",
  "patches": [
    {"op": "set", "path": "blocks.6.props.fields", "value": [
      {
        "key": "batch_results",
        "label": "批量仿真结果汇总",
        "type": "table",
        "columns": [
          {"key": "index", "title": "序号", "width": "80px"},
          {"key": "stability", "title": "稳定性", "width": "100px", "renderType": "tag", "tagType": "value => value === 'stable' ? 'success' : 'error'"},
          {"key": "result_file", "title": "结果文件", "width": "250px", "renderType": "text"},
          {"key": "voltage_chart", "title": "电压曲线", "width": "200px", "renderType": "image"},
          {"key": "power_chart", "title": "功率曲线", "width": "200px", "renderType": "image"}
        ],
        "value": [
          {"index": 1, "stability": "stable", "result_file": "results_001.hdf5", "voltage_chart": "https://minio.example.com/voltage_001.html", "power_chart": "https://minio.example.com/power_001.html"},
          {"index": 2, "stability": "unstable", "result_file": "results_002.hdf5", "voltage_chart": "https://minio.example.com/voltage_002.html", "power_chart": "https://minio.example.com/power_002.html"}
        ]
      }
    ]}
  ]
}
```

**对话引导**：
```
批量仿真已完成！
在「步骤7: 结果查询」标签页中查看所有仿真结果。
每个结果包含：
- 稳定性判断
- 结果文件下载链接
- 电压曲线和功率曲线
```

---

## PTA 使用技巧

### 状态管理

**获取用户输入**：
```python
# 推荐使用 validate_completion（返回更多信息）
result = validate_completion({"instance_name": "n1_simulation"})
state = result['state']['params']

# 或使用 get_schema（返回完整 schema）
schema = get_schema({"instance_name": "n1_simulation"})
state = schema['state']['params']
```

**切换标签页**：
```python
# 切换到指定 block（tab）
switch_ui({"instance_name": "n1_simulation", "block_id": "step2_powerflow"})
```

### 错误处理

如果仿真失败，在 PTA 中展示错误信息：

```json
{
  "instance_name": "n1_simulation",
  "patches": [
    {"op": "set", "path": "blocks.5.props.fields", "value": [
      {
        "key": "error_message",
        "label": "错误信息",
        "type": "html",
        "value": "<div style=\"color: #f5222d;\"><strong>仿真失败：</strong><p>潮流计算不收敛，请检查参数配置。</p></div>"
      }
    ]},
    {"op": "set", "path": "blocks.5.props.actions", "value": [
      {
        "id": "retry",
        "label": "重新尝试",
        "style": "primary",
        "action_type": "apply_patch",
        "patches": [{"op": "set", "path": "state.params.retry", "value": true}]
      }
    ]}
  ]
}
```

---

## 总结

本指南提供了使用 PTA 可视化组件完成 N-1 仿真的完整流程，包括：

1. **PTA 实例初始化**：使用 tabs 布局，每个步骤一个 tab
2. **参数配置**：使用可编辑表格收集用户输入
3. **结果展示**：使用表格和图片组件展示仿真结果
4. **状态管理**：使用 `validate_completion` 获取用户修改
5. **错误处理**：在 PTA 中展示错误信息并提供重试选项

关键要点：
- 所有交互都通过 PTA 完成，对话框仅用于流程引导
- 使用表格的 `tableEditable` 属性实现可编辑配置
- 使用 `validate_completion` 获取用户修改后的数据
- 使用 `image` 组件展示仿真结果图片
- 使用 `switch_ui` 在不同步骤间切换
