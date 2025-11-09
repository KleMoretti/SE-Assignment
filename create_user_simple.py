"""
简单创建测试用户 - 直接通过API
"""
import requests
import json

def create_user_via_api():
    """通过API创建用户"""
    api_url = "http://localhost:5000/api/auth/register"
    
    user_data = {
        "username": "user",
        "password": "user123",
        "email": "user@hospital.com",
        "real_name": "测试用户",
        "role": "user",
        "department": "测试部门",
        "phone": "13800138000"
    }
    
    try:
        print("=" * 60)
        print("正在创建测试用户...")
        print("=" * 60)
        
        response = requests.post(api_url, json=user_data, timeout=10)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print()
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
        else:
            print()
            print(f"⚠️  注册失败: {result.get('message', '未知错误')}")
            print()
            if "已存在" in result.get('message', ''):
                print("=" * 60)
                print("ℹ️  [INFO] 用户已存在，可以直接登录")
                print("=" * 60)
                print("  用户名: user")
                print("  密码: user123")
                print()
                print("  访问: http://localhost:3000")
                print("=" * 60)
    
    except requests.exceptions.ConnectionError:
        print()
        print("❌ [ERROR] 无法连接到后端服务")
        print("   请确保后端服务正在运行 (http://localhost:5000)")
        print()
        print("   启动后端: python manage.py start")
    except Exception as e:
        print()
        print(f"❌ [ERROR] 创建用户失败: {e}")

if __name__ == '__main__':
    create_user_via_api()





