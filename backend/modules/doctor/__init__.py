"""
医生管理子系统
Doctor Management Subsystem
负责人：开发者2
"""
from flask import Blueprint

# 创建蓝图（url_prefix 在 app.py 中统一设置）
doctor_bp = Blueprint('doctor', __name__, template_folder='../../templates/doctor')

from . import routes
