import os
from datetime import datetime, timedelta
from tencentcloud.common.credential import Credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.billing.v20180709.client import BillingClient
from tencentcloud.billing.v20180709.models import (
    DescribeAccountBalanceRequest,
    DescribeBillDetailRequest,
    DescribeBillSummaryByProductRequest,
    DescribeDosageCosDetailByDateRequest
)

class TencentCloudService:
    def __init__(self):
        self.secret_id = os.environ.get("TENCENT_CLOUD_SECRET_ID")
        self.secret_key = os.environ.get("TENCENT_CLOUD_SECRET_KEY")
        self.region = os.environ.get("TENCENT_CLOUD_REGION", "ap-guangzhou")

        cred = Credential(self.secret_id, self.secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "billing.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = BillingClient(cred, self.region, clientProfile)

    def get_account_balance(self):
        """获取账户余额"""
        try:
            req = DescribeAccountBalanceRequest()
            response = self.client.DescribeAccountBalance(req)
            return response.Balance
        except TencentCloudSDKException as err:
            print(f"Error querying Tencent Cloud account balance: {err}")
            return None

    def get_billing_data(self, start_date, end_date):
        """
        获取账单明细数据
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        :return: 账单数据列表
        """
        try:
            billing_data = []
            
            # 将日期转换为账期格式 YYYY-MM
            start_month = start_date[:7]
            end_month = end_date[:7]
            
            # 生成需要查询的月份列表
            months = self._generate_months(start_month, end_month)
            
            for month in months:
                offset = 0
                limit = 100
                
                while True:
                    req = DescribeBillDetailRequest()
                    req.Month = month
                    req.Offset = offset
                    req.Limit = limit
                    
                    response = self.client.DescribeBillDetail(req)
                    
                    if not response.DetailSet:
                        break
                    
                    for item in response.DetailSet:
                        # 过滤日期范围
                        pay_time = item.PayTime if hasattr(item, 'PayTime') else ''
                        item_date = pay_time[:10] if len(pay_time) >= 10 else month + '-01'
                        
                        if start_date <= item_date <= end_date:
                            billing_data.append({
                                'date': item_date,
                                'product_name': item.ProductName if hasattr(item, 'ProductName') else '',
                                'cost': float(item.Cost) if hasattr(item, 'Cost') else 0.0,
                                'currency': 'CNY',
                                'resource_id': item.ResourceId if hasattr(item, 'ResourceId') else '',
                                'region': item.Region if hasattr(item, 'Region') else ''
                            })
                    
                    # 检查是否还有更多数据
                    if len(response.DetailSet) < limit:
                        break
                    
                    offset += limit
            
            return billing_data
        except TencentCloudSDKException as err:
            print(f"Error querying Tencent Cloud billing data: {err}")
            return []

    def get_daily_costs(self, start_date, end_date):
        """
        获取每日成本汇总
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        :return: 每日成本字典 {date: cost}
        """
        try:
            billing_data = self.get_billing_data(start_date, end_date)
            daily_costs = {}
            
            for item in billing_data:
                date = item['date']
                cost = item['cost']
                if date in daily_costs:
                    daily_costs[date] += cost
                else:
                    daily_costs[date] = cost
            
            return daily_costs
        except Exception as e:
            print(f"Error calculating daily costs: {e}")
            return {}

    def get_product_summary(self, start_date, end_date):
        """
        获取按产品汇总的账单
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        :return: 产品成本汇总列表
        """
        try:
            product_summary = []
            
            # 将日期转换为账期格式
            start_month = start_date[:7]
            end_month = end_date[:7]
            months = self._generate_months(start_month, end_month)
            
            for month in months:
                req = DescribeBillSummaryByProductRequest()
                req.Month = month
                
                response = self.client.DescribeBillSummaryByProduct(req)
                
                if response.SummaryDetail:
                    for item in response.SummaryDetail:
                        product_summary.append({
                            'month': month,
                            'product_name': item.ProductName if hasattr(item, 'ProductName') else '',
                            'total_cost': float(item.TotalCost) if hasattr(item, 'TotalCost') else 0.0,
                            'real_total_cost': float(item.RealTotalCost) if hasattr(item, 'RealTotalCost') else 0.0
                        })
            
            return product_summary
        except TencentCloudSDKException as err:
            print(f"Error querying Tencent Cloud product summary: {err}")
            return []

    def _generate_months(self, start_month, end_month):
        """生成月份列表"""
        months = []
        current = datetime.strptime(start_month, '%Y-%m')
        end = datetime.strptime(end_month, '%Y-%m')
        
        while current <= end:
            months.append(current.strftime('%Y-%m'))
            # 移动到下个月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return months