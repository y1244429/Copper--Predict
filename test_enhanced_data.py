"""
测试增强数据源模块
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.enhanced_data_sources import EnhancedDataIntegration
import json
from datetime import datetime

def test_enhanced_data():
    """测试增强数据获取"""
    print("\n" + "="*70)
    print("增强数据源测试")
    print("="*70)
    
    # 创建数据整合器
    integration = EnhancedDataIntegration()
    
    # 获取综合数据
    print("\n正在获取增强数据...")
    data = integration.get_comprehensive_data()
    
    # 打印摘要
    integration.print_summary(data)
    
    # 保存数据
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output_dir}/enhanced_data_{timestamp}.json"
    integration.save_to_file(data, output_file)
    
    print(f"\n✅ 数据已保存到: {output_file}")
    
    # 详细分析
    print("\n" + "="*70)
    print("详细分析")
    print("="*70)
    
    # 宏观指标分析
    macro = data['macro']
    print("\n【宏观指标深度分析】")
    
    # 判断风险等级
    risk_level = 0
    if macro['vix']['value'] > 30:
        risk_level += 2
    elif macro['vix']['value'] > 25:
        risk_level += 1
    
    if macro['pmi']['value'] < 45:
        risk_level += 2
    elif macro['pmi']['value'] < 50:
        risk_level += 1
    
    if macro['dollar_index']['value'] > 102:
        risk_level += 1
    
    risk_desc = '低' if risk_level == 0 else ('中' if risk_level <= 2 else '高')
    print(f"  综合风险等级: {risk_desc} (风险点数: {risk_level})")
    
    # 资金流向分析
    capital = data['capital_flow']
    print("\n【资金流向分析】")
    cftc = capital['cftc']
    commercial_net = cftc['commercial']['net']
    speculative_net = cftc['speculative']['net']
    
    if commercial_net < -50000:
        print(f"  商业头寸: 大幅做空 ({commercial_net:,} 手) → 基本面偏空")
    elif commercial_net > 50000:
        print(f"  商业头寸: 大幅做多 ({commercial_net:,} 手) → 基本面偏多")
    else:
        print(f"  商业头寸: 中性 ({commercial_net:,} 手)")
    
    if speculative_net < -50000:
        print(f"  投机头寸: 大幅做空 ({speculative_net:,} 手) → 情绪偏空")
    elif speculative_net > 50000:
        print(f"  投机头寸: 大幅做多 ({speculative_net:,} 手) → 情绪偏多")
    else:
        print(f"  投机头寸: 中性 ({speculative_net:,} 手)")
    
    # 新闻情绪分析
    news = data['news_sentiment']
    if 'error' not in news:
        print("\n【新闻情绪分析】")
        sentiment = news['overall_sentiment']
        score = news['overall_sentiment_score']
        
        if sentiment == 'positive':
            print(f"  整体情绪: 积极 ({score:.2f}) → 利多铜价")
        elif sentiment == 'negative':
            print(f"  整体情绪: 消极 ({score:.2f}) → 利空铜价")
        else:
            print(f"  整体情绪: 中性 ({score:.2f}) → 方向不明确")
        
        if news['has_emergency']:
            print(f"\n  ⚠️  突发事件 ({len(news['emergency_events'])}个):")
            for event in news['emergency_events'][:3]:
                print(f"    - {event['title']}")
    
    # 投资建议
    print("\n" + "="*70)
    print("综合投资建议")
    print("="*70)
    
    # 综合判断
    bullish_factors = 0
    bearish_factors = 0
    
    # 宏观因素
    if macro['pmi']['value'] > 50:
        bullish_factors += 1
    else:
        bearish_factors += 1
    
    if macro['dollar_index']['value'] < 100:
        bullish_factors += 1
    else:
        bearish_factors += 1
    
    if macro['vix']['value'] < 20:
        bullish_factors += 1
    else:
        bearish_factors += 1
    
    # 资金流向
    if commercial_net > 0:
        bullish_factors += 1
    else:
        bearish_factors += 1
    
    # 新闻情绪
    if news.get('overall_sentiment') == 'positive':
        bullish_factors += 1
    elif news.get('overall_sentiment') == 'negative':
        bearish_factors += 1
    
    # 风险信号
    if data['risk_signals']:
        bearish_factors += len(data['risk_signals'])
    
    print(f"\n  利多因素: {bullish_factors} 个")
    print(f"  利空因素: {bearish_factors} 个")
    
    if bullish_factors > bearish_factors * 1.5:
        recommendation = "强烈看多，建议积极做多"
        color = "🟢"
    elif bullish_factors > bearish_factors:
        recommendation = "偏向看多，建议适度做多"
        color = "🟢"
    elif bearish_factors > bullish_factors * 1.5:
        recommendation = "强烈看空，建议谨慎观望或适度做空"
        color = "🔴"
    elif bearish_factors > bullish_factors:
        recommendation = "偏向看空，建议谨慎观望"
        color = "🔴"
    else:
        recommendation = "多空交织，建议观望"
        color = "🟡"
    
    print(f"\n  {color} 综合建议: {recommendation}")
    
    # 风险提示
    if data['risk_signals']:
        print(f"\n  ⚠️  风险提示: 检测到 {len(data['risk_signals'])} 个风险信号，请重点关注")
    
    return data

if __name__ == '__main__':
    data = test_enhanced_data()
    
    print("\n" + "="*70)
    print("✅ 测试完成")
    print("="*70)
