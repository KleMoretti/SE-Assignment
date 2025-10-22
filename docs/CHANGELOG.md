# 医院综合管理系统 - 变更日志

## [2.2.0] - 2025-10-22

### ✨ 新增功能

#### 用户认证与授权系统

**后端认证功能**：
- ✅ 用户模型（User）- 支持多角色（admin/doctor/nurse/user）
- ✅ JWT认证集成 - 使用Flask-JWT-Extended
- ✅ 用户注册API - 支持用户名、邮箱、角色等信息
- ✅ 用户登录API - 返回access_token和refresh_token
- ✅ Token刷新API - 自动刷新access_token
- ✅ 获取当前用户信息API
- ✅ 更新个人信息API
- ✅ 修改密码API
- ✅ 用户管理API（管理员专用）- 列表、更新、删除
- ✅ 角色权限装饰器 - `@role_required()`
- ✅ 密码加密存储 - 使用Werkzeug安全函数

**前端认证功能**：
- ✅ 登录/注册页面 - 现代化UI设计
- ✅ 用户状态管理 - Pinia Store
- ✅ Token自动管理 - localStorage持久化
- ✅ 请求拦截器升级 - 自动添加Authorization头
- ✅ 响应拦截器优化 - 401自动跳转登录
- ✅ 路由守卫 - 未登录拦截+登录后重定向
- ✅ 用户信息缓存 - 刷新页面保持登录状态

#### 医生管理前端集成

**医生管理界面**：
- ✅ 医生列表页面 - 完整的CRUD操作
- ✅ 高级搜索功能 - 支持姓名、编号、科室、状态多维度筛选
- ✅ 添加/编辑对话框 - 表单验证+美观UI
- ✅ 医生详情展示 - 包含统计信息
- ✅ 数据分页 - 可配置每页显示数量
- ✅ 操作确认 - 删除前二次确认
- ✅ 响应式设计 - 适配不同屏幕尺寸

**API集成**：
- ✅ 完整的医生管理API封装（`/api/doctor.js`）
- ✅ 完整的认证API封装（`/api/auth.js`）
- ✅ 统一的错误处理机制
- ✅ Loading状态管理

### 🔄 核心变更

#### 1. 用户模型 (`backend/models.py`)

**新增User模型**：
```python
class User(db.Model):
    - username（用户名，唯一）
    - password_hash（密码哈希）
    - email（邮箱）
    - phone（手机号）
    - real_name（真实姓名）
    - role（角色：admin/doctor/nurse/user）
    - department（所属科室）
    - is_active（是否激活）
    - last_login（最后登录时间）
```

**方法**：
- `set_password()` - 设置密码（自动加密）
- `check_password()` - 验证密码
- `to_dict()` - 序列化（支持敏感信息控制）

#### 2. 认证模块 (`backend/modules/auth/`)

**新增认证蓝图**：
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新Token
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/update-profile` - 更新个人信息
- `POST /api/auth/change-password` - 修改密码
- `GET /api/auth/users` - 获取用户列表（管理员）
- `PUT /api/auth/users/<id>` - 更新用户（管理员）
- `DELETE /api/auth/users/<id>` - 删除用户（管理员）

**权限控制**：
```python
@role_required('admin', 'doctor')
def protected_route():
    pass
