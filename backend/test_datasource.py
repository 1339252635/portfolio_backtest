#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试备用数据源"""

import requests
import json

def test_sina_api():
    """测试新浪财经API"""
    print("=" * 50)
    print("测试新浪财经API")
    print("=" * 50)
    
    # 新浪API格式：sh+代码(上海) 或 sz+代码(深圳)
    # ETF代码：513100(纳斯达克ETF) -> sh513100
    codes = ['sh513100', 'sh513500', 'sh000001']  # 上证指数
    url = f"https://hq.sinajs.cn/list={','.join(codes)}"
    
    headers = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{response.text[:1000]}")
        
        # 解析数据
        if response.status_code == 200:
            print("\n✅ 新浪财经API连接成功!")
            return True
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    return False


def test_tencent_api():
    """测试腾讯财经API"""
    print("\n" + "=" * 50)
    print("测试腾讯财经API")
    print("=" * 50)
    
    # 腾讯API格式：sh+代码 或 sz+代码
    codes = ['sh513100', 'sh513500', 'sh000001']
    url = f"https://qt.gtimg.cn/q={','.join(codes)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{response.text[:1000]}")
        
        if response.status_code == 200:
            print("\n✅ 腾讯财经API连接成功!")
            return True
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    return False


def test_baidu_api():
    """测试百度股市通API"""
    print("\n" + "=" * 50)
    print("测试百度股市通API")
    print("=" * 50)
    
    # 百度API
    url = "https://finance.pae.baidu.com/api/foreignquotation?srcid=5353&all=1&pointType=string&group=quotation_index_minute&query=上证指数&code=000001&market=ab&finClientType=pc"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{response.text[:500]}")
        
        if response.status_code == 200:
            print("\n✅ 百度股市通API连接成功!")
            return True
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    return False


if __name__ == "__main__":
    print("开始测试备用数据源...\n")
    
    results = {
        "新浪财经": test_sina_api(),
        "腾讯财经": test_tencent_api(),
        "百度股市通": test_baidu_api()
    }
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    for name, success in results.items():
        status = "✅ 可用" if success else "❌ 不可用"
        print(f"{name}: {status}")
