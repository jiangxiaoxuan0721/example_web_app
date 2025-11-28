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
        "TOKEN": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTA4NDYsInVzZXJuYW1lIjoiamlhbmd4aWFveHVhbjA3MjEiLCJzY29wZXMiOlsibW9kZWw6OTgzNjciLCJmdW5jdGlvbjo5ODM2NyIsImFwcGxpY2F0aW9uOjMyODMxIl0sInJvbGVzIjpbImppYW5neGlhb3h1YW4wNzIxIl0sInR5cGUiOiJhcHBseSIsImV4cCI6MTc4NDI1NTExOSwibm90ZSI6InRva2VuIiwiaWF0IjoxNzUzMTUxMTE5fQ.z81LJIF4kGa6ZOroPp6KzwmCCGvFBCy1fS1B2vqijKymMOCnnKN3O_tHDmKhUhKb0E1zNOovJ_cF23pzMgoDjg",
        "API_URL": "https://cloudpss.net/"
    }