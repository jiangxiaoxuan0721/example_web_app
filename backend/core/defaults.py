"""默认 Schema 实例 - 综合演示"""

from backend.fastapi.models.enums import FieldType
from ..fastapi.models import (
    UISchema, StateInfo, LayoutInfo, Block, ActionConfig,
    BlockProps, LayoutType, SchemaPatch, PatchOperationType,ActionType,
    BaseFieldConfig, SelectableFieldConfig, TableFieldConfig, ImageFieldConfig,
    OptionItem, ColumnConfig
)
from ..fastapi.models.patch_models import ExternalApiConfig


def get_default_instances() -> dict[str, UISchema]:
    """获取所有默认 Schema 实例"""
    return {
        "demo": _create_demo_schema(),  # 综合演示 - 所有功能整合
    }


def _create_demo_schema() -> UISchema:
    """创建综合演示 Schema - 包含计数器、动态列表、表格、选项组件、图片组件、布局切换、日期时间、文件上传等"""
    from datetime import datetime

    return UISchema(
        page_key="demo",
        state=StateInfo(
            params=dict(
                # 计数器
                counter=0,
                message="欢迎使用 UI Patch System",

                # 动态列表
                dynamic_users=[],
                next_id=1,

                # 任务表格（带行选择）
                tasks=[
                    {"id": 1, "name": "完成文档编写", "status": "active", "progress": {"current": 80, "total": 100}, "assignee": "张三", "priority": "high"},
                    {"id": 2, "name": "代码审查", "status": "pending", "progress": {"current": 30, "total": 100}, "assignee": "李四", "priority": "medium"},
                    {"id": 3, "name": "部署上线", "status": "completed", "progress": {"current": 100, "total": 100}, "assignee": "王五", "priority": "low"},
                ],
                tasks_selected=[],

                # 选项组件
                status="active",
                priority="medium",
                categories=["tech", "life"],

                # 日期时间组件
                start_date="2024-01-01",
                end_date="2024-12-31",
                meeting_time="2024-01-15T14:30",

                # 文件上传
                uploaded_file="",

                # 图片组件
                avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix",
                image_url="https://via.placeholder.com/300x200/4A90E2/ffffff?text=Sample+Image",

                # 布局字段
                grid_a="字段A", grid_b="字段B", grid_c="字段C", grid_d="字段D",
                tab1_field="标签页1内容", tab2_field="标签页2内容", tab3_field="标签页3内容",
                acc1_q="问题1", acc1_a="答案1", acc2_q="问题2", acc2_a="答案2",

                # API 调用字段
                api_request_data="",
                api_response="",
                api_status="",
            ),
            runtime={"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ),
        layout=LayoutInfo(type=LayoutType.SINGLE, columns=None, gap=None),
        blocks=[
            # Block 1: 计数器演示
            Block(
                id="counter_block",
                layout="form",
                title="计数器",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(label="计数器", key="counter", type=FieldType.NUMBER, editable=False),
                        BaseFieldConfig(label="消息", key="message", type=FieldType.TEXT),
                    ],
                    actions=[
                        ActionConfig(id="inc", label="+1", style="primary", patches=[SchemaPatch(op=PatchOperationType.INCREMENT, path="state.params.counter", value=1)]),
                        ActionConfig(id="dec", label="-1", style="secondary", patches=[SchemaPatch(op=PatchOperationType.DECREMENT, path="state.params.counter", value=1)]),
                    ]
                )
            ),
            
            # Block 2: 动态添加数据演示
            Block(
                id="dynamic_block",
                layout="form",
                title="动态列表",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        TableFieldConfig(
                            type=FieldType.TABLE, label="动态列表", key="dynamic_users",
                            columns=[ColumnConfig(key="id", title="ID"), ColumnConfig(key="name", title="名称"), ColumnConfig(key="added_at", title="时间")],
                            rowKey="id", bordered=True, pageSize=5
                        )
                    ],
                    actions=[
                        ActionConfig(id="add", label="添加", style="primary", patches=[
                            SchemaPatch(op=PatchOperationType.APPEND_TO_LIST, path="state.params.dynamic_users",
                                       value={"id": "${state.params.next_id}", "name": "新项目", "added_at": "${state.runtime.timestamp}"}),
                            SchemaPatch(op=PatchOperationType.INCREMENT, path="state.params.next_id", value=1)
                        ])
                    ]
                )
            ),
            
            # Block 3: 表格高级特性（带行选择）
            Block(
                id="table_block",
                layout="form",
                title="任务列表",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        TableFieldConfig(
                            type=FieldType.TABLE,
                            label="任务列表",
                            key="tasks",
                            tableEditable=True,
                            showPagination=True,
                            pageSize=10,
                            row_selection=True,
                            columns=[
                                ColumnConfig(key="id", title="ID", width="60px", sortable=True),
                                ColumnConfig(key="name", title="任务名称", editable=True),
                                ColumnConfig(key="status", title="状态", renderType="tag",
                                             tagType="value => value === 'active' ? 'success' : (value === 'completed' ? 'success' : 'warning')",
                                             editable=True, editType="select",
                                             options=[OptionItem(label="进行中", value="active"), OptionItem(label="待处理", value="pending"), OptionItem(label="已完成", value="completed")]),
                                ColumnConfig(key="progress", title="进度", renderType="progress"),
                                ColumnConfig(key="assignee", title="负责人", editable=True),
                                ColumnConfig(key="priority", title="优先级", renderType="tag",
                                             tagType="value => value === 'high' ? 'error' : (value === 'medium' ? 'warning' : 'default')",
                                             editable=True, editType="select",
                                             options=[OptionItem(label="高", value="high"), OptionItem(label="中", value="medium"), OptionItem(label="低", value="low")]),
                                ColumnConfig(key="actions", title="操作", renderType="mixed", components=[
                                    {"type": "button", "buttonLabel": "编辑", "buttonStyle": "primary", "actionId": "edit"},
                                    {"type": "spacer", "width": "8px"},
                                    {"type": "button", "buttonLabel": "删除", "buttonStyle": "danger", "actionId": "delete", "confirmMessage": "确认删除此任务？"}
                                ])
                            ],
                            rowKey="id",
                            bordered=True,
                            striped=True,
                            hover=True
                        )
                    ],
                    actions=[
                        ActionConfig(id="show_selected", label="查看选中", style="primary", patches=[
                            SchemaPatch(op=PatchOperationType.MERGE, path="state.runtime", value={"message": f"已选中 {len('${state.params.tasks_selected}')} 条记录"})
                        ])
                    ]
                )
            ),
            
            # Block 4: 选项组件
            Block(
                id="options_block",
                layout="form",
                title="选项组件",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        SelectableFieldConfig(
                            label="状态", key="status", type=FieldType.SELECT,
                            options=[OptionItem(label="活跃", value="active"), OptionItem(label="非活跃", value="inactive")]
                        ),
                        SelectableFieldConfig(
                            label="优先级", key="priority", type=FieldType.RADIO,
                            options=[OptionItem(label="高", value="high"), OptionItem(label="中", value="medium"), OptionItem(label="低", value="low")]
                        ),
                        SelectableFieldConfig(
                            label="分类", key="categories", type=FieldType.MULTISELECT,
                            options=[OptionItem(label="科技", value="tech"), OptionItem(label="生活", value="life"), OptionItem(label="娱乐", value="entertainment")]
                        ),
                    ]
                )
            ),
            
            # Block 5: 日期时间组件
            Block(
                id="datetime_block",
                layout="form",
                title="日期时间组件",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(label="开始日期", key="start_date", type=FieldType.DATE, placeholder="请选择日期"),
                        BaseFieldConfig(label="结束日期", key="end_date", type=FieldType.DATE, placeholder="请选择日期"),
                        BaseFieldConfig(label="会议时间", key="meeting_time", type=FieldType.DATETIME, placeholder="请选择日期时间"),
                    ]
                )
            ),

            # Block 6: API 调用组件
            Block(
                id="api_block",
                layout="form",
                title="API 调用",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(label="请求数据", key="api_request_data", type=FieldType.TEXT, placeholder="输入要发送的数据"),
                        BaseFieldConfig(label="API 响应", key="api_response", type=FieldType.TEXT, editable=False, placeholder="API 调用结果将显示在这里"),
                        BaseFieldConfig(label="状态", key="api_status", type=FieldType.TEXT, editable=False, placeholder="API 调用状态"),
                    ],
                    actions=[
                        ActionConfig(
                            id="call_api",
                            label="调用 API",
                            style="primary",
                            action_type=ActionType.API,
                            api=ExternalApiConfig(
                                url="https://httpbin.org/post",
                                method="POST",
                                body_template={"data": "${state.params.api_request_data}"},
                                body_template_type="json",
                                timeout=30,
                                response_mappings={
                                    "state.params.api_response": "json",
                                    "state.params.api_status": "status_code"
                                }
                            )
                        )
                    ]
                )
            ),

            # Block 7: 文件上传组件
            Block(
                id="file_block",
                layout="form",
                title="文件上传",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(label="上传文件", key="uploaded_file", type=FieldType.FILE, placeholder="拖拽或点击上传文件"),
                    ]
                )
            ),

            # Block 8: 图片组件
            Block(
                id="image_block",
                layout="grid",
                title="图片组件",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    cols=2,
                    gap="16px",
                    fields=[
                        ImageFieldConfig(
                            type=FieldType.IMAGE,
                            label="头像",
                            key="avatar_url",
                            imageHeight="100px",
                            imageFit="cover",
                            subtitle="圆形头像"
                        ),
                        ImageFieldConfig(
                            type=FieldType.IMAGE,
                            label="图片展示",
                            key="image_url",
                            imageHeight="200px",
                            imageFit="cover"
                        ),
                    ]
                )
            ),

            # Block 9: Grid 布局
            Block(
                id="grid_block",
                layout="grid",
                title="Grid布局",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    cols=2,
                    gap="16px",
                    fields=[
                        BaseFieldConfig(label="字段 A", key="grid_a", type=FieldType.TEXT),
                        BaseFieldConfig(label="字段 B", key="grid_b", type=FieldType.TEXT),
                        BaseFieldConfig(label="字段 C", key="grid_c", type=FieldType.TEXT),
                        BaseFieldConfig(label="字段 D", key="grid_d", type=FieldType.TEXT),
                    ]
                )
            ),

            # Block 10: Tabs 布局
            Block(
                id="tabs_block",
                layout="tabs",
                title="Tabs布局",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    tabs=[
                        {"label": "标签1", "fields": [{"key": "tab1_field", "label": "内容", "type": "text"}]},
                        {"label": "标签2", "fields": [{"key": "tab2_field", "label": "内容", "type": "text"}]},
                        {"label": "标签3", "fields": [{"key": "tab3_field", "label": "内容", "type": "text"}]},
                    ]
                )
            ),

            # Block 11: Accordion 布局
            Block(
                id="accordion_block",
                layout="accordion",
                title="Accordion布局",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    panels=[
                        {"title": "面板1", "fields": [{"key": "acc1_q", "label": "问题", "type": "text"}, {"key": "acc1_a", "label": "答案", "type": "textarea"}]},
                        {"title": "面板2", "fields": [{"key": "acc2_q", "label": "问题", "type": "text"}, {"key": "acc2_a", "label": "答案", "type": "textarea"}]},
                    ]
                )
            ),

            # Block 12: 导航功能演示
            Block(
                id="navigation_block",
                layout="form",
                title="块导航演示",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    actions=[
                        ActionConfig(id="nav_to_counter", label="跳转到计数器", style="primary", action_type=ActionType.NAVIGATE_BLOCK, target_block="counter_block"),
                        ActionConfig(id="nav_to_table", label="跳转到任务列表", style="secondary", action_type=ActionType.NAVIGATE_BLOCK, target_block="table_block"),
                        ActionConfig(id="nav_to_options", label="跳转到选项组件", style="secondary", action_type=ActionType.NAVIGATE_BLOCK, target_block="options_block"),
                    ]
                )
            ),
        ],
        actions=[            
            # 顶层布局切换
            ActionConfig(id="to_tabs", label="Tabs布局", style="primary", patches=[
                SchemaPatch(op=PatchOperationType.SET, path="layout", value={"type": "tabs", "columns": None, "gap": None})
            ]),
            ActionConfig(id="to_grid", label="Grid布局", style="secondary", patches=[
                SchemaPatch(op=PatchOperationType.SET, path="layout", value={"type": "grid", "columns": 2, "gap": "20px"})
            ]),
            ActionConfig(id="to_flex", label="Flex布局", style="secondary", patches=[
                SchemaPatch(op=PatchOperationType.SET, path="layout", value={"type": "flex", "gap": "16px"})
            ]),
        ]
    )
