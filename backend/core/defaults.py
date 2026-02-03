"""默认 Schema 实例"""

from backend.fastapi.models.enums import FieldType
from ..fastapi.models import (
    UISchema, StateInfo, LayoutInfo, Block, ActionConfig,ColumnConfig,
    BlockProps, LayoutType, ActionType,SchemaPatch,PatchOperationType,
    BaseFieldConfig, SelectableFieldConfig, TableFieldConfig, ImageFieldConfig
)


def get_default_instances() -> dict[str, UISchema]:
    """获取所有默认 Schema 实例"""
    return {
        "demo": _create_demo_schema(),
        "block_actions_test": _create_block_actions_test_schema(),
        "block_layouts_demo": _create_layouts_demo_schema(),
        "table_buttons_demo": _create_table_buttons_demo_schema(),
    }


def _create_demo_schema() -> UISchema:
    """创建 demo Schema - 展示系统核心功能"""
    from datetime import datetime

    return UISchema(
        page_key="demo",
        state=StateInfo(
            params=dict(
                # 用户数据表格
                users=[
                    {"id": 1, "name": "张三", "email": "zhangsan@example.com", "status": "active", "avatar": "https://picsum.photos/seed/zhangsan/100/100.jpg"},
                    {"id": 2, "name": "李四", "email": "lisi@example.com", "status": "inactive", "avatar": "https://picsum.photos/seed/lisi/100/100.jpg"},
                    {"id": 3, "name": "王五", "email": "wangwu@example.com", "status": "active", "avatar": "https://picsum.photos/seed/wangwu/100/100.jpg"},
                    {"id": 4, "name": "赵六", "email": "zhaoliu@example.com", "status": "pending", "avatar": "https://picsum.photos/seed/zhaoliu/100/100.jpg"},
                    {"id": 5, "name": "钱七", "email": "qianqi@example.com", "status": "active", "avatar": "https://picsum.photos/seed/qianqi/100/100.jpg"},
                ],
                # 动态交互
                counter=0,
                message="欢迎使用 UI Patch System！点击按钮体验动态更新功能",
                new_name="",
                new_email="",
                next_id=2,  # 下一个用户的 ID
                dynamic_users=[
                    {"id": 1, "name": "示例用户", "email": "demo@example.com", "added_at": "2026-01-27 10:00:00"}
                ],
                # 示例图片 URL
                demo_image="https://picsum.photos/seed/demo/800/300.jpg"
            ),
            runtime={
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0.0"
            }
        ),
        layout=LayoutInfo(type=LayoutType.SINGLE, columns=None, gap=None),
        blocks=[
            # Block 1:系统消息和计数器
            Block(
                id="overview_block",
                layout="form",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(
                            label="系统消息",
                            key="message",
                            type=FieldType.TEXT,
                            description="系统状态消息"
                        ),
                        BaseFieldConfig(
                            label="计数器",
                            key="counter",
                            type=FieldType.NUMBER,
                            description="实时计数器，展示动态更新功能",
                            editable=False
                        ),
                    ],
                    actions=[
                        ActionConfig(
                            id="increment_counter",
                            label="+1",
                            style="primary",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(op=PatchOperationType.INCREMENT, path="state.params.counter", value=1)
                            ]
                        ),
                        ActionConfig(
                            id="decrement_counter",
                            label="-1",
                            style="secondary",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(op=PatchOperationType.DECREMENT, path="state.params.counter", value=1)
                            ]
                        ),
                        ActionConfig(
                            id="update_message",
                            label="更新消息",
                            style="secondary",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(op=PatchOperationType.SET, path="state.params.message", value="消息已更新！时间戳: ${state.runtime.timestamp}")
                            ]
                        ),
                    ]
                )
            ),

            # Block 2: 模板表达式演示 - 动态添加数据到表格
            Block(
                id="template_demo_block",
                layout="form",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(
                            label="姓名",
                            key="new_name",
                            type=FieldType.TEXT,
                            description="输入姓名后点击下方按钮添加到表格"
                        ),
                        BaseFieldConfig(
                            label="邮箱",
                            key="new_email",
                            type=FieldType.TEXT,
                            description="输入邮箱后点击下方按钮添加到表格"
                        ),
                        BaseFieldConfig(
                            label="下一个 ID",
                            key="next_id",
                            type=FieldType.NUMBER,
                            description="下一个用户的 ID（自动递增）",
                            editable=False
                        ),
                        TableFieldConfig(
                            type=FieldType.TABLE,
                            label="动态数据表格",
                            key="dynamic_users",
                            description="使用模板表达式 ${state.xxx} 动态添加的数据",
                            columns=[  # pyright: ignore[reportArgumentType]
                                {"key": "id", "title": "ID", "align": "center"},
                                {"key": "name", "title": "姓名"},
                                {"key": "email", "title": "邮箱"},
                                {"key": "added_at", "title": "添加时间"},
                            ],
                            rowKey="id",
                            bordered=True,
                            striped=True,
                            hover=True,
                            showPagination=True,
                            pageSize=5
                        )
                    ],
                    actions=[
                        ActionConfig(
                            id="add_dynamic_user",
                            label="添加到表格",
                            style="primary",
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.APPEND_TO_LIST,
                                    path="state.params.dynamic_users",
                                    value={
                                        "id": "${state.params.next_id}",
                                        "name": "${state.params.new_name}",
                                        "email": "${state.params.new_email}",
                                        "added_at": "${state.runtime.timestamp}"
                                    }
                                ),
                                # 自动递增 next_id
                                SchemaPatch(op=PatchOperationType.INCREMENT, path="state.params.next_id", value=1)
                            ]
                        ),
                        ActionConfig(
                            id="clear_dynamic_users",
                            label="清空表格",
                            style="danger",
                            patches=[
                                SchemaPatch(op=PatchOperationType.SET, path="state.params.dynamic_users", value=[]),
                                SchemaPatch(op=PatchOperationType.SET, path="state.params.next_id", value=2),
                                SchemaPatch(op=PatchOperationType.SET, path="state.params.new_name", value=""),
                                SchemaPatch(op=PatchOperationType.SET, path="state.params.new_email", value=""),
                            ]
                        ),
                    ]
                )
            ),

            # Block 3: 模态框演示
            Block(
                id="modal_demo_block",
                layout="form",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(
                            label="模态框",
                            key="confirm_modal",
                            type=FieldType.MODAL,
                            description="点击下方按钮触发模态框",
                            value={
                                "visible": False,
                                "title": "确认操作",
                                "content": "<p>确定要执行此操作吗？</p>",
                                "okText": "确认",
                                "cancelText": "取消"
                            }
                        ),
                    ],
                    actions=[
                        ActionConfig(
                            id="show_modal",
                            label="显示确认对话框",
                            style="primary",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.SET,
                                    path="state.params.confirm_modal",
                                    value={
                                        "visible": True,
                                        "title": "确认操作",
                                        "content": "<p>确定要执行此操作吗？此操作将显示成功消息。</p>",
                                        "okText": "确认执行",
                                        "cancelText": "取消"
                                    }
                                )
                            ]
                        ),
                        ActionConfig(
                            id="execute_operation",
                            label="执行操作",
                            style="success",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.SET,
                                    path="state.params.message",
                                    value="操作已成功执行！"
                                ),
                                SchemaPatch(
                                    op=PatchOperationType.SET,
                                    path="state.params.confirm_modal.visible",
                                    value=False
                                )
                            ]
                        ),
                        ActionConfig(
                            id="hide_modal",
                            label="隐藏模态框",
                            style="secondary",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.SET,
                                    path="state.params.confirm_modal.visible",
                                    value=False
                                )
                            ]
                        )
                    ]
                )
            ),

            # Block 4: 图片展示
            Block(
                id="image_block",
                layout="form",
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    fields=[
                        ImageFieldConfig(
                            type=FieldType.IMAGE,
                            label="示例图片",
                            key="demo_image",
                            description="示例图片展示，支持全屏查看",
                            value="https://picsum.photos/seed/demo/800/300.jpg",
                            showFullscreen=True,
                            showDownload=True,
                            imageHeight="300px",
                            imageFit="cover"
                        )
                    ],
                    actions=[
                        ActionConfig(
                            id="refresh_image",
                            label="刷新图片",
                            style="primary",
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.SET,
                                    path="state.params.demo_image",
                                    value=f"https://picsum.photos/seed/{datetime.now().strftime('%Y%m%d%H%M%S')}/800/300.jpg"
                                )
                            ]
                        )
                    ]
                )
            ),
        ],
        actions=[
            # 实例导航 actions
            ActionConfig(
                id="to_counter",
                label="计数器演示",
                style="primary",
                action_type=ActionType.NAVIGATE,
                target_instance="counter"
            ),
            ActionConfig(
                id="to_rich_content",
                label="富内容展示",
                style="secondary",
                action_type=ActionType.NAVIGATE,
                target_instance="rich_content"
            ),
            ActionConfig(
                id="to_block_actions",
                label="Block Actions",
                style="secondary",
                action_type=ActionType.NAVIGATE,
                target_instance="block_actions_test"
            ),

            # 全局操作 actions
            ActionConfig(
                id="generate_block",
                label="生成 Block",
                style="primary",
                patches=[
                    SchemaPatch(
                        op=PatchOperationType.ADD,
                        path="blocks",
                        value={
                            "id": "generated_block",
                            "layout": "form",
                            "props": {
                                "fields": [
                                    {
                                        "label": "动态生成的 Block",
                                        "key": "dynamic_field",
                                        "type": "text",
                                        "description": "这是一个通过按钮动态添加的 Block"
                                    }
                                ]
                            }
                        }
                    )
                ]
            ),
            ActionConfig(
                id="reset_all",
                label="重置所有",
                style="danger",
                action_type=ActionType.PATCH,
                patches=[
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.users",
                        value=[
                            {"id": 1, "name": "张三", "email": "zhangsan@example.com", "status": "active", "avatar": "https://picsum.photos/seed/zhangsan/100/100.jpg"},
                            {"id": 2, "name": "李四", "email": "lisi@example.com", "status": "inactive", "avatar": "https://picsum.photos/seed/lisi/100/100.jpg"},
                            {"id": 3, "name": "王五", "email": "wangwu@example.com", "status": "active", "avatar": "https://picsum.photos/seed/wangwu/100/100.jpg"},
                        ]),
                    SchemaPatch(op=PatchOperationType.SET,path="state.params.counter",value=0),
                    SchemaPatch(op=PatchOperationType.SET,path="state.params.message",value="欢迎使用 UI Patch System！点击按钮体验动态更新功能"),
                    SchemaPatch(op=PatchOperationType.SET,path="state.params.new_name",value=""),
                    SchemaPatch(op=PatchOperationType.SET,path="state.params.new_email",value=""),
                    SchemaPatch(op=PatchOperationType.SET,path="state.params.next_id",value=2),
                    SchemaPatch(op=PatchOperationType.SET,path="state.params.dynamic_users",value=[{"id": 1, "name": "示例用户", "email": "demo@example.com", "added_at": "2026-01-27 10:00:00"}]
                    )
                ]
            )
        ]
    )

