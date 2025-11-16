import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  DatePicker, 
  Button, 
  Table, 
  message, 
  Spin,
  Select,
  Space,
  Typography,
  Divider
} from 'antd';
import { 
  DollarOutlined, 
  BarChartOutlined, 
  PieChartOutlined,
  LineChartOutlined,
  WalletOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

/**
 * 腾讯云财务信息主页面
 * 提供账单查询、费用统计、消费趋势等功能
 */
export default function HomePage() {
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(30, 'day'),
    dayjs()
  ]);
  const [billOverview, setBillOverview] = useState<any>(null);
  const [costStatistics, setCostStatistics] = useState<any>(null);
  const [accountBalance, setAccountBalance] = useState<any>(null);
  const [consumptionTrend, setConsumptionTrend] = useState<any>(null);
  const [selectedAction, setSelectedAction] = useState<string>('bill-overview');

  /**
   * 获取财务数据
   */
  const fetchFinanceData = async () => {
    if (!dateRange[0] || !dateRange[1]) {
      message.error('请选择日期范围');
      return;
    }

    setLoading(true);
    try {
      const beginTime = dateRange[0].format('YYYY-MM-DD');
      const endTime = dateRange[1].format('YYYY-MM-DD');

      // 获取账单概览
      const overviewResponse = await fetch(
        `/api/finance?action=bill-overview&beginTime=${beginTime}&endTime=${endTime}`
      );
      const overviewData = await overviewResponse.json();
      if (overviewData.success) {
        setBillOverview(overviewData.data);
      }

      // 获取费用统计
      const statisticsResponse = await fetch(
        `/api/finance?action=cost-statistics&beginTime=${beginTime}&endTime=${endTime}`
      );
      const statisticsData = await statisticsResponse.json();
      if (statisticsData.success) {
        setCostStatistics(statisticsData.data);
      }

      // 获取账户余额
      const balanceResponse = await fetch('/api/finance?action=account-balance');
      const balanceData = await balanceResponse.json();
      if (balanceData.success) {
        setAccountBalance(balanceData.data);
      }

      // 获取消费趋势
      const trendResponse = await fetch(
        `/api/finance?action=consumption-trend&beginTime=${beginTime}&endTime=${endTime}`
      );
      const trendData = await trendResponse.json();
      if (trendData.success) {
        setConsumptionTrend(trendData.data);
      }

      message.success('数据获取成功');
    } catch (error) {
      console.error('获取数据失败:', error);
      message.error('获取数据失败，请检查网络连接和API配置');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFinanceData();
  }, []);

  /**
   * 格式化金额显示
   */
  const formatAmount = (amount: number) => {
    return `¥${(amount / 100).toFixed(2)}`;
  };

  /**
   * 准备图表数据
   */
  const prepareChartData = (data: any) => {
    if (!data || !data.SummaryOverview) return [];
    
    return data.SummaryOverview.map((item: any) => ({
      name: item.PayMode,
      value: item.RealCost / 100,
      color: getRandomColor()
    }));
  };

  /**
   * 获取随机颜色
   */
  const getRandomColor = () => {
    const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2'];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  /**
   * 表格列定义
   */
  const columns = [
    {
      title: '付费模式',
      dataIndex: 'PayMode',
      key: 'PayMode',
    },
    {
      title: '实际费用',
      dataIndex: 'RealCost',
      key: 'RealCost',
      render: (value: number) => formatAmount(value),
    },
    {
      title: '现金费用',
      dataIndex: 'CashPayAmount',
      key: 'CashPayAmount',
      render: (value: number) => formatAmount(value),
    },
    {
      title: '赠送费用',
      dataIndex: 'IncentivePayAmount',
      key: 'IncentivePayAmount',
      render: (value: number) => formatAmount(value),
    },
  ];

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <Title level={2} style={{ marginBottom: '24px', textAlign: 'center' }}>
        <DollarOutlined style={{ marginRight: '8px' }} />
        腾讯云财务信息管理系统
      </Title>

      {/* 控制面板 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={16} align="middle">
          <Col span={8}>
            <Text strong>日期范围：</Text>
            <RangePicker
              value={dateRange}
              onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
              style={{ marginLeft: '8px' }}
            />
          </Col>
          <Col span={8}>
            <Text strong>查询类型：</Text>
            <Select
              value={selectedAction}
              onChange={setSelectedAction}
              style={{ marginLeft: '8px', width: '200px' }}
            >
              <Option value="bill-overview">账单概览</Option>
              <Option value="cost-statistics">费用统计</Option>
              <Option value="account-balance">账户余额</Option>
              <Option value="consumption-trend">消费趋势</Option>
            </Select>
          </Col>
          <Col span={8}>
            <Space>
              <Button 
                type="primary" 
                onClick={fetchFinanceData}
                loading={loading}
                icon={<ReloadOutlined />}
              >
                刷新数据
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      <Spin spinning={loading}>
        {/* 统计卡片 */}
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总费用"
                value={billOverview?.SummaryOverview?.reduce((sum: number, item: any) => sum + item.RealCost, 0) / 100 || 0}
                precision={2}
                valueStyle={{ color: '#3f8600' }}
                prefix="¥"
                suffix="元"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="账户余额"
                value={accountBalance?.Balance / 100 || 0}
                precision={2}
                valueStyle={{ color: '#1890ff' }}
                prefix="¥"
                suffix="元"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="现金支付"
                value={billOverview?.SummaryOverview?.reduce((sum: number, item: any) => sum + item.CashPayAmount, 0) / 100 || 0}
                precision={2}
                valueStyle={{ color: '#cf1322' }}
                prefix="¥"
                suffix="元"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="赠送金额"
                value={billOverview?.SummaryOverview?.reduce((sum: number, item: any) => sum + item.IncentivePayAmount, 0) / 100 || 0}
                precision={2}
                valueStyle={{ color: '#faad14' }}
                prefix="¥"
                suffix="元"
              />
            </Card>
          </Col>
        </Row>

        {/* 图表和表格 */}
        <Row gutter={16}>
          <Col span={12}>
            <Card title="费用分布" extra={<PieChartOutlined />}>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={prepareChartData(billOverview)}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {prepareChartData(billOverview).map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `¥${value.toFixed(2)}`} />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="消费趋势" extra={<LineChartOutlined />}>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={consumptionTrend?.SummaryOverview || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="PayMode" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => `¥${(value / 100).toFixed(2)}`} />
                  <Line type="monotone" dataKey="RealCost" stroke="#1890ff" />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>

        {/* 详细数据表格 */}
        <Card title="详细账单数据" style={{ marginTop: '24px' }}>
          <Table
            columns={columns}
            dataSource={billOverview?.SummaryOverview || []}
            rowKey="PayMode"
            pagination={false}
          />
        </Card>
      </Spin>
    </div>
  );
} 