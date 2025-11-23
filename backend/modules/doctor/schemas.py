"""
医生管理子系统 - 数据验证模式
Doctor Management - Validation Schemas

使用Marshmallow进行数据验证
"""
from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema
from datetime import date
import re


# ============= 医生信息验证 =============

class DoctorSchema(Schema):
    """医生数据验证模式"""
    doctor_no = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=20),
        error_messages={'required': '医生编号不能为空'}
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50),
        error_messages={'required': '姓名不能为空'}
    )
    gender = fields.Str(
        required=True,
        validate=validate.OneOf(['男', '女', '其他']),
        error_messages={'required': '性别不能为空'}
    )
    age = fields.Int(validate=validate.Range(min=22, max=70, error='年龄必须在22-70之间'))
    phone = fields.Str(validate=validate.Length(max=20))
    email = fields.Email(error_messages={'invalid': '邮箱格式不正确'})
    department = fields.Str(validate=validate.Length(max=50))
    title = fields.Str(
        validate=validate.OneOf(['主任医师', '副主任医师', '主治医师', '住院医师', '医师', None]),
        allow_none=True
    )
    specialty = fields.Str(validate=validate.Length(max=100))
    education = fields.Str(validate=validate.Length(max=100))
    hire_date = fields.Date()
    status = fields.Str(validate=validate.OneOf(['active', 'inactive']))
    
    @validates('phone')
    def validate_phone(self, value, **kwargs):
        """验证手机号格式"""
        if value and not re.match(r'^1[3-9]\d{9}$', value):
            raise ValidationError('手机号格式不正确，应为11位数字且以1开头')
    
    @validates('hire_date')
    def validate_hire_date(self, value, **kwargs):
        """验证入职日期"""
        if value and value > date.today():
            raise ValidationError('入职日期不能晚于今天')
    
    @validates_schema
    def validate_age_hire_date(self, data, **kwargs):
        """验证年龄与入职日期的一致性"""
        age = data.get('age')
        hire_date = data.get('hire_date')
        
        if age and hire_date:
            years_since_hire = (date.today() - hire_date).days // 365
            if age < 22 or (age - years_since_hire) < 22:
                raise ValidationError({'age': '入职时年龄应至少为22岁'})


# ============= 排班验证 =============

