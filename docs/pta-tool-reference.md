<PTA_TOOL_REFERENCE>
<KEY_WORDS>
ui_schema :  记录在内存中,用于渲染UI界面的json schema,查看 **UI_SCHEMA_STRUCTURE**了解它的结构
patch     :  补丁,用于修改ui_schema来实现UI界面的修改(也包括一些处理逻辑的设计),查看**PATCH_EXAMPLE**。
block     :  一个block是一个UI元素,包含一个或多个field,一个或多个action
field     :  最小的UI元素,用于展示数据或收集数据,查看 **FIELD_STRUCTURE**了解它的结构
action    :  以按钮的形式呈现,用于触发一个或多个操作,查看 **ACTION_STRUCTURE**了解它的结构
path      :  用于定位schema中的某个元素,使用JSON指针语法从ui_schema根目录开始索引
instance  :  一个实例是一个完整的单页面PTA应用,包含一个ui_schema和一个运行时状态
state     :  ui_schema中数据存储的地方,由params(原始数据)和runtime(运行数据)两者构成
</KEY_WORDS>
<TOOL_DEFINITION>
- NAME: patch_ui_state
- DESCRIPTION: 修改 UI 状态
- PARAMETERS:
  instance_name: str - 决定你要将修改应用到哪个实例,使用以下值之一:
    - "__CREATE__" - 创建新实例
    - "__DELETE__" - 删除实例
    - 现有实例名 - 修改现有实例
  patches: list[patch] - patch字典数组,详见 **SCHEMA_PATCH_DESCRIPTION**
  new_instance_name: str | None - instance_name为"__CREATE__"时提供的新实例名
  target_instance_name: str | None - instance_name为"__DELETE__"时提供的目标实例名
</TOOL_DEFINITION>

<TOOL_DEFINITION>
- NAME: get_schema
- DESCRIPTION: 获取实例的完整 ui_schema
- PARAMETERS:
  instance_name: str - 要获取 ui_schema 的实例名
</TOOL_DEFINITION>

<TOOL_DEFINITION>
- NAME: list_instances
- DESCRIPTION: 列出所有可用实例
</TOOL_DEFINITION>

<TOOL_DEFINITION>
- NAME: validate_completion
- DESCRIPTION: 快速诊断UI实例状态,返回当前结构摘要和调试信息,指导进行完成度检查
- PARAMETERS:
  instance_name: str - 要诊断的实例名
- 返回: {status, debug_info, state_summary, structure_summary, fields_summary, actions_summary, hints}
  - debug_info: {instance_exists, instance_name, block_count, field_count, action_count, state_params_keys, state_runtime_keys, layout_type}
  - state_summary: {params: {键值对}, runtime: {键值对}} - 完整的状态数据
  - structure_summary: [{id, title, layout, fields: [{key, type, label}], actions: [{id, type, label}]}, ...]
    - 第一项(id="__global__")是顶层全局actions,后续项是各block的结构
  - fields_summary: [{key, type, label, path, has_value}, ...] - 所有字段的紧凑列表
  - actions_summary: [{id, label, type, patch_count, scope}, ...] - 所有actions的紧凑列表(scope: "global"|"block")
  - hints: 基于当前状态的改进建议
- 调用此工具获取界面快照,判断完成度,决定后续patch操作
- 示例: {"instance_name":"counter"} -> 返回计数器的完整结构概览、状态值和缺失组件提示
</TOOL_DEFINITION>

<TOOL_DEFINITION>
- NAME: switch_ui
- DESCRIPTION: 切换UI界面，支持切换到指定实例或切换到实例内的指定block
- PARAMETERS:
  instance_name: str | None - 要切换到的实例名，不传则不切换实例
  block_id: str | None - 要切换到的block ID，不传则不切换block（例如在Tabs布局中切换标签页）
- 使用方式：
  1. 切换到实例: {"instance_name": "demo"}
  2. 切换到实例内的block: {"instance_name": "demo", "block_id": "counter_block"}
  3. 仅切换当前实例内的block: {"block_id": "counter_block"}
</TOOL_DEFINITION>

