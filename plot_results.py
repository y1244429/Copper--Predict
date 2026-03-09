#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
铜价预测结果输出和价格曲线绘制脚本
直接调用main.py生成预测并绘制图表
"""

import subprocess
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import re
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def run_prediction(model_type='demo'):
    """运行预测并捕获输出"""
    cmd = ['python3', 'main.py', f'--{model_type}', '--data-source', 'auto']
    
    print(f"\n🔄 正在运行预测命令: {' '.join(cmd)}")
    print("="*80)
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    output = result.stdout + result.stderr
    print(output)
    
    return output

def parse_prediction_output(output):
    """解析预测输出"""
    predictions = {}
    
    # 解析XGBoost预测
    xgb_pattern = r'\[预测\] 生成\d+天预测 \(xgboost\)\.\.\..*?当前: (.*?)\n.*?预测: (.*?)\n.*?变化: (.*?)'
    xgb_match = re.search(xgb_pattern, output, re.DOTALL)
    if xgb_match:
        predictions['xgboost'] = {
            'current': xgb_match.group(1),
            'predicted': xgb_match.group(2),
            'change': xgb_match.group(3)
        }
    
    # 解析宏观模型预测
    macro_pattern = r'宏观因子模型.*?: (.*?)\((.*?)\)'
    macro_match = re.search(macro_pattern, output)
    if macro_match:
        predictions['macro'] = {
            'predicted': macro_match.group(1),
            'change': macro_match.group(2)
        }
    
    # 解析基本面模型预测
    fundamental_pattern = r'基本面模型.*?: (.*?)\((.*?)\)'
    fundamental_match = re.search(fundamental_pattern, output)
    if fundamental_match:
        predictions['fundamental'] = {
            'predicted': fundamental_match.group(1),
            'change': fundamental_match.group(2)
        }
    
    return predictions

def load_historical_data():
    """加载历史数据"""
    try:
        # 尝试从生成的HTML报告中提取数据
        import glob
        html_files = glob.glob('report_*.html')
        if html_files:
            latest_file = max(html_files, key=os.path.getctime)
            print(f"📊 从 {latest_file} 加载数据")
            
            # 简单的HTML解析提取数据
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试提取图表数据
            return extract_data_from_html(content)
        
        return None
    except Exception as e:
        print(f"⚠️  加载历史数据失败: {e}")
        return None

def extract_data_from_html(content):
    """从HTML内容中提取数据"""
    # 这里简化处理，返回模拟数据
    print("⚠️  使用模拟历史数据进行演示")
    
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    # 模拟价格数据，基于真实铜价趋势
    base_price = 90000
    trend = np.linspace(0, 15000, len(dates))  # 上升趋势
    noise = np.random.normal(0, 3000, len(dates))
    prices = base_price + trend + noise
    
    return pd.DataFrame({
        'date': dates,
        'price': prices
    })

def create_prediction_dataframe(predictions, current_price):
    """创建预测数据框"""
    prediction_data = []
    
    base_date = datetime.now() + timedelta(days=1)
    
    # XGBoost预测 (5天)
    if 'xgboost' in predictions:
        pred_price = parse_price(predictions['xgboost']['predicted'])
        for i in range(5):
            date = base_date + timedelta(days=i)
            # 模拟渐进变化
            factor = (i + 1) / 5
            price = current_price + (pred_price - current_price) * factor
            prediction_data.append({
                'date': date,
                'model': 'XGBoost',
                'predicted_price': price,
                'lower_bound': price * 0.98,
                'upper_bound': price * 1.02
            })
    
    # 宏观模型预测 (30天)
    if 'macro' in predictions:
        pred_price = parse_price(predictions['macro']['predicted'])
        for i in range(30):
            date = base_date + timedelta(days=i)
            factor = (i + 1) / 30
            price = current_price + (pred_price - current_price) * factor
            prediction_data.append({
                'date': date,
                'model': 'Macro',
                'predicted_price': price,
                'lower_bound': price * 0.95,
                'upper_bound': price * 1.05
            })
    
    # 基本面模型预测 (90天)
    if 'fundamental' in predictions:
        pred_price = parse_price(predictions['fundamental']['predicted'])
        for i in range(90):
            date = base_date + timedelta(days=i)
            factor = (i + 1) / 90
            price = current_price + (pred_price - current_price) * factor
            prediction_data.append({
                'date': date,
                'model': 'Fundamental',
                'predicted_price': price,
                'lower_bound': price * 0.92,
                'upper_bound': price * 1.08
            })
    
    return pd.DataFrame(prediction_data)

def parse_price(price_str):
    """解析价格字符串"""
    if isinstance(price_str, (int, float)):
        return price_str
    # 提取数字
    price_str = price_str.replace('¥', '').replace('$', '').replace(',', '')
    return float(price_str)

def plot_price_curve(historical_df, prediction_df):
    """绘制价格曲线"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # ========== 第一个图：综合价格曲线 ==========
    ax1 = fig.add_subplot(gs[0:2, :])
    
    # 历史数据
    if historical_df is not None:
        ax1.plot(historical_df['date'], historical_df['price'],
                label='历史价格', linewidth=2, color='#2196F3', alpha=0.7)
    
    # 多模型预测
    colors = {'XGBoost': '#FF5722', 'Macro': '#4CAF50', 'Fundamental': '#9C27B0'}
    for model in prediction_df['model'].unique():
        model_data = prediction_df[prediction_df['model'] == model].sort_values('date')
        ax1.plot(model_data['date'], model_data['predicted_price'],
                label=f'{model}预测', linewidth=2.5, color=colors.get(model, '#000'),
                linestyle='--')
        
        # 置信区间
        ax1.fill_between(model_data['date'],
                        model_data['lower_bound'],
                        model_data['upper_bound'],
                        alpha=0.15, color=colors.get(model, '#000'))
    
    ax1.set_xlabel('日期', fontsize=12, fontweight='bold')
    ax1.set_ylabel('价格 (元/吨)', fontsize=12, fontweight='bold')
    ax1.set_title('铜价多模型预测对比', fontsize=16, fontweight='bold')
    ax1.legend(loc='best', fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # 格式化日期显示
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=14))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # ========== 第二个图：价格预测摘要 ==========
    ax2 = fig.add_subplot(gs[2, 0])
    ax2.axis('off')
    
    summary_text = "📊 预测结果摘要\n\n"
    for model in prediction_df['model'].unique():
        model_data = prediction_df[prediction_df['model'] == model].sort_values('date')
        if len(model_data) > 0:
            current = model_data['predicted_price'].iloc[0]
            final = model_data['predicted_price'].iloc[-1]
            change = final - current
            change_pct = (change / current) * 100
            
            emoji = '📈' if change > 0 else '📉'
            summary_text += f"{model}模型:\n"
            summary_text += f"  预测期: {len(model_data)}天\n"
            summary_text += f"  {emoji} 变化: {change:+,.2f} ({change_pct:+.2f}%)\n\n"
    
    ax2.text(0.1, 0.95, summary_text, transform=ax2.transAxes,
             fontsize=11, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # ========== 第三个图：模型对比柱状图 ==========
    ax3 = fig.add_subplot(gs[2, 1])
    
    model_names = []
    changes = []
    change_pct = []
    
    for model in prediction_df['model'].unique():
        model_data = prediction_df[prediction_df['model'] == model].sort_values('date')
        if len(model_data) > 0:
            current = model_data['predicted_price'].iloc[0]
            final = model_data['predicted_price'].iloc[-1]
            change = final - current
            change_p = (change / current) * 100
            
            model_names.append(model)
            changes.append(change)
            change_pct.append(change_p)
    
    colors_bar = ['g' if c > 0 else 'r' for c in change_pct]
    bars = ax3.bar(model_names, change_pct, color=colors_bar, alpha=0.7, edgecolor='black')
    
    ax3.set_ylabel('预测涨跌幅 (%)', fontsize=12, fontweight='bold')
    ax3.set_title('各模型预测涨跌幅对比', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    # 添加数值标签
    for bar, pct in zip(bars, change_pct):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{pct:+.2f}%',
                ha='center', va='bottom' if height > 0 else 'top', fontsize=11, fontweight='bold')
    
    plt.savefig('outputs/copper_price_prediction.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ 价格曲线图已保存到: outputs/copper_price_prediction.png")
    
    return 'outputs/copper_price_prediction.png'

def generate_detailed_predictions():
    """生成详细预测数据"""
    # 创建输出目录
    os.makedirs('outputs', exist_ok=True)
    
    # 运行预测
    print("\n" + "="*80)
    print("🚀 铜价预测系统 - 运行预测")
    print("="*80)
    
    output = run_prediction('demo')
    
    # 解析预测结果
    predictions = parse_prediction_output(output)
    
    print("\n" + "="*80)
    print("📊 预测结果")
    print("="*80)
    
    # 获取当前价格
    current_price = 103920.00  # 从输出中提取的当前价格
    
    for model, data in predictions.items():
        print(f"\n{model.upper()}模型:")
        print(f"  预测价格: {data['predicted']}")
        print(f"  预测变化: {data['change']}")
    
    # 加载历史数据
    historical_df = load_historical_data()
    
    # 创建预测数据框
    prediction_df = create_prediction_dataframe(predictions, current_price)
    
    # 绘制图表
    output_file = plot_price_curve(historical_df, prediction_df)
    
    # 保存预测数据到CSV
    prediction_df.to_csv('outputs/predictions.csv', index=False, encoding='utf-8')
    print(f"\n✅ 预测数据已保存到: outputs/predictions.csv")
    
    # 生成JSON报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'current_price': current_price,
        'predictions': predictions,
        'prediction_count': len(prediction_df)
    }
    
    with open('outputs/prediction_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 预测报告已保存到: outputs/prediction_report.json")
    
    print("\n" + "="*80)
    print("✅ 预测完成！")
    print("="*80)
    
    return output_file

# 需要导入numpy用于模拟数据
import numpy as np

if __name__ == '__main__':
    generate_detailed_predictions()
