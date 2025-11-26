"""
挂号预约管理服务
Appointment Management Services
"""
from backend.models import Appointment, Patient, DoctorSchedule
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

    # 检查是否预约过去的时间
    now = datetime.now()
    today = datetime(now.year, now.month, now.day)
    
    # 如果预约日期是今天，需要检查时间是否已过
    if appointment_date.date() == today.date():
        # 解析预约时间（格式如 "09:00" 或 "14:30"）
        try:
            time_parts = appointment_time.split(':')
            appointment_hour = int(time_parts[0])
            appointment_minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            
            # 如果预约时间已经过去，不允许预约
            if appointment_hour < now.hour or (appointment_hour == now.hour and appointment_minute <= now.minute):
                raise ValueError(f"不能预约今日已过去的时间段 {appointment_time}，请选择未来的时间。")
        except (ValueError, IndexError) as e:
            if "不能预约今日已过去的时间段" in str(e):
                raise
            # 时间格式错误，继续执行（后续可能会有其他验证）
            pass
    
    # 检查是否预约过去的日期
    if appointment_date.date() < today.date():
        raise ValueError(f"不能预约过去的日期 {appointment_date_str}，请选择今天或未来的日期。")

    # 检查医生在该日期是否有排班，并验证预约时间是否在排班时间范围内
    doctor_schedules = DoctorSchedule.query.filter(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.date == appointment_date
    ).all()
    
    if not doctor_schedules:
        raise ValueError(f"该医生在 {appointment_date_str} 没有排班，无法预约。请选择其他日期或医生。")
    
    # 验证预约时间是否在任一排班时间段内，并检查该排班是否已满
    appointment_time_valid = False
    matched_schedule = None
    for schedule in doctor_schedules:
        if schedule.start_time and schedule.end_time:
            # 比较时间字符串 (格式: "HH:MM")
            if schedule.start_time <= appointment_time <= schedule.end_time:
                appointment_time_valid = True
                matched_schedule = schedule
                break
    
    if not appointment_time_valid:
        # 构建可用时间段提示
        available_times = [f"{s.start_time}-{s.end_time}" for s in doctor_schedules if s.start_time and s.end_time]
        time_hint = "、".join(available_times) if available_times else "无可用时间段"
        raise ValueError(f"预约时间 {appointment_time} 不在医生的排班时间内。该医生在 {appointment_date_str} 的排班时间为：{time_hint}")
    
    # 检查该排班是否已达到最大接诊数量
    if matched_schedule and matched_schedule.max_patients:
        # 统计该排班当天该医生的有效预约数量（不包括已取消的）
        booked_count = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_(['pending', 'confirmed', 'completed'])
        ).count()
        
        if booked_count >= matched_schedule.max_patients:
            raise ValueError(f"该医生在 {appointment_date_str} 的排班已满（{booked_count}/{matched_schedule.max_patients}），无法继续预约。请选择其他日期或医生。")

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
