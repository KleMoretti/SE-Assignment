"""
医生管理子系统 - 路由
Doctor Management - Routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from . import doctor_bp
from models import Doctor, DoctorSchedule, DoctorPerformance, Appointment, MedicalRecord, Patient, Medicine, MedicationRequest
from extensions import db
from datetime import datetime, date
from sqlalchemy import func, extract
from modules.doctor.models_extended import DoctorLeave
from modules.doctor.utils import calculate_leave_days


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
        
        # 分页
        pagination = query.order_by(Doctor.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 序列化数据
        doctors_data = [doctor.to_dict() for doctor in pagination.items]
        
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
        
        # 附加统计信息
        doctor_data['statistics'] = {
            'total_appointments': Appointment.query.filter_by(doctor_id=doctor_id).count(),
            'completed_appointments': Appointment.query.filter_by(
                doctor_id=doctor_id, status='completed'
            ).count(),
            'total_medical_records': MedicalRecord.query.filter_by(doctor_id=doctor_id).count(),
            'total_schedules': DoctorSchedule.query.filter_by(doctor_id=doctor_id).count()
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
        
        required_fields = ['doctor_no', 'name', 'gender']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段：{field}', 'MISSING_FIELD')
        
        # 检查医生编号是否已存在
        if Doctor.query.filter_by(doctor_no=data['doctor_no']).first():
            return error_response('医生编号已存在', 'DOCTOR_NO_EXISTS')
        
        # 处理日期
        hire_date = None
        if data.get('hire_date'):
            try:
                hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('入职日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
        
        # 创建医生
        doctor = Doctor(
            doctor_no=data['doctor_no'],
            name=data['name'],
            gender=data['gender'],
            age=data.get('age'),
            phone=data.get('phone'),
            email=data.get('email'),
            department=data.get('department'),
            title=data.get('title'),
            specialty=data.get('specialty'),
            education=data.get('education'),
            hire_date=hire_date,
            status=data.get('status', 'active')
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        return success_response(doctor.to_dict(), '医生创建成功', 'DOCTOR_CREATED')
    
    except Exception as e:
        db.session.rollback()
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
        
        # 更新字段
        if 'name' in data:
            doctor.name = data['name']
        if 'gender' in data:
            doctor.gender = data['gender']
        if 'age' in data:
            doctor.age = data['age']
        if 'phone' in data:
            doctor.phone = data['phone']
        if 'email' in data:
            doctor.email = data['email']
        if 'department' in data:
            doctor.department = data['department']
        if 'title' in data:
            doctor.title = data['title']
        if 'specialty' in data:
            doctor.specialty = data['specialty']
        if 'education' in data:
            doctor.education = data['education']
        if 'status' in data:
            doctor.status = data['status']
        
        # 处理日期
        if 'hire_date' in data:
            if data['hire_date']:
                try:
                    doctor.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
                except ValueError:
                    return error_response('入职日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
            else:
                doctor.hire_date = None
        
        db.session.commit()
        
        return success_response(doctor.to_dict(), '医生信息更新成功', 'DOCTOR_UPDATED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新医生信息失败：{str(e)}', 'UPDATE_DOCTOR_ERROR', 500)


@doctor_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    """删除医生（API）"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        # 检查是否有关联的预约或病历
        appointment_count = Appointment.query.filter_by(doctor_id=doctor_id).count()
        if appointment_count > 0:
            return error_response(
                f'该医生有 {appointment_count} 条关联预约记录，无法删除',
                'DOCTOR_HAS_APPOINTMENTS'
            )
        
        medical_record_count = MedicalRecord.query.filter_by(doctor_id=doctor_id).count()
        if medical_record_count > 0:
            return error_response(
                f'该医生有 {medical_record_count} 条关联病历记录，无法删除',
                'DOCTOR_HAS_MEDICAL_RECORDS'
            )
        
        db.session.delete(doctor)
        db.session.commit()
        
        return success_response(None, '医生删除成功', 'DOCTOR_DELETED')
    
    except Exception as e:
        db.session.rollback()
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
        
        required_fields = ['doctor_id', 'date', 'shift']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段：{field}', 'MISSING_FIELD')
        
        # 验证医生是否存在
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        # 处理日期
        try:
            schedule_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response('日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
        
        # 检查是否已存在相同的排班
        existing = DoctorSchedule.query.filter_by(
            doctor_id=data['doctor_id'],
            date=schedule_date,
            shift=data['shift']
        ).first()
        
        if existing:
            return error_response('该医生在此时间段已有排班', 'SCHEDULE_EXISTS')
        
        # 创建排班
        schedule = DoctorSchedule(
            doctor_id=data['doctor_id'],
            date=schedule_date,
            shift=data['shift'],
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            max_patients=data.get('max_patients', 20),
            status=data.get('status', 'available'),
            notes=data.get('notes')
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return success_response(schedule.to_dict(), '排班创建成功', 'SCHEDULE_CREATED')
    
    except Exception as e:
        db.session.rollback()
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
        
        # 更新字段
        if 'doctor_id' in data:
            doctor = Doctor.query.get(data['doctor_id'])
            if not doctor:
                return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
            schedule.doctor_id = data['doctor_id']
        
        if 'date' in data:
            try:
                schedule.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
        
        if 'shift' in data:
            schedule.shift = data['shift']
        if 'start_time' in data:
            schedule.start_time = data['start_time']
        if 'end_time' in data:
            schedule.end_time = data['end_time']
        if 'max_patients' in data:
            schedule.max_patients = data['max_patients']
        if 'status' in data:
            schedule.status = data['status']
        if 'notes' in data:
            schedule.notes = data['notes']
        
        db.session.commit()
        
        return success_response(schedule.to_dict(), '排班更新成功', 'SCHEDULE_UPDATED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新排班失败：{str(e)}', 'UPDATE_SCHEDULE_ERROR', 500)


@doctor_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """删除排班（API）"""
    try:
        schedule = DoctorSchedule.query.get(schedule_id)
        if not schedule:
            return error_response('排班不存在', 'SCHEDULE_NOT_FOUND', 404)
        
        db.session.delete(schedule)
        db.session.commit()
        
        return success_response(None, '排班删除成功', 'SCHEDULE_DELETED')
    
    except Exception as e:
        db.session.rollback()
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


@doctor_bp.route('/schedules/overview', methods=['GET'])
def get_schedules_overview():
    """按科室和日期范围获取排班总览（API）"""
    try:
        department = request.args.get('department', '', type=str)
        start_date_str = request.args.get('start_date', '', type=str)
        end_date_str = request.args.get('end_date', '', type=str)
        shift = request.args.get('shift', '', type=str)
        status = request.args.get('status', '', type=str)

        query = db.session.query(DoctorSchedule, Doctor).join(Doctor, DoctorSchedule.doctor_id == Doctor.id)

        if department:
            query = query.filter(Doctor.department == department)

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('开始日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
            query = query.filter(DoctorSchedule.date >= start_date)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('结束日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
            query = query.filter(DoctorSchedule.date <= end_date)

        if shift:
            query = query.filter(DoctorSchedule.shift == shift)

        if status:
            query = query.filter(DoctorSchedule.status == status)

        results = query.order_by(DoctorSchedule.date.asc(), Doctor.id.asc()).all()
        items = []
        for schedule, doctor in results:
            data = schedule.to_dict()
            data['doctor_name'] = doctor.name
            data['doctor_department'] = doctor.department
            data['doctor_title'] = doctor.title
            items.append(data)

        return success_response({
            'list': items,
            'items': items,
            'total': len(items)
        })
    
    except Exception as e:
        return error_response(f'获取排班总览失败：{str(e)}', 'GET_SCHEDULES_OVERVIEW_ERROR', 500)


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
        
        required_fields = ['doctor_id', 'year', 'month']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段：{field}', 'MISSING_FIELD')
        
        # 验证医生是否存在
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        # 验证年月
        year = data['year']
        month = data['month']
        if not (1 <= month <= 12):
            return error_response('月份必须在1-12之间', 'INVALID_MONTH')
        
        # 检查是否已存在该医生在该年月的绩效记录
        existing = DoctorPerformance.query.filter_by(
            doctor_id=data['doctor_id'],
            year=year,
            month=month
        ).first()
        
        if existing:
            return error_response('该医生在此时间已有绩效记录', 'PERFORMANCE_EXISTS')
        
        # 获取评分数据
        patient_count = data.get('patient_count', 0)
        satisfaction = data.get('satisfaction_score', 0.0)
        punctuality = data.get('punctuality_score', 0.0)
        quality = data.get('quality_score', 0.0)
        
        # 计算综合评分（满意度40% + 准时率20% + 质量评分40%）
        total_score = satisfaction * 0.4 + punctuality * 0.2 + quality * 0.4
        
        # 计算绩效奖金（可根据实际需求调整计算公式）
        bonus = patient_count * 10 + total_score * 100
        
        # 创建绩效记录
        performance = DoctorPerformance(
            doctor_id=data['doctor_id'],
            year=year,
            month=month,
            patient_count=patient_count,
            satisfaction_score=satisfaction,
            punctuality_score=punctuality,
            quality_score=quality,
            total_score=total_score,
            bonus=bonus,
            notes=data.get('notes')
        )
        
        db.session.add(performance)
        db.session.commit()
        
        return success_response(performance.to_dict(), '绩效评估创建成功', 'PERFORMANCE_CREATED')
    
    except Exception as e:
        db.session.rollback()
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
        
        query = DoctorPerformance.query.filter_by(doctor_id=doctor_id)
        
        if year:
            query = query.filter_by(year=year)
        
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


@doctor_bp.route('/leaves', methods=['GET'])
def get_leaves():
    """获取请假列表（API）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        status = request.args.get('status', '', type=str)
        leave_type = request.args.get('leave_type', '', type=str)
        start_date_str = request.args.get('start_date', '', type=str)
        end_date_str = request.args.get('end_date', '', type=str)

        query = DoctorLeave.query

        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)

        if status:
            query = query.filter_by(status=status)

        if leave_type:
            query = query.filter_by(leave_type=leave_type)

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('开始日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
            query = query.filter(DoctorLeave.start_date >= start_date)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('结束日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
            query = query.filter(DoctorLeave.end_date <= end_date)

        pagination = query.order_by(DoctorLeave.start_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        items = [leave.to_dict() for leave in pagination.items]

        return success_response({
            'list': items,
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    
    except Exception as e:
        return error_response(f'获取请假列表失败：{str(e)}', 'GET_LEAVES_ERROR', 500)


@doctor_bp.route('/leaves/<int:leave_id>', methods=['GET'])
def get_leave(leave_id):
    """获取请假详情（API）"""
    try:
        leave = DoctorLeave.query.get(leave_id)
        if not leave:
            return error_response('请假记录不存在', 'LEAVE_NOT_FOUND', 404)
        
        return success_response(leave.to_dict())
    
    except Exception as e:
        return error_response(f'获取请假详情失败：{str(e)}', 'GET_LEAVE_ERROR', 500)


@doctor_bp.route('/leaves', methods=['POST'])
def create_leave():
    """创建请假申请（API）"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        required_fields = ['doctor_id', 'leave_type', 'start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段：{field}', 'MISSING_FIELD')
        
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response('日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
        
        if end_date < start_date:
            return error_response('结束日期不能早于开始日期', 'INVALID_DATE_RANGE')
        
        days = calculate_leave_days(start_date, end_date)
        
        leave = DoctorLeave(
            doctor_id=data['doctor_id'],
            leave_type=data['leave_type'],
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=data.get('reason'),
            status=data.get('status', 'pending'),
            substitute_doctor_id=data.get('substitute_doctor_id'),
            approval_notes=data.get('approval_notes')
        )
        
        db.session.add(leave)
        db.session.commit()
        
        return success_response(leave.to_dict(), '请假申请创建成功', 'LEAVE_CREATED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建请假申请失败：{str(e)}', 'CREATE_LEAVE_ERROR', 500)


@doctor_bp.route('/leaves/<int:leave_id>', methods=['PUT'])
def update_leave(leave_id):
    """更新请假申请（API）"""
    try:
        leave = DoctorLeave.query.get(leave_id)
        if not leave:
            return error_response('请假记录不存在', 'LEAVE_NOT_FOUND', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        if 'doctor_id' in data:
            doctor = Doctor.query.get(data['doctor_id'])
            if not doctor:
                return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
            leave.doctor_id = data['doctor_id']
        
        if 'leave_type' in data:
            leave.leave_type = data['leave_type']
        
        start_date = leave.start_date
        end_date = leave.end_date
        
        if 'start_date' in data:
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('开始日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
        
        if 'end_date' in data:
            try:
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('结束日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
        
        if start_date and end_date:
            if end_date < start_date:
                return error_response('结束日期不能早于开始日期', 'INVALID_DATE_RANGE')
            leave.start_date = start_date
            leave.end_date = end_date
            leave.days = calculate_leave_days(start_date, end_date)
        
        if 'reason' in data:
            leave.reason = data['reason']
        
        if 'status' in data:
            leave.status = data['status']
        
        if 'substitute_doctor_id' in data:
            leave.substitute_doctor_id = data['substitute_doctor_id']
        
        if 'approval_notes' in data:
            leave.approval_notes = data['approval_notes']
        
        db.session.commit()
        
        return success_response(leave.to_dict(), '请假申请更新成功', 'LEAVE_UPDATED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新请假申请失败：{str(e)}', 'UPDATE_LEAVE_ERROR', 500)


@doctor_bp.route('/leaves/<int:leave_id>', methods=['DELETE'])
def delete_leave(leave_id):
    """删除请假记录（API）"""
    try:
        leave = DoctorLeave.query.get(leave_id)
        if not leave:
            return error_response('请假记录不存在', 'LEAVE_NOT_FOUND', 404)
        
        db.session.delete(leave)
        db.session.commit()
        
        return success_response(None, '请假记录删除成功', 'LEAVE_DELETED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除请假记录失败：{str(e)}', 'DELETE_LEAVE_ERROR', 500)


@doctor_bp.route('/leaves/<int:leave_id>/approve', methods=['PUT'])
def approve_leave(leave_id):
    """审批通过请假申请（API）"""
    try:
        leave = DoctorLeave.query.get(leave_id)
        if not leave:
            return error_response('请假记录不存在', 'LEAVE_NOT_FOUND', 404)
        
        data = request.get_json() or {}
        approver_id = data.get('approver_id')
        approval_notes = data.get('approval_notes')
        
        leave.status = 'approved'
        leave.approver_id = approver_id
        leave.approval_notes = approval_notes
        leave.approval_date = datetime.utcnow()
        
        db.session.commit()
        
        return success_response(leave.to_dict(), '请假审批通过', 'LEAVE_APPROVED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'审批请假失败：{str(e)}', 'APPROVE_LEAVE_ERROR', 500)


@doctor_bp.route('/leaves/<int:leave_id>/reject', methods=['PUT'])
def reject_leave(leave_id):
    """审批拒绝请假申请（API）"""
    try:
        leave = DoctorLeave.query.get(leave_id)
        if not leave:
            return error_response('请假记录不存在', 'LEAVE_NOT_FOUND', 404)
        
        data = request.get_json() or {}
        approver_id = data.get('approver_id')
        approval_notes = data.get('approval_notes')
        
        leave.status = 'rejected'
        leave.approver_id = approver_id
        leave.approval_notes = approval_notes
        leave.approval_date = datetime.utcnow()
        
        db.session.commit()
        
        return success_response(leave.to_dict(), '请假审批已拒绝', 'LEAVE_REJECTED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'拒绝请假失败：{str(e)}', 'REJECT_LEAVE_ERROR', 500)


@doctor_bp.route('/doctors/<int:doctor_id>/leaves', methods=['GET'])
def get_doctor_leaves(doctor_id):
    """获取指定医生的请假记录（API）"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        status = request.args.get('status', '', type=str)
        start_date_str = request.args.get('start_date', '', type=str)
        end_date_str = request.args.get('end_date', '', type=str)
        
        query = DoctorLeave.query.filter_by(doctor_id=doctor_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('开始日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
            query = query.filter(DoctorLeave.start_date >= start_date)
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('结束日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
            query = query.filter(DoctorLeave.end_date <= end_date)
        
        leaves = query.order_by(DoctorLeave.start_date.desc()).all()
        items = [leave.to_dict() for leave in leaves]
        
        return success_response({
            'doctor': doctor.to_dict(),
            'leaves': items,
            'list': items,
            'items': items,
            'total': len(items)
        })
    
    except Exception as e:
        return error_response(f'获取医生请假记录失败：{str(e)}', 'GET_DOCTOR_LEAVES_ERROR', 500)


# ============= RESTful API - 医生用药申请管理 =============

@doctor_bp.route('/medication-requests', methods=['GET'])
def get_medication_requests():
    """获取用药申请列表（API）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        patient_id = request.args.get('patient_id', type=int)
        status = request.args.get('status', '', type=str)
        
        query = MedicationRequest.query
        
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(MedicationRequest.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = [req.to_dict() for req in pagination.items]
        
        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    
    except Exception as e:
        return error_response(f'获取用药申请列表失败：{str(e)}', 'GET_MEDICATION_REQUESTS_ERROR', 500)


@doctor_bp.route('/medication-requests', methods=['POST'])
def create_medication_request():
    """创建用药申请（API）"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        required_fields = ['patient_id', 'doctor_id', 'medicine_id', 'quantity']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段：{field}', 'MISSING_FIELD')
        
        try:
            quantity = int(data.get('quantity'))
        except (TypeError, ValueError):
            return error_response('数量必须为正整数', 'INVALID_QUANTITY')
        
        if quantity <= 0:
            return error_response('数量必须大于0', 'INVALID_QUANTITY')
        
        patient = Patient.query.get(data['patient_id'])
        if not patient:
            return error_response('病人不存在', 'PATIENT_NOT_FOUND', 404)
        
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        medicine = Medicine.query.get(data['medicine_id'])
        if not medicine:
            return error_response('药品不存在', 'MEDICINE_NOT_FOUND', 404)
        
        medication_request = MedicationRequest(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            medicine_id=data['medicine_id'],
            dose=data.get('dose'),
            usage=data.get('usage'),
            quantity=quantity,
            status='PENDING',
            reason=data.get('reason')
        )
        
        db.session.add(medication_request)
        db.session.commit()
        
        return success_response(medication_request.to_dict(), '用药申请创建成功', 'MEDICATION_REQUEST_CREATED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建用药申请失败：{str(e)}', 'CREATE_MEDICATION_REQUEST_ERROR', 500)


@doctor_bp.route('/doctors/<int:doctor_id>/medication-requests', methods=['GET'])
def get_doctor_medication_requests(doctor_id):
    """获取指定医生的用药申请（API）"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return error_response('医生不存在', 'DOCTOR_NOT_FOUND', 404)
        
        status = request.args.get('status', '', type=str)
        patient_id = request.args.get('patient_id', type=int)
        
        query = MedicationRequest.query.filter_by(doctor_id=doctor_id)
        
        if status:
            query = query.filter_by(status=status)
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        
        requests = query.order_by(MedicationRequest.created_at.desc()).all()
        items = [req.to_dict() for req in requests]
        
        return success_response({
            'doctor': doctor.to_dict(),
            'requests': items,
            'list': items,
            'items': items,
            'total': len(items)
        })
    
    except Exception as e:
        return error_response(f'获取医生用药申请失败：{str(e)}', 'GET_DOCTOR_MEDICATION_REQUESTS_ERROR', 500)


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
        # 从医生表中获取所有科室（去重）
        departments_query = db.session.query(Doctor.department).filter(
            Doctor.department.isnot(None),
            Doctor.department != ''
        ).distinct().all()
        
        default_departments = [
            {'id': '内科', 'name': '内科'},
            {'id': '外科', 'name': '外科'},
            {'id': '儿科', 'name': '儿科'},
            {'id': '妇产科', 'name': '妇产科'},
            {'id': '骨科', 'name': '骨科'},
            {'id': '神经科', 'name': '神经科'},
            {'id': '皮肤科', 'name': '皮肤科'},
            {'id': '眼科', 'name': '眼科'},
            {'id': '耳鼻喉科', 'name': '耳鼻喉科'},
            {'id': '口腔科', 'name': '口腔科'},
            {'id': '急诊科', 'name': '急诊科'},
            {'id': '中医科', 'name': '中医科'}
        ]

        existing_ids = {item['id'] for item in default_departments}
        for dept in departments_query:
            name = dept[0]
            if name and name not in existing_ids:
                default_departments.append({'id': name, 'name': name})
                existing_ids.add(name)

        departments = default_departments

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
