"""默认 Schema 实例"""

from .fastapi.models import UISchema, MetaInfo, StateInfo, LayoutInfo, Block, ActionConfig, StepInfo, BlockProps, FieldConfig


def get_default_instances() -> dict[str, UISchema]:
    """获取所有默认 Schema 实例"""
    return {
        "demo": _create_demo_schema(),
        "counter": _create_counter_schema(),
        "form": _create_form_schema(),
        "json_viewer": _create_json_viewer_schema(),
        "rich_content": _create_rich_content_schema(),
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
            params=dict(message="Hello Schema!", description="这是主页"),
            runtime={}
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="text_block",
                type="form",
                bind="state.params",
                props=BlockProps(
                    fields=[
                        FieldConfig(
                            label="消息",
                            key="message",
                            type="text",
                            rid=None,
                            value=None,
                            description=None,
                            options=None
                        ) # type: ignore
                        ,
                        FieldConfig(
                            label="描述",
                            key="description",
                            type="text",
                            rid=None,
                            value=None,
                            description=None,
                            options=None
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
            ActionConfig(
                id="to_counter", 
                label="打开计数器", 
                style="secondary",
                action_type="navigate",
                target_instance="counter"
            ),
            ActionConfig(
                id="to_form", 
                label="打开表单", 
                style="secondary",
                action_type="navigate",
                target_instance="form"
            ),
            ActionConfig(
                id="to_json", 
                label="JSON查看器", 
                style="secondary",
                action_type="navigate",
                target_instance="json_viewer"
            ),
            ActionConfig(
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
                        FieldConfig(
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
            ActionConfig(id="increment", label="+1", style="primary"), # type: ignore
            ActionConfig(id="decrement", label="-1", style="secondary"), # type: ignore
            ActionConfig(
                id="to_form", 
                label="跳转到表单", 
                style="secondary",
                action_type="navigate",
                target_instance="form"
            )
        ]
    )


def _create_form_schema() -> UISchema:
    """创建表单 Schema"""
    return UISchema(
        meta=MetaInfo(
            pageKey="form",
            step=StepInfo(current=1, total=1),
            status="idle",
            schemaVersion="1.0"
        ),
        state=StateInfo(
            params=dict(name="", email=""),
            runtime={}
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="form_block",
                type="form",
                bind="state.params",
                props=BlockProps(
                    fields=[
                        FieldConfig(
                            label="姓名",
                            key="name",
                            type="text",
                        ), # type: ignore
                        FieldConfig(
                            label="邮箱",
                            key="email",
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
            ActionConfig(id="submit", label="提交", style="primary"), # type: ignore
            ActionConfig(id="clear", label="清空", style="danger"), # type: ignore
            ActionConfig(
                id="to_counter", 
                label="跳转到计数器", 
                style="secondary",
                action_type="navigate",
                target_instance="counter"
            ),
            ActionConfig(
                id="to_demo", 
                label="跳转到主页", 
                style="secondary",
                action_type="navigate",
                target_instance="demo"
            )
        ]
    )


def _create_json_viewer_schema() -> UISchema:
    """创建 JSON 查看器 Schema"""
    return UISchema(
        meta=MetaInfo(
            pageKey="json_viewer",
            step=StepInfo(current=1, total=1),
            status="idle",
            schemaVersion="1.0"
        ),
        state=StateInfo(
            params=dict(
                json_data={"example": "data", "number": 123, "nested": {"key": "value"}},
                editable=True,
                theme="light"
            ),
            runtime={}
        ),
        layout=LayoutInfo(type="single"),
        blocks=[
            Block(
                id="json_block",
                type="form",
                bind="state.params",
                props=BlockProps(
                    fields=[
                        FieldConfig(
                            label="JSON 数据",
                            key="json_data",
                            type="json",
                            content_type="json",
                            editable=True,
                            description="可编辑的JSON数据"
                        ), # type: ignore
                        FieldConfig(
                            label="可编辑模式",
                            key="editable",
                            type="checkbox",
                            description="启用/禁用编辑功能"
                        ), # type: ignore
                        FieldConfig(
                            label="主题",
                            key="theme",
                            type="select",
                            options=[
                                {"label": "浅色", "value": "light"},
                                {"label": "深色", "value": "dark"}
                            ]
                        ) # type: ignore
                    ]
                ) # type: ignore
            )
        ],
        actions=[
            ActionConfig(id="format", label="格式化", style="secondary"), # type: ignore
            ActionConfig(id="validate", label="验证JSON", style="primary"), # type: ignore
            ActionConfig(id="clear", label="清空", style="danger"), # type: ignore
            ActionConfig(
                id="to_demo", 
                label="返回主页", 
                style="secondary",
                action_type="navigate",
                target_instance="demo"
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
                        FieldConfig(
                            label="HTML 内容",
                            key="html_content",
                            type="html",
                            description="这是一个HTML内容字段，可以渲染各种HTML标签"
                        ), # type: ignore
                        FieldConfig(
                            label="简单图片",
                            key="image_url",
                            type="image",
                            description="使用简单URL的图片字段"
                        ), # type: ignore
                        FieldConfig(
                            label="详细图片",
                            key="image_info",
                            type="image",
                            description="包含URL、alt文本和标题的图片字段"
                        ), # type: ignore
                        FieldConfig(
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
            ActionConfig(
                id="to_demo", 
                label="返回主页", 
                style="secondary",
                action_type="navigate",
                target_instance="demo"
            ),
            ActionConfig(
                id="refresh_images", 
                label="刷新图片", 
                style="primary"
            ) # type: ignore
        ]
    )