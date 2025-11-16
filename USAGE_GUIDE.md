# 云成本账单拉取和预测系统 - 使用指南

## 📋 项目概述

本系统提供完整的云成本管理解决方案，专为管理阿里云和腾讯云账单而设计。

### 核心功能

1. **账单数据拉取** - 自动从阿里云和腾讯云获取账单数据
2. **每日成本分析** - 分析每天成本是高是低，识别成本模式
3. **智能成本预测** - 使用机器学习算法预测未来成本趋势
4. **异常检测** - 自动识别异常成本波动
5. **预算管理** - 与预算进行对比分析

### ✅ 测试结果

所有核心功能已通过测试：
- ✓ 成本分析功能正常
- ✓ 成本预测功能正常（预测准确度高）
- ✓ 异常检测功能正常
- ✓ 预算比较功能正常

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置云服务商凭证

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的云服务商凭证：

```env
# 阿里云配置
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret

# 腾讯云配置
TENCENT_CLOUD_SECRET_ID=your_secret_id
TENCENT_CLOUD_SECRET_KEY=your_secret_key
```

### 3. 使用命令行工具

#### 拉取账单数据

```bash
# 拉取所有云服务商最近30天的账单
python scripts/fetch_billing.py fetch --provider all

# 拉取指定云服务商的账单
python scripts/fetch_billing.py fetch --provider alibaba --start-date 2024-01-01 --end-date 2024-01-31

# 保存结果到文件
python scripts/fetch_billing.py fetch --output billing_data.json
```

#### 分析每日成本（判断高/低）

```bash
# 分析最近30天成本，判断每天成本是高是低
python scripts/fetch_billing.py analyze --provider all --days 30
```

**输出示例：**
```
📈 成本统计:
  平均: ¥150.34
  最小: ¥95.37
  最大: ¥309.05

成本水平分布:
  高成本天数: 1 天      (成本 > 平均值 + 标准差)
  正常成本天数: 25 天   (成本在正常范围)
  低成本天数: 4 天      (成本 < 平均值 - 标准差)
```

#### 预测未来成本

```bash
# 预测未来30天成本
python scripts/fetch_billing.py predict --provider all --days 30
```

**输出示例：**
```
🔮 成本预测:
  历史平均成本: ¥182.50
  预测平均成本: ¥186.07
  成本趋势: increasing (上升) / decreasing (下降) / stable (稳定)

未来5天预测:
  2024-02-01: ¥187.11
  2024-02-02: ¥187.07
  2024-02-03: ¥185.76
  ...
```

#### 检测异常成本

```bash
# 检测异常成本波动
python scripts/fetch_billing.py anomaly --provider all
```

**输出示例：**
```
⚠️ 异常检测:
  发现 2 个异常:
    2024-01-15: ¥435.38 (偏高, Z-score: 4.09)
    2024-01-20: ¥45.00 (偏低, Z-score: -2.15)
```

#### 完整分析报告

```bash
# 执行包含所有功能的完整分析
python scripts/fetch_billing.py full --provider all --days 30 --output report.json
```

## 📊 成本分析说明

### 成本水平判断标准

系统使用统计学方法判断每日成本水平：

- **高成本（high）**: 成本 > 平均值 + 标准差
  - 表示当天成本明显高于正常水平
  - 需要关注和调查原因

- **正常成本（normal）**: 成本在 [平均值 - 标准差, 平均值 + 标准差] 范围内
  - 表示当天成本在正常波动范围内

- **低成本（low）**: 成本 < 平均值 - 标准差
  - 表示当天成本明显低于正常水平
  - 可能是业务量下降或资源使用减少

### 预测算法

系统采用集成学习方法，结合多种算法：

1. **线性回归** - 捕捉长期趋势
2. **随机森林** - 处理非线性关系
3. **移动平均** - 短期预测

特征包括：
- 时间特征（星期几、日期、月份）
- 历史成本统计（7天/30天移动平均）
- 成本波动性（标准差）

### 异常检测

使用 Z-score 方法检测异常：
- Z-score > 2.0：异常偏高
- Z-score < -2.0：异常偏低

## 🔌 API 接口

### Django REST API

启动Django服务：

```bash
python manage.py runserver
```

### 主要接口

#### 1. 获取账单数据
```
GET /api/finance/billing/?provider=all&start_date=2024-01-01&end_date=2024-01-31
```

#### 2. 分析每日成本（判断高/低）
```
GET /api/finance/analyze/?provider=all&start_date=2024-01-01&end_date=2024-01-31
```