<PATCH_DESCRIPTION>
patch包含以下键:
  - "op": 可选值以及示例请查看**PATCH_EXAMPLE**
  - "path": "blocks.xxx"|"states.xxx"|"actions.xxx"|"layout.xxx"
  - "value": 用于操作所选path的字典,需要根据界面的结构来确定value的结构,因此将详细讨论界面各个组件的结构,详见: **UI_SCHEMA_STRUCTURE**,**FIELD_STRUCTURE**,**ACTION_STRUCTURE**
</PATCH_DESCRIPTION>

<UI_SCHEMA_STRUCTURE>
ui_schema 包含 page_key state layout blocks actions 5个键。
每个block有自己的actions,和全局actions不冲突。
field和action的结构参见:**FIELD_STRUCTURE**,**ACTION_STRUCTURE**
page_key - 页面标识符,创建实例时通过 path="page_key" 设置
state - 包含状态参数和运行时参数字典 {params: dict[str, Any], runtime: dict[str, Any]}
layout - 布局参数字典,将决定blocks如何布局,包含以下键:
  - "type": "single"|"flex"|"grid"|"tabs"
  - "columns": 仅用于grid布局
  - "gap": 间距
blocks - list[block],包含界面所有block,每个block包含以下键:
  - "id": 字符串,用于唯一标识block,将显示为block的名称
  - "layout": 布局参数字典,将决定block中的field如何布局,可选值为:"form"|"grid"|"tabs"|"accordition"
  - "props": 字典,用于指定block的配置,根据layout的不同,props的结构也不同
    form布局的props: {fields: list[field], actions: list[action]}
    grid布局的props:{cols: int, gap: int, fields: list[field], actions: list[action]}
    tabs布局的props:{tabs: list[dict[label: str, fields: list[field], actions: list[action]]]}
    accordition布局的props:{panels: list[dict[title: str, fields: list[field], actions: list[action]]]}
actions - list[action],全局action列表
</UI_SCHEMA_STRUCTURE>

<FIELD_STRUCTURE>
field 包含以下键:
  - "type": 字段类型,可选值:text/textarea/number/select/radio/multiselect/checkbox/json/image/table/component/date/datetime/file/html/tag/progress/badge
  - "label": 字符串,字段显示标签
  - "key": 字符串,字段唯一标识,用于从 state 中读取和写入数据
  - "value": any,字段值（可选）
  - "description": 字符串|None,字段描述（可选）
  - "editable": 布尔值,默认 true,是否可编辑
  - "required": 布尔值,默认 false,是否必填
  - "disabled": 布尔值,默认 false,是否禁用
  - "placeholder": 字符串|None,占位符（可选）

根据type的不同有额外字段:
  - select/radio/multiselect 类型:用于渲染选择器
    - "options": 选项对象数组,每个选项包含 {label: string, value: string, disabled: bool, description: string}
    - "multiple": select 类型可选,布尔值,默认 false,是否多选
  - image 类型:用于渲染图片或HTML
    - "showFullscreen": 布尔值,默认 true,显示全屏按钮
    - "showDownload": 布尔值,默认 true,显示下载按钮
    - "imageHeight": 字符串,默认 "auto",图片高度
    - "imageFit": 字符串,可选值 "contain"/"cover"/"fill",图片适应方式
    - "lazy": 布尔值,默认 false,懒加载
    - "fallback": 字符串|None,加载失败回退内容
    - "subtitle": 字符串|None,子标题
    - "alt": 字符串|None,替代文本
  - table 类型:用于绘制表格
    - "columns": 列配置数组,参见**COLUMN_STRUCTURE**
    - "rowKey": 字符串,行唯一标识字段,默认 "id"
    - "bordered": 布尔值,默认 true,显示边框
    - "striped": 布尔值,默认 true,斑马纹
    - "hover": 布尔值,默认 true,悬停效果
    - "emptyText": 字符串,默认 "暂无数据",空数据提示
    - "tableEditable": 布尔值,默认 false,表格是否可编辑
    - "showHeader": 布尔值,默认 true,显示表头
    - "showPagination": 布尔值,默认 false,显示分页
    - "pageSize": 数字,默认 10,每页显示条数
    - "maxHeight": 字符串|None,最大高度
    - "compact": 布尔值,默认 false,紧凑模式
    - "rowSelection": 布尔值,默认 false,行选择
  - component 类型:用于组件中嵌入组件
    - "block_config": 要嵌入的block配置,结构同**block**