```

#### 3. 应用配置 (`backend/app.py`)

**变更**：
- ✅ 注册认证蓝图 - `/api/auth`
- ✅ JWT配置已在config.py中定义
- ✅ CORS配置已支持Authorization头

#### 4. 前端状态管理 (`frontend/src/stores/user.js`)

**新增用户Store**：
```javascript
- token, refreshToken（Token管理）
- userInfo（用户信息）
- isLoggedIn（登录状态）
- isAdmin, isDoctor（角色判断）
- handleLogin()（登录处理）
- handleLogout()（登出处理）
- getUserInfo()（获取用户信息）
```

#### 5. 请求拦截器 (`frontend/src/api/request.js`)

**升级内容**：
- ✅ 自动添加Token到请求头
- ✅ 刷新Token请求特殊处理
- ✅ 401错误自动清除Token并跳转登录
- ✅ 错误信息优化展示

#### 6. 路由配置 (`frontend/src/router/index.js`)

**新增功能**：
- ✅ 登录路由 - `/login`
- ✅ 全局前置守卫 - 认证检查
- ✅ 未登录拦截 - 自动跳转登录页
- ✅ 登录后重定向 - 返回原始页面
- ✅ 404路由处理

**路由元信息**：
```javascript
meta: {
  title: '页面标题',
  requiresAuth: true // 是否需要认证
}
```

### 📝 文件变更

#### 新增文件

**后端**：
- `backend/modules/auth/__init__.py` - 认证模块初始化
- `backend/modules/auth/routes.py` - 认证路由（10个API，400+行）

**前端**：
- `frontend/src/api/auth.js` - 认证API封装（9个方法）
- `frontend/src/api/doctor.js` - 医生管理API封装（17个方法）
- `frontend/src/stores/user.js` - 用户状态管理
- `frontend/src/views/Login.vue` - 登录/注册页面
- `frontend/src/views/doctor/DoctorList.vue` - 医生列表页面（完整功能）

#### 修改文件

**后端**：
- `backend/models.py` - 添加User模型
- `backend/app.py` - 注册认证蓝图

**前端**：
- `frontend/src/api/request.js` - 升级请求/响应拦截器
- `frontend/src/router/index.js` - 添加路由守卫

### 🔧 功能特性

#### 认证流程

1. **注册流程**：
   - 填写用户名、密码等信息
   - 后端验证（用户名唯一性、密码长度等）
   - 密码加密存储
   - 返回用户信息

2. **登录流程**：
   - 提交用户名和密码
   - 后端验证用户身份
   - 生成JWT Token（access + refresh）
   - 前端存储Token和用户信息
   - 自动跳转到首页或原始页面

3. **Token管理**：
   - Access Token - 有效期短（如1小时）
   - Refresh Token - 有效期长（如7天）
   - Token自动刷新机制
   - 过期自动跳转登录

4. **权限控制**：
   - 基于角色的访问控制（RBAC）
   - 装饰器保护API端点
   - 前端路由守卫
   - 管理员特权功能

#### 安全特性

- ✅ 密码加密存储（Werkzeug安全函数）
- ✅ JWT Token认证（Flask-JWT-Extended）
- ✅ Token过期自动处理
- ✅ 用户状态检查（is_active）
- ✅ 角色权限验证
- ✅ 防止管理员账号删除
- ✅ CORS跨域安全配置

### 📚 API使用示例

#### 用户注册
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "doctor_zhang",
  "password": "123456",
  "email": "zhang@hospital.com",
  "real_name": "张医生",
  "role": "doctor",
  "department": "内科"
}
```

#### 用户登录
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "doctor_zhang",
  "password": "123456"
}

响应：
{
  "success": true,
  "data": {
    "user": { ... },
    "access_token": "eyJ0eXAi...",
    "refresh_token": "eyJ0eXAi...",
    "token_type": "Bearer"
  }
}
```

#### 受保护的API请求
```bash
GET /api/doctor/doctors
Authorization: Bearer eyJ0eXAi...
```

### ⚠️ 重要提示

#### 初始化管理员账号

系统首次运行后，需要手动创建管理员账号：

```bash
# 方法1：通过注册API创建
POST /api/auth/register
{
  "username": "admin",
  "password": "admin123",
  "role": "admin",
  "email": "admin@hospital.com"
}

