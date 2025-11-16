from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .alibaba_cloud_service import AlibabaCloudService
from .tencent_cloud_service import TencentCloudService
from .billing_fetch_service import BillingFetchService
from .cost_prediction_service import CostPredictionService

# 初始化服务
billing_service = BillingFetchService()
prediction_service = CostPredictionService()

@require_http_methods(["GET"])
def get_alibaba_cloud_balance(request):
    """获取阿里云账户余额"""
    service = AlibabaCloudService()
    balance = service.get_account_balance()
    if balance is not None:
        return JsonResponse({"provider": "Alibaba Cloud", "balance": balance})
    return JsonResponse({"error": "Could not retrieve Alibaba Cloud balance"}, status=500)

@require_http_methods(["GET"])
def get_tencent_cloud_balance(request):
    """获取腾讯云账户余额"""
    service = TencentCloudService()
    balance = service.get_account_balance()
    if balance is not None:
        return JsonResponse({"provider": "Tencent Cloud", "balance": balance})
    return JsonResponse({"error": "Could not retrieve Tencent Cloud balance"}, status=500)

@require_http_methods(["GET"])
def get_all_balances(request):
    """获取所有云账户余额"""
    result = billing_service.get_account_balances()
    return JsonResponse(result)

@require_http_methods(["GET"])
def fetch_billing_data(request):
    """
    拉取账单数据
    参数:
        provider: alibaba/tencent/all
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
    """
    provider = request.GET.get('provider', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        # 默认最近30天
        start_date, end_date = billing_service.get_last_n_days(30)
    
    if provider == 'all':
        result = billing_service.fetch_all_billing_data(start_date, end_date)
    else:
        result = billing_service.fetch_billing_data(provider, start_date, end_date)
    
    return JsonResponse(result, safe=False)

@require_http_methods(["GET"])
def get_daily_costs(request):
    """
    获取每日成本
    参数:
        provider: alibaba/tencent/all
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
    """
    provider = request.GET.get('provider', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        start_date, end_date = billing_service.get_last_n_days(30)
    
    if provider == 'all':
        result = billing_service.fetch_all_billing_data(start_date, end_date)
        daily_costs = result.get('combined_daily_costs', {})
    else:
        result = billing_service.fetch_billing_data(provider, start_date, end_date)
        daily_costs = result.get('daily_costs', {})
    
    return JsonResponse({
        'success': True,
        'provider': provider,
        'start_date': start_date,
        'end_date': end_date,
        'daily_costs': daily_costs
    })

@require_http_methods(["GET"])
def analyze_daily_costs(request):
    """
    分析每日成本，判断成本高低
    参数:
        provider: alibaba/tencent/all
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
    """
    provider = request.GET.get('provider', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        start_date, end_date = billing_service.get_last_n_days(30)
    
    # 获取账单数据
    if provider == 'all':
        result = billing_service.fetch_all_billing_data(start_date, end_date)
        daily_costs = result.get('combined_daily_costs', {})
    else:
        result = billing_service.fetch_billing_data(provider, start_date, end_date)
        daily_costs = result.get('daily_costs', {})
    
    if not daily_costs:
        return JsonResponse({
            'success': False,
            'message': '无法获取账单数据'
        }, status=400)
    
    # 分析每日成本
    analysis = prediction_service.daily_cost_analysis(daily_costs)
    
    return JsonResponse(analysis)

@require_http_methods(["GET"])
def predict_costs(request):
    """
    预测未来成本
    参数:
        provider: alibaba/tencent/all
        start_date: YYYY-MM-DD (历史数据开始日期)
        end_date: YYYY-MM-DD (历史数据结束日期)
        days_ahead: 预测未来多少天，默认30
        method: 预测方法 linear/random_forest/ensemble，默认ensemble
    """
    provider = request.GET.get('provider', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    days_ahead = int(request.GET.get('days_ahead', 30))
    method = request.GET.get('method', 'ensemble')
    
    if not start_date or not end_date:
        start_date, end_date = billing_service.get_last_n_days(30)
    
    # 获取历史账单数据
    if provider == 'all':
        result = billing_service.fetch_all_billing_data(start_date, end_date)
        daily_costs = result.get('combined_daily_costs', {})
    else:
        result = billing_service.fetch_billing_data(provider, start_date, end_date)
        daily_costs = result.get('daily_costs', {})
    
    if not daily_costs:
        return JsonResponse({
            'success': False,
            'message': '无法获取历史账单数据'
        }, status=400)
    
    # 预测未来成本
    predictions = prediction_service.predict_costs(daily_costs, days_ahead, method)
    
    return JsonResponse(predictions)

@require_http_methods(["GET"])
def detect_anomalies(request):
    """
    检测异常成本
    参数:
        provider: alibaba/tencent/all
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        threshold: 异常阈值（标准差倍数），默认2.0
    """
    provider = request.GET.get('provider', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    threshold = float(request.GET.get('threshold', 2.0))
    
    if not start_date or not end_date:
        start_date, end_date = billing_service.get_last_n_days(30)
    
    # 获取账单数据
    if provider == 'all':
        result = billing_service.fetch_all_billing_data(start_date, end_date)
        daily_costs = result.get('combined_daily_costs', {})
    else:
        result = billing_service.fetch_billing_data(provider, start_date, end_date)
        daily_costs = result.get('daily_costs', {})
    
    if not daily_costs:
        return JsonResponse({
            'success': False,
            'message': '无法获取账单数据'
        }, status=400)
    
    # 检测异常
    anomalies = prediction_service.detect_anomalies(daily_costs, threshold)
    
    return JsonResponse({
        'success': True,
        'provider': provider,
        'start_date': start_date,
        'end_date': end_date,
        'anomalies': anomalies,
        'anomaly_count': len(anomalies)
    })

@require_http_methods(["GET"])
def full_analysis(request):
    """
    完整的成本分析和预测
    参数:
        provider: alibaba/tencent/all
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        prediction_days: 预测天数，默认30
    """
    provider = request.GET.get('provider', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    prediction_days = int(request.GET.get('prediction_days', 30))
    
    if not start_date or not end_date:
        start_date, end_date = billing_service.get_last_n_days(30)
    
    # 使用统一服务进行分析和预测
    result = billing_service.analyze_and_predict(
        provider, start_date, end_date, prediction_days
    )
    
    return JsonResponse(result)

@require_http_methods(["GET"])
def compare_with_budget(request):
    """
    与预算进行比较
    参数:
        provider: alibaba/tencent/all
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        daily_budget: 每日预算
    """
    provider = request.GET.get('provider', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    daily_budget = request.GET.get('daily_budget')
    
    if not daily_budget:
        return JsonResponse({
            'success': False,
            'message': '请提供每日预算 (daily_budget)'
        }, status=400)
    
    daily_budget = float(daily_budget)
    
    if not start_date or not end_date:
        start_date, end_date = billing_service.get_last_n_days(30)
    
    # 获取账单数据
    if provider == 'all':
        result = billing_service.fetch_all_billing_data(start_date, end_date)
        daily_costs = result.get('combined_daily_costs', {})
    else:
        result = billing_service.fetch_billing_data(provider, start_date, end_date)
        daily_costs = result.get('daily_costs', {})
    
    if not daily_costs:
        return JsonResponse({
            'success': False,
            'message': '无法获取账单数据'
        }, status=400)
    
    # 与预算比较
    comparison = prediction_service.compare_with_baseline(daily_costs, daily_budget)
    
    return JsonResponse(comparison)

