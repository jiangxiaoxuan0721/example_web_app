#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

class Config:
    """应用配置"""
    BACKEND_DIR = os.path.join(os.path.dirname(__file__), 'backend')
    FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'frontend', 'templates')
    STATIC_DIR = os.path.join(os.path.dirname(__file__), 'frontend', 'static')

    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 50890
    DEBUG = True

    CLOUDPSS = {
        "TOKEN": "<CloudPSS Token>",
        "API_URL": "https://cloudpss.net/"
    }