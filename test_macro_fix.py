#!/usr/bin/env python3
"""
测试宏观因子模型修复
"""

from models.advanced_models import MacroFactorModel, MacroConfig
from data.data_sources import MockDataSource
import pandas as pd
import numpy as np

# 生成测试数据
mock_source = MockDataSource()
data = mock_source.fetch_copper_price(start_date='2023-01-01', end_date='2024-12-31')

# 训练宏观因子模型
config = MacroConfig()
model = MacroFactorModel(config)
model.train(data)

# 预测7天
pred7 = model.predict(data, horizon=7)
print('='*60)
print('宏观因子模型预测结果（修复后）')
print('='*60)
print(f'\n当前价格: ¥{pred7["current_price"]:,.2f}')
print(f'预测价格(7天): ¥{pred7["predicted_price"]:,.2f}')
print(f'预测收益率: {pred7["predicted_return"]:+.2f}%')
print(f'预测周期: {pred7["horizon_days"]}天')
print(f'趋势: {pred7["trend"]}')

# 预测30天
pred = model.predict(data, horizon=30)
print(f'\n预测价格(30天): ¥{pred["predicted_price"]:,.2f}')
print(f'预测收益率: {pred["predicted_return"]:+.2f}%')
print(f'预测周期: {pred["horizon_days"]}天')
print(f'趋势: {pred["trend"]}')

# 预测90天
pred90 = model.predict(data, horizon=90)
print(f'\n预测价格(90天): ¥{pred90["predicted_price"]:,.2f}')
print(f'预测收益率: {pred90["predicted_return"]:+.2f}%')
print(f'预测周期: {pred90["horizon_days"]}天')
print(f'趋势: {pred90["trend"]}')
print('='*60)
