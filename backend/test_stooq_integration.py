#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试Stooq数据源集成"""

from datetime import datetime, timedelta
from app.services.data_service import DataService

def test_stooq_spy():
    """测试获取SPY数据"""
    print("=" * 60)
    print("测试: 通过DataService获取SPY数据")
    print("=" * 60)
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    try:
        df = DataService._fetch_us_stock_data('SPY', start_date, end_date)
        if df is not None and not df.empty:
            print(f"✅ 成功! 获取到 {len(df)} 条记录")
            print(f"数据列: {df.columns.tolist()}")
            print(f"最新数据:\n{df.tail(3)}")
            return True
        else:
            print("❌ 失败: 返回空数据")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stooq_qqq():
    """测试获取QQQ数据"""
    print("\n" + "=" * 60)
    print("测试: 通过DataService获取QQQ数据")
    print("=" * 60)
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    try:
        df = DataService._fetch_us_stock_data('QQQ', start_date, end_date)
        if df is not None and not df.empty:
            print(f"✅ 成功! 获取到 {len(df)} 条记录")
            print(f"最新数据:\n{df.tail(3)}")
            return True
        else:
            print("❌ 失败: 返回空数据")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试Stooq数据源集成...\n")
    
    results = {
        "SPY": test_stooq_spy(),
        "QQQ": test_stooq_qqq()
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, success in results.items():
        status = "✅ 可用" if success else "❌ 不可用"
        print(f"{name}: {status}")
