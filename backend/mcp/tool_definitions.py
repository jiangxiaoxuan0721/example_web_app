"""MCP工具定义文件

此文件定义所有MCP工具。实现逻辑在tool_implements.py中。
工具描述会被注入到Agent上下文,必须完整、准确。
"""

from typing import Any
from fastmcp import FastMCP

mcp = FastMCP("ui-patch-server")


# ===== 万能修改工具(推荐使用)=====

@mcp.tool()
async def patch_ui_state(
    instance_id: str,
    patches: list[dict[str, Any]] = [],
    new_instance_id: str | None = None,
    target_instance_id: str | None = None
) -> dict[str, Any]:
    """
通过JSON Patch修改UI Schema。

<parameter>
    instance_id: 三种模式:
        - "example_instance" 引用已创建的实例
        - "__CREATE__" 创建实例,需要指定new_instance_id
        - "__DELETE__" 删除实例,需要指定target_instance_id
    patches: Patch操作数组,每项包含op、path、value
</parameter>

<op>
    set: 设置或更新值,路径不存在则创建
    add: 向数组末尾添加元素(blocks、actions、fields等)
    remove: 从数组删除元素(通过id或key匹配)
</op>

<path>
    state.params.xxx: 状态参数
    state.runtime.xxx: 运行时数据
    layout.type: 顶层布局类型(single/grid/flex/tabs),决定blocks的布局
    layout.columns: grid布局列数
    layout.gap: 布局间距
    blocks.0: 第一个block
    blocks.0.type: block内部布局(form/grid/tabs/accordion),决定fields的布局
    blocks.0.props.fields: block的字段数组
    blocks.0.props.fields.0.label: 第一个字段的label属性
    blocks.0.props.cols: grid布局列数
    blocks.0.props.tabs: tabs布局的标签页数组
    blocks.0.props.panels: accordion布局的面板数组
    blocks.0.props.actions: block级actions
    actions: 全局actions
</path>

<field_types>
字段类型(19种):
    输入: text, number, textarea, checkbox, json, date, datetime, file
    选择: select, radio, multiselect
    显示: html, image, tag, progress, badge, table, modal, component
</field_types>

<field_type_details>
各显示类型详细说明:

    image: 图片/HTML内容渲染
        - 支持图片URL(.jpg/.png/.gif等)
        - 支持HTML文件URL(.html结尾,如波形图链接)
        - HTML链接会自动识别,点击工具栏"全屏"或"下载"按钮查看
        - 支持属性: imageHeight(高度), imageFit(适应方式), showFullscreen(全屏), showDownload(下载)

    html: HTML富内容渲染
        - 支持HTML字符串或HTML文件URL
        - 支持模板渲染(${state.xxx}语法)
        - 图片可点击全屏查看
        - 自动处理表格溢出

    table: 表格数据展示
        - 支持分页、排序、悬停高亮
        - 列支持多种渲染类型(见table_render_types)
        - 支持mixed混合渲染(图片+标签+按钮组合)
</field_type_details>

<table_render_types>
表格列渲染类型(renderType):
    text: 普通文本
    tag: 标签(支持tagType动态样式)
    badge: 徽章(支持badgeColor颜色)
    progress: 进度条(值需包含current/total)
    image: 图片/HTML内容:
        - 支持.jpg/.png/.gif等图片URL
        - 支持.html文件URL(如波形图链接),点击"查看内容"按钮全屏展示
        - 支持内联HTML字符串(以<开头)
    mixed: 混合渲染(支持components数组组合多种类型)
</table_render_types>

<block_types>
Block布局类型(4种):
    form: 基础表单布局(默认,卡片式容器,字段垂直堆叠)
    grid: 网格布局(多列并排,响应式)
    tabs: 标签页布局(分页显示内容)
    accordion: 折叠面板布局(可展开/收起)
</block_types>

<block_props>
Block属性配置:
    通用属性:
        fields: 字段数组(所有布局必需)
        actions: block级操作按钮数组
        title: 区块标题(可选)

    Grid布局专属:
        cols: 列数(默认3,范围1-12)
        gap: 列间距(默认"16px")

    Tabs布局专属:
        tabs: 标签页数组,每项包含 label 和 fields

    Accordion布局专属:
        panels: 面板数组,每项包含 title 和 fields
</block_props>

<top_level_layout>
顶层Layout配置(控制blocks和全局actions的排列):
    layout.type: 顶层布局类型(默认"single")
    layout.columns: 列数(grid布局专用,默认2)
    layout.gap: 间距(grid/flex布局,默认"20px")

    布局类型:
        single: 垂直堆叠(默认,blocks按顺序垂直排列,actions在底部)
        grid: 网格布局(blocks多列并排,actions在底部)
        flex: 水平布局(blocks水平排列,自动换行,actions在底部)
        tabs: 标签页布局(blocks分组到不同标签页,actions在底部)
</top_level_layout>

<action_handlers>
Action Handler类型(9种):
    set: 直接赋值
    increment/decrement: 数值增减
    toggle: 布尔切换
    template: 模板渲染(${state.xxx}语法)
    external: 外部API调用
    template:all/template:state: 模板变体
</action_handlers>

<list_operations>
列表操作(在action patches中):
    通过 mode: "operation" 触发,支持以下操作:

    - append_to_list: 追加元素到列表末尾
        * 格式: {"mode": "operation", "operation": "append_to_list", "params": {"items": [...]}}
        * 注意:必须使用 items(数组),不能使用 item(单数)
        * 示例: {"items": [{"name": "张三", "id": "001"}]}
        * 支持模板: {"items": [{"name": "${state.params.input_name}"}]}

    - prepend_to_list: 在列表开头插入元素
        * 格式: {"mode": "operation", "operation": "prepend_to_list", "params": {"items": [...]}}
        * 注意:必须使用 items(数组),不能使用 item(单数)
        * 示例: {"items": [{"name": "新用户"}]}

    - remove_from_list: 删除匹配的元素
        * 删除单个: {"mode": "operation", "operation": "remove_from_list", "params": {"key": "id", "value": "5"}}
        * 批量删除: {"mode": "operation", "operation": "remove_from_list", "params": {"key": "status", "value": "completed", "index": -1}}
        * 说明: index=-1 表示删除所有满足条件的项

    - remove_last: 删除列表最后一项
        * 格式: {"mode": "operation", "operation": "remove_last", "params": {}}

    - update_list_item: 更新指定位置的元素
        * 格式: {"mode": "operation", "operation": "update_list_item", "params": {"key": "id", "value": "5", "updates": {...}}}

    - clear_all_params: 清空所有参数
        * 格式: {"mode": "operation", "operation": "clear_all_params", "params": {}}

    - append_block: 追加block到blocks数组
    - prepend_block: 在blocks开头插入block
    - remove_block: 删除指定block
    - update_block: 更新指定block

    通用格式:
    {"mode": "operation", "operation": "操作名称", "params": {...}}
</list_operations>

<template_expressions>
模板表达式(在action patches值中使用):
    支持 ${state.xxx} 语法引用状态值,在运行时动态替换

    支持的场景:
    1. 直接赋值字符串: "姓名: ${state.params.name}"
    2. 列表操作的items参数: {"name": "${state.params.input_name}"}
    3. 列表更新的updates参数: {"email": "${state.params.new_email}"}
    4. 字典嵌套模板: {"text": "你好 ${state.params.name}, 邮箱: ${state.params.email}"}

    注意: 模板仅在 action patches 的 value 中生效,MCP 调用 patches 的 value 不支持
</template_expressions>

<block_operations>
Block操作(在action patches中):
    通过 mode: "operation" + operation: "append_block" 触发
    格式:
    {"mode": "operation", "operation": "append_block", "params": {"block": {...}}}
</block_operations>

<return_value>
返回值:
    {status: "success"|"error", instance_id, patches_applied, skipped_patches, message/error}
</return_value>

<examples>
常用示例:

⚠️ 格式规范提醒:
    - append_to_list 和 prepend_to_list 必须使用 params.items(复数),不要使用 item(单数)
    - 所有操作参数名必须严格匹配,不能随意修改
    - 模板表达式仅在 action patches 的 value 中生效

<example>1. 修改状态:
{"instance_id":"counter","patches":[{"op":"set","path":"state.params.count","value":42}]}
</example>

<example>2. 添加字段:
{"instance_id":"form","patches":[
    {"op":"set","path":"state.params.name","value":""},
    {"op":"add","path":"blocks.0.props.fields","value":{"label":"姓名","key":"name","type":"text"}}
]}
</example>

<example>3. 添加表格:
{"instance_id":"form","patches":[
    {"op":"set","path":"state.params.students","value":[{"name":"张三","id":"001","class":"一班"}]},
    {"op":"add","path":"blocks.0.props.fields","value":{
        "label":"学生列表","key":"students","type":"table",
        "columns":[{"key":"name","title":"姓名"},{"key":"id","title":"学号"}],
        "showPagination":true,"pageSize":5
    }}
]}
</example>

<example>3.1 表格列显示HTML/图片(波形图):
{"instance_id":"waveforms","patches":[
    {"op":"set","path":"state.params.waveforms","value":[
        {"id":"1","name":"节点1波形","url":"http://example.com/wave_2025_01_01.html"},
        {"id":"2","name":"节点2波形","url":"http://example.com/wave_2025_01_02.html"}
    ]},
    {"op":"add","path":"blocks.0.props.fields","value":{
        "label":"波形图列表","key":"waveforms","type":"table",
        "columns":[
            {"key":"name","title":"节点名称"},
            {"key":"url","title":"波形图","renderType":"image"}
        ],
        "showPagination":true,"pageSize":10
    }}
]}
</example>

<example>3.2 表格列使用mixed渲染(图片+标签+按钮):
{"instance_id":"products","patches":[
    {"op":"set","path":"state.params.products","value":[
        {"id":"1","name":"商品A","price":99.99,"stock":50,"image":"http://example.com/product_a.jpg"}
    ]},
    {"op":"add","path":"blocks.0.props.fields","value":{
        "label":"商品列表","key":"products","type":"table",
        "columns":[
            {"key":"name","title":"商品名称"},
            {"key":"price","title":"价格","renderType":"text"},
            {
                "key":"mixed_info",
                "title":"商品信息",
                "renderType":"mixed",
                "components":[
                    {"type":"image","field":"image","imageSize":"32px","imageFit":"cover"},
                    {"type":"tag","field":"stock","tagType":"value===50?'充足':'不足'"},
                    {"type":"button","buttonLabel":"购买","actionId":"buy"}
                ]
            }
        ],
        "showPagination":true,"pageSize":5
    }}
]}
</example>

<example>4. 添加block级action(添加学生):
{"instance_id":"form","patches":[
    {"op":"add","path":"blocks.0.props.actions","value":{
        "id":"add_student","label":"添加学生","style":"primary","handler_type":"set",
        "patches":{"state.params.students":{"mode":"operation","operation":"append_to_list","params":{"items":[{"name":"新生","id":"999"}]}}}
    }}
]}
</example>

<example>5. 添加全局action:
{"instance_id":"form","patches":[
    {"op":"add","path":"actions","value":{
        "id":"reset","label":"重置","style":"danger","handler_type":"set","patches":{"state.params.count":0}
    }}
]}
</example>

<example>6. 删除列表项(单个):
{"instance_id":"todo","patches":[
    {"op":"add","path":"actions","value":{
        "id":"remove","label":"删除","handler_type":"set",
        "patches":{"state.params.todos":{"mode":"operation","operation":"remove_from_list","params":{"key":"id","value":"5"}}}
    }}
]}
</example>

<example>7. 批量删除(删除所有completed=true的项):
{"instance_id":"todo","patches":[
    {"op":"add","path":"actions","value":{
        "id":"clear_done","label":"清除已完成","handler_type":"set",
        "patches":{"state.params.todos":{"mode":"operation","operation":"remove_from_list","params":{"key":"done","value":true,"index":-1}}}
    }}
]}
</example>

<example>8. 删除列表最后一项:
{"instance_id":"list_demo","patches":[
    {"op":"add","path":"actions","value":{
        "id":"remove_last","label":"删除最后一项","handler_type":"set",
        "patches":{"state.params.items":{"mode":"operation","operation":"remove_last","params":{}}}
    }}
]}
</example>

<example>9. 修改字段属性:
{"instance_id":"form","patches":[{"op":"set","path":"blocks.0.props.fields.0.label","value":"新标签"}]}
</example>

<example>10. 删除字段:
{"instance_id":"form","patches":[{"op":"remove","path":"blocks.0.props.fields","value":{"key":"old_field"}}]}
</example>

<example>11. 添加完整block:
{"instance_id":"form","patches":[
    {"op":"add","path":"blocks","value":{
        "id":"students","type":"form","bind":"state.params","props":{
            "fields":[{"label":"学生","key":"students","type":"table","columns":[{"key":"name","label":"姓名"}]}],
            "actions":[{"id":"add","label":"添加","handler_type":"set","patches":{"state.params.students":{"mode":"operation","operation":"append_to_list","params":{"items":[{"name":"新生"}]}}}}]
        }
    }}
]}
</example>

<example>11.1 使用Grid布局(2列):
{"instance_id":"demo","patches":[
    {"op":"add","path":"blocks","value":{
        "id":"user_form","type":"grid","bind":"state.params",
        "title":"用户信息",
        "props":{
            "cols":2,"gap":"20px",
            "fields":[
                {"label":"名","key":"first_name","type":"text"},
                {"label":"姓","key":"last_name","type":"text"},
                {"label":"年龄","key":"age","type":"number"},
                {"label":"性别","key":"gender","type":"select","options":[{"label":"男","value":"male"},{"label":"女","value":"female"}]}
            ]
        }
    }}
]}
</example>

<example>11.2 使用Tabs布局:
{"instance_id":"demo","patches":[
    {"op":"add","path":"blocks","value":{
        "id":"settings","type":"tabs","bind":"state.params",
        "title":"系统设置",
        "props":{
            "tabs":[
                {"label":"基本信息","fields":[
                    {"label":"用户名","key":"username","type":"text"},
                    {"label":"邮箱","key":"email","type":"text"}
                ]},
                {"label":"安全设置","fields":[
                    {"label":"密码","key":"password","type":"text"},
                    {"label":"确认密码","key":"confirm_password","type":"text"}
                ]}
            ]
        }
    }}
]}
</example>

<example>11.3 使用Accordion布局:
{"instance_id":"demo","patches":[
    {"op":"add","path":"blocks","value":{
        "id":"faq","type":"accordion","bind":"state.params",
        "title":"常见问题",
        "props":{
            "panels":[
                {"title":"如何注册？","fields":[
                    {"label":"答案","key":"answer1","type":"textarea","value":"点击右上角注册按钮"}
                ]},
                {"title":"如何找回密码？","fields":[
                    {"label":"答案","key":"answer2","type":"textarea","value":"使用忘记密码功能"}
                ]}
            ]
        }
    }}
]}
</example>

<example>11.4 修改顶层布局为Grid:
{"instance_id":"demo","patches":[
    {"op":"set","path":"layout.type","value":"grid"},
    {"op":"set","path":"layout.columns","value":2},
    {"op":"set","path":"layout.gap","value":"20px"}
]}
</example>

<example>11.5 修改顶层布局为Tabs(blocks分组到标签页):
{"instance_id":"demo","patches":[
    {"op":"set","path":"layout.type","value":"tabs"}
]}
</example>

<example>12. 创建实例:
{"instance_id":"__CREATE__","new_instance_id":"my_ui","patches":[
    {"op":"set","path":"meta","value":{"pageKey":"my_ui","step":{"current":1,"total":1},"status":"idle","schemaVersion":"1.0"}},
    {"op":"set","path":"state","value":{"params":{},"runtime":{}}},
    {"op":"set","path":"layout","value":{"type":"single"}},
    {"op":"set","path":"blocks","value":[]},
    {"op":"set","path":"actions","value":[]}
]}
</example>

<example>13. 删除实例:
{"instance_id":"__DELETE__","target_instance_id":"old_ui"}
</example>

<example>14. 添加全局action(动态生成block):
{"instance_id":"demo","patches":[
    {"op":"add","path":"actions","value":{
        "id":"generate_block","label":"生成 Block","style":"primary","handler_type":"set",
        "patches":{"blocks":{"mode":"operation","operation":"append_block","params":{"block":{
            "id":"dynamic_block","type":"form","bind":"state.params","props":{
                "fields":[{"label":"动态字段","key":"dynamic","type":"text"}]
            }
        }}}}
    }}
]}
</example>

<example>15. 使用模板表达式(将输入框值添加到表格):
{"instance_id":"form","patches":[
    {"op":"set","path":"state.params.name","value":""},
    {"op":"set","path":"state.params.email","value":""},
    {"op":"set","path":"state.params.students","value":[]},
    {"op":"add","path":"blocks.0.props.fields","value":{"label":"姓名","key":"name","type":"text"}},
    {"op":"add","path":"blocks.0.props.fields","value":{"label":"邮箱","key":"email","type":"text"}},
    {"op":"add","path":"blocks.0.props.fields","value":{"label":"学生列表","key":"students","type":"table","columns":[{"key":"name","label":"姓名"},{"key":"email","label":"邮箱"}]}},
    {"op":"add","path":"blocks.0.props.actions","value":{
        "id":"add_student","label":"添加学生","style":"primary","handler_type":"set",
        "patches":{"state.params.students":{"mode":"operation","operation":"append_to_list","params":{"items":[{"name":"${state.params.name}","email":"${state.params.email}"}]}}}
    }}
]}
</example>

<example>16. 使用模板表达式(更新字段):
{"instance_id":"form","patches":[
    {"op":"set","path":"state.params.username","value":"张三"},
    {"op":"set","path":"state.params.nickname","value":""},
    {"op":"add","path":"actions","value":{
        "id":"sync_nickname","label":"同步昵称","style":"secondary","handler_type":"set",
        "patches":{"state.params.nickname":"${state.params.username}"}
    }}
]}

17. 使用模板表达式(批量更新列表项):
{"instance_id":"form","patches":[
    {"op":"set","path":"state.params.todos","value":[{"id":"1","task":"任务1","done":false}]},
    {"op":"set","path":"state.params.new_task","value":""},
    {"op":"set","path":"state.params.update_msg","value":"已完成更新"},
    {"op":"add","path":"actions","value":{
        "id":"update_todo","label":"更新任务","style":"primary","handler_type":"set",
        "patches":{"state.params.todos":{"mode":"operation","operation":"update_list_item","params":{"key":"id","value":"1","updates":{"task":"${state.params.new_task}","status":"${state.params.update_msg}"}}}}
    }}
]}
</example>

<note>
注意:
- 修改后UI自动刷新,无需调用access_instance
- state.runtime.timestamp引用会自动更新为当前时间
- 使用前先调用get_schema了解当前结构
- 使用operation时必须包含 mode: "operation" 字段,否则会被当作普通值处理
- 模板表达式 ${state.xxx} 仅在 action patches 的 value 中生效,运行时才替换
- MCP 调用的 patches value 中使用模板字符串不会被处理(因为 action 还没执行)
</note>
</examples>
    """
    from backend.mcp.tool_implements import patch_ui_state_impl
    return await patch_ui_state_impl(
        instance_id, patches, new_instance_id, target_instance_id
    )


