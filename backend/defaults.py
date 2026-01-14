"""默认 Schema 实例"""

from .fastapi.models import UISchema, MetaInfo, StateInfo, LayoutInfo, Block, ActionConfig, StepInfo, BlockProps, FieldConfig


def get_default_instances() -> dict[str, UISchema]:
    """获取所有默认 Schema 实例"""
    return {
        "demo": _create_demo_schema(),
        "counter": _create_counter_schema(),
        "form": _create_form_schema(),
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
                            options=None
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
                            options=None
                        ),
                        FieldConfig(
                            label="邮箱",
                            key="email",
                            type="text",
                            rid=None,
                            value=None,
                            description=None,
                            options=None
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