def _create_block_actions_test_schema() -> UISchema:
    """创建 Block Actions 测试 Schema - 用于测试 block 级别的 actions"""
    from datetime import datetime
    return UISchema(
        page_key="block_actions_test",
        state=StateInfo(
            params=dict(
                todo_list=[
                    {"id": 1, "task": "学习 Python", "completed": False},
                    {"id": 2, "task": "学习 FastAPI", "completed": True},
                    {"id": 3, "task": "学习 React", "completed": False},
                    {"id": 4, "task": "学习 TypeScript", "completed": True},
                ],
                message="欢迎使用 Block Actions 测试页面！"
            ),
            runtime={"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ),
        layout=LayoutInfo(type=LayoutType.SINGLE, columns=None, gap=None),
        blocks=[
            # Block 1: 带有 block 级别 actions 的待办事项列表
            Block(
                id="todo_block",
                layout="form",
                props=BlockProps(  # type: ignore
                    fields=[
                        TableFieldConfig(  # type: ignore  # pyright: ignore[reportCallIssue]
                            type=FieldType.TABLE,
                            label="待办事项列表",
                            key="todo_list",
                            value=None,
                            description="这是一个带 block 级别 actions 的待办事项列表",
                            columns=[  # pyright: ignore[reportArgumentType]
                                {"key": "id", "title": "ID", "align": "center"},
                                {"key": "task", "title": "任务", "sortable": True},
                                {"key": "completed", "title": "状态", "renderType": "tag", "tagType": "value => value ? 'success' : 'default'"}
                            ],
                            rowKey="id",
                            bordered=True,
                            striped=True,
                            hover=True,
                            showPagination=True,
                            pageSize=10
                        )
                    ],
                    # Block 级别的 actions
                    actions=[
                        ActionConfig(
                            id="add_todo",
                            label="添加任务",
                            style="primary",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.APPEND_TO_LIST,
                                    path="state.params.todo_list",
                                    value={"id": 5, "task": "新任务", "completed": False}
                                )
                            ]
                        ),
                        ActionConfig(
                            id="clear_completed",
                            label="清除已完成",
                            style="danger",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.FILTER_LIST,
                                    path="state.params.todo_list",
                                    value={"key": "completed", "operator": "!=", "value": True}
                                )
                            ]
                        )
                    ]
                ) # type: ignore
            ),
            # Block 2: 消息显示和操作
            Block(
                id="message_block",
                layout="form",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="消息",
                            key="message",
                            type=FieldType.TEXT
                        )
                    ],
                    # Block 级别的 actions
                    actions=[
                        ActionConfig(
                            id="update_message",
                            label="更新消息",
                            style="primary",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.SET,
                                    path="state.params.message",
                                    value="消息已更新！时间戳: ${state.runtime.timestamp}"
                                )
                            ]
                        ),
                        ActionConfig(
                            id="clear_message",
                            label="清空消息",
                            style="secondary",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.SET,
                                    path="state.params.message",
                                    value=""
                                )
                            ]
                        )
                    ]
                ) # type: ignore
            ),
            # Block 3: 显示当前时间（只读展示，无 actions）
            Block(
                id="info_block",
                layout="display",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[]
                ) # type: ignore
            )
        ],
        # 全局级别的 actions
        actions=[
            ActionConfig(
                id="reset_all",
                label="重置所有",
                style="danger",
                action_type=ActionType.PATCH,
                patches=[
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.todo_list",
                        value=[
                            {"id": 1, "task": "学习 Python", "completed": False},
                            {"id": 2, "task": "学习 FastAPI", "completed": True},
                            {"id": 3, "task": "学习 React", "completed": False}
                        ]
                    ),
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.message",
                        value="欢迎使用 Block Actions 测试页面！"
                    )
                ]
            ),
            ActionConfig(
                id="to_demo",
                label="返回主页",
                style="secondary",
                action_type=ActionType.NAVIGATE,
                target_instance="demo"
            )
        ]
    )



