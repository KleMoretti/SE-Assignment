# 医生管理子系统 - 功能说明

## 📚 目录结构

```
backend/modules/doctor/
├── __init__.py              # 模块初始化
├── routes.py                # API路由（现有功能）
├── models_extended.py       # 扩展数据模型（新增）
├── schemas.py               # 数据验证（新增）
├── utils.py                 # 工具函数（新增）
└── README.md                # 本文件
```

---

## 🎯 功能概览

### 现有功能（routes.py）
- ✅ 医生信息CRUD
- ✅ 医生排班管理
- ✅ 医生绩效评估
- ✅ 统计分析

### 新增功能

#### 1. 扩展数据模型（models_extended.py）
- **DoctorQualification**: 医生资质证书管理
- **DoctorLeave**: 医生请假管理
- **DoctorScheduleTemplate**: 排班模板管理
- **OperationLog**: 操作日志记录
- **Notification**: 通知消息管理

#### 2. 数据验证（schemas.py）
- **DoctorSchema**: 医生信息验证
- **DoctorScheduleSchema**: 排班信息验证
- **DoctorPerformanceSchema**: 绩效评估验证
- **DoctorQualificationSchema**: 资质证书验证
- **DoctorLeaveSchema**: 请假信息验证
- **DoctorScheduleTemplateSchema**: 排班模板验证

#### 3. 工具函数（utils.py）
- 排班冲突检测
- 请假冲突检测
- 绩效自动计算
- 操作日志记录
- 通知发送
- 数据导出
- 统计分析

---

## 🚀 快速开始

### 1. 数据库迁移

首先需要创建新的数据表：

```python
# 在Python交互环境中执行
from backend.app import create_app, db
from backend.modules.doctor.models_extended import (
    DoctorQualification, DoctorLeave, DoctorScheduleTemplate,
    DoctorScheduleTemplateDetail, OperationLog, Notification
)

app = create_app()
with app.app_context():
    db.create_all()
    print("数据库表创建成功！")
```

### 2. 安装依赖

```bash
pip install marshmallow==3.20.0
pip install marshmallow-sqlalchemy==0.29.0
pip install openpyxl==3.1.2
```

### 3. 在routes.py中集成新功能

示例 - 在创建医生时添加数据验证：

```python
from modules.doctor.schemas import DoctorSchema
from modules.doctor.utils import log_operation
from marshmallow import ValidationError

@doctor_bp.route('/doctors', methods=['POST'])
def create_doctor():
    """创建医生（带验证）"""
    try:
        data = request.get_json()
        
        # 数据验证
        schema = DoctorSchema()
        validated_data = schema.load(data)
        
        # 检查医生编号是否已存在
        if Doctor.query.filter_by(doctor_no=validated_data['doctor_no']).first():
            return error_response('医生编号已存在', 'DOCTOR_NO_EXISTS')
        
        # 创建医生
        doctor = Doctor(**validated_data)
        db.session.add(doctor)
        db.session.commit()
        
        # 记录操作日志
        log_operation(
            operation='create',
            resource='doctor',
            resource_id=doctor.id,
            resource_name=doctor.name,
            username='current_user'  # 实际应从认证获取
        )
        
        return success_response(doctor.to_dict(), '医生创建成功')
        
    except ValidationError as err:
        return error_response(str(err.messages), 'VALIDATION_ERROR')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建医生失败：{str(e)}', 'CREATE_DOCTOR_ERROR', 500)
```

---

## 📖 详细使用说明

### 数据验证使用

#### 基本验证
```python
from modules.doctor.schemas import DoctorSchema
from marshmallow import ValidationError

schema = DoctorSchema()

# 成功案例
data = {
    'doctor_no': 'D001',
    'name': '张医生',
    'gender': '男',
    'age': 35,
    'phone': '13800138000',
    'email': 'zhang@hospital.com',
    'department': '内科',
    'title': '主治医师'
}

try:
    validated_data = schema.load(data)
    print("验证通过！", validated_data)
except ValidationError as err:
    print("验证失败：", err.messages)
```

#### 失败案例
```python
# 会抛出ValidationError
bad_data = {
    'doctor_no': 'D001',
    'name': '张',  # 太短，最少2个字符
    'gender': '未知',  # 不在枚举值中
    'age': 18,  # 小于22岁
    'phone': '123',  # 格式不正确
    'email': 'invalid-email'  # 邮箱格式不正确
}
```

