"""默认 Schema 实例"""

from ..fastapi.models import UISchema, MetaInfo, StateInfo, LayoutInfo, Block, ActionConfig, StepInfo, BlockProps, FieldConfig


def get_default_instances() -> dict[str, UISchema]:
    """获取所有默认 Schema 实例"""
    return {
        "demo": _create_demo_schema(),
        "counter": _create_counter_schema(),
        "rich_content": _create_rich_content_schema(),
        "block_actions_test": _create_block_actions_test_schema(),
    }


def _create_demo_schema() -> UISchema:
    """创建 demo Schema"""
    return UISchema(
        meta=MetaInfo(
            pageKey="demo",
            step=StepInfo(current=1, total=1),
            status="idle",
            schemaVersion="1.0"
        ),
        state=StateInfo(
            params=dict(
                users=[
                    {"id": 1, "name": "张三", "email": "zhangsan@example.com", "status": "active", "avatar": "https://picsum.photos/seed/zhangsan/100/100.jpg"},
                    {"id": 2, "name": "李四", "email": "lisi@example.com", "status": "inactive", "avatar": "https://picsum.photos/seed/lisi/100/100.jpg"},
                    {"id": 3, "name": "王五", "email": "wangwu@example.com", "status": "active", "avatar": "https://picsum.photos/seed/wangwu/100/100.jpg"},
                    {"id": 4, "name": "赵六", "email": "zhaoliu@example.com", "status": "pending", "avatar": "https://picsum.photos/seed/zhaoliu/100/100.jpg"},
                    {"id": 5, "name": "钱七", "email": "qianqi@example.com", "status": "active", "avatar": "https://picsum.photos/seed/qianqi/100/100.jpg"}
                ]
            ),
            runtime={}
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="demo_block",
                type="form",
                bind="state.params",
                props=BlockProps(
                    fields=[
                        FieldConfig(  # pyright: ignore[reportCallIssue]
                            label="用户列表",
                            key="users",
                            type="table",
                            rid=None,
                            value=None,
                            description="示例用户数据表格",
                            options=None,
                            columns=[
                                {"key": "id", "label": "ID", "align": "center"},
                                {"key": "name", "label": "姓名", "sortable": True},
                                {"key": "email", "label": "邮箱"},
                                {"key": "avatar", "label": "头像", "renderType": "image"},
                                {"key": "status", "label": "状态", "renderType": "tag", "tagType": "value => value === 'active' ? 'success' : value === 'inactive' ? 'default' : 'warning'"}
                            ],
                            rowKey="id",
                            bordered=True,
                            striped=True,
                            hover=True
                        ) # type: ignore
                    ],
                    showProgress=None,
                    showStatus=None,
                    showImages=None,
                    showTable=None,
                    showCountInput=None,
                    showTaskId=None
                )
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
                        "operation": "append_to_list",
                        "params": {
                            "item": {
                                "id": 6,
                                "name": "赵六",
                                "email": "zhaoliu@example.com",
                                "status": "pending",
                                "avatar": "https://picsum.photos/seed/zhaoliu/100/100.jpg"
                            }
                        }
                    }
                }
            ),
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="reset_users",
                label="重置用户",
                style="secondary",
                handler_type="set",
                patches={"state.params.users": [
                    {"id": 1, "name": "张三", "email": "zhangsan@example.com", "status": "active", "avatar": "https://picsum.photos/seed/zhangsan/100/100.jpg"},
                    {"id": 2, "name": "李四", "email": "lisi@example.com", "status": "inactive", "avatar": "https://picsum.photos/seed/lisi/100/100.jpg"},
                    {"id": 3, "name": "王五", "email": "wangwu@example.com", "status": "active", "avatar": "https://picsum.photos/seed/wangwu/100/100.jpg"}
                ]}
            ),
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="generate_block",
                label="生成 Block",
                style="primary",
                handler_type="set",
                patches={
                    "blocks": {
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
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="to_rich_content",
                label="富内容展示",
                style="secondary",
                action_type="navigate",
                target_instance="rich_content"
            )
        ]
    )


