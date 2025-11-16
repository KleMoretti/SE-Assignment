"""
重建数据库表 - 删除现有表并重新创建
Reset Database Tables - Drop existing tables and recreate
警告：此操作将删除所有数据！
"""
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[INFO] 已加载环境变量文件: {env_path}")

# noinspection PyUnresolvedReferences
from app import create_app
# noinspection PyUnresolvedReferences
from extensions import db

def reset_database(auto_confirm=False):
    """重建数据库"""
    print("=" * 70)
    print("🔄 重建数据库表")
    print("=" * 70)
    print()
    print("⚠️  警告: 此操作将删除所有现有数据!")
    print()

    if not auto_confirm:
        response = input("确认要继续吗? (输入 yes 确认): ")
        if response.lower() != 'yes':
            print("操作已取消")
            return
    else:
        print("自动确认模式: 继续...")

    print()
    print("正在创建应用...")
    app = create_app()

    with app.app_context():
        print("正在删除所有表...")
        db.drop_all()
        print("✅ 所有表已删除")

        print()
        print("正在创建新表...")
        db.create_all()
        print("✅ 所有表已创建")

        print()
        print("=" * 70)
        print("✅ 数据库重建完成!")
        print("=" * 70)
        print()
        print("💡 提示: 现在可以创建管理员账号")
        print("   运行: python create_admin.py")
        print()

if __name__ == '__main__':
    try:
        # 检查是否有 --yes 参数
        auto_confirm = '--yes' in sys.argv or '-y' in sys.argv
        reset_database(auto_confirm)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")

