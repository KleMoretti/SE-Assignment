"""
配置文件
Configuration File
"""
import os
from datetime import timedelta


class Config:
    """基础配置类"""
    # 安全密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hospital-management-system-key-2024'
    
    # MySQL数据库配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'hospital_db')
    
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS配置
    CORS_HEADERS = 'Content-Type'
    
    # 分页配置
    ITEMS_PER_PAGE = 10
    MAX_PAGE_SIZE = 100
    
    # 系统配置
    SYSTEM_NAME = '医院综合管理系统'
    SYSTEM_VERSION = '2.0.0'
    
    # API配置
    JSON_AS_ASCII = False  # 支持中文JSON
    RESTFUL_JSON = {
        'ensure_ascii': False
    }


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 开发环境可以使用SQLite（可选）
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///hospital.db'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 生产环境必须使用环境变量配置数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