# 方法2：通过Python脚本创建
python create_admin.py
```

#### Token配置

在`backend/config.py`中配置JWT：
```python
JWT_SECRET_KEY = 'your-secret-key'  # 生产环境请使用强随机字符串
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
```

#### 前端环境变量

在`frontend/.env`中配置：
```env
VITE_API_BASE_URL=http://localhost:5000/api
```

### 🐛 Bug修复

- ✅ 修复request.js中router导入循环依赖问题
- ✅ 修复Token过期后无限重定向问题
- ✅ 修复用户信息缓存不一致问题

### 🚀 性能优化

- ✅ Token存储优化（localStorage）
- ✅ 用户信息缓存机制
- ✅ 路由懒加载（动态import）
- ✅ API请求防抖处理

---

## [2.1.0] - 2025-10-22

### ✨ 新增功能

#### 医生管理模块 RESTful API

**医生信息管理 API**：
- ✅ `GET /api/doctor/doctors` - 获取医生列表（支持分页、搜索、多维度过滤）
- ✅ `GET /api/doctor/doctors/<id>` - 获取医生详情（包含统计信息）
- ✅ `POST /api/doctor/doctors` - 创建医生
- ✅ `PUT /api/doctor/doctors/<id>` - 更新医生信息
- ✅ `DELETE /api/doctor/doctors/<id>` - 删除医生（带关联检查）
- ✅ `GET /api/doctor/doctors/statistics` - 获取医生统计数据

**医生排班管理 API**：
- ✅ `GET /api/doctor/schedules` - 获取排班列表（支持多维度过滤）
- ✅ `GET /api/doctor/schedules/<id>` - 获取排班详情
- ✅ `POST /api/doctor/schedules` - 创建排班（带重复检查）
- ✅ `PUT /api/doctor/schedules/<id>` - 更新排班
- ✅ `DELETE /api/doctor/schedules/<id>` - 删除排班
- ✅ `GET /api/doctor/doctors/<id>/schedules` - 获取医生的排班列表（支持日期范围）

**医生绩效管理 API**：
- ✅ `GET /api/doctor/performances` - 获取绩效列表（支持年月过滤）
- ✅ `GET /api/doctor/performances/<id>` - 获取绩效详情
- ✅ `POST /api/doctor/performances` - 创建绩效评估（自动计算综合评分和奖金）
- ✅ `PUT /api/doctor/performances/<id>` - 更新绩效评估
- ✅ `DELETE /api/doctor/performances/<id>` - 删除绩效评估
- ✅ `GET /api/doctor/doctors/<id>/performances` - 获取医生的绩效记录（含统计）
- ✅ `GET /api/doctor/performances/statistics` - 获取绩效统计数据

### 🔄 核心变更

#### 1. 统一响应格式 (`backend/modules/doctor/routes.py`)

**新增辅助函数**：
```python
def success_response(data=None, message='操作成功', code='SUCCESS')
def error_response(message='操作失败', code='ERROR', status_code=400)
```

**响应格式**：
```json
{
  "success": true/false,
  "message": "提示信息",
  "code": "状态码",
  "data": { ... }
}
```

#### 2. 数据验证增强

**医生信息验证**：
- ✅ 必填字段验证（doctor_no, name, gender）
- ✅ 医生编号唯一性检查
- ✅ 日期格式验证（YYYY-MM-DD）
- ✅ 外键关联验证

**排班验证**：
- ✅ 必填字段验证（doctor_id, date, shift）
- ✅ 排班冲突检查（同医生同时段）
- ✅ 医生存在性验证
- ✅ 日期范围验证

**绩效验证**：
- ✅ 必填字段验证（doctor_id, year, month）
- ✅ 月份范围验证（1-12）
- ✅ 重复记录检查（同医生同年月）
- ✅ 自动计算综合评分和奖金

#### 3. 错误处理优化

**新增错误代码**：
- `DOCTOR_NOT_FOUND` - 医生不存在
- `DOCTOR_NO_EXISTS` - 医生编号已存在
- `DOCTOR_HAS_APPOINTMENTS` - 医生有关联预约记录
- `DOCTOR_HAS_MEDICAL_RECORDS` - 医生有关联病历记录
- `SCHEDULE_NOT_FOUND` - 排班不存在
- `SCHEDULE_EXISTS` - 排班冲突
- `PERFORMANCE_NOT_FOUND` - 绩效记录不存在
- `PERFORMANCE_EXISTS` - 绩效记录重复
- `INVALID_DATE_FORMAT` - 日期格式错误
- `INVALID_MONTH` - 月份无效
- `MISSING_FIELD` - 缺少必填字段

#### 4. 查询功能增强

**医生列表过滤**：
- ✅ 搜索：姓名、编号、电话、邮箱
- ✅ 科室过滤
- ✅ 状态过滤（在职/离职）
- ✅ 职称过滤
- ✅ 分页支持

**排班列表过滤**：
- ✅ 医生过滤
- ✅ 日期过滤
- ✅ 班次过滤
- ✅ 状态过滤
- ✅ 日期范围查询

**绩效列表过滤**：
- ✅ 医生过滤
- ✅ 年份过滤
- ✅ 月份过滤
- ✅ 分页支持

#### 5. 统计功能

**医生统计**：
- ✅ 总医生数、在职数、离职数
- ✅ 按科室统计分布
- ✅ 按职称统计分布
- ✅ 科室列表、职称列表

**医生详情统计**：
- ✅ 预约总数、已完成预约数
- ✅ 病历记录总数
- ✅ 排班总数

**绩效统计**：
- ✅ 接诊人数统计
- ✅ 平均满意度
- ✅ 平均综合评分
- ✅ 奖金总额

### 📝 文件变更

#### 修改的文件
- `backend/modules/doctor/routes.py` - 完善医生管理API接口
  - 添加RESTful API路由（医生信息、排班、绩效）
  - 添加统一响应格式
  - 添加数据验证和错误处理
  - 添加统计分析功能
  - 保留传统视图（兼容现有模板）

### 🔧 API功能特性

#### 分页支持
所有列表接口均支持分页：
```
?page=1&per_page=10
```

#### 搜索过滤
支持模糊搜索和精确过滤：
```
?search=张三&department=内科&status=active
```

#### 关联数据
响应中包含关联对象的基本信息：
```json
{
  "doctor_id": 1,
  "doctor_name": "张医生"
}
```

#### 级联检查
删除操作前检查关联记录，防止数据孤立。

### ⚠️ 兼容性说明

- ✅ 保留传统视图路由（`/list`, `/doctor/add`, `/doctor/edit` 等）
- ✅ RESTful API使用新路由（`/doctors`, `/schedules`, `/performances`）
- ✅ 两种路由可以并存，互不影响
- ✅ 模板路径更新为 `doctor/` 子目录

### 🐛 Bug修复

- ✅ 修复传统视图路由冲突问题（`/doctors` vs `/list`）
- ✅ 修复日期格式处理错误
- ✅ 修复外键关联验证缺失

### 🚀 性能优化

- ✅ 使用 `filter_by` 而非 `filter` 提升查询性能
- ✅ 优化统计查询，减少数据库访问次数
- ✅ 序列化优化，使用模型自带的 `to_dict()` 方法

### 📚 API使用示例

#### 创建医生
```bash
POST /api/doctor/doctors
Content-Type: application/json

