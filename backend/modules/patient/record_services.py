"""
病历记录管理服务
Medical Record Management Services
"""
from backend.models import MedicalRecord
from backend.extensions import db

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
    # 安全转换ID
    patient_id = form_data.get('patient_id')
    doctor_id = form_data.get('doctor_id')

    # 如果是字符串，转换为整数
    if isinstance(patient_id, str):
        patient_id = int(patient_id) if patient_id else None
    if isinstance(doctor_id, str):
        doctor_id = int(doctor_id) if doctor_id else None

    record = MedicalRecord(
        patient_id=patient_id,
        doctor_id=doctor_id,
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
