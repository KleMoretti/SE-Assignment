"""
病人基本信息管理服务
Patient Information Management Services
"""
from backend.models import Patient
from backend.extensions import db
from sqlalchemy import func

def get_patients_with_pagination(page, per_page=10, search=''):
    """获取病人列表（分页和搜索）"""
    query = Patient.query
    if search:
        query = query.filter(
            (Patient.name.like(f'%{search}%')) |
            (Patient.patient_no.like(f'%{search}%')) |
            (Patient.phone.like(f'%{search}%'))
        )

    pagination = query.order_by(Patient.patient_no.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return pagination


def generate_patient_no():
    """生成下一个病人编号，如 P00000001、P00000002 ..."""
    max_no = db.session.query(func.max(Patient.patient_no)).scalar()
    if not max_no:
        return 'P00000001'
    # 假设格式为以字母开头 + 数字，比如 P00000001
    prefix = max_no[0]
    numeric_part = max_no[1:]
    try:
        num = int(numeric_part)
    except (TypeError, ValueError):
        # 如果现有数据格式不符合预期，就从 0 开始
        num = 0
    return f"{prefix}{num + 1:08d}"


def add_new_patient(form_data):
    """添加新病人，支持表单和 JSON 数据"""
    # 将传入的数据统一转换为 dict，便于处理
    try:
        data = dict(form_data)
    except Exception:
        data = form_data or {}

    # patient_no：表单提交时通常会传；API 调用时可以不传，由后端自动生成
    patient_no = data.get('patient_no')
    if not patient_no:
        patient_no = generate_patient_no()

    # 安全转换年龄
    raw_age = data.get('age')
    try:
        age = int(raw_age) if raw_age not in (None, '') else None
    except (TypeError, ValueError):
        age = None

    patient = Patient(
        patient_no=patient_no,
        name=data.get('name'),
        gender=data.get('gender'),
        age=age,
        phone=data.get('phone'),
        id_card=data.get('id_card'),
        address=data.get('address'),
        emergency_contact=data.get('emergency_contact'),
        emergency_phone=data.get('emergency_phone')
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

    # 安全地转换年龄
    raw_age = form_data.get('age')
    try:
        age = int(raw_age) if raw_age not in (None, '') else None
    except (TypeError, ValueError):
        age = None
    patient.age = age

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
