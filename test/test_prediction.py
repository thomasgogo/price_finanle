#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试成本预测服务（不需要云SDK）
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 只导入预测服务
from finance_api.cost_prediction_service import CostPredictionService


def test_cost_analysis():
    """测试成本分析功能"""
    print("\n" + "="*60)
    print("测试 1: 每日成本分析")
    print("="*60 + "\n")
    
    # 创建模拟数据
    daily_costs = {}
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        import random
        base_cost = 150 + random.uniform(-20, 20)
        if i % 7 == 6:  # 周日成本较低
            base_cost *= 0.7
        if i == 15:  # 模拟异常高成本
            base_cost *= 2
        daily_costs[date] = round(base_cost, 2)
    
    service = CostPredictionService()
    
    # 分析每日成本
    analysis = service.daily_cost_analysis(daily_costs)
    
    if analysis['success']:
        stats = analysis['statistics']
        print("✓ 成本分析成功")
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
        
        if high_days:
            print(f"\n高成本日期示例:")
            for day in high_days[:3]:
                print(f"  {day['date']}: ¥{day['cost']:.2f} (偏离 {day['deviation_pct']:+.1f}%)")
        
        return True
    else:
        print("✗ 成本分析失败")
        return False


def test_cost_prediction():
    """测试成本预测功能"""
    print("\n" + "="*60)
    print("测试 2: 成本预测")
    print("="*60 + "\n")
    
    # 创建模拟数据 - 包含上升趋势
    daily_costs = {}
    base_date = datetime.now() - timedelta(days=60)
    
    for i in range(60):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        import random
        base_cost = 150 + (i * 0.5) + random.uniform(-10, 10)
        daily_costs[date] = round(base_cost, 2)
    
    service = CostPredictionService()
    
    # 预测未来30天
    predictions = service.predict_costs(
        daily_costs,
        days_ahead=30,
        method='ensemble'
    )
    
    if predictions['success']:
        stats = predictions['statistics']
        print("✓ 成本预测成功")
        print(f"\n预测统计:")
        print(f"  历史平均成本: ¥{stats['recent_avg_cost']:.2f}")
        print(f"  预测平均成本: ¥{stats['predicted_avg_cost']:.2f}")
        print(f"  成本趋势: {stats['trend']}")
        print(f"  历史天数: {stats['historical_days']}")
        print(f"  预测天数: {stats['prediction_days']}")
        
        # 显示未来5天预测
        print(f"\n未来5天预测:")
        for pred in predictions['predictions'][:5]:
            print(f"  {pred['date']}: ¥{pred['predicted_cost']:.2f}")
        
        # 计算预测总成本
        total_predicted = sum(p['predicted_cost'] for p in predictions['predictions'])
        print(f"\n预测30天总成本: ¥{total_predicted:.2f}")
        
        return True
    else:
        print(f"✗ 成本预测失败: {predictions.get('message', '未知错误')}")
        return False


def test_anomaly_detection():
    """测试异常检测功能"""
    print("\n" + "="*60)
    print("测试 3: 异常成本检测")
    print("="*60 + "\n")
    
    # 创建包含异常的模拟数据
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
    
    service = CostPredictionService()
    
    # 检测异常
    anomalies = service.detect_anomalies(daily_costs, threshold=2.0)
    
    print("✓ 异常检测完成")
    
    if anomalies:
        print(f"\n发现 {len(anomalies)} 个异常:")
        for anomaly in anomalies:
            status = "偏高" if anomaly['status'] == 'high' else "偏低"
            print(f"  {anomaly['date']}: ¥{anomaly['cost']:.2f} ({status}, Z-score: {anomaly['z_score']:.2f})")
        return True
    else:
        print("\n未发现异常成本")
        return False


def test_budget_comparison():
    """测试预算比较功能"""
    print("\n" + "="*60)
    print("测试 4: 预算比较")
    print("="*60 + "\n")
    
    # 创建模拟数据
    daily_costs = {}
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        import random
        base_cost = 150 + random.uniform(-30, 50)
        daily_costs[date] = round(base_cost, 2)
    
    service = CostPredictionService()
    
    # 设置每日预算
    daily_budget = 160.0
    print(f"每日预算: ¥{daily_budget:.2f}")
    
    # 与预算比较
    comparison = service.compare_with_baseline(daily_costs, daily_budget)
    
    if comparison['success']:
        summary = comparison['summary']
        print("\n✓ 预算比较完成")
        print(f"\n预算分析:")
        print(f"  总成本: ¥{summary['total_cost']:.2f}")
        print(f"  总预算: ¥{summary['total_baseline']:.2f}")
        print(f"  差异: ¥{summary['total_difference']:.2f}")
        print(f"  超预算天数: {summary['over_budget_days']}/{summary['total_days']} 天")
        print(f"  超预算率: {summary['over_budget_rate']:.1f}%")
        
        # 显示超预算日期
        over_budget_days = [c for c in comparison['comparison'] if c['status'] == 'over_budget']
        if over_budget_days:
            print(f"\n超预算日期 (前3天):")
            for day in over_budget_days[:3]:
                print(f"  {day['date']}: ¥{day['cost']:.2f} (超出 ¥{day['difference']:.2f}, {day['difference_pct']:+.1f}%)")
        
        return True
    else:
        print("✗ 预算比较失败")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("云成本预测服务测试")
    print("="*60)
    
    results = []
    
    try:
        results.append(("成本分析", test_cost_analysis()))
        results.append(("成本预测", test_cost_prediction()))
        results.append(("异常检测", test_anomaly_detection()))
        results.append(("预算比较", test_budget_comparison()))
        
        # 显示测试总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60 + "\n")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✓ 通过" if result else "✗ 失败"
            print(f"  {name}: {status}")
        
        print(f"\n总计: {passed}/{total} 测试通过")
        print("="*60 + "\n")
        
        if passed == total:
            print("✓ 所有测试通过！")
        else:
            print("⚠ 部分测试失败")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
