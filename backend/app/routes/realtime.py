from flask import Blueprint, jsonify, request
import logging
import time
from app.services.realtime_service import realtime_service
from app.models import Product

# 配置路由日志
logger = logging.getLogger(__name__)

realtime_bp = Blueprint('realtime', __name__, url_prefix='/api/realtime')


@realtime_bp.route('/quote/<code>', methods=['GET'])
def get_realtime_quote(code):
    """获取单个产品实时行情"""
    logger.info(f"[API /quote/{code}] Request received")
    start_time = time.time()
    try:
        data = realtime_service.get_realtime_quote(code)
        duration = time.time() - start_time
        if data:
            logger.info(f"[API /quote/{code}] Success in {duration:.2f}s")
            return jsonify({
                'code': 200,
                'data': data
            })
        else:
            logger.warning(f"[API /quote/{code}] No data found in {duration:.2f}s")
            return jsonify({
                'code': 404,
                'error': f'No realtime data found for {code}'
            }), 404
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[API /quote/{code}] Error in {duration:.2f}s: {e}", exc_info=True)
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/quotes', methods=['POST'])
def get_batch_quotes():
    """批量获取实时行情"""
    logger.info("[API /quotes] Request received")
    start_time = time.time()
    try:
        codes = request.json.get('codes', [])
        logger.info(f"[API /quotes] Requesting {len(codes)} codes: {codes}")
        if not codes:
            logger.warning("[API /quotes] No codes provided")
            return jsonify({
                'code': 400,
                'error': 'No codes provided'
            }), 400
        
        data = realtime_service.get_batch_realtime(codes)
        duration = time.time() - start_time
        logger.info(f"[API /quotes] Success: {len(data)}/{len(codes)} codes in {duration:.2f}s")
        return jsonify({
            'code': 200,
            'data': data
        })
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[API /quotes] Error in {duration:.2f}s: {e}", exc_info=True)
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/products', methods=['GET'])
def get_all_products_realtime():
    """获取所有产品的实时行情 - 限制数量避免超时"""
    logger.info("[API /products] Request received")
    start_time = time.time()
    try:
        # 获取所有产品代码，但限制数量
        products = Product.query.limit(50).all()  # 最多50个产品
        codes = [p.code for p in products]
        logger.info(f"[API /products] Found {len(codes)} products in database")
        
        if not codes:
            logger.info("[API /products] No products in database")
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
        
        logger.info(f"[API /products] Cache hit: {len(data)}/{len(codes)} codes")
        
        # 如果缓存数据不足，异步更新
        if len(data) < len(codes) * 0.5:  # 如果缓存数据少于50%
            logger.info(f"[API /products] Cache insufficient, starting background update")
            import threading
            def update_cache():
                realtime_service.get_batch_realtime(codes)
            threading.Thread(target=update_cache, daemon=True).start()
        
        duration = time.time() - start_time
        logger.info(f"[API /products] Response in {duration:.2f}s: {len(data)} cached items")
        return jsonify({
            'code': 200,
            'data': data,
            'message': f'Returning {len(data)} cached items, updating in background' if len(data) < len(codes) else 'All data from cache'
        })
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[API /products] Error in {duration:.2f}s: {e}", exc_info=True)
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/market-overview', methods=['GET'])
def get_market_overview():
    """获取市场概览"""
    logger.info("[API /market-overview] Request received")
    start_time = time.time()
    try:
        data = realtime_service.get_market_overview()
        duration = time.time() - start_time
        if not data:
            logger.warning(f"[API /market-overview] No data available in {duration:.2f}s")
            return jsonify({
                'code': 503,
                'error': '无法获取市场数据，请检查网络连接',
                'data': {}
            }), 503
        logger.info(f"[API /market-overview] Success: {len(data)} indices in {duration:.2f}s")
        return jsonify({
            'code': 200,
            'data': data
        })
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[API /market-overview] Error in {duration:.2f}s: {e}", exc_info=True)
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/subscribe', methods=['POST'])
def subscribe_realtime():
    """订阅实时数据更新（WebSocket准备）"""
    logger.info("[API /subscribe] Request received")
    try:
        codes = request.json.get('codes', [])
        logger.info(f"[API /subscribe] Subscribing to {len(codes)} codes: {codes}")
        # 这里可以添加WebSocket订阅逻辑
        return jsonify({
            'code': 200,
            'message': f'Subscribed to {len(codes)} products'
        })
    except Exception as e:
        logger.error(f"[API /subscribe] Error: {e}", exc_info=True)
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500


@realtime_bp.route('/stats', methods=['GET'])
def get_service_stats():
    """获取服务统计信息"""
    logger.info("[API /stats] Request received")
    try:
        stats = realtime_service.get_stats()
        logger.info(f"[API /stats] Returning stats: {stats}")
        return jsonify({
            'code': 200,
            'data': stats
        })
    except Exception as e:
        logger.error(f"[API /stats] Error: {e}", exc_info=True)
        return jsonify({
            'code': 500,
            'error': str(e)
        }), 500