</FIELD_STRUCTURE>

<ACTION_STRUCTURE>
action 包含以下键:
  - "id": 字符串,不显示的唯一标识
  - "label": 字符串,显示的标签
  - "style": 字符串,按钮样式,可选值:primary/secondary/danger/warning/success,默认 secondary
  - "action_type": 字符串,点击触发的事件类型,可选值:apply_patch/navigate/navigate_block/api
  - "patches": action_type=apply_patch时,将执行的patch数组,详见 **PATCH_DESCRIPTION**
  - "target_instance": action_type=navigate时跳转到target_instance（实例导航）
  - "target_block": action_type=navigate_block时跳转到target_block（block导航，同实例内滚动到指定block）
  - "api": action_type=api 时,将执行的api调用,详见**API_CONFIG_STRUCTURE**
  - "disabled": 布尔值,默认 false,是否禁用
</ACTION_STRUCTURE>

<API_CONFIG_STRUCTURE>
api 配置包含以下键,用于 action_type=api 的外部 API 调用:
  - "url": 字符串 - API 请求地址
  - "method": 字符串 - HTTP 方法,默认 "POST",可选值:GET/POST/PUT/DELETE
  - "headers": 对象 - 请求头字典,默认 {}
  - "body_template": 对象|字符串|null - 请求体模板,支持 ${state.params.xxx} 模板语法
  - "body_template_type": 字符串 - 请求体类型,默认 "json",可选值:json/form
  - "timeout": 数字 - 请求超时时间(秒),默认 30
  - "response_mappings": 对象 - 响应映射,将 API 响应映射到 state.params,格式为 {目标路径: JSON路径}
    - 特殊值 "status_code": 用于获取 HTTP 状态码
    - 示例: {"state.params.api_response": "json", "state.params.api_status": "status_code"}
    - 当映射值为对象或数组时,会自动转换为 JSON 字符串显示
  - "error_mapping": 对象 - 错误映射,将 API 错误映射到 state.runtime,格式同 response_mappings
</API_CONFIG_STRUCTURE>

<API_EXAMPLE>
- 基础 API 调用示例(调用 httpbin.org/post):
  {
    "id": "call_api",
    "label": "调用 API",
    "style": "primary",
    "action_type": "api",
    "api": {
      "url": "https://httpbin.org/post",
      "method": "POST",
      "body_template": {"data": "${state.params.api_request_data}"},
      "body_template_type": "json",
      "timeout": 30,
      "response_mappings": {
        "state.params.api_response": "json",
        "state.params.api_status": "status_code"
      }
    }
  }

- 模板语法使用(动态传递请求数据):
  {
    "api": {
      "url": "https://api.example.com/users",
      "method": "POST",
      "body_template": {
        "name": "${state.params.username}",
        "email": "${state.params.useremail}",
        "timestamp": "${state.runtime.timestamp}"
      },
      "body_template_type": "json",
      "response_mappings": {
        "state.params.user_id": "data.id",
        "state.params.user_name": "data.name"
      }
    }
  }

- 带请求头的 API 调用:
  {
    "api": {
      "url": "https://api.example.com/protected",
      "method": "GET",
      "headers": {
        "Authorization": "Bearer ${state.params.token}",
        "Content-Type": "application/json"
      },
      "response_mappings": {
        "state.params.result": "data"
      }
    }
  }

- 使用 JSONPath 提取嵌套数据:
  {
    "api": {
      "url": "https://api.example.com/search",
      "response_mappings": {
        "state.params.items": "results.items",
        "state.params.total": "results.total_count",
        "state.params.status_code": "status_code"
      }
    }
  }
</API_EXAMPLE>