def _create_layouts_demo_schema() -> UISchema:
    """创建布局演示 Schema - 展示所有布局类型"""
    return UISchema(
        page_key="layouts_demo",
        state=StateInfo(
            params=dict(
                # Card 布局数据
                card_name="张三",
                card_email="zhangsan@example.com",
                card_phone="13800138000",

                # Grid 布局数据
                col_first_name="张",
                col_last_name="三",
                col_gender="male",

                # Tabs 布局数据
                tab_username="demo_user",
                tab_email="demo@example.com",
                tab_password="password123",
                tab_two_factor=False,
                tab_language="zh",
                tab_theme="light",

                # Accordion 布局数据
                acc_question1="如何注册账号？",
                acc_answer1="点击右上角的注册按钮，填写必要信息即可完成注册。",
                acc_question2="支持哪些支付方式？",
                acc_answer2="我们支持支付宝、微信支付、银行卡等多种支付方式。",
                acc_question3="如何联系客服？",
                acc_answer3="可以通过网站在线客服、电话或邮件联系我们。",
            ),
            runtime={}
        ),
        layout=LayoutInfo(type=LayoutType.SINGLE, columns=None, gap=None),
        blocks=[
            # Block 1: Grid 布局
            Block(
                id="grid_layout",
                layout="grid",
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    cols=2,
                    gap="20px",
                    fields=[
                        BaseFieldConfig(
                            label="姓名",
                            key="card_name",
                            type=FieldType.TEXT,
                            description="用户姓名"
                        ),
                        BaseFieldConfig(
                            label="邮箱",
                            key="card_email",
                            type=FieldType.TEXT,
                            description="电子邮箱"
                        ),
                        BaseFieldConfig(
                            label="电话",
                            key="card_phone",
                            type=FieldType.TEXT,
                            description="联系电话"
                        ),
                        BaseFieldConfig(
                            label="年龄",
                            key="col_age",
                            type=FieldType.NUMBER,
                            description="年龄"
                        ),
                    ]
                )
            ),

            # Block 2: Grid 布局（多列）
            Block(
                id="grid_layout_multi",
                layout="grid",
                props=BlockProps(
                    cols=2,
                    gap="20px",
                    fields=[
                        BaseFieldConfig(
                            label="名",
                            key="col_first_name",
                            type=FieldType.TEXT,
                            description="名字"
                        ),
                        BaseFieldConfig(
                            label="姓",
                            key="col_last_name",
                            type=FieldType.TEXT,
                            description="姓氏"
                        ),
                        SelectableFieldConfig( # pyright: ignore[reportCallIssue]
                            label="性别",
                            key="col_gender",
                            type=FieldType.SELECT,
                            options=[  # pyright: ignore[reportArgumentType]
                                {"label": "男", "value": "male"},
                                {"label": "女", "value": "female"}
                            ]
                        ),
                    ]
                )
            ),

            # Block 3: Tabs 布局
            Block(
                id="tabs_layout",
                layout="tabs",
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    tabs=[
                        {
                            "label": "基本信息",
                            "fields": [
                                {"label": "用户名", "key": "tab_username", "type": "text"},
                                {"label": "邮箱", "key": "tab_email", "type": "text"}
                            ]
                        },
                        {
                            "label": "安全设置",
                            "fields": [
                                {"label": "密码", "key": "tab_password", "type": "text"},
                                {"label": "启用两步验证", "key": "tab_two_factor", "type": "checkbox"}
                            ]
                        },
                        {
                            "label": "偏好设置",
                            "fields": [
                                {
                                    "label": "语言",
                                    "key": "tab_language",
                                    "type": "select",
                                    "options": [
                                        {"label": "中文", "value": "zh"},
                                        {"label": "English", "value": "en"}
                                    ]
                                },
                                {
                                    "label": "主题",
                                    "key": "tab_theme",
                                    "type": "select",
                                    "options": [
                                        {"label": "浅色", "value": "light"},
                                        {"label": "深色", "value": "dark"}
                                    ]
                                }
                            ]
                        }
                    ]
                )
            ),

            # Block 4: Accordion 布局
            Block(
                id="accordion_layout",
                layout="accordion",
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    panels=[
                        {
                            "title": "账号问题",
                            "fields": [
                                {"label": "问题", "key": "acc_question1", "type": "text"},
                                {"label": "答案", "key": "acc_answer1", "type": "textarea"}
                            ]
                        },
                        {
                            "title": "支付问题",
                            "fields": [
                                {"label": "问题", "key": "acc_question2", "type": "text"},
                                {"label": "答案", "key": "acc_answer2", "type": "textarea"}
                            ]
                        },
                        {
                            "title": "技术支持",
                            "fields": [
                                {"label": "问题", "key": "acc_question3", "type": "text"},
                                {"label": "答案", "key": "acc_answer3", "type": "textarea"}
                            ]
                        }
                    ]
                )
            ),
        ]
    )

