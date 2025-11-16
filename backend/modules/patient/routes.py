"""
病人管理子系统 - 路由
Patient Management - Routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from . import patient_bp
from models import Patient, MedicalRecord, Appointment
from extensions import db
from datetime import datetime


# ============= 病人基本信息管理 =============

@patient_bp.route('/')
def index():
    """病人管理首页"""
    return render_template('patient_index.html')


@patient_bp.route('/patients')
def patient_list():
    """病人列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Patient.query
    if search:
        query = query.filter(
            (Patient.name.like(f'%{search}%')) | 
            (Patient.patient_no.like(f'%{search}%')) |
            (Patient.phone.like(f'%{search}%'))
        )
    
    pagination = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    patients = pagination.items
    
    return render_template('patient_list.html', 
                         patients=patients, 
                         pagination=pagination,
                         search=search)


@patient_bp.route('/patient/add', methods=['GET', 'POST'])
def patient_add():
    """添加病人"""
    if request.method == 'POST':
        try:
            patient = Patient(
                patient_no=request.form.get('patient_no'),
                name=request.form.get('name'),
                gender=request.form.get('gender'),
                age=request.form.get('age', type=int),
                phone=request.form.get('phone'),
                id_card=request.form.get('id_card'),
                address=request.form.get('address'),
                emergency_contact=request.form.get('emergency_contact'),
                emergency_phone=request.form.get('emergency_phone')
            )
            db.session.add(patient)
            db.session.commit()
            flash('病人信息添加成功！', 'success')
            return redirect(url_for('patient.patient_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    return render_template('patient_form.html', patient=None)


@patient_bp.route('/patient/edit/<int:id>', methods=['GET', 'POST'])
def patient_edit(id):
    """编辑病人信息"""
    patient = Patient.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            patient.name = request.form.get('name')
            patient.gender = request.form.get('gender')
            patient.age = request.form.get('age', type=int)
            patient.phone = request.form.get('phone')
            patient.id_card = request.form.get('id_card')
            patient.address = request.form.get('address')
            patient.emergency_contact = request.form.get('emergency_contact')
            patient.emergency_phone = request.form.get('emergency_phone')
            
            db.session.commit()
            flash('病人信息更新成功！', 'success')
            return redirect(url_for('patient.patient_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('patient_form.html', patient=patient)


@patient_bp.route('/patient/delete/<int:id>', methods=['POST'])
def patient_delete(id):
    """删除病人"""
    try:
        patient = Patient.query.get_or_404(id)
        db.session.delete(patient)
        db.session.commit()
        flash('病人信息已删除！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('patient.patient_list'))


@patient_bp.route('/patient/detail/<int:id>')
def patient_detail(id):
    """病人详情"""
    patient = Patient.query.get_or_404(id)
    return render_template('patient_detail.html', patient=patient)


# ============= 病历记录管理 =============

@patient_bp.route('/medical-records')
def medical_record_list():
    """病历列表"""
    page = request.args.get('page', 1, type=int)
    patient_id = request.args.get('patient_id', type=int)
    
    query = MedicalRecord.query
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    pagination = query.order_by(MedicalRecord.visit_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    records = pagination.items
    
    return render_template('medical_record_list.html', 
                         records=records, 
                         pagination=pagination,
                         patient_id=patient_id)


@patient_bp.route('/medical-record/add', methods=['GET', 'POST'])
def medical_record_add():
    """添加病历"""
    if request.method == 'POST':
        try:
            record = MedicalRecord(
                patient_id=request.form.get('patient_id', type=int),
                doctor_id=request.form.get('doctor_id', type=int),
                diagnosis=request.form.get('diagnosis'),
                symptoms=request.form.get('symptoms'),
                treatment=request.form.get('treatment'),
                prescription=request.form.get('prescription'),
                notes=request.form.get('notes')
            )
            db.session.add(record)
            db.session.commit()
            flash('病历添加成功！', 'success')
            return redirect(url_for('patient.medical_record_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    patients = Patient.query.all()
    return render_template('medical_record_form.html', record=None, patients=patients)


@patient_bp.route('/medical-record/detail/<int:id>')
def medical_record_detail(id):
    """病历详情"""
    record = MedicalRecord.query.get_or_404(id)
    return render_template('medical_record_detail.html', record=record)


# ============= 挂号预约管理 =============

@patient_bp.route('/appointments')
def appointment_list():
    """预约列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Appointment.appointment_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    appointments = pagination.items
    
    return render_template('appointment_list.html', 
                         appointments=appointments, 
                         pagination=pagination,
                         status=status)


@patient_bp.route('/appointment/add', methods=['GET', 'POST'])
def appointment_add():
    """添加预约"""
    if request.method == 'POST':
        try:
            appointment = Appointment(
                patient_id=request.form.get('patient_id', type=int),
                doctor_id=request.form.get('doctor_id', type=int),
                appointment_date=datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d'),
                appointment_time=request.form.get('appointment_time'),
                department=request.form.get('department'),
                notes=request.form.get('notes')
            )
            db.session.add(appointment)
            db.session.commit()
            flash('预约添加成功！', 'success')
            return redirect(url_for('patient.appointment_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    patients = Patient.query.all()
    return render_template('appointment_form.html', appointment=None, patients=patients)


@patient_bp.route('/appointment/update-status/<int:id>', methods=['POST'])
def appointment_update_status(id):
    """更新预约状态"""
    try:
        appointment = Appointment.query.get_or_404(id)
        appointment.status = request.form.get('status')
        db.session.commit()
        flash('预约状态更新成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失败：{str(e)}', 'error')
    
    return redirect(url_for('patient.appointment_list'))