<PATCH_EXAMPLE>
op 参数可选的值及示例使用如下:
  - "set": 直接设置值,支持模板渲染
    - 参数: path(string), value(any), 支持字符串/字典/列表
    - 示例: {"op": "set", "path": "state.params.name", "value": "张三"}
    - 示例: {"op": "set", "path": "state.params.count", "value": 42}

  - "add": 添加块到schema
    - 参数: path(string), value(block对象)
    - 示例: {"op": "add", "path": "blocks", "value": {"id": "new_block", "layout": "form", ...}}

  - "remove": 从schema移除块
    - 参数: path(string), value({id: string})
    - 示例: {"op": "remove", "path": "blocks", "value": {"id": "block_to_remove"}}

  - "append_to_list": 追加元素到列表末尾
    - 参数: path(string), value(单个对象或数组)
    - 示例: {"op": "append_to_list", "path": "state.params.users", "value": {"id": "1", "name": "李四"}}

  - "prepend_to_list": 插入元素到列表开头
    - 参数: path(string), value(单个对象或数组)
    - 示例: {"op": "prepend_to_list", "path": "state.params.messages", "value": {"text": "最新消息"}}

  - "remove_from_list": 从列表删除元素
    - 参数: path(string), value({key, value, index?})
    - key: 匹配字段名,默认"id"
    - value: 要删除的值
    - index: -1删除所有匹配项,否则删除首个匹配
    - 示例: {"op": "remove_from_list", "path": "state.params.users", "value": {"key": "id", "value": "${state.params.temp_rowData.id}"}}

  - "filter_list": 按条件过滤列表
    - 参数: path(string), value({key, operator, value})
    - key: 过滤字段名
    - operator: 操作符,支持==/!=/>/</>=/<=,默认==
    - value: 比较值
    - 示例: {"op": "filter_list", "path": "state.params.todos", "value": {"key": "completed", "operator": "!=", "value": true}}

  - "update_list_item": 更新列表元素
    - 参数: path(string), value({key, value, updates})
    - key: 匹配字段名,默认"id"
    - value: 要更新的元素的key值
    - updates: 要更新的字段字典
    - 示例: {"op": "update_list_item", "path": "state.params.users", "value": {"key": "id", "value": "1", "updates": {"name": "王五"}}}

  - "remove_last": 删除列表最后一项
    - 参数: path(string)
    - 示例: {"op": "remove_last", "path": "state.params.items"}

  - "merge": 合并对象
    - 参数: path(string), value(对象)
    - 示例: {"op": "merge", "path": "state.params.config", "value": {"theme": "dark", "fontSize": 16}}

  - "increment": 增加数值
    - 参数: path(string), value(delta: number)
    - 示例: {"op": "increment", "path": "state.params.count", "value": 1}

  - "decrement": 减少数值
    - 参数: path(string), value(delta: number)
    - 示例: {"op": "decrement", "path": "state.params.count", "value": 1}

  - "toggle": 切换布尔值
    - 参数: path(string)
    - 示例: {"op": "toggle", "path": "state.params.visible"}
more example: see **COMPREHENSIVE_EXAMPLE**
</PATCH_EXAMPLE>

<COMPREHENSIVE_EXAMPLE>
- 模板使用: 支持${path}语法引用state值,支持字符串/字典/列表中的嵌套模板
  - 基础state引用:
    {"op": "set", "path": "state.params.message", "value": "姓名: ${state.params.name}"}
  - 选项组件引用(支持.label获取标签):
    {"op": "set", "path": "state.params.status_display", "value": "状态: ${state.params.status.label} (${state.params.status})"}
    {"op": "set", "path": "state.params.categories_display", "value": "分类: ${state.params.categories.label}"}
  - 嵌套引用(字典/列表中的模板):
    {"op": "append_to_list", "path": "state.params.users",
      "value": {"id": "${state.params.next_id}", "name": "${state.params.new_name}", "status": "${state.params.status.label}"}}
  - 综合示例(动态添加数据):
    {
      "op": "append_to_list", "path": "state.params.dynamic_users",
      "value": {"id": "${state.params.next_id}", "name": "${state.params.new_name}", "email": "${state.params.new_email}", "added_at": "${state.runtime.timestamp}"}
    }

- 创建新实例:
  - 使用 "__CREATE__" 作为 instance_name 创建新实例
  - 必须提供 new_instance_name 参数
  - 使用 "set" 操作定义实例结构(page_key/state/blocks/actions)
  - 示例:
    {
      "instance_name": "__CREATE__",
      "new_instance_name": "my_app",
      "patches": [
        {"op": "set", "path": "page_key", "value": "my_app"},
        {"op": "set", "path": "state", "value": {"params": {}, "runtime": {}}},
        {"op": "set", "path": "blocks", "value": [
          {"id": "main_block", "layout": "form", "props": {"fields": [{"key": "name", "label": "姓名", "type": "text"}], "actions": []}}
        ]},
        {"op": "set", "path": "actions", "value": []}
      ]
    }

