from flask import Blueprint, request, jsonify
from app import db
from app.models import BacktestScenario, ScenarioAllocation, BacktestResult, Holding, Product
from app.services.backtest_engine import BacktestEngine
from app.services.data_service import DataService
from datetime import datetime

bp = Blueprint('backtest', __name__)

# 产品名称到代码的映射
PRODUCT_NAME_TO_CODE = {
    'A50ETF': '560050',
    'SPY': 'SPY',
    'HONGLLB': '515080',  # 红利低波ETF
    'QQQ': 'QQQ',
    '纳指ETF': '513100',
    '标普ETF': '513500',
    '中证A50': '560050',
    '红利低波': '515080',
    '混债基金': '000171'
}

# 产品代码到信息的映射
PRODUCT_INFO = {
    '560050': {'name': 'A50ETF', 'type': 'ETF', 'category': '中证A50'},
    '513100': {'name': '纳指ETF', 'type': 'ETF', 'category': '纳斯达克100'},
    '513500': {'name': '标普500ETF', 'type': 'ETF', 'category': '标普500'},
    '515080': {'name': '红利低波ETF', 'type': 'ETF', 'category': '红利低波'},
    '000171': {'name': '易方达丰润债券', 'type': 'FUND', 'category': '债券基金'},
    'SPY': {'name': 'SPDR S&P 500', 'type': 'US_STOCK', 'category': '美股ETF'},
    'QQQ': {'name': 'Invesco QQQ', 'type': 'US_STOCK', 'category': '美股ETF'}
}


@bp.route('', methods=['GET'])
def get_scenarios():
    """获取回测方案列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = BacktestScenario.query.order_by(BacktestScenario.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'items': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@bp.route('/<int:id>', methods=['GET'])
def get_scenario(id):
    """获取单个回测方案"""
    scenario = BacktestScenario.query.get_or_404(id)
    return jsonify(scenario.to_dict())


@bp.route('', methods=['POST'])
def create_scenario():
    """创建回测方案并执行回测"""
    data = request.get_json()
    
    # 先同步所有需要的价格数据
    allocations = data.get('allocations', [])
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    sync_errors = []
    for alloc in allocations:
        original_code = alloc['product_code']
        
        # 将产品名称转换为代码
        code = PRODUCT_NAME_TO_CODE.get(original_code, original_code)
        
        # 检查产品是否存在，不存在则创建
        product = Product.query.filter_by(code=code).first()
        if not product:
            print(f"Creating product {code}...")
            info = PRODUCT_INFO.get(code, {'name': original_code, 'type': 'ETF', 'category': ''})
            product = Product(
                code=code,
                name=info['name'],
                type=info['type'],
                category=info['category'],
                fee_rate=0.005,  # 默认费率0.5%
                purchase_fee=0.001,
                redemption_fee=0.005
            )
            db.session.add(product)
            db.session.flush()
        
        # 更新allocation中的code为实际代码
        alloc['product_code'] = code
        
        try:
            # 检查是否已有数据
            from app.models import PriceData
            existing_data = PriceData.query.filter(
                PriceData.product_code == code,
                PriceData.date >= start_date,
                PriceData.date <= end_date
            ).count()
            
            # 如果数据不足，尝试同步
            if existing_data < 10:  # 假设至少需要10天的数据
                print(f"Syncing price data for {code}...")
                DataService.sync_product_data(code, start_date, end_date)
                
        except Exception as e:
            print(f"Error syncing data for {code}: {e}")
            sync_errors.append(f"{code}: {str(e)}")
    
    # 创建方案
    scenario = BacktestScenario(
        name=data['name'],
        description=data.get('description'),
        start_date=start_date,
        end_date=end_date,
        initial_amount=data.get('initial_amount', 100000),
        rebalance_strategy=data.get('rebalance_strategy', 'none'),
        rebalance_period=data.get('rebalance_period'),
        rebalance_threshold=data.get('rebalance_threshold'),
        investment_strategy=data.get('investment_strategy', 'none'),
        monthly_amount=data.get('monthly_amount'),
        investment_day=data.get('investment_day', 1),
        benchmark_code=data.get('benchmark_code')
    )
    
    db.session.add(scenario)
    db.session.flush()  # 获取scenario.id
    
    # 添加资产配置
    for alloc in allocations:
        allocation = ScenarioAllocation(
            scenario_id=scenario.id,
            product_code=alloc['product_code'],
            allocation_ratio=alloc['allocation_ratio']
        )
        db.session.add(allocation)
    
    db.session.commit()
    
    # 执行回测
    try:
        engine = BacktestEngine(scenario)
        engine.run()
        return jsonify({
            'scenario': scenario.to_dict(),
            'message': 'Backtest completed successfully',
            'sync_warnings': sync_errors if sync_errors else None
        }), 201
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        if sync_errors:
            error_msg += f" (Data sync errors: {'; '.join(sync_errors)})"
        return jsonify({'error': error_msg}), 500


@bp.route('/<int:id>', methods=['DELETE'])
def delete_scenario(id):
    """删除回测方案"""
    scenario = BacktestScenario.query.get_or_404(id)
    db.session.delete(scenario)
    db.session.commit()
    
    return jsonify({'message': 'Scenario deleted successfully'})


@bp.route('/<int:id>/results', methods=['GET'])
def get_results(id):
    """获取回测结果"""
    scenario = BacktestScenario.query.get_or_404(id)
    
    # 获取所有结果
    results = BacktestResult.query.filter_by(scenario_id=id).order_by(BacktestResult.date.asc()).all()
    
    return jsonify({
        'scenario': scenario.to_dict(),
        'results': [r.to_dict() for r in results]
    })


@bp.route('/<int:id>/metrics', methods=['GET'])
def get_metrics(id):
    """获取回测指标"""
    from app.services.risk_analyzer import RiskAnalyzer
    
    scenario = BacktestScenario.query.get_or_404(id)
    results = BacktestResult.query.filter_by(scenario_id=id).order_by(BacktestResult.date.asc()).all()
    
    if not results:
        return jsonify({'error': 'No results found for this scenario'}), 404
    
    analyzer = RiskAnalyzer(results)
    metrics = analyzer.calculate_all_metrics()
    
    return jsonify({
        'scenario_id': id,
        'metrics': metrics
    })


@bp.route('/<int:id>/holdings', methods=['GET'])
def get_holdings(id):
    """获取持仓记录"""
    date_str = request.args.get('date')
    
    query = Holding.query.filter_by(scenario_id=id)
    
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        query = query.filter_by(date=date)
    else:
        # 获取最新持仓
        latest_date = db.session.query(db.func.max(Holding.date)).filter_by(scenario_id=id).scalar()
        if latest_date:
            query = query.filter_by(date=latest_date)
    
    holdings = query.all()
    
    return jsonify([h.to_dict() for h in holdings])
