"""
分析预测与实际差异的原因
"""

from data.real_data import get_real_copper_data
import pandas as pd

# 获取最近数据
df = get_real_copper_data(days=20)

print('=' * 60)
print('最近15天铜价数据')
print('=' * 60)
print(df[['date', 'open', 'high', 'low', 'close']].tail(15).to_string(index=False))

# 计算收益率
df = df.sort_values('date')
df['returns'] = df['close'].pct_change() * 100
df['returns_5d'] = df['close'].pct_change(5) * 100

print('\n' + '=' * 60)
print('日收益率')
print('=' * 60)
print(df[['date', 'close', 'returns']].tail(15).to_string(index=False))

print('\n' + '=' * 60)
print('5日收益率')
print('=' * 60)
print(df[['date', 'close', 'returns_5d']].tail(15).to_string(index=False))

# 计算技术指标
df['ma5'] = df['close'].rolling(5).mean()
df['ma10'] = df['close'].rolling(10).mean()
df['ma20'] = df['close'].rolling(20).mean()

# 计算RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# 计算波动率
df['volatility_20'] = df['returns'].rolling(20).std()

print('\n' + '=' * 60)
print('技术指标 (最新10天)')
print('=' * 60)
cols = ['date', 'close', 'ma5', 'ma20', 'rsi', 'volatility_20', 'returns']
print(df[cols].tail(10).to_string(index=False))

print('\n' + '=' * 60)
print('关键指标分析')
print('=' * 60)
latest = df.iloc[-1]
prev1 = df.iloc[-2]
prev2 = df.iloc[-3]

print(f'最新价格 (T): {latest["close"]:,.2f}')
print(f'昨日价格 (T-1): {prev1["close"]:,.2f}')
print(f'前日价格 (T-2): {prev2["close"]:,.2f}')
print()
print(f'昨日收益率: {prev1["returns"]:.2f}%')
print(f'今日收益率: {latest["returns"]:.2f}%')
print(f'5日收益率: {latest["returns_5d"]:.2f}%')
print()
print(f'5日均线: {latest["ma5"]:,.2f}')
print(f'20日均线: {latest["ma20"]:,.2f}')
print(f'RSI(14): {latest["rsi"]:.2f}')
print(f'20日波动率: {latest["volatility_20"]:.2f}%')
print()

# 分析价格趋势
if latest['close'] > latest['ma5']:
    trend_short = '上涨'
else:
    trend_short = '下跌'

if latest['close'] > latest['ma20']:
    trend_long = '上涨'
else:
    trend_long = '下跌'

print('趋势判断:')
print(f'短期趋势 (vs MA5): {trend_short}')
print(f'中期趋势 (vs MA20): {trend_long}')
print()

# RSI判断
if latest['rsi'] > 70:
    rsi_status = '超买'
elif latest['rsi'] < 30:
    rsi_status = '超卖'
else:
    rsi_status = '正常'
print(f'RSI状态: {rsi_status}')

# 分析下跌原因
print('\n' + '=' * 60)
print('预测与实际差异分析')
print('=' * 60)

print('模型预测上涨的可能原因:')
print('1. 历史模式: 模型可能学习到类似技术形态后通常会反弹')
print('2. 均线支撑: 价格接近支撑位,预期反弹')
print('3. 动量指标: 可能出现短期超卖信号')
print()
print('实际连续下跌的可能原因:')
print('1. 突发消息: 市场出现模型未训练到的利空消息')
print('2. 宏观变化: 美元指数、PMI等关键因子突然变化')
print('3. 情绪转变: 市场情绪从乐观转为悲观')
print('4. 技术破位: 跌破关键支撑位,引发止损盘')
print()

# 检查是否存在关键支撑位跌破
prev_high_5 = df['high'].tail(5).max()
prev_low_5 = df['low'].tail(5).min()

print(f'近5日最高: {prev_high_5:,.2f}')
print(f'近5日最低: {prev_low_5:,.2f}')
print(f'当前价格: {latest["close"]:,.2f}')
print()

if latest['close'] < prev_low_5:
    print('⚠️ 价格已跌破近5日最低点,技术破位')
else:
    print('✓ 价格仍在近5日区间内')
