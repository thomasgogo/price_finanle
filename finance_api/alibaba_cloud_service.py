import os
from datetime import datetime, timedelta
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bssopenapi20171214.client import Client as BssClient
from alibabacloud_bssopenapi20171214 import models as bss_models
from alibabacloud_tea_util import models as util_models

class AlibabaCloudService:
    def __init__(self):
        # 使用空字符串作为默认值，避免类型检查因 None 报错
        self.access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "")
        self.access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "")
        self.endpoint = os.environ.get("ALIBABA_CLOUD_BSS_ENDPOINT", "business.aliyuncs.com")

        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
        )
        config.endpoint = self.endpoint
        self.client = BssClient(config)

    def get_account_balance(self):
        """获取账户余额"""
        try:
            # 直接调用无参数方法以适配 SDK 的签名
            response = self.client.query_account_balance()
            data = getattr(response.body, "data", None)
            return getattr(data, "available_amount", None)
        except Exception as e:
            print(f"Error querying Alibaba Cloud account balance: {e}")
            return None

    def get_billing_data(self, start_date, end_date, billing_cycle=None):
        """
        获取账单数据
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        :param billing_cycle: 账期 (YYYY-MM), 如果指定则按月账单查询
        :return: 账单数据列表
        """
        try:
            billing_data = []
            
            # 如果指定了billing_cycle，使用月账单查询
            if billing_cycle:
                request = bss_models.QueryBillRequest(
                    billing_cycle=billing_cycle,
                    page_num=1,
                    page_size=300
                )
                response = self.client.query_bill(request)
                if response.body.data and response.body.data.items:
                    for item in response.body.data.items.item:
                        billing_data.append({
                            'date': item.billing_date if hasattr(item, 'billing_date') else billing_cycle,
                            'product_name': item.product_name if hasattr(item, 'product_name') else '',
                            'cost': float(item.pretax_amount) if hasattr(item, 'pretax_amount') else 0.0,
                            'currency': item.currency if hasattr(item, 'currency') else 'CNY',
                            'subscription_type': item.subscription_type if hasattr(item, 'subscription_type') else ''
                        })
            else:
                # 按日期范围查询
                request = bss_models.QueryInstanceBillRequest(
                    billing_cycle=start_date[:7],  # YYYY-MM格式
                    page_num=1,
                    page_size=300
                )
                response = self.client.query_instance_bill(request)
                if response.body.data and response.body.data.items:
                    for item in response.body.data.items.item:
                        # 过滤日期范围
                        item_date = item.billing_date if hasattr(item, 'billing_date') else ''
                        if start_date <= item_date <= end_date:
                            billing_data.append({
                                'date': item_date,
                                'product_name': item.product_name if hasattr(item, 'product_name') else '',
                                'cost': float(item.pretax_amount) if hasattr(item, 'pretax_amount') else 0.0,
                                'currency': item.currency if hasattr(item, 'currency') else 'CNY',
                                'instance_id': item.instance_id if hasattr(item, 'instance_id') else ''
                            })
            
            return billing_data
        except Exception as e:
            print(f"Error querying Alibaba Cloud billing data: {e}")
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