"""字段配置模型模块  # pyright: ignore[reportImportCycles]
包含字段、选项、列配置等模型定义

设计原则：
1. 使用类继承而不是字段覆写，确保类型安全
2. 基类不包含 type 字段，由子类定义
3. 每个具体类型独立定义，避免类型警告
"""

from typing import Any, Literal, TypeAlias, Union
from pydantic import Field

from .base import BaseModelWithConfig
from .enums import FieldType
from .block_models import Block


class OptionItem(BaseModelWithConfig):
    """选项项"""
    label: str = Field(default=..., description="显示标签")
    value: str = Field(default=..., description="选项值")
    disabled: bool = Field(default=False, description="是否禁用")
    description: str | None = Field(default=None, description="选项描述")


class ColumnConfig(BaseModelWithConfig):
    """表格列配置"""
    key: str = Field(default=..., description="列键")
    title: str = Field(default=..., description="列标题")
    width: str | None = Field(default=None, description="列宽")
    sortable: bool = Field(default=False, description="是否可排序")
    filterable: bool = Field(default=False, description="是否可过滤")
    align: Literal["left", "center", "right"] = Field(default="left", description="对齐方式")
    render_type: str | None = Field(
        default=None,
        alias="renderType",
        description="渲染类型: 'text' | 'tag' | 'badge' | 'progress' | 'image' | 'mixed'"
    )
    tag_type: str | None = Field(
        default=None,
        alias="tagType",
        description="标签类型（用于tag渲染，支持表达式如 'value => value === \"active\" ? \"success\" : \"default\"'）"
    )
    badge_color: str | None = Field(
        default=None,
        alias="badgeColor",
        description="徽章颜色（用于badge渲染，如 '#1890ff'）"
    )
    components: list[dict[str, Any]] | None = Field(
        default=None,
        description="混合渲染组件配置（用于mixed类型，支持 text, tag, badge, progress, image, button, spacer）"
    )
    editable: bool = Field(default=True, description="该列是否可编辑（仅当 tableEditable 为 true 时生效）")
    edit_type: Literal["text", "number", "select"] = Field(default="text", alias="editType", description="编辑器类型: text/number/select")
    options: list[OptionItem] | None = Field(default=None, description="编辑器选项（仅 editType=select 时使用）")


class _BaseFieldConfig(BaseModelWithConfig):
    """字段配置基类（不包含 type 字段）"""
    label: str = Field(default=..., description="标签")
    key: str = Field(default=..., description="键（唯一标识）")
    value: Any | None = Field(default=None, description="值")
    description: str | None = Field(default=None, description="描述")
    editable: bool = Field(default=True, description="是否可编辑")
    required: bool = Field(default=False, description="是否必填")
    disabled: bool = Field(default=False, description="是否禁用")
    placeholder: str | None = Field(default=None, description="占位符")


class BaseFieldConfig(_BaseFieldConfig):
    """通用字段配置（text, number, textarea, date, datetime, file, html, json 等类型）"""
    type: FieldType


class SelectableFieldConfig(_BaseFieldConfig):
    """可选择字段配置（select, radio, multiselect 类型）"""
    type: Literal[FieldType.SELECT, FieldType.RADIO, FieldType.MULTISELECT]
    options: list[OptionItem] = Field(..., description="选项列表")
    multiple: bool = Field(default=False, description="是否多选（仅select类型）")


class ImageFieldConfig(_BaseFieldConfig):
    """图片字段配置"""
    type: Literal[FieldType.IMAGE]
    show_fullscreen: bool = Field(default=True, alias="showFullscreen", description="显示全屏按钮")
    show_download: bool = Field(default=True, alias="showDownload", description="显示下载按钮")
    image_height: str = Field(default="auto", alias="imageHeight", description="图片高度")
    image_fit: Literal["contain", "cover", "fill"] = Field(
        default="contain",
        alias="imageFit",
        description="图片适应方式"
    )
    lazy: bool = Field(default=False, description="懒加载")
    fallback: str | None = Field(default=None, description="加载失败回退内容")
    subtitle: str | None = Field(default=None, description="子标题")
    alt: str | None = Field(default=None, description="替代文本")


class TableFieldConfig(_BaseFieldConfig):
    """表格字段配置"""
    type: Literal[FieldType.TABLE]
    columns: list[ColumnConfig] = Field(default=..., description="表格列配置")
    row_key: str = Field(default="id", alias="rowKey", description="行唯一标识字段")
    bordered: bool = Field(default=True, description="显示边框")
    striped: bool = Field(default=True, description="斑马纹")
    hover: bool = Field(default=True, description="悬停效果")
    empty_text: str = Field(default="暂无数据", alias="emptyText", description="空数据提示")
    table_editable: bool = Field(default=False, alias="tableEditable", description="表格是否可编辑")
    show_header: bool = Field(default=True, alias="showHeader", description="显示表头")
    show_pagination: bool = Field(default=False, alias="showPagination", description="显示分页")
    page_size: int = Field(default=10, alias="pageSize", description="每页显示条数")
    max_height: str | None = Field(default=None, alias="maxHeight", description="最大高度")
    compact: bool = Field(default=False, description="紧凑模式")
    row_selection: bool = Field(default=False, description="行选择")


class ComponentFieldConfig(_BaseFieldConfig):
    """组件嵌入字段配置 - 渲染一个 Block"""
    type: Literal[FieldType.COMPONENT]
    # 要渲染的 Block 配置（使用字符串前向引用以避免循环引用）
    block_config: "Block" = Field(default=..., alias="blockConfig", description="要渲染的嵌套Block配置")


# 字段配置类型联合（使用判别式联合）
FieldConfig: TypeAlias = Union[
    BaseFieldConfig,
    SelectableFieldConfig,
    ImageFieldConfig,
    TableFieldConfig,
    ComponentFieldConfig
]
