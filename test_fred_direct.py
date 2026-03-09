import requests
import json

# 测试 FRED API
api_key = "6D092BQN6LS3J2D7"

print("="*70)
print("测试 FRED API 连接")
print("="*70)

# 测试1: 美元指数 (DTWEXBGS)
print("\n【测试1: 美元指数 DTWEXBGS】")
url1 = f"https://api.stlouisfed.org/fred/series/observations?series_id=DTWEXBGS&api_key={api_key}&file_type=json&limit=1"
print(f"URL: {url1}")

try:
    response = requests.get(url1, timeout=10)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2)}")

        if 'observations' in data and len(data['observations']) > 0:
            obs = data['observations'][0]
            print(f"✅ 成功获取美元指数: {obs['value']} (日期: {obs['date']})")
        else:
            print("❌ 响应中没有observations数据")
    else:
        print(f"❌ API调用失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 测试2: PMI (NAPM)
print("\n【测试2: PMI NAPM】")
url2 = f"https://api.stlouisfed.org/fred/series/observations?series_id=NAPM&api_key={api_key}&file_type=json&limit=1"
print(f"URL: {url2}")

try:
    response = requests.get(url2, timeout=10)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2)}")

        if 'observations' in data and len(data['observations']) > 0:
            obs = data['observations'][0]
            print(f"✅ 成功获取PMI: {obs['value']} (日期: {obs['date']})")
        else:
            print("❌ 响应中没有observations数据")
    else:
        print(f"❌ API调用失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 测试3: 联邦基金利率 (FEDFUNDS)
print("\n【测试3: 联邦基金利率 FEDFUNDS】")
url3 = f"https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key={api_key}&file_type=json&limit=1"
print(f"URL: {url3}")

try:
    response = requests.get(url3, timeout=10)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2)}")

        if 'observations' in data and len(data['observations']) > 0:
            obs = data['observations'][0]
            print(f"✅ 成功获取联邦基金利率: {obs['value']}% (日期: {obs['date']})")
        else:
            print("❌ 响应中没有observations数据")
    else:
        print(f"❌ API调用失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

print("\n" + "="*70)
