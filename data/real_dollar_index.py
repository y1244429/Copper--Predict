"""
直接获取真实美元指数 - 使用网络爬虫
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_real_dollar_index():
    """
    从财经网站获取真实美元指数
    """
    try:
        # 使用金投网获取美元指数
        url = "https://forex.cngold.org/usdx/c10362093.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找美元指数的值
            # 网页中美元指数通常在表格中
            content = response.text

            # 使用正则表达式提取数值
            # 查找类似 "美元 指数 98.4903" 的模式
            patterns = [
                r'美元\s*指数\s*([\d.]+)',
                r'DXY[:\s]*([\d.]+)',
                r'美元指数[:\s]*([\d.]+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    value = float(match.group(1))
                    logger.info(f"从金投网获取美元指数: {value}")
                    return {
                        'timestamp': datetime.now(),
                        'value': round(value, 2),
                        'source': '金投网 (爬虫)',
                        'date': datetime.now().strftime('%Y-%m-%d')
                    }

        logger.warning("从金投网获取失败，尝试备用方案")
        return None

    except Exception as e:
        logger.error(f"获取美元指数失败: {e}")
        return None


def get_dollar_index_multiple_sources():
    """
    从多个数据源获取美元指数
    """
    sources = []

    # 尝试金投网
    result = get_real_dollar_index()
    if result:
        sources.append(result)

    # 如果所有方法都失败，使用备用值
    if not sources:
        logger.warning("所有数据源都失败，使用备用数据")
        return {
            'timestamp': datetime.now(),
            'value': 99.0,  # 当前美元指数水平
            'source': 'Fallback (基于当前市场水平)',
            'date': datetime.now().strftime('%Y-%m-%d')
        }

    # 返回第一个成功的源
    return sources[0]


if __name__ == "__main__":
    print("=" * 70)
    print("测试获取真实美元指数")
    print("=" * 70)

    result = get_dollar_index_multiple_sources()

    print(f"\n结果:")
    print(f"  美元指数: {result['value']}")
    print(f"  数据源: {result['source']}")
    print(f"  更新时间: {result['date']}")
    print(f"  获取时间: {result['timestamp']}")

    # 分析风险等级
    print(f"\n风险分析:")
    if result['value'] > 105:
        print(f"  🔴 高风险: 美元指数过强({result['value']:.2f})")
        print(f"  建议调整: -10%")
    elif result['value'] > 102:
        print(f"  🟡 中风险: 美元指数偏高({result['value']:.2f})")
        print(f"  建议调整: -4%")
    elif result['value'] < 95:
        print(f"  🟢 低风险: 美元指数偏低({result['value']:.2f})")
        print(f"  建议调整: 0% (无风险)")
    else:
        print(f"  ✅ 正常: 美元指数正常({result['value']:.2f})")
        print(f"  建议调整: 0% (无风险)")

    print("\n" + "=" * 70)
