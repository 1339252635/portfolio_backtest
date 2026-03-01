#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试新浪财经历史数据API"""

import requests
import pandas as pd
from datetime import datetime, timedelta

def test_sina_hist_data():
    """测试获取ETF历史数据"""
    code = "560050"  # A50ETF
    sina_code = f"sh{code}"
    
    # 新浪财经历史数据API
    url = f"https://quotes.sina.cn/cn/api/quotes.php?symbol={sina_code}&scale=240&ma=5&datalen=1000"
    
    headers = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"Fetching data for {code} from Sina...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # 解析JSONP格式
            text = response.text
            print(f"Response preview: {text[:200]}")
            
            # 提取JSON部分
            start = text.find('(') + 1
            end = text.rfind(')')
            if start > 0 and end > start:
                json_str = text[start:end]
                data = pd.read_json(json_str)
                print(f"\nGot {len(data)} records")
                print(f"\nColumns: {data.columns.tolist()}")
                print(f"\nFirst few rows:")
                print(data.head())
                return True
            else:
                print("Invalid response format")
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    return False

if __name__ == "__main__":
    test_sina_hist_data()
