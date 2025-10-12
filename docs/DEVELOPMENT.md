# 医院综合管理系统 - 开发者指南

> 📚 **本指南面向系统开发者，提供完整的架构设计和开发规范**  
> 版本: v2.0.0 | 更新日期: 2025-10-11

---

## 📋 目录

- [项目架构](#项目架构)
- [技术栈详解](#技术栈详解)
- [项目结构](#项目结构)
- [多人协作开发](#多人协作开发)
- [开发规范](#开发规范)
- [数据库设计](#数据库设计)
- [API设计](#api设计)
- [开发工作流](#开发工作流)
- [测试指南](#测试指南)
- [性能优化](#性能优化)
- [扩展性设计](#扩展性设计)

---

## 项目架构

### 架构设计理念

本系统采用**模块化 + 前后端分离**的架构设计，具有以下优势：

#### 1. 模块化设计
- ✅ 每个子系统是一个独立的Flask蓝图模块
- ✅ 降低模块间的耦合度
- ✅ 便于独立开发、测试和维护
- ✅ 支持功能模块的插拔

#### 2. 前后端分离
- ✅ 后端提供RESTful API
- ✅ 前端独立开发和部署
- ✅ 提升开发效率和用户体验
- ✅ 支持多端访问（Web、移动端）

#### 3. 多人协作
- ✅ 三个开发者可以并行开发
- ✅ 减少代码冲突
- ✅ 清晰的职责划分
- ✅ 统一的开发规范

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    浏览器客户端 / 移动端                   │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/HTTPS (RESTful API)
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   Flask Web应用层                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │              app.py (应用工厂)                       │  │
│  │  - 应用工厂模式 (create_app)                         │  │
│  │  - 蓝图注册                                         │  │
│  │  - 扩展初始化 (db, cors, jwt)                       │  │
│  │  - 错误处理                                         │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 病人管理模块  │ │ 医生管理模块  │ │ 药品管理模块  │
│   Patient    │ │   Doctor     │ │  Pharmacy    │
│   Blueprint  │ │   Blueprint  │ │  Blueprint   │
│              │ │              │ │              │
│ routes.py    │ │ routes.py    │ │ routes.py    │
│ - API路由    │ │ - API路由    │ │ - API路由    │
│ - 业务逻辑   │ │ - 业务逻辑   │ │ - 业务逻辑   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   数据访问层 (ORM)                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Flask-SQLAlchemy (models.py)            │  │
│  │  - Patient, MedicalRecord, Appointment           │  │
│  │  - Doctor, DoctorSchedule, DoctorPerformance     │  │
│  │  - Medicine, MedicineInventory, MedicinePurchase │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   数据库层 (MySQL 8.0)                     │
│                     hospital_db                          │
└─────────────────────────────────────────────────────────┘
```

### 请求处理流程

```
用户请求
    ↓
Flask路由匹配
    ↓
蓝图路由分发
    ↓
视图函数处理
    ↓
业务逻辑执行
    ↓
数据库查询/更新 (ORM)
    ↓
JSON响应返回
    ↓
客户端接收
```

**具体示例 - 获取病人列表:**

1. 前端发起请求: `GET /api/patient/patients?page=1&per_page=10`
2. Flask接收并路由到 `patient` 蓝图
3. 调用 `modules/patient/routes.py` 中的视图函数
4. 执行 `Patient.query.paginate(page=1, per_page=10)`
5. ORM转换为SQL查询: `SELECT * FROM patients LIMIT 10 OFFSET 0`
6. 获取结果并转换为字典: `[p.to_dict() for p in patients]`
7. 返回JSON响应: `{"success": true, "data": {...}}`
8. 前端接收并渲染数据

---

## 技术栈详解

### 后端技术栈

#### Flask 3.0.0 - Web框架
- **选择理由**: 轻量级、灵活、易学
- **核心特性**: 蓝图机制、模板引擎、路由系统
- **适用场景**: 中小型Web应用、API服务

#### Flask-SQLAlchemy 3.1.1 - ORM
- **选择理由**: Python最流行的ORM
- **核心特性**: 对象关系映射、查询构建器、数据库迁移
- **优势**: 避免SQL注入、简化数据库操作

#### MySQL 8.0+ - 数据库
- **选择理由**: 企业级、高性能、开源
- **核心特性**: ACID事务、索引优化、复制机制
- **字符集**: utf8mb4（支持emoji）

#### Flask-JWT-Extended - JWT认证
- **选择理由**: 无状态认证、适合RESTful API
- **核心特性**: Access Token、Refresh Token
- **安全性**: Token签名、过期验证

#### Flask-CORS - 跨域支持
- **选择理由**: 前后端分离必需
- **核心特性**: 自动添加CORS头
- **配置灵活**: 支持自定义域名白名单

### 前端技术栈

#### Vue.js 3.x - 前端框架
- **选择理由**: 渐进式、易学、生态丰富
- **核心特性**: 响应式、组件化、虚拟DOM
- **Composition API**: 更好的代码组织

#### Element Plus - UI组件库
- **选择理由**: 企业级、组件丰富
- **核心组件**: Table、Form、Dialog、Message
- **主题定制**: 支持自定义主题

#### Pinia - 状态管理
- **选择理由**: Vue 3官方推荐
- **优势**: 类型安全、开发工具支持
- **API简洁**: 比Vuex更简单

#### Axios - HTTP客户端
- **选择理由**: Promise支持、拦截器
- **核心特性**: 请求/响应拦截、错误处理
- **封装统一**: 统一API调用方式

---

## 项目结构

### 完整目录结构

```
hospital-management-system/
│
├── app.py                      # 🚀 应用主入口
│   ├── create_app()           # 应用工厂函数
│   ├── 初始化数据库            # db.init_app(app)
│   ├── 注册蓝图               # app.register_blueprint()
│   ├── 错误处理               # @app.errorhandler()
│   └── 启动配置               # app.run()
│
├── config.py                   # ⚙️ 配置管理
│   ├── Config                 # 基础配置类
│   ├── DevelopmentConfig      # 开发环境配置
│   ├── ProductionConfig       # 生产环境配置
│   └── 环境变量读取           # os.getenv()
│
├── models.py                   # 🗄️ 数据库模型定义
│   ├── Patient                # 病人模型
│   ├── MedicalRecord          # 病历模型
│   ├── Appointment            # 预约模型
│   ├── Doctor                 # 医生模型
│   ├── DoctorSchedule         # 排班模型
│   ├── DoctorPerformance      # 绩效模型
│   ├── Medicine               # 药品模型
│   ├── MedicineInventory      # 库存模型
│   └── MedicinePurchase       # 采购模型
│
├── requirements.txt            # 📦 Python依赖包列表
├── init_database.sql           # 🗄️ 数据库初始化脚本
├── env.template                # 📝 环境变量模板
├── .env                        # 🔐 环境变量（不提交到Git）
├── .gitignore                  # 🚫 Git忽略文件
│
├── modules/                    # 📂 子系统模块目录
│   ├── __init__.py            # 模块包标识
│   │
│   ├── patient/               # 🏥 病人管理子系统
│   │   ├── __init__.py       # 蓝图定义
│   │   │   └── patient_bp    # 蓝图对象（路由前缀: /api/patient）
│   │   │
│   │   └── routes.py         # 路由和视图函数
│   │       ├── 病人CRUD       # 增删改查
│   │       ├── 病历管理       # 病历记录
│   │       └── 预约管理       # 预约挂号
│   │
│   ├── doctor/                # 👨‍⚕️ 医生管理子系统
│   │   ├── __init__.py       # 蓝图定义
│   │   │   └── doctor_bp     # 蓝图对象（路由前缀: /api/doctor）
│   │   │
│   │   └── routes.py         # 路由和视图函数
│   │       ├── 医生CRUD       # 增删改查
│   │       ├── 排班管理       # 医生排班
│   │       └── 绩效管理       # 绩效评估
│   │
│   └── pharmacy/              # 💊 药品管理子系统
│       ├── __init__.py       # 蓝图定义
│       │   └── pharmacy_bp   # 蓝图对象（路由前缀: /api/pharmacy）
│       │
│       └── routes.py         # 路由和视图函数
│           ├── 药品CRUD       # 增删改查
│           ├── 库存管理       # 库存查询、调整
│           └── 采购管理       # 采购单管理
│
├── templates/                  # 📄 HTML模板目录（可选，API模式不需要）
│   ├── base.html              # 基础模板
│   ├── index.html             # 首页
│   ├── patient/               # 病人管理模板
│   ├── doctor/                # 医生管理模板
│   └── pharmacy/              # 药品管理模板
│
├── static/                     # 🎨 静态资源目录（可选）
│   ├── css/
│   │   └── style.css          # 全局样式
│   └── js/
│       └── main.js            # JavaScript脚本
│
├── docs/                       # 📚 文档目录
│   ├── README.md              # 项目说明
│   ├── INSTALLATION.md        # 安装指南
│   ├── DEVELOPMENT.md         # 开发指南（本文档）
│   └── CHANGELOG.md           # 变更日志
│
└── tests/                      # 🧪 测试目录（待实现）
    ├── test_patient.py
    ├── test_doctor.py
    └── test_pharmacy.py
```

### 核心文件说明

#### app.py - 应用入口

```python
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    jwt.init_app(app)
    
    # 注册蓝图
    from modules.patient import patient_bp
    from modules.doctor import doctor_bp
    from modules.pharmacy import pharmacy_bp
    
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(pharmacy_bp, url_prefix='/api/pharmacy')
    
    # 健康检查
    @app.route('/')
    def index():
        return jsonify({
            'status': 'success',
            'message': '医院综合管理系统API运行正常',
            'version': app.config['VERSION']
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

#### models.py - 数据模型示例

```python
from datetime import datetime
from typing import Dict
from app import db

class Patient(db.Model):
    """病人模型"""
    __tablename__ = 'patients'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='病人ID')
    
    # 基本信息
    name = db.Column(db.String(50), nullable=False, index=True, comment='姓名')
    gender = db.Column(db.String(10), comment='性别')
    age = db.Column(db.Integer, comment='年龄')
    phone = db.Column(db.String(20), unique=True, index=True, comment='手机号')
    id_card = db.Column(db.String(18), unique=True, comment='身份证号')
    address = db.Column(db.String(200), comment='地址')
    
    # 时间戳
    created_at = db.Column(db.DateTime, nullable=False, 
                          default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    medical_records = db.relationship('MedicalRecord', backref='patient',
                                     lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'id_card': self.id_card,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

---

## 多人协作开发

### 开发分工

#### 👤 开发者1 - 病人管理子系统

**工作目录:**
- `modules/patient/`
- `templates/patient/` (如果需要)

**核心功能:**
1. ✅ 病人基本信息管理（CRUD）
2. ✅ 病历记录管理
3. ✅ 预约挂号管理

**数据库表:**
- `patients` - 病人信息表
- `medical_records` - 病历记录表
- `appointments` - 预约挂号表

**API端点:**
```
GET    /api/patient/patients              # 获取病人列表
POST   /api/patient/patients              # 创建病人
GET    /api/patient/patients/:id          # 获取病人详情
PUT    /api/patient/patients/:id          # 更新病人信息
DELETE /api/patient/patients/:id          # 删除病人

GET    /api/patient/medical-records       # 获取病历列表
POST   /api/patient/medical-records       # 创建病历
GET    /api/patient/medical-records/:id   # 获取病历详情

GET    /api/patient/appointments          # 获取预约列表
POST   /api/patient/appointments          # 创建预约
PUT    /api/patient/appointments/:id      # 更新预约状态
DELETE /api/patient/appointments/:id      # 取消预约
```

#### 👤 开发者2 - 医生管理子系统

**工作目录:**
- `modules/doctor/`
- `templates/doctor/` (如果需要)

**核心功能:**
1. ✅ 医生信息管理（CRUD）
2. ✅ 医生排班管理
3. ✅ 医生绩效评估

**数据库表:**
- `doctors` - 医生信息表
- `doctor_schedules` - 医生排班表
- `doctor_performances` - 医生绩效表

**API端点:**
```
GET    /api/doctor/doctors                # 获取医生列表
POST   /api/doctor/doctors                # 创建医生
GET    /api/doctor/doctors/:id            # 获取医生详情
PUT    /api/doctor/doctors/:id            # 更新医生信息
DELETE /api/doctor/doctors/:id            # 删除医生

GET    /api/doctor/schedules              # 获取排班列表
POST   /api/doctor/schedules              # 创建排班
PUT    /api/doctor/schedules/:id          # 更新排班
DELETE /api/doctor/schedules/:id          # 删除排班

GET    /api/doctor/performances           # 获取绩效列表
POST   /api/doctor/performances           # 创建绩效记录
GET    /api/doctor/performances/:id       # 获取绩效详情
```

#### 👤 开发者3 - 药品管理子系统

**工作目录:**
- `modules/pharmacy/`
- `templates/pharmacy/` (如果需要)

**核心功能:**
1. ✅ 药品信息管理（CRUD）
2. ✅ 药品库存管理（库存预警）
3. ✅ 药品采购管理

**数据库表:**
- `medicines` - 药品信息表
- `medicine_inventory` - 药品库存表
- `medicine_purchases` - 药品采购表

**API端点:**
```
GET    /api/pharmacy/medicines            # 获取药品列表
POST   /api/pharmacy/medicines            # 创建药品
GET    /api/pharmacy/medicines/:id        # 获取药品详情
PUT    /api/pharmacy/medicines/:id        # 更新药品信息
DELETE /api/pharmacy/medicines/:id        # 删除药品

GET    /api/pharmacy/inventory            # 获取库存列表
PUT    /api/pharmacy/inventory/:id        # 调整库存
GET    /api/pharmacy/inventory/low-stock  # 获取低库存预警

GET    /api/pharmacy/purchases            # 获取采购列表
POST   /api/pharmacy/purchases            # 创建采购单
GET    /api/pharmacy/purchases/:id        # 获取采购详情
POST   /api/pharmacy/purchases/:id/receive # 确认收货
```

### 协作流程

#### 1. 初始设置

```bash
# 克隆项目
git clone <repository-url>
cd hospital-management-system

# 安装依赖
pip install -r requirements.txt

# 配置数据库
cp env.template .env
# 编辑.env配置MySQL信息
```

#### 2. 创建开发分支

```bash
# 开发者1
git checkout -b feature/patient-system

# 开发者2
git checkout -b feature/doctor-system

# 开发者3
git checkout -b feature/pharmacy-system
```

#### 3. 开发步骤

1. **熟悉数据库模型**
   - 查看 `models.py` 中对应的模型
   - 理解表结构和关系

2. **实现API路由**
   ```python
   # modules/patient/routes.py
   from . import patient_bp
   from models import Patient
   from app import db
   from flask import request, jsonify
   
   @patient_bp.route('/patients', methods=['GET'])
   def get_patients():
       page = request.args.get('page', 1, type=int)
       per_page = request.args.get('per_page', 10, type=int)
       
       pagination = Patient.query.paginate(
           page=page, per_page=per_page, error_out=False
       )
       
       return jsonify({
           'success': True,
           'data': {
               'items': [p.to_dict() for p in pagination.items],
               'total': pagination.total,
               'page': pagination.page,
               'pages': pagination.pages
           }
       })
   ```

3. **测试功能**
   ```bash
   # 启动服务
   python app.py
   
   # 使用curl测试
   curl http://localhost:5000/api/patient/patients
   ```

4. **提交代码**
   ```bash
   git add modules/patient/
   git commit -m "feat(patient): 实现病人列表查询API"
   git push origin feature/patient-system
   ```

5. **创建Pull Request**
   - 在Git平台创建PR
   - 请求团队成员代码审查
   - 审查通过后合并

#### 4. 定期同步

```bash
# 获取主分支最新代码
git checkout main
git pull origin main

# 合并到自己的分支
git checkout feature/your-system
git merge main

# 解决冲突（如有）
# 测试确保功能正常
```

---

## 开发规范

### 代码规范

#### Python代码规范（PEP 8）

**命名规范:**
```python
# 模块名：小写+下划线
patient_routes.py

# 类名：大驼峰
class PatientService:
    pass

# 函数名：小写+下划线
def get_patient_list():
    pass

# 变量名：小写+下划线
patient_count = 0
is_active = True

# 常量：大写+下划线
MAX_PAGE_SIZE = 100
```

**文档字符串:**
```python
def create_patient(name: str, age: int, gender: str) -> Dict:
    """创建新病人
    
    Args:
        name: 病人姓名
        age: 年龄
        gender: 性别
        
    Returns:
        病人信息字典
        
    Raises:
        ValueError: 参数验证失败
    """
    pass
```

**类型提示:**
```python
from typing import List, Dict, Optional

def get_patients(page: int = 1, per_page: int = 10) -> List[Dict]:
    """获取病人列表"""
    pass
```

#### Vue.js代码规范

**组件命名:**
```javascript
// 文件名：大驼峰
PatientList.vue
PatientForm.vue

// 组件使用
<PatientList />
<patient-list />  // kebab-case也可以
```

**变量命名:**
```javascript
// 小驼峰
const patientList = ref([])
const isLoading = ref(false)

// 常量：大写+下划线
const MAX_PAGE_SIZE = 100
```

**组件结构:**
```vue
<script setup>
// 1. 导入依赖
import { ref, onMounted } from 'vue'

// 2. 定义props和emits
const props = defineProps({
  title: String
})

const emit = defineEmits(['update'])

// 3. 响应式数据
const data = ref([])

// 4. 计算属性
const count = computed(() => data.value.length)

// 5. 方法
function fetchData() {
  // ...
}

// 6. 生命周期
onMounted(() => {
  fetchData()
})
</script>

<template>
  <!-- 模板内容 -->
</template>

<style scoped>
/* 样式 */
</style>
```

### API设计规范

#### RESTful API约定

**HTTP方法:**
- `GET` - 获取资源
- `POST` - 创建资源
- `PUT` - 更新资源（完整更新）
- `PATCH` - 更新资源（部分更新）
- `DELETE` - 删除资源

**URL设计:**
```
# 获取资源列表
GET /api/patient/patients

# 获取单个资源
GET /api/patient/patients/1

# 创建资源
POST /api/patient/patients

# 更新资源
PUT /api/patient/patients/1

# 删除资源
DELETE /api/patient/patients/1

# 资源的子资源
GET /api/patient/patients/1/medical-records
```

**响应格式:**

成功响应：
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "张三",
    "age": 30
  },
  "message": "操作成功"
}
```

错误响应：
```json
{
  "success": false,
  "message": "病人不存在",
  "code": "PATIENT_NOT_FOUND"
}
```

列表响应：
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "per_page": 10,
    "pages": 10
  }
}
```

**HTTP状态码:**
- `200 OK` - 成功
- `201 Created` - 创建成功
- `204 No Content` - 删除成功
- `400 Bad Request` - 请求参数错误
- `401 Unauthorized` - 未认证
- `403 Forbidden` - 无权限
- `404 Not Found` - 资源不存在
- `500 Internal Server Error` - 服务器错误

### Git提交规范

**Conventional Commits格式:**
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Type类型:**
- `feat` - 新功能
- `fix` - Bug修复
- `docs` - 文档更新
- `style` - 代码格式（不影响功能）
- `refactor` - 代码重构
- `perf` - 性能优化
- `test` - 测试相关
- `chore` - 构建/工具相关

**示例:**
```bash
git commit -m "feat(patient): 添加病人列表分页功能"
git commit -m "fix(doctor): 修复排班时间冲突问题"
git commit -m "docs: 更新API文档"
git commit -m "refactor(pharmacy): 重构库存管理逻辑"
```

---

## 数据库设计

### ER图（实体关系图）

```
┌─────────────┐         ┌─────────────┐
│   Patient   │         │   Doctor    │
│   (病人)     │         │   (医生)     │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │ 1:N                   │ 1:N
       ↓                       ↓
┌──────────────────────────────────────┐
│        MedicalRecord (病历)           │
└──────────────────────────────────────┘

┌─────────────┐         ┌─────────────┐
│   Patient   │         │   Doctor    │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │ 1:N                   │ 1:N
       ↓                       ↓
┌──────────────────────────────────────┐
│        Appointment (预约)             │
└──────────────────────────────────────┘

┌─────────────┐
│   Doctor    │
└──────┬──────┘
       │ 1:N
       ↓
┌──────────────────────┐
│  DoctorSchedule      │
│  (排班)               │
└──────────────────────┘

┌─────────────┐
│   Doctor    │
└──────┬──────┘
       │ 1:N
       ↓
┌──────────────────────┐
│ DoctorPerformance    │
│ (绩效)                │
└──────────────────────┘

┌─────────────┐
│  Medicine   │
│  (药品)      │
└──────┬──────┘
       │ 1:1
       ↓
┌──────────────────────┐
│ MedicineInventory    │
│ (库存)                │
└──────────────────────┘

┌─────────────┐
│  Medicine   │
└──────┬──────┘
       │ 1:N
       ↓
┌──────────────────────┐
│ MedicinePurchase     │
│ (采购)                │
└──────────────────────┘
```

### 表设计规范

**字段设计:**
- 主键：`INT UNSIGNED AUTO_INCREMENT`
- 字符串：`VARCHAR(length)`，长度根据实际需求
- 文本：`TEXT` 或 `LONGTEXT`
- 整数：`INT` 或 `BIGINT`
- 小数：`DECIMAL(10, 2)`
- 日期时间：`DATETIME`
- 布尔：`TINYINT(1)`

**索引设计:**
- 主键自动创建索引
- 外键字段创建索引
- 常用查询字段创建索引
- 唯一约束字段创建唯一索引

**命名规范:**
- 表名：小写+下划线+复数（如`patients`）
- 字段名：小写+下划线（如`created_at`）
- 索引名：`idx_表名_字段名`
- 唯一索引：`uk_表名_字段名`
- 外键：`fk_表名_字段名`

---

## API设计

### 蓝图机制

**什么是蓝图？**
- Flask的模块化机制
- 类似于应用的"子应用"
- 可以独立开发和测试

**蓝图定义:**
```python
# modules/patient/__init__.py
from flask import Blueprint

patient_bp = Blueprint(
    'patient',                 # 蓝图名称
    __name__,                  # 导入名称
    url_prefix='/api/patient'  # URL前缀
)

from . import routes  # 导入路由
```

**蓝图注册:**
```python
# app.py
from modules.patient import patient_bp

app.register_blueprint(patient_bp)
```

**URL生成:**
```python
# 在代码中生成URL
url_for('patient.get_patients')  # /api/patient/patients
url_for('doctor.get_doctors')    # /api/doctor/doctors
```

### 路由实现示例

```python
# modules/patient/routes.py
from . import patient_bp
from models import Patient, db
from flask import request, jsonify

@patient_bp.route('/patients', methods=['GET'])
def get_patients():
    """获取病人列表"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        search = request.args.get('search', '')
        
        # 构建查询
        query = Patient.query
        if search:
            query = query.filter(Patient.name.like(f'%{search}%'))
        
        # 分页查询
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 返回响应
        return jsonify({
            'success': True,
            'data': {
                'items': [p.to_dict() for p in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@patient_bp.route('/patients', methods=['POST'])
def create_patient():
    """创建病人"""
    try:
        data = request.get_json()
        
        # 参数验证
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'message': '姓名不能为空'
            }), 400
        
        # 创建病人
        patient = Patient(
            name=data['name'],
            gender=data.get('gender'),
            age=data.get('age'),
            phone=data.get('phone'),
            address=data.get('address')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': patient.to_dict(),
            'message': '创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@patient_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """获取病人详情"""
    patient = Patient.query.get_or_404(patient_id)
    return jsonify({
        'success': True,
        'data': patient.to_dict()
    }), 200

@patient_bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """更新病人信息"""
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    
    # 更新字段
    for key in ['name', 'gender', 'age', 'phone', 'address']:
        if key in data:
            setattr(patient, key, data[key])
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'data': patient.to_dict(),
            'message': '更新成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@patient_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """删除病人"""
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        db.session.delete(patient)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '删除成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
```

---

## 开发工作流

### 日常开发流程

```bash
# 1. 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 2. 确保代码最新
git pull origin main

# 3. 切换到开发分支
git checkout feature/your-module

# 4. 开发...

# 5. 测试
python app.py

# 6. 提交代码
git add .
git commit -m "feat: description"
git push origin feature/your-module
```

### 调试技巧

#### 1. 使用print调试
```python
@patient_bp.route('/test')
def test():
    data = request.get_json()
    print(f"接收到的数据: {data}")  # 会在终端输出
    return jsonify({'message': 'OK'})
```

#### 2. 使用Flask-DebugToolbar
```bash
pip install flask-debugtoolbar
```

```python
from flask_debugtoolbar import DebugToolbarExtension

app.config['DEBUG_TB_ENABLED'] = True
toolbar = DebugToolbarExtension(app)
```

#### 3. 查看SQL查询
```python
# 在开发环境启用SQL日志
app.config['SQLALCHEMY_ECHO'] = True
```

#### 4. 使用Python交互环境
```python
python
>>> from app import create_app, db
>>> from models import Patient
>>> app = create_app()
>>> with app.app_context():
...     patients = Patient.query.all()
...     for p in patients:
...         print(p.name)
```

---

## 测试指南

### 单元测试

```python
# tests/test_patient.py
import unittest
from app import create_app, db
from models import Patient

class PatientTestCase(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_patient(self):
        """测试创建病人"""
        response = self.client.post('/api/patient/patients', json={
            'name': '测试病人',
            'age': 30,
            'gender': '男'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], '测试病人')
    
    def test_get_patients(self):
        """测试获取病人列表"""
        response = self.client.get('/api/patient/patients')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('items', data['data'])

if __name__ == '__main__':
    unittest.main()
```

### API测试

使用Postman或curl进行API测试：

```bash
# 测试创建病人
curl -X POST http://localhost:5000/api/patient/patients \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","age":30,"gender":"男"}'

# 测试获取列表
curl http://localhost:5000/api/patient/patients?page=1&per_page=10
```

---

## 性能优化

### 数据库优化

1. **使用分页**
```python
# 避免一次加载所有数据
pagination = Patient.query.paginate(page=1, per_page=10)
```

2. **添加索引**
```python
# 在常用查询字段上创建索引
name = db.Column(db.String(50), index=True)
```

3. **预加载关系**
```python
# 避免N+1查询问题
patients = Patient.query.options(
    db.joinedload(Patient.medical_records)
).all()
```

### 缓存优化

使用Flask-Caching：

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@cache.cached(timeout=300)
@patient_bp.route('/patients')
def get_patients():
    # 缓存5分钟
    pass
```

---

## 扩展性设计

### 添加新子系统

1. **创建模块目录**
```bash
mkdir modules/billing
```

2. **定义蓝图**
```python
# modules/billing/__init__.py
from flask import Blueprint

billing_bp = Blueprint('billing', __name__)

from . import routes
```

3. **实现路由**
```python
# modules/billing/routes.py
from . import billing_bp

@billing_bp.route('/bills')
def get_bills():
    return {'message': 'billing system'}
```

4. **注册蓝图**
```python
# app.py
from modules.billing import billing_bp
app.register_blueprint(billing_bp, url_prefix='/api/billing')
```

---

## 常见问题解答

### Q1: 如何处理数据库迁移？

使用Flask-Migrate：
```bash
pip install Flask-Migrate

# 初始化
flask db init

# 生成迁移脚本
flask db migrate -m "描述"

# 执行迁移
flask db upgrade
```

### Q2: 如何实现用户认证？

使用Flask-JWT-Extended：
```python
from flask_jwt_extended import create_access_token, jwt_required

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # 验证用户
    if validate_user(username, password):
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@patient_bp.route('/patients')
@jwt_required()
def get_patients():
    # 需要认证才能访问
    pass
```

### Q3: 如何处理文件上传？

```python
from werkzeug.utils import secure_filename

@patient_bp.route('/patients/<int:id>/avatar', methods=['POST'])
def upload_avatar(id):
    if 'file' not in request.files:
        return jsonify({'message': 'No file'}), 400
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(f'uploads/{filename}')
    
    return jsonify({'filename': filename})
```

---

## 资源链接

### 官方文档
- [Flask文档](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy文档](https://flask-sqlalchemy.palletsprojects.com/)
- [Vue.js文档](https://cn.vuejs.org/)
- [Element Plus文档](https://element-plus.org/)

### 学习资源
- [Python PEP 8规范](https://pep8.org/)
- [RESTful API设计指南](https://restfulapi.net/)
- [Git提交规范](https://www.conventionalcommits.org/)

---

**文档版本**: v2.0  
**最后更新**: 2025-10-11  
**维护团队**: 医院管理系统开发组

---

<div align="center">

开发愉快！有问题请查看[安装指南](INSTALLATION.md)或提交Issue

[返回README](README.md) • [安装指南](INSTALLATION.md) • [更新日志](CHANGELOG.md)

</div>