def _create_table_buttons_demo_schema() -> UISchema:
    """创建表格按钮事件演示 Schema - 展示表格内按钮点击事件处理"""
    from datetime import datetime

    return UISchema(
        page_key="table_buttons_demo",
        state=StateInfo(
            params=dict(
                # 员工数据表格
                employees=[
                    {"id": 1, "name": "张三", "department": "研发部", "role": "工程师", "status": "active"},
                    {"id": 2, "name": "李四", "department": "产品部", "role": "产品经理", "status": "active"},
                    {"id": 3, "name": "王五", "department": "设计部", "role": "UI设计师", "status": "inactive"},
                    {"id": 4, "name": "赵六", "department": "研发部", "role": "测试工程师", "status": "pending"},
                    {"id": 5, "name": "钱七", "department": "运营部", "role": "运营专员", "status": "active"},
                ],
                # 选中的员工（用于编辑）
                selected_employee=None,
                # 操作消息
                action_message="表格按钮事件演示 - 点击表格中的按钮查看效果",
                # 添加新员工的表单数据
                new_name="",
                new_department="",
                new_role="",
                next_id=6,
            ),
            runtime={
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0.0"
            }
        ),
        layout=LayoutInfo(type=LayoutType.SINGLE, columns=None, gap=None),
        blocks=[
            # Block 1: 操作消息
            Block(
                id="message_block",
                layout="form",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="操作消息",
                            key="action_message",
                            type=FieldType.TEXT,
                            description="显示最近的操作结果",
                            editable=False
                        ),
                    ]
                )
            ),

            # Block 2: 员工列表表格（带操作按钮）
            Block(
                id="employees_block",
                layout="form",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        TableFieldConfig(
                            type=FieldType.TABLE,
                            label="员工列表",
                            key="employees",
                            description="点击操作列中的按钮测试表格按钮事件",
                            columns=[  # pyright: ignore[reportArgumentType]
                                {"key": "id", "title": "ID", "align": "center", "width": "60px"},
                                {"key": "name", "title": "姓名"},
                                {"key": "department", "title": "部门"},
                                {"key": "role", "title": "职位"},
                                {
                                    "key": "status",
                                    "title": "状态",
                                    "renderType": "tag",
                                    "tagType": "value => value === 'active' ? 'success' : (value === 'pending' ? 'warning' : 'default')",
                                    "align": "center"
                                },
                                {
                                    "key": "actions",
                                    "title": "操作",
                                    "renderType": "mixed",
                                    "align": "center",
                                    "components": [
                                        {
                                            "type": "button",
                                            "buttonLabel": "查看",
                                            "buttonStyle": "secondary",
                                            "buttonSize": "small",
                                            "actionId": "view_employee"
                                        },
                                        {"type": "spacer", "width": "8px"},
                                        {
                                            "type": "button",
                                            "buttonLabel": "编辑",
                                            "buttonStyle": "primary",
                                            "buttonSize": "small",
                                            "actionId": "edit_employee"
                                        },
                                        {"type": "spacer", "width": "8px"},
                                        {
                                            "type": "button",
                                            "buttonLabel": "删除",
                                            "buttonStyle": "danger",
                                            "buttonSize": "small",
                                            "actionId": "delete_employee",
                                            "confirmMessage": "确定要删除此员工吗？"
                                        }
                                    ]
                                }
                            ],
                            rowKey="id",
                            bordered=True,
                            striped=True,
                            hover=True,
                            showPagination=True,
                            pageSize=10,
                            emptyText="暂无员工数据"
                        )
                    ],
                    actions=[
                        ActionConfig(
                            id="add_employee",
                            label="添加员工",
                            style="primary",
                            action_type=ActionType.PATCH,
                            patches=[
                                SchemaPatch(
                                    op=PatchOperationType.SET,
                                    path="state.params.action_message",
                                    value="已添加新员工！时间戳: ${state.runtime.timestamp}"
                                )
                            ]
                        ),
                    ]
                )
            ),

            # Block 3: 选中的员工信息（只读）
            Block(
                id="selected_block",
                layout="form",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(
                            label="选中员工信息",
                            key="selected_employee",
                            type=FieldType.TEXT,
                            description="点击表格中的查看或编辑按钮后，此处会显示员工信息",
                            editable=False
                        ),
                    ]
                )
            ),
        ],
        # 全局级别的 Actions - 这些 Action 会被表格按钮触发
        actions=[
            # 查看员工 - 设置选中员工信息
            ActionConfig(
                id="view_employee",
                label="查看员工",
                style="secondary",
                action_type=ActionType.PATCH,
                patches=[
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.selected_employee",
                        value="${state.params.temp_rowData}"
                    ),
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.action_message",
                        value="已查看员工：${state.params.temp_rowData.name} (${state.params.temp_rowData.department} - ${state.params.temp_rowData.role})"
                    )
                ]
            ),

            # 编辑员工 - 设置选中员工信息
            ActionConfig(
                id="edit_employee",
                label="编辑员工",
                style="primary",
                action_type=ActionType.PATCH,
                patches=[
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.selected_employee",
                        value="${state.params.temp_rowData}"
                    ),
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.action_message",
                        value="正在编辑员工：${state.params.temp_rowData.name} (ID: ${state.params.temp_rowData.id})"
                    )
                ]
            ),

            # 删除员工 - 从列表中移除
            ActionConfig(
                id="delete_employee",
                label="删除员工",
                style="danger",
                action_type=ActionType.PATCH,
                patches=[
                    SchemaPatch(
                        op=PatchOperationType.REMOVE_FROM_LIST,
                        path="state.params.employees",
                        value={
                            "key": "id",
                            "value": "${state.params.temp_rowData.id}"
                        }
                    ),
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.action_message",
                        value="已删除员工：${state.params.temp_rowData.name}"
                    )
                ]
            ),

            # 导航 Action
            ActionConfig(
                id="to_demo",
                label="返回主页",
                style="secondary",
                action_type=ActionType.NAVIGATE,
                target_instance="demo"
            ),
            # 重置 Action
            ActionConfig(
                id="reset_all",
                label="重置数据",
                style="danger",
                action_type=ActionType.PATCH,
                patches=[
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.employees",
                        value=[
                            {"id": 1, "name": "张三", "department": "研发部", "role": "工程师", "status": "active"},
                            {"id": 2, "name": "李四", "department": "产品部", "role": "产品经理", "status": "active"},
                            {"id": 3, "name": "王五", "department": "设计部", "role": "UI设计师", "status": "inactive"},
                            {"id": 4, "name": "赵六", "department": "研发部", "role": "测试工程师", "status": "pending"},
                            {"id": 5, "name": "钱七", "department": "运营部", "role": "运营专员", "status": "active"},
                        ]
                    ),
                    SchemaPatch(op=PatchOperationType.SET, path="state.params.selected_employee", value=None),
                    SchemaPatch(
                        op=PatchOperationType.SET,
                        path="state.params.action_message",
                        value="数据已重置！"
                    ),
                    SchemaPatch(op=PatchOperationType.SET, path="state.params.next_id", value=6),
                ]
            )
        ]
    )
