# 开发指南 - 三人协作开发说明

## 项目分工

### 开发者1：病人管理子系统
**负责模块**: 病人管理系统
**工作目录**: 
- `modules/patient/`
- `templates/patient/`

**核心功能**:
1. 病人基本信息管理（CRUD操作）
2. 病历记录管理
3. 挂号预约管理

**数据库表**:
- `patients`: 病人基本信息
- `medical_records`: 病历记录
- `appointments`: 预约挂号

**路由列表**:
```
GET  /patient/                           # 病人管理首页
GET  /patient/patients                   # 病人列表
GET  /patient/patient/add               # 添加病人表单
POST /patient/patient/add               # 提交添加病人
GET  /patient/patient/edit/<id>         # 编辑病人表单
POST /patient/patient/edit/<id>         # 提交编辑病人
POST /patient/patient/delete/<id>       # 删除病人
GET  /patient/patient/detail/<id>       # 病人详情

GET  /patient/medical-records           # 病历列表
GET  /patient/medical-record/add        # 添加病历表单
POST /patient/medical-record/add        # 提交添加病历
GET  /patient/medical-record/detail/<id> # 病历详情

GET  /patient/appointments              # 预约列表
GET  /patient/appointment/add           # 添加预约表单
POST /patient/appointment/add           # 提交添加预约
POST /patient/appointment/update-status/<id> # 更新预约状态
```

**需要创建的模板文件**:
- ✅ `patient_index.html` - 已创建
- ✅ `patient_list.html` - 已创建
- ✅ `patient_form.html` - 已创建
- `patient_detail.html` - 需要创建
- `medical_record_list.html` - 需要创建
- `medical_record_form.html` - 需要创建
- `medical_record_detail.html` - 需要创建
- `appointment_list.html` - 需要创建
- `appointment_form.html` - 需要创建

---

### 开发者2：医生管理子系统
**负责模块**: 医生管理系统
**工作目录**: 
- `modules/doctor/`
- `templates/doctor/`

**核心功能**:
1. 医生信息管理（CRUD操作）
2. 医生排班管理
3. 医生绩效评估

**数据库表**:
- `doctors`: 医生信息
- `doctor_schedules`: 医生排班
- `doctor_performances`: 医生绩效

**路由列表**:
```
GET  /doctor/                           # 医生管理首页
GET  /doctor/doctors                    # 医生列表
GET  /doctor/doctor/add                # 添加医生表单
POST /doctor/doctor/add                # 提交添加医生
GET  /doctor/doctor/edit/<id>          # 编辑医生表单
POST /doctor/doctor/edit/<id>          # 提交编辑医生
POST /doctor/doctor/delete/<id>        # 删除医生
GET  /doctor/doctor/detail/<id>        # 医生详情

GET  /doctor/schedules                 # 排班列表
GET  /doctor/schedule/add              # 添加排班表单
POST /doctor/schedule/add              # 提交添加排班
GET  /doctor/schedule/edit/<id>        # 编辑排班表单
POST /doctor/schedule/edit/<id>        # 提交编辑排班
POST /doctor/schedule/delete/<id>      # 删除排班

GET  /doctor/performances              # 绩效列表
GET  /doctor/performance/add           # 添加绩效表单
POST /doctor/performance/add           # 提交添加绩效
GET  /doctor/performance/detail/<id>   # 绩效详情
```

**需要创建的模板文件**:
- ✅ `doctor_index.html` - 已创建
- ✅ `doctor_list.html` - 已创建
- `doctor_form.html` - 需要创建
- `doctor_detail.html` - 需要创建
- `schedule_list.html` - 需要创建
- `schedule_form.html` - 需要创建
- `performance_list.html` - 需要创建
- `performance_form.html` - 需要创建
- `performance_detail.html` - 需要创建

---

### 开发者3：药品管理子系统
**负责模块**: 药品管理系统
**工作目录**: 
- `modules/pharmacy/`
- `templates/pharmacy/`

**核心功能**:
1. 药品信息管理（CRUD操作）
2. 药品库存管理（库存预警）
3. 药品采购管理（采购单、收货）

**数据库表**:
- `medicines`: 药品信息
- `medicine_inventory`: 药品库存
- `medicine_purchases`: 药品采购

