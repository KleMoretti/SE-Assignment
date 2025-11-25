"""
病人端门户服务
Patient Portal Services

提供病人端自助服务功能：
- 用户档案管理
- 家庭成员管理
- 病人端预约功能
 - 病历查看功能
 - 权限验证等
"""
from backend.models import User, Patient, PatientUserLink, Appointment, MedicalRecord
from backend.extensions import db
from . import patient_services, appointment_services


# ============= 用户档案管理 =============

def get_user_patient_profile(user_id):
    """
    获取用户关联的病人档案

    Args:
        user_id: 用户ID

    Returns:
        Patient对象，如果不存在则返回None
    """
    link = PatientUserLink.query.filter_by(user_id=user_id).first()
    if link:
        return link.patient
    return None


def create_user_patient_profile(user_id, patient_data):
    """
    为用户创建病人档案并建立关联

    Args:
        user_id: 用户ID
        patient_data: 病人信息字典

    Returns:
        创建的Patient对象

    Raises:
        ValueError: 如果用户已有关联的档案或数据无效
    """
    # 检查用户是否已有关联档案
    existing_link = PatientUserLink.query.filter_by(user_id=user_id).first()
    if existing_link:
        raise ValueError('用户已有关联的病人档案')

    # 创建病人档案
    patient = patient_services.add_new_patient(patient_data)

    # 建立用户与病人的关联
    link = PatientUserLink(user_id=user_id, patient_id=patient.id)
    db.session.add(link)

    # 同时添加到可管理列表
    user = User.query.get(user_id)
    if user:
        user.managed_patients.append(patient)

    db.session.commit()
    return patient


# ============= 家庭成员管理 =============

def get_managed_patients(user_id):
    """
    获取用户可管理的所有病人列表（包括自己和家人）

    Args:
        user_id: 用户ID

    Returns:
        Patient对象列表
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError('用户不存在')

    return user.managed_patients.all()


def add_family_member(user_id, family_username, family_password):
    """
    通过家人的用户名和密码，将家人的病人档案添加到当前用户的管理列表

    Args:
        user_id: 当前用户ID
        family_username: 家人的用户名
        family_password: 家人的密码

    Returns:
        家人的Patient对象

    Raises:
        ValueError: 如果验证失败或家人无病人档案
    """
    # 验证当前用户
    user = User.query.get(user_id)
    if not user:
        raise ValueError('用户不存在')

    # 验证家人的用户名和密码
    family_user = User.query.filter_by(username=family_username).first()
    if not family_user:
        raise ValueError('家人用户不存在')

    if not family_user.check_password(family_password):
        raise ValueError('家人密码错误')

    # 获取家人的病人档案
    family_link = PatientUserLink.query.filter_by(user_id=family_user.id).first()
    if not family_link:
        raise ValueError('该用户没有关联的病人档案')

    family_patient = family_link.patient

    # 检查是否已经在管理列表中
    if family_patient in user.managed_patients:
        raise ValueError('该家人已在您的管理列表中')

    # 添加到管理列表
    user.managed_patients.append(family_patient)
    db.session.commit()

    return family_patient


def remove_family_member(user_id, patient_id):
    """
    从用户的管理列表中移除家人

    Args:
        user_id: 用户ID
        patient_id: 要移除的病人ID

    Raises:
        ValueError: 如果是自己的档案或不在管理列表中
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError('用户不存在')

    # 不能移除自己的档案
    own_link = PatientUserLink.query.filter_by(user_id=user_id).first()
    if own_link and own_link.patient_id == patient_id:
        raise ValueError('不能移除自己的病人档案')

    patient = Patient.query.get(patient_id)
    if not patient:
        raise ValueError('病人不存在')

    if patient not in user.managed_patients:
        raise ValueError('该病人不在您的管理列表中')

    user.managed_patients.remove(patient)
    db.session.commit()


# ============= 病人信息管理 =============

def get_patient_info(patient_id):
    """
    获取病人详细信息

    Args:
        patient_id: 病人ID

    Returns:
        Patient对象

    Raises:
        ValueError: 如果病人不存在
    """
    patient = Patient.query.get(patient_id)
    if not patient:
        raise ValueError('病人不存在')
    return patient


