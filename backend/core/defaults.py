"""默认 Schema 实例"""

from ..fastapi.models import (
    UISchema, MetaInfo, StateInfo, LayoutInfo, Block, ActionConfig,
    StepInfo, BlockProps,  StatusType, LayoutType, ActionType, HandlerType,
    BaseFieldConfig, SelectableFieldConfig, TableFieldConfig, ImageFieldConfig
)


def get_default_instances() -> dict[str, UISchema]:
    """获取所有默认 Schema 实例"""
    return {
        "demo": _create_demo_schema(),
        "rich_content": _create_rich_content_schema(),
        "block_actions_test": _create_block_actions_test_schema(),
        "block_layouts_demo": _create_layouts_demo_schema(),
        "top_layout_demo": _create_top_level_layouts_demo_schema(),
    }


def _create_demo_schema() -> UISchema:
    """创建 demo Schema - 展示系统核心功能"""
    from datetime import datetime

    return UISchema(
        meta=MetaInfo(
            pageKey="demo",
            step=StepInfo(current=1, total=1),
            status=StatusType.IDLE,
            schemaVersion="1.0",
            title="UI Patch System",
            description="基于 Patch 驱动的动态 UI 系统",
            created_at=datetime.now()
        ),
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
                # 模板表达式演示字段
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
            # Block 1: 系统消息和计数器
            Block(
                id="overview_block",
                type="form",
                bind="state.params",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="系统消息",
                            key="message",
                            type="text",
                            description="系统状态消息"
                        ),
                        BaseFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="计数器",
                            key="counter",
                            type="text",
                            description="实时计数器，展示动态更新功能"
                        ),
                    ],
                    actions=[
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="increment_counter",
                            label="+1",
                            style="primary",
                            handler_type="increment",
                            patches={"state.params.counter": 1}
                        ),
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="decrement_counter",
                            label="-1",
                            style="secondary",
                            handler_type="decrement",
                            patches={"state.params.counter": 1}
                        ),
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="update_message",
                            label="更新消息",
                            style="secondary",
                            handler_type="set",
                            patches={"state.params.message": "消息已更新！时间戳: ${state.runtime.timestamp}"}
                        ),
                    ]
                )
            ),

            # Block 2: 用户数据表格
            Block(
                id="users_table_block",
                type="form",
                bind="state.params",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        TableFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="用户列表",
                            key="users",
                            type="table",
                            description="用户数据表格，支持排序、分页、状态标签",
                            columns=[
                                {"key": "id", "title": "ID", "align": "center"},
                                {"key": "name", "title": "姓名", "sortable": True},
                                {"key": "email", "title": "邮箱"},
                                {"key": "status", "title": "状态", "renderType": "tag", "tagType": "value => value === 'active' ? 'success' : value === 'inactive' ? 'default' : 'warning'"},
                                {"key": "avatar", "title": "头像", "renderType": "image"},
                            ],
                            rowKey="id",
                            bordered=True,
                            striped=True,
                            hover=True,
                            showPagination=True,
                            pageSize=10
                        )
                    ],
                    actions=[
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="add_user",
                            label="添加用户",
                            style="primary",
                            handler_type="set",
                            patches={
                                "state.params.users": {
                                    "mode": "operation",
                                    "operation": "append_to_list",
                                    "params": {
                                        "items": [
                                            {
                                                "id": 6,
                                                "name": "新用户",
                                                "email": "newuser@example.com",
                                                "status": "active",
                                                "avatar": "https://picsum.photos/seed/newuser/100/100.jpg"
                                            }
                                        ]
                                    }
                                }
                            }
                        ),
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="reset_users",
                            label="重置列表",
                            style="secondary",
                            handler_type="set",
                            patches={
                                "state.params.users": [
                                    {"id": 1, "name": "张三", "email": "zhangsan@example.com", "status": "active", "avatar": "https://picsum.photos/seed/zhangsan/100/100.jpg"},
                                    {"id": 2, "name": "李四", "email": "lisi@example.com", "status": "inactive", "avatar": "https://picsum.photos/seed/lisi/100/100.jpg"},
                                    {"id": 3, "name": "王五", "email": "wangwu@example.com", "status": "active", "avatar": "https://picsum.photos/seed/wangwu/100/100.jpg"}
                                ]
                            }
                        ),
                    ]
                )
            ),

            # Block 3: 模板表达式演示 - 动态添加数据到表格
            Block(
                id="template_demo_block",
                type="form",
                bind="state.params",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="姓名",
                            key="new_name",
                            type="text",
                            description="输入姓名后点击下方按钮添加到表格"
                        ),
                        BaseFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="邮箱",
                            key="new_email",
                            type="text",
                            description="输入邮箱后点击下方按钮添加到表格"
                        ),
                        BaseFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="下一个 ID",
                            key="next_id",
                            type="text",
                            description="下一个用户的 ID（自动递增）"
                        ),
                        TableFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="动态数据表格",
                            key="dynamic_users",
                            type="table",
                            description="使用模板表达式 ${state.xxx} 动态添加的数据",
                            columns=[
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
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="add_dynamic_user",
                            label="添加到表格",
                            style="primary",
                            handler_type="set",
                            patches={
                                "state.params.dynamic_users": {
                                    "mode": "operation",
                                    "operation": "append_to_list",
                                    "params": {
                                        "items": [
                                            {
                                                "id": "${state.params.next_id}",
                                                "name": "${state.params.new_name}",
                                                "email": "${state.params.new_email}",
                                                "added_at": "${state.runtime.timestamp}"
                                            }
                                        ]
                                    }
                                }
                            }
                        ),
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="clear_dynamic_users",
                            label="清空表格",
                            style="danger",
                            handler_type="set",
                            patches={
                                "state.params.dynamic_users": [],
                                "state.params.next_id": 2,
                                "state.params.new_name": "",
                                "state.params.new_email": ""
                            }
                        ),
                    ]
                )
            ),

            # Block 4: 图片展示
            Block(
                id="image_block",
                type="form",
                bind="state.params",
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    fields=[
                        ImageFieldConfig( # pyright: ignore[reportCallIssue]
                            label="示例图片",
                            key="demo_image",
                            type="image",
                            description="示例图片展示，支持全屏查看",
                            value="https://picsum.photos/seed/demo/800/300.jpg",
                            showFullscreen=True,
                            showDownload=True,
                            imageHeight="300px",
                            imageFit="cover"
                        )
                    ],
                    actions=[
                        ActionConfig( # pyright: ignore[reportCallIssue]
                            id="refresh_image",
                            label="刷新图片",
                            style="primary",
                            handler_type="set",
                            patches={
                                "state.params.demo_image": f"https://picsum.photos/seed/{datetime.now().strftime('%Y%m%d%H%M%S')}/800/300.jpg"
                            }
                        )
                    ]
                )
            ),
        ],
        actions=[
            # 实例导航 actions
            ActionConfig( # pyright: ignore[reportCallIssue]
                id="to_counter",
                label="计数器演示",
                style="primary",
                action_type="navigate",
                target_instance="counter"
            ),
            ActionConfig( # pyright: ignore[reportCallIssue]
                id="to_rich_content",
                label="富内容展示",
                style="secondary",
                action_type="navigate",
                target_instance="rich_content"
            ),
            ActionConfig( # pyright: ignore[reportCallIssue]
                id="to_block_actions",
                label="Block Actions",
                style="secondary",
                action_type="navigate",
                target_instance="block_actions_test"
            ),

            # 全局操作 actions
            ActionConfig( # pyright: ignore[reportCallIssue]
                id="generate_block",
                label="生成 Block",
                style="primary",
                handler_type="set",
                patches={
                    "blocks": {
                        "mode": "operation",
                        "operation": "append_block",
                        "params": {
                            "block": {
                                "id": "generated_block",
                                "type": "form",
                                "bind": "state.params",
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
                        }
                    }
                }
            ),
            ActionConfig( # pyright: ignore[reportCallIssue]
                id="reset_all",
                label="重置所有",
                style="danger",
                handler_type="set",
                patches={
                    "state.params.users": [
                        {"id": 1, "name": "张三", "email": "zhangsan@example.com", "status": "active", "avatar": "https://picsum.photos/seed/zhangsan/100/100.jpg"},
                        {"id": 2, "name": "李四", "email": "lisi@example.com", "status": "inactive", "avatar": "https://picsum.photos/seed/lisi/100/100.jpg"},
                        {"id": 3, "name": "王五", "email": "wangwu@example.com", "status": "active", "avatar": "https://picsum.photos/seed/wangwu/100/100.jpg"},
                    ],
                    "state.params.counter": 0,
                    "state.params.message": "欢迎使用 UI Patch System！点击按钮体验动态更新功能",
                    "state.params.new_name": "",
                    "state.params.new_email": "",
                    "state.params.next_id": 2,
                    "state.params.dynamic_users": [{"id": 1, "name": "示例用户", "email": "demo@example.com", "added_at": "2026-01-27 10:00:00"}]
                }
            )
        ]
    )


