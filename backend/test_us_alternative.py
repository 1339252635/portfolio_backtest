#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试美股替代数据源"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def test_alpha_vantage():
    """测试Alpha Vantage (需要API key)"""
    print("=" * 60)
    print("测试: Alpha Vantage API (SPY)")
    print("=" * 60)
    # Alpha Vantage需要API key，这里只是测试接口格式
    print("Alpha Vantage需要API key，跳过测试")
    return False

def test_stooq():
    """测试Stooq免费数据源"""
    print("\n" + "=" * 60)
    print("测试: Stooq数据源 (SPY)")
    print("=" * 60)
    try:
        # Stooq提供CSV格式的免费数据
        url = "https://stooq.com/q/d/l/?s=spy.us&i=d"
        df = pd.read_csv(url)
        print(f"✅ 成功! 获取到 {len(df)} 条记录")
        print(f"数据列: {df.columns.tolist()}")
        print(f"最新数据:\n{df.tail(3)}")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_fred():
    """测试FRED数据源（美联储经济数据）"""
    print("\n" + "=" * 60)
    print("测试: FRED数据源")
    print("=" * 60)
    print("FRED主要用于经济指标，不适合股票价格")
    return False

def test_yahoo_with_session():
    """测试使用session的Yahoo Finance"""
    print("\n" + "=" * 60)
    print("测试: Yahoo Finance with Session (延迟5秒)")
    print("=" * 60)
    try:
        import yfinance as yf
        
        # 等待一段时间再请求
        time.sleep(5)
        
        # 使用不同的方式
        ticker = yf.Ticker("SPY")
        # 使用不同的period
        df = ticker.history(period="5d", interval="1d")
        
        if not df.empty:
            print(f"✅ 成功! 获取到 {len(df)} 条记录")
            print(f"最新数据: {df.tail(1).to_dict('records')[0]}")
            return True
        else:
            print("❌ 失败: 返回空数据")
            return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试美股替代数据源...\n")
    
    results = {
        "Stooq": test_stooq(),
        "Yahoo(with delay)": test_yahoo_with_session()
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, success in results.items():
        status = "✅ 可用" if success else "❌ 不可用"
        print(f"{name}: {status}")
