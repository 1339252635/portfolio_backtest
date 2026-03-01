#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试智能配置API"""

import requests
import json

url = 'http://127.0.0.1:5000/api/smart-allocation/assess'
data = {
    'age': 30,
    'investment_experience': 3,
    'annual_income': 200000,
    'liquid_assets': 300000,
    'investment_horizon': 10,
    'loss_tolerance': 0.20,
    'monthly_investment': 5000,
    'investment_goal': 'balanced_growth'
}

try:
    response = requests.post(url, json=data, timeout=10)
    print('Status:', response.status_code)
    result = response.json()
    print('Success:', result.get('success'))
    print('Data:', json.dumps(result.get('data', {}), indent=2, ensure_ascii=False)[:1000])
except Exception as e:
    print('Error:', e)
