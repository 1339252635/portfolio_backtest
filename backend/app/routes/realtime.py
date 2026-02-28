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
    """获取所有产品的实时行情 - 限制数量避免超时"""
    try:
        # 获取所有产品代码，但限制数量
        products = Product.query.limit(50).all()  # 最多50个产品
        codes = [p.code for p in products]
        
        if not codes:
            return jsonify({
                'code': 200,
                'data': {}
            })
        
        # 使用缓存数据，如果没有缓存则返回空
        data = {}
        for code in codes:
            cached = realtime_service.cache.get(code)
            if cached:
                data[code] = cached
        
        # 如果缓存数据不足，异步更新
        if len(data) < len(codes) * 0.5:  # 如果缓存数据少于50%
            import threading
            def update_cache():
                realtime_service.get_batch_realtime(codes)
            threading.Thread(target=update_cache, daemon=True).start()
        
        return jsonify({
            'code': 200,
            'data': data,
            'message': f'Returning {len(data)} cached items, updating in background' if len(data) < len(codes) else 'All data from cache'
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


@realtime_bp.route('/mock-mode', methods=['POST'])
def toggle_mock_mode():
    """切换模拟数据模式"""
    try:
        enabled = request.json.get('enabled', False)
        realtime_service.use_mock_data = enabled
        return jsonify({
            'code': 200,
            'message': f'Mock mode {"enabled" if enabled else "disabled"}',
            'mock_mode': enabled
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/mock-mode', methods=['GET'])
def get_mock_mode():
    """获取模拟数据模式状态"""
    return jsonify({
        'code': 200,
        'mock_mode': realtime_service.use_mock_data
    })
