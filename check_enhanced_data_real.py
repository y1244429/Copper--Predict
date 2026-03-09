#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查增强数据预测使用的数据来源真实性
"""

import sys
sys.path.append('/Users/ydy/CodeBuddy/20260227142050/copper_prediction_v2')

from data.enhanced_data_sources import EnhancedDataIntegration
import json

print("="*80)
print("增强数据预测 - 数据来源真实性检查")
print("="*80)

# 1. 初始化数据管理器
print("\n【步骤1】初始化数据管理器")
print("-"*80)

integration = EnhancedDataIntegration()
print("✓ EnhancedDataIntegration 已初始化")

# 2. 获取增强数据
print("\n【步骤2】获取增强数据")
print("-"*80)

enhanced_data = integration.get_comprehensive_data()

# 3. 详细分析每个数据源
print("\n【步骤3】数据来源详细分析")
print("-"*80)

macro = enhanced_data['macro']

# 美元指数
dollar_index = macro['dollar_index']
print(f"\n📊 美元指数:")
print(f"   数值: {dollar_index['value']}")
print(f"   来源: {dollar_index['source']}")
print(f"   时间戳: {dollar_index['timestamp']}")
if 'Mock' in dollar_index['source']:
    print(f"   ⚠️  状态: 模拟数据")
else:
    print(f"   ✅ 状态: 真实数据")

# PMI
pmi = macro['pmi']
print(f"\n📊 PMI:")
print(f"   数值: {pmi['value']}")
print(f"   来源: {pmi['source']}")
print(f"   时间戳: {pmi['timestamp']}")
if 'Mock' in pmi['source']:
    print(f"   ⚠️  状态: 模拟数据")
else:
    print(f"   ✅ 状态: 真实数据")

# 联邦利率
interest_rate = macro['interest_rate']
print(f"\n📊 联邦利率:")
print(f"   数值: {interest_rate['federal_funds_rate']}%")
print(f"   来源: {interest_rate['source']}")
if 'Mock' in interest_rate['source']:
    print(f"   ⚠️  状态: 模拟数据")
else:
    print(f"   ✅ 状态: 真实数据")

# VIX
vix = macro['vix']
print(f"\n📊 VIX恐慌指数:")
print(f"   数值: {vix['value']}")
print(f"   来源: {vix['source']}")
if 'Mock' in vix['source']:
    print(f"   ⚠️  状态: 模拟数据")
else:
    print(f"   ✅ 状态: 真实数据")

# 4. 资金流向数据
print(f"\n【资金流向数据】")
capital_flow = enhanced_data['capital_flow']

print(f"\n📊 CFTC持仓:")
if 'cftc_report' in capital_flow:
    print(f"   来源: {capital_flow['cftc_report']['source']}")
    print(f"   净持仓: {capital_flow['cftc_report']['net_position']}")
    if 'Mock' in capital_flow['cftc_report']['source']:
        print(f"   ⚠️  状态: 模拟数据")
    else:
        print(f"   ✅ 状态: 真实数据")
elif 'cftc' in capital_flow:
    cftc = capital_flow['cftc']
    print(f"   来源: {cftc.get('source', 'Unknown')}")
    if 'speculative' in cftc:
        print(f"   投机净头寸: {cftc['speculative']['net']}")
    if 'Mock' in cftc.get('source', ''):
        print(f"   ⚠️  状态: 模拟数据")
    else:
        print(f"   ✅ 状态: 真实数据")
else:
    print(f"   ⚠️  数据不可用")

print(f"\n📊 持仓量:")
if 'open_interest' in capital_flow:
    oi = capital_flow['open_interest']
    if isinstance(oi, dict) and 'source' in oi:
        print(f"   来源: {oi['source']}")
        print(f"   最新持仓量: {oi['latest_value']}")
        if 'Mock' in oi['source']:
            print(f"   ⚠️  状态: 模拟数据")
        else:
            print(f"   ✅ 状态: 真实数据")
    else:
        print(f"   数据类型: {type(oi)}")
        print(f"   ⚠️  状态: 数据格式异常")
else:
    print(f"   ⚠️  数据不可用")

# 5. 新闻情绪数据
print(f"\n【新闻情绪数据】")
news = enhanced_data.get('news', {})

if 'overall_sentiment' in news:
    print(f"\n📊 新闻情绪:")
    print(f"   来源: {news['overall_sentiment']['source']}")
    print(f"   情绪分数: {news['overall_sentiment']['sentiment_score']}")
    print(f"   情绪倾向: {news['overall_sentiment']['sentiment']}")
    print(f"   新闻数量: {len(news.get('articles', []))}")
    if 'Mock' in news['overall_sentiment']['source']:
        print(f"   ⚠️  状态: 模拟数据")
    else:
        print(f"   ✅ 状态: 真实数据")
elif 'news_sentiment' in enhanced_data:
    news_sentiment = enhanced_data['news_sentiment']
    print(f"\n📊 新闻情绪:")
    print(f"   整体情绪: {news_sentiment.get('overall_sentiment', 'Unknown')}")
    print(f"   情绪分数: {news_sentiment.get('overall_sentiment_score', 0)}")
    print(f"   新闻数量: {len(news_sentiment.get('articles', []))}")
    print(f"   ⚠️  状态: 数据格式异常")
else:
    print(f"\n📊 新闻情绪:")
    print(f"   ⚠️  数据不可用")

# 6. 风险信号生成
print(f"\n【风险信号生成】")
print("-"*80)

risk_signals = enhanced_data['risk_signals']
print(f"生成风险信号数量: {len(risk_signals)}")

for i, signal in enumerate(risk_signals, 1):
    level = '🔴 高风险' if signal['level'] == 'high' else '🟡 中风险'
    print(f"\n  {i}. {level}")
    print(f"     {signal['message']}")

# 分析风险信号基于的数据
print(f"\n  风险信号基于的数据:")
if any('Mock' in macro['dollar_index']['source'] for macro in [enhanced_data['macro']]):
    print(f"     ⚠️  美元指数: 基于模拟数据")
else:
    print(f"     ✅ 美元指数: 基于真实数据")

if any('Mock' in macro['pmi']['source'] for macro in [enhanced_data['macro']]):
    print(f"     ⚠️  PMI: 基于模拟数据")
else:
    print(f"     ✅ PMI: 基于真实数据")

if any('Mock' in macro['vix']['source'] for macro in [enhanced_data['macro']]):
    print(f"     ⚠️  VIX: 基于模拟数据")
else:
    print(f"     ✅ VIX: 基于真实数据")

# 7. 统计数据真实性
print(f"\n【数据真实性统计】")
print("-"*80)

data_sources = [
    ('美元指数', macro['dollar_index']['source']),
    ('PMI', macro['pmi']['source']),
    ('联邦利率', macro['interest_rate']['source']),
    ('VIX', macro['vix']['source'])
]

# 添加资金流向数据
if 'cftc_report' in capital_flow:
    data_sources.append(('CFTC持仓', capital_flow['cftc_report']['source']))
elif 'cftc' in capital_flow:
    data_sources.append(('CFTC持仓', capital_flow['cftc'].get('source', 'Unknown')))

if 'open_interest' in capital_flow and isinstance(capital_flow['open_interest'], dict):
    data_sources.append(('持仓量', capital_flow['open_interest'].get('source', 'Unknown')))

# 添加新闻情绪数据
if 'overall_sentiment' in news:
    data_sources.append(('新闻情绪', news['overall_sentiment']['source']))
elif 'news_sentiment' in enhanced_data:
    data_sources.append(('新闻情绪', enhanced_data['news_sentiment'].get('source', 'Unknown')))

real_count = sum(1 for _, source in data_sources if 'Mock' not in source)
mock_count = sum(1 for _, source in data_sources if 'Mock' in source)

print(f"\n✅ 真实数据: {real_count}/{len(data_sources)}")
for name, source in data_sources:
    if 'Mock' not in source:
        print(f"   ✓ {name}: {source}")

print(f"\n⚠️  模拟数据: {mock_count}/{len(data_sources)}")
for name, source in data_sources:
    if 'Mock' in source:
        print(f"   ✗ {name}: {source}")

# 8. 结论
print(f"\n【结论】")
print("-"*80)

if real_count == len(data_sources):
    print("✅ 所有数据都是真实数据!")
    print("   增强数据调整完全基于真实市场数据。")
elif real_count > 0:
    print(f"⚠️  部分数据是真实的 ({real_count}/{len(data_sources)})")
    print(f"   真实数据用于: {[name for name, source in data_sources if 'Mock' not in source]}")
    print(f"   模拟数据用于: {[name for name, source in data_sources if 'Mock' in source]}")
else:
    print("❌ 所有数据都是模拟数据!")
    print("   增强数据调整不基于真实市场数据。")

print("\n" + "="*80)
