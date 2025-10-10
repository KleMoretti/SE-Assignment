# 项目架构说明文档

## 架构设计理念

本医院综合管理系统采用**模块化架构设计**，基于Flask的**蓝图（Blueprint）**机制，实现了三个相对独立的子系统。这种设计具有以下优势：

### 1. 模块化设计
- 每个子系统是一个独立的蓝图模块
- 降低模块间的耦合度
- 便于独立开发、测试和维护

### 2. 可扩展性
- 易于添加新的子系统
- 可以独立升级某个子系统
- 支持功能模块的插拔

### 3. 多人协作
- 三个开发者可以并行开发
- 减少代码冲突
- 清晰的职责划分

---

## 技术架构

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│                      浏览器客户端                          │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP请求
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   Flask Web应用层                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │              app.py (应用入口)                      │  │
│  │  - 应用工厂模式                                      │  │
│  │  - 蓝图注册                                         │  │
│  │  - 扩展初始化                                        │  │
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
│                   数据库层 (SQLite)                        │
│                   hospital.db                            │
└─────────────────────────────────────────────────────────┘
```

---

## 目录结构详解

```
SE-Assignment/
│
├── app.py                      # 应用主入口，应用工厂
│   - create_app(): 创建Flask应用实例
│   - 初始化数据库
│   - 注册蓝图
│   - 配置路由
│
├── config.py                   # 配置管理
│   - Config: 基础配置类
│   - DevelopmentConfig: 开发环境配置
│   - ProductionConfig: 生产环境配置
│
├── models.py                   # 数据库模型定义
│   - 所有数据表的ORM模型
│   - 定义表关系和约束
│
├── requirements.txt            # Python依赖包
│   - Flask 3.0.0
│   - Flask-SQLAlchemy 3.1.1
│   - Werkzeug 3.0.1
│
├── hospital.db                 # SQLite数据库文件（运行时生成）
│
├── modules/                    # 子系统模块目录
│   ├── __init__.py            # 模块包标识
│   │
│   ├── patient/               # 病人管理子系统
│   │   ├── __init__.py       # 蓝图定义和初始化
│   │   │   - patient_bp: 蓝图对象
│   │   │   - 路由前缀: /patient
│   │   │
│   │   └── routes.py         # 路由和视图函数
│   │       - 病人信息管理路由
│   │       - 病历记录管理路由
│   │       - 预约挂号管理路由
│   │
│   ├── doctor/                # 医生管理子系统
│   │   ├── __init__.py       # 蓝图定义和初始化
│   │   │   - doctor_bp: 蓝图对象
│   │   │   - 路由前缀: /doctor
│   │   │
│   │   └── routes.py         # 路由和视图函数
│   │       - 医生信息管理路由
│   │       - 医生排班管理路由
│   │       - 医生绩效评估路由
│   │
│   └── pharmacy/              # 药品管理子系统
│       ├── __init__.py       # 蓝图定义和初始化
│       │   - pharmacy_bp: 蓝图对象
│       │   - 路由前缀: /pharmacy
│       │
│       └── routes.py         # 路由和视图函数
│           - 药品信息管理路由
│           - 药品库存管理路由
│           - 药品采购管理路由
│
├── templates/                 # HTML模板目录
│   ├── base.html             # 基础模板（母版页）
│   │   - 导航栏
│   │   - 页脚
│   │   - 消息提示区域
│   │   - 公共CSS/JS引用
│   │
│   ├── index.html            # 系统首页
│   │   - 三个子系统的入口
│   │   - 系统介绍
│   │
│   ├── patient/              # 病人管理模板
│   │   ├── patient_index.html         # 病人管理首页
│   │   ├── patient_list.html          # 病人列表
│   │   ├── patient_form.html          # 病人表单（添加/编辑）
│   │   ├── patient_detail.html        # 病人详情
│   │   ├── medical_record_list.html   # 病历列表
│   │   ├── medical_record_form.html   # 病历表单
│   │   ├── medical_record_detail.html # 病历详情
│   │   ├── appointment_list.html      # 预约列表
│   │   └── appointment_form.html      # 预约表单
│   │
│   ├── doctor/               # 医生管理模板
│   │   ├── doctor_index.html          # 医生管理首页
│   │   ├── doctor_list.html           # 医生列表
│   │   ├── doctor_form.html           # 医生表单
│   │   ├── doctor_detail.html         # 医生详情
│   │   ├── schedule_list.html         # 排班列表
│   │   ├── schedule_form.html         # 排班表单
│   │   ├── performance_list.html      # 绩效列表
│   │   ├── performance_form.html      # 绩效表单
│   │   └── performance_detail.html    # 绩效详情
│   │
│   └── pharmacy/             # 药品管理模板
│       ├── pharmacy_index.html        # 药品管理首页
│       ├── medicine_list.html         # 药品列表
│       ├── medicine_form.html         # 药品表单
│       ├── medicine_detail.html       # 药品详情
│       ├── inventory_list.html        # 库存列表
│       ├── inventory_form.html        # 库存表单
│       ├── purchase_list.html         # 采购列表
│       ├── purchase_form.html         # 采购表单
│       └── purchase_detail.html       # 采购详情
│
└── static/                    # 静态资源目录
    ├── css/
    │   └── style.css         # 全局样式表
    │       - 导航栏样式
    │       - 表格样式
    │       - 表单样式
    │       - 按钮样式
    │       - 响应式设计
    │
    └── js/
        └── main.js           # JavaScript脚本
            - 消息自动隐藏
            - 表单验证
            - 交互增强