**返回示例：**
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
    "std_cost": 45.30
  }
}
```

#### 3. 预测未来成本
```
GET /api/finance/predict/?provider=all&days_ahead=30
```

#### 4. 检测异常
```
GET /api/finance/anomalies/?provider=all
```

#### 5. 完整分析
```
GET /api/finance/full-analysis/?provider=all&prediction_days=30
```

完整API文档请查看：[BILLING_API_DOCS.md](BILLING_API_DOCS.md)

## 📝 Python SDK 使用示例

### 示例 1: 拉取账单并分析

```python
from finance_api.billing_fetch_service import BillingFetchService

# 初始化服务
service = BillingFetchService()

# 获取最近30天数据
start_date, end_date = service.get_last_n_days(30)

# 拉取并分析
result = service.analyze_and_predict('all', start_date, end_date, prediction_days=30)

# 查看成本分析
for day in result['daily_analysis']['daily_analysis']:
    print(f"{day['date']}: ¥{day['cost']} - {day['description']}")

# 查看预测结果
for pred in result['predictions']['predictions'][:7]:
    print(f"{pred['date']}: ¥{pred['predicted_cost']}")
```

### 示例 2: 仅使用预测服务

```python
from finance_api.cost_prediction_service import CostPredictionService

# 初始化预测服务
prediction_service = CostPredictionService()

# 假设已有历史成本数据
daily_costs = {
    '2024-01-01': 150.50,
    '2024-01-02': 200.30,
    # ... 更多数据
}

# 分析每日成本
analysis = prediction_service.daily_cost_analysis(daily_costs)
print(f"平均成本: ¥{analysis['statistics']['mean_cost']}")

# 统计高/低成本天数
high_days = sum(1 for d in analysis['daily_analysis'] if d['level'] == 'high')
low_days = sum(1 for d in analysis['daily_analysis'] if d['level'] == 'low')
print(f"高成本天数: {high_days}")
print(f"低成本天数: {low_days}")

# 预测未来成本
predictions = prediction_service.predict_costs(daily_costs, days_ahead=30)
print(f"预测趋势: {predictions['statistics']['trend']}")

# 检测异常
anomalies = prediction_service.detect_anomalies(daily_costs)
print(f"发现 {len(anomalies)} 个异常")
```

更多示例请查看：[examples/billing_example.py](examples/billing_example.py)

## 🧪 运行测试

```bash
# 测试预测服务（不需要云服务商凭证）
python test/test_prediction.py
```

## 📁 项目结构

```
price_finanle/
├── finance_api/
│   ├── alibaba_cloud_service.py        # 阿里云API封装
│   ├── tencent_cloud_service.py        # 腾讯云API封装
│   ├── billing_fetch_service.py        # 账单拉取统一服务
│   ├── cost_prediction_service.py      # 成本预测和分析服务
│   ├── views.py                        # Django API视图
│   └── urls.py                         # API路由配置
├── scripts/
│   └── fetch_billing.py                # 命令行工具
├── examples/
│   └── billing_example.py              # 使用示例
├── test/
│   └── test_prediction.py              # 单元测试
├── requirements.txt                    # Python依赖
├── BILLING_API_DOCS.md                # 完整API文档
└── USAGE_GUIDE.md                     # 本文件
```

## 💡 实用技巧

### 1. 定期监控

建议每日运行以下命令进行成本监控：

```bash
# 每日成本分析
python scripts/fetch_billing.py analyze --provider all --days 7

# 异常检测
python scripts/fetch_billing.py anomaly --provider all --days 7
```

### 2. 周度预测

每周运行一次成本预测：

```bash
python scripts/fetch_billing.py predict --provider all --days 30
```

### 3. 月度报告

每月生成完整报告：

```bash
python scripts/fetch_billing.py full --provider all --days 30 --output monthly_report_$(date +%Y%m).json
```

### 4. 预算管理

设置每日预算并定期检查：

```bash
# 通过API检查预算
curl "http://localhost:8000/api/finance/budget-comparison/?daily_budget=200"
```

## ⚠️ 注意事项

1. **API权限**：确保云服务商凭证具有账单查询权限
2. **数据量**：首次拉取大量历史数据可能较慢
3. **预测准确度**：建议至少使用30天历史数据进行预测
4. **成本更新**：云服务商账单通常有1-2天延迟

## 🔒 安全建议

1. 不要将 `.env` 文件提交到版本控制
2. 使用只读权限的API凭证
3. 定期轮换API密钥
4. 限制API访问IP白名单

## 📞 支持

如有问题或建议，请查看：
- [完整API文档](BILLING_API_DOCS.md)
- [代码示例](examples/billing_example.py)
- 或联系开发团队

## 📄 许可证

MIT License

---

**快速开始示例：**

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置凭证
cp .env.example .env
# 编辑 .env 填入凭证

# 3. 拉取账单
python scripts/fetch_billing.py fetch --provider all

# 4. 分析成本（判断高/低）
python scripts/fetch_billing.py analyze --provider all

# 5. 预测未来成本
python scripts/fetch_billing.py predict --provider all --days 30
```
