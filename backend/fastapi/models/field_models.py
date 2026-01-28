"""字段配置模型模块

包含字段、选项、列配置等模型定义

设计原则：
1. 使用类继承而不是字段覆写，确保类型安全
2. 基类不包含 type 字段，由子类定义
3. 每个具体类型独立定义，避免类型警告
"""

from typing import Any, Optional, Union, Literal
from pydantic import BaseModel, Field

from .base import BaseModelWithConfig
from .enums import FieldType


class OptionItem(BaseModelWithConfig):
    """选项项"""
    label: str = Field(..., description="显示标签")
    value: str = Field(..., description="选项值")
    disabled: bool = Field(default=False, description="是否禁用")
    description: Optional[str] = Field(None, description="选项描述")


class ColumnConfig(BaseModelWithConfig):
    """表格列配置"""
    key: str = Field(..., description="列键")
    title: str = Field(..., description="列标题")
    width: Optional[str] = Field(None, description="列宽")
    sortable: bool = Field(default=False, description="是否可排序")
    filterable: bool = Field(default=False, description="是否可过滤")
    align: Literal["left", "center", "right"] = Field(default="left", description="对齐方式")
    renderType: Optional[str] = Field(
        None,
        description="渲染类型: 'text' | 'tag' | 'badge' | 'progress' | 'image' | 'mixed'"
    )
    tagType: Optional[str] = Field(None, description="标签类型（用于tag渲染，支持表达式如 'value => value === \"active\" ? \"success\" : \"default\"'）")
    badgeColor: Optional[str] = Field(None, description="徽章颜色（用于badge渲染，如 '#1890ff'）")
    components: Optional[list[dict[str, Any]]] = Field(None, description="混合渲染组件配置（用于mixed类型，支持 text, tag, badge, progress, image, button, spacer）")


class _BaseFieldConfig(BaseModelWithConfig):
    """字段配置基类（不包含 type 字段）"""
    label: str = Field(..., description="标签")
    key: str = Field(..., description="键（唯一标识）")
    rid: Optional[str] = Field(None, description="资源ID")
    value: Optional[Any] = Field(None, description="值")
    description: Optional[str] = Field(None, description="描述")
    content_type: Optional[str] = Field(None, description="内容类型")
    editable: bool = Field(default=True, description="是否可编辑")
    required: bool = Field(default=False, description="是否必填")
    disabled: bool = Field(default=False, description="是否禁用")
    placeholder: Optional[str] = Field(None, description="占位符")
    help_text: Optional[str] = Field(None, description="帮助文本")
    validation_rules: list[str] = Field(default_factory=list, description="验证规则")
    visible: bool = Field(default=True, description="是否可见")


class BaseFieldConfig(_BaseFieldConfig):
    """通用字段配置（text, number, textarea, date, datetime, file, html, json 等类型）"""
    type: Literal[FieldType.TEXT, FieldType.NUMBER, FieldType.TEXTAREA, FieldType.DATE,
                  FieldType.DATETIME, FieldType.FILE, FieldType.HTML, FieldType.JSON,
                  FieldType.TAG, FieldType.PROGRESS, FieldType.BADGE, FieldType.MODAL]


class SelectableFieldConfig(_BaseFieldConfig):
    """可选择字段配置（select, radio, multiselect 类型）"""
    type: Literal[FieldType.SELECT, FieldType.RADIO, FieldType.MULTISELECT]
    options: list[OptionItem] = Field(..., description="选项列表")
    multiple: bool = Field(default=False, description="是否多选（仅select类型）")
    allow_clear: bool = Field(default=True, description="是否允许清除（仅select类型）")


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
    fallback: Optional[str] = Field(None, description="加载失败回退内容")
    subtitle: Optional[str] = Field(None, description="子标题")
    alt: Optional[str] = Field(None, description="替代文本")


class TableFieldConfig(_BaseFieldConfig):
    """表格字段配置"""
    type: Literal[FieldType.TABLE]
    columns: list[ColumnConfig] = Field(..., description="表格列配置")
    row_key: str = Field(default="id", alias="rowKey", description="行唯一标识字段")
    bordered: bool = Field(default=True, description="显示边框")
    striped: bool = Field(default=True, description="斑马纹")
    hover: bool = Field(default=True, description="悬停效果")
    empty_text: str = Field(default="暂无数据", alias="emptyText", description="空数据提示")
    table_editable: bool = Field(default=False, alias="tableEditable", description="表格是否可编辑")
    show_header: bool = Field(default=True, alias="showHeader", description="显示表头")
    show_pagination: bool = Field(default=False, alias="showPagination", description="显示分页")
    page_size: int = Field(default=10, alias="pageSize", description="每页显示条数")
    max_height: Optional[str] = Field(None, alias="maxHeight", description="最大高度")
    compact: bool = Field(default=False, description="紧凑模式")
    row_selection: bool = Field(default=False, description="行选择")


class ComponentFieldConfig(_BaseFieldConfig):
    """组件嵌入字段配置"""
    type: Literal[FieldType.COMPONENT]
    target_instance: str = Field(..., alias="targetInstance", description="目标实例ID")
    target_block: Optional[str] = Field(None, alias="targetBlock", description="目标block ID")
    component_props: dict[str, Any] = Field(default_factory=dict, description="组件属性")


# 字段配置类型联合（使用判别式联合）
FieldConfig = Union[
    BaseFieldConfig,
    SelectableFieldConfig,
    ImageFieldConfig,
    TableFieldConfig,
    ComponentFieldConfig
]