```

---

## 数据流向

### 1. 请求处理流程

```
用户请求 → Flask路由 → 蓝图路由 → 视图函数 → 数据库查询 → 模板渲染 → 响应返回
```

**示例：查看病人列表**

1. 用户访问: `http://localhost:5000/patient/patients`
2. Flask接收请求，匹配到 `patient` 蓝图
3. 调用 `modules/patient/routes.py` 中的 `patient_list()` 函数
4. 函数查询数据库: `Patient.query.all()`
5. 将数据传递给模板: `render_template('patient_list.html', patients=patients)`
6. Jinja2渲染HTML
7. 返回HTML给浏览器

### 2. 数据提交流程

```
表单提交 → POST请求 → 视图函数验证 → ORM模型创建 → 数据库写入 → 重定向/响应
```

**示例：添加病人**

1. 用户填写表单，点击提交
2. POST请求发送到: `/patient/patient/add`
3. `patient_add()` 函数接收数据
4. 创建 `Patient` 模型实例
5. `db.session.add(patient)` 添加到会话
6. `db.session.commit()` 提交到数据库
7. 重定向到列表页: `redirect(url_for('patient.patient_list'))`

---

## 蓝图机制详解

### 什么是蓝图？

蓝图（Blueprint）是Flask提供的模块化应用的方式，可以理解为应用的"子应用"或"模块"。

### 蓝图的优势

1. **模块化**: 将大型应用拆分为多个小模块
2. **可重用**: 蓝图可以在多个应用中注册使用
3. **独立开发**: 每个蓝图可以独立开发和测试
4. **URL前缀**: 自动添加URL前缀，避免路由冲突

### 蓝图的定义

**在 `modules/patient/__init__.py` 中**:

```python
from flask import Blueprint

# 创建蓝图对象
patient_bp = Blueprint(
    'patient',                              # 蓝图名称
    __name__,                               # 导入名称
    template_folder='../../templates/patient'  # 模板目录
)

# 导入路由（避免循环导入）
from . import routes
```

### 蓝图的注册

**在 `app.py` 中**:

```python
from modules.patient import patient_bp

app.register_blueprint(patient_bp, url_prefix='/patient')
# url_prefix: 所有该蓝图的路由都会加上 /patient 前缀
```

### 路由URL生成

使用 `url_for()` 生成URL时，需要指定蓝图名称：

```python
# 生成 /patient/patients 的URL
url_for('patient.patient_list')

# 生成 /doctor/doctors 的URL
url_for('doctor.doctor_list')

# 生成 /pharmacy/medicines 的URL
url_for('pharmacy.medicine_list')
```

---

## 数据库设计

### ER图（实体关系图）

