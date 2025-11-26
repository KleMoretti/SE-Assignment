"""
挂号预约管理服务
Appointment Management Services
"""
from backend.models import Appointment, Patient
from backend.extensions import db
from datetime import datetime

def generate_appointment_no():
    """生成预约编号 格式: AP + 年月日 + 4位顺序号（从0000开始）"""
    date_str = datetime.now().strftime('%Y%m%d')
    prefix = f'AP{date_str}'

    # 查找当天最大的预约编号
    last_appointment = Appointment.query.filter(
        Appointment.appointment_no.like(f'{prefix}%')
    ).order_by(Appointment.appointment_no.desc()).first()

    if last_appointment:
        # 提取最后四位数字并加1
        last_num = int(last_appointment.appointment_no[-4:])
        new_num = last_num + 1
    else:
        # 当天第一个预约，从0000开始
        new_num = 0

    # 格式化为4位数字（补零）
    return f'{prefix}{new_num:04d}'

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
    appointment_date_str = form_data.get('appointment_date')
    appointment_time = form_data.get('appointment_time')

    # 验证 patient_id 是否存在
    if patient_id:
        patient = Patient.query.get(patient_id)
        if not patient:
            # 如果前端传来的 patient_id 无效，则拒绝创建
            raise ValueError(f"无效的病人ID: {patient_id}，找不到对应的病人档案。")
    else:
        # 如果前端没有传来 patient_id，也拒绝创建
        raise ValueError("创建预约必须提供病人ID。")

    # 验证必填字段
    if not doctor_id:
        raise ValueError("创建预约必须提供医生ID。")
    if not appointment_date_str:
        raise ValueError("创建预约必须提供预约日期。")
    if not appointment_time:
        raise ValueError("创建预约必须提供预约时间。")

    # 转换日期
    appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d')

    # 检查医生在该时间段是否已有预约（排除已取消的预约）
    existing_doctor_appointment = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status.in_(['pending', 'confirmed'])
    ).first()

    if existing_doctor_appointment:
        raise ValueError(f"该医生在 {appointment_date_str} {appointment_time} 已有预约，请选择其他时间段。")

    # 检查病人在该时间段是否已有预约（排除已取消的预约）
    existing_patient_appointment = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status.in_(['pending', 'confirmed'])
    ).first()

    if existing_patient_appointment:
        raise ValueError(f"您在 {appointment_date_str} {appointment_time} 已有预约，不能重复预约。")

    # 生成唯一的预约编号
    appointment_no = generate_appointment_no()

    appointment = Appointment(
        appointment_no=appointment_no,
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
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