### 排班冲突检测

```python
from modules.doctor.utils import check_schedule_conflict
from datetime import date

# 检查是否有冲突
has_conflict = check_schedule_conflict(
    doctor_id=1,
    schedule_date=date(2025, 11, 20),
    start_time='09:00',
    end_time='12:00'
)

if has_conflict:
    return error_response('该时段已有排班，存在冲突', 'SCHEDULE_CONFLICT')
```

### 请假冲突检测

```python
from modules.doctor.utils import check_leave_conflict, calculate_leave_days
from datetime import date

# 检查请假冲突
has_conflict = check_leave_conflict(
    doctor_id=1,
    start_date=date(2025, 11, 20),
    end_date=date(2025, 11, 22)
)

# 计算请假天数
days = calculate_leave_days(
    start_date=date(2025, 11, 20),
    end_date=date(2025, 11, 22)
)
print(f"请假{days}天")  # 输出：请假3天
```

### 操作日志记录

```python
from modules.doctor.utils import log_operation

# 记录创建操作
log_operation(
    operation='create',
    resource='doctor',
    resource_id=1,
    resource_name='张医生',
    details={'action': '创建医生信息', 'department': '内科'},
    user_id=1,
    username='admin',
    status='success'
)

# 记录失败操作
log_operation(
    operation='delete',
    resource='doctor',
    resource_id=1,
    resource_name='张医生',
    user_id=1,
    username='admin',
    status='failed',
    error_message='该医生有关联预约记录，无法删除'
)
```

### 发送通知

```python
from modules.doctor.utils import send_notification

# 发送排班通知
notification_id = send_notification(
    user_id=1,
    title='排班提醒',
    content='您明天上午有门诊，请准时到岗',
    notification_type='schedule',
    priority='high',
    related_resource='schedule',
    related_id=123
)
```

### 数据导出

```python
from modules.doctor.utils import export_doctors_to_excel
from models import Doctor
from flask import send_file

@doctor_bp.route('/doctors/export', methods=['GET'])
def export_doctors():
    """导出医生数据"""
    # 获取要导出的医生
    doctors = Doctor.query.filter_by(status='active').all()
    
    # 生成Excel
    excel_file = export_doctors_to_excel(doctors)
    
    # 返回文件
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'doctors_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )
```

### 绩效自动计算

```python
from modules.doctor.utils import calculate_doctor_performance

# 计算某医生某月绩效
performance_data = calculate_doctor_performance(
    doctor_id=1,
    year=2025,
    month=11
)

print(f"接诊人数: {performance_data['patient_count']}")
print(f"排班次数: {performance_data['schedule_count']}")
print(f"病历数量: {performance_data['medical_record_count']}")
```

---

## 🔧 API接口示例

### 资质管理API（待实现）

```python
# GET /api/doctor/doctors/<doctor_id>/qualifications
# 获取医生的所有资质证书

# POST /api/doctor/qualifications
# 创建资质证书
{
    "doctor_id": 1,
    "qualification_type": "medical_license",
    "certificate_no": "ML123456",
    "certificate_name": "执业医师证",
    "issue_date": "2020-01-01",
    "expiry_date": "2025-12-31",
    "issuing_authority": "国家卫健委"
}

# PUT /api/doctor/qualifications/<id>
# 更新资质证书

# DELETE /api/doctor/qualifications/<id>
# 删除资质证书
```

### 请假管理API（待实现）

```python
# GET /api/doctor/leaves
# 获取请假列表

# POST /api/doctor/leaves
# 创建请假申请
{
    "doctor_id": 1,
    "leave_type": "annual",
    "start_date": "2025-12-01",
    "end_date": "2025-12-03",
    "reason": "年假",
    "substitute_doctor_id": 2
}

# PUT /api/doctor/leaves/<id>/approve
# 审批请假
{
    "status": "approved",
    "approval_notes": "同意请假"
}

# PUT /api/doctor/leaves/<id>/reject
# 拒绝请假
{
    "status": "rejected",
    "approval_notes": "此时段人手不足，建议改期"
}
```

### 排班模板API（待实现）

