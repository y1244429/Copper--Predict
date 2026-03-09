#!/usr/bin/env python3
"""测试综合预测计算逻辑"""

import requests
import json

print("="*70)
print("测试综合预测计算逻辑")
print("="*70)

# 获取API数据
r = requests.get('http://localhost:8002/api/integrated-prediction')
data = r.json()

# 提取预测数据
current_price = data['current_price']
xgboost = data['predictions']['xgboost']
weighted = data['predictions']['weighted']
integrated = data['final_prediction']

print(f"\n当前价格: ¥{current_price:,.2f}")
print("\n各模型预测:")
print(f"1. XGBoost技术模型: ¥{xgboost['price']:,.2f} ({xgboost['return_pct']:+.2f}%)")
print(f"2. 加权融合预测: ¥{weighted['price']:,.2f} ({weighted['return_pct']:+.2f}%)")
print(f"3. 集成系统预测: ¥{integrated['price']:,.2f} ({integrated['return_pct']:+.2f}%)")

# 计算综合预测（3个模型平均）
avg_price = (xgboost['price'] + weighted['price'] + integrated['price']) / 3
avg_change = (xgboost['return_pct'] + weighted['return_pct'] + integrated['return_pct']) / 3

print("\n" + "="*70)
print("综合预测（3个模型平均）")
print("="*70)
print(f"综合预测价格: ¥{avg_price:,.2f}")
print(f"综合预测涨跌: {avg_change:+.2f}%")
print(f"预测方向: {'看涨' if avg_change >= 0 else '看跌'}")

# 计算一致性
changes = [xgboost['return_pct'], weighted['return_pct'], integrated['return_pct']]
directions = [1 if c >= 0 else -1 for c in changes]
same_direction = all(d == directions[0] for d in directions)

avg_change_abs = abs(avg_change)
variance = sum((c - avg_change)**2 for c in changes) / len(changes)
std_dev = variance ** 0.5
similar_magnitude = avg_change_abs == 0 or (std_dev / avg_change_abs) < 0.3

consensus = "高度一致" if (same_direction and similar_magnitude) else "存在分歧"

print(f"\n模型一致性: {consensus}")
print(f"  - 方向一致: {'是' if same_direction else '否'} ({directions})")
print(f"  - 幅度接近: {'是' if similar_magnitude else '否'} (标准差: {std_dev:.4f}%)")

print("\n" + "="*70)
print("修复说明:")
print("="*70)
print("1. 修复前: 基于4个模型计算（XGBoost、宏观、基本面、集成）")
print("   问题: API没有返回独立的宏观和基本面预测")
print("   结果: 使用了错误的计算值")
print("")
print("2. 修复后: 基于3个模型计算（XGBoost、加权融合、集成）")
print("   说明: 加权融合已经是XGBoost、宏观、基本面的综合")
print("   结果: 集成系统 = 加权融合 + 市场状态 + 情绪 + 风险调整")
print("="*70)
