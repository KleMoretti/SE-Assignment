"""
医生管理子系统
Doctor Management Subsystem
负责人：开发者2
"""
from flask import Blueprint

doctor_bp = Blueprint('doctor', __name__, template_folder='../../templates/doctor')

from . import routes

