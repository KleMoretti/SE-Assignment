"""
医生管理子系统 - 扩展数据模型
Doctor Management - Extended Models

本文件包含医生子系统的扩展功能模型：
- DoctorQualification: 医生资质证书管理
- DoctorLeave: 医生请假管理
- DoctorScheduleTemplate: 排班模板管理
- OperationLog: 操作日志记录
- Notification: 通知消息管理
"""
from datetime import datetime, date
from backend.extensions import db
from typing import Dict


# ============= 医生资质管理 =============

class DoctorQualification(db.Model):
    """医生资质证书表"""
    __tablename__ = 'doctor_qualifications'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, comment='医生ID')
    qualification_type = db.Column(db.String(50), nullable=False, comment='资质类型：medical_license/practice_certificate/specialist_certificate/title_certificate')
    certificate_no = db.Column(db.String(50), comment='证书编号')
    certificate_name = db.Column(db.String(100), comment='证书名称')
    issue_date = db.Column(db.Date, comment='颁发日期')
    expiry_date = db.Column(db.Date, comment='过期日期')
    issuing_authority = db.Column(db.String(100), comment='颁发机构')
    scope_of_practice = db.Column(db.String(200), comment='执业范围')
    attachment_url = db.Column(db.String(200), comment='证书附件URL')
    status = db.Column(db.String(20), default='valid', comment='状态：valid/expired/revoked/pending')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    doctor = db.relationship('Doctor', backref=db.backref('qualifications', lazy='dynamic'))
    
    # 索引
    __table_args__ = (
        db.Index('idx_doctor_qualification', 'doctor_id', 'qualification_type'),
        db.Index('idx_expiry_date', 'expiry_date'),
        db.Index('idx_status', 'status'),
    )
    
    def __repr__(self):
        return f'<DoctorQualification {self.doctor_id}-{self.qualification_type}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        # 判断证书是否即将过期（30天内）
        is_expiring_soon = False
        if self.expiry_date:
            days_until_expiry = (self.expiry_date - date.today()).days
            is_expiring_soon = 0 <= days_until_expiry <= 30
        
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'qualification_type': self.qualification_type,
            'certificate_no': self.certificate_no,
            'certificate_name': self.certificate_name,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'issuing_authority': self.issuing_authority,
            'scope_of_practice': self.scope_of_practice,
            'attachment_url': self.attachment_url,
            'status': self.status,
            'is_expiring_soon': is_expiring_soon,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ============= 医生请假管理 =============

class DoctorLeave(db.Model):
    """医生请假记录表"""
    __tablename__ = 'doctor_leaves'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, comment='医生ID')
    leave_type = db.Column(db.String(20), nullable=False, comment='请假类型：sick/annual/personal/emergency/other')
    start_date = db.Column(db.Date, nullable=False, comment='开始日期')
    end_date = db.Column(db.Date, nullable=False, comment='结束日期')
    days = db.Column(db.Integer, comment='请假天数')
    reason = db.Column(db.Text, comment='请假原因')
    status = db.Column(db.String(20), default='pending', comment='状态：pending/approved/rejected/cancelled')
    approver_id = db.Column(db.Integer, comment='审批人ID')
    approval_date = db.Column(db.DateTime, comment='审批日期')
    approval_notes = db.Column(db.Text, comment='审批意见')
    substitute_doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), comment='替班医生ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    doctor = db.relationship('Doctor', foreign_keys=[doctor_id], backref=db.backref('leaves', lazy='dynamic'))
    substitute_doctor = db.relationship('Doctor', foreign_keys=[substitute_doctor_id])
    
    # 索引
    __table_args__ = (
        db.Index('idx_doctor_leave', 'doctor_id', 'start_date'),
        db.Index('idx_status', 'status'),
    )
    
    def __repr__(self):
        return f'<DoctorLeave {self.doctor_id}-{self.start_date}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'leave_type': self.leave_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'days': self.days,
            'reason': self.reason,
            'status': self.status,
            'approver_id': self.approver_id,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'approval_notes': self.approval_notes,
            'substitute_doctor_id': self.substitute_doctor_id,
            'substitute_doctor_name': self.substitute_doctor.name if self.substitute_doctor else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ============= 排班模板管理 =============

