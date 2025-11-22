"""
医生管理子系统 - 路由
Doctor Management - Routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from . import doctor_bp
from models import Doctor, DoctorSchedule, DoctorPerformance, Appointment, MedicalRecord
from extensions import db
from datetime import datetime, date
from sqlalchemy import func, extract
from .utils import (
    validate_doctor_data, validate_schedule_data, validate_performance_data,
    check_schedule_conflict_enhanced, log_operation,
    validate_with_schema, log_operation_decorator
)
from .schemas import DoctorSchema, DoctorScheduleSchema, DoctorPerformanceSchema
from marshmallow import ValidationError


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


# ============= RESTful API - 医生信息管理 =============

@doctor_bp.route('/doctors', methods=['GET'])
def get_doctors():
    """获取医生列表（API）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        department = request.args.get('department', '')
        status = request.args.get('status', '')
        title = request.args.get('title', '')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        education = request.args.get('education', '')
        
        # 构建查询
        query = Doctor.query
        
        # 搜索过滤
        if search:
            query = query.filter(
                (Doctor.name.like(f'%{search}%')) | 
                (Doctor.doctor_no.like(f'%{search}%')) |
                (Doctor.phone.like(f'%{search}%')) |
                (Doctor.email.like(f'%{search}%'))
            )
        
        # 科室过滤
        if department:
            query = query.filter_by(department=department)
        
        # 状态过滤
        if status:
            query = query.filter_by(status=status)
        
        # 职称过滤
        if title:
            query = query.filter_by(title=title)
        
        # 年龄范围过滤
        if min_age is not None:
            query = query.filter(Doctor.age >= min_age)
        if max_age is not None:
            query = query.filter(Doctor.age <= max_age)
        
        # 学历过滤
        if education:
            query = query.filter_by(education=education)
        
        # 分页
        pagination = query.order_by(Doctor.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 序列化数据并附加统计字段（总接诊人数、总排班数）
        doctors = pagination.items
        doctor_ids = [d.id for d in doctors]

        if doctor_ids:
            # 按医生统计预约数量
            appointment_counts = dict(
                db.session.query(Appointment.doctor_id, func.count(Appointment.id))
                .filter(Appointment.doctor_id.in_(doctor_ids))
                .group_by(Appointment.doctor_id)
                .all()
            )

            # 按医生统计排班数量
            schedule_counts = dict(
                db.session.query(DoctorSchedule.doctor_id, func.count(DoctorSchedule.id))
                .filter(DoctorSchedule.doctor_id.in_(doctor_ids))
                .group_by(DoctorSchedule.doctor_id)
                .all()
            )
        else:
            appointment_counts = {}
            schedule_counts = {}

        doctors_data = []
        for d in doctors:
            data = d.to_dict()
            # 与单个医生详情接口中的字段命名保持一致
            data['total_patients'] = appointment_counts.get(d.id, 0)
            data['total_schedules'] = schedule_counts.get(d.id, 0)
            doctors_data.append(data)
        
        return success_response({
            'items': doctors_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    
    except Exception as e:
        return error_response(f'获取医生列表失败：{str(e)}', 'GET_DOCTORS_ERROR', 500)


@doctor_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    """获取医生详情（API）"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        doctor_data = doctor.to_dict()
        
        # 附加统计信息 - 安全处理表不存在的情况
        try:
            total_appointments = Appointment.query.filter_by(doctor_id=doctor_id).count()
            completed_appointments = Appointment.query.filter_by(
                doctor_id=doctor_id, status='completed'
            ).count()
        except Exception:
            # 如果appointments表不存在，使用默认值
            total_appointments = 0
            completed_appointments = 0
        
        try:
            total_medical_records = MedicalRecord.query.filter_by(doctor_id=doctor_id).count()
        except Exception:
            total_medical_records = 0
        
        try:
            total_schedules = DoctorSchedule.query.filter_by(doctor_id=doctor_id).count()
        except Exception:
            total_schedules = 0
        
        doctor_data['statistics'] = {
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'total_medical_records': total_medical_records,
            'total_schedules': total_schedules
        }
        
        return success_response(doctor_data)
    
    except Exception as e:
        return error_response(f'获取医生详情失败：{str(e)}', 'GET_DOCTOR_ERROR', 500)


@doctor_bp.route('/doctors', methods=['POST'])
def create_doctor():
    """创建医生（API）"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        # 使用Schema进行数据验证
        schema = DoctorSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            log_operation('create', 'doctor', status='failed', 
                         error_message=f'数据验证失败: {err.messages}')
            return error_response(f'数据验证失败：{err.messages}', 'VALIDATION_ERROR')
        
        # 检查医生编号是否已存在
        if Doctor.query.filter_by(doctor_no=validated_data['doctor_no']).first():
            log_operation('create', 'doctor', status='failed', 
                         error_message='医生编号已存在')
            return error_response('医生编号已存在', 'DOCTOR_NO_EXISTS')
        
        # 创建医生
        doctor = Doctor(**validated_data)
        
        db.session.add(doctor)
        db.session.commit()
        
        # 记录操作日志
        log_operation('create', 'doctor', resource_id=doctor.id, 
                     resource_name=doctor.name, status='success',
                     details={'doctor_no': doctor.doctor_no, 'department': doctor.department})
        
        return success_response(doctor.to_dict(), '医生创建成功', 'DOCTOR_CREATED')
    
    except Exception as e:
        db.session.rollback()
        log_operation('create', 'doctor', status='failed', error_message=str(e))
        return error_response(f'创建医生失败：{str(e)}', 'CREATE_DOCTOR_ERROR', 500)


@doctor_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    """更新医生信息（API）"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        # 使用Schema进行部分数据验证（partial=True允许部分更新）
        schema = DoctorSchema(partial=True)
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            log_operation('update', 'doctor', resource_id=doctor_id, 
                         resource_name=doctor.name, status='failed',
                         error_message=f'数据验证失败: {err.messages}')
            return error_response(f'数据验证失败：{err.messages}', 'VALIDATION_ERROR')
        
        # 记录旧值用于日志
        old_values = {
            'name': doctor.name,
            'department': doctor.department,
            'status': doctor.status
        }
        
        # 更新字段
        for key, value in validated_data.items():
            setattr(doctor, key, value)
        
        db.session.commit()
        
        # 记录操作日志
        log_operation('update', 'doctor', resource_id=doctor.id, 
                     resource_name=doctor.name, status='success',
                     details={'old_values': old_values, 'updated_fields': list(validated_data.keys())})
        
        return success_response(doctor.to_dict(), '医生信息更新成功', 'DOCTOR_UPDATED')
    
    except Exception as e:
        db.session.rollback()
        log_operation('update', 'doctor', resource_id=doctor_id, 
                     status='failed', error_message=str(e))
        return error_response(f'更新医生信息失败：{str(e)}', 'UPDATE_DOCTOR_ERROR', 500)


@doctor_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    """删除医生（API）"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        doctor_name = doctor.name
        doctor_no = doctor.doctor_no
        
        # 检查是否有关联的预约或病历
        appointment_count = Appointment.query.filter_by(doctor_id=doctor_id).count()
        if appointment_count > 0:
            log_operation('delete', 'doctor', resource_id=doctor_id, 
                         resource_name=doctor_name, status='failed',
                         error_message=f'该医生有 {appointment_count} 条关联预约记录')
            return error_response(
                f'该医生有 {appointment_count} 条关联预约记录，无法删除',
                'DOCTOR_HAS_APPOINTMENTS'
            )
        
        medical_record_count = MedicalRecord.query.filter_by(doctor_id=doctor_id).count()
        if medical_record_count > 0:
            log_operation('delete', 'doctor', resource_id=doctor_id, 
                         resource_name=doctor_name, status='failed',
                         error_message=f'该医生有 {medical_record_count} 条关联病历记录')
            return error_response(
                f'该医生有 {medical_record_count} 条关联病历记录，无法删除',
                'DOCTOR_HAS_MEDICAL_RECORDS'
            )
        
        db.session.delete(doctor)
        db.session.commit()
        
        # 记录操作日志
        log_operation('delete', 'doctor', resource_id=doctor_id, 
                     resource_name=doctor_name, status='success',
                     details={'doctor_no': doctor_no})
        
        return success_response(None, '医生删除成功', 'DOCTOR_DELETED')
    
    except Exception as e:
        db.session.rollback()
        log_operation('delete', 'doctor', resource_id=doctor_id, 
                     status='failed', error_message=str(e))
        return error_response(f'删除医生失败：{str(e)}', 'DELETE_DOCTOR_ERROR', 500)


@doctor_bp.route('/doctors/statistics', methods=['GET'])
def get_doctors_statistics():
    """获取医生统计数据（API）"""
    try:
        # 总医生数
        total_doctors = Doctor.query.count()
        
        # 在职医生数
        active_doctors = Doctor.query.filter_by(status='active').count()
        
        # 离职医生数
        inactive_doctors = Doctor.query.filter_by(status='inactive').count()
        
        # 按科室统计
        department_stats = db.session.query(
            Doctor.department,
            func.count(Doctor.id).label('count')
        ).filter(
            Doctor.department.isnot(None)
        ).group_by(
            Doctor.department
        ).all()
        
        department_data = [
            {'department': dept, 'count': count}
            for dept, count in department_stats
        ]
        
        # 按职称统计
        title_stats = db.session.query(
            Doctor.title,
            func.count(Doctor.id).label('count')
        ).filter(
            Doctor.title.isnot(None)
        ).group_by(
            Doctor.title
        ).all()
        
        title_data = [
            {'title': title, 'count': count}
            for title, count in title_stats
        ]
        
        # 获取所有科室列表
        departments = db.session.query(Doctor.department).filter(
            Doctor.department.isnot(None)
        ).distinct().all()
        department_list = [d[0] for d in departments]
        
        # 获取所有职称列表
        titles = db.session.query(Doctor.title).filter(
            Doctor.title.isnot(None)
        ).distinct().all()
        title_list = [t[0] for t in titles]
        
        return success_response({
            'total_doctors': total_doctors,
            'active_doctors': active_doctors,
            'inactive_doctors': inactive_doctors,
            'by_department': department_data,
            'by_title': title_data,
            'departments': department_list,
            'titles': title_list
        })
    
    except Exception as e:
        return error_response(f'获取统计数据失败：{str(e)}', 'GET_STATISTICS_ERROR', 500)


# ============= 传统视图（兼容现有模板） =============

@doctor_bp.route('/')
def index():
    """医生管理首页"""
    return render_template('doctor_index.html')


@doctor_bp.route('/list')
def doctor_list():
    """医生列表页面"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    department = request.args.get('department', '')
    
    query = Doctor.query
    if search:
        query = query.filter(
            (Doctor.name.like(f'%{search}%')) | 
            (Doctor.doctor_no.like(f'%{search}%'))
        )
    if department:
        query = query.filter_by(department=department)
    
    pagination = query.order_by(Doctor.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    doctors = pagination.items
    
    # 获取所有科室用于筛选
    departments = db.session.query(Doctor.department).distinct().all()
    departments = [d[0] for d in departments if d[0]]
    
    return render_template('doctor/doctor_list.html', 
                         doctors=doctors, 
                         pagination=pagination,
                         search=search,
                         department=department,
                         departments=departments)


@doctor_bp.route('/doctor/add', methods=['GET', 'POST'])
def doctor_add():
    """添加医生"""
    if request.method == 'POST':
        try:
            hire_date_str = request.form.get('hire_date')
            hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date() if hire_date_str else None
            
            doctor = Doctor(
                doctor_no=request.form.get('doctor_no'),
                name=request.form.get('name'),
                gender=request.form.get('gender'),
                age=request.form.get('age', type=int),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                department=request.form.get('department'),
                title=request.form.get('title'),
                specialty=request.form.get('specialty'),
                education=request.form.get('education'),
                hire_date=hire_date
            )
            db.session.add(doctor)
            db.session.commit()
            flash('医生信息添加成功！', 'success')
            return redirect(url_for('doctor.doctor_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    return render_template('doctor/doctor_form.html', doctor=None)


@doctor_bp.route('/doctor/edit/<int:id>', methods=['GET', 'POST'])
def doctor_edit(id):
    """编辑医生信息"""
    doctor = Doctor.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            hire_date_str = request.form.get('hire_date')
            hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date() if hire_date_str else None
            
            doctor.name = request.form.get('name')
            doctor.gender = request.form.get('gender')
            doctor.age = request.form.get('age', type=int)
            doctor.phone = request.form.get('phone')
            doctor.email = request.form.get('email')
            doctor.department = request.form.get('department')
            doctor.title = request.form.get('title')
            doctor.specialty = request.form.get('specialty')
            doctor.education = request.form.get('education')
            doctor.hire_date = hire_date
            doctor.status = request.form.get('status')
            
            db.session.commit()
            flash('医生信息更新成功！', 'success')
            return redirect(url_for('doctor.doctor_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('doctor/doctor_form.html', doctor=doctor)


@doctor_bp.route('/doctor/delete/<int:id>', methods=['POST'])
def doctor_delete(id):
    """删除医生"""
    try:
        doctor = Doctor.query.get_or_404(id)
        db.session.delete(doctor)
        db.session.commit()
        flash('医生信息已删除！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('doctor.doctor_list'))


@doctor_bp.route('/doctor/detail/<int:id>')
def doctor_detail(id):
    """医生详情"""
    doctor = Doctor.query.get_or_404(id)
    return render_template('doctor/doctor_detail.html', doctor=doctor)


# ============= RESTful API - 医生排班管理 =============

@doctor_bp.route('/schedules', methods=['GET'])
def get_schedules():
    """获取排班列表（API）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        date_str = request.args.get('date', '')
        shift = request.args.get('shift', '')
        status = request.args.get('status', '')
        
        # 构建查询
        query = DoctorSchedule.query
        
        # 医生过滤
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        
        # 日期过滤
        if date_str:
            try:
                schedule_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                query = query.filter_by(date=schedule_date)
            except ValueError:
                return error_response('日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
        
        # 班次过滤
        if shift:
            query = query.filter_by(shift=shift)
        
        # 状态过滤
        if status:
            query = query.filter_by(status=status)
        
        # 分页
        pagination = query.order_by(DoctorSchedule.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 序列化数据
        schedules_data = [schedule.to_dict() for schedule in pagination.items]
        
        return success_response({
            'list': schedules_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    
    except Exception as e:
        return error_response(f'获取排班列表失败：{str(e)}', 'GET_SCHEDULES_ERROR', 500)


@doctor_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """获取排班详情（API）"""
    try:
        schedule = DoctorSchedule.query.get(schedule_id)
        if not schedule:
            return error_response('排班不存在', 'SCHEDULE_NOT_FOUND', 404)
        
        return success_response(schedule.to_dict())
    
    except Exception as e:
        return error_response(f'获取排班详情失败：{str(e)}', 'GET_SCHEDULE_ERROR', 500)


@doctor_bp.route('/schedules', methods=['POST'])
def create_schedule():
    """创建排班（API）"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        # 使用Schema进行数据验证
        schema = DoctorScheduleSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            log_operation('create', 'schedule', status='failed', 
                         error_message=f'数据验证失败: {err.messages}')
            return error_response(f'数据验证失败：{err.messages}', 'VALIDATION_ERROR')
        
        # 验证医生是否存在
        doctor = Doctor.query.get(validated_data['doctor_id'])
        if not doctor:
            log_operation('create', 'schedule', status='failed', 
                         error_message='医生不存在')
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        # 排班冲突检测（增强版）
        has_conflict, conflict_msg = check_schedule_conflict_enhanced(
            doctor_id=validated_data['doctor_id'],
            schedule_date=validated_data['date'],
            shift=validated_data['shift'],
            start_time=validated_data.get('start_time'),
            end_time=validated_data.get('end_time')
        )
        
        if has_conflict:
            log_operation('create', 'schedule', 
                         resource_name=f"{doctor.name}-{validated_data['date']}-{validated_data['shift']}",
                         status='failed', error_message=conflict_msg)
            return error_response(conflict_msg, 'SCHEDULE_CONFLICT')
        
        # 创建排班
        schedule = DoctorSchedule(**validated_data)
        
        db.session.add(schedule)
        db.session.commit()
        
        # 记录操作日志
        log_operation('create', 'schedule', resource_id=schedule.id, 
                     resource_name=f"{doctor.name}-{schedule.date}-{schedule.shift}",
                     status='success',
                     details={
                         'doctor_id': doctor.id,
                         'doctor_name': doctor.name,
                         'date': str(schedule.date),
                         'shift': schedule.shift
                     })
        
        return success_response(schedule.to_dict(), '排班创建成功', 'SCHEDULE_CREATED')
    
    except Exception as e:
        db.session.rollback()
        log_operation('create', 'schedule', status='failed', error_message=str(e))
        return error_response(f'创建排班失败：{str(e)}', 'CREATE_SCHEDULE_ERROR', 500)


@doctor_bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """更新排班（API）"""
    try:
        schedule = DoctorSchedule.query.get(schedule_id)
        if not schedule:
            return error_response('排班不存在', 'SCHEDULE_NOT_FOUND', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        # 使用Schema进行部分数据验证
        schema = DoctorScheduleSchema(partial=True)
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            log_operation('update', 'schedule', resource_id=schedule_id, 
                         status='failed', error_message=f'数据验证失败: {err.messages}')
            return error_response(f'数据验证失败：{err.messages}', 'VALIDATION_ERROR')
        
        # 获取用于冲突检测的数据
        doctor_id = validated_data.get('doctor_id', schedule.doctor_id)
        schedule_date = validated_data.get('date', schedule.date)
        shift = validated_data.get('shift', schedule.shift)
        start_time = validated_data.get('start_time', schedule.start_time)
        end_time = validated_data.get('end_time', schedule.end_time)
        
        # 排班冲突检测（排除当前排班记录）
        has_conflict, conflict_msg = check_schedule_conflict_enhanced(
            doctor_id=doctor_id,
            schedule_date=schedule_date,
            shift=shift,
            start_time=start_time,
            end_time=end_time,
            exclude_schedule_id=schedule_id
        )
        
        if has_conflict:
            log_operation('update', 'schedule', resource_id=schedule_id, 
                         status='failed', error_message=conflict_msg)
            return error_response(conflict_msg, 'SCHEDULE_CONFLICT')
        
        # 记录旧值
        old_values = {
            'doctor_id': schedule.doctor_id,
            'date': str(schedule.date),
            'shift': schedule.shift
        }
        
        # 更新字段
        for key, value in validated_data.items():
            setattr(schedule, key, value)
        
        db.session.commit()
        
        # 记录操作日志
        if schedule.doctor:
            resource_name = f"{schedule.doctor.name}-{schedule.date}-{schedule.shift}"
        else:
            resource_name = f"{schedule.date}-{schedule.shift}"
        log_operation('update', 'schedule', resource_id=schedule.id, 
                     resource_name=resource_name,
                     status='success',
                     details={'old_values': old_values, 'updated_fields': list(validated_data.keys())})
        
        return success_response(schedule.to_dict(), '排班更新成功', 'SCHEDULE_UPDATED')
    
    except Exception as e:
        db.session.rollback()
        log_operation('update', 'schedule', resource_id=schedule_id, 
                     status='failed', error_message=str(e))
        return error_response(f'更新排班失败：{str(e)}', 'UPDATE_SCHEDULE_ERROR', 500)


@doctor_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """删除排班（API）"""
    try:
        schedule = DoctorSchedule.query.get(schedule_id)
        if not schedule:
            return error_response('排班不存在', 'SCHEDULE_NOT_FOUND', 404)
        
        # 保存信息用于日志
        if schedule.doctor:
            schedule_name = f"{schedule.doctor.name}-{schedule.date}-{schedule.shift}"
            doctor_name = schedule.doctor.name
        else:
            schedule_name = f"{schedule.date}-{schedule.shift}"
            doctor_name = None
        schedule_info = {
            'doctor_id': schedule.doctor_id,
            'doctor_name': doctor_name,
            'date': str(schedule.date),
            'shift': schedule.shift
        }
        
        db.session.delete(schedule)
        db.session.commit()
        
        # 记录操作日志
        log_operation('delete', 'schedule', resource_id=schedule_id, 
                     resource_name=schedule_name, status='success',
                     details=schedule_info)
        
        return success_response(None, '排班删除成功', 'SCHEDULE_DELETED')
    
    except Exception as e:
        db.session.rollback()
        log_operation('delete', 'schedule', resource_id=schedule_id, 
                     status='failed', error_message=str(e))
        return error_response(f'删除排班失败：{str(e)}', 'DELETE_SCHEDULE_ERROR', 500)


@doctor_bp.route('/doctors/<int:doctor_id>/schedules', methods=['GET'])
def get_doctor_schedules(doctor_id):
    """获取指定医生的排班（API）"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        query = DoctorSchedule.query.filter_by(doctor_id=doctor_id)
        
        # 日期范围过滤
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(DoctorSchedule.date >= start_date)
            except ValueError:
                return error_response('开始日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(DoctorSchedule.date <= end_date)
            except ValueError:
                return error_response('结束日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
        
        schedules = query.order_by(DoctorSchedule.date.asc()).all()
        schedules_data = [schedule.to_dict() for schedule in schedules]
        
        return success_response({
            'doctor': doctor.to_dict(),
            'schedules': schedules_data,
            'total': len(schedules_data)
        })
    
    except Exception as e:
        return error_response(f'获取医生排班失败：{str(e)}', 'GET_DOCTOR_SCHEDULES_ERROR', 500)


# ============= 传统视图 - 排班管理 =============

@doctor_bp.route('/schedules-list')
def schedule_list():
    """排班列表页面"""
    page = request.args.get('page', 1, type=int)
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date', '')
    
    query = DoctorSchedule.query
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    if date_str:
        try:
            schedule_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(date=schedule_date)
        except:
            pass
    
    pagination = query.order_by(DoctorSchedule.date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    schedules = pagination.items
    
    doctors = Doctor.query.filter_by(status='active').all()
    
    return render_template('doctor/schedule_list.html', 
                         schedules=schedules, 
                         pagination=pagination,
                         doctors=doctors,
                         doctor_id=doctor_id,
                         date=date_str)


@doctor_bp.route('/schedule/add', methods=['GET', 'POST'])
def schedule_add():
    """添加排班"""
    if request.method == 'POST':
        try:
            schedule_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            
            schedule = DoctorSchedule(
                doctor_id=request.form.get('doctor_id', type=int),
                date=schedule_date,
                shift=request.form.get('shift'),
                start_time=request.form.get('start_time'),
                end_time=request.form.get('end_time'),
                max_patients=request.form.get('max_patients', type=int),
                notes=request.form.get('notes')
            )
            db.session.add(schedule)
            db.session.commit()
            flash('排班添加成功！', 'success')
            return redirect(url_for('doctor.schedule_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    doctors = Doctor.query.filter_by(status='active').all()
    return render_template('doctor/schedule_form.html', schedule=None, doctors=doctors)


@doctor_bp.route('/schedule/edit/<int:id>', methods=['GET', 'POST'])
def schedule_edit(id):
    """编辑排班"""
    schedule = DoctorSchedule.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            schedule_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            
            schedule.doctor_id = request.form.get('doctor_id', type=int)
            schedule.date = schedule_date
            schedule.shift = request.form.get('shift')
            schedule.start_time = request.form.get('start_time')
            schedule.end_time = request.form.get('end_time')
            schedule.max_patients = request.form.get('max_patients', type=int)
            schedule.status = request.form.get('status')
            schedule.notes = request.form.get('notes')
            
            db.session.commit()
            flash('排班更新成功！', 'success')
            return redirect(url_for('doctor.schedule_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    doctors = Doctor.query.filter_by(status='active').all()
    return render_template('doctor/schedule_form.html', schedule=schedule, doctors=doctors)


@doctor_bp.route('/schedule/delete/<int:id>', methods=['POST'])
def schedule_delete(id):
    """删除排班"""
    try:
        schedule = DoctorSchedule.query.get_or_404(id)
        db.session.delete(schedule)
        db.session.commit()
        flash('排班已删除！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('doctor.schedule_list'))


# ============= RESTful API - 医生绩效管理 =============

@doctor_bp.route('/performances', methods=['GET'])
def get_performances():
    """获取绩效列表（API）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        # 构建查询
        query = DoctorPerformance.query
        
        # 医生过滤
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        
        # 年份过滤
        if year:
            query = query.filter_by(year=year)
        
        # 月份过滤
        if month:
            query = query.filter_by(month=month)
        
        # 分页
        pagination = query.order_by(
            DoctorPerformance.year.desc(),
            DoctorPerformance.month.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        # 序列化数据
        performances_data = [perf.to_dict() for perf in pagination.items]
        
        return success_response({
            'list': performances_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    
    except Exception as e:
        return error_response(f'获取绩效列表失败：{str(e)}', 'GET_PERFORMANCES_ERROR', 500)


@doctor_bp.route('/performances/<int:performance_id>', methods=['GET'])
def get_performance(performance_id):
    """获取绩效详情（API）"""
    try:
        performance = DoctorPerformance.query.get(performance_id)
        if not performance:
            return error_response('绩效记录不存在', 'PERFORMANCE_NOT_FOUND', 404)
        
        return success_response(performance.to_dict())
    
    except Exception as e:
        return error_response(f'获取绩效详情失败：{str(e)}', 'GET_PERFORMANCE_ERROR', 500)


@doctor_bp.route('/performances', methods=['POST'])
def create_performance():
    """创建绩效评估（API）"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        # 使用Schema进行数据验证
        schema = DoctorPerformanceSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            log_operation('create', 'performance', status='failed', 
                         error_message=f'数据验证失败: {err.messages}')
            return error_response(f'数据验证失败：{err.messages}', 'VALIDATION_ERROR')
        
        # 验证医生是否存在
        doctor = Doctor.query.get(validated_data['doctor_id'])
        if not doctor:
            log_operation('create', 'performance', status='failed', 
                         error_message='医生不存在')
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        # 检查是否已存在该医生在该年月的绩效记录
        existing = DoctorPerformance.query.filter_by(
            doctor_id=validated_data['doctor_id'],
            year=validated_data['year'],
            month=validated_data['month']
        ).first()
        
        if existing:
            log_operation('create', 'performance', status='failed', 
                         error_message='该医生在此时间已有绩效记录')
            return error_response('该医生在此时间已有绩效记录', 'PERFORMANCE_EXISTS')
        
        # 获取评分数据
        patient_count = validated_data.get('patient_count', 0)
        satisfaction = validated_data.get('satisfaction_score', 0.0)
        punctuality = validated_data.get('punctuality_score', 0.0)
        quality = validated_data.get('quality_score', 0.0)
        
        # 计算综合评分（满意度40% + 准时率20% + 质量评分40%）
        total_score = satisfaction * 0.4 + punctuality * 0.2 + quality * 0.4
        
        # 计算绩效奖金（可根据实际需求调整计算公式）
        bonus = patient_count * 10 + total_score * 100
        
        # 创建绩效记录
        performance = DoctorPerformance(
            **validated_data,
            total_score=total_score,
            bonus=bonus
        )
        
        db.session.add(performance)
        db.session.commit()
        
        # 记录操作日志
        log_operation('create', 'performance', resource_id=performance.id, 
                     resource_name=f"{doctor.name}-{performance.year}年{performance.month}月",
                     status='success',
                     details={
                         'doctor_id': doctor.id,
                         'doctor_name': doctor.name,
                         'year': performance.year,
                         'month': performance.month,
                         'total_score': total_score
                     })
        
        return success_response(performance.to_dict(), '绩效评估创建成功', 'PERFORMANCE_CREATED')
    
    except Exception as e:
        db.session.rollback()
        log_operation('create', 'performance', status='failed', error_message=str(e))
        return error_response(f'创建绩效评估失败：{str(e)}', 'CREATE_PERFORMANCE_ERROR', 500)


@doctor_bp.route('/performances/<int:performance_id>', methods=['PUT'])
def update_performance(performance_id):
    """更新绩效评估（API）"""
    try:
        performance = DoctorPerformance.query.get(performance_id)
        if not performance:
            return error_response('绩效记录不存在', 'PERFORMANCE_NOT_FOUND', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        # 更新字段
        if 'patient_count' in data:
            performance.patient_count = data['patient_count']
        if 'satisfaction_score' in data:
            performance.satisfaction_score = data['satisfaction_score']
        if 'punctuality_score' in data:
            performance.punctuality_score = data['punctuality_score']
        if 'quality_score' in data:
            performance.quality_score = data['quality_score']
        if 'notes' in data:
            performance.notes = data['notes']
        
        # 重新计算综合评分和奖金
        satisfaction = performance.satisfaction_score or 0
        punctuality = performance.punctuality_score or 0
        quality = performance.quality_score or 0
        patient_count = performance.patient_count or 0
        
        performance.total_score = satisfaction * 0.4 + punctuality * 0.2 + quality * 0.4
        performance.bonus = patient_count * 10 + performance.total_score * 100
        
        db.session.commit()
        
        return success_response(performance.to_dict(), '绩效评估更新成功', 'PERFORMANCE_UPDATED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新绩效评估失败：{str(e)}', 'UPDATE_PERFORMANCE_ERROR', 500)


@doctor_bp.route('/performances/<int:performance_id>', methods=['DELETE'])
def delete_performance(performance_id):
    """删除绩效评估（API）"""
    try:
        performance = DoctorPerformance.query.get(performance_id)
        if not performance:
            return error_response('绩效记录不存在', 'PERFORMANCE_NOT_FOUND', 404)
        
        db.session.delete(performance)
        db.session.commit()
        
        return success_response(None, '绩效评估删除成功', 'PERFORMANCE_DELETED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除绩效评估失败：{str(e)}', 'DELETE_PERFORMANCE_ERROR', 500)


@doctor_bp.route('/doctors/<int:doctor_id>/performances', methods=['GET'])
def get_doctor_performances(doctor_id):
    """获取指定医生的绩效记录（API）"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        query = DoctorPerformance.query.filter_by(doctor_id=doctor_id)
        
        if year:
            query = query.filter_by(year=year)
        if month:
            query = query.filter_by(month=month)
        
        performances = query.order_by(
            DoctorPerformance.year.desc(),
            DoctorPerformance.month.desc()
        ).all()
        
        performances_data = [perf.to_dict() for perf in performances]
        
        # 计算统计数据
        total_patients = sum(p.patient_count or 0 for p in performances)
        avg_satisfaction = sum(p.satisfaction_score or 0 for p in performances) / len(performances) if performances else 0
        avg_total_score = sum(p.total_score or 0 for p in performances) / len(performances) if performances else 0
        total_bonus = sum(p.bonus or 0 for p in performances)
        
        return success_response({
            'doctor': doctor.to_dict(),
            'performances': performances_data,
            'total': len(performances_data),
            'statistics': {
                'total_patients': total_patients,
                'average_satisfaction': round(avg_satisfaction, 2),
                'average_total_score': round(avg_total_score, 2),
                'total_bonus': round(total_bonus, 2)
            }
        })
    
    except Exception as e:
        return error_response(f'获取医生绩效失败：{str(e)}', 'GET_DOCTOR_PERFORMANCES_ERROR', 500)


@doctor_bp.route('/performances/statistics', methods=['GET'])
def get_performances_statistics():
    """获取绩效统计数据（API）"""
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        query = DoctorPerformance.query
        
        if year:
            query = query.filter_by(year=year)
        if month:
            query = query.filter_by(month=month)
        
        performances = query.all()
        
        if not performances:
            return success_response({
                'total_records': 0,
                'total_patients': 0,
                'average_satisfaction': 0,
                'average_punctuality': 0,
                'average_quality': 0,
                'average_total_score': 0,
                'total_bonus': 0
            })
        
        # 计算统计数据
        total_patients = sum(p.patient_count or 0 for p in performances)
        avg_satisfaction = sum(p.satisfaction_score or 0 for p in performances) / len(performances)
        avg_punctuality = sum(p.punctuality_score or 0 for p in performances) / len(performances)
        avg_quality = sum(p.quality_score or 0 for p in performances) / len(performances)
        avg_total_score = sum(p.total_score or 0 for p in performances) / len(performances)
        total_bonus = sum(p.bonus or 0 for p in performances)
        
        return success_response({
            'total_records': len(performances),
            'total_patients': total_patients,
            'average_satisfaction': round(avg_satisfaction, 2),
            'average_punctuality': round(avg_punctuality, 2),
            'average_quality': round(avg_quality, 2),
            'average_total_score': round(avg_total_score, 2),
            'total_bonus': round(total_bonus, 2)
        })
    
    except Exception as e:
        return error_response(f'获取绩效统计失败：{str(e)}', 'GET_PERFORMANCE_STATISTICS_ERROR', 500)


# ============= 传统视图 - 绩效管理 =============

@doctor_bp.route('/performances-list')
def performance_list():
    """绩效列表页面"""
    page = request.args.get('page', 1, type=int)
    doctor_id = request.args.get('doctor_id', type=int)
    year = request.args.get('year', type=int)
    
    query = DoctorPerformance.query
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    if year:
        query = query.filter_by(year=year)
    
    pagination = query.order_by(
        DoctorPerformance.year.desc(), 
        DoctorPerformance.month.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    performances = pagination.items
    
    doctors = Doctor.query.filter_by(status='active').all()
    
    return render_template('doctor/performance_list.html', 
                         performances=performances, 
                         pagination=pagination,
                         doctors=doctors,
                         doctor_id=doctor_id,
                         year=year)


@doctor_bp.route('/performance/add', methods=['GET', 'POST'])
def performance_add():
    """添加绩效评估"""
    if request.method == 'POST':
        try:
            patient_count = request.form.get('patient_count', type=int) or 0
            satisfaction = request.form.get('satisfaction_score', type=float) or 0
            punctuality = request.form.get('punctuality_score', type=float) or 0
            quality = request.form.get('quality_score', type=float) or 0
            
            # 计算综合评分
            total_score = (satisfaction * 0.4 + punctuality * 0.2 + quality * 0.4)
            
            # 计算绩效奖金（简单示例）
            bonus = patient_count * 10 + total_score * 100
            
            performance = DoctorPerformance(
                doctor_id=request.form.get('doctor_id', type=int),
                year=request.form.get('year', type=int),
                month=request.form.get('month', type=int),
                patient_count=patient_count,
                satisfaction_score=satisfaction,
                punctuality_score=punctuality,
                quality_score=quality,
                total_score=total_score,
                bonus=bonus,
                notes=request.form.get('notes')
            )
            db.session.add(performance)
            db.session.commit()
            flash('绩效评估添加成功！', 'success')
            return redirect(url_for('doctor.performance_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    doctors = Doctor.query.filter_by(status='active').all()
    return render_template('doctor/performance_form.html', performance=None, doctors=doctors)


@doctor_bp.route('/performance/detail/<int:id>')
def performance_detail(id):
    """绩效详情"""
    performance = DoctorPerformance.query.get_or_404(id)
    return render_template('doctor/performance_detail.html', performance=performance)


# ============= 辅助数据接口 =============

@doctor_bp.route('/departments', methods=['GET'])
def get_departments():
    """获取科室列表（API）"""
    try:
        # 标准科室列表
        base_departments = [
            '内科', '外科', '儿科', '妇产科', '骨科', '神经科',
            '皮肤科', '眼科', '耳鼻喉科', '口腔科', '急诊科', '中医科'
        ]

        # 从医生表中获取所有已存在的科室（去重）
        departments_query = db.session.query(Doctor.department).filter(
            Doctor.department.isnot(None),
            Doctor.department != ''
        ).distinct().all()

        existing_departments = {dept[0] for dept in departments_query}

        # 合并标准科室和已存在科室，去重
        all_departments = sorted(set(base_departments) | existing_departments)

        departments = [{'id': name, 'name': name} for name in all_departments]

        return success_response(departments)

    except Exception as e:
        return error_response(f'获取科室列表失败：{str(e)}', 'GET_DEPARTMENTS_ERROR', 500)


@doctor_bp.route('/titles', methods=['GET'])
def get_titles():
    """获取职称列表（API）"""
    try:
        # 标准职称列表
        titles = [
            '主任医师',
            '副主任医师',
            '主治医师',
            '住院医师',
            '医师'
        ]

        return success_response(titles)

    except Exception as e:
        return error_response(f'获取职称列表失败：{str(e)}', 'GET_TITLES_ERROR', 500)


