"""
病人管理子系统
Patient Management Module
"""
from flask import Blueprint

# 创建蓝图（url_prefix 在 app.py 中统一设置）
patient_bp = Blueprint('patient', __name__, template_folder='../../templates/patient')

# 导入路由（会自动加载所有服务模块）
from . import routes
