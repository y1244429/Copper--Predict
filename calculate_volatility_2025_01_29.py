"""
计算2025年1月29日的COMEX铜价波动率
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data.data_sources import AKShareDataSource
import warnings
warnings.filterwarnings('ignore')

def calculate_volatility_for_date(target_date: str):
    """
    计算指定日期的波动率

    Args:
        target_date: 目标日期 (格式: YYYY-MM-DD)
    """
    print(f"📊 计算 {target_date} 的COMEX铜价波动率\n")
    print("=" * 60)

    # 获取数据
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    start_date = target_date_obj - timedelta(days=365)

    print(f"数据范围: {start_date.strftime('%Y-%m-%d')} 至 {target_date}")

    # 尝试获取真实数据
    print("\n正在从AKShare获取数据...")
    source = AKShareDataSource()

    try:
        data = source.fetch_copper_price(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=target_date
        )

        if data is None or len(data) == 0:
            print("❌ 未获取到数据")
            return

        print(f"✅ 成功获取 {len(data)} 条数据\n")

        # 检查目标日期是否存在
        target_date_data = data[data.index == pd.Timestamp(target_date)]
        if target_date_data.empty:
            print(f"⚠️  目标日期 {target_date} 的数据不存在")
            print(f"数据日期范围: {data.index.min()} 至 {data.index.max()}")
            # 使用最接近的日期
            closest_date = data.index[data.index <= pd.Timestamp(target_date)].max()
            print(f"使用最接近的日期: {closest_date.strftime('%Y-%m-%d')}")
            target_date_data = data[data.index == closest_date]

        print("\n" + "=" * 60)
        print("📈 波动率计算结果")
        print("=" * 60)

        # 计算收益率
        data['returns'] = data['close'].pct_change()

        # 1. 日内波动率（使用目标日期及前4天的平均日内波动）
        if 'high' in data.columns and 'low' in data.columns:
            recent_data = data.tail(5)
            intraday_vol = ((recent_data['high'] - recent_data['low']) / recent_data['close']).mean() * 100

            print(f"\n📊 日内波动率（最近5天平均）")
            print(f"   计算方法: ((最高价 - 最低价) / 收盘价) × 100%")
            print(f"   数值: {intraday_vol:.4f}%")

            # 显示最近5天的日内波动详情
            print(f"\n   最近5天详情:")
            for i, (date, row) in enumerate(recent_data.iterrows(), 1):
                daily_intraday = (row['high'] - row['low']) / row['close'] * 100
                print(f"     {date.strftime('%Y-%m-%d')}: {daily_intraday:.4f}%")

        # 2. 20日年化波动率
        if len(data) >= 20:
            daily_vol_20d = data['returns'].tail(20).std() * np.sqrt(252) * 100
            print(f"\n📊 20日年化波动率")
            print(f"   计算方法: 20日收益率标准差 × √252 × 100%")
            print(f"   数值: {daily_vol_20d:.4f}%")

            # 显示20日收益率统计
            recent_20d = data['returns'].tail(20)
            print(f"\n   20日收益率统计:")
            print(f"     平均值: {recent_20d.mean() * 100:.4f}%")
            print(f"     标准差: {recent_20d.std() * 100:.4f}%")
            print(f"     最大值: {recent_20d.max() * 100:.4f}%")
            print(f"     最小值: {recent_20d.min() * 100:.4f}%")

        # 3. 周波动率（5日）
        if len(data) >= 5:
            weekly_vol = data['returns'].tail(5).std() * np.sqrt(52) * 100
            print(f"\n📊 周波动率（5日）")
            print(f"   计算方法: 5日收益率标准差 × √52 × 100%")
            print(f"   数值: {weekly_vol:.4f}%")

        # 4. 日波动率（年化）
        daily_vol_annual = data['returns'].std() * np.sqrt(252) * 100
        print(f"\n📊 全部数据年化波动率")
        print(f"   计算方法: 全部收益率标准差 × √252 × 100%")
        print(f"   数值: {daily_vol_annual:.4f}%")

        # 5. 目标日期的具体波动率
        if not target_date_data.empty:
            date_data = target_date_data.iloc[0]
            target_date_index = target_date_data.index[0]

            print(f"\n" + "=" * 60)
            print(f"📅 {target_date_index.strftime('%Y-%m-%d')} 当日数据")
            print("=" * 60)

            print(f"\n价格信息:")
            print(f"   开盘价: {date_data['open']:.4f}")
            print(f"   最高价: {date_data['high']:.4f}")
            print(f"   最低价: {date_data['low']:.4f}")
            print(f"   收盘价: {date_data['close']:.4f}")

            if 'volume' in date_data:
                print(f"   成交量: {date_data['volume']:.0f}")

            # 当日日内波动率
            daily_intraday = (date_data['high'] - date_data['low']) / date_data['close'] * 100
            print(f"\n当日日内波动率: {daily_intraday:.4f}%")

            # 当日价格变动
            if 'open' in date_data and 'close' in date_data:
                daily_change = (date_data['close'] - date_data['open']) / date_data['open'] * 100
                print(f"当日价格变动: {daily_change:+.4f}%")

        print(f"\n" + "=" * 60)
        print("✅ 计算完成")
        print("=" * 60)

        return {
            'intraday': float(intraday_vol),
            'daily_20d': float(daily_vol_20d) if len(data) >= 20 else None,
            'weekly': float(weekly_vol) if len(data) >= 5 else None,
            'annual': float(daily_vol_annual)
        }

    except Exception as e:
        print(f"❌ 计算失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # 计算2025年1月29日的波动率
    result = calculate_volatility_for_date("2025-01-29")

    if result:
        print(f"\n📊 波动率汇总:")
        print(f"   日内波动率: {result['intraday']:.4f}%")
        print(f"   20日年化波动率: {result['daily_20d']:.4f}%")
        print(f"   周波动率: {result['weekly']:.4f}%")
        print(f"   全部数据年化波动率: {result['annual']:.4f}%")