{
  "doctor_no": "D001",
  "name": "张医生",
  "gender": "男",
  "department": "内科",
  "title": "主任医师",
  "phone": "13800138000",
  "email": "zhang@hospital.com"
}
```

#### 创建排班
```bash
POST /api/doctor/schedules
Content-Type: application/json

{
  "doctor_id": 1,
  "date": "2025-10-23",
  "shift": "morning",
  "start_time": "08:00",
  "end_time": "12:00",
  "max_patients": 30
}
```

#### 创建绩效评估
```bash
POST /api/doctor/performances
Content-Type: application/json

{
  "doctor_id": 1,
  "year": 2025,
  "month": 10,
  "patient_count": 120,
  "satisfaction_score": 95,
  "punctuality_score": 98,
  "quality_score": 92
}
```

---

## [2.0.0] - 2025-10-11

### 🎉 重大变更：技术栈升级

本次更新将系统架构从传统Web应用升级为**前后端分离架构**。

---

### ✨ 新增功能

#### 前端技术栈
- ✅ 引入 **Vue.js 3.x** 作为前端框架
- ✅ 使用 **Vite** 作为构建工具
- ✅ 集成 **Element Plus** UI组件库
- ✅ 引入 **Pinia** 进行状态管理
- ✅ 使用 **Axios** 处理HTTP请求
- ✅ 配置 **Vue Router 4** 路由管理

#### 后端技术栈
- ✅ 添加 **Flask-CORS** 支持跨域请求
- ✅ 集成 **Flask-JWT-Extended** 实现JWT认证
- ✅ 引入 **Flask-RESTful** 构建REST API
- ✅ 添加 **python-dotenv** 环境变量管理
- ✅ 集成 **marshmallow** 数据验证

#### 数据库
- ✅ 从 SQLite 迁移到 **MySQL 8.0+**
- ✅ 配置数据库连接池
- ✅ 添加自动重连机制

---

### 🔄 核心变更

#### 1. 配置文件 (`config.py`)

**变更内容**：
- ✅ 添加 MySQL 数据库配置
- ✅ 添加 JWT 认证配置
- ✅ 添加 CORS 配置
- ✅ 添加数据库连接池配置
- ✅ 系统版本升级至 2.0.0

**新增配置项**：
```python
# MySQL配置
MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

# JWT配置
JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES, JWT_REFRESH_TOKEN_EXPIRES

