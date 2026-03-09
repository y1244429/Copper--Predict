import requests
import json

# 测试 Alpha Vantage API
api_key = "6D092BQN6LS3J2D7"

print("="*70)
print("测试 Alpha Vantage API 连接")
print("="*70)

# 测试1: USD/JPY汇率
print("\n【测试1: USD/JPY 汇率】")
url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol=JPY&apikey={api_key}"
print(f"URL: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2)}")

        if 'Time Series FX (Daily)' in data:
            time_series = data['Time Series FX (Daily)']
            latest_date = list(time_series.keys())[0]
            latest_value = float(time_series[latest_date]['4. close'])
            print(f"✅ 成功获取USD/JPY汇率: {latest_value} (日期: {latest_date})")
        else:
            print("❌ 响应中没有Time Series FX (Daily)数据")
    else:
        print(f"❌ API调用失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 测试2: 使用GLOBAL_QUOTE
print("\n【测试2: GLOBAL_QUOTE】")
url2 = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=USDJPY&apikey={api_key}"
print(f"URL: {url2}")

try:
    response = requests.get(url2, timeout=10)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2)}")

        if 'Global Quote' in data:
            quote = data['Global Quote']
            print(f"✅ 成功获取USD/JPY汇率: {quote['05. price']}")
        else:
            print("❌ 响应中没有Global Quote数据")
    else:
        print(f"❌ API调用失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

print("\n" + "="*70)
