#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试新浪财经历史数据API - 尝试不同接口"""

import requests
import pandas as pd
from datetime import datetime, timedelta

def test_sina_hist_data_v2():
    """测试获取ETF历史数据 - 使用stock_zh_index_daily接口"""
    code = "560050"  # A50ETF
    
    # 尝试使用新浪的股票历史数据接口
    # 格式: https://stock.finance.sina.com.cn/stock/api/jsonp.php/var_123/data/StockService.getStockHistory?symbol=sh560050
    
    sina_code = f"sh{code}"
    url = f"https://stock.finance.sina.com.cn/stock/api/jsonp.php/data/StockService.getStockHistory?symbol={sina_code}"
    
    headers = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"Fetching data for {code} from Sina...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response preview: {response.text[:500]}")
            return True
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def test_akshare_alternative():
    """测试AKShare备用接口"""
    import akshare as ak
    
    code = "560050"
    print(f"\nTrying AKShare alternative for {code}...")
    
    try:
        # 尝试使用stock_zh_a_hist接口
        df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                start_date="20240101", end_date="20241231",
                                adjust="qfq")
        print(f"Got {len(df)} records from stock_zh_a_hist")
        print(df.head())
        return True
    except Exception as e:
        print(f"stock_zh_a_hist failed: {e}")
    
    try:
        # 尝试使用stock_zh_index_daily接口
        df = ak.stock_zh_index_daily(symbol=f"sh{code}")
        print(f"Got {len(df)} records from stock_zh_index_daily")
        print(df.head())
        return True
    except Exception as e:
        print(f"stock_zh_index_daily failed: {e}")
    
    return False

if __name__ == "__main__":
    test_sina_hist_data_v2()
    test_akshare_alternative()