- 删除实例:
  - 使用 "__DELETE__" 作为 instance_name 删除实例
  - 必须提供 target_instance_name 参数
  - 示例:
    {
      "instance_name": "__DELETE__",
      "target_instance_name": "my_app",
      "patches": []
    }

- 创建复杂表格示例（包含多种列类型和可编辑功能）:
  - 示例: 创建一个任务管理表格，包含状态标签、进度条、图片头像、操作按钮和可编辑列
  {
    "instance_name": "__CREATE__",
    "new_instance_name": "task_manager",
    "patches": [
      {"op": "set", "path": "page_key", "value": "task_manager"},
      {"op": "set", "path": "state", "value": {
        "params": {
          "tasks": [
            {"id": "1", "name": "完成文档编写", "status": "active", "progress": {"current": 80, "total": 100}, "assignee": "张三", "priority": "high"},
            {"id": "2", "name": "代码审查", "status": "pending", "progress": {"current": 30, "total": 100}, "assignee": "李四", "priority": "medium"},
            {"id": "3", "name": "部署上线", "status": "completed", "progress": {"current": 100, "total": 100}, "assignee": "王五", "priority": "low"}
          ]
        },
        "runtime": {}
      }},
      {"op": "set", "path": "blocks", "value": [
        {
          "id": "task_block",
          "layout": "form",
          "props": {
            "fields": [{
              "key": "tasks",
              "label": "任务列表",
              "type": "table",
              "tableEditable": true,
              "showPagination": true,
              "pageSize": 10,
              "bordered": true,
              "striped": true,
              "hover": true,
              "columns": [
                {"key": "id", "title": "ID", "width": "80px", "sortable": true},
                {"key": "name", "title": "任务名称", "width": "200px", "editable": true},
                {
                  "key": "status",
                  "title": "状态",
                  "width": "120px",
                  "renderType": "tag",
                  "tagType": "value => value === 'active' ? 'success' : value === 'completed' ? 'success' : 'warning'",
                  "editable": true,
                  "editType": "select",
                  "options": [{"label": "进行中", "value": "active"}, {"label": "待处理", "value": "pending"}, {"label": "已完成", "value": "completed"}]
                },
                {
                  "key": "progress",
                  "title": "进度",
                  "width": "150px",
                  "renderType": "progress"
                },
                {
                  "key": "assignee",
                  "title": "负责人",
                  "width": "100px",
                  "editable": true
                },
                {
                  "key": "priority",
                  "title": "优先级",
                  "width": "100px",
                  "renderType": "tag",
                  "tagType": "value => value === 'high' ? 'error' : value === 'medium' ? 'warning' : 'default'",
                  "editable": true,
                  "editType": "select",
                  "options": [{"label": "高", "value": "high"}, {"label": "中", "value": "medium"}, {"label": "低", "value": "low"}]
                },
                {
                  "key": "actions",
                  "title": "操作",
                  "width": "180px",
                  "renderType": "mixed",
                  "components": [
                    {"type": "button", "buttonLabel": "编辑", "buttonStyle": "primary", "actionId": "edit_task"},
                    {"type": "spacer", "width": "8px"},
                    {"type": "button", "buttonLabel": "删除", "buttonStyle": "danger", "actionId": "delete_task", "confirmMessage": "确认删除此任务？"}
                  ]
                }
              ]
            }],
            "actions": [
              {"id": "add_task", "label": "添加任务", "style": "primary", "action_type": "apply_patch", "patches": [
                {"op": "append_to_list", "path": "state.params.tasks", "value": {"id": "${state.runtime.next_id}", "name": "新任务", "status": "pending", "progress": {"current": 0, "total": 100}, "assignee": "", "priority": "medium"}}
              ]}
            ]
          }
        }
      ]},
      {"op": "set", "path": "actions", "value": []}
    ]
  }

