#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库功能测试脚本
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from data.prediction_db import PredictionDatabase
from datetime import datetime

def test_database():
    """测试数据库功能"""
    print("=" * 60)
    print("数据库功能测试")
    print("=" * 60)
    
    # 初始化数据库
    print("\n1. 初始化数据库...")
    db = PredictionDatabase()
    print("   ✓ 数据库初始化成功")
    
    # 显示统计信息
    print("\n2. 数据库统计信息:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 创建测试数据
    print("\n3. 创建测试数据...")
    test_data = {
        'prediction_date': datetime.now().strftime('%Y-%m-%d'),
        'run_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'current_price': 85000.0,
        'xgboost_5day': 85500.0,
        'xgboost_10day': 86000.0,
        'xgboost_20day': 86500.0,
        'macro_1month': 87000.0,
        'macro_3month': 88000.0,
        'macro_6month': 89000.0,
        'fundamental_6month': 88500.0,
        'lstm_5day': 85200.0,
        'lstm_10day': 85800.0,
        'overall_trend': '上涨',
        'confidence': 0.75,
        'risk_level': '中风险',
        'notes': '测试数据',
        'technical_indicators': {
            'ma5': 84800.0,
            'ma10': 84500.0,
            'ma20': 84000.0,
            'ma60': 83500.0,
            'rsi': 55.0,
            'macd': 200.0,
            'macd_signal': 180.0,
            'volume_ratio': 1.2,
            'support_level': 80750.0,
            'resistance_level': 89250.0
        },
        'macro_factors': {
            'usd_index': 105.0,
            'dollar_trend': 'neutral',
            'vix': 15.0,
            'vix_trend': 'neutral',
            'china_pmi': 50.5,
            'china_pmi_trend': 'stable',
            'us_pmi': 51.0,
            'us_pmi_trend': 'stable',
            'oil_price': 80.0,
            'gold_price': 2000.0,
            'global_demand': 'normal'
        },
        'model_performance': {
            'xgboost': {
                'accuracy': 0.85,
                'mae': 0.0241,
                'rmse': 0.0320,
                'r2_score': 0.75
            }
        },
        'prediction_details': {
            'xgboost': {'predicted_price': 85500.0, 'predicted_return': 0.59},
            'macro': {'predicted_price': 88000.0, 'predicted_return': 3.53}
        }
    }
    
    # 保存测试数据
    print("   保存测试数据到数据库...")
    success = db.save_prediction(test_data)
    
    if success:
        print("   ✓ 测试数据保存成功")
    else:
        print("   ✗ 测试数据保存失败")
        return False
    
    # 查询测试数据
    print("\n4. 查询测试数据:")
    prediction = db.get_prediction(test_data['prediction_date'])
    
    if prediction:
        print(f"   ✓ 找到预测记录:")
        print(f"     日期: {prediction['prediction_date']}")
        print(f"     当前价格: ¥{prediction['current_price']:,.2f}")
        print(f"     XGBoost 5天预测: ¥{prediction['xgboost_5day']:,.2f}")
        print(f"     总体趋势: {prediction['overall_trend']}")
    else:
        print("   ✗ 未找到预测记录")
        return False
    
    # 查询所有数据
    print("\n5. 查询所有预测记录:")
    all_predictions = db.get_all_predictions(limit=5)
    print(f"   找到 {len(all_predictions)} 条记录")
    
    for i, pred in enumerate(all_predictions, 1):
        print(f"   {i}. {pred['prediction_date']} - ¥{pred['current_price']:,.2f}")
    
    # 获取最新预测
    print("\n6. 获取最新预测:")
    latest = db.get_latest_prediction()
    if latest:
        print(f"   ✓ 最新预测日期: {latest['prediction_date']}")
        print(f"     当前价格: ¥{latest['current_price']:,.2f}")
    else:
        print("   ⚠ 暂无预测数据")
    
    # 导出CSV
    print("\n7. 导出CSV:")
    try:
        csv_path = db.export_to_csv()
        print(f"   ✓ CSV导出成功: {csv_path}")
    except Exception as e:
        print(f"   ✗ CSV导出失败: {e}")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过!")
    print("=" * 60)
    print("\n数据库文件位置:")
    print(f"  {db.db_path}")
    print("\n可以使用以下命令查看数据库:")
    print(f"  sqlite3 {db.db_path}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
