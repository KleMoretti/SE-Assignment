# 医院综合管理系统

<div align="center">

**基于Flask的模块化医院管理系统**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-orange.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-Educational-lightgrey.svg)]()

</div>

---

## 📋 项目简介

医院综合管理系统是一个采用**前后端分离架构**的现代化管理系统，使用Flask构建RESTful API后端，Vue.js构建前端界面。系统采用模块化设计，支持三人协作开发。

### 核心特性

- 🏗️ **模块化架构** - 基于Flask蓝图的模块化设计
- 🔄 **前后端分离** - RESTful API + Vue.js前端
- 👥 **多人协作** - 三个独立子系统，支持并行开发
- 🗄️ **MySQL数据库** - 企业级数据库支持
- 🔐 **JWT认证** - 现代化的身份认证机制
- 📱 **响应式设计** - 适配多种设备

---

## 🏛️ 系统架构

### 技术栈 v2.0

**后端技术**
- Python 3.8+
- Flask 3.0.0 (Web框架)
- Flask-SQLAlchemy 3.1.1 (ORM)
- Flask-RESTful (REST API)
- Flask-JWT-Extended (JWT认证)
- MySQL 8.0+ (数据库)

**前端技术**
- Vue.js 3.x (前端框架)
- Vite 4.x (构建工具)
- Element Plus (UI组件库)
- Pinia (状态管理)
- Axios (HTTP客户端)

### 子系统模块

| 模块 | 路由前缀 | 负责开发者 | 主要功能 |
|------|----------|-----------|----------|
| **病人管理** | `/api/patient` | 开发者1 | 病人信息、病历记录、预约挂号 |
| **医生管理** | `/api/doctor` | 开发者2 | 医生信息、排班管理、绩效评估 |
| **药品管理** | `/api/pharmacy` | 开发者3 | 药品信息、库存管理、采购管理 |

---

## 🚀 快速开始

### 前置要求

- Python 3.8+
- MySQL 8.0+
- Node.js 16+ (前端开发)

### 三步启动

```bash
# 1. 安装后端依赖
pip install -r requirements.txt

# 2. 配置数据库
cp env.template .env  # 编辑.env配置MySQL连接信息
mysql -u root -p < init_database.sql

# 3. 启动后端服务
python app.py
```

**访问地址:**
- 后端API: http://localhost:5000/
- 前端应用: http://localhost:5173/ (需单独启动Vue项目)

> 💡 **详细安装步骤请查看**: [📖 INSTALLATION.md](INSTALLATION.md)

---

## 📂 项目结构

```
hospital-management-system/
├── app.py                      # 应用入口
├── config.py                   # 配置文件
├── models.py                   # 数据库模型
├── requirements.txt            # Python依赖
├── init_database.sql           # 数据库初始化脚本
├── env.template                # 环境变量模板
│
├── modules/                    # 子系统模块
│   ├── patient/               # 病人管理（开发者1）
│   ├── doctor/                # 医生管理（开发者2）
│   └── pharmacy/              # 药品管理（开发者3）
│
├── templates/                  # HTML模板
│   ├── patient/
│   ├── doctor/
│   └── pharmacy/
│
└── static/                     # 静态资源
    ├── css/
    └── js/
```

---

## 📚 文档导航

| 文档 | 说明 | 适用对象 |
|------|------|---------|
| [📖 INSTALLATION.md](INSTALLATION.md) | 完整的安装配置指南 | 首次安装、环境配置 |
| [👨‍💻 DEVELOPMENT.md](DEVELOPMENT.md) | 开发者完整指南 | 项目开发、多人协作 |
| [📝 CHANGELOG.md](CHANGELOG.md) | 版本变更历史 | 了解版本更新内容 |
| [📋 .cursor/rules/hospital.mdc](.cursor/rules/hospital.mdc) | 技术选型与编码规范 | 编码规范参考 |

---

## 💻 开发指南

### 多人协作分工

#### 👤 开发者1 - 病人管理子系统
- **工作目录**: `modules/patient/`, `templates/patient/`
- **核心功能**: 病人信息管理、病历记录、预约挂号
- **数据模型**: Patient, MedicalRecord, Appointment

#### 👤 开发者2 - 医生管理子系统
- **工作目录**: `modules/doctor/`, `templates/doctor/`
- **核心功能**: 医生信息管理、排班管理、绩效评估
- **数据模型**: Doctor, DoctorSchedule, DoctorPerformance

#### 👤 开发者3 - 药品管理子系统
- **工作目录**: `modules/pharmacy/`, `templates/pharmacy/`
- **核心功能**: 药品信息管理、库存管理、采购管理
- **数据模型**: Medicine, MedicineInventory, MedicinePurchase

> 📘 **详细开发指南请查看**: [👨‍💻 DEVELOPMENT.md](DEVELOPMENT.md)

### Git协作流程

