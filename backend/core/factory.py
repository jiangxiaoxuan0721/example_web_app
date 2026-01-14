"""Schema 工厂 - 创建默认 Schema 实例"""

from ..fastapi.models import (
    UISchema, MetaInfo, StateInfo, LayoutInfo,
    Block, BlockProps, FieldConfig, ActionConfig, StepInfo
)


def create_demo_schema() -> UISchema:
    """创建 demo 实例的 Schema"""
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
                            type="text"
                        )
                    ]
                )
            )
        ],
        actions=[
            ActionConfig(id="click_me", label="Click Me", style="primary")
        ]
    )


def create_counter_schema() -> UISchema:
    """创建 counter 实例的 Schema"""
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
                            type="text"
                        )
                    ]
                )
            )
        ],
        actions=[
            ActionConfig(id="increment", label="+1", style="primary"),
            ActionConfig(id="decrement", label="-1", style="secondary")
        ]
    )


def create_form_schema() -> UISchema:
    """创建 form 实例的 Schema"""
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
                            type="text"
                        ),
                        FieldConfig(
                            label="邮箱",
                            key="email",
                            type="text"
                        )
                    ]
                )
            )
        ],
        actions=[
            ActionConfig(id="submit", label="提交", style="primary"),
            ActionConfig(id="clear", label="清空", style="danger")
        ]
    )


def create_default_instances() -> dict:
    """创建所有默认实例"""
    return {
        "demo": create_demo_schema(),
        "counter": create_counter_schema(),
        "form": create_form_schema()
    }