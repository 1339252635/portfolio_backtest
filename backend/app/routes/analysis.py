from flask import Blueprint, request, jsonify
from app import db
from app.models import BacktestScenario, BacktestResult
from app.services.risk_analyzer import RiskAnalyzer
from app.services.backtest_engine import BacktestEngine
import numpy as np

bp = Blueprint('analysis', __name__)


@bp.route('/compare', methods=['POST'])
def compare_scenarios():
    """对比多个回测方案"""
    data = request.get_json()
    scenario_ids = data.get('scenario_ids', [])
    
    if len(scenario_ids) < 2:
        return jsonify({'error': 'At least 2 scenarios required for comparison'}), 400
    
    comparison = []
    for sid in scenario_ids:
        scenario = BacktestScenario.query.get(sid)
        if not scenario:
            continue
        
        results = BacktestResult.query.filter_by(scenario_id=sid).order_by(BacktestResult.date.asc()).all()
        if not results:
            continue
        
        analyzer = RiskAnalyzer(results)
        metrics = analyzer.calculate_all_metrics()
        
        comparison.append({
            'scenario_id': sid,
            'scenario_name': scenario.name,
            'metrics': metrics,
            'final_value': results[-1].total_value if results else 0
        })
    
    return jsonify({
        'comparison': comparison
    })


@bp.route('/monte-carlo', methods=['POST'])
def monte_carlo_simulation():
    """蒙特卡洛模拟"""
    data = request.get_json()
    scenario_id = data.get('scenario_id')
    n_simulations = data.get('n_simulations', 1000)
    n_years = data.get('n_years', 5)
    
    scenario = BacktestScenario.query.get_or_404(scenario_id)
    results = BacktestResult.query.filter_by(scenario_id=scenario_id).order_by(BacktestResult.date.asc()).all()
    
    if not results:
        return jsonify({'error': 'No results found'}), 404
    
    # 获取日收益率序列
    returns = np.array([r.daily_return for r in results if r.daily_return is not None])
    
    if len(returns) == 0:
        return jsonify({'error': 'No return data available'}), 400
    
    # 蒙特卡洛模拟
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    n_days = n_years * 252  # 假设每年252个交易日
    initial_value = float(scenario.initial_amount)
    
    simulations = []
    for _ in range(n_simulations):
        values = [initial_value]
        for _ in range(n_days):
            daily_return = np.random.normal(mean_return, std_return)
            values.append(values[-1] * (1 + daily_return))
        simulations.append(values)
    
    simulations = np.array(simulations)
    
    # 计算统计量
    final_values = simulations[:, -1]
    
    return jsonify({
        'scenario_id': scenario_id,
        'n_simulations': n_simulations,
        'n_years': n_years,
        'statistics': {
            'mean_final_value': float(np.mean(final_values)),
            'median_final_value': float(np.median(final_values)),
            'std_final_value': float(np.std(final_values)),
            'min_final_value': float(np.min(final_values)),
            'max_final_value': float(np.max(final_values)),
            'percentile_5': float(np.percentile(final_values, 5)),
            'percentile_25': float(np.percentile(final_values, 25)),
            'percentile_75': float(np.percentile(final_values, 75)),
            'percentile_95': float(np.percentile(final_values, 95))
        },
        'sample_paths': [simulations[i].tolist() for i in range(min(10, n_simulations))]
    })


@bp.route('/correlation', methods=['POST'])
def correlation_analysis():
    """相关性分析"""
    data = request.get_json()
    product_codes = data.get('product_codes', [])
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if len(product_codes) < 2:
        return jsonify({'error': 'At least 2 products required'}), 400
    
    from app.models import PriceData
    from datetime import datetime
    
    # 获取各产品的收益率数据
    returns_data = {}
    for code in product_codes:
        query = PriceData.query.filter_by(product_code=code)
        
        if start_date:
            query = query.filter(PriceData.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(PriceData.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        prices = query.order_by(PriceData.date.asc()).all()
        
        if len(prices) < 2:
            continue
        
        # 计算日收益率
        prices_list = [p.close_price or p.nav for p in prices]
        returns = []
        for i in range(1, len(prices_list)):
            if prices_list[i-1] and prices_list[i]:
                ret = (float(prices_list[i]) - float(prices_list[i-1])) / float(prices_list[i-1])
                returns.append(ret)
        
        returns_data[code] = returns
    
    # 计算相关系数矩阵
    import pandas as pd
    
    # 确保所有序列长度一致
    min_len = min(len(v) for v in returns_data.values())
    df_data = {k: v[:min_len] for k, v in returns_data.items()}
    
    df = pd.DataFrame(df_data)
    corr_matrix = df.corr()
    
    return jsonify({
        'correlation_matrix': corr_matrix.to_dict(),
        'products': product_codes
    })
