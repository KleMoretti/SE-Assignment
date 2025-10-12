"""
病人管理子系统
Patient Management Subsystem
负责人：开发者1
"""
from flask import Blueprint

patient_bp = Blueprint('patient', __name__, template_folder='../../templates/patient')

from . import routes

