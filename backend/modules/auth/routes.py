"""
认证模块 - 路由
Authentication - Routes
"""
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from . import auth_bp
from backend.models import User
from backend.extensions import db
from datetime import datetime
from functools import wraps


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


# ============= 权限装饰器 =============

def role_required(*roles):
    """角色权限装饰器"""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role', 'user')
            
            if user_role not in roles and 'admin' not in roles:
                return error_response('权限不足', 'FORBIDDEN', 403)
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ============= 用户注册登录 =============

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        required_fields = ['username', 'password']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段：{field}', 'MISSING_FIELD')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return error_response('用户名已存在', 'USERNAME_EXISTS')
        
        # 处理邮箱字段：空字符串转为None，避免唯一约束冲突
        email = data.get('email')
        email = email if email and email.strip() else None
        
        # 检查邮箱是否已存在（只检查非空邮箱）
        if email:
            if User.query.filter_by(email=email).first():
                return error_response('邮箱已被使用', 'EMAIL_EXISTS')
        
        # 密码长度验证
        if len(data['password']) < 6:
            return error_response('密码长度至少6位', 'PASSWORD_TOO_SHORT')
        
        # 处理其他可选字段：空字符串转为None
        phone = data.get('phone')
        phone = phone if phone and phone.strip() else None
        
        real_name = data.get('real_name')
        real_name = real_name if real_name and real_name.strip() else None
        
        department = data.get('department')
        department = department if department and department.strip() else None
        
        # 创建用户
        user = User(
            username=data['username'],
            email=email,
            phone=phone,
            real_name=real_name,
            role=data.get('role', 'user'),
            department=department
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # 获取用户ID

        # 如果是普通用户，自动创建病人记录
        if user.role == 'user' and phone:
            from backend.models import Patient, PatientUserLink
            from backend.modules.patient.patient_services import generate_patient_no

            # 生成病人编号
            patient_no = generate_patient_no()

            # 创建病人记录（基础信息）
            patient = Patient(
                patient_no=patient_no,
                name=real_name or data['username'],  # 使用真实姓名或用户名
                gender='未知',  # 默认未知，后续完善
                phone=phone,
                age=None,
                id_card=None,
                address=None,
                emergency_contact=None,
                emergency_phone=None
            )
            db.session.add(patient)
            db.session.flush()  # 获取病人ID

            # 创建用户-病人关联
            link = PatientUserLink(user_id=user.id, patient_id=patient.id)
            db.session.add(link)
            
            # 将病人添加到用户的可管理列表（用于家庭成员管理和在线挂号）
            user.managed_patients.append(patient)

        if user.role == 'doctor':
            from backend.models import Doctor, DoctorUserLink

            # 优先使用 doctor_no，如果没有则使用 username
            doctor_no = data.get('doctor_no') or data.get('doctorNo') or data['username']
            existing_doctor = Doctor.query.filter_by(doctor_no=doctor_no).first()

            if existing_doctor:
                doctor = existing_doctor
            else:
                # 医生注册时只创建基本记录，详细信息需要后续完善
                # 这样可以确保首次登录时会弹出完善信息的弹窗
                doctor = Doctor(
                    doctor_no=doctor_no,
                    name=real_name or data['username'],
                    # 不在注册时填充 gender, phone, email, department, title 等字段
                    # 这些字段留空，让医生首次登录时完善
                    status='active'
                )
                db.session.add(doctor)
                db.session.flush()

            doctor_link = DoctorUserLink(user_id=user.id, doctor_id=doctor.id)
            db.session.add(doctor_link)

        db.session.commit()
        
        return success_response(
            user.to_dict(),
            '注册成功',
            'REGISTER_SUCCESS'
        )
    
    except Exception as e:
        db.session.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"[ERROR] 注册失败: {str(e)}")
        print(f"[ERROR] 详细错误:\n{error_detail}")
        return error_response(f'注册失败：{str(e)}', 'REGISTER_ERROR', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return error_response('用户名和密码不能为空', 'MISSING_CREDENTIALS')
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return error_response('用户名或密码错误', 'INVALID_CREDENTIALS', 401)
        
        # 验证密码（兼容早期明文密码存储的用户数据）
        if not user.check_password(password):
            # 兼容处理：如果数据库中 password_hash 字段恰好等于明文密码，视为旧数据，自动迁移为哈希存储
            if user.password_hash == password:
                user.set_password(password)
                db.session.commit()
            else:
                return error_response('用户名或密码错误', 'INVALID_CREDENTIALS', 401)
        
        # 检查用户是否激活
        if not user.is_active:
            return error_response('账号已被禁用', 'ACCOUNT_DISABLED', 403)
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成JWT Token
        additional_claims = {
            'role': user.role,
            'department': user.department
        }
        
        # 注意：根据最新JWT规范，sub(Subject)必须为字符串
        # 因此在创建Token时将用户ID转换为字符串，避免"Subject must be a string"错误
        identity = str(user.id)
        
        access_token = create_access_token(
            identity=identity,
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=identity)
        
        user_data = user.to_dict()

        if user.role == 'doctor':
            from backend.models import DoctorUserLink

            link = DoctorUserLink.query.filter_by(user_id=user.id).first()
            if link and link.doctor:
                user_data['doctor'] = link.doctor.to_dict()

        return success_response({
            'user': user_data,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }, '登录成功', 'LOGIN_SUCCESS')
    
    except Exception as e:
        return error_response(f'登录失败：{str(e)}', 'LOGIN_ERROR', 500)


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新Token"""
    try:
        identity = get_jwt_identity()
        user = User.query.get(identity)
        
        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)
        
        if not user.is_active:
            return error_response('账号已被禁用', 'ACCOUNT_DISABLED', 403)
        
        additional_claims = {
            'role': user.role,
            'department': user.department
        }
        
        # 刷新Token时也确保JWT Subject为字符串类型，避免"Subject must be a string"错误
        new_identity = str(user.id)
        access_token = create_access_token(
            identity=new_identity,
            additional_claims=additional_claims
        )
        
        return success_response({
            'access_token': access_token,
            'token_type': 'Bearer'
        }, 'Token刷新成功', 'TOKEN_REFRESHED')
    
    except Exception as e:
        return error_response(f'刷新Token失败：{str(e)}', 'REFRESH_ERROR', 500)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前登录用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)

        data = user.to_dict()

        if user.role == 'doctor':
            from backend.models import DoctorUserLink

            link = DoctorUserLink.query.filter_by(user_id=user.id).first()
            if link and link.doctor:
                data['doctor'] = link.doctor.to_dict()
        
        return success_response(data)
    
    except Exception as e:
        return error_response(f'获取用户信息失败：{str(e)}', 'GET_USER_ERROR', 500)


@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新个人信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        # 更新允许的字段
        if 'email' in data:
            # 检查邮箱是否被其他用户使用
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return error_response('邮箱已被使用', 'EMAIL_EXISTS')
            user.email = data['email']
        
        if 'phone' in data:
            user.phone = data['phone']
        if 'real_name' in data:
            user.real_name = data['real_name']
        if 'department' in data:
            user.department = data['department']
        
        db.session.commit()
        
        return success_response(user.to_dict(), '个人信息更新成功', 'PROFILE_UPDATED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新个人信息失败：{str(e)}', 'UPDATE_PROFILE_ERROR', 500)


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return error_response('旧密码和新密码不能为空', 'MISSING_PASSWORDS')
        
        # 验证旧密码
        if not user.check_password(old_password):
            return error_response('旧密码错误', 'INVALID_OLD_PASSWORD', 401)
        
        # 新密码长度验证
        if len(new_password) < 6:
            return error_response('新密码长度至少6位', 'PASSWORD_TOO_SHORT')
        
        # 设置新密码
        user.set_password(new_password)
        db.session.commit()
        
        return success_response(None, '密码修改成功', 'PASSWORD_CHANGED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'修改密码失败：{str(e)}', 'CHANGE_PASSWORD_ERROR', 500)


# ============= 用户管理（仅管理员） =============

@auth_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_users():
    """获取用户列表（管理员）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        role = request.args.get('role', '')
        
        query = User.query
        
        # 搜索
        if search:
            query = query.filter(
                (User.username.like(f'%{search}%')) |
                (User.real_name.like(f'%{search}%')) |
                (User.email.like(f'%{search}%'))
            )
        
        # 角色过滤
        if role:
            query = query.filter_by(role=role)
        
        # 分页
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = [user.to_dict() for user in pagination.items]
        
        return success_response({
            'list': users_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    
    except Exception as e:
        return error_response(f'获取用户列表失败：{str(e)}', 'GET_USERS_ERROR', 500)


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    """更新用户信息（管理员）"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')
        
        # 更新字段
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'department' in data:
            user.department = data['department']
        
        db.session.commit()
        
        return success_response(user.to_dict(), '用户信息更新成功', 'USER_UPDATED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新用户信息失败：{str(e)}', 'UPDATE_USER_ERROR', 500)


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """删除用户（管理员）"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)
        
        # 不能删除管理员账号
        if user.role == 'admin':
            return error_response('不能删除管理员账号', 'CANNOT_DELETE_ADMIN')
        
        db.session.delete(user)
        db.session.commit()
        
        return success_response(None, '用户删除成功', 'USER_DELETED')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除用户失败：{str(e)}', 'DELETE_USER_ERROR', 500)


# ============= 病人信息管理 =============

@auth_bp.route('/check-patient-info', methods=['GET'])
@jwt_required()
def check_patient_info():
    """检查当前用户的病人信息是否完整"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)

        # 只有普通用户才需要检查病人信息
        if user.role != 'user':
            return success_response({
                'has_patient_info': False,
                'is_complete': True,
                'patient': None
            }, '非普通用户，无需病人信息')

        # 查找关联的病人记录
        from backend.models import PatientUserLink, Patient
        link = PatientUserLink.query.filter_by(user_id=user.id).first()

        if not link:
            return success_response({
                'has_patient_info': False,
                'is_complete': False,
                'patient': None
            }, '未找到病人信息')

        patient = link.patient

        # 检查信息是否完整
        is_complete = all([
            patient.name and patient.name != user.username,
            patient.gender and patient.gender != '未知',
            patient.age is not None,
            patient.id_card,
            patient.address
        ])

        return success_response({
            'has_patient_info': True,
            'is_complete': is_complete,
            'patient': patient.to_dict()
        }, '病人信息检查完成')

    except Exception as e:
        return error_response(f'检查病人信息失败：{str(e)}', 'CHECK_PATIENT_ERROR', 500)


@auth_bp.route('/complete-patient-info', methods=['POST'])
@jwt_required()
def complete_patient_info():
    """完善病人信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)

        if user.role != 'user':
            return error_response('只有普通用户才能完善病人信息', 'INVALID_ROLE')

        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        # 查找关联的病人记录
        from backend.models import PatientUserLink, Patient
        link = PatientUserLink.query.filter_by(user_id=user.id).first()

        if not link:
            return error_response('未找到病人信息', 'PATIENT_NOT_FOUND', 404)

        patient = link.patient

        # 更新病人信息
        if 'name' in data:
            patient.name = data['name']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'age' in data:
            try:
                patient.age = int(data['age'])
            except (TypeError, ValueError):
                patient.age = None
        if 'id_card' in data:
            patient.id_card = data['id_card']
        if 'address' in data:
            patient.address = data['address']
        if 'emergency_contact' in data:
            patient.emergency_contact = data['emergency_contact']
        if 'emergency_phone' in data:
            patient.emergency_phone = data['emergency_phone']

        # 同步更新用户的真实姓名
        if 'name' in data:
            user.real_name = data['name']

        db.session.commit()

        return success_response(
            patient.to_dict(),
            '病人信息完善成功',
            'PATIENT_INFO_COMPLETED'
        )

    except Exception as e:
        db.session.rollback()
        return error_response(f'完善病人信息失败：{str(e)}', 'COMPLETE_PATIENT_ERROR', 500)


# ============= 医生信息管理 =============

@auth_bp.route('/check-doctor-info', methods=['GET'])
@jwt_required()
def check_doctor_info():
    """检查当前用户的医生信息是否完整"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)

        # 只有医生才需要检查医生信息
        if user.role != 'doctor':
            return success_response({
                'has_doctor_info': False,
                'is_complete': True,
                'doctor': None
            }, '非医生用户，无需医生信息')

        # 查找关联的医生记录
        from backend.models import DoctorUserLink
        link = DoctorUserLink.query.filter_by(user_id=user.id).first()

        if not link or not link.doctor:
            return success_response({
                'has_doctor_info': False,
                'is_complete': False,
                'doctor': None
            }, '未找到医生信息')

        doctor = link.doctor

        # 检查信息是否完整（必填字段：doctor_no, name, gender, department, title, phone）
        # 这些是医生执业必须的基本信息
        is_complete = all([
            doctor.doctor_no,
            doctor.name,
            doctor.gender,
            doctor.department,
            doctor.title,
            doctor.phone
        ])

        return success_response({
            'has_doctor_info': True,
            'is_complete': is_complete,
            'doctor': doctor.to_dict()
        }, '医生信息检查完成')

    except Exception as e:
        return error_response(f'检查医生信息失败：{str(e)}', 'CHECK_DOCTOR_ERROR', 500)


@auth_bp.route('/complete-doctor-info', methods=['POST'])
@jwt_required()
def complete_doctor_info():
    """完善医生信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('用户不存在', 'USER_NOT_FOUND', 404)

        if user.role != 'doctor':
            return error_response('只有医生才能完善医生信息', 'INVALID_ROLE')

        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        # 验证必填字段
        required_fields = {
            'name': '姓名',
            'gender': '性别',
            'department': '科室',
            'title': '职称',
            'phone': '联系电话'
        }
        for field, field_name in required_fields.items():
            if not data.get(field):
                return error_response(f'{field_name}为必填字段', 'MISSING_FIELD')
        
        # 验证手机号格式
        import re
        if not re.match(r'^1[3-9]\d{9}$', data['phone']):
            return error_response('手机号格式不正确', 'INVALID_PHONE')

        from backend.models import DoctorUserLink, Doctor
        from datetime import datetime

        link = DoctorUserLink.query.filter_by(user_id=user.id).first()

        if link and link.doctor:
            # 更新已有医生信息
            doctor = link.doctor
        else:
            # 创建新的医生记录
            doctor_no = user.username
            existing = Doctor.query.filter_by(doctor_no=doctor_no).first()
            if existing:
                doctor = existing
            else:
                doctor = Doctor(
                    doctor_no=doctor_no,
                    name=data['name'],
                    status='active'
                )
                db.session.add(doctor)
                db.session.flush()

            # 创建关联
            if not link:
                link = DoctorUserLink(user_id=user.id, doctor_id=doctor.id)
                db.session.add(link)
            else:
                link.doctor_id = doctor.id

        # 更新医生信息
        if 'name' in data:
            doctor.name = data['name']
        if 'gender' in data:
            doctor.gender = data['gender']
        if 'age' in data:
            try:
                doctor.age = int(data['age']) if data['age'] else None
            except (TypeError, ValueError):
                doctor.age = None
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
        if 'hire_date' in data and data['hire_date']:
            try:
                doctor.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass

        # 同步更新用户的真实姓名和科室
        if 'name' in data:
            user.real_name = data['name']
        if 'department' in data:
            user.department = data['department']

        db.session.commit()

        return success_response(
            doctor.to_dict(),
            '医生信息完善成功',
            'DOCTOR_INFO_COMPLETED'
        )

    except Exception as e:
        db.session.rollback()
        return error_response(f'完善医生信息失败：{str(e)}', 'COMPLETE_DOCTOR_ERROR', 500)
