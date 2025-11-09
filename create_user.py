"""
创建测试用户脚本
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 加载环境变量
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

from app import create_app, db
from models import User

def create_test_user():
    """创建测试用户"""
    app = create_app()
    
    with app.app_context():
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username='user').first()
        
        if existing_user:
            print("=" * 60)
            print("[INFO] 测试用户已存在")
            print("=" * 60)
            print(f"  用户名: {existing_user.username}")
            print(f"  邮箱: {existing_user.email}")
            print(f"  角色: {existing_user.role}")
            print(f"  真实姓名: {existing_user.real_name}")
            print()
            print("  登录信息:")
            print("  用户名: user")
            print("  密码: user123")
            print("=" * 60)
            return
        
        # 创建测试用户
        user = User(
            username='user',
            email='user@hospital.com',
            real_name='测试用户',
            role='user',
            department='测试部门',
            phone='13800138000',
            is_active=True
        )
        user.set_password('user123')  # 默认密码
        
        db.session.add(user)
        db.session.commit()
        
        print("=" * 60)
        print("✅ [SUCCESS] 测试用户创建成功！")
        print("=" * 60)
        print("  用户名: user")
        print("  密码: user123")
        print("  角色: 普通用户 (user)")
        print("  真实姓名: 测试用户")
        print("  邮箱: user@hospital.com")
        print()
        print("💡 [提示] 现在可以使用以下信息登录系统：")
        print("  - 访问: http://localhost:3000")
        print("  - 用户名: user")
        print("  - 密码: user123")
        print("=" * 60)

if __name__ == '__main__':
    try:
        create_test_user()
    except Exception as e:
        print(f"❌ [ERROR] 创建测试用户失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)





