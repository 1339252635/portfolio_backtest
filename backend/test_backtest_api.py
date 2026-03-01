#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试回测API"""

import requests
import json
from datetime import datetime, timedelta

def test_create_backtest():
    """测试创建回测"""
    print("=" * 60)
    print("测试: 创建回测")
    print("=" * 60)
    
    url = "http://127.0.0.1:5000/api/backtest"
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    data = {
        "name": "测试回测",
        "description": "测试回测功能",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "initial_amount": 100000,
        "rebalance_strategy": "none",
        "allocations": [
            {"product_code": "A50ETF", "allocation_ratio": 20},
            {"product_code": "SPY", "allocation_ratio": 35},
            {"product_code": "HONGLLB", "allocation_ratio": 10},
            {"product_code": "QQQ", "allocation_ratio": 35}
        ]
    }
    
    try:
        print(f"发送请求: {json.dumps(data, indent=2, ensure_ascii=False)}")
        response = requests.post(url, json=data, timeout=60)
        print(f"\n状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return response.status_code == 201
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试回测API...\n")
    success = test_create_backtest()
    print(f"\n{'✅ 成功' if success else '❌ 失败'}")
