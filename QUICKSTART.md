# 快速开始指南

## 5分钟快速上手

### 1. 环境要求

- Python 3.8 或以上版本
- pip 包管理工具

### 2. 安装步骤

#### 步骤1：克隆或下载项目

```bash
# 如果使用Git
git clone <repository-url>
cd SE-Assignment

# 或者直接下载ZIP并解压
```

#### 步骤2：安装依赖

```bash
pip install -r requirements.txt
```

**依赖包说明**：
- Flask 3.0.0 - Web框架
- Flask-SQLAlchemy 3.1.1 - 数据库ORM
- Werkzeug 3.0.1 - WSGI工具库

#### 步骤3：运行系统

```bash
python app.py
```

**运行成功后会看到**：
```
============================================================
医院综合管理系统已启动
系统模块：
  - 病人管理系统: http://localhost:5000/patient
  - 医生管理系统: http://localhost:5000/doctor
  - 药品管理系统: http://localhost:5000/pharmacy
============================================================
 * Running on http://127.0.0.1:5000
```

#### 步骤4：访问系统

打开浏览器，访问：
- **系统首页**: http://localhost:5000/
- **病人管理**: http://localhost:5000/patient
- **医生管理**: http://localhost:5000/doctor
- **药品管理**: http://localhost:5000/pharmacy

---

## 快速测试功能

### 测试病人管理系统

1. 访问 http://localhost:5000/patient
2. 点击"病人列表"
3. 点击"添加病人"按钮
4. 填写病人信息：
   - 病人编号: P001
   - 姓名: 张三
   - 性别: 男
   - 年龄: 30
   - 联系电话: 13800138000
5. 点击"保存"
6. 查看病人列表，确认添加成功

### 测试医生管理系统

1. 访问 http://localhost:5000/doctor
2. 点击"医生列表"
3. 点击"添加医生"按钮
4. 填写医生信息：
   - 医生编号: D001
   - 姓名: 李医生
   - 性别: 女
   - 科室: 内科
   - 职称: 主任医师
5. 点击"保存"
6. 查看医生列表，确认添加成功

### 测试药品管理系统

1. 访问 http://localhost:5000/pharmacy
2. 点击"药品列表"
3. 点击"添加药品"按钮
4. 填写药品信息：
   - 药品编号: M001
   - 药品名称: 阿莫西林
   - 分类: 抗生素
   - 规格: 0.25g*24片
   - 单价: 15.50
   - 生产厂家: XX制药
5. 点击"保存"
6. 查看药品列表和库存，确认添加成功

---

## 项目结构一览

```
SE-Assignment/
├── app.py              # 主程序入口
├── config.py           # 配置文件
├── models.py           # 数据库模型
├── requirements.txt    # 依赖包
├── modules/            # 三个子系统模块
│   ├── patient/       # 病人管理（开发者1）
│   ├── doctor/        # 医生管理（开发者2）
│   └── pharmacy/      # 药品管理（开发者3）
├── templates/          # HTML模板
└── static/            # CSS和JS
```

---

## 三人协作分工

### 🏥 开发者1 - 病人管理子系统
**工作目录**: `modules/patient/` 和 `templates/patient/`

**主要功能**:
- ✅ 病人信息管理（已完成路由）
- ✅ 病历记录管理（已完成路由）
- ✅ 挂号预约管理（已完成路由）

**需完成的模板**:
- patient_detail.html
- medical_record_list.html
- medical_record_form.html
- medical_record_detail.html
- appointment_list.html
- appointment_form.html

---

### 👨‍⚕️ 开发者2 - 医生管理子系统
**工作目录**: `modules/doctor/` 和 `templates/doctor/`

**主要功能**:
- ✅ 医生信息管理（已完成路由）
- ✅ 医生排班管理（已完成路由）
- ✅ 医生绩效评估（已完成路由）

**需完成的模板**:
- doctor_form.html
- doctor_detail.html
- schedule_list.html
- schedule_form.html
- performance_list.html
- performance_form.html
- performance_detail.html

---

### 💊 开发者3 - 药品管理子系统
**工作目录**: `modules/pharmacy/` 和 `templates/pharmacy/`

**主要功能**:
- ✅ 药品信息管理（已完成路由）
- ✅ 药品库存管理（已完成路由）
- ✅ 药品采购管理（已完成路由）

**需完成的模板**:
- medicine_form.html
- medicine_detail.html
- inventory_list.html
- inventory_form.html
- purchase_list.html
- purchase_form.html
- purchase_detail.html

---

## 开发步骤建议

### 第一阶段：熟悉项目（1天）
1. 阅读 README.md 了解项目整体
2. 阅读 PROJECT_STRUCTURE.md 理解架构
3. 运行项目，测试现有功能
4. 查看数据库模型 models.py

### 第二阶段：实现基础功能（2-3天）
1. 完成列表页面（List）
2. 完成添加/编辑表单（Form）
3. 完成详情页面（Detail）
4. 测试CRUD操作

### 第三阶段：完善功能（1-2天）
1. 添加搜索功能
2. 添加筛选功能
3. 优化页面样式
4. 添加数据验证

### 第四阶段：集成测试（1天）
1. 测试各个子系统功能
2. 测试子系统间的数据关联
3. 修复bug
4. 优化用户体验

---

## 常用命令

### 运行项目
```bash
python app.py
```

### 停止项目
按 `Ctrl + C`

### 重置数据库
```bash
# Windows
del hospital.db
python app.py

# Mac/Linux
rm hospital.db
python app.py
```

### 查看Python版本
```bash
python --version
```

### 查看已安装的包
```bash
pip list
```

---

## 获取帮助

### 文档资源
- **README.md** - 项目总体介绍
- **PROJECT_STRUCTURE.md** - 架构详解
- **DEVELOPMENT_GUIDE.md** - 开发指南（必读！）
- **QUICKSTART.md** - 本文档

### 学习资源
- [Flask官方文档](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy文档](https://flask-sqlalchemy.palletsprojects.com/)
- [Jinja2模板文档](https://jinja.palletsprojects.com/)

### 遇到问题？
1. 查看控制台错误信息
2. 检查浏览器开发者工具
3. 阅读相关文档
4. 与团队成员讨论

---

## 小贴士

### 💡 提示1：数据库自动创建
首次运行 `app.py` 时，系统会自动创建 `hospital.db` 数据库文件和所有表。

### 💡 提示2：代码热重载
开发模式下修改代码后，Flask会自动重启服务器，刷新浏览器即可看到效果。

### 💡 提示3：查看数据库
可以使用SQLite浏览器工具（如DB Browser for SQLite）查看 `hospital.db` 的内容。

### 💡 提示4：模板继承
所有页面模板都应该继承 `base.html`，这样可以保持统一的页面布局和样式。

### 💡 提示5：CSS样式
已经在 `static/css/style.css` 中定义了大量CSS类，可以直接使用，避免重复编写样式。

### 💡 提示6：Git协作
建议每个开发者创建自己的分支，完成功能后再合并到主分支。

---

## 下一步

1. ✅ **已完成**: 项目框架搭建
2. ✅ **已完成**: 核心功能路由实现
3. ✅ **已完成**: 部分模板创建
4. 🚀 **进行中**: 完善各子系统的模板文件
5. ⏳ **待完成**: 功能测试和优化
6. ⏳ **待完成**: 添加用户认证（可选）

---

祝你开发顺利！如有问题，请查阅 `DEVELOPMENT_GUIDE.md` 获取详细的开发说明。

**项目维护者**: 三人开发团队  
**版本**: v1.0.0  
**更新日期**: 2024-10-10

