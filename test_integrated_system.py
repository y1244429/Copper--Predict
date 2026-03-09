#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试集成预测系统结果
"""

import sys
sys.path.append('.')

from run_integrated_prediction import IntegratedPredictionSystem

def test_integrated_prediction():
    """测试集成预测系统"""
    print("="*60)
    print("测试集成预测系统")
    print("="*60)

    # 创建集成预测系统
    system = IntegratedPredictionSystem()

    # 执行预测
    result = system.predict_with_integration(horizon=5)

    # 输出结果
    print(f"\n当前价格: ¥{result['current_price']:,.2f}")
    print(f"\n各模型预测:")
    print(f"  XGBoost: ¥{result['models']['xgboost']['price']:,.2f} ({result['models']['xgboost']['return_pct']:+.2f}%)")
    print(f"  宏观因子: ¥{result['models']['macro']['price']:,.2f} ({result['models']['macro']['return_pct']:+.2f}%)")
    print(f"  基本面: ¥{result['models']['fundamental']['price']:,.2f} ({result['models']['fundamental']['return_pct']:+.2f}%)")
    
    print(f"\n加权预测: ¥{result['weighted_prediction']['price']:,.2f} ({result['weighted_prediction']['return_pct']:+.2f}%)")
    print(f"风险调整后: ¥{result['risk_adjusted_prediction']['price']:,.2f} ({result['risk_adjusted_prediction']['return_pct']:+.2f}%)")
    print(f"最终预测: ¥{result['final_prediction']['price']:,.2f} ({result['final_prediction']['return_pct']:+.2f}%)")

if __name__ == '__main__':
    test_integrated_prediction()
