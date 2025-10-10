"""
医生管理子系统 - 路由
Doctor Management - Routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from . import doctor_bp
from models import Doctor, DoctorSchedule, DoctorPerformance
from app import db
from datetime import datetime, date


# ============= 医生信息管理 =============

@doctor_bp.route('/')
def index():
    """医生管理首页"""
    return render_template('doctor_index.html')


@doctor_bp.route('/doctors')
def doctor_list():
    """医生列表"""
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
    
    return render_template('doctor_list.html', 
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
    
    return render_template('doctor_form.html', doctor=None)


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
    
    return render_template('doctor_form.html', doctor=doctor)


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
    return render_template('doctor_detail.html', doctor=doctor)


# ============= 医生排班管理 =============

@doctor_bp.route('/schedules')
def schedule_list():
    """排班列表"""
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
    
    return render_template('schedule_list.html', 
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
    return render_template('schedule_form.html', schedule=None, doctors=doctors)


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
    return render_template('schedule_form.html', schedule=schedule, doctors=doctors)


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


# ============= 医生绩效评估 =============

@doctor_bp.route('/performances')
def performance_list():
    """绩效列表"""
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
    
    return render_template('performance_list.html', 
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
    return render_template('performance_form.html', performance=None, doctors=doctors)


@doctor_bp.route('/performance/detail/<int:id>')
def performance_detail(id):
    """绩效详情"""
    performance = DoctorPerformance.query.get_or_404(id)
    return render_template('performance_detail.html', performance=performance)

