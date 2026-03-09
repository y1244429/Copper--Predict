#!/usr/bin/env python3
"""测试预警系统检查清单"""
import sys
sys.path.append('.')

from models.risk_alert_system import CopperRiskMonitor
from data.data_sources import AKShareDataSource, MockDataSource
from data.inventory_data import get_inventory_source
from datetime import datetime, timedelta

print("=== 测试预警系统检查清单 ===\n")

# 创建监控器
monitor = CopperRiskMonitor()

# 获取价格数据 - 使用真实数据
try:
    real_source = AKShareDataSource()
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    price_data = real_source.fetch_copper_price(start_date=start_date, end_date=end_date)
    print(f"✅ 价格数据: {len(price_data)} 条记录\n")
except Exception as e:
    print(f"⚠️  真实数据获取失败，使用模拟数据: {e}")
    source = MockDataSource()
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    price_data = source.fetch_copper_price(start_date=start_date, end_date=end_date)
    print(f"✅ 价格数据(模拟): {len(price_data)} 条记录\n")

# 获取库存数据
inventory_mgr = get_inventory_source('auto')
inventory_data_full = inventory_mgr.get_inventory_data()

# 提取库存数据用于检查
if 'summary' in inventory_data_full:
    inventory_dict = {
        'lme_inventory': inventory_data_full['summary']['lme_inventory'],
        'comex_inventory': inventory_data_full['summary']['comex_inventory'],
        'shfe_inventory': inventory_data_full['summary']['shfe_inventory'],
    }
    print(f"✅ 库存数据:")
    print(f"  - LME: {inventory_dict['lme_inventory']}")
    print(f"  - COMEX: {inventory_dict['comex_inventory']}")
    print(f"  - SHFE: {inventory_dict['shfe_inventory']}\n")
else:
    inventory_dict = {}
    print("⚠️  库存数据为空\n")

# 执行检查清单
try:
    print("开始执行检查清单...")
    check_results = monitor.auto_execute_checklist(
        price_data=price_data,
        inventory_data=inventory_dict
    )

    print(f"\n每日检查: {len(check_results['daily'])} 项")
    for i, item in enumerate(check_results['daily'], 1):
        print(f"  {i}. {item['item']}: {item['message']}")

    print(f"\n实时监控: {len(check_results['realtime'])} 项")
    for i, item in enumerate(check_results['realtime'], 1):
        print(f"  {i}. {item['item']}: {item['message']}")

    print(f"\n摘要: {check_results['summary']}\n")

except Exception as e:
    print(f"❌ 检查清单执行失败: {e}")
    import traceback
    traceback.print_exc()
