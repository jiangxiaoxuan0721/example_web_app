"""枚举定义模块

包含所有系统使用的枚举类型定义
"""

from enum import Enum


class EventType(str, Enum):
    """事件类型枚举"""
    FIELD_CHANGE = "field_change"
    ACTION_CLICK = "action_click"
    SELECT_MODE = "select_mode"
    CONFIRM_STEP = "confirm_step"
    PAGE_LOAD = "page_load"

class ActionType(str, Enum):
    """操作类型枚举"""
    API = "api"
    NAVIGATE = "navigate"
    NAVIGATE_BLOCK = "navigate_block"
    PATCH = "apply_patch"


class PatchOperationType(str, Enum):
    """操作类型枚举"""
    # Schema 操作
    SET = "set"
    ADD = "add"
    REMOVE = "remove"
    # 列表操作
    APPEND_TO_LIST = "append_to_list"
    PREPEND_TO_LIST = "prepend_to_list"
    REMOVE_FROM_LIST = "remove_from_list"
    UPDATE_LIST_ITEM = "update_list_item"
    FILTER_LIST = "filter_list"
    REMOVE_LAST = "remove_last"
    MERGE = "merge"
    # 参数操作
    INCREMENT = "increment"
    DECREMENT = "decrement"
    TOGGLE = "toggle"
    # 全局操作
    CLEAR_ALL_PARAMS = "clear_all_params"


class HTTPMethod(str, Enum):
    """HTTP 方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class BodyTemplateType(str, Enum):
    """请求体模板类型枚举"""
    JSON = "json"
    FORM = "form"


class FieldType(str, Enum):
    """字段类型枚举"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    SELECT = "select"
    RADIO = "radio"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    JSON = "json"
    IMAGE = "image"
    TABLE = "table"
    COMPONENT = "component"
    DATE = "date"
    DATETIME = "datetime"
    FILE = "file"
    HTML = "html"
    TAG = "tag"
    PROGRESS = "progress"
    BADGE = "badge"


class LayoutType(str, Enum):
    """布局类型枚举"""
    SINGLE = "single"
    GRID = "grid"
    FLEX = "flex"
    TABS = "tabs"