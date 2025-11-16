import { NextApiRequest, NextApiResponse } from 'next';
import { TencentCloudFinanceService } from '../../lib/tencentCloudService';

/**
 * 腾讯云财务信息API路由
 * 提供账单查询、费用统计等接口
 */
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: '只支持GET请求' });
  }

  try {
    // 从环境变量获取腾讯云凭证
    const secretId = process.env.TENCENT_SECRET_ID;
    const secretKey = process.env.TENCENT_SECRET_KEY;
    const region = process.env.TENCENT_REGION || 'ap-guangzhou';

    if (!secretId || !secretKey) {
      return res.status(400).json({ 
        error: '缺少腾讯云凭证，请设置TENCENT_SECRET_ID和TENCENT_SECRET_KEY环境变量' 
      });
    }

    const service = new TencentCloudFinanceService(secretId, secretKey, region);
    const { action, beginTime, endTime, payMode } = req.query;

    let result;

    switch (action) {
      case 'bill-overview':
        if (!beginTime || !endTime) {
          return res.status(400).json({ error: '账单概览需要提供beginTime和endTime参数' });
        }
        result = await service.getBillOverview(beginTime as string, endTime as string);
        break;

      case 'bill-details':
        if (!beginTime || !endTime) {
          return res.status(400).json({ error: '详细账单需要提供beginTime和endTime参数' });
        }
        result = await service.getBillDetails(beginTime as string, endTime as string, payMode as string);
        break;

      case 'cost-statistics':
        if (!beginTime || !endTime) {
          return res.status(400).json({ error: '费用统计需要提供beginTime和endTime参数' });
        }
        result = await service.getCostStatistics(beginTime as string, endTime as string);
        break;

      case 'account-balance':
        result = await service.getAccountBalance();
        break;

      case 'consumption-trend':
        if (!beginTime || !endTime) {
          return res.status(400).json({ error: '消费趋势需要提供beginTime和endTime参数' });
        }
        result = await service.getConsumptionTrend(beginTime as string, endTime as string);
        break;

      default:
        return res.status(400).json({ 
          error: '无效的action参数，支持的值：bill-overview, bill-details, cost-statistics, account-balance, consumption-trend' 
        });
    }

    res.status(200).json({
      success: true,
      data: result,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('API错误:', error);
    res.status(500).json({
      success: false,
      error: error.message || '服务器内部错误',
      timestamp: new Date().toISOString()
    });
  }
} 