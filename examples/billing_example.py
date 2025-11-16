#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
云成本账单拉取和预测示例
演示如何使用API进行账单拉取和成本预测
"""

import os
import sys
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量示例（实际使用时应从.env文件加载）
# os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'] = 'your_key_id'
# os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'] = 'your_key_secret'
# os.environ['TENCENT_CLOUD_SECRET_ID'] = 'your_secret_id'
# os.environ['TENCENT_CLOUD_SECRET_KEY'] = 'your_secret_key'

from finance_api.billing_fetch_service import BillingFetchService
from finance_api.cost_prediction_service import CostPredictionService


def example_1_fetch_billing():
    """示例1: 拉取账单数据"""
    print("\n" + "="*60)
    print("示例1: 拉取账单数据")
    print("="*60 + "\n")
    
    service = BillingFetchService()
    
    # 获取最近30天的日期
    start_date, end_date = service.get_last_n_days(30)
    print(f"日期范围: {start_date} 至 {end_date}\n")
    
    # 拉取阿里云账单
    print("1. 拉取阿里云账单...")
    alibaba_result = service.fetch_billing_data('alibaba', start_date, end_date)
    if alibaba_result['success']:
        print(f"   ✓ 总成本: ¥{alibaba_result['total_cost']:.2f}")
        print(f"   ✓ 账单条目: {len(alibaba_result['billing_data'])} 条")
    else:
        print(f"   ✗ 失败: {alibaba_result.get('message', '未知错误')}")
    
    # 拉取腾讯云账单
    print("\n2. 拉取腾讯云账单...")
    tencent_result = service.fetch_billing_data('tencent', start_date, end_date)
    if tencent_result['success']:
        print(f"   ✓ 总成本: ¥{tencent_result['total_cost']:.2f}")
        print(f"   ✓ 账单条目: {len(tencent_result['billing_data'])} 条")
    else:
        print(f"   ✗ 失败: {tencent_result.get('message', '未知错误')}")
    
    # 拉取所有云服务商账单
    print("\n3. 拉取所有云服务商账单...")
    all_result = service.fetch_all_billing_data(start_date, end_date)
    print(f"   ✓ 总成本: ¥{all_result['total_cost']:.2f}")
    print(f"   ✓ 云服务商数量: {len(all_result['providers'])}")


def example_2_analyze_costs():
    """示例2: 分析每日成本，判断高低"""
    print("\n" + "="*60)
    print("示例2: 分析每日成本")
    print("="*60 + "\n")
    
    # 模拟每日成本数据
    daily_costs = {}
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        # 模拟成本数据，包含一些波动
        import random
        base_cost = 150 + random.uniform(-20, 20)
        if i % 7 == 6:  # 周日成本较低
            base_cost *= 0.7
        if i == 15:  # 模拟异常高成本
            base_cost *= 2
        daily_costs[date] = round(base_cost, 2)
    
    prediction_service = CostPredictionService()
    
    # 分析每日成本
    print("分析每日成本水平...")
    analysis = prediction_service.daily_cost_analysis(daily_costs)
    
    if analysis['success']:
        stats = analysis['statistics']
        print(f"\n统计信息:")
        print(f"  平均成本: ¥{stats['mean_cost']:.2f}")
        print(f"  最低成本: ¥{stats['min_cost']:.2f}")
        print(f"  最高成本: ¥{stats['max_cost']:.2f}")
        print(f"  标准差: ¥{stats['std_cost']:.2f}")
        
        # 统计成本水平分布
        daily_data = analysis['daily_analysis']
        high_days = [d for d in daily_data if d['level'] == 'high']
        low_days = [d for d in daily_data if d['level'] == 'low']
        normal_days = [d for d in daily_data if d['level'] == 'normal']
        
        print(f"\n成本水平分布:")
        print(f"  高成本天数: {len(high_days)} 天")
        print(f"  正常成本天数: {len(normal_days)} 天")
        print(f"  低成本天数: {len(low_days)} 天")
        
        # 显示高成本天数
        if high_days:
            print(f"\n高成本日期:")
            for day in high_days[:5]:  # 只显示前5天
                print(f"  {day['date']}: ¥{day['cost']:.2f} (偏离 {day['deviation_pct']:+.1f}%)")


def example_3_predict_costs():
    """示例3: 预测未来成本"""
    print("\n" + "="*60)
    print("示例3: 预测未来成本")
    print("="*60 + "\n")
    
    # 模拟历史成本数据
    daily_costs = {}
    base_date = datetime.now() - timedelta(days=60)
    
    for i in range(60):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        # 模拟成本数据，包含上升趋势
        import random
        base_cost = 150 + (i * 0.5) + random.uniform(-15, 15)
        daily_costs[date] = round(base_cost, 2)
    
    prediction_service = CostPredictionService()
    
    # 预测未来30天成本
    print("基于最近60天数据，预测未来30天成本...")
    predictions = prediction_service.predict_costs(
        daily_costs,
        days_ahead=30,
        method='ensemble'
    )
    
    if predictions['success']:
        stats = predictions['statistics']
        print(f"\n预测结果:")
        print(f"  历史平均成本: ¥{stats['recent_avg_cost']:.2f}")
        print(f"  预测平均成本: ¥{stats['predicted_avg_cost']:.2f}")
        print(f"  成本趋势: {stats['trend']}")
        
        # 显示未来7天预测
        print(f"\n未来7天预测:")
        for pred in predictions['predictions'][:7]:
            print(f"  {pred['date']}: ¥{pred['predicted_cost']:.2f}")
        
        # 计算预测总成本
        total_predicted = sum(p['predicted_cost'] for p in predictions['predictions'])
        print(f"\n预测30天总成本: ¥{total_predicted:.2f}")


def example_4_detect_anomalies():
    """示例4: 检测异常成本"""
    print("\n" + "="*60)
    print("示例4: 检测异常成本")
    print("="*60 + "\n")
    
    # 模拟成本数据，包含异常
    daily_costs = {}
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        import random
        base_cost = 150 + random.uniform(-10, 10)
        
        # 模拟几个异常日期
        if i == 5:
            base_cost *= 3  # 异常高
        elif i == 15:
            base_cost *= 0.3  # 异常低
        elif i == 25:
            base_cost *= 2.5  # 异常高
        
        daily_costs[date] = round(base_cost, 2)
    
    prediction_service = CostPredictionService()
    
    # 检测异常
    print("检测异常成本...")
    anomalies = prediction_service.detect_anomalies(daily_costs, threshold=2.0)
    
    if anomalies:
        print(f"\n发现 {len(anomalies)} 个异常:")
        for anomaly in anomalies:
            status = "偏高" if anomaly['status'] == 'high' else "偏低"
            print(f"  {anomaly['date']}: ¥{anomaly['cost']:.2f} ({status}, Z-score: {anomaly['z_score']:.2f})")
    else:
        print("\n未发现异常成本")


def example_5_budget_comparison():
    """示例5: 与预算比较"""
    print("\n" + "="*60)
    print("示例5: 与预算比较")
    print("="*60 + "\n")
    
    # 模拟成本数据
    daily_costs = {}
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        import random
        base_cost = 150 + random.uniform(-30, 50)
        daily_costs[date] = round(base_cost, 2)
    
    prediction_service = CostPredictionService()
    
    # 设置每日预算
    daily_budget = 160.0
    print(f"每日预算: ¥{daily_budget:.2f}")
    
    # 与预算比较
    print("\n与预算比较...")
    comparison = prediction_service.compare_with_baseline(daily_costs, daily_budget)
    
    if comparison['success']:
        summary = comparison['summary']
        print(f"\n预算分析:")
        print(f"  总成本: ¥{summary['total_cost']:.2f}")
        print(f"  总预算: ¥{summary['total_baseline']:.2f}")
        print(f"  差异: ¥{summary['total_difference']:.2f}")
        print(f"  超预算天数: {summary['over_budget_days']}/{summary['total_days']} 天")
        print(f"  超预算率: {summary['over_budget_rate']:.1f}%")
        
        # 显示超预算日期
        over_budget_days = [c for c in comparison['comparison'] if c['status'] == 'over_budget']
        if over_budget_days:
            print(f"\n超预算日期 (前5天):")
            for day in over_budget_days[:5]:
                print(f"  {day['date']}: ¥{day['cost']:.2f} (超出 ¥{day['difference']:.2f}, {day['difference_pct']:+.1f}%)")


def example_6_complete_analysis():
    """示例6: 完整分析流程"""
    print("\n" + "="*60)
    print("示例6: 完整分析流程")
    print("="*60 + "\n")
    
    service = BillingFetchService()
    
    # 获取最近30天的日期
    start_date, end_date = service.get_last_n_days(30)
    
    print(f"执行完整分析...")
    print(f"日期范围: {start_date} 至 {end_date}")
    
    # 执行完整分析
    result = service.analyze_and_predict(
        provider='all',
        start_date=start_date,
        end_date=end_date,
        prediction_days=30
    )
    
    if result['success']:
        print(f"\n✓ 分析完成\n")
        
        # 账单摘要
        print("📊 账单摘要:")
        print(f"  总成本: ¥{result['billing_summary']['total_cost']:.2f}")
        print(f"  天数: {result['billing_summary']['days_count']}")
        
        # 成本统计
        if result['daily_analysis']['success']:
            stats = result['daily_analysis']['statistics']
            print(f"\n📈 成本统计:")
            print(f"  平均: ¥{stats['mean_cost']:.2f}")
            print(f"  最小: ¥{stats['min_cost']:.2f}")
            print(f"  最大: ¥{stats['max_cost']:.2f}")
        
        # 预测结果
        if result['predictions']['success']:
            pred_stats = result['predictions']['statistics']
            print(f"\n🔮 成本预测:")
            print(f"  趋势: {pred_stats['trend']}")
            print(f"  预测平均: ¥{pred_stats['predicted_avg_cost']:.2f}")
        
        # 异常检测
        anomalies = result.get('anomalies', [])
        if anomalies:
            print(f"\n⚠️  异常检测:")
            print(f"  发现 {len(anomalies)} 个异常")
            for anomaly in anomalies[:3]:
                status = "偏高" if anomaly['status'] == 'high' else "偏低"
                print(f"    {anomaly['date']}: ¥{anomaly['cost']:.2f} ({status})")
    else:
        print(f"\n✗ 分析失败: {result.get('message', '未知错误')}")


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("云成本账单拉取和预测 - 使用示例")
    print("="*60)
    
    try:
        # 注意：示例1需要配置真实的云服务商凭证
        # example_1_fetch_billing()
        
        # 以下示例使用模拟数据，可以直接运行
        example_2_analyze_costs()
        example_3_predict_costs()
        example_4_detect_anomalies()
        example_5_budget_comparison()
        
        # 示例6需要真实凭证
        # example_6_complete_analysis()
        
        print("\n" + "="*60)
        print("所有示例运行完成")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
