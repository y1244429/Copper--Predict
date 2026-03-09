import sys
import pandas as pd
sys.path.append('.')

from data.inventory_data import get_inventory_source

# 测试库存数据获取
print('=== 测试库存数据获取 ===')
manager = get_inventory_source('composite')
data = manager.get_inventory_data()

print(f'数据源: {data["source"]}')
print(f'数据完整性: {data["metadata"]["data_completeness"]}')
print(f'\n交易所数据状态:')
for exchange, status in data['data_status'].items():
    print(f'  {exchange}: {"可用" if status["available"] else "不可用"}')
    if not status['available']:
        print(f'    原因: {status["reason"]}')

print(f'\nSHFE库存数据: {data["exchanges"]["SHFE"]}')
print(f'\n汇总数据:')
print(f'  SHFE库存: {data["summary"]["shfe_inventory"]}')
print(f'  LME库存: {data["summary"]["lme_inventory"]}')
print(f'  COMEX库存: {data["summary"]["comex_inventory"]}')

# 测试历史数据
print('\n\n=== 测试历史库存数据 ===')
history = manager.get_historical_data(days=10)

print(f'历史数据形状: {history.shape}')
print(f'\n数据可用性统计:')
print(f'  LME数据可用: {history["lme_data_available"].sum()} 天')
print(f'  COMEX数据可用: {history["comex_data_available"].sum()} 天')
print(f'  SHFE数据可用: {history["shfe_data_available"].sum()} 天')

print(f'\nSHFE库存最近10天:')
for i in range(min(10, len(history))):
    date = history.index[i].strftime('%Y-%m-%d')
    inv = history['shfe_inventory'].iloc[i]
    status = '✓' if pd.notna(inv) else '✗'
    print(f'  {date}: {status} {inv if pd.notna(inv) else "缺失"}')

# 测试注销仓单占比
print('\n\n=== 测试注销仓单占比变化 ===')
warrant_data = manager.get_warrant_cancel_change(days=7)
print(f'数据可用: {warrant_data.get("available", False)}')
if not warrant_data.get('available'):
    print(f'错误: {warrant_data.get("error")}')
    print(f'数据源: {warrant_data.get("data_source")}')
    print(f'指标名称: {warrant_data.get("indicator_name")}')
    print(f'备注: {warrant_data.get("note")}')
