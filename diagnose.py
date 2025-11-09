"""
医院综合管理系统 - 诊断工具
Hospital Management System - Diagnostic Tool
检查系统配置和服务状态
"""
import subprocess
import socket
import sys
from pathlib import Path


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"📋 {title}")
    print("=" * 70)


def check_port_listening(port):
    """检查端口是否在监听"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"',
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return f"检查失败: {e}"


def check_port_accessible(host, port):
    """检查端口是否可访问"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False


def check_mysql():
    """检查MySQL"""
    print_section("MySQL数据库检查")
    result = check_port_listening(3306)
    if "3306" in result:
        print("✅ MySQL正在运行")
        print(result)
    else:
        print("❌ MySQL未运行")
        print("💡 请先启动MySQL数据库")


def check_backend():
    """检查后端服务"""
    print_section("后端服务检查 (端口5000)")
    
    # 检查端口监听
    result = check_port_listening(5000)
    if "5000" in result:
        print("✅ 端口5000正在监听")
        print(result)
        print()
        
        # 检查各种访问方式
        print("🔍 测试访问方式:")
        
        hosts_to_test = [
            ('localhost', 5000, 'http://localhost:5000'),
            ('127.0.0.1', 5000, 'http://127.0.0.1:5000'),
            ('0.0.0.0', 5000, 'http://0.0.0.0:5000'),
        ]
        
        accessible_hosts = []
        for host, port, url in hosts_to_test:
            accessible = check_port_accessible(host, port)
            status = "✅ 可访问" if accessible else "❌ 不可访问"
            print(f"   {status} - {url}")
            if accessible:
                accessible_hosts.append(url)
        
        if accessible_hosts:
            print()
            print("💡 推荐使用以下地址访问:")
            for url in accessible_hosts:
                print(f"   {url}")
        else:
            print()
            print("⚠️  警告: 端口在监听但无法访问")
            print("💡 可能的原因:")
            print("   1. 防火墙阻止了访问")
            print("   2. 服务绑定到了特定的网络接口")
            print("   3. 服务启动失败但进程仍在运行")
    else:
        print("❌ 端口5000未监听")
        print("💡 后端服务未启动或启动失败")


def check_frontend():
    """检查前端服务"""
    print_section("前端服务检查 (端口3000)")
    
    # 检查端口监听
    result = check_port_listening(3000)
    if "3000" in result:
        print("✅ 端口3000正在监听")
        print(result)
        print()
        
        # 检查各种访问方式
        print("🔍 测试访问方式:")
        
        hosts_to_test = [
            ('localhost', 3000, 'http://localhost:3000'),
            ('127.0.0.1', 3000, 'http://127.0.0.1:3000'),
            ('0.0.0.0', 3000, 'http://0.0.0.0:3000'),
        ]
        
        accessible_hosts = []
        for host, port, url in hosts_to_test:
            accessible = check_port_accessible(host, port)
            status = "✅ 可访问" if accessible else "❌ 不可访问"
            print(f"   {status} - {url}")
            if accessible:
                accessible_hosts.append(url)
        
        if accessible_hosts:
            print()
            print("💡 推荐使用以下地址访问:")
            for url in accessible_hosts:
                print(f"   {url}")
        else:
            print()
            print("⚠️  警告: 端口在监听但无法访问")
            print("💡 可能的原因:")
            print("   1. 防火墙阻止了访问")
            print("   2. Vite配置问题 (host设置)")
            print("   3. 服务启动失败但进程仍在运行")
    else:
        print("❌ 端口3000未监听")
        print("💡 前端服务未启动或启动失败")


def check_files():
    """检查关键文件"""
    print_section("项目文件检查")
    
    files_to_check = [
        ("backend/app.py", "后端入口文件"),
        ("backend/config.py", "后端配置文件"),
        ("backend/requirements.txt", "后端依赖文件"),
        ("frontend/package.json", "前端配置文件"),
        ("frontend/vite.config.js", "Vite配置文件"),
        ("frontend/src/main.js", "前端入口文件"),
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        exists = Path(file_path).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {description}: {file_path}")
        if not exists:
            all_exist = False
    
    if all_exist:
        print("\n✅ 所有关键文件都存在")
    else:
        print("\n❌ 部分关键文件缺失")


def check_processes():
    """检查Python和Node进程"""
    print_section("进程检查")
    
    try:
        # 检查Python进程
        python_result = subprocess.run(
            'tasklist | findstr "python"',
            shell=True,
            capture_output=True,
            text=True
        )
        if python_result.stdout:
            print("✅ Python进程:")
            print(python_result.stdout)
        else:
            print("❌ 未找到Python进程")
        
        print()
        
        # 检查Node进程
        node_result = subprocess.run(
            'tasklist | findstr "node"',
            shell=True,
            capture_output=True,
            text=True
        )
        if node_result.stdout:
            print("✅ Node.js进程:")
            print(node_result.stdout)
        else:
            print("❌ 未找到Node.js进程")
    except Exception as e:
        print(f"检查失败: {e}")


def show_solutions():
    """显示解决方案"""
    print_section("常见问题解决方案")
    
    print("""
1️⃣  如果端口在监听但无法访问:
   - 检查Windows防火墙设置
   - 运行: netsh advfirewall firewall add rule name="Allow Port 3000" dir=in action=allow protocol=TCP localport=3000
   - 运行: netsh advfirewall firewall add rule name="Allow Port 5000" dir=in action=allow protocol=TCP localport=5000

2️⃣  如果服务未启动:
   - 检查是否有错误日志
   - 确保MySQL数据库正在运行
   - 确保所有依赖都已安装

3️⃣  如果前端无法访问后端:
   - 检查 frontend/vite.config.js 中的proxy配置
   - 检查 backend/app.py 中的CORS配置
   - 确保后端在前端之前启动

4️⃣  如果端口被占用:
   - 运行: python manage.py stop
   - 或手动结束相关进程

5️⃣  重新配置并启动:
   - 运行: python fix_config.py  (修复配置)
   - 运行: python manage.py restart  (重启服务)
""")


def main():
    """主函数"""
    print("=" * 70)
    print("🏥 医院综合管理系统 - 诊断工具")
    print("=" * 70)
    
    check_files()
    check_mysql()
    check_backend()
    check_frontend()
    check_processes()
    show_solutions()
    
    print("\n" + "=" * 70)
    print("✅ 诊断完成")
    print("=" * 70)
    print()
    input("按回车键退出...")


if __name__ == "__main__":
    main()



