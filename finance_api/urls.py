from django.urls import path
from . import views

urlpatterns = [
    # 账户余额
    path('alibaba/balance/', views.get_alibaba_cloud_balance, name='alibaba-balance'),
    path('tencent/balance/', views.get_tencent_cloud_balance, name='tencent-balance'),
    path('balances/', views.get_all_balances, name='all-balances'),
    
    # 账单数据拉取
    path('billing/', views.fetch_billing_data, name='fetch-billing'),
    path('daily-costs/', views.get_daily_costs, name='daily-costs'),
    
    # 成本分析
    path('analyze/', views.analyze_daily_costs, name='analyze-costs'),
    path('predict/', views.predict_costs, name='predict-costs'),
    path('anomalies/', views.detect_anomalies, name='detect-anomalies'),
    path('full-analysis/', views.full_analysis, name='full-analysis'),
    path('budget-comparison/', views.compare_with_budget, name='budget-comparison'),
]