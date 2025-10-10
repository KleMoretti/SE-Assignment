"""
配置文件
Configuration File
"""
import os


class Config:
    """基础配置类"""
    # 安全密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hospital-management-system-key-2024'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///hospital.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 分页配置
    ITEMS_PER_PAGE = 10
    
    # 系统配置
    SYSTEM_NAME = '医院综合管理系统'
    SYSTEM_VERSION = '1.0.0'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

