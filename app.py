"""
医院综合管理系统 - 主应用入口
Hospital Management System - Main Application Entry
"""
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config

# 初始化数据库对象
db = SQLAlchemy()


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    
    # 注册蓝图 - 三个子系统
    from modules.patient import patient_bp
    from modules.doctor import doctor_bp
    from modules.pharmacy import pharmacy_bp
    
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(pharmacy_bp, url_prefix='/pharmacy')
    
    # 首页路由
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("医院综合管理系统已启动")
    print("系统模块：")
    print("  - 病人管理系统: http://localhost:5000/patient")
    print("  - 医生管理系统: http://localhost:5000/doctor")
    print("  - 药品管理系统: http://localhost:5000/pharmacy")
    print("=" * 60)
    app.run(debug=True)

