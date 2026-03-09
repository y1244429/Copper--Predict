#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Comex 波动率显示"""

from app import app
import json

print("测试 Comex 日内波动率...")
print("="*80)

# 测试获取历史记录
with app.test_client() as client:
    response = client.get('/db/history')
    result = json.loads(response.data)

    if result.get('success') and result.get('data'):
        print(f"✓ 成功获取 {result.get('total')} 条记录")
        print()
        print("数据库表格应显示的列（包含波动率）:")
        print("-"*110)
        print(f"{'预测日期':<12} {'当前价格':<12} {'宏观3月':<12} {'基本面6月':<12} {'Comex开盘':<12} {'Comex收盘':<12} {'波动率':<10}")
        print("-"*110)
        for row in result['data'][:5]:  # 显示前5条
            print(f"{row.get('prediction_date'):<12} "
                  f"¥{row.get('current_price'):>10.2f} "
                  f"¥{row.get('macro_3month'):>10.2f} "
                  f"¥{row.get('fundamental_6month'):>10.2f} "
                  f"${row.get('comex_open'):>10.2f} "
                  f"${row.get('comex_close'):>10.2f} "
                  f"{row.get('comex_volatility'):>8.2f}%")
    else:
        print("✗ 获取失败:", result.get('message'))

print()
print("="*80)
print("✓ Comex 日内波动率计算公式:")
print("  波动率 = (最高价 - 最低价) / ((开盘价 + 收盘价) / 2) × 100%")
