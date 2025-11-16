# 云成本账单拉取和预测系统

## 功能概述

本系统提供完整的云成本管理解决方案，支持：

1. **账单数据拉取**: 自动从阿里云和腾讯云拉取账单数据
2. **成本分析**: 分析每日成本，识别高/低成本天数
3. **成本预测**: 使用机器学习预测未来成本趋势
4. **异常检测**: 自动检测异常成本波动
5. **预算比较**: 与预算进行对比分析

## 支持的云服务商

- ✅ 阿里云 (Alibaba Cloud)
- ✅ 腾讯云 (Tencent Cloud)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
cp env.example .env
```

编辑 `.env` 文件，配置云服务商的访问凭证：

```env
# 阿里云配置
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
ALIBABA_CLOUD_BSS_ENDPOINT=business.aliyuncs.com

# 腾讯云配置
TENCENT_CLOUD_SECRET_ID=your_secret_id
TENCENT_CLOUD_SECRET_KEY=your_secret_key
TENCENT_CLOUD_REGION=ap-guangzhou
```

### 3. 使用命令行工具

#### 拉取账单数据

```bash
# 拉取所有云服务商最近30天的账单
python scripts/fetch_billing.py fetch --provider all

# 拉取阿里云指定日期范围的账单
python scripts/fetch_billing.py fetch --provider alibaba --start-date 2024-01-01 --end-date 2024-01-31

# 保存结果到文件
python scripts/fetch_billing.py fetch --provider all --output billing_data.json
```

#### 查询账户余额

```bash
python scripts/fetch_billing.py balance --provider all
```

#### 分析每日成本

```bash
# 分析最近30天的成本，判断每天成本高/低
python scripts/fetch_billing.py analyze --provider all --days 30

# 分析指定日期范围
python scripts/fetch_billing.py analyze --provider tencent --start-date 2024-01-01 --end-date 2024-01-31
```

#### 预测未来成本

```bash
# 基于最近30天数据，预测未来30天成本
python scripts/fetch_billing.py predict --provider all --days 30

