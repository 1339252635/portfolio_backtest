import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
import json


class RealtimeService:
    """实时行情数据服务"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 30  # 缓存30秒
        self.subscribers = {}  # WebSocket订阅者
        self.running = False
        self.update_thread = None
    
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
        # 检查缓存
        if code in self.cache:
            cache_age = (datetime.now() - self.cache_time.get(code, datetime.min)).total_seconds()
            if cache_age < self.cache_duration:
                return self.cache[code]
        
        try:
            # 判断代码类型
            if code.startswith('5') or code.startswith('1'):
                # ETF
                data = self._get_etf_realtime(code)
            elif code.startswith('0') or code.startswith('2'):
                # 基金
                data = self._get_fund_realtime(code)
            else:
                # 尝试获取美股数据
                data = self._get_us_stock_realtime(code)
            
            if data:
                # 更新缓存
                self.cache[code] = data
                self.cache_time[code] = datetime.now()
                return data
            else:
                print(f"No data found for {code}")
                return None
            
        except Exception as e:
            print(f"Error getting realtime quote for {code}: {e}")
            return None
    
    def _get_etf_realtime(self, code: str) -> Optional[Dict]:
        """获取ETF实时行情"""
        try:
            # 使用AKShare获取ETF实时行情 - 使用stock_zh_a_spot_em获取A股实时行情
            df = ak.stock_zh_a_spot_em()
            etf_data = df[df['代码'] == code]
            
            if etf_data.empty:
                return None
            
            row = etf_data.iloc[0]
            return {
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
        except Exception as e:
            print(f"Error getting ETF realtime: {e}")
            return None
    
    def _get_fund_realtime(self, code: str) -> Optional[Dict]:
        """获取基金实时行情"""
        try:
            # 使用AKShare获取基金实时净值
            df = ak.fund_open_fund_daily_em()
            fund_data = df[df['基金代码'] == code]
            
            if fund_data.empty:
                return None
            
            row = fund_data.iloc[0]
            return {
                'code': code,
                'name': row.get('基金简称', ''),
                'nav': float(row.get('单位净值', 0)),
                'acc_nav': float(row.get('累计净值', 0)),
                'daily_return': float(row.get('日增长率', 0).replace('%', '')) if pd.notna(row.get('日增长率')) else 0,
                'date': row.get('净值日期', ''),
                'timestamp': datetime.now().isoformat(),
                'type': 'FUND'
            }
        except Exception as e:
            print(f"Error getting fund realtime: {e}")
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
                return code, self.get_realtime_quote(code)
            except Exception as e:
                print(f"Error fetching {code}: {e}")
                return code, None
        
        # 使用线程池并发获取，设置超时
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_single, code): code for code in codes}
            
            for future in futures:
                try:
                    code, data = future.result(timeout=10)  # 单个请求10秒超时
                    if data:
                        result[code] = data
                except TimeoutError:
                    print(f"Timeout fetching {futures[future]}")
                except Exception as e:
                    print(f"Error in batch fetch: {e}")
        
        return result
    
    def get_market_overview(self) -> Dict:
        """获取市场概览"""
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
                df = ak.stock_zh_index_spot_em()
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
                    except Exception as e:
                        print(f"Error getting index {code}: {e}")
            except Exception as e:
                print(f"Error getting market overview data: {e}")
            
            return result
        except Exception as e:
            print(f"Error getting market overview: {e}")
            return {}


# 全局实时服务实例
realtime_service = RealtimeService()
