#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试基本面模型预测结果对比
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 导入模块
from data.real_data import RealDataManager
from models.advanced_models import FundamentalModel, FundamentalConfig

def test_main_system():
    """测试main.py系统中的基本面模型"""
    print("="*60)
    print("测试 main.py 系统中的基本面模型")
    print("="*60)

    # 获取数据
    data_mgr = RealDataManager()
    end_date = datetime.now().strftime("%Y-%m-%d")
    current_data = data_mgr.get_full_data(days=365, end_date=end_date)
    print(f"数据量: {len(current_data)}")
    print(f"日期范围: {current_data.index[0].date()} ~ {current_data.index[-1].date()}")
    print(f"当前价格: ¥{current_data['close'].iloc[-1]:,.2f}")

    # 创建并训练基本面模型
    config = FundamentalConfig()
    fund_model = FundamentalModel(config)
    fund_model.train(current_data)

    # 使用180天预测
    fund_pred = fund_model.predict(current_data, horizon=180)
    print(f"\n基本面模型预测 (180天): ¥{fund_pred['predicted_price']:,.2f} ({fund_pred['predicted_return']:+.2f}%)")

    return fund_pred['predicted_price']

def test_integrated_system():
    """测试run_integrated_prediction.py系统中的基本面模型"""
    print("\n" + "="*60)
    print("测试 run_integrated_prediction.py 系统中的基本面模型")
    print("="*60)

    from run_integrated_prediction import IntegratedPredictionSystem

    # 创建集成预测系统
    system = IntegratedPredictionSystem()

    # 获取数据
    current_data = system.data_mgr.get_full_data(days=365)
    print(f"数据量: {len(current_data)}")
    print(f"日期范围: {current_data.index[0].date()} ~ {current_data.index[-1].date()}")
    print(f"当前价格: ¥{current_data['close'].iloc[-1]:,.2f}")

    # 训练并预测基本面模型
    system.fund_model.train(current_data)
    fund_pred = system.fund_model.predict(current_data, horizon=180)
    print(f"\n基本面模型预测 (180天): ¥{fund_pred['predicted_price']:,.2f} ({fund_pred['predicted_return']:+.2f}%)")

    return fund_pred['predicted_price']

if __name__ == '__main__':
    price1 = test_main_system()
    price2 = test_integrated_system()

    print("\n" + "="*60)
    print("对比结果")
    print("="*60)
    print(f"main.py 系统: ¥{price1:,.2f}")
    print(f"run_integrated_prediction.py 系统: ¥{price2:,.2f}")
    print(f"差异: ¥{abs(price1 - price2):,.2f}")
    print(f"差异百分比: {abs(price1 - price2) / price1 * 100:.2f}%")

    if abs(price1 - price2) < 0.01:
        print("\n✓ 两个系统的预测结果一致")
    else:
        print("\n✗ 两个系统的预测结果不一致，需要检查原因")