def _create_counter_schema() -> UISchema:
    """创建计数器 Schema"""
    return UISchema(
        meta=MetaInfo(
            pageKey="counter",
            step=StepInfo(current=1, total=1),
            status="idle",
            schemaVersion="1.0"
        ),
        state=StateInfo(
            params=dict(count=0),
            runtime={}
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="counter_block",
                type="form",
                bind="state.params",
                props=BlockProps(
                    fields=[
                        FieldConfig(  # pyright: ignore[reportCallIssue]
                            label="计数器",
                            key="count",
                            type="text",
                        ) # type: ignore
                    ],
                    showProgress=None,
                    showStatus=None,
                    showImages=None,
                    showTable=None,
                    showCountInput=None,
                    showTaskId=None
                )
            )
        ],
        actions=[
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="increment",
                label="+1",
                style="primary",
                handler_type="increment",
                patches={"state.params.count": 1}
            ),
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="decrement",
                label="-1",
                style="secondary",
                handler_type="decrement",
                patches={"state.params.count": 1}
            ),
            ActionConfig(  # pyright: ignore[reportCallIssue]
                id="to_form",
                label="跳转到表单",
                style="secondary",
                action_type="navigate",
                target_instance="form"
            )
        ]
    )


def _create_rich_content_schema() -> UISchema:
    """创建富内容展示 Schema"""
    return UISchema(
        meta=MetaInfo(
            pageKey="rich_content",
            step=StepInfo(current=1, total=1),
            status="idle",
            schemaVersion="1.0"
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
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="rich_content_block",
                type="form",
                bind="state.params",
                props=BlockProps(
                    fields=[
                        FieldConfig(  # pyright: ignore[reportCallIssue]
                            label="HTML 内容",
                            key="html_content",
                            type="html",
                            description="这是一个HTML内容字段，可以渲染各种HTML标签"
                        ), # type: ignore
                        FieldConfig(  # pyright: ignore[reportCallIssue]
                            label="简单图片",
                            key="image_url",
                            type="image",
                            description="使用简单URL的图片字段"
                        ), # type: ignore
                        FieldConfig(  # pyright: ignore[reportCallIssue]
                            label="详细图片",
                            key="image_info",
                            type="image",
                            description="包含URL、alt文本和标题的图片字段"
                        ), # type: ignore
                        FieldConfig(  # pyright: ignore[reportCallIssue]
                            label="增强版图片",
                            key="enhanced_image",
                            type="image",
                            description="增强版图片，支持全屏查看、下载等功能",
                            showFullscreen=True,
                            showDownload=True,
                            imageHeight="400px",
                            imageFit="cover",
                            subtitle="点击可全屏查看，支持多种图片格式"
                        ) # type: ignore
                    ],
                    showProgress=None,
                    showStatus=None,
                    showImages=None,
                    showTable=None,
                    showCountInput=None,
                    showTaskId=None
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
            status="idle",
            schemaVersion="1.0"
        ),
        state=StateInfo(
            params=dict(
                todo_list=[
                    {"id": 1, "task": "学习 Python", "completed": False},
                    {"id": 2, "task": "学习 FastAPI", "completed": True},
                    {"id": 3, "task": "学习 React", "completed": False}
                ],
                message="欢迎使用 Block Actions 测试页面！"
            ),
            runtime={"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            # Block 1: 带有 block 级别 actions 的待办事项列表
            Block(
                id="todo_block",
                type="form",
                bind="state.params",
                props=BlockProps(  # pyright: ignore[reportCallIssue]
                    fields=[
                        FieldConfig(  # pyright: ignore[reportCallIssue]
                            label="待办事项列表",
                            key="todo_list",
                            type="table",
                            rid=None,
                            value=None,
                            description="这是一个带 block 级别 actions 的待办事项列表",
                            options=None,
                            columns=[
                                {"key": "id", "label": "ID", "align": "center"},
                                {"key": "task", "label": "任务", "sortable": True},
                                {"key": "completed", "label": "状态", "renderType": "tag", "tagType": "value => value ? 'success' : 'default'"}
                            ],
                            rowKey="id",
                            bordered=True,
                            striped=True,
                            hover=True
                        ) # type: ignore
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
                                    "operation": "append_to_list",
                                    "params": {
                                        "item": {
                                            "id": 4,
                                            "task": "新任务",
                                            "completed": False
                                        }
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
                                    "operation": "remove_from_list",
                                    "params": {
                                        "key": "completed",
                                        "value": True
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
                        FieldConfig(  # pyright: ignore[reportCallIssue]
                            label="消息",
                            key="message",
                            type="text",
                        ) # type: ignore
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