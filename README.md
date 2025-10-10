# 医院综合管理系统

## 项目简介

医院综合管理系统是一个基于Flask框架开发的模块化管理系统，采用蓝图（Blueprint）架构设计，便于多人协作开发和维护。

## 系统架构

### 技术栈
- **后端框架**: Flask 3.0.0
- **数据库ORM**: Flask-SQLAlchemy 3.1.1
- **数据库**: SQLite（可扩展至MySQL/PostgreSQL）
- **模板引擎**: Jinja2
- **前端**: HTML5 + CSS3 + JavaScript

### 项目结构

```
hospital-management-system/
│
├── app.py                      # 主应用入口
├── config.py                   # 配置文件
├── models.py                   # 数据库模型
├── requirements.txt            # 依赖包列表
│
├── modules/                    # 子系统模块
│   ├── __init__.py
│   │
│   ├── patient/               # 病人管理子系统（开发者1）
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── doctor/                # 医生管理子系统（开发者2）
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   └── pharmacy/              # 药品管理子系统（开发者3）
│       ├── __init__.py
│       └── routes.py
│
├── templates/                  # 模板文件
│   ├── base.html              # 基础模板
│   ├── index.html             # 首页
│   │
│   ├── patient/               # 病人管理模板
│   │   ├── patient_index.html
│   │   ├── patient_list.html
│   │   ├── patient_form.html
│   │   └── ...
│   │
│   ├── doctor/                # 医生管理模板
│   │   ├── doctor_index.html
│   │   ├── doctor_list.html
│   │   └── ...
│   │
│   └── pharmacy/              # 药品管理模板
│       ├── pharmacy_index.html
│       ├── medicine_list.html
│       └── ...
│
└── static/                    # 静态文件
    ├── css/
    │   └── style.css          # 样式表
    └── js/
        └── main.js            # JavaScript脚本
```

## 子系统说明

### 1. 病人管理子系统（开发者1负责）

**功能模块**：
- **病人基本信息管理**
  - 添加、编辑、查询、删除病人信息
  - 病人信息包括：姓名、性别、年龄、联系方式、身份证号、住址等
  
- **病历记录管理**
  - 创建和查看病历记录
  - 记录诊断结果、症状、治疗方案、处方等
  
- **挂号预约管理**
  - 病人挂号预约
  - 预约状态管理（待确认、已确认、已完成、已取消）

**数据库模型**：
- `Patient`: 病人信息表
- `MedicalRecord`: 病历记录表
- `Appointment`: 预约挂号表

**路由前缀**: `/patient`

### 2. 医生管理子系统（开发者2负责）

**功能模块**：
- **医生信息管理**
  - 添加、编辑、查询、删除医生信息
  - 医生信息包括：姓名、科室、职称、专长、学历、入职日期等
  
- **医生排班管理**
  - 创建和编辑医生排班
  - 排班信息包括：日期、班次、工作时间、最大接诊数等
  
- **医生绩效评估**
  - 记录医生月度绩效
  - 绩效指标：接诊人数、满意度评分、出勤准时率、医疗质量评分等
  - 自动计算综合评分和绩效奖金

**数据库模型**：
- `Doctor`: 医生信息表
- `DoctorSchedule`: 医生排班表
- `DoctorPerformance`: 医生绩效表

**路由前缀**: `/doctor`

### 3. 药品管理子系统（开发者3负责）

**功能模块**：
- **药品信息管理**
  - 添加、编辑、查询、删除药品信息
  - 药品信息包括：名称、分类、规格、单价、生产厂家、用法用量等
  
- **药品库存管理**
  - 查看药品库存
  - 库存调整
  - 低库存预警（库存量低于最小库存警戒线）
  
- **药品采购管理**
  - 创建采购订单
  - 采购单管理（待收货、已收货、已完成）
  - 收货确认并自动更新库存

**数据库模型**：
- `Medicine`: 药品信息表
- `MedicineInventory`: 药品库存表
- `MedicinePurchase`: 药品采购表

**路由前缀**: `/pharmacy`

## 安装和运行

### 1. 环境准备

确保已安装Python 3.8或以上版本。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行系统

```bash
python app.py
```

系统将在 `http://localhost:5000` 启动。

### 4. 访问子系统

- 首页: http://localhost:5000/
- 病人管理: http://localhost:5000/patient
- 医生管理: http://localhost:5000/doctor
- 药品管理: http://localhost:5000/pharmacy

## 开发指南

### 多人协作开发

本系统采用模块化架构，三个子系统相对独立，适合三人分别开发：

#### 开发者1 - 病人管理子系统
- 主要工作目录: `modules/patient/`
- 模板目录: `templates/patient/`
- 数据库模型: `models.py` 中的 `Patient`, `MedicalRecord`, `Appointment`

