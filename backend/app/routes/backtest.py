from flask import Blueprint, request, jsonify
from app import db
from app.models import BacktestScenario, ScenarioAllocation, BacktestResult, Holding
from app.services.backtest_engine import BacktestEngine
from datetime import datetime

bp = Blueprint('backtest', __name__)


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
    
    # 创建方案
    scenario = BacktestScenario(
        name=data['name'],
        description=data.get('description'),
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
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
    for alloc in data.get('allocations', []):
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
            'message': 'Backtest completed successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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
