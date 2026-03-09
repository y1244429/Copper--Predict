"""
铜库存数据获取模块 - 支持 LME/COMEX/SHFE
实现三大交易所库存数据的实时获取和更新
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import time
import warnings
warnings.filterwarnings('ignore')


class InventoryDataSource:
    """库存数据源基类"""

    def __init__(self):
        self.last_update = None
        self.cache_ttl = 3600  # 缓存1小时
        self._cache = {}

    def fetch_inventory_data(self) -> Dict:
        """
        获取库存数据

        Returns:
            库存数据字典
        """
        raise NotImplementedError("子类必须实现此方法")

    def get_cached_data(self, force_refresh: bool = False) -> Dict:
        """
        获取缓存的数据（如果未过期）

        Args:
            force_refresh: 强制刷新

        Returns:
            库存数据字典
        """
        if not force_refresh and self.last_update:
            age = (datetime.now() - self.last_update).total_seconds()
            if age < self.cache_ttl:
                return self._cache

        # 获取新数据
        self._cache = self.fetch_inventory_data()
        self.last_update = datetime.now()
        return self._cache


class MockInventorySource(InventoryDataSource):
    """模拟库存数据源 - 用于测试"""

    def fetch_inventory_data(self) -> Dict:
        """获取模拟库存数据"""
        np.random.seed(int(datetime.now().strftime('%Y%m%d')))

        # 基础库存数据（单位：吨）
        base_lme = 260000  # LME库存约26万吨
        base_comex = 80000  # COMEX库存约8万吨
        base_shfe = 150000  # SHFE库存约15万吨

        # 添加随机波动
        lme_inventory = base_lme + np.random.randint(-5000, 5000)
        comex_inventory = base_comex + np.random.randint(-2000, 2000)
        shfe_inventory = base_shfe + np.random.randint(-3000, 3000)

        # LME注销仓单占比（%）- 模拟历史波动
        warrant_cancel_ratio = np.random.uniform(10, 80)

        # 保税区库存（吨）
        bonded_zone_inventory = 250000 + np.random.randint(-10000, 10000)

        # 注册仓单（吨）
        registered_inventory = lme_inventory * np.random.uniform(0.8, 0.95)

        # 持仓集中度（%）
        position_concentration = np.random.uniform(15, 45)

        return {
            'timestamp': datetime.now().isoformat(),
            'source': 'mock',
            'data': {
                'lme_inventory': lme_inventory,
                'comex_inventory': comex_inventory,
                'shfe_inventory': shfe_inventory,
                'total_inventory': lme_inventory + comex_inventory + shfe_inventory,
                'lme_warrant_cancel_ratio': warrant_cancel_ratio,
                'bonded_zone_inventory': bonded_zone_inventory,
                'registered_inventory': registered_inventory,
                'position_concentration': position_concentration
            },
            'metadata': {
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': '吨',
                'exchange': ['LME', 'COMEX', 'SHFE']
            }
        }


class LMEInventorySource(InventoryDataSource):
    """LME库存数据源 - 从LME官方API获取"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.lme.com/api"

    def fetch_inventory_data(self) -> Dict:
        """从LME获取库存数据"""
        try:
            # 注意: LME API需要付费订阅认证
            # 免费数据不可用，返回缺失标识
            print("⚠️  LME库存数据需要付费订阅，当前数据缺失")

            # 返回缺失标识数据
            return {
                'timestamp': datetime.now().isoformat(),
                'source': 'lme_missing',
                'data': {
                    'lme_inventory': None,
                    'lme_warrant_cancel_ratio': None,
                    'registered_inventory': None,
                    'data_source': 'LME库存数据需要付费订阅',
                    'available': False
                },
                'metadata': {
                    'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'currency': '吨',
                    'exchange': 'LME',
                    'note': 'LME官方数据需要付费API订阅'
                }
            }

        except Exception as e:
            print(f"LME数据获取失败: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'source': 'lme_error',
                'data': {
                    'lme_inventory': None,
                    'data_source': f'数据获取失败: {str(e)}',
                    'available': False
                }
            }


