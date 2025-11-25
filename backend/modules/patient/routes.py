"""
病人管理子系统 - 路由
Patient Management - Routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from . import patient_bp
from extensions import db
from . import patient_services, record_services, appointment_services
from . import portal_services  # 病人端门户服务


# ============= 统一响应格式 =============

def success_response(data=None, message='操作成功', code='SUCCESS'):
    """成功响应"""
    return jsonify({
        'success': True,
        'message': message,
        'code': code,
        'data': data
    })


def error_response(message='操作失败', code='ERROR', status_code=400):
    """错误响应"""
    return jsonify({
        'success': False,
        'message': message,
        'code': code,
        'data': None
    }), status_code


# ============= 传统视图路由 (HTML) =============

@patient_bp.route('/')
def index():
    """病人管理首页"""
    return render_template('patient/patient_index.html')


# --- 病人信息视图 ---

@patient_bp.route('/list')
def view_patient_list():
    """病人列表页面"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    pagination = patient_services.get_patients_with_pagination(page=page, search=search)
    patients = pagination.items
    
    return render_template('patient/patient_list.html',
                         patients=patients,
                         pagination=pagination,
                         search=search)


@patient_bp.route('/add', methods=['GET', 'POST'])
def view_patient_add():
    """添加病人页面"""
    if request.method == 'POST':
        print('>>> [view_patient_add] 收到表单提交')  # 加这一行

        try:
            patient_services.add_new_patient(request.form)
            flash('病人信息添加成功！', 'success')
            return redirect(url_for('patient.view_patient_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    return render_template('patient/patient_form.html', patient=None)


@patient_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def view_patient_edit(id):
    """编辑病人信息页面"""
    patient = patient_services.get_patient_by_id(id)

    if request.method == 'POST':
        try:
            patient_services.update_patient_info(id, request.form)
            flash('病人信息更新成功！', 'success')
            return redirect(url_for('patient.view_patient_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('patient/patient_form.html', patient=patient)


@patient_bp.route('/delete/<int:id>', methods=['POST'])
def view_patient_delete(id):
    """删除病人动作"""
    try:
        patient_services.delete_patient_by_id(id)
        flash('病人信息已删除！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('patient.view_patient_list'))


@patient_bp.route('/detail/<int:id>')
def view_patient_detail(id):
    """病人详情页面"""
    patient = patient_services.get_patient_by_id(id)
    return render_template('patient/patient_detail.html', patient=patient)


# --- 病历记录视图 ---

@patient_bp.route('/medical-records/list')
def view_medical_record_list():
    """病历列表页面"""
    page = request.args.get('page', 1, type=int)
    patient_id = request.args.get('patient_id', type=int)
    
    pagination = record_services.get_medical_records_with_pagination(page=page, patient_id=patient_id)
    records = pagination.items
    
    return render_template('patient/medical_record_list.html',
                         records=records,
                         pagination=pagination,
                         patient_id=patient_id)


@patient_bp.route('/medical-records/add', methods=['GET', 'POST'])
def view_medical_record_add():
    """添加病历页面"""
    if request.method == 'POST':
        try:
            record_services.add_new_medical_record(request.form)
            flash('病历添加成功！', 'success')
            return redirect(url_for('patient.view_medical_record_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    patients = patient_services.get_all_patients_for_dropdown()
    return render_template('patient/medical_record_form.html', record=None, patients=patients)


@patient_bp.route('/medical-records/detail/<int:id>')
def view_medical_record_detail(id):
    """病历详情页面"""
    record = record_services.get_medical_record_by_id(id)
    return render_template('patient/medical_record_detail.html', record=record)


# --- 挂号预约视图 ---

@patient_bp.route('/appointments/list')
def view_appointment_list():
    """预约列表页面"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    pagination = appointment_services.get_appointments_with_pagination(page=page, status=status)
    appointments = pagination.items
    
    return render_template('patient/appointment_list.html',
                         appointments=appointments,
                         pagination=pagination,
                         status=status)


@patient_bp.route('/appointments/add', methods=['GET', 'POST'])
def view_appointment_add():
    """添加预约页面"""
    if request.method == 'POST':
        try:
            appointment_services.add_new_appointment(request.form)
            flash('预约添加成功！', 'success')
            return redirect(url_for('patient.view_appointment_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建预约失败: {str(e)}', 'error')

    from backend.models import Doctor
    from datetime import date

    patients = patient_services.get_all_patients_for_dropdown()
    doctors = Doctor.query.filter_by(status='active').order_by(Doctor.department, Doctor.name).all()
    today = date.today().strftime('%Y-%m-%d')

    return render_template('patient/appointment_form.html',
                         appointment=None,
                         patients=patients,
                         doctors=doctors,
                         today=today)


@patient_bp.route('/appointments/update-status/<int:id>', methods=['POST'])
def view_appointment_update_status(id):
    """更新预约状态动作"""
    try:
        status = request.form.get('status')
        appointment_services.update_appointment_status(id, status)
        flash('预约状态更新成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失败：{str(e)}', 'error')
    
    return redirect(url_for('patient.view_appointment_list'))


# ============= RESTful API (JSON) =============

# --- 病人管理 API ---

@patient_bp.route('/patients', methods=['GET'])
def api_get_patients():
    """获取病人列表 (API)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')

        pagination = patient_services.get_patients_with_pagination(page=page, per_page=per_page, search=search)
        patients_data = [p.to_dict() for p in pagination.items]

        return success_response({
            'items': patients_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(f'获取病人列表失败: {str(e)}', 'GET_PATIENTS_ERROR', 500)


@patient_bp.route('/patients/<int:id>', methods=['GET'])
def api_get_patient(id):
    """获取单个病人详情 (API)"""
    try:
        patient = patient_services.get_patient_by_id(id)
        return success_response(patient.to_dict())
    except Exception as e:
        return error_response(f'获取病人详情失败: {str(e)}', 'GET_PATIENT_ERROR', 404)


@patient_bp.route('/patients', methods=['POST'])
def api_create_patient():
    """创建新病人 (API)"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        patient = patient_services.add_new_patient(data)
        return success_response(patient.to_dict(), '病人创建成功', 'PATIENT_CREATED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建病人失败: {str(e)}', 'CREATE_PATIENT_ERROR', 500)


@patient_bp.route('/patients/<int:id>', methods=['PUT'])
def api_update_patient(id):
    """更新病人信息 (API)"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        patient = patient_services.update_patient_info(id, data)
        return success_response(patient.to_dict(), '病人信息更新成功', 'PATIENT_UPDATED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新病人信息失败: {str(e)}', 'UPDATE_PATIENT_ERROR', 500)


@patient_bp.route('/patients/<int:id>', methods=['DELETE'])
def api_delete_patient(id):
    """删除病人 (API)"""
    try:
        patient_services.delete_patient_by_id(id)
        return success_response(None, '病人删除成功', 'PATIENT_DELETED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除病人失败: {str(e)}', 'DELETE_PATIENT_ERROR', 500)


# --- 挂号预约管理 API ---

@patient_bp.route('/appointments', methods=['GET'])
def api_get_appointments():
    """获取预约列表 (API)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')

        pagination = appointment_services.get_appointments_with_pagination(
            page=page,
            per_page=per_page,
            status=status
        )
        items = [a.to_dict() for a in pagination.items]

        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(f'获取预约列表失败: {str(e)}', 'GET_APPOINTMENTS_ERROR', 500)


@patient_bp.route('/appointments', methods=['POST'])
def api_create_appointment():
    """创建新预约 (API)"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        appointment = appointment_services.add_new_appointment(data)
        return success_response(appointment.to_dict(), '预约创建成功', 'APPOINTMENT_CREATED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建预约失败: {str(e)}', 'CREATE_APPOINTMENT_ERROR', 500)


@patient_bp.route('/appointments/<int:id>/status', methods=['PUT'])
def api_update_appointment_status(id):
    """更新预约状态 (API)"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return error_response('缺少状态信息', 'INVALID_DATA')

        appointment = appointment_services.update_appointment_status(id, data['status'])
        return success_response(appointment.to_dict(), '预约状态更新成功', 'APPOINTMENT_STATUS_UPDATED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新预约状态失败: {str(e)}', 'UPDATE_APPOINTMENT_STATUS_ERROR', 500)


@patient_bp.route('/appointments/<int:id>/cancel', methods=['PUT', 'POST'])
def api_cancel_appointment(id):
    """取消预约 (API)"""
    try:
        appointment = appointment_services.cancel_appointment(id)
        return success_response(appointment.to_dict(), '预约已取消', 'APPOINTMENT_CANCELLED')
    except ValueError as e:
        return error_response(str(e), 'CANCEL_FAILED', 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f'取消预约失败: {str(e)}', 'CANCEL_APPOINTMENT_ERROR', 500)


# --- 病历记录管理 API ---

@patient_bp.route('/medical-records', methods=['GET'])
def api_get_medical_records():
    """获取病历列表 (API)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        patient_id = request.args.get('patient_id', type=int)

        pagination = record_services.get_medical_records_with_pagination(
            page=page,
            per_page=per_page,
            patient_id=patient_id
        )
        items = [r.to_dict() for r in pagination.items]

        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(f'获取病历列表失败: {str(e)}', 'GET_MEDICAL_RECORDS_ERROR', 500)


@patient_bp.route('/medical-records', methods=['POST'])
def api_create_medical_record():
    """创建新病历 (API)"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        record = record_services.add_new_medical_record(data)
        return success_response(record.to_dict(), '病历创建成功', 'RECORD_CREATED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建病历失败: {str(e)}', 'CREATE_RECORD_ERROR', 500)


# ============= 病人端门户 API (Patient Portal) =============

def get_current_user_id():
    """获取当前登录用户ID（临时实现）"""
    # TODO: 实现真实的用户认证，可以使用 Flask-Login 或 JWT
    user_id = session.get('user_id')
    if not user_id:
        # 开发测试用：如果没有登录，使用请求头中的用户ID
        user_id = request.headers.get('X-User-Id', 1)
    return int(user_id)


@patient_bp.route('/portal/profile', methods=['GET'])
def portal_get_profile():
    """获取当前用户的病人档案"""
    try:
        user_id = get_current_user_id()
        patient = portal_services.get_user_patient_profile(user_id)

        if not patient:
            return error_response('您还没有关联的病人档案', 'NO_PROFILE', 404)

        return success_response(patient.to_dict())
    except Exception as e:
        return error_response(f'获取用户档案失败: {str(e)}', 'GET_PROFILE_ERROR', 500)


@patient_bp.route('/portal/managed-patients', methods=['GET'])
def portal_get_managed_patients():
    """获取可管理的所有病人列表（自己和家人）"""
    try:
        user_id = get_current_user_id()
        patients = portal_services.get_managed_patients(user_id)
        patients_data = [p.to_dict() for p in patients]

        return success_response(patients_data)
    except Exception as e:
        return error_response(f'获取家庭成员列表失败: {str(e)}', 'GET_MANAGED_PATIENTS_ERROR', 500)


@patient_bp.route('/portal/family-members/add', methods=['POST'])
def portal_add_family_member():
    """添加家庭成员"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return error_response('请提供家人的用户名和密码', 'INVALID_DATA')

        family_patient = portal_services.add_family_member(user_id, username, password)

        return success_response(
            family_patient.to_dict(),
            '家庭成员添加成功',
            'FAMILY_MEMBER_ADDED'
        )
    except ValueError as e:
        return error_response(str(e), 'ADD_FAMILY_MEMBER_FAILED', 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f'添加家庭成员失败: {str(e)}', 'ADD_FAMILY_MEMBER_ERROR', 500)


@patient_bp.route('/portal/patients/<int:patient_id>/appointments', methods=['GET'])
def portal_get_patient_appointments(patient_id):
    """获取指定病人的预约列表"""
    try:
        user_id = get_current_user_id()

        # 验证权限
        managed_patients = portal_services.get_managed_patients(user_id)
        if patient_id not in [p.id for p in managed_patients]:
            return error_response('您没有权限查看此病人的预约', 'FORBIDDEN', 403)

        status = request.args.get('status', None)
        appointments = portal_services.get_patient_appointments(patient_id, status)
        appointments_data = [a.to_dict() for a in appointments]

        return success_response(appointments_data)
    except Exception as e:
        return error_response(f'获取预约列表失败: {str(e)}', 'GET_APPOINTMENTS_ERROR', 500)


@patient_bp.route('/portal/patients/<int:patient_id>/medical-records', methods=['GET'])
def portal_get_patient_medical_records(patient_id):
    """获取指定病人的病历记录"""
    try:
        user_id = get_current_user_id()

        # 验证权限
        managed_patients = portal_services.get_managed_patients(user_id)
        if patient_id not in [p.id for p in managed_patients]:
            return error_response('您没有权限查看此病人的病历', 'FORBIDDEN', 403)

        records = portal_services.get_patient_medical_records(patient_id)
        records_data = [r.to_dict() for r in records]

        return success_response(records_data)
    except Exception as e:
        return error_response(f'获取病历列表失败: {str(e)}', 'GET_RECORDS_ERROR', 500)


@patient_bp.route('/portal/appointments', methods=['POST'])
def portal_create_appointment():
    """创建预约（病人端自助挂号）"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        patient_id = data.get('patient_id')
        if not patient_id:
            return error_response('请指定病人ID', 'INVALID_DATA')

        # 验证权限
        managed_patients = portal_services.get_managed_patients(user_id)
        if patient_id not in [p.id for p in managed_patients]:
            return error_response('您没有权限为此病人预约', 'FORBIDDEN', 403)

        appointment = portal_services.create_appointment_for_patient(patient_id, data)

        return success_response(
            appointment.to_dict(),
            '预约创建成功',
            'APPOINTMENT_CREATED'
        )
    except ValueError as e:
        return error_response(str(e), 'CREATE_APPOINTMENT_FAILED', 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建预约失败: {str(e)}', 'CREATE_APPOINTMENT_ERROR', 500)


@patient_bp.route('/portal/appointments/<int:appointment_id>/cancel', methods=['PUT', 'POST'])
def portal_cancel_appointment(appointment_id):
    """取消预约"""
    try:
        user_id = get_current_user_id()
        appointment = portal_services.cancel_patient_appointment(user_id, appointment_id)

        return success_response(
            appointment.to_dict(),
            '预约已取消',
            'APPOINTMENT_CANCELLED'
        )
    except ValueError as e:
        return error_response(str(e), 'CANCEL_APPOINTMENT_FAILED', 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f'取消预约失败: {str(e)}', 'CANCEL_APPOINTMENT_ERROR', 500)


@patient_bp.route('/portal/patients/<int:patient_id>', methods=['GET'])
def portal_get_patient_detail(patient_id):
    """获取病人详细信息"""
    try:
        user_id = get_current_user_id()

        # 验证权限
        managed_patients = portal_services.get_managed_patients(user_id)
        if patient_id not in [p.id for p in managed_patients]:
            return error_response('您没有权限查看此病人信息', 'FORBIDDEN', 403)

        patient = portal_services.get_patient_info(patient_id)
        return success_response(patient.to_dict())
    except ValueError as e:
        return error_response(str(e), 'GET_PATIENT_FAILED', 404)
    except Exception as e:
        return error_response(f'获取病人信息失败: {str(e)}', 'GET_PATIENT_ERROR', 500)


@patient_bp.route('/portal/patients/<int:patient_id>', methods=['PUT'])
def portal_update_patient_info(patient_id):
    """更新病人信息"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        patient = portal_services.update_patient_info_by_user(user_id, patient_id, data)

        return success_response(
            patient.to_dict(),
            '病人信息更新成功',
            'PATIENT_UPDATED'
        )
    except ValueError as e:
        return error_response(str(e), 'UPDATE_PATIENT_FAILED', 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新病人信息失败: {str(e)}', 'UPDATE_PATIENT_ERROR', 500)


# --- 新增：病人关系管理 API（保留兼容性）---

@patient_bp.route('/managed-patients', methods=['GET'])
def api_get_managed_patients():
    """获取当前用户可管理的所有病人列表（自己和家人）- 兼容旧接口"""
    return portal_get_managed_patients()


@patient_bp.route('/managed-patients/add', methods=['POST'])
def api_add_managed_patient():
    """为当前用户添加一个可管理的病人（家人）- 兼容旧接口"""
    return portal_add_family_member()
