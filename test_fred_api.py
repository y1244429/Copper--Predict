from data.enhanced_data_sources import EnhancedDataIntegration
import json

# 测试增强数据获取
integration = EnhancedDataIntegration()
data = integration.get_comprehensive_data()

print('='*70)
print('测试 FRED API Key 配置')
print('='*70)

# 检查宏观数据
macro = data['macro']
print(f'\n【宏观数据】')
print(f'  美元指数: {macro["dollar_index"]["value"]} (来源: {macro["dollar_index"]["source"]})')
print(f'  PMI: {macro["pmi"]["value"]} (来源: {macro["pmi"]["source"]})')
print(f'  联邦利率: {macro["interest_rate"]["federal_funds_rate"]}% (来源: {macro["interest_rate"]["source"]})')
print(f'  VIX: {macro["vix"]["value"]} (来源: {macro["vix"]["source"]})')

# 检查数据来源
print(f'\n【数据来源】')
if 'Mock' in macro['dollar_index']['source']:
    print('  ❌ 美元指数: 模拟数据')
else:
    print('  ✅ 美元指数: 真实数据')

if 'Mock' in macro['pmi']['source']:
    print('  ❌ PMI: 模拟数据')
else:
    print('  ✅ PMI: 真实数据')

print(f'\n【风险信号】({len(data["risk_signals"])}个)')
for i, signal in enumerate(data['risk_signals'], 1):
    level = '🔴' if signal['level'] == 'high' else '🟡'
    print(f'  {i}. {level} {signal["message"]}')

print('\n' + '='*70)