class DoctorScheduleSchema(Schema):
    """医生排班数据验证模式"""
    doctor_id = fields.Int(required=True, error_messages={'required': '医生ID不能为空'})
    date = fields.Date(required=True, error_messages={'required': '日期不能为空'})
    shift = fields.Str(
        required=True,
        validate=validate.OneOf(['morning', 'afternoon', 'evening']),
        error_messages={'required': '班次不能为空'}
    )
    start_time = fields.Str(validate=validate.Regexp(r'^([01]\d|2[0-3]):([0-5]\d)$', error='时间格式应为HH:MM'))
    end_time = fields.Str(validate=validate.Regexp(r'^([01]\d|2[0-3]):([0-5]\d)$', error='时间格式应为HH:MM'))
    max_patients = fields.Int(validate=validate.Range(min=1, max=100, error='最大接诊数应在1-100之间'))
    status = fields.Str(validate=validate.OneOf(['available', 'full', 'cancelled']))
    notes = fields.Str(validate=validate.Length(max=500))
    
    @validates('date')
    def validate_date(self, value, **kwargs):
        """验证排班日期不能是过去的日期"""
        if value < date.today():
            raise ValidationError('排班日期不能早于今天')
    
    @validates_schema
    def validate_time_range(self, data, **kwargs):
        """验证开始时间必须早于结束时间"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError({'end_time': '结束时间必须晚于开始时间'})


# ============= 绩效评估验证 =============

class DoctorPerformanceSchema(Schema):
    """医生绩效评估数据验证模式"""
    doctor_id = fields.Int(required=True, error_messages={'required': '医生ID不能为空'})
    year = fields.Int(
        required=True,
        validate=validate.Range(min=2000, max=2100),
        error_messages={'required': '年份不能为空'}
    )
    month = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=12, error='月份必须在1-12之间'),
        error_messages={'required': '月份不能为空'}
    )
    patient_count = fields.Int(validate=validate.Range(min=0, max=10000))
    satisfaction_score = fields.Float(validate=validate.Range(min=0, max=100, error='满意度评分应在0-100之间'))
    punctuality_score = fields.Float(validate=validate.Range(min=0, max=100, error='准时率评分应在0-100之间'))
    quality_score = fields.Float(validate=validate.Range(min=0, max=100, error='质量评分应在0-100之间'))
    notes = fields.Str(validate=validate.Length(max=1000))
    
    @validates_schema
    def validate_period(self, data, **kwargs):
        """验证评估期间不能晚于当前月份"""
        year = data.get('year')
        month = data.get('month')
        
        if year and month:
            today = date.today()
            if year > today.year or (year == today.year and month > today.month):
                raise ValidationError({'month': '评估期间不能晚于当前月份'})


# ============= 资质证书验证 =============

class DoctorQualificationSchema(Schema):
    """医生资质证书数据验证模式"""
    doctor_id = fields.Int(required=True, error_messages={'required': '医生ID不能为空'})
    qualification_type = fields.Str(
        required=True,
        validate=validate.OneOf([
            'medical_license',
            'practice_certificate',
            'specialist_certificate',
            'title_certificate'
        ]),
        error_messages={'required': '资质类型不能为空'}
    )
    certificate_no = fields.Str(validate=validate.Length(max=50))
    certificate_name = fields.Str(validate=validate.Length(min=2, max=100))
    issue_date = fields.Date()
    expiry_date = fields.Date()
    issuing_authority = fields.Str(validate=validate.Length(max=100))
    scope_of_practice = fields.Str(validate=validate.Length(max=200))
    attachment_url = fields.Url()
    status = fields.Str(validate=validate.OneOf(['valid', 'expired', 'revoked', 'pending']))
    notes = fields.Str(validate=validate.Length(max=1000))
    
    @validates_schema
    def validate_dates(self, data, **kwargs):
        """验证日期的合理性"""
        issue_date = data.get('issue_date')
        expiry_date = data.get('expiry_date')
        
        if issue_date and issue_date > date.today():
            raise ValidationError({'issue_date': '颁发日期不能晚于今天'})
        
        if issue_date and expiry_date and expiry_date <= issue_date:
            raise ValidationError({'expiry_date': '过期日期必须晚于颁发日期'})


# ============= 请假记录验证 =============

class DoctorLeaveSchema(Schema):
    """医生请假记录数据验证模式"""
    doctor_id = fields.Int(required=True, error_messages={'required': '医生ID不能为空'})
    leave_type = fields.Str(
        required=True,
        validate=validate.OneOf(['sick', 'annual', 'personal', 'emergency', 'other']),
        error_messages={'required': '请假类型不能为空'}
    )
    start_date = fields.Date(required=True, error_messages={'required': '开始日期不能为空'})
    end_date = fields.Date(required=True, error_messages={'required': '结束日期不能为空'})
    reason = fields.Str(validate=validate.Length(min=1, max=500))
    status = fields.Str(validate=validate.OneOf(['pending', 'approved', 'rejected', 'cancelled']))
    substitute_doctor_id = fields.Int()
    approval_notes = fields.Str(validate=validate.Length(max=500))
    
    @validates_schema
    def validate_dates(self, data, **kwargs):
        """验证日期的合理性"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError({'end_date': '结束日期不能早于开始日期'})
            
            # 计算请假天数
            days = (end_date - start_date).days + 1
            if days > 365:
                raise ValidationError({'end_date': '请假天数不能超过365天'})
    
    @validates_schema
    def validate_substitute(self, data, **kwargs):
        """验证替班医生不能是本人"""
        doctor_id = data.get('doctor_id')
        substitute_doctor_id = data.get('substitute_doctor_id')
        
        if substitute_doctor_id and doctor_id == substitute_doctor_id:
            raise ValidationError({'substitute_doctor_id': '替班医生不能是本人'})


# ============= 排班模板验证 =============

class DoctorScheduleTemplateSchema(Schema):
    """排班模板数据验证模式"""
    template_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50),
        error_messages={'required': '模板名称不能为空'}
    )
    department = fields.Str(validate=validate.Length(max=50))
    description = fields.Str(validate=validate.Length(max=500))
    is_active = fields.Bool()


class DoctorScheduleTemplateDetailSchema(Schema):
    """排班模板详情数据验证模式"""
    template_id = fields.Int(required=True, error_messages={'required': '模板ID不能为空'})
    day_of_week = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=7, error='星期几必须在1-7之间'),
        error_messages={'required': '星期几不能为空'}
    )
    shift = fields.Str(
        required=True,
        validate=validate.OneOf(['morning', 'afternoon', 'evening']),
        error_messages={'required': '班次不能为空'}
    )
    start_time = fields.Str(validate=validate.Regexp(r'^([01]\d|2[0-3]):([0-5]\d)$', error='时间格式应为HH:MM'))
    end_time = fields.Str(validate=validate.Regexp(r'^([01]\d|2[0-3]):([0-5]\d)$', error='时间格式应为HH:MM'))
    max_patients = fields.Int(validate=validate.Range(min=1, max=100))


# ============= 批量操作验证 =============

class BulkScheduleSchema(Schema):
    """批量排班数据验证模式"""
    doctor_id = fields.Int(required=True)
    template_id = fields.Int(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    
    @validates_schema
    def validate_dates(self, data, **kwargs):
        """验证日期范围"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError({'end_date': '结束日期不能早于开始日期'})
            
            days = (end_date - start_date).days
            if days > 90:
                raise ValidationError({'end_date': '批量排班最多支持90天'})