class DoctorScheduleTemplate(db.Model):
    """医生排班模板表"""
    __tablename__ = 'doctor_schedule_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(50), nullable=False, comment='模板名称')
    department = db.Column(db.String(50), comment='适用科室')
    description = db.Column(db.Text, comment='模板描述')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    template_details = db.relationship('DoctorScheduleTemplateDetail', backref='template', 
                                      lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<DoctorScheduleTemplate {self.template_name}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'template_name': self.template_name,
            'department': self.department,
            'description': self.description,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'details': [detail.to_dict() for detail in self.template_details.all()]
        }


class DoctorScheduleTemplateDetail(db.Model):
    """排班模板详情表"""
    __tablename__ = 'doctor_schedule_template_details'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('doctor_schedule_templates.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False, comment='星期几（1-7，1为周一）')
    shift = db.Column(db.String(20), nullable=False, comment='班次：morning/afternoon/evening')
    start_time = db.Column(db.String(10), comment='开始时间')
    end_time = db.Column(db.String(10), comment='结束时间')
    max_patients = db.Column(db.Integer, default=20, comment='最大接诊数')
    
    def __repr__(self):
        return f'<TemplateDetail {self.template_id}-{self.day_of_week}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        day_names = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
        return {
            'id': self.id,
            'template_id': self.template_id,
            'day_of_week': self.day_of_week,
            'day_name': day_names.get(self.day_of_week, ''),
            'shift': self.shift,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'max_patients': self.max_patients
        }


# ============= 操作日志 =============

class OperationLog(db.Model):
    """操作日志表"""
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, comment='操作用户ID')
    username = db.Column(db.String(50), comment='操作用户名')
    operation = db.Column(db.String(20), nullable=False, comment='操作类型：create/update/delete/view/export')
    resource = db.Column(db.String(50), nullable=False, comment='资源类型：doctor/schedule/performance/qualification/leave')
    resource_id = db.Column(db.Integer, comment='资源ID')
    resource_name = db.Column(db.String(100), comment='资源名称')
    details = db.Column(db.Text, comment='操作详情（JSON格式）')
    ip_address = db.Column(db.String(50), comment='IP地址')
    user_agent = db.Column(db.String(200), comment='用户代理')
    status = db.Column(db.String(20), default='success', comment='状态：success/failed')
    error_message = db.Column(db.Text, comment='错误信息')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True, comment='操作时间')
    
    # 添加索引
    __table_args__ = (
        db.Index('idx_user_id', 'user_id'),
        db.Index('idx_operation', 'operation'),
        db.Index('idx_resource', 'resource'),
        db.Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f'<OperationLog {self.operation}-{self.resource}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'operation': self.operation,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============= 通知消息 =============

class Notification(db.Model):
    """通知消息表"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='接收用户ID')
    title = db.Column(db.String(100), nullable=False, comment='通知标题')
    content = db.Column(db.Text, comment='通知内容')
    type = db.Column(db.String(20), comment='类型：schedule/performance/system/leave/qualification')
    priority = db.Column(db.String(20), default='normal', comment='优先级：low/normal/high/urgent')
    related_resource = db.Column(db.String(50), comment='关联资源类型')
    related_id = db.Column(db.Integer, comment='关联资源ID')
    is_read = db.Column(db.Boolean, default=False, index=True, comment='是否已读')
    read_at = db.Column(db.DateTime, comment='阅读时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 添加索引
    __table_args__ = (
        db.Index('idx_user_is_read', 'user_id', 'is_read'),
        db.Index('idx_type', 'type'),
        db.Index('idx_priority', 'priority'),
    )
    
    def __repr__(self):
        return f'<Notification {self.title}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'priority': self.priority,
            'related_resource': self.related_resource,
            'related_id': self.related_id,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
