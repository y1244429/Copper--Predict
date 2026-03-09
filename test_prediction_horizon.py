#!/usr/bin/env python3
"""
测试宏观和基本面模型的预测
"""
import sys
sys.path.append('/Users/ydy/CodeBuddy/20260227142050/copper_prediction_v2')

import pandas as pd
import numpy as np
from main import CopperPredictionSystem

# 创建系统
system = CopperPredictionSystem(data_source="auto")

# 加载数据
print("加载数据...")
system.load_data(days=365)

# 计算历史波动率
close = system.current_data['close']
returns = close.pct_change().dropna()
volatility_annual = returns.std() * np.sqrt(252)
volatility_daily = volatility_annual / np.sqrt(252)
print(f"\n历史波动率:")
print(f"  年化波动率: {volatility_annual:.4f} ({volatility_annual*100:.2f}%)")
print(f"  日波动率: {volatility_daily:.4f} ({volatility_daily*100:.2f}%)")

# 训练模型
print("\n训练模型...")
system.train_macro()
system.train_fundamental()

# 测试不同horizon的预测
print("\n\n测试不同预测周期的结果:")
print("="*80)

for horizon in [1, 7, 30, 60, 90, 180]:
    print(f"\n预测周期: {horizon}天")

    # 宏观模型
    try:
        macro_pred = system.macro_model.predict(system.current_data, horizon=horizon)
        print(f"  宏观模型: ¥{macro_pred['predicted_price']:,.2f} ({macro_pred['predicted_return']:+.2f}%)")
    except Exception as e:
        print(f"  宏观模型失败: {e}")

    # 基本面模型
    try:
        fund_pred = system.fundamental_model.predict(system.current_data, horizon=horizon)
        print(f"  基本面模型: ¥{fund_pred['predicted_price']:,.2f} ({fund_pred['predicted_return']:+.2f}%)")
    except Exception as e:
        print(f"  基本面模型失败: {e}")

print("\n" + "="*80)
