from flask import Blueprint, request, jsonify
from app import db
from app.models import Product, PriceData
from app.services.data_service import DataService
from datetime import datetime

bp = Blueprint('products', __name__)


@bp.route('', methods=['GET'])
def get_products():
    """获取产品列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    product_type = request.args.get('type')
    
    query = Product.query
    if product_type:
        query = query.filter_by(type=product_type)
    
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'items': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    """获取单个产品"""
    product = Product.query.get_or_404(id)
    return jsonify(product.to_dict())


@bp.route('', methods=['POST'])
def create_product():
    """创建产品"""
    data = request.get_json()
    
    # 检查产品代码是否已存在
    if Product.query.filter_by(code=data['code']).first():
        return jsonify({'error': 'Product code already exists'}), 400
    
    product = Product(
        code=data['code'],
        name=data['name'],
        type=data['type'],
        category=data.get('category'),
        fee_rate=data.get('fee_rate', 0),
        purchase_fee=data.get('purchase_fee', 0),
        redemption_fee=data.get('redemption_fee', 0),
        description=data.get('description')
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify(product.to_dict()), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_product(id):
    """更新产品"""
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.type = data.get('type', product.type)
    product.category = data.get('category', product.category)
    product.fee_rate = data.get('fee_rate', product.fee_rate)
    product.purchase_fee = data.get('purchase_fee', product.purchase_fee)
    product.redemption_fee = data.get('redemption_fee', product.redemption_fee)
    product.description = data.get('description', product.description)
    
    db.session.commit()
    
    return jsonify(product.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    """删除产品"""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'})


@bp.route('/<string:code>/data', methods=['GET'])
def get_product_data(code):
    """获取产品历史数据"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = PriceData.query.filter_by(product_code=code)
    
    if start_date:
        query = query.filter(PriceData.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(PriceData.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    data = query.order_by(PriceData.date.asc()).all()
    
    return jsonify([d.to_dict() for d in data])


@bp.route('/sync', methods=['POST'])
def sync_products():
    """同步产品数据"""
    data = request.get_json()
    codes = data.get('codes', [])
    
    if not codes:
        return jsonify({'error': 'No product codes provided'}), 400
    
    results = []
    for code in codes:
        try:
            result = DataService.sync_product_data(code)
            results.append({'code': code, 'status': 'success', 'records': result})
        except Exception as e:
            results.append({'code': code, 'status': 'error', 'message': str(e)})
    
    return jsonify({'results': results})


@bp.route('/init-defaults', methods=['POST'])
def init_default_products():
    """初始化默认产品"""
    default_products = [
        {
            'code': '513100',
            'name': '纳指ETF',
            'type': 'ETF',
            'category': '美股指数',
            'description': '纳斯达克100指数ETF'
        },
        {
            'code': '513500',
            'name': '标普500ETF',
            'type': 'ETF',
            'category': '美股指数',
            'description': '标普500指数ETF'
        },
        {
            'code': '515080',
            'name': '红利低波ETF',
            'type': 'ETF',
            'category': 'A股策略指数',
            'description': '中证红利低波动指数ETF'
        },
        {
            'code': '560050',
            'name': '中证A50ETF',
            'type': 'ETF',
            'category': 'A股宽基指数',
            'description': '中证A50指数ETF'
        },
        {
            'code': '000171',
            'name': '混合债券基金',
            'type': '混合型',
            'category': '偏债混合',
            'description': '易方达裕丰回报债券'
        }
    ]
    
    created = []
    for prod_data in default_products:
        if not Product.query.filter_by(code=prod_data['code']).first():
            product = Product(**prod_data)
            db.session.add(product)
            created.append(prod_data['code'])
    
    db.session.commit()
    
    return jsonify({
        'message': f'Created {len(created)} default products',
        'created': created
    })
