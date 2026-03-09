from data.enhanced_data_sources import EnhancedDataIntegration
from data.real_enhanced_data import RealEnhancedDataManager
import json

print("="*70)
print("对比增强数据 vs 集成系统数据")
print("="*70)

# 1. 测试增强数据预测的数据源
print("\n【增强数据预测】(enhanced_data_sources.py)")
enhanced_integration = EnhancedDataIntegration()
enhanced_data = enhanced_integration.get_comprehensive_data()

enhanced_macro = enhanced_data['macro']
print(f"  美元指数: {enhanced_macro['dollar_index']['value']} (来源: {enhanced_macro['dollar_index']['source']})")
print(f"  VIX: {enhanced_macro['vix']['value']} (来源: {enhanced_macro['vix']['source']})")
print(f"  PMI: {enhanced_macro['pmi']['value']} (来源: {enhanced_macro['pmi']['source']})")
print(f"  联邦利率: {enhanced_macro['interest_rate']['federal_funds_rate']}% (来源: {enhanced_macro['interest_rate']['source']})")

# 2. 测试集成系统预测的数据源
print("\n【集成系统预测】(real_enhanced_data.py)")
real_integration = RealEnhancedDataManager()
real_data = real_integration.get_all_data()

real_macro = real_data['macro']
print(f"  美元指数: {real_macro['dollar_index']['value']} (来源: {real_macro['dollar_index']['source']})")
print(f"  VIX: {real_macro['vix']['value']} (来源: {real_macro['vix']['source']})")
print(f"  PMI: {real_macro['pmi']['value']} (来源: {real_macro['pmi']['source']})")
print(f"  联邦利率: {real_macro['interest_rate']['federal_funds_rate']}% (来源: {real_macro['interest_rate']['source']})")

# 3. 对比分析
print("\n" + "="*70)
print("【数据真实性分析】")
print("="*70)

enhanced_sources = {
    '美元指数': enhanced_macro['dollar_index']['source'],
    'VIX': enhanced_macro['vix']['source'],
    'PMI': enhanced_macro['pmi']['source'],
    '联邦利率': enhanced_macro['interest_rate']['source']
}

real_sources = {
    '美元指数': real_macro['dollar_index']['source'],
    'VIX': real_macro['vix']['source'],
    'PMI': real_macro['pmi']['source'],
    '联邦利率': real_macro['interest_rate']['source']
}

for key in ['美元指数', 'VIX', 'PMI', '联邦利率']:
    enhanced_source = enhanced_sources[key]
    real_source = real_sources[key]

    enhanced_status = "✅ 真实" if "Mock" not in enhanced_source else "❌ 模拟"
    real_status = "✅ 真实" if "Mock" not in real_source and "Fallback" not in real_source and "基于" not in real_source else "❌ 模拟"

    print(f"\n{key}:")
    print(f"  增强数据: {enhanced_status} - {enhanced_source}")
    print(f"  集成系统: {real_status} - {real_source}")

print("\n" + "="*70)
