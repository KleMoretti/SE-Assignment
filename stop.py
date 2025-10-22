"""
医院综合管理系统 - Windows停止脚本
Hospital Management System - Stop Script
停止所有后台运行的服务
"""
import subprocess
from pathlib import Path

def main():
    """主函数"""
    print("=" * 70)
    print("🛑 医院综合管理系统 - 停止服务")
    print("=" * 70)
    print()
    
    # 使用相对路径
    pid_file = ".server_pids"
    
    # 方法1: 从PID文件读取并停止
    if Path(pid_file).exists():
        print("📝 从PID文件读取进程信息...")
        try:
            with open(pid_file, 'r', encoding='utf-8') as f:
                pids = f.readlines()
            
            for pid in pids:
                pid = pid.strip()
                if pid:
                    print(f"   停止进程 {pid}...")
                    subprocess.run(
                        f'taskkill /F /PID {pid}',
                        shell=True,
                        capture_output=True
                    )
            
            # 删除PID文件
            Path(pid_file).unlink()
            print("   ✅ 进程已停止")
        except Exception as e:
            print(f"   ⚠️  停止进程失败: {e}")
    
    # 方法2: 根据端口停止
    print()
    print("🔍 检查并停止占用端口的进程...")
    
    # 停止5000端口（后端）
    result = subprocess.run(
        'netstat -ano | findstr "5000"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                print(f"   停止后端进程 (PID: {pid})...")
                subprocess.run(
                    f'taskkill /F /PID {pid}',
                    shell=True,
                    capture_output=True
                )
        print("   ✅ 后端服务已停止")
    else:
        print("   ℹ️  后端服务未运行")
    
    # 停止3000端口（前端）
    result = subprocess.run(
        'netstat -ano | findstr "3000"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                print(f"   停止前端进程 (PID: {pid})...")
                subprocess.run(
                    f'taskkill /F /PID {pid}',
                    shell=True,
                    capture_output=True
                )
        print("   ✅ 前端服务已停止")
    else:
        print("   ℹ️  前端服务未运行")
    
    print()
    print("=" * 70)
    print("✅ 所有服务已停止")
    print("=" * 70)
    print()
    input("按回车键退出...")

if __name__ == "__main__":
    main()