#### 开发者2 - 医生管理子系统
- 主要工作目录: `modules/doctor/`
- 模板目录: `templates/doctor/`
- 数据库模型: `models.py` 中的 `Doctor`, `DoctorSchedule`, `DoctorPerformance`

#### 开发者3 - 药品管理子系统
- 主要工作目录: `modules/pharmacy/`
- 模板目录: `templates/pharmacy/`
- 数据库模型: `models.py` 中的 `Medicine`, `MedicineInventory`, `MedicinePurchase`

### 开发流程

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd hospital-management-system
   ```

2. **创建分支**（每个开发者创建自己的分支）
   ```bash
   git checkout -b feature/patient-system    # 开发者1
   git checkout -b feature/doctor-system     # 开发者2
   git checkout -b feature/pharmacy-system   # 开发者3
   ```

3. **独立开发**
   - 在各自的模块目录下进行开发
   - 遵循统一的代码规范和数据库模型定义

4. **测试**
   ```bash
   python app.py
   # 访问对应的子系统进行测试
   ```

5. **提交代码**
   ```bash
   git add .
   git commit -m "描述你的修改"
   git push origin feature/xxx-system
   ```

6. **合并代码**
   - 创建Pull Request
   - 代码审查后合并到主分支

### 添加新功能

#### 1. 添加路由

在对应子系统的 `routes.py` 中添加新路由：

```python
@subsystem_bp.route('/new-feature')
def new_feature():
    # 处理逻辑
    return render_template('new_feature.html')
```

#### 2. 添加模板

在对应的模板目录下创建HTML文件，继承 `base.html`:

```html
{% extends "base.html" %}

{% block title %}新功能{% endblock %}

{% block content %}
<!-- 你的内容 -->
{% endblock %}
```

#### 3. 修改数据库模型

如需添加或修改数据库表，编辑 `models.py` 文件。

## 数据库说明

### 初始化数据库

首次运行时，系统会自动创建 `hospital.db` 数据库文件和所有必要的表。

### 数据库关系

- `Patient` ↔ `MedicalRecord`: 一对多（一个病人有多条病历）
- `Patient` ↔ `Appointment`: 一对多（一个病人有多个预约）
- `Doctor` ↔ `MedicalRecord`: 一对多（一个医生诊治多个病人）
- `Doctor` ↔ `Appointment`: 一对多（一个医生有多个预约）
- `Doctor` ↔ `DoctorSchedule`: 一对多（一个医生有多个排班）
- `Doctor` ↔ `DoctorPerformance`: 一对多（一个医生有多个绩效记录）
- `Medicine` ↔ `MedicineInventory`: 一对一（一个药品对应一个库存记录）
- `Medicine` ↔ `MedicinePurchase`: 一对多（一个药品有多个采购记录）

## 注意事项

1. **代码规范**
   - 使用PEP 8编码规范
   - 函数和类添加必要的文档字符串
   - 变量命名清晰明确

2. **安全性**
   - 修改 `config.py` 中的 `SECRET_KEY`
   - 生产环境使用更安全的数据库（MySQL/PostgreSQL）
   - 添加用户认证和授权机制

3. **性能优化**
   - 数据库查询使用分页
   - 添加适当的索引
   - 使用缓存机制

4. **测试**
   - 在提交代码前进行充分测试
   - 测试各种边界情况
   - 确保与其他子系统的集成正常

## 扩展建议

1. **用户认证系统**
   - 添加用户登录、注册功能
   - 实现角色权限管理（管理员、医生、护士等）

2. **数据统计和报表**
   - 病人就诊统计
   - 医生工作量统计
   - 药品销售统计

3. **导出功能**
   - 导出Excel报表
   - 生成PDF文档

4. **消息通知**
   - 预约提醒
   - 库存预警通知
   - 邮件/短信通知

5. **API接口**
   - 提供RESTful API
   - 支持移动端调用

## 常见问题

### Q1: 如何修改数据库配置？
A: 编辑 `config.py` 文件中的 `SQLALCHEMY_DATABASE_URI` 配置项。

### Q2: 如何添加新的子系统？
A: 
1. 在 `modules/` 下创建新目录
2. 创建蓝图并定义路由
3. 在 `app.py` 中注册蓝图
4. 在 `models.py` 中添加数据库模型

### Q3: 如何重置数据库？
A: 删除 `hospital.db` 文件，重新运行 `python app.py` 即可。

## 版本信息

- 版本: v1.0.0
- 更新日期: 2024-10-10
- 开发团队: 三人协作开发

## 许可证

本项目仅供学习和教学使用。

## 联系方式

如有问题或建议，请联系开发团队。

