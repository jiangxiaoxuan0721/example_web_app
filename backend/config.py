"""FastAPI 应用配置"""

from pydantic_settings import BaseSettings
from typing import Optional
import json
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用设置
    app_name: str = "Schema-Driven UI Backend"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 服务器设置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS 设置
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # 配置文件路径
    config_path: str = "../frontend/src/data/wizard_config.json"
    
    # MCP 设置
    mcp_enabled: bool = True
    mcp_server_name: str = "schema-ui-backend"
    mcp_server_version: str = "1.0.0"
    mcp_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or settings.config_path
        self._config_cache = None
    
    def load_config(self) -> dict:
        """加载 Wizard 配置"""
        if self._config_cache:
            return self._config_cache
        
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                # 尝试相对路径
                config_file = Path(__file__).parent.parent.parent / self.config_path
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config_cache = json.load(f)
            return self._config_cache
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {"modes": {}, "components": {}}
    
    def get_modes(self) -> dict:
        """获取所有模式"""
        config = self.load_config()
        return config.get("modes", {})
    
    def get_mode(self, mode_id: str) -> Optional[dict]:
        """获取指定模式"""
        modes = self.get_modes()
        return modes.get(mode_id)
    
    def get_components(self) -> dict:
        """获取所有组件配置"""
        config = self.load_config()
        return config.get("components", {})
    
    def get_component(self, component_id: str) -> Optional[dict]:
        """获取指定组件配置"""
        components = self.get_components()
        return components.get(component_id)
    
    def get_step(self, mode_id: str, step_index: int) -> Optional[dict]:
        """获取指定步骤"""
        mode = self.get_mode(mode_id)
        if not mode:
            return None
        
        steps = mode.get("steps", [])
        if step_index < 0 or step_index >= len(steps):
            return None
        
        return steps[step_index]
    
    def reload(self):
        """重新加载配置"""
        self._config_cache = None


# 全局配置管理器实例
config_manager = ConfigManager()
