"""
病人基本信息管理服务
Patient Information Management Services
"""
from backend.models import Patient
from backend.extensions import db

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

def get_all_patients_for_dropdown():
    """获取所有病人用于下拉选择"""
    return Patient.query.all()