**路由列表**:
```
GET  /pharmacy/                         # 药品管理首页
GET  /pharmacy/medicines                # 药品列表
GET  /pharmacy/medicine/add            # 添加药品表单
POST /pharmacy/medicine/add            # 提交添加药品
GET  /pharmacy/medicine/edit/<id>      # 编辑药品表单
POST /pharmacy/medicine/edit/<id>      # 提交编辑药品
POST /pharmacy/medicine/delete/<id>    # 删除药品
GET  /pharmacy/medicine/detail/<id>    # 药品详情

GET  /pharmacy/inventory               # 库存列表
GET  /pharmacy/inventory/edit/<id>     # 编辑库存表单
POST /pharmacy/inventory/edit/<id>     # 提交编辑库存
POST /pharmacy/inventory/adjust/<id>   # 调整库存数量

GET  /pharmacy/purchases               # 采购列表
GET  /pharmacy/purchase/add            # 添加采购表单
POST /pharmacy/purchase/add            # 提交添加采购
GET  /pharmacy/purchase/detail/<id>    # 采购详情
POST /pharmacy/purchase/receive/<id>   # 确认收货
```

**需要创建的模板文件**:
- ✅ `pharmacy_index.html` - 已创建
- ✅ `medicine_list.html` - 已创建
- `medicine_form.html` - 需要创建
- `medicine_detail.html` - 需要创建
- `inventory_list.html` - 需要创建
- `inventory_form.html` - 需要创建
- `purchase_list.html` - 需要创建
- `purchase_form.html` - 需要创建
- `purchase_detail.html` - 需要创建

---

## 协作流程

### 1. 初始设置

每个开发者首先克隆项目：

```bash
git clone <repository-url>
cd SE-Assignment
```

安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 创建分支

每个开发者在各自的分支上工作：

```bash
# 开发者1
git checkout -b dev/patient-system

# 开发者2
git checkout -b dev/doctor-system

# 开发者3
git checkout -b dev/pharmacy-system
```

### 3. 独立开发

**开发步骤**：

1. **熟悉数据库模型**
   - 阅读 `models.py` 中对应的数据库模型
   - 理解表结构和字段含义

2. **实现路由功能**
   - 在 `modules/<your-module>/routes.py` 中实现功能
   - 参考已有的路由示例

3. **创建模板文件**
   - 在 `templates/<your-module>/` 中创建HTML模板
   - 继承 `base.html` 基础模板
   - 使用现有的CSS样式（在 `static/css/style.css` 中）

4. **测试功能**
   ```bash
   python app.py
   ```
   访问对应的URL进行测试

### 4. 提交代码

```bash
# 查看修改
git status

# 添加修改的文件
git add modules/<your-module>/
git add templates/<your-module>/

# 提交
git commit -m "实现XXX功能"

# 推送到远程
git push origin dev/<your-system>
```

### 5. 代码合并

1. 在Git平台上创建Pull Request
2. 其他开发者进行代码审查
3. 审查通过后合并到主分支

---

## 开发规范

### 代码规范

1. **Python代码**
   - 遵循PEP 8规范
   - 函数和类添加文档字符串
   - 使用有意义的变量名

2. **HTML模板**
   - 使用统一的模板继承
   - 保持代码缩进一致
   - 添加必要的注释

3. **CSS样式**
   - 使用已有的CSS类
   - 如需新增样式，添加到 `static/css/style.css`

### 命名规范

1. **路由命名**
   ```python
   @module_bp.route('/entity-name/action')
   def entity_action():
       pass
   ```

2. **模板命名**
   ```
   entity_list.html      # 列表页
   entity_form.html      # 表单页（新增/编辑）
   entity_detail.html    # 详情页
   ```

3. **变量命名**
   - 使用小写字母和下划线
   - 变量名要清晰表达含义

### Git提交规范

提交信息格式：
```
[模块名] 简短描述

详细描述（可选）
```

示例：
```
[病人管理] 实现病人列表和添加功能

- 完成病人列表查询和分页
- 实现添加病人表单和验证
- 添加搜索功能
```

---

## 常见开发任务

### 任务1：实现列表页面

1. **路由处理**（`routes.py`）：
```python
@module_bp.route('/entities')
def entity_list():
    page = request.args.get('page', 1, type=int)
    query = Entity.query
    pagination = query.paginate(page=page, per_page=10)
    entities = pagination.items
    return render_template('entity_list.html', 
                         entities=entities, 
                         pagination=pagination)
```

