# 云成本账单拉取和预测系统

## 🎯 项目简介

这是一个完整的云成本管理系统，支持从**阿里云**和**腾讯云**自动拉取账单数据，并使用机器学习算法进行成本分析和预测。

### ✨ 核心功能

1. **账单数据拉取** - 使用Python从阿里云/腾讯云拉取账单
2. **成本高低分析** - 自动判断每天的成本是高还是低
3. **成本预测** - 预测未来成本趋势
4. **异常检测** - 自动发现异常成本
5. **预算管理** - 与预算进行对比

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置凭证

```bash
cp .env.example .env
# 编辑 .env 文件，填入云服务商的API凭证
```

### 3. 使用命令行工具

#### 拉取账单数据
```bash
# 拉取所有云服务商最近30天的账单
python scripts/fetch_billing.py fetch --provider all
```

#### 分析成本（判断高/低）
```bash
# 分析每天成本是高还是低
python scripts/fetch_billing.py analyze --provider all --days 30
```

**输出示例：**
```
成本水平分布:
  高成本天数: 1 天      (成本偏高，需要关注)
  正常成本天数: 25 天   (成本正常)
  低成本天数: 4 天      (成本偏低)
```

#### 预测未来成本
```bash
# 预测未来30天的成本
python scripts/fetch_billing.py predict --provider all --days 30
```

**输出示例：**
```
预测结果:
  历史平均成本: ¥182.50
  预测平均成本: ¥186.07
  成本趋势: increasing (上升)

未来5天预测:
  2024-02-01: ¥187.11
  2024-02-02: ¥187.07
  2024-02-03: ¥185.76
```

#### 完整分析
```bash
# 执行完整的分析（包含成本分析、预测、异常检测）
python scripts/fetch_billing.py full --provider all --output report.json
```

## 📊 成本分析说明

### 如何判断成本高低？

系统使用统计学方法自动判断：

- **高成本（high）**: 当天成本 > 平均值 + 标准差
  - 表示成本明显偏高，需要关注
  
- **正常成本（normal）**: 成本在正常范围内
  - 表示成本波动正常
  
- **低成本（low）**: 当天成本 < 平均值 - 标准差
  - 表示成本明显偏低

这种方法无需手动设置阈值，系统会根据历史数据自动计算。

## 🔌 API 接口

### 启动服务

```bash
python manage.py runserver
```

### 主要接口

#### 1. 分析每日成本（判断高/低）
```
GET /api/finance/analyze/?provider=all&start_date=2024-01-01&end_date=2024-01-31
```

#### 2. 预测未来成本
```
GET /api/finance/predict/?provider=all&days_ahead=30
```

#### 3. 检测异常成本
```
GET /api/finance/anomalies/?provider=all
```

#### 4. 完整分析报告
```
GET /api/finance/full-analysis/?provider=all&prediction_days=30
```

完整API文档: [BILLING_API_DOCS.md](BILLING_API_DOCS.md)

## 💻 Python SDK 使用

```python
from finance_api.billing_fetch_service import BillingFetchService

# 初始化服务
service = BillingFetchService()

# 获取最近30天数据并分析
start_date, end_date = service.get_last_n_days(30)
result = service.analyze_and_predict('all', start_date, end_date, prediction_days=30)

# 查看每日成本分析（高/低）
for day in result['daily_analysis']['daily_analysis']:
    print(f"{day['date']}: ¥{day['cost']} - {day['description']}")

# 查看成本预测
for pred in result['predictions']['predictions'][:7]:
    print(f"{pred['date']}: ¥{pred['predicted_cost']}")
```

更多示例: [examples/billing_example.py](examples/billing_example.py)

## ✅ 测试

运行单元测试验证功能：

```bash
python test/test_prediction.py
```

测试结果：
```
测试总结:
  成本分析: ✓ 通过
  成本预测: ✓ 通过
  异常检测: ✓ 通过
  预算比较: ✓ 通过

总计: 4/4 测试通过
✓ 所有测试通过！
```

## 📚 文档

- **[使用指南](USAGE_GUIDE.md)** - 详细的使用说明和示例
- **[API文档](BILLING_API_DOCS.md)** - 完整的API接口文档
- **[项目总结](PROJECT_SUMMARY.md)** - 项目功能和实现总结

## 🎓 支持的云服务商

- ✅ 阿里云 (Alibaba Cloud)
- ✅ 腾讯云 (Tencent Cloud)

## 📦 项目结构

```
price_finanle/
├── finance_api/                      # 核心服务
│   ├── alibaba_cloud_service.py     # 阿里云API封装
│   ├── tencent_cloud_service.py     # 腾讯云API封装
│   ├── billing_fetch_service.py     # 账单拉取服务
│   ├── cost_prediction_service.py   # 成本预测服务
│   ├── views.py                     # Django API视图
│   └── urls.py                      # API路由
├── scripts/
│   └── fetch_billing.py             # 命令行工具
├── examples/
│   └── billing_example.py           # 使用示例
├── test/
│   └── test_prediction.py           # 单元测试
└── docs/
    ├── USAGE_GUIDE.md               # 使用指南
    ├── BILLING_API_DOCS.md          # API文档
    └── PROJECT_SUMMARY.md           # 项目总结
```

## 🔑 配置说明

在 `.env` 文件中配置云服务商凭证：

```env
# 阿里云配置
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret

# 腾讯云配置
TENCENT_CLOUD_SECRET_ID=your_secret_id
TENCENT_CLOUD_SECRET_KEY=your_secret_key
```

## 💡 使用场景

1. **每日成本监控** - 每天自动分析成本是否异常
2. **成本预测** - 提前预知未来成本趋势
3. **预算管理** - 监控是否超出预算
4. **多云管理** - 统一管理多个云服务商的成本
5. **成本优化** - 识别成本异常，及时采取措施

## 🛡️ 安全建议

1. 不要将 `.env` 文件提交到版本控制
2. 使用只读权限的API凭证
3. 定期轮换API密钥
4. 限制API访问IP白名单

## 📄 许可证

MIT License

---

**问题反馈**: 如有问题或建议，请查看文档或联系开发团队
