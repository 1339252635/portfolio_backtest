from flask import Blueprint, jsonify, request
from app.services.realtime_service import realtime_service
from app.models import Product

realtime_bp = Blueprint('realtime', __name__, url_prefix='/api/realtime')


@realtime_bp.route('/quote/<code>', methods=['GET'])
def get_realtime_quote(code):
    """获取单个产品实时行情"""
    try:
        data = realtime_service.get_realtime_quote(code)
        if data:
            return jsonify({
                'code': 200,
                'data': data
            })
        else:
            return jsonify({
                'code': 404,
                'error': f'No realtime data found for {code}'
            }), 404
    except Exception as e:
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/quotes', methods=['POST'])
def get_batch_quotes():
    """批量获取实时行情"""
    try:
        codes = request.json.get('codes', [])
        if not codes:
            return jsonify({
                'code': 400,
                'error': 'No codes provided'
            }), 400
        
        data = realtime_service.get_batch_realtime(codes)
        return jsonify({
            'code': 200,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/products', methods=['GET'])
def get_all_products_realtime():
    """获取所有产品的实时行情"""
    try:
        # 获取所有产品代码
        products = Product.query.all()
        codes = [p.code for p in products]
        
        if not codes:
            return jsonify({
                'code': 200,
                'data': {}
            })
        
        data = realtime_service.get_batch_realtime(codes)
        return jsonify({
            'code': 200,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/market-overview', methods=['GET'])
def get_market_overview():
    """获取市场概览"""
    try:
        data = realtime_service.get_market_overview()
        return jsonify({
            'code': 200,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/subscribe', methods=['POST'])
def subscribe_realtime():
    """订阅实时数据更新（WebSocket准备）"""
    try:
        codes = request.json.get('codes', [])
        # 这里可以添加WebSocket订阅逻辑
        return jsonify({
            'code': 200,
            'message': f'Subscribed to {len(codes)} products'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500
