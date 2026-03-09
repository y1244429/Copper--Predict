"""
测试增强数据调整逻辑
验证美元指数高时是否正确降低预测值
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_integrated_prediction import IntegratedPredictionSystem
import json

def test_high_dollar_adjustment():
    """测试高美元指数的调整"""
    print("\n" + "="*70)
    print("测试：高美元指数情况下的调整")
    print("="*70)

    # 创建系统
    system = IntegratedPredictionSystem()

    # 模拟高美元指数数据
    mock_enhanced_data = {
        'macro': {
            'dollar_index': {'value': 108.5, 'source': 'Test'},  # 高美元指数
            'pmi': {'value': 50.8, 'source': 'Test'},
            'vix': {'value': 18.0, 'source': 'Test'},
            'interest_rate': {'federal_funds_rate': 4.75}
        },
        'capital_flow': {
            'cftc': {
                'commercial': {'net': -30000},
                'speculative': {'net': 10000}
            },
            'open_interest': 520000
        },
        'news_sentiment': {
            'overall_sentiment': 'neutral',
            'overall_sentiment_score': 0.1,
            'has_emergency': False,
            'total_articles': 10
        },
        'risk_signals': [
            {
                'type': 'macro',
                'indicator': 'Dollar Index',
                'value': 108.5,
                'level': 'high',
                'message': '美元指数过强(108.50),对铜价形成强力压制'
            }
        ]
    }

    # 测试调整逻辑
    test_price = 105000.0
    adjustment = system.apply_risk_adjustment(test_price, mock_enhanced_data)

    print(f"\n测试价格: ¥{test_price:,.2f}")
    print(f"调整后价格: ¥{adjustment['adjusted_prediction']:,.2f}")
    print(f"调整因子: {adjustment['adjustment_factor']:.4f}")
    print(f"调整幅度: {(1 - adjustment['adjustment_factor']) * 100:.2f}%")
    print(f"调整原因: {'; '.join(adjustment.get('adjustment_details', []))}")

    # 验证调整是否正确
    expected_reduction = 0.10  # 应该降低10%
    actual_reduction = 1 - adjustment['adjustment_factor']

    if abs(actual_reduction - expected_reduction) < 0.01:
        print(f"\n✅ 测试通过！调整幅度符合预期")
    else:
        print(f"\n❌ 测试失败！预期调整 {expected_reduction*100:.0f}%，实际 {actual_reduction*100:.0f}%")

    return adjustment

def test_normal_conditions():
    """测试正常情况（无风险信号）"""
    print("\n" + "="*70)
    print("测试：正常情况下的调整")
    print("="*70)

    system = IntegratedPredictionSystem()

    mock_enhanced_data = {
        'risk_signals': []  # 无风险信号
    }

    test_price = 105000.0
    adjustment = system.apply_risk_adjustment(test_price, mock_enhanced_data)

    print(f"\n测试价格: ¥{test_price:,.2f}")
    print(f"调整后价格: ¥{adjustment['adjusted_prediction']:,.2f}")
    print(f"调整因子: {adjustment['adjustment_factor']:.4f}")

    if adjustment['adjustment_factor'] == 1.0:
        print(f"\n✅ 测试通过！无风险信号时不调整")
    else:
        print(f"\n❌ 测试失败！无风险信号时不应该调整")

    return adjustment

def test_multiple_risks():
    """测试多个风险信号叠加"""
    print("\n" + "="*70)
    print("测试：多个风险信号叠加")
    print("="*70)

    system = IntegratedPredictionSystem()

    mock_enhanced_data = {
        'risk_signals': [
            {
                'type': 'macro',
                'indicator': 'Dollar Index',
                'value': 106.0,
                'level': 'high',
                'message': '美元指数过强(106.00),对铜价形成强力压制'
            },
            {
                'type': 'macro',
                'indicator': 'VIX',
                'value': 28.0,
                'level': 'medium',
                'message': 'VIX恐慌指数偏高(28.0),市场波动性增加'
            },
            {
                'type': 'news',
                'indicator': 'News Sentiment',
                'value': -0.3,
                'level': 'medium',
                'message': '新闻情绪偏负面(分数: -0.30)'
            }
        ]
    }

    test_price = 105000.0
    adjustment = system.apply_risk_adjustment(test_price, mock_enhanced_data)

    print(f"\n测试价格: ¥{test_price:,.2f}")
    print(f"调整后价格: ¥{adjustment['adjusted_prediction']:,.2f}")
    print(f"调整因子: {adjustment['adjustment_factor']:.4f}")
    print(f"调整幅度: {(1 - adjustment['adjustment_factor']) * 100:.2f}%")
    print(f"调整原因: {'; '.join(adjustment.get('adjustment_details', []))}")

    # 预期调整: 0.90 * 0.97 * 0.98 ≈ 0.855
    expected_factor = 0.90 * 0.97 * 0.98
    actual_factor = adjustment['adjustment_factor']

    if abs(actual_factor - expected_factor) < 0.01:
        print(f"\n✅ 测试通过！多个风险信号正确叠加")
    else:
        print(f"\n⚠️  调整因子略有差异: 预期 {expected_factor:.4f}, 实际 {actual_factor:.4f}")

    return adjustment

if __name__ == "__main__":
    print("\n" + "="*70)
    print("风险调整逻辑测试")
    print("="*70)

    # 运行测试
    test_normal_conditions()
    test_high_dollar_adjustment()
    test_multiple_risks()

    print("\n" + "="*70)
    print("测试完成")
    print("="*70 + "\n")
