"""
深入分析预测误差原因
"""

import sys
import pandas as pd
import numpy as np

# 添加路径
sys.path.append('/Users/ydy/CodeBuddy/20260227142050/copper_prediction_v2')

from data.real_data import RealDataManager
from models.copper_model_v2 import CopperPriceModel, FeatureEngineer

# 获取数据
print('=' * 70)
print('步骤1: 获取最近数据')
print('=' * 70)
data_mgr = RealDataManager()
df = data_mgr.get_full_data(days=60)
print(f"数据条数: {len(df)}")
print(f"日期范围: {df['date'].min()} ~ {df['date'].max()}")
print(f"最新价格: {df.iloc[-1]['close']:,.2f}")

# 显示最近10天数据
print('\n' + '=' * 70)
print('最近10天价格')
print('=' * 70)
print(df[['date', 'open', 'high', 'low', 'close', 'volume']].tail(10).to_string(index=False))

# 计算收益率
df = df.sort_values('date').reset_index(drop=True)
df['returns'] = df['close'].pct_change() * 100
df['returns_5d'] = df['close'].pct_change(5) * 100

print('\n' + '=' * 70)
print('日收益率和5日收益率')
print('=' * 70)
print(df[['date', 'close', 'returns', 'returns_5d']].tail(10).to_string(index=False))

# 查看最近2天的下跌情况
print('\n' + '=' * 70)
print('最近2天下跌分析')
print('=' * 70)
latest = df.iloc[-1]
prev1 = df.iloc[-2]
prev2 = df.iloc[-3]

print(f"T-2日 (3天前): {prev2['date']}")
print(f"  收盘价: {prev2['close']:,.2f}")
print(f"  收益率: {prev2['returns']:.2f}%")
print()
print(f"T-1日 (2天前): {prev1['date']}")
print(f"  收盘价: {prev1['close']:,.2f}")
print(f"  收益率: {prev1['returns']:.2f}%")
print()
print(f"T日 (最新): {latest['date']}")
print(f"  收盘价: {latest['close']:,.2f}")
print(f"  收益率: {latest['returns']:.2f}%")
print()

# 2天累计跌幅
two_day_drop = (latest['close'] - prev2['close']) / prev2['close'] * 100
print(f'2日累计跌幅: {two_day_drop:.2f}%')

# 初始化模型
print('\n' + '=' * 70)
print('步骤2: 训练模型并分析特征')
print('=' * 70)

model = CopperPriceModel()
feature_eng = FeatureEngineer()

# 创建特征
df_features = feature_eng.create_features(df)
print(f"\n生成特征数量: {len(feature_eng.feature_names)}")
print(f"前10个特征: {feature_eng.feature_names[:10]}")

# 查看最新几天的关键特征
print('\n' + '=' * 70)
print('最近3天的关键特征')
print('=' * 70)
key_features = ['date', 'close', 'returns_1d', 'rsi_14', 'ma_5', 'ma_20', 
                'macd', 'macd_hist', 'bb_position', 'volume_ratio']
available_features = [f for f in key_features if f in df_features.columns]
print(df_features[available_features].tail(3).to_string(index=False))

# 分析技术指标状态
print('\n' + '=' * 70)
print('技术指标状态分析')
print('=' * 70)

# RSI
latest_rsi = df_features.iloc[-1]['rsi_14']
if latest_rsi > 70:
    rsi_status = '🔴 超买'
elif latest_rsi < 30:
    rsi_status = '🟢 超卖'
else:
    rsi_status = '🟡 正常'
print(f"RSI(14): {latest_rsi:.2f} - {rsi_status}")

# 均线
latest_price = latest['close']
ma5 = df_features.iloc[-1]['ma_5']
ma20 = df_features.iloc[-1]['ma_20']
print(f"\n当前价格: {latest_price:,.2f}")
print(f"5日均线: {ma5:,.2f} ({'高于' if latest_price > ma5 else '低于'})")
print(f"20日均线: {ma20:,.2f} ({'高于' if latest_price > ma20 else '低于'})")

# MACD
macd = df_features.iloc[-1]['macd']
macd_hist = df_features.iloc[-1]['macd_hist']
print(f"\nMACD: {macd:.2f}")
print(f"MACD直方图: {macd_hist:.2f} ({'看涨' if macd_hist > 0 else '看跌'})")

# 布林带
bb_position = df_features.iloc[-1]['bb_position']
if bb_position > 0.8:
    bb_status = '🔴 接近上轨'
elif bb_position < 0.2:
    bb_status = '🟢 接近下轨'
else:
    bb_status = '🟡 中间位置'
print(f"\n布林带位置: {bb_position:.2f} - {bb_status}")

# 训练模型
print('\n' + '=' * 70)
print('步骤3: 训练模型')
print('=' * 70)