# ===== 只读查询工具 =====

@mcp.tool()
async def get_schema(instance_id: str | None = None) -> dict[str, Any]:
    """获取实例的完整UI Schema。

    参数:
        instance_id: 实例ID(如"demo"、"form")。None返回默认"demo"实例

    返回值:
        {status: "success"|"error", instance_id, schema}
        Schema结构:
        - meta: {pageKey, step: {current, total}, status, schemaVersion}
        - state: {params: {...}, runtime: {...}}
        - layout: {type} (顶层布局: single/multi)
        - blocks: [{id, type, bind, title, props: {fields, actions, cols, gap, tabs, panels}}, ...]
        - actions: [{id, label, style, handler_type, patches}, ...]

    示例:
        {"instance_id": "form"}
        {"instance_id": null}
    """
    from backend.mcp.tool_implements import get_schema_impl
    return await get_schema_impl(instance_id)


@mcp.tool()
async def list_instances() -> dict[str, Any]:
    """列出所有可用实例。

    返回值:
        {status: "success"|"error", instances: [{instance_id, page_key, status, blocks_count, actions_count}, ...], total}

    示例:
        {}(无需参数)
    """
    from backend.mcp.tool_implements import list_instances_impl
    return await list_instances_impl()


@mcp.tool()
async def switch_to_instance(instance_id: str) -> dict[str, Any]:
    """切换到指定实例,将其显示给用户。

    <parameter>
    参数:
        instance_id: 要切换到的实例ID(如"demo"、"form"、"counter")
    </parameter>

    <description>
    功能说明:
        - 切换前端显示的UI实例
        - 自动触发WebSocket推送通知前端
        - 不返回schema数据(如需获取schema请使用get_schema工具)
        - 主要用于在不同实例间切换
    </description>

    <return_value>
    返回值:
        {status: "success"|"error", instance_id, message}
    </return_value>

    <note>
    注意事项:
        - 如果需要查看实例的schema,请在切换后调用get_schema
        - 切换后前端会立即更新显示
        - 实例不存在时会返回错误并列出可用实例
    </note>

    <example>
    示例:
        {"instance_id": "form"}
    </example>
    """
    from backend.mcp.tool_implements import switch_to_instance_impl
    return await switch_to_instance_impl(instance_id)


