"""
病历记录管理服务
Medical Record Management Services
"""
from models import MedicalRecord
from extensions import db

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