def update_patient_info_by_user(user_id, patient_id, data):
    """
    用户更新病人信息（需要验证权限）

    Args:
        user_id: 用户ID
        patient_id: 病人ID
        data: 更新数据字典

    Returns:
        更新后的Patient对象

    Raises:
        ValueError: 如果无权限或病人不存在
    """
    # 验证权限
    user = User.query.get(user_id)
    if not user:
        raise ValueError('用户不存在')

    patient = Patient.query.get(patient_id)
    if not patient:
        raise ValueError('病人不存在')

    if patient not in user.managed_patients:
        raise ValueError('您没有权限修改此病人信息')

    # 更新信息
    return patient_services.update_patient_info(patient_id, data)


# ============= 预约管理 =============

def get_patient_appointments(patient_id, status=None):
    """
    获取指定病人的预约列表

    Args:
        patient_id: 病人ID
        status: 预约状态过滤（可选）

    Returns:
        Appointment对象列表
    """
    query = Appointment.query.filter_by(patient_id=patient_id)

    if status:
        query = query.filter_by(status=status)

    return query.order_by(Appointment.appointment_date.desc()).all()


def create_appointment_for_patient(patient_id, data):
    """
    为病人创建预约（病人端自助挂号）

    Args:
        patient_id: 病人ID
        data: 预约数据字典

    Returns:
        创建的Appointment对象

    Raises:
        ValueError: 如果数据无效或病人不存在
    """
    patient = Patient.query.get(patient_id)
    if not patient:
        raise ValueError('病人不存在')

    # 确保数据中包含patient_id
    appointment_data = dict(data)
    appointment_data['patient_id'] = patient_id

    # 使用appointment_services创建预约
    return appointment_services.add_new_appointment(appointment_data)


def cancel_patient_appointment(user_id, appointment_id):
    """
    取消预约（需要验证权限）

    Args:
        user_id: 用户ID
        appointment_id: 预约ID

    Returns:
        更新后的Appointment对象

    Raises:
        ValueError: 如果无权限或预约不存在
    """
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        raise ValueError('预约不存在')

    # 验证权限：检查该预约的病人是否在用户的管理列表中
    user = User.query.get(user_id)
    if not user:
        raise ValueError('用户不存在')

    patient = appointment.patient
    if patient not in user.managed_patients:
        raise ValueError('您没有权限取消此预约')

    # 检查预约状态
    if appointment.status == 'cancelled':
        raise ValueError('预约已经被取消')

    if appointment.status == 'completed':
        raise ValueError('已完成的预约无法取消')

    # 使用appointment_services取消预约
    return appointment_services.cancel_appointment(appointment_id)


# ============= 病历管理 =============

def get_patient_medical_records(patient_id):
    """
    获取指定病人的病历记录列表

    Args:
        patient_id: 病人ID

    Returns:
        MedicalRecord对象列表
    """
    return MedicalRecord.query.filter_by(patient_id=patient_id)\
        .order_by(MedicalRecord.visit_date.desc()).all()


def get_medical_record_detail(user_id, record_id):
    """
    获取病历详情（需要验证权限）

    Args:
        user_id: 用户ID
        record_id: 病历ID

    Returns:
        MedicalRecord对象

    Raises:
        ValueError: 如果无权限或病历不存在
    """
    record = MedicalRecord.query.get(record_id)
    if not record:
        raise ValueError('病历不存在')

    # 验证权限
    user = User.query.get(user_id)
    if not user:
        raise ValueError('用户不存在')

    patient = record.patient
    if patient not in user.managed_patients:
        raise ValueError('您没有权限查看此病历')

    return record


# ============= 权限验证辅助函数 =============

def verify_patient_access(user_id, patient_id):
    """
    验证用户是否有权访问指定病人的信息

    Args:
        user_id: 用户ID
        patient_id: 病人ID

    Returns:
        bool: True表示有权限，False表示无权限
    """
    user = User.query.get(user_id)
    if not user:
        return False

    patient = Patient.query.get(patient_id)
    if not patient:
        return False

    return patient in user.managed_patients


def get_user_managed_patient_ids(user_id):
    """
    获取用户可管理的所有病人ID列表

    Args:
        user_id: 用户ID

    Returns:
        病人ID列表
    """
    user = User.query.get(user_id)
    if not user:
        return []

    return [p.id for p in user.managed_patients.all()]
