"""FastAPI 应用配置"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用设置
    app_name: str = "Schema-Driven UI Backend"
    app_version: str = "1.0.0"
    debug: bool = True

    # 服务器设置
    host: str = "0.0.0.0"
    port: int = 8001

    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
