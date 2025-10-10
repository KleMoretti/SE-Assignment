"""
数据库模型
Database Models
"""
from datetime import datetime
from app import db


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
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic')
    
    def __repr__(self):
        return f'<Patient {self.name}>'


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
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<MedicalRecord {self.id}>'


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
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Appointment {self.id}>'


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
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    schedules = db.relationship('DoctorSchedule', backref='doctor', lazy='dynamic')
    performances = db.relationship('DoctorPerformance', backref='doctor', lazy='dynamic')
    medical_records = db.relationship('MedicalRecord', backref='doctor', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')
    
    def __repr__(self):
        return f'<Doctor {self.name}>'


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
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<DoctorSchedule {self.doctor_id}-{self.date}>'


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
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<DoctorPerformance {self.doctor_id}-{self.year}-{self.month}>'


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
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    inventory = db.relationship('MedicineInventory', backref='medicine', uselist=False)
    purchases = db.relationship('MedicinePurchase', backref='medicine', lazy='dynamic')
    
    def __repr__(self):
        return f'<Medicine {self.name}>'


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
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<MedicineInventory {self.medicine_id}>'


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
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<MedicinePurchase {self.purchase_no}>'

