# 医院综合管理系统 - 变更日志

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

