"""
病人管理子系统 - 服务层
Patient Management - Services
"""
from models import Patient, MedicalRecord, Appointment
from extensions import db
from datetime import datetime

# ============= 病人基本信息管理服务 =============

def get_patients_with_pagination(page, per_page=10, search=''):
    """获取病人列表（分页和搜索）"""
    query = Patient.query
    if search:
        query = query.filter(
            (Patient.name.like(f'%{search}%')) |
            (Patient.patient_no.like(f'%{search}%')) |
            (Patient.phone.like(f'%{search}%'))
        )

    pagination = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return pagination


def add_new_patient(form_data):
    """添加新病人"""
    patient = Patient(
        patient_no=form_data.get('patient_no'),
        name=form_data.get('name'),
        gender=form_data.get('gender'),
        age=form_data.get('age', type=int),
        phone=form_data.get('phone'),
        id_card=form_data.get('id_card'),
        address=form_data.get('address'),
        emergency_contact=form_data.get('emergency_contact'),
        emergency_phone=form_data.get('emergency_phone')
    )
    db.session.add(patient)
    db.session.commit()
    return patient


def get_patient_by_id(patient_id):
    """通过ID获取病人信息"""
    return Patient.query.get_or_404(patient_id)


def update_patient_info(patient_id, form_data):
    """更新病人信息"""
    patient = get_patient_by_id(patient_id)
    patient.name = form_data.get('name')
    patient.gender = form_data.get('gender')
    patient.age = form_data.get('age', type=int)
    patient.phone = form_data.get('phone')
    patient.id_card = form_data.get('id_card')
    patient.address = form_data.get('address')
    patient.emergency_contact = form_data.get('emergency_contact')
    patient.emergency_phone = form_data.get('emergency_phone')
    db.session.commit()
    return patient


def delete_patient_by_id(patient_id):
    """删除病人信息"""
    patient = get_patient_by_id(patient_id)
    db.session.delete(patient)
    db.session.commit()


# ============= 病历记录管理服务 =============

def get_medical_records_with_pagination(page, per_page=10, patient_id=None):
    """获取病历列表（分页和过滤）"""
    query = MedicalRecord.query
    if patient_id:
        query = query.filter_by(patient_id=patient_id)

    pagination = query.order_by(MedicalRecord.visit_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return pagination


def add_new_medical_record(form_data):
    """添加新病历"""
    record = MedicalRecord(
        patient_id=form_data.get('patient_id', type=int),
        doctor_id=form_data.get('doctor_id', type=int),
        diagnosis=form_data.get('diagnosis'),
        symptoms=form_data.get('symptoms'),
        treatment=form_data.get('treatment'),
        prescription=form_data.get('prescription'),
        notes=form_data.get('notes')
    )
    db.session.add(record)
    db.session.commit()
    return record


def get_medical_record_by_id(record_id):
    """通过ID获取病历详情"""
    return MedicalRecord.query.get_or_404(record_id)


# ============= 挂号预约管理服务 =============

def get_appointments_with_pagination(page, per_page=10, status=''):
    """获取预约列表（分页和状态过滤）"""
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Appointment.appointment_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return pagination


def add_new_appointment(form_data):
    """添加新预约"""
    appointment = Appointment(
        patient_id=form_data.get('patient_id', type=int),
        doctor_id=form_data.get('doctor_id', type=int),
        appointment_date=datetime.strptime(form_data.get('appointment_date'), '%Y-%m-%d'),
        appointment_time=form_data.get('appointment_time'),
        department=form_data.get('department'),
        notes=form_data.get('notes')
    )
    db.session.add(appointment)
    db.session.commit()
    return appointment


def get_appointment_by_id(appointment_id):
    """通过ID获取预约信息"""
    return Appointment.query.get_or_404(appointment_id)


def update_appointment_status(appointment_id, status):
    """更新预约状态"""
    appointment = get_appointment_by_id(appointment_id)
    appointment.status = status
    db.session.commit()
    return appointment

def get_all_patients_for_dropdown():
    """获取所有病人用于下拉选择"""
    return Patient.query.all()