class COMEXInventorySource(InventoryDataSource):
    """COMEX库存数据源 - 从CME获取"""

    def __init__(self):
        super().__init__()
        # COMEX铜期货代码：HG
        self.symbol = 'HG'

    def fetch_inventory_data(self) -> Dict:
        """从COMEX获取库存数据"""
        try:
            # 注意: CME COMEX库存数据也需要付费订阅
            # 免费数据不可用，返回缺失标识
            print("⚠️  COMEX库存数据需要付费订阅，当前数据缺失")

            # 返回缺失标识数据
            return {
                'timestamp': datetime.now().isoformat(),
                'source': 'comex_missing',
                'data': {
                    'comex_inventory': None,
                    'data_source': 'COMEX库存数据需要付费订阅',
                    'available': False
                },
                'metadata': {
                    'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'currency': '吨',
                    'exchange': 'COMEX',
                    'note': 'CME官方数据需要付费订阅'
                }
            }

        except Exception as e:
            print(f"COMEX数据获取失败: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'source': 'comex_error',
                'data': {
                    'comex_inventory': None,
                    'data_source': f'数据获取失败: {str(e)}',
                    'available': False
                }
            }


class SHFEInventorySource(InventoryDataSource):
    """SHFE库存数据源 - 从上海期货交易所获取"""

    def __init__(self):
        super().__init__()
        self.base_url = "http://www.shfe.com.cn"

    def fetch_inventory_data(self) -> Dict:
        """从SHFE获取库存数据"""
        try:
            import akshare as ak

            # 从AKShare获取SHFE库存数据（东方财富网）
            print("正在获取SHFE库存数据...")
            df = ak.futures_inventory_em(symbol="cu")

            if not df.empty:
                latest = df.iloc[-1]

                return {
                    'timestamp': datetime.now().isoformat(),
                    'source': 'akshare',
                    'data': {
                        'shfe_inventory': int(latest.get('库存', 0)),
                        'shfe_inventory_change': float(latest.get('增减', 0)) if not pd.isna(latest.get('增减')) else 0,
                        'date': str(latest.get('日期', datetime.now().strftime('%Y-%m-%d'))),
                        'available': True,
                        'data_source': '东方财富网 (AKShare)',
                        'history_count': len(df)
                    },
                    'metadata': {
                        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'currency': '吨',
                        'exchange': 'SHFE',
                        'data_provider': '东方财富网'
                    }
                }
            else:
                print("⚠️  SHFE库存数据为空")
                return self._get_missing_data('SHFE库存数据为空')

        except ImportError:
            print("⚠️  AKShare未安装")
            return self._get_missing_data('AKShare未安装')
        except Exception as e:
            print(f"⚠️  SHFE数据获取失败: {e}")
            return self._get_missing_data(f'数据获取失败: {str(e)}')

    def _get_missing_data(self, reason: str) -> Dict:
        """返回缺失数据标识"""
        return {
            'timestamp': datetime.now().isoformat(),
            'source': 'shfe_error',
            'data': {
                'shfe_inventory': None,
                'shfe_inventory_change': None,
                'data_source': reason,
                'available': False
            },
            'metadata': {
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': '吨',
                'exchange': 'SHFE'
            }
        }