# 基于历史数据预测未来60天
python scripts/fetch_billing.py predict --provider alibaba --start-date 2024-01-01 --end-date 2024-01-31 --days 60
```

#### 检测异常成本

```bash
# 检测最近30天的异常成本
python scripts/fetch_billing.py anomaly --provider all --days 30
```

#### 完整分析

```bash
# 执行完整的分析（包含成本分析、预测、异常检测）
python scripts/fetch_billing.py full --provider all --days 30 --output full_report.json
```

## API 接口

### 账户余额

#### 获取所有云账户余额

```
GET /api/finance/balances/
```

返回示例：
```json
{
  "success": true,
  "balances": [
    {
      "provider": "Alibaba Cloud",
      "balance": 1000.50,
      "currency": "CNY"
    },
    {
      "provider": "Tencent Cloud",
      "balance": 2000.00,
      "currency": "CNY"
    }
  ],
  "total_balance": 3000.50
}
```

### 账单数据

#### 拉取账单数据

```
GET /api/finance/billing/?provider=all&start_date=2024-01-01&end_date=2024-01-31
```

参数：
- `provider`: 云服务商 (`alibaba`, `tencent`, `all`)
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)

#### 获取每日成本

```
GET /api/finance/daily-costs/?provider=all&start_date=2024-01-01&end_date=2024-01-31
```

返回示例：
```json
{
  "success": true,
  "provider": "all",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "daily_costs": {
    "2024-01-01": 150.50,
    "2024-01-02": 200.30,
    ...
  }
}
```

### 成本分析

#### 分析每日成本（判断高/低）

```
GET /api/finance/analyze/?provider=all&start_date=2024-01-01&end_date=2024-01-31
```

返回示例：
```json
{
  "success": true,
  "daily_analysis": [
    {
      "date": "2024-01-01",
      "cost": 150.50,
      "level": "normal",
      "description": "成本正常",
      "deviation_pct": -5.2
    },
    {
      "date": "2024-01-02",
      "cost": 250.30,
      "level": "high",
      "description": "成本偏高",
      "deviation_pct": 25.8
    }
  ],
  "statistics": {
    "mean_cost": 180.40,
    "median_cost": 175.20,
    "std_cost": 45.30,
    "min_cost": 120.00,
    "max_cost": 280.00
  }
}
```

成本水平说明：
- **high**: 成本 > 平均值 + 标准差（成本偏高）
- **normal**: 成本在正常范围内
- **low**: 成本 < 平均值 - 标准差（成本偏低）

### 成本预测

#### 预测未来成本

```
GET /api/finance/predict/?provider=all&start_date=2024-01-01&end_date=2024-01-31&days_ahead=30&method=ensemble
```

参数：
- `days_ahead`: 预测未来多少天（默认30）
- `method`: 预测方法
  - `ensemble`: 集成多个模型（推荐，默认）
  - `linear`: 线性回归
  - `random_forest`: 随机森林
  - `moving_average`: 移动平均

返回示例：
```json
{
  "success": true,
  "predictions": [
    {
      "date": "2024-02-01",
      "predicted_cost": 185.20
    },
    {
      "date": "2024-02-02",
      "predicted_cost": 190.50
    }
  ],
  "statistics": {
    "recent_avg_cost": 180.40,
    "predicted_avg_cost": 195.30,
    "trend": "increasing",
    "historical_days": 31,
    "prediction_days": 30
  }
}
```

趋势说明：
- **increasing**: 预测成本上升
- **decreasing**: 预测成本下降
- **stable**: 预测成本稳定

#### 检测异常成本

```
GET /api/finance/anomalies/?provider=all&start_date=2024-01-01&end_date=2024-01-31&threshold=2.0
```

参数：
- `threshold`: 异常阈值（标准差倍数，默认2.0）

返回示例：
```json
{
  "success": true,
  "provider": "all",
  "anomalies": [
    {
      "date": "2024-01-15",
      "cost": 350.00,
      "z_score": 2.5,
      "status": "high"
    }
  ],
  "anomaly_count": 1
}
```

#### 完整分析

```
GET /api/finance/full-analysis/?provider=all&start_date=2024-01-01&end_date=2024-01-31&prediction_days=30
```

返回包含账单摘要、每日分析、成本预测和异常检测的完整报告。

#### 预算比较

```
GET /api/finance/budget-comparison/?provider=all&start_date=2024-01-01&end_date=2024-01-31&daily_budget=200
```

参数：
- `daily_budget`: 每日预算金额

返回示例：
```json
{
  "success": true,
  "comparison": [
    {
      "date": "2024-01-01",
      "cost": 150.50,
      "baseline": 200.00,
      "difference": -49.50,
      "difference_pct": -24.75,
      "status": "within_budget"
    },
    {
      "date": "2024-01-02",
      "cost": 250.30,
      "baseline": 200.00,
      "difference": 50.30,
      "difference_pct": 25.15,
      "status": "over_budget"
    }
  ],
  "summary": {
    "total_cost": 5580.50,
    "total_baseline": 6200.00,
    "total_difference": -619.50,
    "over_budget_days": 8,
    "total_days": 31,
    "over_budget_rate": 25.81
  }
}
```

## Python SDK 使用

### 基本使用

```python
from finance_api.billing_fetch_service import BillingFetchService

# 初始化服务
service = BillingFetchService()

# 获取最近30天的日期范围
start_date, end_date = service.get_last_n_days(30)

# 拉取账单数据
result = service.fetch_all_billing_data(start_date, end_date)

print(f"总成本: {result['total_cost']}")
print(f"每日成本: {result['combined_daily_costs']}")
```

### 成本分析

```python
from finance_api.cost_prediction_service import CostPredictionService

# 初始化预测服务
prediction_service = CostPredictionService()

# 假设已有每日成本数据
daily_costs = {
    '2024-01-01': 150.50,
    '2024-01-02': 200.30,
    # ...
}

# 分析每日成本
analysis = prediction_service.daily_cost_analysis(daily_costs)

# 查看成本水平
for day in analysis['daily_analysis']:
    print(f"{day['date']}: ¥{day['cost']} - {day['description']}")
```

### 成本预测

```python
# 预测未来30天成本
predictions = prediction_service.predict_costs(
    daily_costs, 
    days_ahead=30,
    method='ensemble'
)

