/**
 * 腾讯云财务信息API测试
 * 用于验证API功能是否正常工作
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:3000/api';

/**
 * 测试API连接
 */
async function testApiConnection() {
  try {
    console.log('🔍 测试API连接...');
    
    const response = await axios.get(`${BASE_URL}/finance?action=account-balance`);
    
    if (response.status === 200) {
      console.log('✅ API连接成功');
      console.log('📊 响应数据:', JSON.stringify(response.data, null, 2));
    } else {
      console.log('❌ API连接失败:', response.status);
    }
  } catch (error) {
    console.log('❌ API连接错误:', error.message);
    
    if (error.response) {
      console.log('📋 错误详情:', error.response.data);
    }
  }
}

/**
 * 测试账单概览API
 */
async function testBillOverview() {
  try {
    console.log('\n📊 测试账单概览API...');
    
    const beginTime = '2024-01-01';
    const endTime = '2024-01-31';
    
    const response = await axios.get(
      `${BASE_URL}/finance?action=bill-overview&beginTime=${beginTime}&endTime=${endTime}`
    );
    
    if (response.status === 200) {
      console.log('✅ 账单概览API测试成功');
      console.log('📊 响应数据:', JSON.stringify(response.data, null, 2));
    }
  } catch (error) {
    console.log('❌ 账单概览API测试失败:', error.message);
  }
}

/**
 * 测试费用统计API
 */
async function testCostStatistics() {
  try {
    console.log('\n💰 测试费用统计API...');
    
    const beginTime = '2024-01-01';
    const endTime = '2024-01-31';
    
    const response = await axios.get(
      `${BASE_URL}/finance?action=cost-statistics&beginTime=${beginTime}&endTime=${endTime}`
    );
    
    if (response.status === 200) {
      console.log('✅ 费用统计API测试成功');
      console.log('📊 响应数据:', JSON.stringify(response.data, null, 2));
    }
  } catch (error) {
    console.log('❌ 费用统计API测试失败:', error.message);
  }
}

/**
 * 测试消费趋势API
 */
async function testConsumptionTrend() {
  try {
    console.log('\n📈 测试消费趋势API...');
    
    const beginTime = '2024-01-01';
    const endTime = '2024-01-31';
    
    const response = await axios.get(
      `${BASE_URL}/finance?action=consumption-trend&beginTime=${beginTime}&endTime=${endTime}`
    );
    
    if (response.status === 200) {
      console.log('✅ 消费趋势API测试成功');
      console.log('📊 响应数据:', JSON.stringify(response.data, null, 2));
    }
  } catch (error) {
    console.log('❌ 消费趋势API测试失败:', error.message);
  }
}

/**
 * 运行所有测试
 */
async function runAllTests() {
  console.log('🚀 开始运行腾讯云财务信息API测试');
  console.log('=====================================');
  
  await testApiConnection();
  await testBillOverview();
  await testCostStatistics();
  await testConsumptionTrend();
  
  console.log('\n🎉 测试完成！');
  console.log('\n📋 注意事项:');
  console.log('1. 确保应用正在运行 (npm run dev)');
  console.log('2. 确保环境变量已正确配置');
  console.log('3. 确保腾讯云API凭证有效');
}

// 如果直接运行此文件，则执行测试
if (require.main === module) {
  runAllTests().catch(console.error);
}

module.exports = {
  testApiConnection,
  testBillOverview,
  testCostStatistics,
  testConsumptionTrend,
  runAllTests
}; 