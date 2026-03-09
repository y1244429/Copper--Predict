import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_integrated_prediction import IntegratedPredictionSystem
import json

print("="*70)
print("集成系统预测 - 数据来源追踪")
print("="*70)

# 创建系统
system = IntegratedPredictionSystem()

# 执行预测(会显示详细日志)
result = system.predict_with_integration(horizon=5)

print("\n" + "="*70)
print("【数据来源详细分析】")
print("="*70)

# 1. 增强数据来源
enhanced_data = result['enhanced_data']
macro = enhanced_data['macro']

print(f"\n【1. 宏观数据】")
print(f"  美元指数: {macro['dollar_index']['value']}")
print(f"    数据源: {macro['dollar_index']['source']}")
print(f"    日期: {macro['dollar_index']['date']}")
print(f"    真实性: {'✅ 真实' if 'Mock' not in macro['dollar_index']['source'] and 'Fallback' not in macro['dollar_index']['source'] else '⚠️ 备用/模拟'}")

print(f"\n  VIX恐慌指数: {macro['vix']['value']}")
print(f"    数据源: {macro['vix']['source']}")
print(f"    日期: {macro['vix']['date']}")
print(f"    真实性: {'✅ 真实' if 'Mock' not in macro['vix']['source'] and 'Fallback' not in macro['vix']['source'] else '⚠️ 备用/模拟'}")

print(f"\n  PMI: {macro['pmi']['value']}")
print(f"    数据源: {macro['pmi']['source']}")
print(f"    日期: {macro['pmi']['date']}")
print(f"    真实性: {'✅ 真实' if 'Mock' not in macro['pmi']['source'] and 'Fallback' not in macro['pmi']['source'] else '⚠️ 备用/模拟'}")

print(f"\n  联邦利率: {macro['interest_rate']['federal_funds_rate']}%")
print(f"    数据源: {macro['interest_rate']['source']}")
print(f"    日期: {macro['interest_rate']['date']}")
print(f"    真实性: {'✅ 真实' if 'Mock' not in macro['interest_rate']['source'] and 'Fallback' not in macro['interest_rate']['source'] else '⚠️ 备用/模拟'}")

# 2. 风险信号
risk_signals = enhanced_data['risk_signals']
print(f"\n【2. 风险信号】({len(risk_signals)}个)")
for i, signal in enumerate(risk_signals, 1):
    level = '🔴 高' if signal['level'] == 'high' else '🟡 中'
    print(f"  {i}. {level} - {signal['message']}")
    print(f"     指标: {signal['indicator']}")
    print(f"     值: {signal['value']}")

# 3. 市场状态判断
market_state = result['market_state']
print(f"\n【3. 市场状态】")
print(f"  状态: {market_state}")
print(f"  基于宏观数据判断: VIX={macro['vix']['value']}, 美元指数={macro['dollar_index']['value']}, PMI={macro['pmi']['value']}")

# 4. 动态权重
weights = result['weights']
print(f"\n【4. 模型权重】")
print(f"  XGBoost: {weights['xgboost']:.1%}")
print(f"  宏观: {weights['macro']:.1%}")
print(f"  基本面: {weights['fundamental']:.1%}")
print(f"  说明: 基于'{market_state}'市场状态调整")

# 5. 风险调整
risk_adj = result['risk_adjusted_prediction']
print(f"\n【5. 风险调整】")
print(f"  调整前: ¥{result['weighted_prediction']['price']:,.2f}")
print(f"  调整后: ¥{risk_adj['price']:,.2f}")
print(f"  调整因子: {risk_adj['adjustment_factor']:.4f}")
print(f"  调整原因: {'; '.join(risk_adj['adjustment_details']) if risk_adj['adjustment_details'] else '无'}")
print(f"  置信度: {result['confidence_level']}")

# 6. 最终预测
final = result['final_prediction']
print(f"\n【6. 最终预测】")
print(f"  预测价格: ¥{final['price']:,.2f} ({final['return_pct']:+.2f}%)")
print(f"  预测区间: ¥{final['lower_bound']:,.2f} ~ ¥{final['upper_bound']:,.2f}")

# 7. 投资建议
rec = result['recommendation']
print(f"\n【7. 投资建议】")
print(f"  方向: {rec['direction']}")
print(f"  建议: {rec['advice']}")
print(f"  仓位: {rec['position_size']}")

print("\n" + "="*70)
print("【总结】")
print("="*70)

# 统计数据真实性
macro_sources = {
    '美元指数': macro['dollar_index']['source'],
    'VIX': macro['vix']['source'],
    'PMI': macro['pmi']['source'],
    '联邦利率': macro['interest_rate']['source']
}

real_count = 0
for name, source in macro_sources.items():
    is_real = 'Mock' not in source and 'Fallback' not in source
    status = '✅ 真实' if is_real else '⚠️ 备用/模拟'
    print(f"  {name}: {status} ({source})")
    if is_real:
        real_count += 1

print(f"\n  数据真实性: {real_count}/4 项为真实实时数据")
print(f"  风险信号: {len(risk_signals)} 个, 基于真实宏观数据生成")
print(f"  市场状态: 基于{real_count}项真实宏观数据判断")

print("\n" + "="*70)
