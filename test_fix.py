#!/usr/bin/env python3
"""测试集成预测系统修复效果"""

import sys
sys.path.append('/Users/ydy/CodeBuddy/20260227142050/copper_prediction_v2')

from run_integrated_prediction import IntegratedPredictionSystem
import json

print("="*70)
print("测试集成预测系统修复")
print("="*70)

# 创建预测系统
system = IntegratedPredictionSystem()

# 执行预测
print("\n执行预测中...")
result = system.predict_with_integration(horizon=5)

print("\n" + "="*70)
print("修复后计算结果")
print("="*70)
print(f"当前价格: ¥{result['current_price']:,.2f}")
print(f"市场状态: {result['market_state']}")
print(f"模型权重: {result['weights']}")

print("\n各模型预测:")
print(f"  XGBoost: ¥{result['models']['xgboost']['price']:,.2f} ({result['models']['xgboost']['return_pct']:+.2f}%)")
print(f"  加权融合: ¥{result['weighted_prediction']['price']:,.2f} ({result['weighted_prediction']['return_pct']:+.2f}%)")
print(f"  集成系统: ¥{result['final_prediction']['price']:,.2f} ({result['final_prediction']['return_pct']:+.2f}%)")
print(f"  风险调整: ¥{result['risk_adjusted_prediction']['price']:,.2f} ({result['risk_adjusted_prediction']['return_pct']:+.2f}%)")

print(f"\n风险信号: {len(result['risk_signals'])}个")
for sig in result['risk_signals']:
    print(f"  - {sig['indicator']}: {sig['level']}")

print(f"\n风险调整因子: {result['risk_adjusted_prediction']['adjustment_factor']:.4f}")
print(f"调整详情: {result['risk_adjusted_prediction'].get('adjustment_details', [])}")

print("\n" + "="*70)
print("修复总结:")
print("="*70)
print("1. 市场状态判断: 现在优先检查风险信号，而不是被情绪覆盖")
print("2. 集成预测计算: 当加权融合为负数时，牛市和正面情绪会让预测更接近0")
print("   - 旧逻辑: -0.15% * 1.05 * 1.03 = -0.162% (更负了，错误)")
print("   - 新逻辑: -0.15% * 0.95 * 0.97 = -0.138% (接近0，正确)")
print("="*70)
