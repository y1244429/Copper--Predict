#!/usr/bin/env python3
"""
测试ARDL宏观模型预测结果提取
"""

import re

# 读取最新的报告文件
with open('report_20260305_194959.txt', 'r', encoding='utf-8') as f:
    report_text = f.read()

print("="*60)
print("ARDL宏观模型预测结果提取测试")
print("="*60)

# 使用与Web界面相同的正则表达式
pattern = r'宏观因子模型[\s\S]*?预测 \(90天\): ¥([\d,.]+) \(([+-][\d.]+)%\)'
match = re.search(pattern, report_text)

if match:
    price = float(match.group(1).replace(',', ''))
    change = float(match.group(2))
    
    print("\n✓ 正则表达式匹配成功！")
    print(f"\nARDL宏观模型预测结果:")
    print(f"  预测价格: ¥{price:,.2f}")
    print(f"  涨跌幅: {change:+.2f}%")
    print(f"  预测周期: 90天")
    
    print("\n" + "="*60)
    print("Web界面应该显示:")
    print("="*60)
    print(f"ARDL宏观模型:")
    print(f"  预测价格: ¥{price:,.2f}")
    print(f"  涨跌幅: {change:+.2f}%")
    print(f"  预测周期: 中期（1-6个月）")
    
    # 检查价格是否合理
    print("\n" + "="*60)
    print("价格合理性检查:")
    print("="*60)
    if 40000 <= price <= 120000:
        print(f"✓ 预测价格 ¥{price:,.2f} 在合理范围内 (¥40,000-¥120,000)")
    else:
        print(f"✗ 警告: 预测价格 ¥{price:,.2f} 超出合理范围")
        
    if -30 <= change <= 30:
        print(f"✓ 预涨跌幅 {change:+.2f}% 在合理范围内 (-30% ~ +30%)")
    else:
        print(f"✗ 警告: 预涨跌幅 {change:+.2f}% 超出合理范围")
        
else:
    print("\n✗ 正则表达式匹配失败")
    print("\n尝试查看报告内容...")
    lines = report_text.split('\n')
    for i, line in enumerate(lines):
        if '宏观因子' in line or '90天' in line:
            print(f"第{i+1}行: {line}")