def _create_rich_content_schema() -> UISchema:
    """创建富内容展示 Schema"""
    return UISchema(
        meta=MetaInfo(
            pageKey="rich_content",
            step=StepInfo(current=1, total=1),
            status=StatusType.IDLE,
            schemaVersion="1.0",
            title=None,
            description=None
        ),
        state=StateInfo(
            params=dict(
                html_content="""
                <h2>HTML 内容示例</h2>
                <p>这是一个<strong>HTML内容</strong>的示例，支持各种HTML标签：</p>
                <ul>
                    <li>支持<strong>粗体</strong>和<em>斜体</em>文本</li>
                    <li>支持<code>行内代码</code>和代码块</li>
                    <li>支持<a href="#" onclick="alert('链接被点击!')">链接</a></li>
                </ul>
                <blockquote>
                    这是一段引用文本，可以用于突出重要内容。
                </blockquote>
                <table border="1" style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px;">列1</th>
                        <th style="padding: 8px;">列2</th>
                        <th style="padding: 8px;">列3</th>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">数据1</td>
                        <td style="padding: 8px;">数据2</td>
                        <td style="padding: 8px;">数据3</td>
                    </tr>
                    <tr style="background-color: #f9f9f9;">
                        <td style="padding: 8px;">数据4</td>
                        <td style="padding: 8px;">数据5</td>
                        <td style="padding: 8px;">数据6</td>
                    </tr>
                </table>
                """,
                image_url="https://picsum.photos/seed/example123/600/300.jpg",
                image_info={
                    "url": "https://picsum.photos/seed/nature456/600/300.jpg",
                    "alt": "自然风景",
                    "title": "这是一张美丽的自然风景图片"
                },
                enhanced_image={
                    "url": "http://192.168.130.30:9100/psaagent/IEEE39/n_1/Waveform/2025/12/17/wave_2025_12_17_15_08_13_05a13b.html",
                    "alt": "增强版图片",
                    "title": "这是一张展示增强功能的图片"
                }
            ),
            runtime={}
        ),
        layout=LayoutInfo(type=LayoutType.FLEX, columns=None, gap=None),
        blocks=[
            Block(
                id="rich_content_block",
                type="form",
                bind="state.params",
                props=BlockProps(  # type: ignore
                    fields=[
                        BaseFieldConfig(  # type: ignore  # pyright: ignore[reportCallIssue]
                            label="HTML 内容",
                            key="html_content",
                            type="html",
                            description="这是一个HTML内容字段，可以渲染各种HTML标签"
                        ),
                        ImageFieldConfig(  # type: ignore  # pyright: ignore[reportCallIssue]
                            label="简单图片",
                            key="image_url",
                            type="image",
                            description="使用简单URL的图片字段"
                        ),
                        ImageFieldConfig(  # type: ignore  # pyright: ignore[reportCallIssue]
                            label="详细图片",
                            key="image_info",
                            type="image",
                            description="包含URL、alt文本和标题的图片字段"
                        ),
                        ImageFieldConfig(  # type: ignore  # pyright: ignore[reportCallIssue]
                            label="增强版图片",
                            key="enhanced_image",
                            type="image",
                            description="增强版图片，支持全屏查看、下载等功能",
                            showFullscreen=True,
                            showDownload=True,
                            imageHeight="400px",
                            imageFit="cover",
                            subtitle="点击可全屏查看，支持多种图片格式"
                        )
                    ]
                )
            )
        ],
        actions=[
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="to_demo",
                label="返回主页",
                style="secondary",
                action_type="navigate",
                target_instance="demo"
            ),
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="refresh_images",
                label="刷新图片",
                style="primary"
            ) # type: ignore
        ]
    )


