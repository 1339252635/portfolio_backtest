#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试美股数据获取"""

from datetime import datetime, timedelta
from app.services.data_service import DataService

def test_us_stock():
    """测试获取美股数据"""
    code = 'SPY'
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    try:
        print(f"Testing fetch for {code}...")
        df = DataService._fetch_us_stock_data(code, start_date, end_date)
        if df is not None and not df.empty:
            print(f"✅ Success! Got {len(df)} records")
            print(df.head())
        else:
            print("❌ No data returned")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_us_stock()
