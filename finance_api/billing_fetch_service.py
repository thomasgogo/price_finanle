"""
云账单拉取服务
支持阿里云和腾讯云账单数据拉取
"""
import json
from datetime import datetime, timedelta
from .alibaba_cloud_service import AlibabaCloudService
from .tencent_cloud_service import TencentCloudService
from .cost_prediction_service import CostPredictionService


class BillingFetchService:
    """统一的账单拉取服务"""
    
    def __init__(self):
        self.alibaba_service = None
        self.tencent_service = None
        self.prediction_service = CostPredictionService()
        
    def initialize_alibaba_cloud(self):
        """初始化阿里云服务"""
        try:
            self.alibaba_service = AlibabaCloudService()
            return True
        except Exception as e:
            print(f"Failed to initialize Alibaba Cloud service: {e}")
            return False
    
    def initialize_tencent_cloud(self):
        """初始化腾讯云服务"""
        try:
            self.tencent_service = TencentCloudService()
            return True
        except Exception as e:
            print(f"Failed to initialize Tencent Cloud service: {e}")
            return False
    
    def fetch_billing_data(self, provider, start_date, end_date):
        """
        拉取指定云服务商的账单数据
        :param provider: 'alibaba' 或 'tencent'
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        :return: 账单数据
        """
        if provider == 'alibaba':
            if not self.alibaba_service:
                self.initialize_alibaba_cloud()
            
            if not self.alibaba_service:
                return {'success': False, 'message': '阿里云服务初始化失败'}
            
            billing_data = self.alibaba_service.get_billing_data(start_date, end_date)
            daily_costs = self.alibaba_service.get_daily_costs(start_date, end_date)
            
            return {
                'success': True,
                'provider': 'Alibaba Cloud',
                'start_date': start_date,
                'end_date': end_date,
                'billing_data': billing_data,
                'daily_costs': daily_costs,
                'total_cost': sum(daily_costs.values()) if daily_costs else 0
            }
            
        elif provider == 'tencent':
            if not self.tencent_service:
                self.initialize_tencent_cloud()
            
            if not self.tencent_service:
                return {'success': False, 'message': '腾讯云服务初始化失败'}
            
            billing_data = self.tencent_service.get_billing_data(start_date, end_date)
            daily_costs = self.tencent_service.get_daily_costs(start_date, end_date)
            
            return {
                'success': True,
                'provider': 'Tencent Cloud',
                'start_date': start_date,
                'end_date': end_date,
                'billing_data': billing_data,
                'daily_costs': daily_costs,
                'total_cost': sum(daily_costs.values()) if daily_costs else 0
            }
        else:
            return {'success': False, 'message': f'不支持的云服务商: {provider}'}
    
    def fetch_all_billing_data(self, start_date, end_date):
        """
        拉取所有云服务商的账单数据
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 合并的账单数据
        """
        results = {
            'start_date': start_date,
            'end_date': end_date,
            'providers': []
        }
        
        # 拉取阿里云数据
        alibaba_result = self.fetch_billing_data('alibaba', start_date, end_date)
        if alibaba_result['success']:
            results['providers'].append(alibaba_result)
        
        # 拉取腾讯云数据
        tencent_result = self.fetch_billing_data('tencent', start_date, end_date)
        if tencent_result['success']:
            results['providers'].append(tencent_result)
        
        # 计算总成本
        total_cost = sum(p.get('total_cost', 0) for p in results['providers'])
        results['total_cost'] = total_cost
        
        # 合并每日成本
        combined_daily_costs = {}
        for provider_data in results['providers']:
            daily_costs = provider_data.get('daily_costs', {})
            for date, cost in daily_costs.items():
                if date in combined_daily_costs:
                    combined_daily_costs[date] += cost
                else:
                    combined_daily_costs[date] = cost
        
        results['combined_daily_costs'] = combined_daily_costs
        
        return results
    
    def analyze_and_predict(self, provider, start_date, end_date, prediction_days=30):
        """
        拉取账单数据并进行成本分析和预测
        :param provider: 'alibaba', 'tencent', 或 'all'
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param prediction_days: 预测未来多少天
        :return: 完整的分析和预测结果
        """
        # 拉取账单数据
        if provider == 'all':
            billing_result = self.fetch_all_billing_data(start_date, end_date)
            daily_costs = billing_result.get('combined_daily_costs', {})
        else:
            billing_result = self.fetch_billing_data(provider, start_date, end_date)
            daily_costs = billing_result.get('daily_costs', {})
        
        if not daily_costs:
            return {
                'success': False,
                'message': '无法获取账单数据'
            }
        
        # 每日成本分析
        daily_analysis = self.prediction_service.daily_cost_analysis(daily_costs)
        
        # 成本预测
        predictions = self.prediction_service.predict_costs(
            daily_costs, 
            days_ahead=prediction_days,
            method='ensemble'
        )
        
        # 异常检测
        anomalies = self.prediction_service.detect_anomalies(daily_costs)
        
        return {
            'success': True,
            'provider': provider,
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'billing_summary': {
                'total_cost': billing_result.get('total_cost', 0),
                'days_count': len(daily_costs)
            },
            'daily_analysis': daily_analysis,
            'predictions': predictions,
            'anomalies': anomalies
        }
    
    def get_account_balances(self):
        """获取所有云账户余额"""
        balances = []
        
        # 阿里云余额
        if not self.alibaba_service:
            self.initialize_alibaba_cloud()
        
        if self.alibaba_service:
            alibaba_balance = self.alibaba_service.get_account_balance()
            if alibaba_balance is not None:
                balances.append({
                    'provider': 'Alibaba Cloud',
                    'balance': alibaba_balance,
                    'currency': 'CNY'
                })
        
        # 腾讯云余额
        if not self.tencent_service:
            self.initialize_tencent_cloud()
        
        if self.tencent_service:
            tencent_balance = self.tencent_service.get_account_balance()
            if tencent_balance is not None:
                balances.append({
                    'provider': 'Tencent Cloud',
                    'balance': tencent_balance,
                    'currency': 'CNY'
                })
        
        return {
            'success': True,
            'balances': balances,
            'total_balance': sum(b['balance'] for b in balances)
        }
    
    def export_to_json(self, data, filename):
        """导出数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return {'success': True, 'filename': filename}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_last_n_days(self, days=30):
        """获取最近N天的日期范围"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
