"""
MCP 工具接口定义

此文件包含 PATCH_SPEC.md 中定义的接口的代码形式。
使用 backend.fastapi.models 中已定义的类型，确保一致性。
"""

from typing import  Any, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

# 从已有的模型导入
from backend.fastapi.models import *

# 定义操作类型
PatchOp = Literal["set", "add", "remove", "clear", "delete", "create", "replace"]

class PatchOperation(BaseModel):
    """补丁操作定义"""
    op: PatchOp = Field(..., description="操作类型")
    path: str = Field(..., description="点分隔路径到目标")
    value: Any | None = Field(None, description="新值（用于'set', 'add', 'replace'）")
    items: Optional[list[Any]] = Field(None, description="要添加的项目（用于'add'）")
    condition: str | None = Field(None, description="可选条件")

class PatchInput(BaseModel):
    """补丁输入接口"""
    instance_id: str = Field(..., description="目标实例（如 'demo', 'counter', 'form'）")
                                 # 使用 "__CREATE__" 创建新实例
                                 # 使用 "__DELETE__" 删除实例
    new_instance_id: str | None = Field(None, description="当 instance_id == '__CREATE__' 时必需")
    target_instance_id: str | None = Field(None, description="当 instance_id == '__DELETE__' 时必需")
    patches: list[PatchOperation] = Field(default_factory=list, description="补丁操作数组")

# 扩展版本，包含字段操作快捷方式（已弃用，保留用于向后兼容）
class PatchInputWithShortcuts(BaseModel):
    """带有字段操作快捷方式的补丁输入接口（已弃用，请使用 PatchInput）"""
    instance_id: str = Field(..., description="目标实例（如 'demo', 'counter', 'form'）")
                                 # 使用 "__CREATE__" 创建新实例
                                 # 使用 "__DELETE__" 删除实例
    new_instance_id: str | None = Field(None, description="当 instance_id == '__CREATE__' 时必需")
    target_instance_id: str | None = Field(None, description="当 instance_id == '__DELETE__' 时必需")
    patches: list[PatchOperation] = Field(default_factory=list, description="补丁操作数组（使用字段快捷方式时为可选）")

class CompletionCriterion(BaseModel):
    """完成标准"""
    type: Literal["field_exists", "field_value", "block_count", "action_exists", "custom"] = Field(..., description="标准类型")
    path: str | None = Field(None, description="字段路径（用于字段相关标准）")
    value: Any | None = Field(None, description="期望值（用于 field_value 标准）")
    count: int | None = Field(None, description="期望计数（用于 block_count 标准）")
    condition: str | None = Field(None, description="自定义验证表达式（用于自定义标准）")
    description: str = Field(..., description="人类可读的标准描述")

class ValidateCompletionInput(BaseModel):
    """验证完成输入"""
    instance_id: str = Field(..., description="要验证的实例 ID")
    intent: str = Field(..., description="UI 应完成的高级描述")
    completion_criteria: list[CompletionCriterion] = Field(..., description="要检查的标准列表")

class ValidateCompletionResult(BaseModel):
    """验证完成结果"""
    evaluation: dict[str, Any] = Field(..., description="评估指标")
        # passed_criteria: 通过的标准数
        # total_criteria: 总评估标准数
        # completion_ratio: 通过到总数比率（0.0 到 1.0）
        # detailed_results: 个别标准结果数组
    summary: str = Field(..., description="当前状态的高级评估")
    recommendations: list[str] = Field(default_factory=list, description="建议的下一步操作")
