"""
认证模块
Authentication Module
"""
from flask import Blueprint

# 创建蓝图（url_prefix 在 app.py 中统一设置）
# 认证模块通常不需要 template_folder，因为主要提供 API
auth_bp = Blueprint('auth', __name__)

from . import routes
