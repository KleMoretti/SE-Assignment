"""
创建管理员账号脚本
"""
import sys
import os

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# 加载环境变量
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 导入必要的模块
# noinspection PyUnresolvedReferences
from app import create_app
# noinspection PyUnresolvedReferences
from extensions import db
# noinspection PyUnresolvedReferences
from models import User

def create_admin_user():
    """创建管理员用户"""
    app = create_app()
    
    with app.app_context():
        # 检查管理员是否已存在
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print("[INFO] 管理员账号已存在")
            print(f"  用户名: {admin.username}")
            print(f"  邮箱: {admin.email}")
            print(f"  角色: {admin.role}")
            return
        
        # 创建管理员账号
        admin = User(
            username='admin',
            email='admin@hospital.com',
            real_name='系统管理员',
            role='admin',
            department='管理部门',
            is_active=True
        )
        admin.set_password('admin123')  # 默认密码
        
        db.session.add(admin)
        db.session.commit()
        
        print("=" * 60)
        print("[SUCCESS] 管理员账号创建成功！")
        print("=" * 60)
        print("  用户名: admin")
        print("  密码: admin123")
        print("  角色: 管理员")
        print()
        print("[IMPORTANT] 请登录后立即修改密码！")
        print("=" * 60)

if __name__ == '__main__':
    try:
        create_admin_user()
    except Exception as e:
        print(f"[ERROR] 创建管理员账号失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