def _create_block_actions_test_schema() -> UISchema:
    """创建 Block Actions 测试 Schema - 用于测试 block 级别的 actions"""
    from datetime import datetime
    return UISchema(
        meta=MetaInfo(
            pageKey="block_actions_test",
            step=StepInfo(current=1, total=1),
            status=StatusType.IDLE,
            schemaVersion="1.0",
            title=None,
            description=None
        ),
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
                type="form",
                bind="state.params",
                props=BlockProps(  # type: ignore
                    fields=[
                        TableFieldConfig(  # type: ignore  # pyright: ignore[reportCallIssue]
                            label="待办事项列表",
                            key="todo_list",
                            type="table",
                            rid=None,
                            value=None,
                            description="这是一个带 block 级别 actions 的待办事项列表",
                            columns=[
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
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="add_todo",
                            label="添加任务",
                            style="primary",
                            handler_type="set",
                            patches={
                                "state.params.todo_list": {
                                    "mode": "operation",
                                    "operation": "append_to_list",
                                    "params": {
                                        "items": [
                                            {
                                                "id": 5,
                                                "task": "新任务",
                                                "completed": False
                                            }
                                        ]
                                    }
                                }
                            }
                        ),
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="clear_completed",
                            label="清除已完成",
                            style="danger",
                            handler_type="set",
                            patches={
                                "state.params.todo_list": {
                                    "mode": "operation",
                                    "operation": "remove_from_list",
                                    "params": {
                                        "key": "completed",
                                        "value": True,
                                        "index": -1
                                    }
                                }
                            }
                        )
                    ]
                ) # type: ignore
            ),
            # Block 2: 消息显示和操作
            Block(
                id="message_block",
                type="form",
                bind="state.params",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig(  # pyright: ignore[reportCallIssue]
                            label="消息",
                            key="message",
                            type="text"
                        )
                    ],
                    # Block 级别的 actions
                    actions=[
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="update_message",
                            label="更新消息",
                            style="primary",
                            handler_type="set",
                            patches={
                                "state.params.message": "消息已更新！时间戳: ${state.runtime.timestamp}"
                            }
                        ),
                        ActionConfig(  # pyright: ignore[reportCallIssue]
                            id="clear_message",
                            label="清空消息",
                            style="secondary",
                            handler_type="set",
                            patches={
                                "state.params.message": ""
                            }
                        )
                    ]
                ) # type: ignore
            ),
            # Block 3: 显示当前时间（只读展示，无 actions）
            Block(
                id="info_block",
                type="display",
                bind="state.runtime",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[]
                ) # type: ignore
            )
        ],
        # 全局级别的 actions
        actions=[
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="reset_all",
                label="重置所有",
                style="danger",
                handler_type="set",
                patches={
                    "state.params.todo_list": [
                        {"id": 1, "task": "学习 Python", "completed": False},
                        {"id": 2, "task": "学习 FastAPI", "completed": True},
                        {"id": 3, "task": "学习 React", "completed": False}
                    ],
                    "state.params.message": "欢迎使用 Block Actions 测试页面！"
                }
            ),
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="to_demo",
                label="返回主页",
                style="secondary",
                action_type="navigate",
                target_instance="demo"
            )
        ]
    )