class CompositeInventorySource(InventoryDataSource):
    """综合库存数据源 - 整合多个交易所的库存数据"""

    def __init__(self):
        super().__init__()
        self.lme_source = LMEInventorySource()
        self.comex_source = COMEXInventorySource()
        self.shfe_source = SHFEInventorySource()

    def fetch_inventory_data(self) -> Dict:
        """整合所有交易所的库存数据"""
        # 从各个源获取数据
        lme_data = self.lme_source.get_cached_data()
        comex_data = self.comex_source.get_cached_data()
        shfe_data = self.shfe_source.get_cached_data()

        # 合并数据
        combined_data = {
            'timestamp': datetime.now().isoformat(),
            'source': 'composite',
            'exchanges': {},
            'summary': {},
            'data_status': {}
        }

        # LME数据
        if 'data' in lme_data:
            lme_available = lme_data['data'].get('available', True) if 'available' in lme_data['data'] else True
            lme_inv = lme_data['data'].get('lme_inventory')

            combined_data['exchanges']['LME'] = {
                'inventory': lme_inv if lme_available else None,
                'warrant_cancel_ratio': lme_data['data'].get('lme_warrant_cancel_ratio') if lme_available else None,
                'registered_inventory': lme_data['data'].get('registered_inventory') if lme_available else None,
                'available': lme_available,
                'source': lme_data.get('source', 'unknown'),
                'note': lme_data['data'].get('data_source') if not lme_available else None
            }
            combined_data['data_status']['LME'] = {
                'available': lme_available,
                'reason': lme_data['data'].get('data_source') if not lme_available else None
            }

        # COMEX数据
        if 'data' in comex_data:
            comex_available = comex_data['data'].get('available', True) if 'available' in comex_data['data'] else True
            comex_inv = comex_data['data'].get('comex_inventory')

            combined_data['exchanges']['COMEX'] = {
                'inventory': comex_inv if comex_available else None,
                'available': comex_available,
                'source': comex_data.get('source', 'unknown'),
                'note': comex_data['data'].get('data_source') if not comex_available else None
            }
            combined_data['data_status']['COMEX'] = {
                'available': comex_available,
                'reason': comex_data['data'].get('data_source') if not comex_available else None
            }

        # SHFE数据
        if 'data' in shfe_data:
            shfe_available = shfe_data['data'].get('available', True) if 'available' in shfe_data['data'] else True
            shfe_inv = shfe_data['data'].get('shfe_inventory')

            combined_data['exchanges']['SHFE'] = {
                'inventory': shfe_inv if shfe_available else None,
                'inventory_change': shfe_data['data'].get('shfe_inventory_change') if shfe_available else None,
                'date': shfe_data['data'].get('date'),
                'available': shfe_available,
                'source': shfe_data.get('source', 'unknown'),
                'note': shfe_data['data'].get('data_source') if not shfe_available else None
            }
            combined_data['data_status']['SHFE'] = {
                'available': shfe_available,
                'reason': shfe_data['data'].get('data_source') if not shfe_available else None
            }

        # 计算汇总数据（只统计可用数据）
        available_exchanges = [k for k, v in combined_data['data_status'].items() if v['available']]
        lme_inv = combined_data['exchanges']['LME']['inventory'] if combined_data['data_status']['LME']['available'] else 0
        comex_inv = combined_data['exchanges']['COMEX']['inventory'] if combined_data['data_status']['COMEX']['available'] else 0
        shfe_inv = combined_data['exchanges']['SHFE']['inventory'] if combined_data['data_status']['SHFE']['available'] else 0
        total_inv = (lme_inv if lme_inv else 0) + (comex_inv if comex_inv else 0) + (shfe_inv if shfe_inv else 0)

        combined_data['summary'] = {
            'total_inventory': total_inv if total_inv > 0 else None,
            'lme_inventory': lme_inv if lme_inv else None,
            'comex_inventory': comex_inv if comex_inv else None,
            'shfe_inventory': shfe_inv if shfe_inv else None,
            'lme_warrant_cancel_ratio': combined_data['exchanges']['LME'].get('warrant_cancel_ratio'),
            'registered_inventory': combined_data['exchanges']['LME'].get('registered_inventory'),
            'bonded_zone_inventory': None,  # 数据不可用
            'position_concentration': None,  # 数据不可用
            'exchange_distribution': {
                'LME': f"{lme_inv/total_inv*100:.1f}%" if total_inv > 0 and lme_inv else "数据缺失",
                'COMEX': f"{comex_inv/total_inv*100:.1f}%" if total_inv > 0 and comex_inv else "数据缺失",
                'SHFE': f"{shfe_inv/total_inv*100:.1f}%" if total_inv > 0 and shfe_inv else "数据缺失"
            },
            'available_exchanges': available_exchanges,
            'missing_exchanges': [k for k, v in combined_data['data_status'].items() if not v['available']]
        }

        combined_data['metadata'] = {
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'currency': '吨',
            'sources': [lme_data.get('source', 'unknown'),
                       comex_data.get('source', 'unknown'),
                       shfe_data.get('source', 'unknown')],
            'data_completeness': {
                'total': 3,
                'available': len(available_exchanges),
                'missing': 3 - len(available_exchanges),
                'percentage': f"{len(available_exchanges)/3*100:.1f}%"
            }
        }

        return combined_data


