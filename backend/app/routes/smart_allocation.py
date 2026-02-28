"""
智能配置建议 API 路由
"""

from flask import Blueprint, request, jsonify
from app.services.smart_allocation import (
    SmartAllocationService, 
    RiskProfile, 
    RiskLevel,
    InvestmentGoal,
    get_smart_allocation
)

bp = Blueprint('smart_allocation', __name__)


@bp.route('/assess', methods=['POST'])
def assess_risk():
    """
    评估风险承受能力并获取配置建议
    
    Request Body:
    {
        "age": 30,
        "investment_experience": 3,
        "annual_income": 200000,
        "liquid_assets": 300000,
        "investment_horizon": 10,
        "loss_tolerance": 0.20,
        "monthly_investment": 5000
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "risk_level": "balanced",
            "risk_level_name": "平衡型",
            "investment_goal": "balanced_growth",
            "investment_goal_name": "平衡增长",
            "allocations": {
                "混债基金": 25.0,
                "红利低波": 20.0,
                "中证A50": 20.0,
                "标普ETF": 20.0,
                "纳指ETF": 15.0
            },
            "expected_return": 0.10,
            "expected_volatility": 0.18,
            "max_drawdown": -0.25,
            "sharpe_ratio": 0.70,
            "description": "平衡型配置，风险收益均衡，适合稳健型投资者",
            "reasoning": [
                "您处于职业发展的黄金期...",
                "您拥有3年投资经验...",
                ...
            ]
        }
    }
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = [
            'age', 'investment_experience', 'annual_income', 
            'liquid_assets', 'investment_horizon', 'loss_tolerance', 'monthly_investment'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        # 创建风险画像
        profile = RiskProfile(
            age=data['age'],
            investment_experience=data['investment_experience'],
            annual_income=data['annual_income'],
            liquid_assets=data['liquid_assets'],
            investment_horizon=data['investment_horizon'],
            loss_tolerance=data['loss_tolerance'],
            monthly_investment=data['monthly_investment']
        )
        
        # 获取配置建议
        suggestion = SmartAllocationService.get_allocation_suggestion(profile)
        
        # 风险等级中文映射
        risk_level_names = {
            'conservative': '保守型',
            'cautious': '谨慎型',
            'balanced': '平衡型',
            'aggressive': '进取型',
            'radical': '激进型'
        }
        
        # 投资目标中文映射
        goal_names = {
            'capital_preservation': '资产保值',
            'steady_income': '稳定收益',
            'balanced_growth': '平衡增长',
            'capital_growth': '资本增值',
            'aggressive_growth': '激进增长'
        }
        
        return jsonify({
            'success': True,
            'data': {
                'risk_level': suggestion.risk_level.value,
                'risk_level_name': risk_level_names.get(suggestion.risk_level.value, suggestion.risk_level.value),
                'investment_goal': suggestion.investment_goal.value,
                'investment_goal_name': goal_names.get(suggestion.investment_goal.value, suggestion.investment_goal.value),
                'allocations': suggestion.allocations,
                'expected_return': suggestion.expected_return,
                'expected_volatility': suggestion.expected_volatility,
                'max_drawdown': suggestion.max_drawdown,
                'sharpe_ratio': suggestion.sharpe_ratio,
                'description': suggestion.description,
                'reasoning': suggestion.reasoning
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/templates', methods=['GET'])
def get_templates():
    """
    获取所有风险等级的配置模板
    
    Returns:
    {
        "success": true,
        "data": [
            {
                "risk_level": "conservative",
                "risk_level_name": "保守型",
                "investment_goal": "capital_preservation",
                "investment_goal_name": "资产保值",
                "allocations": {...},
                "expected_return": 0.05,
                "expected_volatility": 0.08,
                "max_drawdown": -0.10,
                "sharpe_ratio": 0.50,
                "description": "..."
            },
            ...
        ]
    }
    """
    try:
        suggestions = SmartAllocationService.get_all_suggestions()
        
        # 风险等级中文映射
        risk_level_names = {
            'conservative': '保守型',
            'cautious': '谨慎型',
            'balanced': '平衡型',
            'aggressive': '进取型',
            'radical': '激进型'
        }
        
        # 投资目标中文映射
        goal_names = {
            'capital_preservation': '资产保值',
            'steady_income': '稳定收益',
            'balanced_growth': '平衡增长',
            'capital_growth': '资本增值',
            'aggressive_growth': '激进增长'
        }
        
        data = []
        for risk_level, suggestion in suggestions.items():
            data.append({
                'risk_level': suggestion.risk_level.value,
                'risk_level_name': risk_level_names.get(suggestion.risk_level.value, suggestion.risk_level.value),
                'investment_goal': suggestion.investment_goal.value,
                'investment_goal_name': goal_names.get(suggestion.investment_goal.value, suggestion.investment_goal.value),
                'allocations': suggestion.allocations,
                'expected_return': suggestion.expected_return,
                'expected_volatility': suggestion.expected_volatility,
                'max_drawdown': suggestion.max_drawdown,
                'sharpe_ratio': suggestion.sharpe_ratio,
                'description': suggestion.description
            })
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/adjust-by-market', methods=['POST'])
def adjust_by_market():
    """
    根据市场环境调整配置
    
    Request Body:
    {
        "allocations": {
            "混债基金": 25.0,
            "红利低波": 20.0,
            "中证A50": 20.0,
            "标普ETF": 20.0,
            "纳指ETF": 15.0
        },
        "market_condition": "bull"  // bull/bear/sideways
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "original_allocations": {...},
            "adjusted_allocations": {...},
            "market_condition": "bull",
            "adjustment_reason": "牛市环境下增加权益类资产配置"
        }
    }
    """
    try:
        data = request.get_json()
        
        allocations = data.get('allocations')
        market_condition = data.get('market_condition')
        
        if not allocations or not market_condition:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: allocations 或 market_condition'
            }), 400
        
        if market_condition not in ['bull', 'bear', 'sideways']:
            return jsonify({
                'success': False,
                'error': 'market_condition 必须是 bull/bear/sideways 之一'
            }), 400
        
        adjusted = SmartAllocationService.adjust_allocation_by_market(
            allocations, market_condition
        )
        
        condition_names = {
            'bull': '牛市',
            'bear': '熊市',
            'sideways': '震荡市'
        }
        
        adjustment_reasons = {
            'bull': '牛市环境下增加权益类资产配置，把握上涨机会',
            'bear': '熊市环境下增加防御性资产配置，降低组合波动',
            'sideways': '震荡市环境下保持均衡配置，等待市场方向明确'
        }
        
        return jsonify({
            'success': True,
            'data': {
                'original_allocations': allocations,
                'adjusted_allocations': adjusted,
                'market_condition': market_condition,
                'market_condition_name': condition_names.get(market_condition),
                'adjustment_reason': adjustment_reasons.get(market_condition)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/risk-questions', methods=['GET'])
def get_risk_questions():
    """
    获取风险评估问卷
    
    Returns:
    {
        "success": true,
        "data": {
            "questions": [
                {
                    "id": "age",
                    "question": "您的年龄是？",
                    "type": "single_choice",
                    "options": [
                        {"value": 25, "label": "30岁以下"},
                        {"value": 35, "label": "30-40岁"},
                        ...
                    ]
                },
                ...
            ]
        }
    }
    """
    questions = [
        {
            'id': 'age',
            'question': '您的年龄是？',
            'type': 'single_choice',
            'options': [
                {'value': 25, 'label': '30岁以下', 'score': 25},
                {'value': 35, 'label': '30-40岁', 'score': 20},
                {'value': 45, 'label': '40-50岁', 'score': 15},
                {'value': 55, 'label': '50-60岁', 'score': 10},
                {'value': 65, 'label': '60岁以上', 'score': 5}
            ]
        },
        {
            'id': 'investment_experience',
            'question': '您的投资经验是？',
            'type': 'single_choice',
            'options': [
                {'value': 0, 'label': '无经验', 'score': 5},
                {'value': 1, 'label': '1-2年', 'score': 10},
                {'value': 3, 'label': '3-5年', 'score': 15},
                {'value': 7, 'label': '5-10年', 'score': 18},
                {'value': 12, 'label': '10年以上', 'score': 20}
            ]
        },
        {
            'id': 'annual_income',
            'question': '您的年收入是？',
            'type': 'single_choice',
            'options': [
                {'value': 50000, 'label': '10万以下', 'score': 3},
                {'value': 100000, 'label': '10-20万', 'score': 7},
                {'value': 200000, 'label': '20-50万', 'score': 12},
                {'value': 500000, 'label': '50-100万', 'score': 15},
                {'value': 1000000, 'label': '100万以上', 'score': 15}
            ]
        },
        {
            'id': 'liquid_assets',
            'question': '您的流动资产（现金、存款、理财产品等）是？',
            'type': 'single_choice',
            'options': [
                {'value': 50000, 'label': '10万以下', 'score': 3},
                {'value': 150000, 'label': '10-30万', 'score': 7},
                {'value': 500000, 'label': '30-100万', 'score': 12},
                {'value': 1500000, 'label': '100-300万', 'score': 15},
                {'value': 3000000, 'label': '300万以上', 'score': 15}
            ]
        },
        {
            'id': 'investment_horizon',
            'question': '您的投资期限是？',
            'type': 'single_choice',
            'options': [
                {'value': 1, 'label': '1年以内', 'score': 2},
                {'value': 3, 'label': '1-3年', 'score': 4},
                {'value': 5, 'label': '3-5年', 'score': 6},
                {'value': 10, 'label': '5-10年', 'score': 8},
                {'value': 20, 'label': '10年以上', 'score': 10}
            ]
        },
        {
            'id': 'loss_tolerance',
            'question': '您能承受的最大投资损失是？',
            'type': 'single_choice',
            'options': [
                {'value': 0.05, 'label': '5%以内', 'score': 0.75},
                {'value': 0.10, 'label': '5-10%', 'score': 1.5},
                {'value': 0.20, 'label': '10-20%', 'score': 3.0},
                {'value': 0.30, 'label': '20-30%', 'score': 4.5},
                {'value': 0.50, 'label': '30%以上', 'score': 7.5}
            ]
        }
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'questions': questions
        }
    })
