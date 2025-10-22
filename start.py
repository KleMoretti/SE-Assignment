"""
医院综合管理系统 - Windows一键启动脚本
Hospital Management System - Windows Startup Script
同时启动前端和后端服务（后台运行）
"""
import os
import subprocess
import time
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("=" * 70)
    print("🏥 医院综合管理系统 - 一键启动")
    print("=" * 70)
    print()

def check_mysql():
    """检查MySQL是否运行"""
    print("🔍 检查MySQL数据库...")
    try:
        result = subprocess.run(
            'netstat -ano | findstr "3306"',
            shell=True,
            capture_output=True,
            text=True
        )
        if "3306" in result.stdout:
            print("    ✅ MySQL数据库正在运行")
            return True
        else:
            print("    ⚠️  警告: MySQL数据库未运行")
            print("    💡 后端可能无法连接数据库")
            return True  # 继续启动，让用户看到具体错误
    except Exception:
        return True

def main():
    """主函数"""
    print_banner()
    
    # 使用相对路径
    backend_dir = Path("backend")
    frontend_dir = Path("frontend")
    
    # 检查目录
    if not backend_dir.exists():
        print("❌ 错误: 未找到backend目录")
        input("按回车键退出...")
        return
    
    if not frontend_dir.exists():
        print("❌ 错误: 未找到frontend目录")
        input("按回车键退出...")
        return
    
    print("✅ 项目目录检查通过")
    print()
    
    # 检查MySQL
    check_mysql()
    print()
    
    print("=" * 70)
    print("🚀 正在启动服务...")
    print("=" * 70)
    print()
    
    # 启动后端
    print("[1/2] 正在启动后端服务...")
    
    # 检查虚拟环境（使用相对路径）
    venv_python = Path("backend/venv/Scripts/python.exe")
    if venv_python.exists():
        python_cmd = "backend\\venv\\Scripts\\python.exe"
        print("    ✅ 使用虚拟环境")
    else:
        python_cmd = "python"
        print("    ⚠️  使用系统Python")
    
    # 使用相对路径
    app_py = "app.py"
    
    try:
        # 使用CREATE_NO_WINDOW标志在后台启动（相对路径）
        backend_process = subprocess.Popen(
            [python_cmd, app_py],
            cwd="backend",
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"    ✅ 后端服务已启动 (PID: {backend_process.pid})")
    except Exception as e:
        print(f"    ❌ 后端启动失败: {e}")
        input("按回车键退出...")
        return
    
    # 等待后端启动
    print("    ⏳ 等待后端启动...")
    time.sleep(5)
    
    # 检查后端是否启动成功
    result = subprocess.run(
        'netstat -ano | findstr "5000"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if "5000" in result.stdout:
        print("    ✅ 后端服务启动成功 (http://localhost:5000)")
    else:
        print("    ⚠️  后端服务可能未成功启动")
        print("    💡 提示: 可能是数据库连接问题")
    
    # 启动前端
    print()
    print("[2/2] 正在启动前端服务...")
    
    # 检查node_modules（相对路径）
    node_modules = Path("frontend/node_modules")
    if not node_modules.exists():
        print("    ⚠️  未找到node_modules，正在安装依赖...")
        print("    ⏳ 这可能需要几分钟，请稍候...")
        result = subprocess.run(
            "npm install",
            shell=True,
            cwd="frontend",
            capture_output=False
        )
        if result.returncode == 0:
            print("    ✅ 依赖安装完成")
        else:
            print("    ❌ 依赖安装失败")
            input("按回车键退出...")
            return
    
    try:
        # 在后台启动前端（相对路径）
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="frontend",
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        print(f"    ✅ 前端服务已启动 (PID: {frontend_process.pid})")
    except Exception as e:
        print(f"    ❌ 前端启动失败: {e}")
        input("按回车键退出...")
        return
    
    # 等待前端启动
    print("    ⏳ 等待前端启动...")
    time.sleep(8)
    
    # 检查前端是否启动成功
    result = subprocess.run(
        'netstat -ano | findstr "3000"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if "3000" in result.stdout:
        print("    ✅ 前端服务启动成功 (http://localhost:3000)")
    else:
        print("    ⚠️  前端服务可能未成功启动")
    
    # 保存进程ID到文件，方便后续关闭（相对路径）
    pid_file = ".server_pids"
    with open(pid_file, 'w', encoding='utf-8') as f:
        f.write(f"{backend_process.pid}\n")
        f.write(f"{frontend_process.pid}\n")
    
    print()
    print("=" * 70)
    print("🎉 系统启动完成！")
    print("=" * 70)
    print()
    print("📋 访问地址:")
    print("   🔹 前端应用: http://localhost:3000")
    print("   🔹 后端API:  http://localhost:5000")
    print()
    print("💡 服务信息:")
    print(f"   - 后端进程 PID: {backend_process.pid}")
    print(f"   - 前端进程 PID: {frontend_process.pid}")
    print("   - 服务已在后台运行")
    print()
    print("🛑 停止服务:")
    print("   - 运行 stop.py 脚本停止所有服务")
    print("   - 或使用任务管理器手动结束进程")
    print()
    print("=" * 70)
    print()
    
    # 自动打开浏览器（可选）
    try:
        import webbrowser
        time.sleep(2)
        print("🌐 正在打开浏览器...")
        webbrowser.open('http://localhost:3000')
    except:
        pass
    
    print()
    input("按回车键关闭此窗口（服务将继续在后台运行）...")

if __name__ == "__main__":
    main()