def _create_layouts_demo_schema() -> UISchema:
    """创建布局演示 Schema - 展示所有布局类型"""
    from datetime import datetime

    return UISchema(
        meta=MetaInfo(
            pageKey="layouts_demo",
            step=StepInfo(current=1, total=1),
            status=StatusType.IDLE,
            schemaVersion="1.0",
            title="布局类型演示",
            description="展示所有可用的布局类型",
            created_at=datetime.now()
        ),
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
                type="grid",
                bind="state.params",
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    cols=2,
                    gap="20px",
                    fields=[
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="姓名",
                            key="card_name",
                            type="text",
                            description="用户姓名"
                        ),
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="邮箱",
                            key="card_email",
                            type="text",
                            description="电子邮箱"
                        ),
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="电话",
                            key="card_phone",
                            type="text",
                            description="联系电话"
                        ),
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="年龄",
                            key="col_age",
                            type="number",
                            description="年龄"
                        ),
                    ]
                )
            ),

            # Block 2: Grid 布局（多列）
            Block(
                id="grid_layout_multi",
                type="grid",
                bind="state.params",
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    cols=2,
                    gap="20px",
                    fields=[
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="名",
                            key="col_first_name",
                            type="text",
                            description="名字"
                        ),
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="姓",
                            key="col_last_name",
                            type="text",
                            description="姓氏"
                        ),
                        SelectableFieldConfig( # pyright: ignore[reportCallIssue]
                            label="性别",
                            key="col_gender",
                            type="select",
                            options=[
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
                type="tabs",
                bind="state.params",
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
                type="accordion",
                bind="state.params",
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


def _create_top_level_layouts_demo_schema() -> UISchema:
    """创建顶层布局演示 Schema - 展示 layout.type 的不同效果"""
    from datetime import datetime

    return UISchema(
        meta=MetaInfo(
            pageKey="top_level_layouts_demo",
            step=StepInfo(current=1, total=1),
            status=StatusType.IDLE,
            schemaVersion="1.0",
            title="顶层布局演示",
            description="展示 layout.type 如何控制 blocks 和 actions 的排列",
            created_at=datetime.now()
        ),
        state=StateInfo(
            params=dict(
                section1_content="这是第一个区块的内容",
                section2_content="这是第二个区块的内容",
                section3_content="这是第三个区块的内容",
                section4_content="这是第四个区块的内容",
            ),
            runtime={}
        ),
        layout=LayoutInfo(
            type=LayoutType.GRID,  # 修改为 GRID/FLEX/CARD/TABS 来查看不同效果
            columns=2,
            gap="20px"
        ),
        blocks=[
            Block(
                id="section1",
                type="form",
                bind="state.params",
                order=0,
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="内容 1",
                            key="section1_content",
                            type="textarea",
                            description="第一个区块的内容"
                        ),
                    ]
                )
            ),
            Block(
                id="section2",
                type="form",
                bind="state.params",
                order=1,
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="内容 2",
                            key="section2_content",
                            type="textarea",
                            description="第二个区块的内容"
                        ),
                    ]
                )
            ),
            Block(
                id="section3",
                type="form",
                bind="state.params",
                order=2,
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="内容 3",
                            key="section3_content",
                            type="textarea",
                            description="第三个区块的内容"
                        ),
                    ]
                )
            ),
            Block(
                id="section4",
                type="form",
                bind="state.params",
                order=3,
                props=BlockProps( # pyright: ignore[reportCallIssue]
                    fields=[
                        BaseFieldConfig( # pyright: ignore[reportCallIssue]
                            label="内容 4",
                            key="section4_content",
                            type="textarea",
                            description="第四个区块的内容"
                        ),
                    ]
                )
            ),
        ],
        actions=[
            ActionConfig( # pyright: ignore[reportCallIssue]
                id="save_all",
                label="保存全部",
                style="primary",
                action_type=ActionType.API,
                handler_type=HandlerType.SET,
                patches={}
            ),
            ActionConfig( # pyright: ignore[reportCallIssue]
                id="reset_all",
                label="重置全部",
                style="danger",
                action_type=ActionType.API,
                handler_type=HandlerType.SET,
                patches={}
            ),
        ]
    )