```
┌─────────────┐         ┌─────────────┐
│   Patient   │         │   Doctor    │
│  (病人表)    │         │  (医生表)    │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │ 1:N                   │ 1:N
       ↓                       ↓
┌──────────────────────────────────────┐
│        MedicalRecord (病历表)         │
└──────────────────────────────────────┘

┌─────────────┐         ┌─────────────┐
│   Patient   │         │   Doctor    │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │ 1:N                   │ 1:N
       ↓                       ↓
┌──────────────────────────────────────┐
│        Appointment (预约表)           │
└──────────────────────────────────────┘

┌─────────────┐
│   Doctor    │
└──────┬──────┘
       │
       │ 1:N
       ↓
┌──────────────────────┐
│  DoctorSchedule      │
│  (医生排班表)         │
└──────────────────────┘

┌─────────────┐
│   Doctor    │
└──────┬──────┘
       │
       │ 1:N
       ↓
┌──────────────────────┐
│ DoctorPerformance    │
│ (医生绩效表)          │
└──────────────────────┘

┌─────────────┐
│  Medicine   │
│  (药品表)    │
└──────┬──────┘
       │
       │ 1:1
       ↓
┌──────────────────────┐
│ MedicineInventory    │
│ (药品库存表)          │
└──────────────────────┘

┌─────────────┐
│  Medicine   │
└──────┬──────┘
       │
       │ 1:N
       ↓
┌──────────────────────┐
│ MedicinePurchase     │
│ (药品采购表)          │
└──────────────────────┘
```

### 表关系说明

1. **Patient ↔ MedicalRecord**: 一对多
   - 一个病人可以有多条病历记录

2. **Patient ↔ Appointment**: 一对多
   - 一个病人可以有多个预约

3. **Doctor ↔ MedicalRecord**: 一对多
   - 一个医生可以诊治多个病人

4. **Doctor ↔ Appointment**: 一对多
   - 一个医生可以有多个预约

5. **Doctor ↔ DoctorSchedule**: 一对多
   - 一个医生可以有多个排班记录

6. **Doctor ↔ DoctorPerformance**: 一对多
   - 一个医生可以有多个绩效记录

7. **Medicine ↔ MedicineInventory**: 一对一
   - 一个药品对应一个库存记录

8. **Medicine ↔ MedicinePurchase**: 一对多
   - 一个药品可以有多个采购记录

---

## 扩展性设计

### 如何添加新的子系统？

假设要添加"财务管理子系统"：

1. **创建模块目录**
   ```bash
   mkdir modules/finance
   mkdir templates/finance
   ```

2. **定义蓝图** (`modules/finance/__init__.py`)
   ```python
   from flask import Blueprint
   
   finance_bp = Blueprint('finance', __name__, 
                         template_folder='../../templates/finance')
   
   from . import routes
   ```

3. **实现路由** (`modules/finance/routes.py`)
   ```python
   from . import finance_bp
   
   @finance_bp.route('/')
   def index():
       return render_template('finance_index.html')
   ```

4. **注册蓝图** (`app.py`)
   ```python
   from modules.finance import finance_bp
   app.register_blueprint(finance_bp, url_prefix='/finance')
   ```

5. **创建模板** (`templates/finance/finance_index.html`)

6. **定义数据模型** (`models.py`)

### 数据库迁移

当需要修改数据库结构时，建议使用Flask-Migrate：

```bash
pip install Flask-Migrate

# 初始化
flask db init

# 生成迁移脚本
flask db migrate -m "描述"

# 执行迁移
flask db upgrade
```

---

## 性能优化建议

1. **数据库查询优化**
   - 使用分页避免一次加载大量数据
   - 添加数据库索引
   - 使用 `lazy='dynamic'` 延迟加载关系

2. **缓存机制**
   - 使用Flask-Caching缓存频繁查询的数据
   - 缓存静态资源

3. **前端优化**
   - 压缩CSS和JavaScript
   - 使用CDN加载第三方库
   - 图片懒加载

---

## 安全性考虑

1. **输入验证**
   - 后端验证所有用户输入
   - 防止SQL注入（使用ORM）
   - 防止XSS攻击（模板自动转义）

2. **认证和授权**（待添加）
   - 用户登录系统
   - 基于角色的权限控制
   - 会话管理

3. **数据保护**
   - 敏感信息加密存储
   - HTTPS传输
   - 定期备份数据库

---

本架构文档提供了系统的整体设计思路和技术实现细节，帮助开发者快速理解项目结构和开发规范。

