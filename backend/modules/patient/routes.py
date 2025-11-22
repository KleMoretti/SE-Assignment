"""
病人管理子系统 - 路由
Patient Management - Routes
"""
from flask import render_template, request, redirect, url_for, flash
from . import patient_bp
from backend.extensions import db
from . import patient_services, record_services, appointment_services


# ============= 病人基本信息管理 =============

@patient_bp.route('/')
def index():
    """病人管理首页"""
    return render_template('patient/patient_index.html')


@patient_bp.route('/patients')
def patient_list():
    """病人列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    pagination = patient_services.get_patients_with_pagination(page=page, search=search)
    patients = pagination.items
    
    return render_template('patient/patient_list.html',
                         patients=patients,
                         pagination=pagination,
                         search=search)


@patient_bp.route('/patient/add', methods=['GET', 'POST'])
def patient_add():
    """添加病人"""
    if request.method == 'POST':
        try:
            patient_services.add_new_patient(request.form)
            flash('病人信息添加成功！', 'success')
            return redirect(url_for('patient.patient_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    return render_template('patient/patient_form.html', patient=None)


@patient_bp.route('/patient/edit/<int:id>', methods=['GET', 'POST'])
def patient_edit(id):
    """编辑病人信息"""
    patient = patient_services.get_patient_by_id(id)

    if request.method == 'POST':
        try:
            patient_services.update_patient_info(id, request.form)
            flash('病人信息更新成功！', 'success')
            return redirect(url_for('patient.patient_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('patient/patient_form.html', patient=patient)


@patient_bp.route('/patient/delete/<int:id>', methods=['POST'])
def patient_delete(id):
    """删除病人"""
    try:
        patient_services.delete_patient_by_id(id)
        flash('病人信息已删除！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('patient.patient_list'))


@patient_bp.route('/patient/detail/<int:id>')
def patient_detail(id):
    """病人详情"""
    patient = patient_services.get_patient_by_id(id)
    return render_template('patient/patient_detail.html', patient=patient)


# ============= 病历记录管理 =============

@patient_bp.route('/medical-records')
def medical_record_list():
    """病历列表"""
    page = request.args.get('page', 1, type=int)
    patient_id = request.args.get('patient_id', type=int)
    
    pagination = record_services.get_medical_records_with_pagination(page=page, patient_id=patient_id)
    records = pagination.items
    
    return render_template('patient/medical_record_list.html',
                         records=records,
                         pagination=pagination,
                         patient_id=patient_id)


@patient_bp.route('/medical-record/add', methods=['GET', 'POST'])
def medical_record_add():
    """添加病历"""
    if request.method == 'POST':
        try:
            record_services.add_new_medical_record(request.form)
            flash('病历添加成功！', 'success')
            return redirect(url_for('patient.medical_record_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    patients = patient_services.get_all_patients_for_dropdown()
    return render_template('patient/medical_record_form.html', record=None, patients=patients)


@patient_bp.route('/medical-record/detail/<int:id>')
def medical_record_detail(id):
    """病历详情"""
    record = record_services.get_medical_record_by_id(id)
    return render_template('patient/medical_record_detail.html', record=record)


# ============= 挂号预约管理 =============

@patient_bp.route('/appointments')
def appointment_list():
    """预约列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    pagination = appointment_services.get_appointments_with_pagination(page=page, status=status)
    appointments = pagination.items
    
    return render_template('patient/appointment_list.html',
                         appointments=appointments,
                         pagination=pagination,
                         status=status)


@patient_bp.route('/appointment/add', methods=['GET', 'POST'])
def appointment_add():
    """添加预约"""
    if request.method == 'POST':
        try:
            appointment_services.add_new_appointment(request.form)
            flash('预约添加成功！', 'success')
            return redirect(url_for('patient.appointment_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    patients = patient_services.get_all_patients_for_dropdown()
    return render_template('patient/appointment_form.html', appointment=None, patients=patients)


@patient_bp.route('/appointment/update-status/<int:id>', methods=['POST'])
def appointment_update_status(id):
    """更新预约状态"""
    try:
        status = request.form.get('status')
        appointment_services.update_appointment_status(id, status)
        flash('预约状态更新成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失败：{str(e)}', 'error')
    
    return redirect(url_for('patient.appointment_list'))
