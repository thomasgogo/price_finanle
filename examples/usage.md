# 腾讯云财务信息管理系统 - 使用示例

## 快速开始

### 1. 环境准备

确保您的系统已安装：
- Node.js (版本 16 或更高)
- npm 或 yarn

### 2. 项目设置

```bash
# 克隆项目（如果是从Git仓库）
git clone <repository-url>
cd price_finanle

# 安装依赖
npm install

# 配置环境变量
cp env.example .env.local
```

### 3. 配置腾讯云API凭证

编辑 `.env.local` 文件：

```env
TENCENT_SECRET_ID=xxxxxxxx
TENCENT_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TENCENT_REGION=ap-guangzhou
```

### 4. 启动应用

```bash
npm run dev
```

访问 http://localhost:3000 查看应用。

## 功能使用示例

### 查看账单概览

1. 在页面顶部选择日期范围
2. 选择"账单概览"查询类型
3. 点击"刷新数据"按钮
4. 查看统计卡片和图表数据

### 分析费用分布

1. 选择"费用统计"查询类型
2. 设置合适的时间范围
3. 查看饼图显示的费用分布
4. 分析各产品和服务的费用占比

### 监控消费趋势

1. 选择"消费趋势"查询类型
2. 选择较长的时间范围（如3个月）
3. 查看折线图显示的消费趋势
4. 分析消费变化规律

### 查看账户余额

1. 选择"账户余额"查询类型
2. 点击"刷新数据"按钮
3. 查看当前账户余额信息

## API调用示例

### 使用curl测试API

```bash
# 获取账单概览
curl "http://localhost:3000/api/finance?action=bill-overview&beginTime=2024-01-01&endTime=2024-01-31"

# 获取费用统计
curl "http://localhost:3000/api/finance?action=cost-statistics&beginTime=2024-01-01&endTime=2024-01-31"

# 获取账户余额
curl "http://localhost:3000/api/finance?action=account-balance"
```

### 使用JavaScript调用API

```javascript
// 获取账单概览
const response = await fetch('/api/finance?action=bill-overview&beginTime=2024-01-01&endTime=2024-01-31');
const data = await response.json();
console.log(data);

// 获取费用统计
const statsResponse = await fetch('/api/finance?action=cost-statistics&beginTime=2024-01-01&endTime=2024-01-31');
const statsData = await statsResponse.json();
console.log(statsData);
```

## 常见问题

### Q: 如何获取腾讯云API凭证？

A: 
1. 登录腾讯云控制台
2. 访问 [API密钥管理](https://console.cloud.tencent.com/cam/capi)
3. 创建新的API密钥
4. 复制SecretId和SecretKey

### Q: 为什么API调用失败？

A: 请检查：
1. 环境变量是否正确配置
2. API凭证是否有效
3. 网络连接是否正常
4. 控制台错误信息

### Q: 如何自定义图表样式？

A: 
1. 修改 `pages/index.tsx` 中的图表配置
2. 调整颜色、大小、标签等属性
3. 参考Recharts官方文档

### Q: 如何添加新的财务功能？

A: 
1. 在 `lib/tencentCloudService.ts` 中添加新方法
2. 在 `pages/api/finance.ts` 中添加API路由
3. 在前端页面中添加UI组件

## 数据格式说明

### 账单概览数据格式

```json
{
  "success": true,
  "data": {
    "SummaryOverview": [
      {
        "PayMode": "postpaid",
        "RealCost": 100000,
        "CashPayAmount": 80000,
        "IncentivePayAmount": 20000
      }
    ]
  }
}
```

### 费用统计数据格式

```json
{
  "success": true,
  "data": {
    "SummaryOverview": [
      {
        "BusinessCode": "CVM",
        "BusinessCodeName": "云服务器",
        "RealCost": 50000
      }
    ]
  }
}
```

### 账户余额数据格式

```json
{
  "success": true,
  "data": {
    "Balance": 1000000,
    "Uin": "123456789"
  }
}
```

## 最佳实践

1. **定期备份**: 定期备份重要的财务数据
2. **权限管理**: 合理设置API密钥权限
3. **监控告警**: 设置费用监控和告警
4. **数据分析**: 定期分析消费趋势，优化成本
5. **安全防护**: 保护API凭证，避免泄露

## 技术支持

如果您遇到问题，请：

1. 查看浏览器控制台错误信息
2. 检查网络连接和API配置
3. 参考腾讯云API文档
4. 提交Issue描述问题 