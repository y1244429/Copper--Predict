"""
详细检查增强数据调整的计算逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.real_enhanced_data import RealEnhancedDataManager
from run_integrated_prediction import IntegratedPredictionSystem

def detailed_check():
    print("\n" + "="*80)
    print("增强数据调整计算逻辑详细检查")
    print("="*80)

    # 1. 获取真实增强数据
    print("\n" + "-"*80)
    print("第一步：获取增强数据")
    print("-"*80)

    manager = RealEnhancedDataManager()
    data = manager.get_all_data()

    # 显示原始数据
    print("\n【原始宏观数据】")
    macro = data['macro']
    print(f"  美元指数: {macro['dollar_index']['value']:.2f}")
    print(f"  PMI: {macro['pmi']['value']:.1f}")
    print(f"  VIX: {macro['vix']['value']:.1f}")
    print(f"  利率: {macro['interest_rate']['federal_funds_rate']:.2f}%")

    # 2. 风险信号生成
    print("\n" + "-"*80)
    print("第二步：风险信号生成逻辑")
    print("-"*80)

    print("\n【风险信号阈值】")
    print("  美元指数:")
    print(f"    - High风险: >100 (当前: {macro['dollar_index']['value']:.2f})")
    print(f"    - Medium风险: >97 (当前: {macro['dollar_index']['value']:.2f})")
    print("  VIX:")
    print(f"    - High风险: >22 (当前: {macro['vix']['value']:.1f})")
    print(f"    - Medium风险: >18 (当前: {macro['vix']['value']:.1f})")
    print("  PMI:")
    print(f"    - High风险: <50 (当前: {macro['pmi']['value']:.1f})")
    print(f"    - Medium风险: <51 (当前: {macro['pmi']['value']:.1f})")

    signals = data.get('risk_signals', [])
    print(f"\n【生成的风险信号】({len(signals)}个)")
    for i, signal in enumerate(signals, 1):
        level_icon = '🔴' if signal['level'] == 'high' else '🟡'
        print(f"  {i}. {level_icon} {signal['message']}")
        print(f"     - 指标: {signal['indicator']}")
        print(f"     - 级别: {signal['level']}")
        print(f"     - 值: {signal['value']}")

    # 3. 风险调整计算
    print("\n" + "-"*80)
    print("第三步：风险调整计算")
    print("-"*80)

    # 模拟一个预测值
    test_prediction = 105099.70
    print(f"\n假设传统模型加权融合后的预测: ¥{test_prediction:,.2f}")

    # 初始化
    risk_factor = 0.98  # 基础保守调整
    adjustment_details = ["基础保守调整(-2%)"]
    print(f"\n初始风险因子: {risk_factor:.4f} (基础-2%)")

    # 逐个应用风险信号
    print("\n应用风险信号:")
    for signal in signals:
        print(f"\n  信号: {signal['indicator']} ({signal['level']})")

        if signal['level'] == 'high':
            if 'Dollar' in signal['indicator']:
                adjustment = 0.88  # -12%
                print(f"    -> High级别美元指数: 调整因子 ×{adjustment} (-{(1-adjustment)*100:.0f}%)")
            elif 'VIX' in signal['indicator']:
                adjustment = 0.90  # -10%
                print(f"    -> High级别VIX: 调整因子 ×{adjustment} (-{(1-adjustment)*100:.0f}%)")
            elif 'Emergency' in signal['indicator']:
                adjustment = 0.85  # -15%
                print(f"    -> 突发事件: 调整因子 ×{adjustment} (-{(1-adjustment)*100:.0f}%)")
            elif 'PMI' in signal['indicator']:
                adjustment = 0.92  # -8%
                print(f"    -> High级别PMI: 调整因子 ×{adjustment} (-{(1-adjustment)*100:.0f}%)")
            else:
                adjustment = 0.93  # -7%
                print(f"    -> High级别其他: 调整因子 ×{adjustment} (-{(1-adjustment)*100:.0f}%)")
        else:  # medium
            if 'Dollar' in signal['indicator']:
                adjustment = 0.94  # -6%
                print(f"    -> Medium级别美元指数: 调整因子 ×{adjustment} (-{(1-adjustment)*100:.0f}%)")
            elif 'VIX' in signal['indicator']:
                adjustment = 0.96  # -4%
                print(f"    -> Medium级别VIX: 调整因子 ×{adjustment} (-{(1-adjustment)*100:.0f}%)")
            elif 'PMI' in signal['indicator']:
                adjustment = 0.96  # -4%
                print(f"    -> Medium级别PMI: 调整因子 ×{adjustment} (-{(1-adjustment)*100:.0f}%)")
            else:
                adjustment = 0.97  # -3%
                print(f"    -> Medium级别其他: 调整因子 ×{adjustment} (-{(1-adjustment)*100:.0f}%)")

        risk_factor *= adjustment
        reduction = (1 - adjustment) * 100
        adjustment_details.append(f"{signal['indicator']}: -{reduction:.0f}%")
        print(f"    累计风险因子: {risk_factor:.4f}")

    # 4. 最终计算
    print("\n" + "-"*80)
    print("第四步：最终计算")
    print("-"*80)

    print(f"\n调整过程:")
    print(f"  原预测价格: ¥{test_prediction:,.2f}")
    print(f"  风险因子: {risk_factor:.4f}")
    print(f"  调整原因: {'; '.join(adjustment_details)}")

    adjusted_price = test_prediction * risk_factor
    total_reduction = (1 - risk_factor) * 100

    print(f"\n调整结果:")
    print(f"  调整后价格: ¥{adjusted_price:,.2f}")
    print(f"  总调整幅度: -{total_reduction:.2f}%")

    # 5. 收益率计算
    print("\n" + "-"*80)
    print("第五步：收益率计算")
    print("-"*80)

    current_price = 102100.0
    original_return = (test_prediction - current_price) / current_price * 100
    adjusted_return = (adjusted_price - current_price) / current_price * 100

    print(f"\n假设当前价格: ¥{current_price:,.2f}")
    print(f"  传统模型预测收益率: {original_return:+.2f}%")
    print(f"  调整后收益率: {adjusted_return:+.2f}%")
    print(f"  收益率变化: {adjusted_return - original_return:+.2f}%")

    # 6. 问题诊断
    print("\n" + "-"*80)
    print("问题诊断")
    print("-"*80)

    if adjusted_return < 0:
        print(f"\n⚠️  调整后收益率为负 ({adjusted_return:+.2f}%)")
        print("\n可能原因:")
        print(f"  1. 基础保守调整: -2% (固定)")
        print(f"  2. 风险信号叠加: {len(signals)}个信号")
        for detail in adjustment_details[1:]:  # 跳过基础调整
            print(f"     - {detail}")

        print(f"\n累积效应:")
        print(f"  0.98", end="")
        for signal in signals:
            if signal['level'] == 'high':
                if 'Dollar' in signal['indicator']:
                    print(f" × 0.88", end="")
                elif 'VIX' in signal['indicator']:
                    print(f" × 0.90", end="")
                elif 'PMI' in signal['indicator']:
                    print(f" × 0.92", end="")
                else:
                    print(f" × 0.93", end="")
            else:  # medium
                if 'Dollar' in signal['indicator']:
                    print(f" × 0.94", end="")
                elif 'VIX' in signal['indicator']:
                    print(f" × 0.96", end="")
                elif 'PMI' in signal['indicator']:
                    print(f" × 0.96", end="")
                else:
                    print(f" × 0.97", end="")
        print(f" = {risk_factor:.4f}")

    print("\n" + "="*80)

if __name__ == "__main__":
    detailed_check()
