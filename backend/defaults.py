"""默认 Schema 实例"""

from .fastapi.models import UISchema, MetaInfo, StateInfo, LayoutInfo, Block, ActionConfig, StepInfo, BlockProps, FieldConfig


def get_default_instances() -> dict[str, UISchema]:
    """获取所有默认 Schema 实例"""
    return {
        "demo": _create_demo_schema(),
        "counter": _create_counter_schema(),
        "form": _create_form_schema(),
        "json_viewer": _create_json_viewer_schema(),
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
            params=dict(message="Hello Schema!"),
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
            ActionConfig(id="click_me", label="Click Me", style="primary")
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
                            rid=None,
                            value=None,
                            description=None,
                            options=None,
                            content_type=None,
                            editable=False
                        )
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
            ActionConfig(id="increment", label="+1", style="primary"),
            ActionConfig(id="decrement", label="-1", style="secondary")
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
                            rid=None,
                            value=None,
                            description=None,
                            options=None,
                            content_type=None,
                            editable=True
                        ),
                        FieldConfig(
                            label="邮箱",
                            key="email",
                            type="text",
                            rid=None,
                            value=None,
                            description=None,
                            options=None,
                            content_type=None,
                            editable=True
                        )
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
            ActionConfig(id="submit", label="提交", style="primary"),
            ActionConfig(id="clear", label="清空", style="danger")
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
            ActionConfig(id="format", label="格式化", style="secondary"),
            ActionConfig(id="validate", label="验证JSON", style="primary"),
            ActionConfig(id="clear", label="清空", style="danger")
        ]
    )
