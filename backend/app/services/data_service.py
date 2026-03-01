import akshare as ak
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from app import db
from app.models import Product, PriceData


class DataService:
    """数据服务类"""
    
    @staticmethod
    def sync_product_data(code, start_date=None, end_date=None):
        """同步产品历史数据"""
        product = Product.query.filter_by(code=code).first()
        if not product:
            raise ValueError(f"Product {code} not found")
        
        # 确定日期范围
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            # 默认获取5年数据
            start_date = end_date - timedelta(days=365*5)
        
        # 根据产品类型选择数据源
        if product.type == 'US_STOCK':
            df = DataService._fetch_us_stock_data(code, start_date, end_date)
        elif product.type == 'ETF':
            df = DataService._fetch_etf_data(code, start_date, end_date)
        else:
            df = DataService._fetch_fund_data(code, start_date, end_date)
        
        if df is None or df.empty:
            raise ValueError(f"No data available for {code}")
        
        # 保存到数据库
        records_created = 0
        for _, row in df.iterrows():
            # 检查是否已存在
            existing = PriceData.query.filter_by(
                product_code=code,
                date=row['date']
            ).first()
            
            if existing:
                # 更新现有记录
                existing.nav = row.get('nav')
                existing.close_price = row.get('close')
                existing.open_price = row.get('open')
                existing.high_price = row.get('high')
                existing.low_price = row.get('low')
                existing.volume = row.get('volume')
            else:
                # 创建新记录
                price_data = PriceData(
                    product_code=code,
                    date=row['date'],
                    nav=row.get('nav'),
                    close_price=row.get('close'),
                    open_price=row.get('open'),
                    high_price=row.get('high'),
                    low_price=row.get('low'),
                    volume=row.get('volume')
                )
                db.session.add(price_data)
                records_created += 1
        
        db.session.commit()
        return records_created
    
    @staticmethod
    def _code_to_sina_format(code):
        """转换代码为新浪格式"""
        if code.startswith('5'):
            return f"sh{code}"
        elif code.startswith('1'):
            return f"sz{code}"
        elif code.startswith('000') or code.startswith('999'):
            return f"sh{code}"
        elif code.startswith('399'):
            return f"sz{code}"
        return f"sh{code}"
    
    @staticmethod
    def _fetch_etf_data(code, start_date, end_date):
        """获取ETF数据 - 支持多数据源"""
        # 判断是否为美股代码
        if code in ['SPY', 'QQQ'] or (len(code) <= 4 and code.isalpha()):
            return DataService._fetch_us_stock_data(code, start_date, end_date)
        
        # 首先尝试AKShare
        try:
            df = ak.fund_etf_hist_em(symbol=code, period="daily", 
                                     start_date=start_date.strftime("%Y%m%d"),
                                     end_date=end_date.strftime("%Y%m%d"),
                                     adjust="qfq")
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount'
            })
            
            df['date'] = pd.to_datetime(df['date']).dt.date
            df['nav'] = df['close']  # ETF使用收盘价作为净值
            
            return df[['date', 'open', 'close', 'high', 'low', 'volume', 'nav']]
            
        except Exception as e:
            print(f"AKShare failed for {code}: {e}, trying Sina...")
        
        # AKShare失败，尝试新浪财经
        try:
            return DataService._fetch_etf_data_from_sina(code, start_date, end_date)
        except Exception as e:
            print(f"Sina also failed for {code}: {e}")
            return None
    
    @staticmethod
    def _fetch_us_stock_data(code, start_date, end_date):
        """获取美股数据 - 使用Stooq数据源"""
        try:
            print(f"Fetching US stock data for {code} from Stooq...")
            
            # Stooq免费数据源
            url = f"https://stooq.com/q/d/l/?s={code.lower()}.us&i=d"
            df = pd.read_csv(url)
            
            if df.empty:
                raise ValueError(f"No data returned from Stooq for {code}")
            
            # 重命名列
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'Close': 'close',
                'High': 'high',
                'Low': 'low',
                'Volume': 'volume'
            })
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # 过滤日期范围
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            
            # 添加nav列
            df['nav'] = df['close']
            
            print(f"Got {len(df)} records for {code} from Stooq")
            return df[['date', 'open', 'close', 'high', 'low', 'volume', 'nav']]
            
        except Exception as e:
            print(f"Stooq failed for {code}: {e}")
            return None
    
    @staticmethod
    def _fetch_etf_data_from_sina(code, start_date, end_date):
        """从新浪财经获取ETF历史数据 - 使用AKShare的stock_zh_index_daily"""
        sina_code = DataService._code_to_sina_format(code)
        
        # 使用AKShare的stock_zh_index_daily接口（这个接口可以工作）
        df = ak.stock_zh_index_daily(symbol=sina_code)
        
        if df.empty:
            raise ValueError("No data returned from Sina")
        
        # 列名已经是英文，只需要过滤日期范围
        df['date'] = pd.to_datetime(df['date']).dt.date
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        # 添加nav列（ETF使用收盘价）
        df['nav'] = df['close']
        
        return df[['date', 'open', 'close', 'high', 'low', 'volume', 'nav']]
    
    @staticmethod
    def _fetch_etf_data_from_sina_http(code, start_date, end_date):
        """从新浪财经获取ETF历史数据 - HTTP方式（备用）"""
        sina_code = DataService._code_to_sina_format(code)
        
        # 新浪财经历史数据API
        url = f"https://quotes.sina.cn/cn/api/quotes.php?symbol={sina_code}&scale=240&ma=5&datalen=1000"
        
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch data from Sina: {response.status_code}")
        
        # 解析JSONP格式数据
        text = response.text
        # 提取JSON部分
        start = text.find('(') + 1
        end = text.rfind(')')
        if start <= 0 or end <= start:
            raise ValueError("Invalid response format from Sina")
        
        json_str = text[start:end]
        data = pd.read_json(json_str)
        
        if data.empty:
            raise ValueError("No data returned from Sina")
        
        # 重命名列
        df = data.rename(columns={
            'day': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        })
        
        # 转换日期格式
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        # 过滤日期范围
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        # 添加nav列（ETF使用收盘价）
        df['nav'] = df['close']
        
        return df[['date', 'open', 'close', 'high', 'low', 'volume', 'nav']]
    
    @staticmethod
    def _fetch_fund_data(code, start_date, end_date):
        """获取基金数据"""
        try:
            # 使用AKShare获取基金数据
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            
            # 重命名列
            df = df.rename(columns={
                '净值日期': 'date',
                '单位净值': 'nav',
                '日增长率': 'daily_return'
            })
            
            df['date'] = pd.to_datetime(df['date']).dt.date
            df['close'] = df['nav']
            
            # 过滤日期范围
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            
            return df[['date', 'nav', 'close']]
            
        except Exception as e:
            print(f"Error fetching fund data for {code}: {e}")
            return None
    
    @staticmethod
    def get_price_data(code, start_date=None, end_date=None):
        """获取价格数据"""
        query = PriceData.query.filter_by(product_code=code)
        
        if start_date:
            query = query.filter(PriceData.date >= start_date)
        if end_date:
            query = query.filter(PriceData.date <= end_date)
        
        data = query.order_by(PriceData.date.asc()).all()
        
        # 转换为DataFrame
        if data:
            df = pd.DataFrame([{
                'date': d.date,
                'nav': float(d.nav) if d.nav else None,
                'close': float(d.close_price) if d.close_price else None,
                'open': float(d.open_price) if d.open_price else None,
                'high': float(d.high_price) if d.high_price else None,
                'low': float(d.low_price) if d.low_price else None,
                'volume': d.volume
            } for d in data])
            return df
        
        return pd.DataFrame()
    
    @staticmethod
    def get_returns(code, start_date=None, end_date=None):
        """获取收益率序列"""
        df = DataService.get_price_data(code, start_date, end_date)
        
        if df.empty:
            return pd.Series()
        
        # 使用收盘价或净值计算收益率
        price_col = 'nav' if 'nav' in df.columns and df['nav'].notna().any() else 'close'
        df['return'] = df[price_col].pct_change()
        
        return df['return'].dropna()
