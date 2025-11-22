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
        
        # 检查邮箱是否已存在
        if data.get('email'):
            if User.query.filter_by(email=data['email']).first():
                return error_response('邮箱已被使用', 'EMAIL_EXISTS')
        
        # 密码长度验证
        if len(data['password']) < 6:
            return error_response('密码长度至少6位', 'PASSWORD_TOO_SHORT')
        
        # 创建用户
        user = User(
            username=data['username'],
            email=data.get('email'),
            phone=data.get('phone'),
            real_name=data.get('real_name'),
            role=data.get('role', 'user'),
            department=data.get('department')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
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
        
        # 验证密码
        if not user.check_password(password):
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
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return success_response({
            'user': user.to_dict(),
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
        
        access_token = create_access_token(
            identity=user.id,
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
        
        return success_response(user.to_dict())
    
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

