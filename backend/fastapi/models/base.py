"""基础模型模块

包含基础配置模型和通用配置
"""

from pydantic import BaseModel, ConfigDict


class BaseModelWithConfig(BaseModel):
    """基础模型，包含通用配置"""
    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",  # 禁止额外字段
        by_alias=True  # 序列化时使用别名
    )