# 准备训练数据
df_features = df_features.dropna()
X = df_features[feature_eng.feature_names].values[:-1]  # 排除最后一行(无标签)
y = df_features['returns_1d'].values[1:]  # 对应下一日收益率

print(f"训练样本数: {len(X)}")
print(f"特征维度: {X.shape[1]}")

# 训练
model.train(X, y)

# 获取特征重要性
importance = model.get_feature_importance()
print('\n' + '=' * 70)
print('特征重要性 Top 10')
print('=' * 70)
for i, (feat, imp) in enumerate(importance[:10], 1):
    print(f"{i:2d}. {feat:30s} {imp:.6f}")

# 预测最新日期
print('\n' + '=' * 70)
print('步骤4: 预测分析')
print('=' * 70)

# 使用最新特征预测
latest_features = df_features[feature_eng.feature_names].iloc[-1].values.reshape(1, -1)
prediction = model.predict(latest_features)
print(f"预测收益率: {prediction[0]*100:.2f}%")
print(f"预测价格: {latest_price * (1 + prediction[0]):,.2f}")

# 分析SHAP值
try:
    import shap
    
    explainer = shap.TreeExplainer(model.model)
    shap_values = explainer.shap_values(latest_features)
    
    print('\n' + '=' * 70)
    print('SHAP值分析 - 预测上涨的原因')
    print('=' * 70)
    
    # 计算每个特征的SHAP值
    feature_importance = list(zip(feature_eng.feature_names, shap_values[0]))
    
    # 排序
    feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
    
    # 显示Top 10
    for i, (feat, shap_val) in enumerate(feature_importance[:10], 1):
        direction = '⬆️ 推动' if shap_val > 0 else '⬇️ 拖累'
        print(f"{i:2d}. {feat:25s} {shap_val:>+.6f} {direction}")
    
    # 正负向因素汇总
    positive = [(f, v) for f, v in feature_importance if v > 0]
    negative = [(f, v) for f, v in feature_importance if v < 0]
    
    print('\n正向驱动因素 (看涨):')
    for f, v in positive[:5]:
        print(f"  + {f}: {v:.6f}")
    
    print('\n负向拖累因素 (看跌):')
    for f, v in negative[:5]:
        print(f"  - {f}: {v:.6f}")
    
except ImportError:
    print("\nSHAP未安装,无法进行特征贡献分析")

# 分析预测错误原因
print('\n' + '=' * 70)
print('步骤5: 预测与实际差异原因分析')
print('=' * 70)

print("\n模型预测上涨的可能原因:")
print("1. 技术指标显示超卖:")
print(f"   - RSI({latest_rsi:.2f})可能处于超卖区域,预期反弹")
print(f"   - 价格可能在5日均线({ma5:,.2f})附近获得支撑")
print()
print("2. 历史模式匹配:")
print("   - 模型可能在历史数据中学习到类似形态后的反弹规律")
print("   - 近期下跌后反弹的概率在训练集中较高")
print()
print("3. 动量指标反转:")
print(f"   - MACD直方图({macd_hist:.2f})可能显示反转信号")
print()

print("实际连续下跌的可能原因:")
print("1. 突发利空消息:")
print("   - 宏观政策调整、地缘政治、经济数据不及预期等")
print("   - 这些消息在历史训练数据中可能不存在或样本很少")
print()
print("2. 技术破位:")
print("   - 跌破关键支撑位,引发技术性止损盘")
print("   - 支撑位失守后加速下跌")
print()
print("3. 市场情绪恶化:")
print("   - 投资者从乐观转为悲观")
print("   - 风险偏好下降,资金流出商品市场")
print()
print("4. 外部因素影响:")
print("   - 美元指数走强(铜以美元计价)")
print("   - 其他大宗商品联动下跌")
print("   - 股市下跌带动商品下跌")
print()

# 改进建议
print('\n' + '=' * 70)
print('步骤6: 改进建议')
print('=' * 70)

print("针对预测误差,可考虑以下改进:")
print()
print("1. 增强宏观因子监测:")
print("   - 实时跟踪美元指数、PMI、利率等关键指标")
print("   - 加入新闻情绪分析(如财经新闻)")
print()
print("2. 提升数据实时性:")
print("   - 使用分钟级或小时级数据")
print("   - 及时捕捉突发性利空")
print()
print("3. 情景预警系统:")
print("   - 识别历史相似的重大下跌事件")
print("   - 当出现类似情景时提高警惕")
print()
print("4. 模型融合优化:")
print("   - 动态调整各模型权重")
print("   - 基于近期表现选择最佳模型")
print()
print("5. 风险管理:")
print("   - 设置止损位,控制单次损失")
print("   - 不要完全依赖模型预测")
print("   - 结合基本面和宏观面综合判断")