class InventoryManager:
    """库存数据管理器"""

    def __init__(self, source_type: str = 'composite'):
        """
        初始化库存管理器

        Args:
            source_type: 数据源类型 ('mock', 'composite', 'lme', 'comex', 'shfe')
        """
        self.source_type = source_type
        self.source = self._get_source()
        self._history_cache = {}  # 历史数据缓存
        self._history_cache_time = None

    def _get_source(self) -> InventoryDataSource:
        """根据类型获取数据源"""
        if self.source_type == 'composite':
            return CompositeInventorySource()
        elif self.source_type == 'lme':
            return LMEInventorySource()
        elif self.source_type == 'comex':
            return COMEXInventorySource()
        elif self.source_type == 'shfe':
            return SHFEInventorySource()
        else:
            return MockInventorySource()

    def get_inventory_data(self, force_refresh: bool = False) -> Dict:
        """
        获取库存数据

        Args:
            force_refresh: 强制刷新缓存

        Returns:
            库存数据字典
        """
        return self.source.get_cached_data(force_refresh)

    def get_historical_data(self, days: int = 30, force_refresh: bool = False) -> pd.DataFrame:
        """
        获取历史库存数据（包含注销仓单占比）
        注意: LME和COMEX的历史数据需要付费，SHFE可从AKShare获取真实数据

        Args:
            days: 获取多少天的历史数据
            force_refresh: 强制刷新缓存

        Returns:
            历史库存DataFrame，包含数据源标识
        """
        # 检查缓存
        cache_key = f"{days}"
        if not force_refresh and self._history_cache_time:
            age = (datetime.now() - self._history_cache_time).total_seconds()
            if age < 3600 and cache_key in self._history_cache:  # 缓存1小时
                return self._history_cache[cache_key]

        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        np.random.seed(42)

        # 生成模拟历史数据 - 注销仓单占比要有趋势性
        # 模拟趋势：前几天较低，中间上升，最近几天高位震荡
        warrant_trend = np.sin(np.linspace(0, 2*np.pi, days)) * 30 + 45  # 15-75之间的波动
        warrant_trend = np.clip(warrant_trend, 10, 85)

        data = {
            'date': dates,
            'lme_inventory': None,  # 数据缺失
            'comex_inventory': None,  # 数据缺失
            'shfe_inventory': None,  # 可以从AKShare获取，这里先设为None
            'lme_warrant_cancel_ratio': None,  # 数据缺失（LME付费数据）
            'data_source': 'LME和COMEX需要付费订阅，SHFE部分数据可用'
        }

        # 尝试从AKShare获取SHFE历史数据
        try:
            import akshare as ak
            shfe_df = ak.futures_inventory_em(symbol="cu")
            if not shfe_df.empty:
                # 转换日期
                shfe_df['日期'] = pd.to_datetime(shfe_df['日期']).dt.normalize()

                # 取最近days天的数据
                shfe_df = shfe_df.tail(days)

                # 创建一个映射字典
                date_to_inventory = {row['日期'].date(): row['库存'] for _, row in shfe_df.iterrows()}

                # 对齐日期 - 使用列表索引
                shfe_inv_list = [None] * len(dates)
                for i, date in enumerate(dates):
                    date_key = date.date()
                    if date_key in date_to_inventory:
                        shfe_inv_list[i] = date_to_inventory[date_key]

                data['shfe_inventory'] = shfe_inv_list

                filled_count = sum(1 for v in data['shfe_inventory'] if v is not None)
                print(f"✅ 成功获取SHFE历史库存数据 {filled_count}/{days} 条")
        except Exception as e:
            print(f"⚠️  SHFE历史数据获取失败: {e}")

        df = pd.DataFrame(data)
        df['total_inventory'] = df[['lme_inventory', 'comex_inventory', 'shfe_inventory']].sum(axis=1)
        df = df.set_index('date')

        # 添加数据源标记列
        df['lme_data_available'] = False
        df['comex_data_available'] = False
        df['shfe_data_available'] = df['shfe_inventory'].notna()

        # 缓存结果
        self._history_cache[cache_key] = df
        self._history_cache_time = datetime.now()

        return df

    def get_warrant_cancel_change(self, days: int = 7) -> Dict:
        """
        获取注销仓单占比变化情况（新增方法）
        注意: 此数据需要LME付费订阅，当前不可用

        Args:
            days: 对比多少天前的数据

        Returns:
            注销仓单占比变化字典，包含：
                - current_value: 当前值
                - previous_value: 过去值
                - absolute_change: 绝对变化
                - percentage_change: 百分比变化
                - trend: 趋势描述
                - history_days: 最近N天的历史数据
        """
        current_data = self.get_inventory_data()

        # 获取当前注销仓单占比（支持多种数据结构）
        current_ratio = None
        data_source = None

        if 'summary' in current_data:
            current_ratio = current_data['summary'].get('lme_warrant_cancel_ratio')
            # 检查数据是否可用
            if 'data_status' in current_data and 'LME' in current_data['data_status']:
                if not current_data['data_status']['LME'].get('available', True):
                    data_source = current_data['data_status']['LME'].get('reason', '数据不可用')

        elif 'data' in current_data:
            current_ratio = current_data['data'].get('lme_warrant_cancel_ratio')
            if current_data['data'].get('available') == False:
                data_source = current_data['data'].get('data_source', '数据不可用')

        elif 'exchanges' in current_data and 'LME' in current_data['exchanges']:
            current_ratio = current_data['exchanges']['LME'].get('warrant_cancel_ratio')

        # 如果数据不可用，返回缺失标识
        if current_ratio is None or data_source:
            return {
                'available': False,
                'error': 'LME注销仓单占比数据需要付费订阅',
                'data_source': data_source or 'LME官方数据需要付费API订阅',
                'indicator_name': 'LME注销仓单占比',
                'note': '此指标为付费数据，无法获取'
            }

        # 获取历史数据
        historical = self.get_historical_data(days + 1)  # 多获取一天用于计算变化
        if len(historical) < days or historical['lme_warrant_cancel_ratio'].isna().all():
            return {
                'error': '历史数据不足或数据不可用',
                'available': False,
                'data_source': 'LME历史数据需要付费订阅'
            }

        # 获取N天前的数据
        previous_ratio = historical['lme_warrant_cancel_ratio'].iloc[-(days + 1)]

        if pd.isna(previous_ratio) or pd.isna(current_ratio):
            return {
                'available': False,
                'error': '数据缺失',
                'data_source': 'LME注销仓单数据需要付费订阅'
            }

        # 计算变化
        absolute_change = current_ratio - previous_ratio
        percentage_change = (absolute_change / previous_ratio * 100) if previous_ratio != 0 else 0

        # 判断趋势
        if abs(percentage_change) < 2:
            trend = "稳定"
            trend_emoji = "➡️"
        elif percentage_change > 0:
            trend = "上升"
            trend_emoji = "📈"
        else:
            trend = "下降"
            trend_emoji = "📉"

        # 获取最近N天的历史趋势数据
        history_data = []
        for i in range(min(days, len(historical))):
            idx = -(i + 1)
            value = historical['lme_warrant_cancel_ratio'].iloc[idx]
            if pd.notna(value):
                history_data.append({
                    'date': historical.index[idx].strftime('%Y-%m-%d'),
                    'value': float(value),
                    'days_ago': i
                })
        history_data.reverse()  # 从最早的到最新的

        # 计算移动平均趋势
        valid_values = historical['lme_warrant_cancel_ratio'].dropna()
        if len(valid_values) >= 5:
            ma5 = valid_values.iloc[-5:].mean()
            ma5_change = (current_ratio - ma5) / ma5 * 100
        else:
            ma5 = current_ratio
            ma5_change = 0

        # 评估变化幅度
        if abs(percentage_change) < 2:
            change_level = "平稳"
        elif abs(percentage_change) < 5:
            change_level = "小幅波动"
        elif abs(percentage_change) < 10:
            change_level = "显著变化"
        elif abs(percentage_change) < 20:
            change_level = "大幅变化"
        else:
            change_level = "极端波动"

        return {
            'available': True,
            'indicator_name': 'LME注销仓单占比',
            'current_value': round(float(current_ratio), 2),
            'previous_value': round(float(previous_ratio), 2),
            'absolute_change': round(float(absolute_change), 2),
            'percentage_change': round(float(percentage_change), 2),
            'trend': trend,
            'trend_emoji': trend_emoji,
            'change_level': change_level,
            'days_ago': days,
            'ma5': round(float(ma5), 2),
            'ma5_change': round(float(ma5_change), 2),
            'history_data': history_data,
            'date_range': {
                'from': historical.index[-(days + 1)].strftime('%Y-%m-%d'),
                'to': datetime.now().strftime('%Y-%m-%d')
            }
        }

    def get_inventory_change(self, days: int = 7) -> Dict:
        """
        获取库存变化情况

        Args:
            days: 对比多少天前的数据

        Returns:
            库存变化字典
        """
        current_data = self.get_inventory_data()

        if 'summary' not in current_data:
            return {}

        # 获取历史数据进行对比
        historical = self.get_historical_data(days)
        if len(historical) > 0:
            prev = historical.iloc[0]
            current = {
                'lme_inventory': current_data['summary']['lme_inventory'],
                'comex_inventory': current_data['summary']['comex_inventory'],
                'shfe_inventory': current_data['summary']['shfe_inventory'],
                'total_inventory': current_data['summary']['total_inventory']
            }

            changes = {}
            for key in current:
                if key in prev:
                    change = current[key] - prev[key]
                    change_pct = (change / prev[key] * 100) if prev[key] != 0 else 0
                    changes[key] = {
                        'absolute': change,
                        'percentage': change_pct
                    }

            return {
                'days_ago': days,
                'changes': changes,
                'date_range': {
                    'from': historical.index[0].strftime('%Y-%m-%d'),
                    'to': datetime.now().strftime('%Y-%m-%d')
                }
            }

        return {}


def get_inventory_source(source_type: str = 'auto') -> InventoryManager:
    """
    获取库存数据源

    Args:
        source_type: 'auto', 'composite', 'mock', 'lme', 'comex', 'shfe'

    Returns:
        库存管理器实例
    """
    if source_type == 'auto':
        # 尝试检测可用的数据源
        try:
            import akshare
            return InventoryManager('composite')
        except ImportError:
            print("提示: AKShare未安装，使用模拟数据")
            return InventoryManager('mock')
    else:
        return InventoryManager(source_type)
