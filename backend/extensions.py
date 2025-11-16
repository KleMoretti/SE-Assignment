"""
扩展对象
Flask Extensions
用于避免循环导入问题
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# 创建扩展对象（但不初始化应用）
db = SQLAlchemy()
jwt = JWTManager()