```python
# GET /api/doctor/schedule-templates
# 获取排班模板列表

# POST /api/doctor/schedule-templates
# 创建排班模板
{
    "template_name": "内科标准排班",
    "department": "内科",
    "description": "周一至周五上午门诊",
    "details": [
        {
            "day_of_week": 1,  // 周一
            "shift": "morning",
            "start_time": "08:00",
            "end_time": "12:00",
            "max_patients": 30
        }
    ]
}

# POST /api/doctor/schedules/bulk
# 使用模板批量创建排班
{
    "doctor_id": 1,
    "template_id": 1,
    "start_date": "2025-12-01",
    "end_date": "2025-12-31"
}
```

---

## 📊 数据库表设计

### doctor_qualifications (医生资质表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| doctor_id | Integer | 医生ID（外键） |
| qualification_type | String(50) | 资质类型 |
| certificate_no | String(50) | 证书编号 |
| certificate_name | String(100) | 证书名称 |
| issue_date | Date | 颁发日期 |
| expiry_date | Date | 过期日期 |
| issuing_authority | String(100) | 颁发机构 |
| scope_of_practice | String(200) | 执业范围 |
| attachment_url | String(200) | 证书附件URL |
| status | String(20) | 状态 |
| notes | Text | 备注 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### doctor_leaves (请假记录表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| doctor_id | Integer | 医生ID（外键） |
| leave_type | String(20) | 请假类型 |
| start_date | Date | 开始日期 |
| end_date | Date | 结束日期 |
| days | Integer | 请假天数 |
| reason | Text | 请假原因 |
| status | String(20) | 状态 |
| approver_id | Integer | 审批人ID |
| approval_date | DateTime | 审批日期 |
| approval_notes | Text | 审批意见 |
| substitute_doctor_id | Integer | 替班医生ID |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### operation_logs (操作日志表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 操作用户ID |
| username | String(50) | 操作用户名 |
| operation | String(20) | 操作类型 |
| resource | String(50) | 资源类型 |
| resource_id | Integer | 资源ID |
| resource_name | String(100) | 资源名称 |
| details | Text | 操作详情（JSON） |
| ip_address | String(50) | IP地址 |
| user_agent | String(200) | User-Agent |
| status | String(20) | 状态 |
| error_message | Text | 错误信息 |
| created_at | DateTime | 操作时间 |

---

## 🧪 测试示例

```python
# test_doctor_validation.py
import unittest
from modules.doctor.schemas import DoctorSchema
from marshmallow import ValidationError

class TestDoctorValidation(unittest.TestCase):
    
    def test_valid_doctor_data(self):
        """测试有效的医生数据"""
        schema = DoctorSchema()
        data = {
            'doctor_no': 'D001',
            'name': '张医生',
            'gender': '男',
            'age': 35
        }
        result = schema.load(data)
        self.assertEqual(result['name'], '张医生')
    
    def test_invalid_phone(self):
        """测试无效的手机号"""
        schema = DoctorSchema()
        data = {
            'doctor_no': 'D001',
            'name': '张医生',
            'gender': '男',
            'phone': '123'  # 无效格式
        }
        with self.assertRaises(ValidationError):
            schema.load(data)
    
    def test_invalid_age(self):
        """测试无效的年龄"""
        schema = DoctorSchema()
        data = {
            'doctor_no': 'D001',
            'name': '张医生',
            'gender': '男',
            'age': 18  # 小于22岁
        }
        with self.assertRaises(ValidationError):
            schema.load(data)

if __name__ == '__main__':
    unittest.main()
```

---

## 📝 注意事项

1. **数据验证**
   - 所有用户输入都应该经过Schema验证
   - 验证错误要返回清晰的错误信息

2. **操作日志**
   - 所有关键操作（增删改）都应记录日志
   - 日志要包含操作人、操作时间、操作内容

3. **冲突检测**
   - 创建/更新排班前必须检查冲突
   - 创建/更新请假前必须检查冲突

4. **性能优化**
   - 使用索引优化查询
   - 避免N+1查询问题
   - 考虑使用缓存

5. **安全性**
   - 输入验证
   - SQL注入防护（使用ORM）
   - 操作审计

---

## 🔗 相关文档

- [系统分析文档](../../../docs/doctor_system_analysis.md)
- [实施总结文档](../../../docs/doctor_system_improvements.md)
- [项目README](../../../README.md)

---

**最后更新**: 2025-11-18  
**版本**: v1.0
