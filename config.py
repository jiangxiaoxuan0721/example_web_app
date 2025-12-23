#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

class Config:
    """应用配置"""
    # 使用 pathlib 获取项目根目录
    BASE_DIR = Path(__file__).resolve().parent
    
    # 目录配置 - 使用绝对路径
    BACKEND_DIR = BASE_DIR / 'backend'
    FRONTEND_DIR = BASE_DIR / 'frontend'
    OUTPUT_DIR = BASE_DIR / 'output'
    TEMPLATE_DIR = BASE_DIR / 'frontend' / 'pages'
    STATIC_DIR = BASE_DIR / 'frontend'

    # 服务器配置
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 50890))
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

    # CloudPSS 配置 - 从环境变量读取
    CLOUDPSS = {
        "TOKEN": os.getenv('CLOUDPSS_TOKEN', ''),
        "API_URL": os.getenv('CLOUDPSS_API_URL', 'https://cloudpss.net/')
    }

    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'h5', 'hdf5', 'json', 'txt'}