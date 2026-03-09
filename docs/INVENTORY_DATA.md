# 库存数据更新功能说明

## 概述
已成功实现 LME/COMEX/SHFE 三大交易所铜库存数据的自动获取和更新功能，并集成到风险预警系统中。

## 功能特性

### 1. 数据源模块 (`data/inventory_data.py`)

#### 支持的数据源
- **MockInventorySource**: 模拟数据源（用于测试）
- **LMEInventorySource**: LME库存数据源
- **COMEXInventorySource**: COMEX库存数据源
- **SHFEInventorySource**: SHFE库存数据源（通过AKShare）
- **CompositeInventorySource**: 综合数据源（整合所有交易所）

#### 核心功能
- 自动缓存（1小时TTL）
- 历史数据查询（支持自定义天数）
- 库存变化分析（周环比、月环比）
- 综合数据汇总和分布统计

### 2. API 端点

#### GET `/inventory`
获取当前库存数据

```bash
curl http://localhost:8001/inventory
```

参数：
- `refresh=true` - 强制刷新缓存（可选）

返回数据：
```json
{
  "exchanges": {
    "LME": {
      "inventory": 261097,
      "warrant_cancel_ratio": 58.1,
      "registered_inventory": 218271
    },
    "COMEX": {
      "inventory": 81500
    },
    "SHFE": {
      "inventory": 152261
    }
  },
  "summary": {
    "total_inventory": 494858,
    "exchange_distribution": {
      "LME": "52.8%",
      "COMEX": "16.5%",
      "SHFE": "30.7%"
    }
  },
  "metadata": {
    "last_update": "2026-02-28 19:26:07",
    "currency": "吨",
    "sources": ["lme_mock", "comex_mock", "shfe_mock"]
  }
}
```

#### GET `/inventory/history`
获取历史库存数据

```bash
curl http://localhost:8001/inventory/history?days=30
```

参数：
- `days` - 查询天数（默认30天）

#### GET `/inventory/change`
获取库存变化情况

```bash
curl http://localhost:8001/inventory/change?days=7
```

参数：
- `days` - 对比天数（默认7天）

返回数据：
```json
{
  "days_ago": 7,
  "changes": {
    "lme_inventory": {
      "absolute": -3870,
      "percentage": -1.46
    },
    "total_inventory": {
      "absolute": 9853,
      "percentage": 2.03
    }
  }
}
```

### 3. 风险预警集成

库存数据已集成到风险预警系统中，支持以下预警指标：

- **LME注销仓单占比**
  - 二级阈值：50%
  - 三级阈值：70%
  - 用于检测现货挤兑风险

- **注册仓单下降**
  - 逼仓阈值：5万吨
  - 用于检测逼仓风险

- **持仓集中度**
  - 逼仓阈值：40%
  - 用于检测市场操纵风险

#### 预警检查结果
访问 `/checklists` 端点可以看到库存检查结果：
```
库存信息:
  总库存: 494858 吨
  LME: 261097 吨
  COMEX: 81500 吨
  SHFE: 152261 吨
  LME注销仓单占比: 58.1%
  数据源: ['lme_mock', 'comex_mock', 'shfe_mock']
```

## 数据源说明

### 当前状态
- **LME**: 使用模拟数据（LME API需要认证）
- **COMEX**: 使用模拟数据（COMEX库存数据需要订阅）
- **SHFE**: 尝试使用AKShare获取，失败时使用模拟数据

### 生产环境部署建议

#### LME数据
需要申请LME API密钥：
1. 访问 https://www.lme.com/en/Market-data/API
2. 注册并获取API密钥
3. 在 `LMEInventorySource.fetch_inventory_data()` 中配置认证

#### COMEX数据
需要订阅CME数据服务：
1. 访问 https://www.cmegroup.com/market-data/data-vendor.html
2. 选择合适的数据供应商
3. 集成CME QuickStrike或DataStream API

#### SHFE数据
确保AKShare正确安装：
```bash
pip install akshare
```

如果AKShare的SHFE库存接口不可用，可以：
1. 直接访问上海期货交易所官网：http://www.shfe.com.cn
2. 使用Selenium爬取库存数据
3. 或使用其他第三方数据服务

## 使用示例

### Python 脚本使用

```python
from data.inventory_data import get_inventory_source

# 获取库存数据
inventory_mgr = get_inventory_source('auto')
data = inventory_mgr.get_inventory_data()

# 查看总库存
total = data['summary']['total_inventory']
print(f"总库存: {total:.0f} 吨")

# 获取历史数据（30天）
historical = inventory_mgr.get_historical_data(30)

# 分析库存变化
change = inventory_mgr.get_inventory_change(7)
for key, value in change['changes'].items():
    print(f"{key}: {value['absolute']:.0f} 吨 ({value['percentage']:.2f}%)")
```

### Web界面访问
1. 访问 http://localhost:8001
2. 点击"🚨 铜价风险预警系统"
3. 查看库存监控和预警信息

## 性能优化

1. **缓存机制**
   - 数据缓存1小时
   - 避免频繁请求外部API
   - 可通过 `refresh=true` 参数强制刷新

2. **异步请求**
   - 三大交易所数据并行获取
   - 超时设置：10秒
   - 失败时使用缓存或模拟数据

## 监控和维护

### 定期检查
- 每天检查数据更新状态
- 验证数据准确性
- 监控API调用频率

### 错误处理
- API请求失败时自动降级到模拟数据
- 记录错误日志
- 提供数据源状态信息

## 未来改进

1. **真实数据源集成**
   - 申请并配置LME API密钥
   - 订阅COMEX数据服务
   - 完善SHFE数据获取

2. **数据可视化**
   - 添加库存趋势图表
   - 交易所分布饼图
   - 实时数据更新动画

3. **预警优化**
   - 增加更多库存指标
   - 机器学习预测
   - 智能预警阈值调整

## 测试

运行测试脚本：
```bash
python test_inventory.py
```

测试内容：
1. 模拟数据源
2. 综合数据源
3. 历史数据查询
4. 库存变化分析
5. 缓存功能

## 故障排查

### 问题：数据更新失败
**解决方案**：
1. 检查网络连接
2. 验证API密钥是否正确
3. 查看服务器日志：`tail -f server.log`

### 问题：预警不触发
**解决方案**：
1. 检查阈值配置
2. 验证库存数据格式
3. 查看风险预警日志

### 问题：性能慢
**解决方案**：
1. 启用缓存
2. 减少查询天数
3. 使用CDN加速

## 联系支持

如有问题，请：
1. 查看日志文件
2. 运行测试脚本
3. 检查API状态
4. 联系技术支持
