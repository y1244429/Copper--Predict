"""
测试AKShare API获取实时汇率数据
"""

import akshare as ak
import pandas as pd

print("=" * 70)
print("测试AKShare汇率API")
print("=" * 70)

# 测试1: 获取汇率行情
print("\n【测试1: fx_spot_quote】")
try:
    df = ak.fx_spot_quote()
    print(f"获取成功！数据形状: {df.shape}")
    print("\n前5行数据:")
    print(df.head())
    print("\n列名:", df.columns.tolist())

    if not df.empty:
        print("\n查找USD/CNY:")
        if '货币对' in df.columns:
            usd_cny = df[df['货币对'] == 'USD/CNY']
            if not usd_cny.empty:
                print(usd_cny)
            else:
                print("未找到USD/CNY")
        else:
            print("数据列中没有'货币对'字段")
            print("\n所有货币对:")
            print(df.iloc[:10, 0] if len(df.columns) > 0 else df.head(10))
except Exception as e:
    print(f"获取失败: {e}")

# 测试2: 查找其他汇率相关API
print("\n" + "=" * 70)
print("【测试2: 查找其他汇率API】")
print("=" * 70)

# 尝试获取人民币中间价
print("\n测试: fx_spot_quote_bank（外汇中间价）")
try:
    df2 = ak.fx_spot_quote_bank()
    print(f"获取成功！数据形状: {df2.shape}")
    print("\n前5行:")
    print(df2.head())

    # 查找USD/CNY
    if not df2.empty and len(df2.columns) > 0:
        print("\n查找USD/CNY相关数据:")
        for idx, row in df2.head(10).iterrows():
            print(row.to_dict())
except Exception as e:
    print(f"获取失败: {e}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
