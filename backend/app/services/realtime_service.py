import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealtimeService:
    """实时行情数据服务"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 30  # 缓存30秒
        self.subscribers = {}  # WebSocket订阅者
        self.running = False
        self.update_thread = None
        self.request_count = 0  # 请求计数
        self.error_count = 0    # 错误计数
        logger.info("RealtimeService initialized")
    
    def _log_request(self, code: str, source: str, status: str, duration: float = None):
        """记录请求日志"""
        self.request_count += 1
        log_msg = f"[Request #{self.request_count}] Code: {code}, Source: {source}, Status: {status}"
        if duration:
            log_msg += f", Duration: {duration:.2f}s"
        logger.info(log_msg)
    
    def _log_error(self, code: str, source: str, error: str):
        """记录错误日志"""
        self.error_count += 1
        logger.error(f"[Error #{self.error_count}] Code: {code}, Source: {source}, Error: {error}")
    
    def get_stats(self) -> Dict:
        """获取服务统计信息"""
        return {
            'request_count': self.request_count,
            'error_count': self.error_count,
            'cache_size': len(self.cache),
            'subscriber_count': len(self.subscribers),
            'is_running': self.running
        }
    
    def start(self):
        """启动实时数据更新服务"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
    
    def stop(self):
        """停止实时数据更新服务"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
    
    def _update_loop(self):
        """后台更新循环"""
        while self.running:
            try:
                # 更新所有订阅的代码
                for code in list(self.subscribers.keys()):
                    data = self.get_realtime_quote(code)
                    if data:
                        self._notify_subscribers(code, data)
                time.sleep(5)  # 每5秒更新一次
            except Exception as e:
                print(f"Error in update loop: {e}")
                time.sleep(5)
    
    def _notify_subscribers(self, code: str, data: dict):
        """通知订阅者数据更新"""
        if code in self.subscribers:
            for callback in self.subscribers[code]:
                try:
                    callback(code, data)
                except Exception as e:
                    print(f"Error notifying subscriber: {e}")
    
    def subscribe(self, code: str, callback):
        """订阅实时数据"""
        if code not in self.subscribers:
            self.subscribers[code] = []
        self.subscribers[code].append(callback)
    
    def unsubscribe(self, code: str, callback):
        """取消订阅"""
        if code in self.subscribers and callback in self.subscribers[code]:
            self.subscribers[code].remove(callback)
    
    def get_realtime_quote(self, code: str) -> Optional[Dict]:
        """获取实时行情数据"""
        logger.info(f"[get_realtime_quote] Request for code: {code}")
        
        # 检查缓存
        if code in self.cache:
            cache_age = (datetime.now() - self.cache_time.get(code, datetime.min)).total_seconds()
            logger.info(f"[get_realtime_quote] Cache check for {code}: age={cache_age:.1f}s, duration={self.cache_duration}s")
            if cache_age < self.cache_duration:
                logger.info(f"[get_realtime_quote] Returning cached data for {code}")
                return self.cache[code]
            else:
                logger.info(f"[get_realtime_quote] Cache expired for {code}")
        
        start_time = time.time()
        try:
            # 判断代码类型
            if code.startswith('5') or code.startswith('1'):
                logger.info(f"[get_realtime_quote] {code} identified as ETF")
                data = self._get_etf_realtime(code)
            elif code.startswith('0') or code.startswith('2'):
                logger.info(f"[get_realtime_quote] {code} identified as Fund")
                data = self._get_fund_realtime(code)
            else:
                logger.info(f"[get_realtime_quote] {code} identified as US Stock")
                data = self._get_us_stock_realtime(code)
            
            duration = time.time() - start_time
            
            if data:
                # 更新缓存
                self.cache[code] = data
                self.cache_time[code] = datetime.now()
                self._log_request(code, data.get('type', 'UNKNOWN'), 'SUCCESS', duration)
                logger.info(f"[get_realtime_quote] Successfully fetched data for {code}: price={data.get('price', 'N/A')}")
                return data
            else:
                self._log_request(code, 'UNKNOWN', 'NO_DATA', duration)
                logger.warning(f"[get_realtime_quote] No data found for {code}")
                return None
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_error(code, 'UNKNOWN', str(e))
            logger.error(f"[get_realtime_quote] Error getting data for {code}: {e}", exc_info=True)
            return None
    
    def _get_etf_realtime(self, code: str) -> Optional[Dict]:
        """获取ETF实时行情"""
        logger.info(f"[_get_etf_realtime] Fetching ETF data for {code}")
        try:
            # 使用AKShare获取ETF实时行情 - 使用stock_zh_a_spot_em获取A股实时行情
            logger.info(f"[_get_etf_realtime] Calling ak.stock_zh_a_spot_em()")
            df = ak.stock_zh_a_spot_em()
            logger.info(f"[_get_etf_realtime] Got {len(df)} rows from stock_zh_a_spot_em")
            
            etf_data = df[df['代码'] == code]
            logger.info(f"[_get_etf_realtime] Filtered data for {code}: {len(etf_data)} rows")
            
            if etf_data.empty:
                logger.warning(f"[_get_etf_realtime] No data found for ETF {code}")
                return None
            
            row = etf_data.iloc[0]
            result = {
                'code': code,
                'name': row.get('名称', ''),
                'price': float(row.get('最新价', 0)),
                'change': float(row.get('涨跌幅', 0)),
                'change_amount': float(row.get('涨跌额', 0)),
                'open': float(row.get('今开', 0)),
                'high': float(row.get('最高', 0)),
                'low': float(row.get('最低', 0)),
                'volume': int(row.get('成交量', 0)),
                'amount': float(row.get('成交额', 0)),
                'pre_close': float(row.get('昨收', 0)),
                'timestamp': datetime.now().isoformat(),
                'type': 'ETF'
            }
            logger.info(f"[_get_etf_realtime] Successfully parsed ETF data for {code}: {result['name']} @ {result['price']}")
            return result
        except Exception as e:
            self._log_error(code, 'ETF', str(e))
            logger.error(f"[_get_etf_realtime] Error getting ETF {code}: {e}", exc_info=True)
            return None
    
    def _get_fund_realtime(self, code: str) -> Optional[Dict]:
        """获取基金实时行情"""
        logger.info(f"[_get_fund_realtime] Fetching Fund data for {code}")
        try:
            # 使用AKShare获取基金实时净值
            logger.info(f"[_get_fund_realtime] Calling ak.fund_open_fund_daily_em()")
            df = ak.fund_open_fund_daily_em()
            logger.info(f"[_get_fund_realtime] Got {len(df)} rows from fund_open_fund_daily_em")
            
            fund_data = df[df['基金代码'] == code]
            logger.info(f"[_get_fund_realtime] Filtered data for {code}: {len(fund_data)} rows")
            
            if fund_data.empty:
                logger.warning(f"[_get_fund_realtime] No data found for Fund {code}")
                return None
            
            row = fund_data.iloc[0]
            result = {
                'code': code,
                'name': row.get('基金简称', ''),
                'nav': float(row.get('单位净值', 0)),
                'acc_nav': float(row.get('累计净值', 0)),
                'daily_return': float(row.get('日增长率', 0).replace('%', '')) if pd.notna(row.get('日增长率')) else 0,
                'date': row.get('净值日期', ''),
                'timestamp': datetime.now().isoformat(),
                'type': 'FUND'
            }
            logger.info(f"[_get_fund_realtime] Successfully parsed Fund data for {code}: {result['name']} @ {result['nav']}")
            return result
        except Exception as e:
            self._log_error(code, 'FUND', str(e))
            logger.error(f"[_get_fund_realtime] Error getting Fund {code}: {e}", exc_info=True)
            return None
    
    def _get_us_stock_realtime(self, code: str) -> Optional[Dict]:
        """获取美股实时行情"""
        try:
            # 使用yfinance获取美股数据
            ticker = yf.Ticker(code)
            info = ticker.info
            
            if not info:
                return None
            
            return {
                'code': code,
                'name': info.get('shortName', ''),
                'price': info.get('regularMarketPrice', 0),
                'change': info.get('regularMarketChangePercent', 0),
                'change_amount': info.get('regularMarketChange', 0),
                'open': info.get('regularMarketOpen', 0),
                'high': info.get('regularMarketDayHigh', 0),
                'low': info.get('regularMarketDayLow', 0),
                'volume': info.get('regularMarketVolume', 0),
                'pre_close': info.get('regularMarketPreviousClose', 0),
                'timestamp': datetime.now().isoformat(),
                'type': 'US_STOCK'
            }
        except Exception as e:
            print(f"Error getting US stock realtime: {e}")
            return None
    
    def get_batch_realtime(self, codes: List[str]) -> Dict[str, Dict]:
        """批量获取实时行情 - 使用并发和超时控制"""
        from concurrent.futures import ThreadPoolExecutor, TimeoutError
        
        result = {}
        
        def fetch_single(code):
            try:
                logger.info(f"[get_batch_realtime] Fetching single code: {code}")
                return code, self.get_realtime_quote(code)
            except Exception as e:
                logger.error(f"[get_batch_realtime] Error fetching {code}: {e}")
                return code, None
        
        # 使用线程池并发获取，设置超时
        logger.info(f"[get_batch_realtime] Starting batch fetch for {len(codes)} codes with {min(5, len(codes))} workers")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=min(5, len(codes))) as executor:
            futures = {executor.submit(fetch_single, code): code for code in codes}
            
            for future in futures:
                try:
                    code, data = future.result(timeout=10)  # 单个请求10秒超时
                    if data:
                        result[code] = data
                        logger.info(f"[get_batch_realtime] Successfully fetched {code}")
                    else:
                        logger.warning(f"[get_batch_realtime] No data for {code}")
                except TimeoutError:
                    logger.error(f"[get_batch_realtime] Timeout fetching {futures[future]}")
                except Exception as e:
                    logger.error(f"[get_batch_realtime] Error in batch fetch for {futures[future]}: {e}")
        
        duration = time.time() - start_time
        logger.info(f"[get_batch_realtime] Batch fetch completed: {len(result)}/{len(codes)} codes in {duration:.2f}s")
        return result
    
    def get_market_overview(self) -> Dict:
        """获取市场概览"""
        logger.info("[get_market_overview] Fetching market overview")
        try:
            # 获取主要指数 - 使用stock_zh_index_spot_em获取指数行情
            indices = {
                '000001': '上证指数',
                '399001': '深证成指',
                '000300': '沪深300',
                '000016': '上证50',
                '399006': '创业板指',
                '000688': '科创50'
            }
            
            result = {}
            try:
                logger.info("[get_market_overview] Calling ak.stock_zh_index_spot_em()")
                start_time = time.time()
                df = ak.stock_zh_index_spot_em()
                duration = time.time() - start_time
                logger.info(f"[get_market_overview] Got {len(df)} rows from stock_zh_index_spot_em in {duration:.2f}s")
                
                for code, name in indices.items():
                    try:
                        index_data = df[df['代码'] == code]
                        if not index_data.empty:
                            row = index_data.iloc[0]
                            result[code] = {
                                'name': name,
                                'price': float(row.get('最新价', 0)),
                                'change': float(row.get('涨跌幅', 0)),
                                'change_amount': float(row.get('涨跌额', 0)),
                                'volume': int(row.get('成交量', 0)),
                                'amount': float(row.get('成交额', 0))
                            }
                            logger.info(f"[get_market_overview] Got index {code} ({name}): {result[code]['price']}")
                        else:
                            logger.warning(f"[get_market_overview] No data for index {code} ({name})")
                    except Exception as e:
                        logger.error(f"[get_market_overview] Error getting index {code}: {e}")
            except Exception as e:
                logger.error(f"[get_market_overview] Error getting market overview data: {e}", exc_info=True)
            
            logger.info(f"[get_market_overview] Returning {len(result)} indices")
            return result
        except Exception as e:
            logger.error(f"[get_market_overview] Error getting market overview: {e}", exc_info=True)
            return {}


# 全局实时服务实例
realtime_service = RealtimeService()