# 连接池配置
SQLALCHEMY_POOL_SIZE, SQLALCHEMY_POOL_RECYCLE
```

#### 2. 应用入口 (`app.py`)

**重大变更**：
- ✅ 添加 CORS 中间件支持
- ✅ 初始化 JWT 管理器
- ✅ API路由前缀改为 `/api/*`
- ✅ 移除模板渲染，改为JSON API响应
- ✅ 添加健康检查端点 (`/` 和 `/health`)
- ✅ 添加全局错误处理（404, 500）
- ✅ 优化启动信息显示

**路由变更**：
```
旧: /patient/* → 新: /api/patient/*
旧: /doctor/*  → 新: /api/doctor/*
旧: /pharmacy/* → 新: /api/pharmacy/*
```

#### 3. 数据库模型 (`models.py`)

**所有模型添加**：
- ✅ `to_dict()` 方法：支持JSON序列化
- ✅ 时间字段改用 `datetime.utcnow`（避免时区问题）
- ✅ 关系字段添加 `cascade='all, delete-orphan'`（级联删除）
- ✅ 导入 `typing.Dict` 类型提示

**新增功能**：
- ✅ 自动计算低库存状态 (`MedicineInventory`)
- ✅ 包含关联数据（如病人姓名、医生姓名）
- ✅ Float类型字段转换为标准float

#### 4. 依赖包 (`requirements.txt`)

**新增依赖**：
```txt
# 数据库驱动
PyMySQL==1.1.0
mysqlclient==2.2.0

# RESTful API
Flask-RESTful==0.3.10
Flask-CORS==4.0.0

# JWT认证
Flask-JWT-Extended==4.5.3

# 环境变量
python-dotenv==1.0.0

# 数据验证
marshmallow==3.20.1

# 数据库迁移
Flask-Migrate==4.0.5
```

---

### 📁 新增文件

#### 配置文件
- ✅ `env.template` - 环境变量模板
- ✅ `init_database.sql` - MySQL数据库初始化脚本

#### 文档文件
- ✅ `SETUP_GUIDE.md` - 详细的环境配置指南
- ✅ `CHANGELOG.md` - 本变更日志
- ✅ `.cursor/rules/hospital.mdc` - 完整的技术选型与编码规范

---

### 🔧 配置变更

#### 环境变量（新增）
```env
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=hospital_db

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
```

#### 数据库连接字符串
```
旧: sqlite:///hospital.db
新: mysql+pymysql://user:pass@localhost:3306/hospital_db?charset=utf8mb4
```

---

### 📝 API变更

#### 路由前缀变更

| 模块 | 旧路由 | 新路由 |
|------|--------|--------|
| 病人管理 | `/patient/*` | `/api/patient/*` |
| 医生管理 | `/doctor/*` | `/api/doctor/*` |
| 药品管理 | `/pharmacy/*` | `/api/pharmacy/*` |

#### 响应格式标准化

**成功响应**：
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应**：
```json
{
  "success": false,
  "message": "错误信息",
  "code": "ERROR_CODE"
}
```

---

### ⚠️ 重要提示

#### 向后兼容性
- ⚠️ 本次更新**不向后兼容** v1.x版本
- ⚠️ 前端HTML模板不再使用，需要重新开发Vue前端
- ⚠️ 数据库从SQLite迁移到MySQL，需要数据迁移

#### 迁移步骤
1. 备份现有SQLite数据库
2. 安装MySQL 8.0+
3. 创建新数据库并执行`init_database.sql`
4. 迁移数据（如需要）
5. 更新依赖包：`pip install -r requirements.txt`
6. 配置环境变量：复制`env.template`为`.env`
7. 初始化数据库表：运行数据库初始化命令
8. 启动后端服务：`python app.py`
9. 开发Vue前端项目

---

### 📚 文档更新

- ✅ 更新 `README.md` - 反映新技术栈
- ✅ 新增 `SETUP_GUIDE.md` - 详细配置指南
- ✅ 更新 `.cursor/rules/hospital.mdc` - 完整规范文档

---

### 🐛 Bug修复

- ✅ 修复时间字段使用本地时间导致的时区问题
- ✅ 修复datetime.now在类定义时求值的问题
- ✅ 优化数据库连接池配置

---

### 🚀 性能优化

- ✅ 添加数据库连接池（提升并发性能）
- ✅ 添加连接预检和自动重连
- ✅ 优化查询性能（添加索引）
- ✅ 前后端分离架构（提升用户体验）

---

### 📦 依赖变更

#### 新增
- Flask-CORS 4.0.0
- Flask-RESTful 0.3.10
- Flask-JWT-Extended 4.5.3
- PyMySQL 1.1.0
- python-dotenv 1.0.0
- marshmallow 3.20.1

#### 保持
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Werkzeug 3.0.1

---

### 🎯 下一步计划

#### v2.1 (计划中)
- [ ] 完整的JWT认证实现
- [ ] 用户权限管理
- [ ] Vue前端完整实现
- [ ] API文档（Swagger）
- [ ] 单元测试覆盖

#### v3.0 (规划中)
- [ ] 微服务架构
- [ ] Redis缓存
- [ ] 消息队列
- [ ] Docker部署
- [ ] CI/CD集成

---

### 👥 贡献者

- 系统架构升级
- 技术栈迁移
- 文档编写

---

### 📞 技术支持

如有问题，请查看：
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 环境配置指南
- [.cursor/rules/hospital.mdc](.cursor/rules/hospital.mdc) - 编码规范
- [README.md](README.md) - 项目说明

---

**版本**: 2.0.0  
**发布日期**: 2025-10-11  
**架构**: 前后端分离  
**状态**: ✅ 稳定版本

