"""
检查增强数据调整效果
分析为什么调整后的数值仍然偏高
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.real_enhanced_data import RealEnhancedDataManager
from run_integrated_prediction import IntegratedPredictionSystem
import json

def check_real_data():
    """检查当前获取的真实数据"""
    print("\n" + "="*70)
    print("检查当前获取的真实数据")
    print("="*70)

    # 获取真实数据
    manager = RealEnhancedDataManager()
    data = manager.get_all_data()

    print("\n【宏观数据】")
    macro = data['macro']
    print(f"  美元指数: {macro['dollar_index']['value']:.2f}")
    print(f"    - 汇率: {macro['dollar_index'].get('usd_cny_rate', 'N/A')}")
    print(f"    - 数据源: {macro['dollar_index']['source']}")
    print(f"  PMI: {macro['pmi']['value']:.1f}")
    print(f"    - 数据源: {macro['pmi']['source']}")
    print(f"  VIX: {macro['vix']['value']:.1f}")
    print(f"    - 数据源: {macro['vix']['source']}")
    print(f"  利率: {macro['interest_rate']['federal_funds_rate']:.2f}%")

    print("\n【资金流向】")
    capital = data['capital_flow']
    print(f"  CFTC商业净头寸: {capital['cftc']['commercial']['net']:,}")
    print(f"  CFTC投机净头寸: {capital['cftc']['speculative']['net']:,}")
    print(f"  总持仓量: {capital['open_interest']:,}")

    print("\n【新闻情绪】")
    news = data['news_sentiment']
    print(f"  文章总数: {news['total_articles']}")
    print(f"  整体情绪: {news['overall_sentiment']}")
    print(f"  情绪分数: {news['overall_sentiment_score']:.2f}")
    print(f"  突发事件: {'有' if news.get('has_emergency') else '无'}")

    print("\n【风险信号】")
    signals = data.get('risk_signals', [])
    if signals:
        for i, signal in enumerate(signals, 1):
            level_icon = '🔴' if signal['level'] == 'high' else '🟡'
            print(f"  {i}. {level_icon} {signal['message']}")
            print(f"     - 类型: {signal['type']}")
            print(f"     - 指标: {signal['indicator']}")
            print(f"     - 值: {signal['value']}")
    else:
        print("  ⚠️  没有风险信号！")

    return data

def analyze_adjustment_issue(data):
    """分析调整问题"""
    print("\n" + "="*70)
    print("分析调整问题")
    print("="*70)

    signals = data.get('risk_signals', [])

    # 计算总调整因子
    total_factor = 1.0
    details = []

    for signal in signals:
        if signal['level'] == 'high':
            if 'Dollar' in signal['indicator']:
                factor = 0.90
                reduction = 10
            elif 'VIX' in signal['indicator']:
                factor = 0.92
                reduction = 8
            elif 'Emergency' in signal['indicator']:
                factor = 0.85
                reduction = 15
            elif 'PMI' in signal['indicator']:
                factor = 0.93
                reduction = 7
            else:
                factor = 0.95
                reduction = 5
        else:  # medium
            if 'Dollar' in signal['indicator']:
                factor = 0.96
                reduction = 4
            elif 'VIX' in signal['indicator']:
                factor = 0.97
                reduction = 3
            elif 'PMI' in signal['indicator']:
                factor = 0.97
                reduction = 3
            else:
                factor = 0.98
                reduction = 2

        total_factor *= factor
        details.append(f"{signal['indicator']}: -{reduction}%")

    print(f"\n总调整因子: {total_factor:.4f}")
    print(f"总调整幅度: {(1 - total_factor) * 100:.2f}%")
    print(f"调整详情: {'; '.join(details) if details else '无'}")

    # 问题诊断
    print("\n【问题诊断】")
    if not signals:
        print("❌ 问题1: 没有生成任何风险信号！")
        print("   原因: 美元指数阈值设置可能过高，或者数据获取失败")
    elif total_factor > 0.95:
        print(f"⚠️  问题2: 调整幅度太小（仅{(1-total_factor)*100:.1f}%）")
        print("   建议: 当前市场美元指数高，应该有更大的向下调整")
    else:
        print(f"✅ 调整幅度合理: {(1-total_factor)*100:.2f}%")

    # 检查美元指数数据
    dollar_value = data['macro']['dollar_index']['value']
    print(f"\n【美元指数分析】")
    print(f"  当前值: {dollar_value:.2f}")
    if dollar_value > 105:
        print(f"  评估: 高风险（应该触发high风险信号，调整10%）")
        expected_signal = any('Dollar' in s['indicator'] and s['level'] == 'high' for s in signals)
        if not expected_signal:
            print(f"  ❌ 问题: 应该触发high风险信号但没有触发！")
    elif dollar_value > 102:
        print(f"  评估: 中风险（应该触发medium风险信号，调整4%）")
        expected_signal = any('Dollar' in s['indicator'] and s['level'] == 'medium' for s in signals)
        if not expected_signal:
            print(f"  ❌ 问题: 应该触发medium风险信号但没有触发！")
    else:
        print(f"  评估: 正常（无风险信号）")

    # 检查汇率数据来源
    print(f"\n【数据来源检查】")
    source = data['macro']['dollar_index']['source']
    if 'Fallback' in source:
        print(f"  ⚠️  使用的是备用数据，不是真实数据！")
        print(f"  原因: AKShare API获取失败")
    else:
        print(f"  ✅ 使用真实数据: {source}")

    return total_factor

def simulate_high_dollar_scenario():
    """模拟高美元指数场景"""
    print("\n" + "="*70)
    print("模拟高美元指数场景（USD/CNY = 7.35）")
    print("="*70)

    # 模拟高汇率
    simulated_usd_cny = 7.35
    simulated_dollar_index = simulated_usd_cny / 7.2 * 100  # 约102.08

    print(f"\nUSD/CNY汇率: {simulated_usd_cny}")
    print(f"转换后的美元指数: {simulated_dollar_index:.2f}")

    # 判断风险等级
    if simulated_dollar_index > 105:
        risk_level = 'high'
        adjustment = 10
        factor = 0.90
    elif simulated_dollar_index > 102:
        risk_level = 'medium'
        adjustment = 4
        factor = 0.96
    else:
        risk_level = 'low'
        adjustment = 0
        factor = 1.0

    print(f"\n风险等级: {risk_level}")
    print(f"建议调整: -{adjustment}%")
    print(f"调整因子: {factor:.4f}")

    # 模拟预测
    test_price = 105000
    adjusted_price = test_price * factor
    print(f"\n测试预测:")
    print(f"  调整前: ¥{test_price:,.2f}")
    print(f"  调整后: ¥{adjusted_price:,.2f}")
    print(f"  差异: ¥{test_price - adjusted_price:,.2f} ({-adjustment}%)")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("增强数据调整检查")
    print("="*70)

    # 检查真实数据
    real_data = check_real_data()

    # 分析调整问题
    analyze_adjustment_issue(real_data)

    # 模拟高美元场景
    simulate_high_dollar_scenario()

    print("\n" + "="*70)
    print("检查完成")
    print("="*70 + "\n")