if predictions['success']:
    for pred in predictions['predictions']:
        print(f"{pred['date']}: ¥{pred['predicted_cost']}")
    
    # 查看趋势
    print(f"成本趋势: {predictions['statistics']['trend']}")
```

### 异常检测

```python
# 检测异常成本
anomalies = prediction_service.detect_anomalies(daily_costs, threshold=2.0)

for anomaly in anomalies:
    print(f"{anomaly['date']}: ¥{anomaly['cost']} - {anomaly['status']}")
```

## 预测算法

系统使用多种机器学习算法进行成本预测：

1. **线性回归**: 适合成本趋势较为平稳的场景
2. **随机森林**: 适合成本波动较大的场景
3. **移动平均**: 简单的短期预测
4. **集成方法**: 综合多个模型的预测结果（推荐）

特征工程：
- 星期几（工作日/周末模式）
- 月份中的第几天
- 月份（季节性）
- 7天移动平均
- 30天移动平均
- 7天成本标准差

## 项目结构

```
price_finanle/
├── finance_api/
│   ├── alibaba_cloud_service.py       # 阿里云服务
│   ├── tencent_cloud_service.py       # 腾讯云服务
│   ├── billing_fetch_service.py       # 账单拉取服务
│   ├── cost_prediction_service.py     # 成本预测服务
│   ├── views.py                       # Django API视图
│   └── urls.py                        # API路由
├── scripts/
│   └── fetch_billing.py               # 命令行工具
├── requirements.txt                   # Python依赖
└── BILLING_API_DOCS.md               # API文档（本文件）
```

## 常见问题

### 1. 如何获取云服务商的API凭证？

**阿里云**:
1. 登录阿里云控制台
2. 访问 [RAM访问控制](https://ram.console.aliyun.com/users)
3. 创建用户并授权 `AliyunBSSReadOnlyAccess` 权限
4. 创建AccessKey

**腾讯云**:
1. 登录腾讯云控制台
2. 访问 [API密钥管理](https://console.cloud.tencent.com/cam/capi)
3. 创建新的API密钥
4. 确保有账单查看权限

### 2. 预测准确度如何？

预测准确度取决于：
- 历史数据量（建议至少30天）
- 成本模式的规律性
- 是否有突发的业务变化

建议定期更新历史数据以提高预测准确度。

### 3. 如何处理多个云账户？

系统支持同时配置多个云服务商，使用 `provider=all` 参数可以聚合所有账户的数据。

### 4. 数据更新频率建议？

- **账单数据**: 每日拉取一次
- **成本预测**: 每周更新一次
- **异常检测**: 实时或每日检测

## 高级功能

### 1. 自定义预测模型

```python
from finance_api.cost_prediction_service import CostPredictionService

service = CostPredictionService()

# 使用特定算法
predictions = service.predict_costs(
    daily_costs,
    days_ahead=30,
    method='random_forest'  # 可选: linear, random_forest, moving_average, ensemble
)
```

### 2. 调整异常检测敏感度

```python
# threshold越小，检测越敏感
anomalies = service.detect_anomalies(daily_costs, threshold=1.5)  # 更敏感
anomalies = service.detect_anomalies(daily_costs, threshold=3.0)  # 更宽松
```

### 3. 导出数据

```python
from finance_api.billing_fetch_service import BillingFetchService

service = BillingFetchService()
result = service.fetch_all_billing_data(start_date, end_date)

# 导出到JSON文件
service.export_to_json(result, 'billing_report.json')
```

## 性能优化

1. **缓存**: 建议缓存历史账单数据，避免重复请求
2. **批量查询**: 使用日期范围查询而非逐日查询
3. **异步处理**: 对于大量数据，建议使用异步任务

## 安全建议

1. **凭证管理**: 
   - 使用环境变量存储凭证
   - 不要将凭证提交到版本控制
   - 定期轮换API密钥

2. **权限控制**:
   - 使用只读权限的API凭证
   - 限制IP访问白名单

3. **数据保护**:
   - 加密存储敏感账单数据
   - 限制API访问权限

## 支持

如有问题或建议，请联系开发团队或提交Issue。

## 许可证

MIT License
