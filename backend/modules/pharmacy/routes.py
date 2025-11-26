"""
药品管理子系统 - 路由
Pharmacy Management - Routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from . import pharmacy_bp
from backend.models import Medicine, MedicineInventory, MedicinePurchase, MedicationRequest
from backend.extensions import db
from datetime import datetime


def success_response(data=None, message='操作成功', code='SUCCESS'):
    return jsonify({
        'success': True,
        'message': message,
        'code': code,
        'data': data
    })


def error_response(message='操作失败', code='ERROR', status_code=400):
    return jsonify({
        'success': False,
        'message': message,
        'code': code,
        'data': None
    }), status_code


# ============= 药品信息管理 =============

@pharmacy_bp.route('/')
def index():
    """药品管理首页"""
    return render_template('pharmacy_index.html')


@pharmacy_bp.route('/medicines-page')
def medicine_list():
    """药品列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Medicine.query
    if search:
        query = query.filter(
            (Medicine.name.like(f'%{search}%')) | 
            (Medicine.medicine_no.like(f'%{search}%')) |
            (Medicine.generic_name.like(f'%{search}%'))
        )
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.order_by(Medicine.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    medicines = pagination.items
    
    # 获取所有分类用于筛选
    categories = db.session.query(Medicine.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('medicine_list.html', 
                         medicines=medicines, 
                         pagination=pagination,
                         search=search,
                         category=category,
                         categories=categories)


@pharmacy_bp.route('/medicine/add', methods=['GET', 'POST'])
def medicine_add():
    """添加药品"""
    if request.method == 'POST':
        try:
            medicine = Medicine(
                medicine_no=request.form.get('medicine_no'),
                name=request.form.get('name'),
                generic_name=request.form.get('generic_name'),
                category=request.form.get('category'),
                specification=request.form.get('specification'),
                unit=request.form.get('unit'),
                manufacturer=request.form.get('manufacturer'),
                price=request.form.get('price', type=float),
                prescription_required=request.form.get('prescription_required') == 'on',
                usage=request.form.get('usage'),
                indications=request.form.get('indications'),
                contraindications=request.form.get('contraindications'),
                side_effects=request.form.get('side_effects'),
                storage_conditions=request.form.get('storage_conditions')
            )
            db.session.add(medicine)
            db.session.flush()  # 获取medicine.id
            
            # 创建库存记录
            inventory = MedicineInventory(
                medicine_id=medicine.id,
                quantity=0,
                min_stock=request.form.get('min_stock', type=int) or 0
            )
            db.session.add(inventory)
            
            db.session.commit()
            flash('药品信息添加成功！', 'success')
            return redirect(url_for('pharmacy.medicine_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    return render_template('medicine_form.html', medicine=None)


@pharmacy_bp.route('/medicine/edit/<int:id>', methods=['GET', 'POST'])
def medicine_edit(id):
    """编辑药品信息"""
    medicine = Medicine.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            medicine.name = request.form.get('name')
            medicine.generic_name = request.form.get('generic_name')
            medicine.category = request.form.get('category')
            medicine.specification = request.form.get('specification')
            medicine.unit = request.form.get('unit')
            medicine.manufacturer = request.form.get('manufacturer')
            medicine.price = request.form.get('price', type=float)
            medicine.prescription_required = request.form.get('prescription_required') == 'on'
            medicine.usage = request.form.get('usage')
            medicine.indications = request.form.get('indications')
            medicine.contraindications = request.form.get('contraindications')
            medicine.side_effects = request.form.get('side_effects')
            medicine.storage_conditions = request.form.get('storage_conditions')
            medicine.status = request.form.get('status')
            
            db.session.commit()
            flash('药品信息更新成功！', 'success')
            return redirect(url_for('pharmacy.medicine_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('medicine_form.html', medicine=medicine)


@pharmacy_bp.route('/medicine/delete/<int:id>', methods=['POST'])
def medicine_delete(id):
    """删除药品"""
    try:
        medicine = Medicine.query.get_or_404(id)
        db.session.delete(medicine)
        db.session.commit()
        flash('药品信息已删除！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('pharmacy.medicine_list'))


@pharmacy_bp.route('/medicine/detail/<int:id>')
def medicine_detail(id):
    """药品详情"""
    medicine = Medicine.query.get_or_404(id)
    return render_template('medicine_detail.html', medicine=medicine)


# ============= 药品库存管理 =============

@pharmacy_bp.route('/inventory')
def inventory_list():
    """库存列表"""
    page = request.args.get('page', 1, type=int)
    low_stock = request.args.get('low_stock', type=bool)
    
    query = MedicineInventory.query.join(Medicine)
    
    if low_stock:
        # 查询低库存药品
        query = query.filter(MedicineInventory.quantity <= MedicineInventory.min_stock)
    
    pagination = query.order_by(MedicineInventory.updated_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    inventories = pagination.items
    
    # 统计信息
    total_medicines = Medicine.query.count()
    low_stock_count = MedicineInventory.query.filter(
        MedicineInventory.quantity <= MedicineInventory.min_stock
    ).count()
    
    return render_template('inventory_list.html', 
                         inventories=inventories, 
                         pagination=pagination,
                         low_stock=low_stock,
                         total_medicines=total_medicines,
                         low_stock_count=low_stock_count)


@pharmacy_bp.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
def inventory_edit(id):
    """编辑库存"""
    inventory = MedicineInventory.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            inventory.quantity = request.form.get('quantity', type=int)
            inventory.min_stock = request.form.get('min_stock', type=int)
            inventory.max_stock = request.form.get('max_stock', type=int)
            inventory.location = request.form.get('location')
            inventory.batch_no = request.form.get('batch_no')
            
            prod_date_str = request.form.get('production_date')
            if prod_date_str:
                inventory.production_date = datetime.strptime(prod_date_str, '%Y-%m-%d').date()
            
            exp_date_str = request.form.get('expiry_date')
            if exp_date_str:
                inventory.expiry_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
            
            db.session.commit()
            flash('库存信息更新成功！', 'success')
            return redirect(url_for('pharmacy.inventory_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('inventory_form.html', inventory=inventory)


@pharmacy_bp.route('/inventory/adjust/<int:id>', methods=['POST'])
def inventory_adjust(id):
    """调整库存数量"""
    try:
        inventory = MedicineInventory.query.get_or_404(id)
        adjustment = request.form.get('adjustment', type=int)
        
        if adjustment:
            inventory.quantity += adjustment
            if inventory.quantity < 0:
                inventory.quantity = 0
            db.session.commit()
            flash('库存数量已调整！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'调整失败：{str(e)}', 'error')
    
    return redirect(url_for('pharmacy.inventory_list'))


# ============= 药品采购管理 =============

@pharmacy_bp.route('/purchases')
def purchase_list():
    """采购列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')

    query = MedicinePurchase.query
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)

    pagination = query.order_by(MedicinePurchase.purchase_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    purchases = pagination.items
    
    # 统计信息
    total_purchases = MedicinePurchase.query.count()
    pending_count = MedicinePurchase.query.filter_by(status='pending').count()
    
    return render_template('purchase_list.html', 
                         purchases=purchases, 
                         pagination=pagination,
                         status=status,
                         priority=priority,
                         total_purchases=total_purchases,
                         pending_count=pending_count)


@pharmacy_bp.route('/purchase/add', methods=['GET', 'POST'])
def purchase_add():
    """添加采购"""
    if request.method == 'POST':
        try:
            quantity = request.form.get('quantity', type=int)
            unit_price = request.form.get('unit_price', type=float)
            total_price = quantity * unit_price
            priority = request.form.get('priority') or 'medium'

            # 生成采购单号
            purchase_no = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            purchase = MedicinePurchase(
                purchase_no=purchase_no,
                medicine_id=request.form.get('medicine_id', type=int),
                supplier=request.form.get('supplier'),
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                priority=priority,
                purchaser=request.form.get('purchaser'),
                notes=request.form.get('notes')
            )
            
            exp_date_str = request.form.get('expected_delivery_date')
            if exp_date_str:
                purchase.expected_delivery_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
            
            db.session.add(purchase)
            db.session.commit()
            flash('采购单添加成功！', 'success')
            return redirect(url_for('pharmacy.purchase_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    medicines = Medicine.query.filter_by(status='active').all()
    return render_template('purchase_form.html', purchase=None, medicines=medicines)


@pharmacy_bp.route('/purchase/detail/<int:id>')
def purchase_detail(id):
    """采购详情"""
    purchase = MedicinePurchase.query.get_or_404(id)
    return render_template('purchase_detail.html', purchase=purchase)


@pharmacy_bp.route('/purchase/receive/<int:id>', methods=['POST'])
def purchase_receive(id):
    """确认收货"""
    try:
        purchase = MedicinePurchase.query.get_or_404(id)
        
        # 仅允许对待处理的采购单进行收货操作，防止重复入库
        if purchase.status != 'pending':
            flash('当前采购单状态不允许重复收货处理', 'warning')
            return redirect(url_for('pharmacy.purchase_list'))

        # 更新采购状态
        purchase.status = 'completed'
        purchase.actual_delivery_date = datetime.now().date()
        
        # 获取批次和日期信息
        batch_no = request.form.get('batch_no')
        prod_date_str = request.form.get('production_date')
        exp_date_str = request.form.get('expiry_date')
        
        if batch_no:
            purchase.batch_no = batch_no
        if prod_date_str:
            purchase.production_date = datetime.strptime(prod_date_str, '%Y-%m-%d').date()
        if exp_date_str:
            purchase.expiry_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
        
        # 更新库存
        inventory = MedicineInventory.query.filter_by(medicine_id=purchase.medicine_id).first()
        if inventory:
            inventory.quantity += purchase.quantity
            inventory.last_restock_date = datetime.now()
            if batch_no:
                inventory.batch_no = batch_no
            if prod_date_str:
                inventory.production_date = datetime.strptime(prod_date_str, '%Y-%m-%d').date()
            if exp_date_str:
                inventory.expiry_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
        else:
            # 若库存中不存在该药品的记录，则视为新药入库
            inventory = MedicineInventory(
                medicine_id=purchase.medicine_id,
                quantity=purchase.quantity
            )
            inventory.last_restock_date = datetime.now()
            if batch_no:
                inventory.batch_no = batch_no
            if prod_date_str:
                inventory.production_date = datetime.strptime(prod_date_str, '%Y-%m-%d').date()
            if exp_date_str:
                inventory.expiry_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
            db.session.add(inventory)

        db.session.commit()
        flash('收货成功，库存已更新！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'收货失败：{str(e)}', 'error')
    
    return redirect(url_for('pharmacy.purchase_list'))


@pharmacy_bp.route('/purchase-orders', methods=['GET'])
def get_purchase_orders():
    """获取采购列表（API）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        priority = request.args.get('priority', '')

        query = MedicinePurchase.query
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)

        pagination = query.order_by(MedicinePurchase.purchase_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        items = [p.to_dict() for p in pagination.items]

        # 统计信息
        total_purchases = MedicinePurchase.query.count()
        pending_count = MedicinePurchase.query.filter_by(status='pending').count()

        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'stats': {
                'total_purchases': total_purchases,
                'pending_count': pending_count
            }
        })
    except Exception as e:
        return error_response(f'获取采购列表失败：{str(e)}', 'GET_PURCHASE_ORDERS_ERROR', 500)


@pharmacy_bp.route('/purchase-orders', methods=['POST'])
def create_purchase_order():
    """创建采购单（API）"""
    try:
        data = request.get_json() or {}

        medicine_id = data.get('medicine_id')
        quantity = data.get('quantity')
        unit_price = data.get('unit_price')

        if not quantity or not unit_price:
            return error_response('缺少必填字段：quantity / unit_price', 'MISSING_FIELD')

        try:
            quantity = int(quantity)
            unit_price = float(unit_price)
        except (TypeError, ValueError):
            return error_response('数量或单价格式错误', 'INVALID_NUMBER')

        # 处理药品：已有药品 或 新药品
        medicine = None
        if medicine_id:
            medicine = Medicine.query.get(medicine_id)
            if not medicine:
                return error_response('所选药品不存在', 'MEDICINE_NOT_FOUND', 404)
        else:
            medicine_no = data.get('medicine_no')
            medicine_name = data.get('medicine_name') or data.get('name')
            category = data.get('category')

            if not medicine_no or not medicine_name or not category:
                return error_response('新药品必须提供：药品编号、药品名称、分类', 'MISSING_NEW_MEDICINE_FIELD')

            # 若编号已存在则复用原有药品，避免重复创建
            existing = Medicine.query.filter_by(medicine_no=medicine_no).first()
            if existing:
                medicine = existing
            else:
                medicine = Medicine(
                    medicine_no=medicine_no,
                    name=medicine_name,
                    category=category,
                    price=unit_price,
                    status='active'
                )
                db.session.add(medicine)
                db.session.flush()

        medicine_id = medicine.id if medicine else medicine_id
        total_price = quantity * unit_price
        priority = data.get('priority') or 'medium'

        # 生成采购单号
        purchase_no = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"

        purchase = MedicinePurchase(
            purchase_no=purchase_no,
            medicine_id=medicine_id,
            supplier=data.get('supplier'),
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            priority=priority,
            purchaser=data.get('purchaser'),
            notes=data.get('notes')
        )

        exp_date_str = data.get('expected_delivery_date')
        if exp_date_str:
            try:
                purchase.expected_delivery_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('预计到货日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')

        db.session.add(purchase)
        db.session.commit()

        return success_response(purchase.to_dict(), '采购单创建成功', 'PURCHASE_CREATED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建采购单失败：{str(e)}', 'CREATE_PURCHASE_ORDER_ERROR', 500)


@pharmacy_bp.route('/purchase-orders/<int:purchase_id>', methods=['GET'])
def get_purchase_order_detail(purchase_id):
    """获取采购单详情（API）"""
    try:
        purchase = MedicinePurchase.query.get(purchase_id)
        if not purchase:
            return error_response('采购单不存在', 'PURCHASE_NOT_FOUND', 404)
        return success_response(purchase.to_dict())
    except Exception as e:
        return error_response(f'获取采购单详情失败：{str(e)}', 'GET_PURCHASE_ORDER_ERROR', 500)


@pharmacy_bp.route('/purchase-orders/<int:purchase_id>/receive', methods=['POST'])
def receive_purchase_order(purchase_id):
    """确认收货（API）"""
    try:
        purchase = MedicinePurchase.query.get(purchase_id)
        if not purchase:
            return error_response('采购单不存在', 'PURCHASE_NOT_FOUND', 404)

        if purchase.status != 'pending':
            return error_response('当前采购单状态不允许重复收货处理', 'INVALID_PURCHASE_STATUS')

        data = request.get_json() or {}
        batch_no = data.get('batch_no')
        prod_date_str = data.get('production_date')
        exp_date_str = data.get('expiry_date')

        if not prod_date_str or not exp_date_str:
            return error_response('收货时必须提供生产日期和过期日期', 'MISSING_DATE_FIELD')

        try:
            prod_date = datetime.strptime(prod_date_str, '%Y-%m-%d').date()
        except ValueError:
            return error_response('生产日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')

        try:
            exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
        except ValueError:
            return error_response('过期日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')

        # 更新采购状态
        purchase.status = 'completed'
        purchase.actual_delivery_date = datetime.now().date()

        if batch_no:
            purchase.batch_no = batch_no
        purchase.production_date = prod_date
        purchase.expiry_date = exp_date

        # 更新库存（逻辑与表单版保持一致）
        inventory = MedicineInventory.query.filter_by(medicine_id=purchase.medicine_id).first()
        if inventory:
            inventory.quantity += purchase.quantity
            inventory.last_restock_date = datetime.now()
            if batch_no:
                inventory.batch_no = batch_no
            inventory.production_date = prod_date
            inventory.expiry_date = exp_date
        else:
            inventory = MedicineInventory(
                medicine_id=purchase.medicine_id,
                quantity=purchase.quantity
            )
            inventory.last_restock_date = datetime.now()
            if batch_no:
                inventory.batch_no = batch_no
            inventory.production_date = prod_date
            inventory.expiry_date = exp_date
            db.session.add(inventory)

        db.session.commit()
        return success_response(purchase.to_dict(), '收货成功，库存已更新', 'PURCHASE_RECEIVED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'收货失败：{str(e)}', 'RECEIVE_PURCHASE_ORDER_ERROR', 500)


@pharmacy_bp.route('/medication-requests', methods=['GET'])
def get_medication_requests():
    try:
        status = request.args.get('status', 'PENDING')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = MedicationRequest.query
        if status:
            query = query.filter_by(status=status)

        pagination = query.order_by(MedicationRequest.created_at.asc()).paginate(
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


@pharmacy_bp.route('/medication-requests/<int:request_id>/approve', methods=['POST'])
def approve_medication_request(request_id):
    try:
        medication_request = MedicationRequest.query.get(request_id)
        if not medication_request:
            return error_response('用药申请不存在', 'MEDICATION_REQUEST_NOT_FOUND', 404)

        if medication_request.status != 'PENDING':
            return error_response('当前状态不可审核', 'INVALID_MEDICATION_REQUEST_STATUS')

        inventory = MedicineInventory.query.filter_by(medicine_id=medication_request.medicine_id).first()
        if not inventory:
            return error_response('该药品暂无库存记录', 'INVENTORY_NOT_FOUND')

        if inventory.quantity < medication_request.quantity:
            return error_response('库存不足，无法通过审核', 'INSUFFICIENT_STOCK')

        inventory.quantity -= medication_request.quantity
        now = datetime.utcnow()
        medication_request.status = 'APPROVED'
        medication_request.approved_at = now
        medication_request.dispensed_at = now
        medication_request.updated_at = now

        # 如果关联了预约，将预约状态更新为"已完成"
        if medication_request.appointment_id:
            from backend.models import Appointment
            appointment = Appointment.query.get(medication_request.appointment_id)
            if appointment and appointment.status in ['pending', 'confirmed']:
                appointment.status = 'completed'

        db.session.commit()

        return success_response(medication_request.to_dict(), '审核通过并完成库存扣减，预约已完成', 'MEDICATION_REQUEST_APPROVED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'审核用药申请失败：{str(e)}', 'APPROVE_MEDICATION_REQUEST_ERROR', 500)


@pharmacy_bp.route('/medication-requests/<int:request_id>/reject', methods=['POST'])
def reject_medication_request(request_id):
    try:
        medication_request = MedicationRequest.query.get(request_id)
        if not medication_request:
            return error_response('用药申请不存在', 'MEDICATION_REQUEST_NOT_FOUND', 404)

        if medication_request.status != 'PENDING':
            return error_response('当前状态不可拒绝', 'INVALID_MEDICATION_REQUEST_STATUS')

        data = request.get_json() or {}
        reason = data.get('reason') or '管理员拒绝'

        medication_request.status = 'REJECTED'
        medication_request.reason = reason
        medication_request.updated_at = datetime.utcnow()

        db.session.commit()

        return success_response(medication_request.to_dict(), '用药申请已拒绝', 'MEDICATION_REQUEST_REJECTED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'拒绝用药申请失败：{str(e)}', 'REJECT_MEDICATION_REQUEST_ERROR', 500)


@pharmacy_bp.route('/medicines', methods=['GET'])
def get_medicines():
    """获取药品列表（API）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        status = request.args.get('status', '')

        query = Medicine.query

        if search:
            query = query.filter(
                (Medicine.name.like(f'%{search}%')) |
                (Medicine.medicine_no.like(f'%{search}%')) |
                (Medicine.generic_name.like(f'%{search}%'))
            )
        if category:
            query = query.filter_by(category=category)
        if status:
            query = query.filter_by(status=status)

        pagination = query.order_by(Medicine.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        medicines_data = [medicine.to_dict() for medicine in pagination.items]

        return success_response({
            'items': medicines_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(f'获取药品列表失败：{str(e)}', 'GET_MEDICINES_ERROR', 500)


@pharmacy_bp.route('/medicines/<int:medicine_id>', methods=['GET'])
def get_medicine(medicine_id):
    """获取药品详情（API）"""
    try:
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return error_response('药品不存在', 'MEDICINE_NOT_FOUND', 404)
        return success_response(medicine.to_dict())
    except Exception as e:
        return error_response(f'获取药品详情失败：{str(e)}', 'GET_MEDICINE_ERROR', 500)


@pharmacy_bp.route('/medicines', methods=['POST'])
def create_medicine():
    """创建药品（API）"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        required_fields = ['medicine_no', 'name', 'price']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必填字段：{field}', 'MISSING_FIELD')

        if Medicine.query.filter_by(medicine_no=data['medicine_no']).first():
            return error_response('药品编号已存在', 'MEDICINE_NO_EXISTS')

        price_value = data.get('price')
        try:
            price_value = float(price_value)
        except (TypeError, ValueError):
            return error_response('价格格式错误', 'INVALID_PRICE')

        medicine = Medicine(
            medicine_no=data['medicine_no'],
            name=data['name'],
            generic_name=data.get('generic_name'),
            category=data.get('category'),
            specification=data.get('specification'),
            unit=data.get('unit'),
            manufacturer=data.get('manufacturer'),
            price=price_value,
            prescription_required=data.get('prescription_required', False),
            usage=data.get('usage'),
            indications=data.get('indications'),
            contraindications=data.get('contraindications'),
            side_effects=data.get('side_effects'),
            storage_conditions=data.get('storage_conditions'),
            status=data.get('status', 'active')
        )

        db.session.add(medicine)
        db.session.flush()

        inventory_data = data.get('inventory') or {}
        inventory = MedicineInventory(
            medicine_id=medicine.id,
            quantity=inventory_data.get('quantity') or 0,
            min_stock=inventory_data.get('min_stock') or 0,
            max_stock=inventory_data.get('max_stock'),
            location=inventory_data.get('location'),
            batch_no=inventory_data.get('batch_no')
        )

        production_date_str = inventory_data.get('production_date')
        if production_date_str:
            try:
                inventory.production_date = datetime.strptime(production_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        expiry_date_str = inventory_data.get('expiry_date')
        if expiry_date_str:
            try:
                inventory.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        db.session.add(inventory)
        db.session.commit()

        return success_response(medicine.to_dict(), '药品创建成功', 'MEDICINE_CREATED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建药品失败：{str(e)}', 'CREATE_MEDICINE_ERROR', 500)


@pharmacy_bp.route('/medicines/<int:medicine_id>', methods=['PUT'])
def update_medicine(medicine_id):
    """更新药品信息（API）"""
    try:
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return error_response('药品不存在', 'MEDICINE_NOT_FOUND', 404)

        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 'INVALID_DATA')

        if 'medicine_no' in data and data['medicine_no'] != medicine.medicine_no:
            if Medicine.query.filter_by(medicine_no=data['medicine_no']).first():
                return error_response('药品编号已存在', 'MEDICINE_NO_EXISTS')
            medicine.medicine_no = data['medicine_no']

        if 'name' in data:
            medicine.name = data['name']
        if 'generic_name' in data:
            medicine.generic_name = data['generic_name']
        if 'category' in data:
            medicine.category = data['category']
        if 'specification' in data:
            medicine.specification = data['specification']
        if 'unit' in data:
            medicine.unit = data['unit']
        if 'manufacturer' in data:
            medicine.manufacturer = data['manufacturer']
        if 'price' in data:
            try:
                medicine.price = float(data['price']) if data['price'] is not None else None
            except (TypeError, ValueError):
                return error_response('价格格式错误', 'INVALID_PRICE')
        if 'prescription_required' in data:
            medicine.prescription_required = data['prescription_required']
        if 'usage' in data:
            medicine.usage = data['usage']
        if 'indications' in data:
            medicine.indications = data['indications']
        if 'contraindications' in data:
            medicine.contraindications = data['contraindications']
        if 'side_effects' in data:
            medicine.side_effects = data['side_effects']
        if 'storage_conditions' in data:
            medicine.storage_conditions = data['storage_conditions']
        if 'status' in data:
            medicine.status = data['status']

        inventory_data = data.get('inventory')
        if inventory_data is not None:
            if medicine.inventory is None:
                medicine.inventory = MedicineInventory(medicine_id=medicine.id)
            inventory = medicine.inventory

            if 'quantity' in inventory_data:
                inventory.quantity = inventory_data['quantity']
            if 'min_stock' in inventory_data:
                inventory.min_stock = inventory_data['min_stock']
            if 'max_stock' in inventory_data:
                inventory.max_stock = inventory_data['max_stock']
            if 'location' in inventory_data:
                inventory.location = inventory_data['location']
            if 'batch_no' in inventory_data:
                inventory.batch_no = inventory_data['batch_no']

            if 'production_date' in inventory_data:
                prod_str = inventory_data['production_date']
                if prod_str:
                    try:
                        inventory.production_date = datetime.strptime(prod_str, '%Y-%m-%d').date()
                    except ValueError:
                        return error_response('生产日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
                else:
                    inventory.production_date = None

            if 'expiry_date' in inventory_data:
                exp_str = inventory_data['expiry_date']
                if exp_str:
                    try:
                        inventory.expiry_date = datetime.strptime(exp_str, '%Y-%m-%d').date()
                    except ValueError:
                        return error_response('过期日期格式错误，应为YYYY-MM-DD', 'INVALID_DATE_FORMAT')
                else:
                    inventory.expiry_date = None

        db.session.commit()

        return success_response(medicine.to_dict(), '药品信息更新成功', 'MEDICINE_UPDATED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新药品信息失败：{str(e)}', 'UPDATE_MEDICINE_ERROR', 500)


@pharmacy_bp.route('/medicines/<int:medicine_id>', methods=['DELETE'])
def delete_medicine_api(medicine_id):
    """删除药品（API）"""
    try:
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return error_response('药品不存在', 'MEDICINE_NOT_FOUND', 404)

        db.session.delete(medicine)
        db.session.commit()

        return success_response(None, '药品删除成功', 'MEDICINE_DELETED')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除药品失败：{str(e)}', 'DELETE_MEDICINE_ERROR', 500)

