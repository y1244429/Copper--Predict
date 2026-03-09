#!/usr/bin/env python3
"""
训练ARDL宏观模型和VAR基本面模型
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from main import CopperPredictionSystem

def main():
    print("="*80)
    print("训练ARDL宏观模型和VAR基本面模型")
    print("="*80)
    print()

    # 1. 创建系统实例
    print("步骤 1: 初始化预测系统...")
    system = CopperPredictionSystem(data_source="auto")

    # 2. 加载数据
    print("\n步骤 2: 加载训练数据...")
    print("使用最近2年的数据用于模型训练(更好的捕捉长期趋势和周期)...")
    system.load_data(days=730)

    # 3. 训练宏观因子模型(ARDL)
    print("\n" + "="*80)
    print("步骤 3: 训练ARDL宏观因子模型")
    print("="*80)
    print("模型类型: 自回归分布滞后模型(ARDL)")
    print("预测周期: 90天(3个月)")
    print("核心因子: 美元指数 | 中国PMI | 实际利率 | LME升贴水")
    print()
    macro_metrics = system.train_macro()

    if macro_metrics:
        print("\n✓ ARDL宏观模型训练成功!")
        print(f"  模型类型: {macro_metrics.get('model_type', 'ardl')}")
        print(f"  RMSE: {macro_metrics.get('rmse', 0):.4f}")
        print(f"  MAE: {macro_metrics.get('mae', 0):.4f}")
        print(f"  R²: {macro_metrics.get('r2', 0):.4f}")
    else:
        print("\n✗ ARDL宏观模型训练失败!")

    # 4. 训练基本面模型(VAR)
    print("\n" + "="*80)
    print("步骤 4: 训练VAR基本面模型")
    print("="*80)
    print("模型类型: 向量自回归模型(VAR)")
    print("预测周期: 180天(6个月)")
    print("核心因子: 供需平衡 | 成本支撑 | 矿山干扰")
    print()
    fundamental_metrics = system.train_fundamental()

    if fundamental_metrics:
        print("\n✓ VAR基本面模型训练成功!")
        print(f"  模型类型: {fundamental_metrics.get('model_type', 'var')}")
        print(f"  RMSE: {fundamental_metrics.get('rmse', 0):.4f}")
        print(f"  MAE: {fundamental_metrics.get('mae', 0):.4f}")
        print(f"  R²: {fundamental_metrics.get('r2', 0):.4f}")
    else:
        print("\n✗ VAR基本面模型训练失败!")

    # 5. 生成预测报告
    print("\n" + "="*80)
    print("步骤 5: 生成多模型预测报告")
    print("="*80)
    print()

    # 生成文本和HTML报告
    report = system.generate_report(include_xgb=False)

    # 6. 尝试生成PPT报告
    print("\n" + "="*80)
    print("步骤 6: 尝试生成PPT报告")
    print("="*80)
    print()
    try:
        ppt_file = system.generate_ppt_report(include_xgb=False)
        if ppt_file:
            print(f"✓ PPT报告已生成")
        else:
            print("✗ PPT报告生成失败或跳过")
    except Exception as e:
        print(f"✗ PPT报告生成失败: {e}")
        print("  (可能需要安装python-pptx: pip install python-pptx)")

    # 7. 总结
    print("\n" + "="*80)
    print("训练完成总结")
    print("="*80)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("已训练模型:")
    print(f"  1. ARDL宏观因子模型: {'✓ 训练成功' if macro_metrics else '✗ 训练失败'}")
    print(f"  2. VAR基本面模型: {'✓ 训练成功' if fundamental_metrics else '✗ 训练失败'}")
    print()
    print("已生成报告:")
    print(f"  - 文本报告: report_*.txt")
    print(f"  - HTML报告: report_*.html")
    print(f"  - PPT报告: report_*.pptx (如果成功)")
    print()
    print("="*80)

    return macro_metrics, fundamental_metrics

if __name__ == '__main__':
    try:
        macro_metrics, fundamental_metrics = main()

        # 如果两个模型都训练成功,返回成功状态
        if macro_metrics and fundamental_metrics:
            print("\n✓ 所有模型训练完成!")
            sys.exit(0)
        else:
            print("\n⚠ 部分模型训练失败,请检查日志")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ 训练过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