- 布局使用示例:
  - Grid布局示例（2列网格）:
    {
      "instance_name": "my_app",
      "patches": [
        {"op": "set", "path": "layout", "value": {"type": "grid", "columns": 2, "gap": "20px"}},
        {"op": "set", "path": "blocks", "value": [
          {"id": "block1", "layout": "form", "props": {"fields": [{"key": "field1", "label": "字段1", "type": "text"}], "actions": []}},
          {"id": "block2", "layout": "form", "props": {"fields": [{"key": "field2", "label": "字段2", "type": "number"}], "actions": []}}
        ]}
      ]
    }

  - Tabs布局示例（多个标签页）:
    {
      "instance_name": "my_app",
      "patches": [
        {"op": "set", "path": "layout", "value": {"type": "tabs"}},
        {"op": "set", "path": "blocks", "value": [
          {
            "id": "tabs_block",
            "layout": "tabs",
            "props": {
              "tabs": [
                {"label": "基本信息", "fields": [{"key": "name", "label": "姓名", "type": "text"}], "actions": []},
                {"label": "联系方式", "fields": [{"key": "email", "label": "邮箱", "type": "text"}], "actions": []},
                {"label": "系统设置", "fields": [{"key": "theme", "label": "主题", "type": "select", "options": [{"label": "亮色", "value": "light"}, {"label": "暗色", "value": "dark"}]}], "actions": []}
              ]
            }
          }
        ]}
      ]
    }

  - Flex布局示例（自适应排列）:
    {
      "instance_name": "my_app",
      "patches": [
        {"op": "set", "path": "layout", "value": {"type": "flex", "gap": "16px"}},
        {"op": "set", "path": "blocks", "value": [
          {"id": "block1", "layout": "form", "props": {"fields": [{"key": "field1", "label": "字段1", "type": "text"}], "actions": []}},
          {"id": "block2", "layout": "form", "props": {"fields": [{"key": "field2", "label": "字段2", "type": "number"}], "actions": []}},
          {"id": "block3", "layout": "form", "props": {"fields": [{"key": "field3", "label": "字段3", "type": "select"}], "actions": []}}
        ]}
      ]
    }

  - Accordion布局示例（可折叠面板）:
    {
      "instance_name": "my_app",
      "patches": [
        {"op": "set", "path": "layout", "value": {"type": "single"}},
        {"op": "set", "path": "blocks", "value": [
          {
            "id": "accordion_block",
            "layout": "accordion",
            "props": {
              "panels": [
                {"title": "个人资料", "fields": [{"key": "name", "label": "姓名", "type": "text"}], "actions": []},
                {"title": "工作信息", "fields": [{"key": "department", "label": "部门", "type": "text"}], "actions": []},
                {"title": "其他设置", "fields": [{"key": "timezone", "label": "时区", "type": "text"}], "actions": []}
              ]
            }
          }
        ]}
      ]
    }
</COMPREHENSIVE_EXAMPLE>

<COLUMN_STRUCTURE>
"columns": 列配置数组,每列包含
  - key: string - 列的键
  - title: string - 列的标题
  - width: string - 列的宽度
  - sortable: bool - 是否可排序,默认false
  - filterable: bool - 是否可过滤,默认false
  - align: string - 对齐方式,可选值:left/center/right
  - renderType: string - 渲染类型,可选值:text/tag/bage/progress/image/mixed
  - tagType: string - 标签类型,当renderType=tag时使用,用于tag渲染,支持表达式如:'value => value === \"active\" ? \"success\" : \"default\"'
  - badge_color:string - 徽标颜色,当renderType=badge时使用,用于badge渲染,如'#1890ff'
  - components: list[dict[str, Any]] - 混合渲染组件配置,当renderType=mixed时使用,支持 text, tag, badge, progress, image, button, spacer
  - editable: bool - 该列是否可编辑,默认true,仅当tableEditable=true时生效
  - editType: string - 编辑器类型,可选值:text/number/select,默认text
  - options: list[{label: string, value: string}] - 选项列表,仅当editType=select时使用
</COLUMN_STRUCTURE>

<NOTE>
你的MCP调用应当满足以下准则:
- 列表、字典列表等结构如果不传参数而又必须要求传递参数，请使用"[]"或者"[{}]"进行传递,请尽量不要出现这种情况。
- 优先使用validate_completion而非get_schema来获取页面结构信息(第一次需要初步了解详细信息时除外)。
- 注意使用合理的组件和布局,在完成功能的基础上尽量美观。
</NOTE>
</PTA_TOOL_REFERENCE>