"""
药品管理子系统
Pharmacy Management Subsystem
负责人：开发者3
"""
from flask import Blueprint

pharmacy_bp = Blueprint('pharmacy', __name__, template_folder='../../templates/pharmacy')

from . import routes

