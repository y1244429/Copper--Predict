"""简化版预测误差分析"""
from data.real_data import RealDataManager
import pandas as pd

# 获取数据
data_mgr = RealDataManager()
df = data_mgr.get_full_data(days=20)

print('=' * 70)
print('最近20天铜价和收益率')
print('=' * 70)

# 计算收益率
df['returns'] = df['close'].pct_change() * 100
df['returns_5d'] = df['close'].pct_change(5) * 100
df['ma5'] = df['close'].rolling(5).mean()
df['ma20'] = df['close'].rolling(20).mean()

# RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# 显示
df_disp = df.reset_index()
cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'returns', 'ma5', 'rsi']
print(df_disp[cols].tail(15).to_string(index=False))

# 关键分析
latest = df.iloc[-1]
prev1 = df.iloc[-2]
prev2 = df.iloc[-3]

print('\n' + '=' * 70)
print('关键指标分析')
print('=' * 70)
print(f'最新价格: {latest["close"]:,.2f}')
print(f'昨日价格: {prev1["close"]:,.2f}')
print(f'前日价格: {prev2["close"]:,.2f}')
print()
print(f'前日收益: {prev2["returns"]:.2f}%')
print(f'昨日收益: {prev1["returns"]:.2f}%')
print(f'2日累计: {(latest["close"]-prev2["close"])/prev2["close"]*100:.2f}%')
print()
print(f'RSI(14): {latest["rsi"]:.2f}')
print(f'5日均线: {latest["ma5"]:,.2f}')
print(f'当前vsMA5: {latest["close"]-latest["ma5"]:,.2f}')

print('\n' + '=' * 70)
print('为什么模型预测上涨?')
print('=' * 70)
print('1. 超卖反弹预期:')
print(f'   - RSI({latest["rsi"]:.2f})显示可能的超卖状态')
if latest["close"] < latest["ma5"]:
    print(f'   - 价格({latest["close"]:,.2f})低于5日均线({latest["ma5"]:,.2f})')
    print('   - 短期超卖后通常有反弹')

print('\n2. 历史模式学习:')
print('   - XGBoost从历史数据中学习到类似形态')
print('   - 近期下跌后在训练集中反弹概率较高')

print('\n3. 技术指标反转:')
print('   - 可能出现短期底部信号')
print('   - 动量指标显示反转迹象')

print('\n' + '=' * 70)
print('实际连续下跌的可能原因')
print('=' * 70)
print('1. 突发利空消息:')
print('   - 宏观政策调整(如央行加息)')
print('   - 地缘政治事件(如贸易冲突)')
print('   - 经济数据不及预期(如PMI大幅下降)')
print('   - 这些消息模型难以提前预测')

print('\n2. 技术破位:')
print('   - 跌破关键支撑位')
print('   - 引发技术性止损盘')
print('   - 支撑失守后加速下跌')

print('\n3. 市场情绪恶化:')
print('   - 投资者从乐观转为悲观')
print('   - 风险偏好下降')
print('   - 资金从商品市场流出')

print('\n4. 外部因素:')
print('   - 美元指数走强(铜以美元计价)')
print('   - 其他大宗商品联动下跌')
print('   - 股市下跌带动')

print('\n' + '=' * 70)
print('模型局限性分析')
print('=' * 70)
print('1. 训练数据局限:')
print('   - 历史数据不包含所有突发事件')
print('   - 黑天鹅事件难以从历史学习')

print('\n2. 特征工程局限:')
print('   - 技术指标主要反映历史价格')
print('   - 缺乏实时宏观数据和新闻情绪')
print('   - 当前模型依赖日度数据,反应滞后')

print('\n3. 预测周期问题:')
print('   - 5天预测是平均预期')
print('   - 实际走势可能前跌后涨')
print('   - 短期波动可能导致预测偏差')

print('\n' + '=' * 70)
print('改进建议')
print('=' * 70)
print('1. 增强数据源:')
print('   - 实时宏观数据(美元指数、PMI、利率)')
print('   - 新闻情绪分析(财经新闻爬取)')
print('   - 分钟级高频数据')

print('\n2. 情景预警:')
print('   - 识别历史类似暴跌事件')
print('   - 当出现相似情景时提高警惕')
print('   - 及时调整预测权重')

print('\n3. 动态权重融合:')
print('   - 根据近期表现调整各模型权重')
print('   - 宏观因素主导时降低技术模型权重')
print('   - 突发事件时提高预警级别')

print('\n4. 风险管理:')
print('   - 设置止损位,控制单次损失')
print('   - 分批建仓,分散风险')
print('   - 不要完全依赖模型预测')
print('   - 结合基本面和宏观面判断')