# ===== 验证工具 =====

@mcp.tool()
async def validate_completion(
    instance_id: str,
    intent: str,
    completion_criteria: list[dict[str, Any]]
) -> dict[str, Any]:
    """验证UI实例是否满足完成标准。

    参数:
        instance_id: 要验证的实例ID
        intent: UI目标的高级描述
        completion_criteria: 验证标准数组

    标准类型:
        field_exists: 检查字段路径是否存在
        field_value: 检查字段是否具有特定值
        block_count: 检查block数量
        action_exists: 检查action是否存在(通过action的id)
        custom: 使用条件表达式进行自定义验证

    标准属性:
        type: 标准类型(必需)
        path: 字段路径(field_exists/field_value必需)
        value: 期望值(field_value必需)
        count: 期望数量(block_count必需)
        condition: 自定义表达式(custom必需)
        description: 描述(必需)

    返回值:
        {status: "success"|"error", evaluation: {passed_criteria, total_criteria, completion_ratio, detailed_results, summary, recommendations}}
        - completion_ratio >= 1.0 表示完全完成
        - detailed_results: [{criterion, passed, actual, expected}, ...]

    示例:

    检查计数器:
    {"instance_id":"counter","intent":"创建带显示和按钮的计数器",
     "completion_criteria":[
        {"type":"field_exists","path":"state.params.count","description":"计数器字段存在"},
        {"type":"action_exists","path":"increment","description":"增加按钮存在"}
     ]}

    检查表单:
    {"instance_id":"form","intent":"创建用户注册表单",
     "completion_criteria":[
        {"type":"field_exists","path":"state.params.email","description":"Email字段存在"},
        {"type":"field_value","path":"state.params.email","value":"","description":"Email为空"},
        {"type":"block_count","count":1,"description":"有1个表单block"},
        {"type":"action_exists","path":"submit","description":"提交按钮存在"}
     ]}
    """
    from backend.mcp.tool_implements import validate_completion_impl
    return await validate_completion_impl(instance_id, intent, completion_criteria)


if __name__ == "__main__":
    print("🚀 Starting MCP Server for UI Patch Tool...")
    mcp.run(
        transport="streamable-http",
        port=8766,
        host="0.0.0.0",
        path="/mcp",
    )