```bash
# 1. 克隆项目
git clone <repository-url>
cd hospital-management-system

# 2. 创建开发分支
git checkout -b feature/your-module

# 3. 开发完成后提交
git add .
git commit -m "feat(module): description"
git push origin feature/your-module

# 4. 创建Pull Request进行代码审查
```

---

## 🗄️ 数据库设计

### 核心数据表

**病人管理模块**
- `patients` - 病人基本信息
- `medical_records` - 病历记录
- `appointments` - 预约挂号

**医生管理模块**
- `doctors` - 医生信息
- `doctor_schedules` - 医生排班
- `doctor_performances` - 医生绩效

**药品管理模块**
- `medicines` - 药品信息
- `medicine_inventory` - 药品库存
- `medicine_purchases` - 药品采购

### 数据库关系

```
Patient ─┬─ 1:N ─→ MedicalRecord
         └─ 1:N ─→ Appointment

Doctor ──┬─ 1:N ─→ MedicalRecord
         ├─ 1:N ─→ Appointment
         ├─ 1:N ─→ DoctorSchedule
         └─ 1:N ─→ DoctorPerformance

Medicine ┬─ 1:1 ─→ MedicineInventory
         └─ 1:N ─→ MedicinePurchase
```

---

## 🔌 API接口

### RESTful API规范

所有API响应统一格式：

**成功响应:**
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应:**
```json
{
  "success": false,
  "message": "错误信息",
  "code": "ERROR_CODE"
}
```

### API端点示例

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 病人管理 | GET | `/api/patient/patients` | 获取病人列表 |
| 病人管理 | POST | `/api/patient/patients` | 创建病人 |
| 医生管理 | GET | `/api/doctor/doctors` | 获取医生列表 |
| 药品管理 | GET | `/api/pharmacy/medicines` | 获取药品列表 |

---

## ⚙️ 配置说明

### 环境变量配置

复制 `env.template` 为 `.env` 并配置：

```env
# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=hospital_db

# Flask配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
```

---

## 🧪 测试

### 后端API测试

```bash
# 使用curl测试
curl http://localhost:5000/api/patient/patients

# 或使用Postman导入API集合进行测试
```

### 数据库测试

```bash
# 进入Python交互环境测试
python
>>> from app import create_app, db
>>> from models import Patient
>>> app = create_app()
>>> with app.app_context():
...     patients = Patient.query.all()
...     print(patients)
```

---

## 📊 系统截图

（待添加系统界面截图）

---

## 🔄 版本更新

### 当前版本: v2.0.0 (2025-10-11)

**重大更新:**
- ✅ 前后端分离架构
- ✅ 从SQLite迁移到MySQL
- ✅ 引入Vue.js前端框架
- ✅ 添加JWT认证支持
- ✅ RESTful API设计

> 📝 **完整变更历史请查看**: [CHANGELOG.md](CHANGELOG.md)

---

## 🎯 未来规划

### v2.1 (计划中)
- [ ] 完整的用户认证和权限管理
- [ ] Vue前端完整实现
- [ ] API文档（Swagger）
- [ ] 单元测试覆盖

### v3.0 (规划中)
- [ ] 微服务架构
- [ ] Redis缓存
- [ ] Docker容器化部署
- [ ] CI/CD集成

---

## ❓ 常见问题

### Q1: 如何重置数据库？
```bash
# 删除数据库并重新初始化
mysql -u root -p -e "DROP DATABASE hospital_db; CREATE DATABASE hospital_db;"
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### Q2: 如何添加新的子系统？
1. 在 `modules/` 下创建新模块目录
2. 定义蓝图并实现路由
3. 在 `app.py` 中注册蓝图
4. 在 `models.py` 中添加数据模型

### Q3: 前端如何调用API？
```javascript
// 使用axios调用API
import axios from 'axios'

axios.get('http://localhost:5000/api/patient/patients')
  .then(response => {
    console.log(response.data)
  })
```

---

## 🤝 贡献指南

### 代码规范
- Python代码遵循 PEP 8 规范
- Vue代码遵循 Vue.js 官方风格指南
- 提交信息遵循 Conventional Commits 规范

### 提交规范
```bash
feat(module): 新功能描述
fix(module): Bug修复描述
docs: 文档更新描述
style: 代码格式修改
refactor: 代码重构描述
test: 测试相关修改
```

---

## 📄 许可证

本项目仅供学习和教学使用。

---

## 👥 开发团队

- 开发者1: 病人管理子系统
- 开发者2: 医生管理子系统
- 开发者3: 药品管理子系统

---

## 📮 联系方式

如有问题或建议，请：
1. 查看文档: [INSTALLATION.md](INSTALLATION.md) | [DEVELOPMENT.md](DEVELOPMENT.md)
2. 提交Issue到项目仓库
3. 联系开发团队

---

<div align="center">

**医院综合管理系统 v2.0.0**

Made with ❤️ by Development Team

[文档](INSTALLATION.md) • [开发指南](DEVELOPMENT.md) • [更新日志](CHANGELOG.md)

</div>
