"""
医院综合管理系统 - 服务管理脚本
Hospital Management System - Service Manager
统一管理前后端服务的启动、停止、重启和状态查看
"""
import os
import subprocess
import time
import sys
from pathlib import Path

# 设置Windows控制台UTF-8编码支持（避免emoji显示错误）
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass  # 如果设置失败，继续运行


class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.backend_dir = Path("backend")
        self.frontend_dir = Path("frontend")
        self.pid_file = ".server_pids"
        
    def print_banner(self, title):
        """打印横幅"""
        print("=" * 70)
        print(f"🏥 医院综合管理系统 - {title}")
        print("=" * 70)
        print()
    
    def check_directories(self):
        """检查项目目录"""
        if not self.backend_dir.exists():
            print("❌ 错误: 未找到backend目录")
            return False
        
        if not self.frontend_dir.exists():
            print("❌ 错误: 未找到frontend目录")
            return False
        
        print("✅ 项目目录检查通过")
        return True
    
    def check_mysql(self):
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
    
    def check_port(self, port):
        """检查端口是否被占用"""
        try:
            result = subprocess.run(
                f'netstat -ano | findstr "{port}"',
                shell=True,
                capture_output=True,
                text=True
            )
            return port in result.stdout
        except Exception:
            return False
    
    def get_pid_from_port(self, port):
        """从端口获取进程ID"""
        try:
            result = subprocess.run(
                f'netstat -ano | findstr "{port}"',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                pids = []
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pids.append(parts[-1])
                return pids
        except Exception:
            pass
        return []
    
    def kill_process(self, pid):
        """结束进程"""
        try:
            subprocess.run(
                f'taskkill /F /PID {pid}',
                shell=True,
                capture_output=True
            )
            return True
        except Exception:
            return False
    
    def start_backend(self):
        """启动后端服务"""
        print("[1/2] 正在启动后端服务...")
        
        # 检查并选择Python环境
        # 优先级: conda环境 > venv虚拟环境 > 系统Python
        conda_env_name = "hospital"
        conda_base = "D:\\miniconda3"
        conda_python = Path(conda_base) / "envs" / conda_env_name / "python.exe"
        venv_python = self.backend_dir / "venv" / "Scripts" / "python.exe"
        
        if conda_python.exists():
            # 直接使用conda环境的Python路径（推荐）
            python_cmd = [str(conda_python), "app.py"]
            print(f"    ✅ 使用Conda环境: {conda_env_name}")
            print(f"    📁 Python路径: {conda_python}")
        elif venv_python.exists():
            # 使用venv虚拟环境
            python_cmd = [str(venv_python), "app.py"]
            print("    ✅ 使用venv虚拟环境")
        else:
            # 使用系统Python
            python_cmd = ["python", "app.py"]
            print("    ⚠️  使用系统Python (建议使用conda环境)")
        
        try:
            # 启动后端服务
            backend_process = subprocess.Popen(
                python_cmd,
                cwd=str(self.backend_dir),
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print(f"    ✅ 后端服务已启动 (PID: {backend_process.pid})")
            
            # 等待后端启动
            print("    ⏳ 等待后端启动...")
            time.sleep(5)
            
            # 检查后端是否启动成功
            if self.check_port("5000"):
                print("    ✅ 后端服务启动成功 (http://localhost:5000)")
                return backend_process.pid
            else:
                # 尝试获取错误信息
                print("    ⚠️  后端服务可能未成功启动")
                try:
                    _, stderr = backend_process.communicate(timeout=1)
                    if stderr:
                        error_msg = stderr.decode('utf-8', errors='ignore')
                        print(f"    ❌ 错误信息: {error_msg[:200]}")
                except:
                    pass
                print("    💡 提示: 请检查数据库连接或依赖包安装")
                return backend_process.pid
            
        except Exception as e:
            print(f"    ❌ 后端启动失败: {e}")
            return None
    
    def start_frontend(self):
        """启动前端服务"""
        print("[2/2] 正在启动前端服务...")
        
        # 检查node_modules
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            print("    ⚠️  未找到node_modules，正在安装依赖...")
            print("    ⏳ 这可能需要几分钟，请稍候...")
            result = subprocess.run(
                "npm install",
                shell=True,
                cwd=str(self.frontend_dir),
                capture_output=False
            )
            if result.returncode == 0:
                print("    ✅ 依赖安装完成")
            else:
                print("    ❌ 依赖安装失败")
                return None
        
        try:
            # 启动前端服务
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(self.frontend_dir),
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            print(f"    ✅ 前端服务已启动 (PID: {frontend_process.pid})")
            
            # 等待前端启动
            print("    ⏳ 等待前端启动...")
            time.sleep(8)
            
            # 检查前端是否启动成功
            if self.check_port("3000"):
                print("    ✅ 前端服务启动成功 (http://localhost:3000)")
            else:
                print("    ⚠️  前端服务可能未成功启动")
            
            return frontend_process.pid
            
        except Exception as e:
            print(f"    ❌ 前端启动失败: {e}")
            return None
    
    def start(self):
        """启动所有服务"""
        self.print_banner("启动服务")
        
        # 检查目录
        if not self.check_directories():
            return False
        
        print()
        
        # 检查MySQL
        self.check_mysql()
        print()
        
        # 检查服务是否已经运行
        if self.check_port("5000") or self.check_port("3000"):
            print("⚠️  服务可能已经在运行")
            response = input("是否要停止现有服务并重新启动？(y/n): ")
            if response.lower() == 'y':
                self.stop()
                print()
            else:
                return False
        
        print("=" * 70)
        print("🚀 正在启动服务...")
        print("=" * 70)
        print()
        
        # 启动后端
        backend_pid = self.start_backend()
        if not backend_pid:
            print("\n❌ 后端启动失败，停止启动流程")
            return False
        
        print()
        
        # 启动前端
        frontend_pid = self.start_frontend()
        if not frontend_pid:
            print("\n❌ 前端启动失败，停止后端服务")
            self.kill_process(backend_pid)
            return False
        
        # 保存进程ID到文件
        with open(self.pid_file, 'w', encoding='utf-8') as f:
            f.write(f"{backend_pid}\n")
            f.write(f"{frontend_pid}\n")
        
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
        print(f"   - 后端进程 PID: {backend_pid}")
        print(f"   - 前端进程 PID: {frontend_pid}")
        print("   - 服务已在后台运行")
        print()
        print("🛑 停止服务:")
        print("   - 运行 'python manage.py stop' 停止所有服务")
        print("   - 运行 'python manage.py restart' 重启所有服务")
        print("   - 运行 'python manage.py status' 查看服务状态")
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
        
        return True
    
    def stop(self):
        """停止所有服务"""
        self.print_banner("停止服务")
        
        stopped = False
        
        # 方法1: 从PID文件读取并停止
        if Path(self.pid_file).exists():
            print("📝 从PID文件读取进程信息...")
            try:
                with open(self.pid_file, 'r', encoding='utf-8') as f:
                    pids = f.readlines()
                
                for pid in pids:
                    pid = pid.strip()
                    if pid:
                        print(f"   停止进程 {pid}...")
                        self.kill_process(pid)
                
                # 删除PID文件
                Path(self.pid_file).unlink()
                print("   ✅ 进程已停止")
                stopped = True
            except Exception as e:
                print(f"   ⚠️  停止进程失败: {e}")
        
        # 方法2: 根据端口停止
        print()
        print("🔍 检查并停止占用端口的进程...")
        
        # 停止5000端口（后端）
        backend_pids = self.get_pid_from_port("5000")
        if backend_pids:
            for pid in backend_pids:
                print(f"   停止后端进程 (PID: {pid})...")
                self.kill_process(pid)
            print("   ✅ 后端服务已停止")
            stopped = True
        else:
            print("   ℹ️  后端服务未运行")
        
        # 停止3000端口（前端）
        frontend_pids = self.get_pid_from_port("3000")
        if frontend_pids:
            for pid in frontend_pids:
                print(f"   停止前端进程 (PID: {pid})...")
                self.kill_process(pid)
            print("   ✅ 前端服务已停止")
            stopped = True
        else:
            print("   ℹ️  前端服务未运行")
        
        print()
        print("=" * 70)
        if stopped:
            print("✅ 所有服务已停止")
        else:
            print("ℹ️  没有发现运行中的服务")
        print("=" * 70)
        print()
        
        return True
    
    def restart(self):
        """重启所有服务"""
        self.print_banner("重启服务")
        print("正在停止现有服务...")
        print()
        self.stop()
        print()
        print("正在启动服务...")
        print()
        return self.start()
    
    def status(self):
        """查看服务状态"""
        self.print_banner("服务状态")
        
        # 检查后端状态
        print("🔍 检查后端服务状态...")
        backend_running = self.check_port("5000")
        if backend_running:
            backend_pids = self.get_pid_from_port("5000")
            print(f"   ✅ 后端服务正在运行")
            print(f"   📍 地址: http://localhost:5000")
            print(f"   🆔 PID: {', '.join(backend_pids)}")
        else:
            print("   ❌ 后端服务未运行")
        
        print()
        
        # 检查前端状态
        print("🔍 检查前端服务状态...")
        frontend_running = self.check_port("3000")
        if frontend_running:
            frontend_pids = self.get_pid_from_port("3000")
            print(f"   ✅ 前端服务正在运行")
            print(f"   📍 地址: http://localhost:3000")
            print(f"   🆔 PID: {', '.join(frontend_pids)}")
        else:
            print("   ❌ 前端服务未运行")
        
        print()
        
        # 检查MySQL
        self.check_mysql()
        
        print()
        print("=" * 70)
        if backend_running and frontend_running:
            print("✅ 所有服务运行正常")
        elif backend_running or frontend_running:
            print("⚠️  部分服务正在运行")
        else:
            print("❌ 所有服务均未运行")
        print("=" * 70)
        print()
        
        return True
    
    def diagnose(self):
        """诊断系统环境"""
        self.print_banner("环境诊断")
        
        print("🔍 检查Python环境...")
        
        # 检查conda环境
        conda_env_name = "hospital"
        conda_base = "D:\\miniconda3"
        conda_python = Path(conda_base) / "envs" / conda_env_name / "python.exe"
        
        if conda_python.exists():
            print(f"   ✅ Conda环境存在: {conda_env_name}")
            print(f"   📁 路径: {conda_python}")
            
            # 测试conda环境中的Flask（直接使用Python路径）
            try:
                result = subprocess.run(
                    [str(conda_python), "-c", "import flask; import importlib.metadata; print(importlib.metadata.version('flask'))"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    flask_version = result.stdout.strip()
                    print(f"   ✅ Flask已安装: v{flask_version}")
                else:
                    print(f"   ❌ Flask未安装或无法导入")
                    print(f"   💡 请在conda环境中运行: pip install -r backend/requirements.txt")
            except Exception as e:
                print(f"   ⚠️  无法检查Flask: {e}")
        else:
            print(f"   ❌ Conda环境不存在: {conda_env_name}")
            print(f"   💡 请创建环境: conda create -n {conda_env_name} python=3.8")
        
        print()
        
        # 检查venv虚拟环境
        venv_python = self.backend_dir / "venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            print(f"   ✅ venv虚拟环境存在")
            print(f"   📁 路径: {venv_python}")
        else:
            print(f"   ℹ️  venv虚拟环境不存在")
        
        print()
        print("=" * 70)
        print("🔍 检查数据库...")
        self.check_mysql()
        
        print()
        print("=" * 70)
        print("🔍 检查Node.js环境...")
        try:
            result = subprocess.run(
                "node --version",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"   ✅ Node.js已安装: {node_version}")
            else:
                print("   ❌ Node.js未安装")
        except:
            print("   ❌ Node.js未安装")
        
        try:
            result = subprocess.run(
                "npm --version",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                print(f"   ✅ npm已安装: v{npm_version}")
            else:
                print("   ❌ npm未安装")
        except:
            print("   ❌ npm未安装")
        
        # 检查前端依赖
        node_modules = self.frontend_dir / "node_modules"
        if node_modules.exists():
            print(f"   ✅ 前端依赖已安装")
        else:
            print(f"   ⚠️  前端依赖未安装")
            print(f"   💡 请运行: cd frontend && npm install")
        
        print()
        print("=" * 70)
        print("📋 诊断完成")
        print("=" * 70)
        print()
        
        return True


def print_usage():
    """打印使用说明"""
    print("=" * 70)
    print("🏥 医院综合管理系统 - 服务管理工具")
    print("=" * 70)
    print()
    print("用法: python manage.py [命令]")
    print()
    print("可用命令:")
    print("  start    - 启动所有服务（前端 + 后端）")
    print("  stop     - 停止所有服务")
    print("  restart  - 重启所有服务")
    print("  status   - 查看服务运行状态")
    print("  diagnose - 诊断系统环境（检查Python、数据库、Node.js等）")
    print("  help     - 显示此帮助信息")
    print()
    print("示例:")
    print("  python manage.py start      # 启动服务")
    print("  python manage.py stop       # 停止服务")
    print("  python manage.py restart    # 重启服务")
    print("  python manage.py status     # 查看状态")
    print("  python manage.py diagnose   # 诊断环境")
    print()
    print("=" * 70)


def main():
    """主函数"""
    try:
        # 获取命令行参数
        if len(sys.argv) < 2:
            # 默认启动服务
            command = "start"
        else:
            command = sys.argv[1].lower()
        
        # 创建服务管理器
        manager = ServiceManager()
        
        # 执行命令
        if command == "start":
            success = manager.start()
            if success:
                try:
                    print("\n💡 提示: 按回车键将停止所有服务并退出...")
                    input()
                    print("\n正在停止所有服务...")
                    manager.stop()
                    print("✅ 服务已停止，再见！")
                except (KeyboardInterrupt, EOFError):
                    print("\n正在停止所有服务...")
                    manager.stop()
                    print("✅ 服务已停止，再见！")
        elif command == "stop":
            manager.stop()
            try:
                input("\n按回车键退出...")
            except (KeyboardInterrupt, EOFError):
                print("\n")
        elif command == "restart":
            manager.restart()
            try:
                input("\n按回车键关闭此窗口（服务将继续在后台运行）...")
            except (KeyboardInterrupt, EOFError):
                print("\n")
        elif command == "status":
            manager.status()
            try:
                input("\n按回车键退出...")
            except (KeyboardInterrupt, EOFError):
                print("\n")
        elif command == "diagnose":
            manager.diagnose()
            try:
                input("\n按回车键退出...")
            except (KeyboardInterrupt, EOFError):
                print("\n")
        elif command in ["help", "-h", "--help"]:
            print_usage()
            try:
                input("\n按回车键退出...")
            except (KeyboardInterrupt, EOFError):
                print("\n")
        else:
            print(f"❌ 未知命令: {command}")
            print()
            print_usage()
            try:
                input("\n按回车键退出...")
            except (KeyboardInterrupt, EOFError):
                print("\n")
    except KeyboardInterrupt:
        print("\n")
        print("⚠️  操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

