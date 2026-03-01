import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import time
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'realtime_service.log')

# 创建logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 清除已有的处理器
if logger.handlers:
    logger.handlers.clear()

# 文件处理器
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# 添加处理器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info(f"Logging configured. Log file: {log_file}")


class DataSourceManager:
    """数据源管理器 - 支持多数据源自动切换"""
    
    def __init__(self):
        self.session = self._create_session()
        self.primary_source = 'akshare'
        self.fallback_sources = ['sina', 'tencent']
        self.source_status = {
            'akshare': {'available': True, 'fail_count': 0, 'last_fail': None},
            'sina': {'available': True, 'fail_count': 0, 'last_fail': None},
            'tencent': {'available': True, 'fail_count': 0, 'last_fail': None}
        }
    
    def _create_session(self):
        """创建带重试机制的会话"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=5,
            pool_maxsize=5,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.timeout = (3, 15)
        
        return session
    
    def _code_to_sina_format(self, code: str) -> str:
        """转换代码为新浪格式"""
        # ETF: 5开头 -> sh, 1开头 -> sz
        if code.startswith('5'):
            return f"sh{code}"
        elif code.startswith('1'):
            return f"sz{code}"
        # 指数
        elif code.startswith('000') or code.startswith('999'):
            return f"sh{code}"
        elif code.startswith('399'):
            return f"sz{code}"
        return f"sh{code}"
    
    def _code_to_tencent_format(self, code: str) -> str:
        """转换代码为腾讯格式"""
        return self._code_to_sina_format(code)
    
    def get_etf_data_sina(self, code: str) -> Optional[Dict]:
        """从新浪财经获取ETF数据"""
        try:
            sina_code = self._code_to_sina_format(code)
            url = f"https://hq.sinajs.cn/list={sina_code}"
            
            headers = {
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            # 解析新浪返回的数据
            # 格式: var hq_str_sh513100="纳指ETF,1.816,1.832,1.819,...";
            text = response.text
            if f'var hq_str_{sina_code}=""' in text or f'var hq_str_{sina_code}="0' in text:
                return None
            
            # 提取数据部分
            start = text.find('"') + 1
            end = text.rfind('"')
            if start <= 0 or end <= start:
                return None
            
            data_str = text[start:end]
            fields = data_str.split(',')
            
            if len(fields) < 33:
                return None
            
            # 新浪数据字段说明：
            # 0: 名称, 1: 今开, 2: 昨收, 3: 最新价, 4: 最高, 5: 最低
            # 6: 买一价, 7: 卖一价, 8: 成交量(股), 9: 成交额(元)
            # 10-19: 买一到买五价格和数量, 20-29: 卖一到卖五价格和数量
            # 30: 日期, 31: 时间
            
            return {
                'code': code,
                'name': fields[0],
                'price': float(fields[3]) if fields[3] else 0,
                'open': float(fields[1]) if fields[1] else 0,
                'pre_close': float(fields[2]) if fields[2] else 0,
                'high': float(fields[4]) if fields[4] else 0,
                'low': float(fields[5]) if fields[5] else 0,
                'volume': int(float(fields[8]) / 100) if fields[8] else 0,  # 转换为手
                'amount': float(fields[9]) if fields[9] else 0,
                'change': round((float(fields[3]) - float(fields[2])) / float(fields[2]) * 100, 2) if fields[2] and float(fields[2]) > 0 else 0,
                'change_amount': round(float(fields[3]) - float(fields[2]), 3) if fields[2] else 0,
                'timestamp': datetime.now().isoformat(),
                'type': 'ETF',
                'source': 'sina'
            }
        except Exception as e:
            logger.error(f"[Sina] Error getting ETF {code}: {e}")
            return None
    
    def get_etf_data_tencent(self, code: str) -> Optional[Dict]:
        """从腾讯财经获取ETF数据"""
        try:
            tencent_code = self._code_to_tencent_format(code)
            url = f"https://qt.gtimg.cn/q={tencent_code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            # 解析腾讯返回的数据
            # 格式: v_sh513100="1~纳指ETF~513100~1.819~1.832~...";
            text = response.text
            start = text.find('"') + 1
            end = text.rfind('"')
            if start <= 0 or end <= start:
                return None
            
            data_str = text[start:end]
            fields = data_str.split('~')
            
            if len(fields) < 45:
                return None
            
            # 腾讯数据字段说明：
            # 1: 名称, 2: 代码, 3: 最新价, 4: 昨收, 5: 今开
            # 6: 成交量(手), 33: 最高价, 34: 最低价, 35: 涨跌幅
            
            return {
                'code': code,
                'name': fields[1],
                'price': float(fields[3]) if fields[3] else 0,
                'open': float(fields[5]) if fields[5] else 0,
                'pre_close': float(fields[4]) if fields[4] else 0,
                'high': float(fields[33]) if len(fields) > 33 and fields[33] else 0,
                'low': float(fields[34]) if len(fields) > 34 and fields[34] else 0,
                'volume': int(fields[6]) if fields[6] else 0,
                'amount': 0,  # 腾讯接口需要额外计算
                'change': float(fields[35]) if len(fields) > 35 and fields[35] else 0,
                'change_amount': round(float(fields[3]) - float(fields[4]), 3) if fields[3] and fields[4] else 0,
                'timestamp': datetime.now().isoformat(),
                'type': 'ETF',
                'source': 'tencent'
            }
        except Exception as e:
            logger.error(f"[Tencent] Error getting ETF {code}: {e}")
            return None
    
    def get_market_overview_sina(self) -> Dict:
        """从新浪财经获取市场概览"""
        try:
            indices = {
                '000001': '上证指数',
                '399001': '深证成指',
                '000300': '沪深300',
                '000016': '上证50',
                '399006': '创业板指',
                '000688': '科创50'
            }
            
            codes = [f"sh{k}" if k.startswith('0') else f"sz{k}" for k in indices.keys()]
            url = f"https://hq.sinajs.cn/list={','.join(codes)}"
            
            headers = {
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {}
            
            result = {}
            for code, name in indices.items():
                try:
                    sina_code = f"sh{code}" if code.startswith('0') else f"sz{code}"
                    pattern = f'var hq_str_{sina_code}="'
                    start = response.text.find(pattern)
                    if start == -1:
                        continue
                    
                    start += len(pattern)
                    end = response.text.find('"', start)
                    data_str = response.text[start:end]
                    fields = data_str.split(',')
                    
                    if len(fields) >= 3:
                        result[code] = {
                            'name': name,
                            'price': float(fields[3]) if fields[3] else 0,
                            'change': round((float(fields[3]) - float(fields[2])) / float(fields[2]) * 100, 2) if fields[2] and float(fields[2]) > 0 else 0,
                            'change_amount': round(float(fields[3]) - float(fields[2]), 2) if fields[2] else 0,
                            'volume': int(float(fields[8]) / 100) if len(fields) > 8 and fields[8] else 0,
                            'amount': float(fields[9]) if len(fields) > 9 and fields[9] else 0
                        }
                except Exception as e:
                    logger.error(f"[Sina] Error parsing index {code}: {e}")
            
            return result
        except Exception as e:
            logger.error(f"[Sina] Error getting market overview: {e}")
            return {}


class RealtimeService:
    """实时行情数据服务 - 支持多数据源"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 30  # 缓存30秒
        self.subscribers = {}
        self.running = False
        self.update_thread = None
        self.request_count = 0
        self.error_count = 0
        self.last_request_time = 0
        self.min_request_interval = 0.3  # 最小请求间隔0.3秒
        self.data_source = DataSourceManager()
        logger.info("RealtimeService initialized with multi-data-source support")
    
    def _rate_limit(self):
        """速率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
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
    
    def get_realtime_quote(self, code: str) -> Optional[Dict]:
        """获取实时行情数据 - 自动切换数据源"""
        logger.info(f"[get_realtime_quote] Request for code: {code}")
        
        # 检查缓存
        if code in self.cache:
            cache_age = (datetime.now() - self.cache_time.get(code, datetime.min)).total_seconds()
            if cache_age < self.cache_duration:
                logger.info(f"[get_realtime_quote] Cache hit for {code}")
                return self.cache[code]
        
        self._rate_limit()
        start_time = time.time()
        
        try:
            data = None
            
            # 判断代码类型并选择数据源
            if code.startswith('5') or code.startswith('1'):
                logger.info(f"[get_realtime_quote] {code} identified as ETF")
                
                # 尝试AKShare
                try:
                    data = self._get_etf_from_akshare(code)
                    if data:
                        data['source'] = 'akshare'
                except Exception as e:
                    logger.warning(f"[get_realtime_quote] AKShare failed for {code}: {e}")
                
                # AKShare失败，尝试新浪财经
                if not data:
                    logger.info(f"[get_realtime_quote] Trying Sina for {code}")
                    data = self.data_source.get_etf_data_sina(code)
                
                # 新浪失败，尝试腾讯
                if not data:
                    logger.info(f"[get_realtime_quote] Trying Tencent for {code}")
                    data = self.data_source.get_etf_data_tencent(code)
                    
            elif code.startswith('0') or code.startswith('2'):
                logger.info(f"[get_realtime_quote] {code} identified as Fund")
                data = self._get_fund_realtime(code)
            else:
                logger.info(f"[get_realtime_quote] {code} identified as US Stock")
                data = self._get_us_stock_realtime(code)
            
            duration = time.time() - start_time
            
            if data:
                self.cache[code] = data
                self.cache_time[code] = datetime.now()
                source = data.get('source', 'unknown')
                self._log_request(code, source, 'SUCCESS', duration)
                logger.info(f"[get_realtime_quote] Success from {source} for {code}: price={data.get('price', 'N/A')}")
                return data
            else:
                self._log_request(code, 'ALL', 'NO_DATA', duration)
                logger.warning(f"[get_realtime_quote] No data from any source for {code}")
                return None
                
        except Exception as e:
            duration = time.time() - start_time
            self._log_error(code, 'ALL', str(e))
            logger.error(f"[get_realtime_quote] Error getting data for {code}: {e}")
            return None
    
    def _get_etf_from_akshare(self, code: str) -> Optional[Dict]:
        """从AKShare获取ETF数据"""
        try:
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
                'type': 'ETF',
                'source': 'akshare'
            }
        except Exception as e:
            logger.error(f"[AKShare] Error getting ETF {code}: {e}")
            return None
    
    def _get_fund_realtime(self, code: str) -> Optional[Dict]:
        """获取基金实时行情"""
        try:
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
                'type': 'FUND',
                'source': 'akshare'
            }
        except Exception as e:
            logger.error(f"[AKShare] Error getting Fund {code}: {e}")
            return None
    
    def _get_us_stock_realtime(self, code: str) -> Optional[Dict]:
        """获取美股实时行情"""
        try:
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
                'type': 'US_STOCK',
                'source': 'yfinance'
            }
        except Exception as e:
            logger.error(f"[YFinance] Error getting US stock {code}: {e}")
            return None
    
    def get_batch_realtime(self, codes: List[str]) -> Dict[str, Dict]:
        """批量获取实时行情"""
        result = {}
        
        for code in codes:
            try:
                time.sleep(0.2)  # 请求间隔
                data = self.get_realtime_quote(code)
                if data:
                    result[code] = data
            except Exception as e:
                logger.error(f"[get_batch_realtime] Error fetching {code}: {e}")
        
        logger.info(f"[get_batch_realtime] Completed: {len(result)}/{len(codes)} codes")
        return result
    
    def get_market_overview(self) -> Dict:
        """获取市场概览 - 支持多数据源"""
        logger.info("[get_market_overview] Fetching market overview")
        
        # 尝试AKShare
        try:
            result = self._get_market_overview_akshare()
            if result:
                logger.info(f"[get_market_overview] Success from AKShare: {len(result)} indices")
                return result
        except Exception as e:
            logger.warning(f"[get_market_overview] AKShare failed: {e}")
        
        # AKShare失败，使用新浪财经
        logger.info("[get_market_overview] Trying Sina")
        result = self.data_source.get_market_overview_sina()
        if result:
            logger.info(f"[get_market_overview] Success from Sina: {len(result)} indices")
            return result
        
        logger.error("[get_market_overview] All data sources failed")
        return {}
    
    def _get_market_overview_akshare(self) -> Dict:
        """从AKShare获取市场概览"""
        indices = {
            '000001': '上证指数',
            '399001': '深证成指',
            '000300': '沪深300',
            '000016': '上证50',
            '399006': '创业板指',
            '000688': '科创50'
        }
        
        result = {}
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
                logger.error(f"[AKShare] Error getting index {code}: {e}")
        
        return result


# 全局实时服务实例
realtime_service = RealtimeService()
