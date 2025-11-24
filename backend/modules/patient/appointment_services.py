"""
挂号预约管理服务
Appointment Management Services
"""
from backend.models import Appointment, Patient
from backend.extensions import db
from datetime import datetime

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
    patient_id = form_data.get('patient_id')
    doctor_id = form_data.get('doctor_id')

    # 验证 patient_id 是否存在
    if patient_id:
        patient = Patient.query.get(patient_id)
        if not patient:
            # 如果前端传来的 patient_id 无效，则拒绝创建
            raise ValueError(f"无效的病人ID: {patient_id}，找不到对应的病人档案。")
    else:
        # 如果前端没有传来 patient_id，也拒绝创建
        raise ValueError("创建预约必须提供病人ID。")

    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
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


def cancel_appointment(appointment_id):
    """取消预约"""
    appointment = get_appointment_by_id(appointment_id)
    if appointment.status == 'cancelled':
        raise ValueError("该预约已被取消")
    if appointment.status == 'completed':
        raise ValueError("已完成的预约不能取消")

    appointment.status = 'cancelled'
    db.session.commit()
    return appointment
