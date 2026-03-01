#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试所有数据源可用性"""

import requests
import akshare as ak
import yfinance as yf
from datetime import datetime, timedelta
import time

def test_akshare_chinese_etf():
    """测试AKShare中国ETF"""
    print("=" * 60)
    print("测试1: AKShare 中国ETF (560050)")
    print("=" * 60)
    try:
        df = ak.stock_zh_index_daily(symbol="sh560050")
        print(f"✅ 成功! 获取到 {len(df)} 条记录")
        print(f"最新数据: {df.tail(1).to_dict('records')[0]}")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_akshare_fund():
    """测试AKShare基金"""
    print("\n" + "=" * 60)
    print("测试2: AKShare 基金 (515080)")
    print("=" * 60)
    try:
        df = ak.stock_zh_index_daily(symbol="sh515080")
        print(f"✅ 成功! 获取到 {len(df)} 条记录")
        print(f"最新数据: {df.tail(1).to_dict('records')[0]}")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_yahoo_finance():
    """测试Yahoo Finance"""
    print("\n" + "=" * 60)
    print("测试3: Yahoo Finance (SPY)")
    print("=" * 60)
    try:
        # 添加延迟避免限流
        time.sleep(1)
        ticker = yf.Ticker("SPY")
        df = ticker.history(period="1mo")
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

def test_sina_realtime():
    """测试新浪财经实时数据"""
    print("\n" + "=" * 60)
    print("测试4: 新浪财经实时数据 (sh560050)")
    print("=" * 60)
    try:
        url = "https://hq.sinajs.cn/list=sh560050"
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ 成功! 状态码: {response.status_code}")
        print(f"响应: {response.text[:200]}")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试所有数据源...\n")
    
    results = {
        "AKShare中国ETF": test_akshare_chinese_etf(),
        "AKShare基金": test_akshare_fund(),
        "Yahoo Finance": test_yahoo_finance(),
        "新浪财经实时": test_sina_realtime()
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, success in results.items():
        status = "✅ 可用" if success else "❌ 不可用"
        print(f"{name}: {status}")