2. **模板文件**（`entity_list.html`）：
```html
{% extends "base.html" %}

{% block title %}实体列表{% endblock %}

{% block content %}
<div class="page-header">
    <h1>实体列表</h1>
    <a href="{{ url_for('module.entity_add') }}" class="btn btn-primary">添加</a>
</div>

<table class="data-table">
    <thead>
        <tr>
            <th>字段1</th>
            <th>字段2</th>
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        {% for entity in entities %}
        <tr>
            <td>{{ entity.field1 }}</td>
            <td>{{ entity.field2 }}</td>
            <td class="actions">
                <a href="{{ url_for('module.entity_detail', id=entity.id) }}" class="btn-small">详情</a>
                <a href="{{ url_for('module.entity_edit', id=entity.id) }}" class="btn-small">编辑</a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

### 任务2：实现表单页面（添加/编辑）

1. **路由处理**（`routes.py`）：
```python
@module_bp.route('/entity/add', methods=['GET', 'POST'])
def entity_add():
    if request.method == 'POST':
        try:
            entity = Entity(
                field1=request.form.get('field1'),
                field2=request.form.get('field2')
            )
            db.session.add(entity)
            db.session.commit()
            flash('添加成功！', 'success')
            return redirect(url_for('module.entity_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    return render_template('entity_form.html', entity=None)
```

2. **模板文件**（`entity_form.html`）：
```html
{% extends "base.html" %}

{% block title %}添加实体{% endblock %}

{% block content %}
<form method="post" class="form">
    <div class="form-group">
        <label for="field1">字段1 *</label>
        <input type="text" id="field1" name="field1" 
               value="{{ entity.field1 if entity else '' }}" required>
    </div>
    
    <div class="form-actions">
        <button type="submit" class="btn btn-primary">保存</button>
        <a href="{{ url_for('module.entity_list') }}" class="btn btn-secondary">取消</a>
    </div>
</form>
{% endblock %}
```

### 任务3：实现搜索功能

```python
@module_bp.route('/entities')
def entity_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Entity.query
    if search:
        query = query.filter(Entity.name.like(f'%{search}%'))
    
    pagination = query.paginate(page=page, per_page=10)
    entities = pagination.items
    
    return render_template('entity_list.html', 
                         entities=entities, 
                         pagination=pagination,
                         search=search)
```

---

## 调试技巧

### 1. 查看错误信息

Flask开启了调试模式，浏览器会显示详细的错误信息。

### 2. 打印调试

在路由中使用 `print()` 查看变量值：

```python
@module_bp.route('/test')
def test():
    data = request.form.get('data')
    print(f"接收到的数据: {data}")  # 会在控制台输出
    return "OK"
```

### 3. 数据库查询测试

可以在Python交互式环境中测试：

```python
from app import create_app, db
from models import Patient

app = create_app()
with app.app_context():
    # 查询所有病人
    patients = Patient.query.all()
    print(patients)
```

---

## 常见问题解决

### Q1: 模板找不到？
A: 检查模板路径是否正确，确保模板文件在 `templates/<module>/` 目录下。

### Q2: 数据库错误？
A: 
1. 检查模型定义是否正确
2. 确认是否执行了 `db.session.commit()`
3. 使用 `try-except` 捕获异常

### Q3: 样式不生效？
A: 
1. 检查CSS文件路径
2. 清除浏览器缓存（Ctrl+F5）
3. 确认使用了正确的CSS类名

### Q4: 如何与其他子系统交互？
A: 通过共享的数据库模型进行交互。例如，病人管理系统可以查询医生表：
```python
from models import Doctor
doctors = Doctor.query.all()
```

---

## 进度检查清单

### 开发者1检查清单
- [ ] 病人列表页面
- [ ] 添加/编辑病人功能
- [ ] 病人详情页面
- [ ] 病历列表页面
- [ ] 添加病历功能
- [ ] 病历详情页面
- [ ] 预约列表页面
- [ ] 添加预约功能
- [ ] 预约状态管理

### 开发者2检查清单
- [ ] 医生列表页面
- [ ] 添加/编辑医生功能
- [ ] 医生详情页面
- [ ] 排班列表页面
- [ ] 添加/编辑排班功能
- [ ] 绩效列表页面
- [ ] 添加绩效功能
- [ ] 绩效详情页面

### 开发者3检查清单
- [ ] 药品列表页面
- [ ] 添加/编辑药品功能
- [ ] 药品详情页面
- [ ] 库存列表页面
- [ ] 编辑库存功能
- [ ] 库存预警功能
- [ ] 采购列表页面
- [ ] 添加采购功能
- [ ] 采购详情和收货功能

---

## 联系和协作

- **代码审查**: 相互审查对方的代码，提出改进建议
- **遇到问题**: 在团队群组中讨论，或创建Issue
- **定期同步**: 定期将主分支的更新合并到自己的分支

```bash
# 更新主分支
git checkout main
git pull origin main

# 合并到自己的分支
git checkout dev/<your-system>
git merge main
```

---

祝开发顺利！🎉

