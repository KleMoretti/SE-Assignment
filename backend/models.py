"""
数据库模型
Database Models
"""
from datetime import datetime
from app import db
from typing import Dict


# ============= 病人管理子系统模型 =============

class Patient(db.Model):
    """病人基本信息表"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_no = db.Column(db.String(20), unique=True, nullable=False, comment='病人编号')
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    gender = db.Column(db.String(10), nullable=False, comment='性别')
    age = db.Column(db.Integer, comment='年龄')
    phone = db.Column(db.String(20), comment='联系电话')
    id_card = db.Column(db.String(18), comment='身份证号')
    address = db.Column(db.String(200), comment='住址')
    emergency_contact = db.Column(db.String(50), comment='紧急联系人')
    emergency_phone = db.Column(db.String(20), comment='紧急联系电话')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Patient {self.name}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'patient_no': self.patient_no,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'id_card': self.id_card,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MedicalRecord(db.Model):
    """病历记录表"""
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.now, comment='就诊日期')
    diagnosis = db.Column(db.Text, comment='诊断结果')
    symptoms = db.Column(db.Text, comment='症状描述')
    treatment = db.Column(db.Text, comment='治疗方案')
    prescription = db.Column(db.Text, comment='处方')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MedicalRecord {self.id}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'diagnosis': self.diagnosis,
            'symptoms': self.symptoms,
            'treatment': self.treatment,
            'prescription': self.prescription,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Appointment(db.Model):
    """挂号预约表"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False, comment='预约日期')
    appointment_time = db.Column(db.String(20), comment='预约时段')
    department = db.Column(db.String(50), comment='科室')
    status = db.Column(db.String(20), default='pending', comment='状态：pending/confirmed/completed/cancelled')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.id}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time,
            'department': self.department,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============= 医生管理子系统模型 =============

