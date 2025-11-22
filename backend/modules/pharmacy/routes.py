"""
药品管理子系统 - 路由
Pharmacy Management - Routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from . import pharmacy_bp
from backend.models import Medicine, MedicineInventory, MedicinePurchase
from backend.extensions import db
from datetime import datetime


# ============= 药品信息管理 =============

@pharmacy_bp.route('/')
def index():
    """药品管理首页"""
    return render_template('pharmacy_index.html')


@pharmacy_bp.route('/medicines')
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
    
    query = MedicinePurchase.query
    if status:
        query = query.filter_by(status=status)
    
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
            
            # 生成采购单号
            purchase_no = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            purchase = MedicinePurchase(
                purchase_no=purchase_no,
                medicine_id=request.form.get('medicine_id', type=int),
                supplier=request.form.get('supplier'),
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
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
        
        # 更新采购状态
        purchase.status = 'received'
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
        
        db.session.commit()
        flash('收货成功，库存已更新！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'收货失败：{str(e)}', 'error')
    
    return redirect(url_for('pharmacy.purchase_list'))

