# 医院综合管理系统 - 安装配置指南

> 📚 **本指南提供完整的环境配置和安装步骤**  
> 版本: v2.0.0 | 更新日期: 2025-10-11

---

## 📋 目录

- [技术栈版本要求](#技术栈版本要求)
- [快速开始（5分钟）](#快速开始5分钟)
- [详细安装步骤](#详细安装步骤)
  - [1. 环境准备](#1-环境准备)
  - [2. 后端配置](#2-后端配置)
  - [3. 前端配置](#3-前端配置)
  - [4. 数据库配置](#4-数据库配置)
- [验证安装](#验证安装)
- [常见问题](#常见问题)
- [生产环境部署](#生产环境部署)

---

## 技术栈版本要求

### 必备软件

| 软件 | 最低版本 | 推荐版本 | 下载地址 |
|------|---------|---------|---------|
| Python | 3.8+ | 3.11+ | [python.org](https://www.python.org/downloads/) |
| MySQL | 8.0+ | 8.0.35+ | [mysql.com](https://dev.mysql.com/downloads/mysql/) |
| Node.js | 16+ | 18 LTS | [nodejs.org](https://nodejs.org/) |
| Git | 2.0+ | 最新版 | [git-scm.com](https://git-scm.com/) |

### 版本验证

安装完成后，请验证版本：

```bash
# 验证Python
python --version
# 应输出: Python 3.8.0 或更高版本

# 验证MySQL
mysql --version
# 应输出: mysql Ver 8.0.x 或更高版本

# 验证Node.js和npm
node --version    # 应输出: v16.0.0 或更高版本
npm --version     # 应输出: 8.0.0 或更高版本

# 验证Git
git --version     # 应输出: git version 2.x.x
```

---

## 快速开始（5分钟）

### 🚀 超快速安装（适合有经验的开发者）

```bash
# 1. 克隆项目
git clone <repository-url>
cd hospital-management-system

# 2. 安装后端依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp env.template .env
# 编辑.env文件，配置MySQL连接信息

# 4. 初始化数据库
mysql -u root -p < init_database.sql
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# 5. 启动后端服务
python app.py

# 6. 启动前端（可选，新终端）
cd frontend
npm install
npm run dev
```

**访问系统:**
- 后端API: http://localhost:5000/
- 前端应用: http://localhost:5173/

---

## 详细安装步骤

### 1. 环境准备

#### 1.1 安装Python 3.8+

**Windows:**
1. 访问 https://www.python.org/downloads/
2. 下载Python 3.11 安装包
3. 运行安装程序，**勾选"Add Python to PATH"**
4. 点击"Install Now"

**macOS:**
```bash
# 使用Homebrew安装
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

#### 1.2 安装MySQL 8.0+

**Windows:**
1. 访问 https://dev.mysql.com/downloads/mysql/
2. 下载MySQL Installer
3. 运行安装程序，选择"Developer Default"
4. 设置root密码（请记住此密码）

**macOS:**
```bash
# 使用Homebrew安装
brew install mysql@8.0
brew services start mysql@8.0
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**启动MySQL服务:**
```bash
# Windows
net start MySQL80

# macOS
brew services start mysql

# Linux
sudo systemctl start mysql
```

#### 1.3 安装Node.js 16+（前端开发需要）

**Windows/macOS:**
1. 访问 https://nodejs.org/
2. 下载LTS版本（推荐18.x）
3. 运行安装程序

**Linux:**
```bash
# 使用NodeSource仓库
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

---

### 2. 后端配置

#### 2.1 克隆项目

```bash
# 使用Git克隆
git clone <repository-url>
cd hospital-management-system

# 或者直接下载ZIP并解压
```

#### 2.2 创建Python虚拟环境

**为什么使用虚拟环境？**
- 隔离项目依赖
- 避免版本冲突
- 便于管理

**创建虚拟环境:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**激活成功后，命令行前会显示 `(venv)`**

#### 2.3 安装Python依赖

```bash
pip install -r requirements.txt
```

**依赖包列表:**
```txt
Flask==3.0.0                    # Web框架
Flask-SQLAlchemy==3.1.1         # ORM
Flask-CORS==4.0.0               # CORS支持
Flask-RESTful==0.3.10           # REST API
Flask-JWT-Extended==4.5.3       # JWT认证
Flask-Migrate==4.0.5            # 数据库迁移
PyMySQL==1.1.0                  # MySQL驱动
python-dotenv==1.0.0            # 环境变量管理
marshmallow==3.20.1             # 数据验证
Werkzeug==3.0.1                 # WSGI工具库
```

**常见安装问题:**

**问题1: mysqlclient安装失败**
```bash
# 解决方案：只使用PyMySQL
# 编辑requirements.txt，注释掉mysqlclient这行
# mysqlclient==2.2.0  ← 注释这行
```

**问题2: 网络慢**
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 2.4 配置环境变量

**复制环境变量模板:**
```bash
cp env.template .env
```

**编辑 `.env` 文件:**
```env
# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password    # 改为你的MySQL密码
MYSQL_DATABASE=hospital_db

# Flask配置
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# JWT配置
JWT_SECRET_KEY=jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
```

**⚠️ 重要提示:**
- `MYSQL_PASSWORD` 必须改为你的MySQL root密码
- 生产环境必须修改 `SECRET_KEY` 和 `JWT_SECRET_KEY`

---

### 3. 前端配置

#### 3.1 创建前端项目（首次）

```bash
# 使用Vite创建Vue 3项目
npm create vite@latest frontend -- --template vue

# 进入前端目录
cd frontend
```

#### 3.2 安装前端依赖

```bash
# 核心依赖
npm install vue-router@4 pinia axios element-plus

# Element Plus图标
npm install @element-plus/icons-vue

# Tailwind CSS（可选）
npm install -D tailwindcss autoprefixer postcss
```

#### 3.3 配置Axios基础URL

创建 `frontend/src/api/request.js`:

```javascript
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { data } = response
    if (data.success === false) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    return data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          ElMessage.error(data.message || '请求参数错误')
          break
        case 401:
          ElMessage.error('未授权，请重新登录')
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 404:
          ElMessage.error('请求资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(data.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request
```

创建 `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

#### 3.4 配置Vite

编辑 `frontend/vite.config.js`:

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

---

### 4. 数据库配置

#### 4.1 登录MySQL

```bash
# Windows/Linux/macOS
mysql -u root -p
# 输入MySQL root密码
```

#### 4.2 创建数据库

**方式1: 使用SQL脚本（推荐）**

```bash
# 退出MySQL命令行后执行
mysql -u root -p < init_database.sql
```

**方式2: 手动创建**

在MySQL命令行中执行：

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS hospital_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 查看数据库
SHOW DATABASES;

-- 使用数据库
USE hospital_db;
```

#### 4.3 创建数据库用户（生产环境推荐）

```sql
-- 创建专用用户
CREATE USER IF NOT EXISTS 'hospital_user'@'localhost' 
IDENTIFIED BY 'secure_password';

-- 授权
GRANT ALL PRIVILEGES ON hospital_db.* 
TO 'hospital_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;
```

然后更新 `.env` 文件：
```env
MYSQL_USER=hospital_user
MYSQL_PASSWORD=secure_password
```

#### 4.4 初始化数据库表

```bash
# 确保虚拟环境已激活
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ 数据库表创建成功')"
```

**成功输出:**
```
✅ 数据库表创建成功
```

#### 4.5 验证数据库表

```bash
mysql -u root -p hospital_db -e "SHOW TABLES;"
```

**应该看到以下表:**
```
+------------------------+
| Tables_in_hospital_db  |
+------------------------+
| appointments           |
| doctor_performances    |
| doctor_schedules       |
| doctors                |
| medical_records        |
| medicine_inventory     |
| medicine_purchases     |
| medicines              |
| patients               |
+------------------------+
```

---

## 验证安装

### 1. 启动后端服务

```bash
# 确保在项目根目录，虚拟环境已激活
python app.py
```

**成功启动的输出:**

```
======================================================================
🏥 医院综合管理系统 API 已启动
======================================================================
📋 系统信息:
   - 版本: 2.0.0
   - 数据库: MySQL (hospital_db)
   - 模式: 前后端分离架构
   - 环境: development

🔗 API端点:
   - 健康检查: http://localhost:5000/
   - 病人管理API: http://localhost:5000/api/patient
   - 医生管理API: http://localhost:5000/api/doctor
   - 药品管理API: http://localhost:5000/api/pharmacy

💡 提示:
   - 前端Vue项目请运行: npm run dev
   - API响应格式: JSON
   - 确保MySQL数据库已启动
======================================================================
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 2. 测试后端API

**方式1: 浏览器访问**

打开浏览器访问: http://localhost:5000/

应该看到：
```json
{
  "status": "success",
  "message": "医院综合管理系统API运行正常",
  "version": "2.0.0",
  "architecture": "前后端分离",
  "database": "MySQL"
}
```

**方式2: 使用curl命令**

```bash
# 测试健康检查
curl http://localhost:5000/

# 测试获取病人列表
curl http://localhost:5000/api/patient/patients

# 测试获取医生列表
curl http://localhost:5000/api/doctor/doctors

# 测试获取药品列表
curl http://localhost:5000/api/pharmacy/medicines
```

**方式3: 使用Postman**

1. 打开Postman
2. 创建GET请求: `http://localhost:5000/api/patient/patients`
3. 发送请求，应该返回病人列表（初始为空数组）

### 3. 启动前端服务

```bash
# 新开一个终端
cd frontend
npm run dev
```

**成功启动的输出:**
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

访问 http://localhost:5173/ 应该能看到Vue应用界面。

### 4. 测试完整流程

#### 测试病人管理功能

使用Postman或curl创建一个病人：

```bash
curl -X POST http://localhost:5000/api/patient/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "gender": "男",
    "age": 30,
    "phone": "13800138000",
    "address": "北京市朝阳区"
  }'
```

**成功响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "张三",
    "gender": "男",
    "age": 30,
    "phone": "13800138000",
    "address": "北京市朝阳区",
    "created_at": "2025-10-11T10:30:00"
  },
  "message": "创建成功"
}
```

然后查询病人列表：
```bash
curl http://localhost:5000/api/patient/patients
```

---

## 常见问题

### 后端相关

#### Q1: MySQL连接失败

**错误信息:**
```
Can't connect to MySQL server on 'localhost'
```

**解决方案:**
1. 确认MySQL服务已启动
   ```bash
   # Windows
   net start MySQL80
   
   # macOS
   brew services start mysql
   
   # Linux
   sudo systemctl start mysql
   ```

2. 检查`.env`文件中的数据库配置
3. 验证MySQL用户名和密码
4. 测试MySQL连接：
   ```bash
   mysql -u root -p -h localhost
   ```

#### Q2: 端口5000已被占用

**错误信息:**
```
Address already in use
```

**解决方案:**

**Windows:**
```bash
# 查找占用端口的进程
netstat -ano | findstr :5000

# 结束进程（替换PID）
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
# 查找占用端口的进程
lsof -i :5000

# 结束进程
kill -9 <PID>
```

或者修改`config.py`中的端口：
```python
PORT = 5001  # 改为其他端口
```

#### Q3: 虚拟环境激活失败

**Windows PowerShell错误:**
```
无法加载文件 venv\Scripts\Activate.ps1
```

**解决方案:**
```bash
# 以管理员身份运行PowerShell
Set-ExecutionPolicy RemoteSigned

# 或使用cmd
venv\Scripts\activate.bat
```

#### Q4: pip安装依赖很慢

**解决方案:**
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或配置永久镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### Q5: 数据库表不存在

**错误信息:**
```
Table 'hospital_db.patients' doesn't exist
```

**解决方案:**
```bash
# 重新创建数据库表
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"
```

### 前端相关

#### Q6: npm install失败

**解决方案:**
```bash
# 清除缓存
npm cache clean --force

# 删除node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 或使用淘宝镜像
npm install --registry=https://registry.npmmirror.com
```

#### Q7: CORS跨域错误

**错误信息:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**解决方案:**
1. 确认`app.py`中已配置CORS：
   ```python
   from flask_cors import CORS
   CORS(app)
   ```

2. 检查前端API请求地址是否正确
3. 确认后端服务已启动

#### Q8: Vite启动失败

**错误信息:**
```
Error: Cannot find module '@vitejs/plugin-vue'
```

**解决方案:**
```bash
npm install -D @vitejs/plugin-vue
```

### 数据库相关

#### Q9: MySQL root密码忘记

**解决方案（Windows）:**
```bash
# 1. 停止MySQL服务
net stop MySQL80

# 2. 跳过权限验证启动
mysqld --console --skip-grant-tables --shared-memory

# 3. 新开终端，无密码登录
mysql -u root

# 4. 重置密码
USE mysql;
UPDATE user SET authentication_string='' WHERE user='root';
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';

# 5. 重启MySQL服务
```

#### Q10: 字符编码问题

**错误信息:**
```
Incorrect string value
```

**解决方案:**
```sql
-- 确认数据库字符集
SHOW CREATE DATABASE hospital_db;

-- 修改为utf8mb4
ALTER DATABASE hospital_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

---

## 生产环境部署

### 1. 后端部署

#### 使用Gunicorn

```bash
# 安装Gunicorn
pip install gunicorn

# 启动生产服务器（4个工作进程）
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# 使用gevent worker（更高性能）
pip install gevent
gunicorn -w 4 -k gevent -b 0.0.0.0:5000 "app:create_app()"
```

#### 配置Systemd服务（Linux）

创建 `/etc/systemd/system/hospital-api.service`:

```ini
[Unit]
Description=Hospital Management System API
After=network.target mysql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/hospital-management-system
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start hospital-api
sudo systemctl enable hospital-api
```

### 2. 前端部署

#### 构建前端

```bash
cd frontend
npm run build
```

构建完成后，`dist` 目录包含静态文件。

#### 使用Nginx托管

安装Nginx：
```bash
# Ubuntu/Debian
sudo apt install nginx

# macOS
brew install nginx
```

配置Nginx（`/etc/nginx/sites-available/hospital`）：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 代理后端API
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/hospital /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. SSL证书配置

使用Let's Encrypt免费证书：

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 4. 生产环境配置清单

- [ ] 修改 `SECRET_KEY` 和 `JWT_SECRET_KEY`
- [ ] 关闭 `DEBUG` 模式
- [ ] 使用专用数据库用户
- [ ] 配置防火墙
- [ ] 启用HTTPS
- [ ] 配置日志记录
- [ ] 设置自动备份
- [ ] 配置监控告警

---

## 开发工作流

### 日常开发

```bash
# 1. 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 2. 启动后端（终端1）
python app.py

# 3. 启动前端（终端2）
cd frontend
npm run dev

# 4. 开始开发...
```

### 数据库迁移

```bash
# 安装Flask-Migrate
pip install Flask-Migrate

# 初始化迁移（仅首次）
flask db init

# 生成迁移脚本
flask db migrate -m "描述变更内容"

# 执行迁移
flask db upgrade

# 回滚
flask db downgrade
```

### 代码格式化

```bash
# Python代码格式化
pip install black flake8
black .
flake8 .

# Vue代码格式化
cd frontend
npm run lint
```

---

## 技术支持

### 获取帮助

1. **查看文档**
   - [README.md](README.md) - 项目概览
   - [DEVELOPMENT.md](DEVELOPMENT.md) - 开发指南
   - [CHANGELOG.md](CHANGELOG.md) - 版本历史

2. **调试技巧**
   - 查看后端日志（终端输出）
   - 查看前端日志（浏览器控制台F12）
   - 检查MySQL日志
   - 使用浏览器Network面板查看API请求

3. **社区资源**
   - [Flask官方文档](https://flask.palletsprojects.com/)
   - [Vue.js官方文档](https://cn.vuejs.org/)
   - [MySQL官方文档](https://dev.mysql.com/doc/)

---

## 下一步

安装完成后，建议：

1. 📖 阅读 [DEVELOPMENT.md](DEVELOPMENT.md) 了解开发规范
2. 🧪 测试各个API端点
3. 💻 开始开发你负责的模块
4. 🤝 与团队成员协作

---

**文档版本**: v2.0  
**最后更新**: 2025-10-11  
**维护团队**: 医院管理系统开发组

---

<div align="center">

如遇到问题，请先查看[常见问题](#常见问题)部分

[返回README](README.md) • [开发指南](DEVELOPMENT.md) • [更新日志](CHANGELOG.md)

</div>