class Doctor(db.Model):
    """医生信息表"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_no = db.Column(db.String(20), unique=True, nullable=False, comment='医生编号')
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    gender = db.Column(db.String(10), comment='性别')
    age = db.Column(db.Integer, comment='年龄')
    phone = db.Column(db.String(20), comment='联系电话')
    email = db.Column(db.String(100), comment='邮箱')
    department = db.Column(db.String(50), comment='所属科室')
    title = db.Column(db.String(50), comment='职称')
    specialty = db.Column(db.String(100), comment='专长')
    education = db.Column(db.String(100), comment='学历')
    hire_date = db.Column(db.Date, comment='入职日期')
    status = db.Column(db.String(20), default='active', comment='状态：active/inactive')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    schedules = db.relationship('DoctorSchedule', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')
    performances = db.relationship('DoctorPerformance', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')
    medical_records = db.relationship('MedicalRecord', backref='doctor', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')
    
    def __repr__(self):
        return f'<Doctor {self.name}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'doctor_no': self.doctor_no,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'email': self.email,
            'department': self.department,
            'title': self.title,
            'specialty': self.specialty,
            'education': self.education,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DoctorSchedule(db.Model):
    """医生排班表"""
    __tablename__ = 'doctor_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, comment='日期')
    shift = db.Column(db.String(20), comment='班次：morning/afternoon/evening')
    start_time = db.Column(db.String(10), comment='开始时间')
    end_time = db.Column(db.String(10), comment='结束时间')
    max_patients = db.Column(db.Integer, default=20, comment='最大接诊数')
    status = db.Column(db.String(20), default='available', comment='状态：available/full/cancelled')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DoctorSchedule {self.doctor_id}-{self.date}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'date': self.date.isoformat() if self.date else None,
            'shift': self.shift,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'max_patients': self.max_patients,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DoctorPerformance(db.Model):
    """医生绩效评估表"""
    __tablename__ = 'doctor_performances'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False, comment='年份')
    month = db.Column(db.Integer, nullable=False, comment='月份')
    patient_count = db.Column(db.Integer, default=0, comment='接诊人数')
    satisfaction_score = db.Column(db.Float, comment='满意度评分')
    punctuality_score = db.Column(db.Float, comment='出勤准时率')
    quality_score = db.Column(db.Float, comment='医疗质量评分')
    total_score = db.Column(db.Float, comment='综合评分')
    bonus = db.Column(db.Float, comment='绩效奖金')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DoctorPerformance {self.doctor_id}-{self.year}-{self.month}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'year': self.year,
            'month': self.month,
            'patient_count': self.patient_count,
            'satisfaction_score': self.satisfaction_score,
            'punctuality_score': self.punctuality_score,
            'quality_score': self.quality_score,
            'total_score': self.total_score,
            'bonus': self.bonus,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============= 药品管理子系统模型 =============

class Medicine(db.Model):
    """药品信息表"""
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    medicine_no = db.Column(db.String(20), unique=True, nullable=False, comment='药品编号')
    name = db.Column(db.String(100), nullable=False, comment='药品名称')
    generic_name = db.Column(db.String(100), comment='通用名称')
    category = db.Column(db.String(50), comment='药品分类')
    specification = db.Column(db.String(50), comment='规格')
    unit = db.Column(db.String(20), comment='单位')
    manufacturer = db.Column(db.String(100), comment='生产厂家')
    price = db.Column(db.Float, nullable=False, comment='单价')
    prescription_required = db.Column(db.Boolean, default=False, comment='是否需要处方')
    usage = db.Column(db.Text, comment='用法用量')
    indications = db.Column(db.Text, comment='适应症')
    contraindications = db.Column(db.Text, comment='禁忌症')
    side_effects = db.Column(db.Text, comment='副作用')
    storage_conditions = db.Column(db.String(200), comment='储存条件')
    status = db.Column(db.String(20), default='active', comment='状态：active/inactive')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    inventory = db.relationship('MedicineInventory', backref='medicine', uselist=False, cascade='all, delete-orphan')
    purchases = db.relationship('MedicinePurchase', backref='medicine', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Medicine {self.name}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'medicine_no': self.medicine_no,
            'name': self.name,
            'generic_name': self.generic_name,
            'category': self.category,
            'specification': self.specification,
            'unit': self.unit,
            'manufacturer': self.manufacturer,
            'price': float(self.price) if self.price else 0,
            'prescription_required': self.prescription_required,
            'usage': self.usage,
            'indications': self.indications,
            'contraindications': self.contraindications,
            'side_effects': self.side_effects,
            'storage_conditions': self.storage_conditions,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # 包含库存信息
            'inventory': self.inventory.to_dict() if self.inventory else None
        }


class MedicineInventory(db.Model):
    """药品库存表"""
    __tablename__ = 'medicine_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False, unique=True)
    quantity = db.Column(db.Integer, default=0, comment='库存数量')
    min_stock = db.Column(db.Integer, default=0, comment='最小库存警戒线')
    max_stock = db.Column(db.Integer, comment='最大库存')
    location = db.Column(db.String(50), comment='存放位置')
    batch_no = db.Column(db.String(50), comment='批次号')
    production_date = db.Column(db.Date, comment='生产日期')
    expiry_date = db.Column(db.Date, comment='过期日期')
    last_restock_date = db.Column(db.DateTime, comment='最后补货日期')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MedicineInventory {self.medicine_id}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        # 判断是否低库存
        is_low_stock = self.quantity <= self.min_stock if self.min_stock else False
        
        return {
            'id': self.id,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else None,
            'quantity': self.quantity,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'is_low_stock': is_low_stock,
            'location': self.location,
            'batch_no': self.batch_no,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'last_restock_date': self.last_restock_date.isoformat() if self.last_restock_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MedicinePurchase(db.Model):
    """药品采购表"""
    __tablename__ = 'medicine_purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_no = db.Column(db.String(30), unique=True, nullable=False, comment='采购单号')
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    supplier = db.Column(db.String(100), comment='供应商')
    quantity = db.Column(db.Integer, nullable=False, comment='采购数量')
    unit_price = db.Column(db.Float, nullable=False, comment='采购单价')
    total_price = db.Column(db.Float, nullable=False, comment='总价')
    purchase_date = db.Column(db.DateTime, default=datetime.now, comment='采购日期')
    expected_delivery_date = db.Column(db.Date, comment='预计到货日期')
    actual_delivery_date = db.Column(db.Date, comment='实际到货日期')
    status = db.Column(db.String(20), default='pending', comment='状态：pending/received/completed')
    batch_no = db.Column(db.String(50), comment='批次号')
    production_date = db.Column(db.Date, comment='生产日期')
    expiry_date = db.Column(db.Date, comment='过期日期')
    purchaser = db.Column(db.String(50), comment='采购员')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MedicinePurchase {self.purchase_no}>'
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        return {
            'id': self.id,
            'purchase_no': self.purchase_no,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else None,
            'supplier': self.supplier,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'status': self.status,
            'batch_no': self.batch_no,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'purchaser': self.purchaser,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

