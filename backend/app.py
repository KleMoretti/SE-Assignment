"""
医院综合管理系统 - 主应用入口
Hospital Management System - Main Application Entry
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 设置Windows控制台UTF-8编码支持
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass  # 如果设置失败，继续运行

# 加载环境变量（必须在导入config之前）
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print("[INFO] 已加载环境变量文件: {}".format(env_path))
else:
    print("[WARN] 未找到.env文件: {}".format(env_path))

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.extensions import db, jwt


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    print('>>> [create_app] Flask app created:', app.name)  # 加这一行
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    
    # 配置CORS - 允许Vue前端跨域访问
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],  # Vue开发服务器
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # 注册蓝图 - 认证 + 三个子系统（API路由）
    from backend.modules.auth import auth_bp
    from backend.modules.patient import patient_bp
    from backend.modules.doctor import doctor_bp
    from backend.modules.pharmacy import pharmacy_bp
    
    # API路由前缀
    app.register_blueprint(auth_bp, url_prefix='/api/auth')  # 认证路由
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(pharmacy_bp, url_prefix='/api/pharmacy')
    
    # 健康检查路由
    @app.route('/')
    @app.route('/health')
    def health_check():
        """API健康检查"""
        return jsonify({
            'status': 'success',
            'message': '医院综合管理系统API运行正常',
            'version': app.config['SYSTEM_VERSION']
        })
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': '请求的资源不存在',
            'code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'code': 'INTERNAL_ERROR'
        }), 500
    
    # 创建数据库表
    with app.app_context():
        try:
            db.create_all()
            print("[INFO] 数据库表创建成功")
        except Exception as e:
            print(f"[WARN] 数据库表创建失败: {e}")
            print("[WARN] 如果遇到外键类型不兼容错误，请运行: python reset_database.py")
            # 不抛出异常，允许应用继续运行（假设表已存在）

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 70)
    print("🏥 医院综合管理系统 API 已启动")
    print("=" * 70)
    print("📋 系统信息:")
    print(f"   - 版本: {app.config['SYSTEM_VERSION']}")
    print(f"   - 数据库: MySQL")
    print(f"   - 模式: 前后端分离架构")
    print()
    print("🔗 API模块:")
    print("   - 病人管理API: http://localhost:5000/api/patient")
    print("   - 医生管理API: http://localhost:5000/api/doctor")
    print("   - 药品管理API: http://localhost:5000/api/pharmacy")
    print()
    print("💡 提示:")
    print("   - 前端Vue项目请运行: npm run dev")
    print("   - API文档地址: http://localhost:5000/")
    print("   - 确保MySQL数据库已启动")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5000)

