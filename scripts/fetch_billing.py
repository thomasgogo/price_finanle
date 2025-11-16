#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
云成本账单拉取和预测脚本
支持阿里云和腾讯云
"""

import os
import sys
import json
from datetime import datetime, timedelta
import argparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量（如果需要）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_finanle_django.settings')

# 导入服务
from finance_api.billing_fetch_service import BillingFetchService


def main():
    parser = argparse.ArgumentParser(description='云成本账单拉取和预测工具')
    
    parser.add_argument('action', 
                       choices=['fetch', 'analyze', 'predict', 'balance', 'anomaly', 'full'],
                       help='操作类型')
    
    parser.add_argument('--provider', 
                       choices=['alibaba', 'tencent', 'all'],
                       default='all',
                       help='云服务商 (默认: all)')
    
    parser.add_argument('--start-date',
                       help='开始日期 YYYY-MM-DD (默认: 30天前)')
    
    parser.add_argument('--end-date',
                       help='结束日期 YYYY-MM-DD (默认: 今天)')
    
    parser.add_argument('--days',
                       type=int,
                       default=30,
                       help='预测天数或历史天数 (默认: 30)')
    
    parser.add_argument('--output',
                       help='输出JSON文件路径')
    
    parser.add_argument('--budget',
                       type=float,
                       help='每日预算金额（用于预算比较）')
    
    args = parser.parse_args()
    
    # 初始化服务
    service = BillingFetchService()
    
    # 设置日期范围
    if not args.start_date or not args.end_date:
        args.start_date, args.end_date = service.get_last_n_days(args.days)
    
    print(f"\n{'='*60}")
    print(f"云成本账单分析工具")
    print(f"{'='*60}")
    print(f"云服务商: {args.provider}")
    print(f"日期范围: {args.start_date} 至 {args.end_date}")
    print(f"{'='*60}\n")
    
    # 执行操作
    result = None
    
    if args.action == 'fetch':
        print("正在拉取账单数据...")
        if args.provider == 'all':
            result = service.fetch_all_billing_data(args.start_date, args.end_date)
        else:
            result = service.fetch_billing_data(args.provider, args.start_date, args.end_date)
        
        print(f"\n✓ 账单数据拉取完成")
        print(f"  总成本: ¥{result.get('total_cost', 0):.2f}")
        
    elif args.action == 'balance':
        print("正在查询账户余额...")
        result = service.get_account_balances()
        
        print(f"\n✓ 账户余额查询完成")
        for balance_info in result.get('balances', []):
            print(f"  {balance_info['provider']}: ¥{balance_info['balance']:.2f}")
        print(f"  总余额: ¥{result.get('total_balance', 0):.2f}")
        
    elif args.action == 'analyze':
        print("正在分析每日成本...")
        result = service.analyze_and_predict(
            args.provider, 
            args.start_date, 
            args.end_date,
            prediction_days=0
        )
        
        print(f"\n✓ 成本分析完成")
        if result['success'] and result['daily_analysis']['success']:
            stats = result['daily_analysis']['statistics']
            print(f"  平均成本: ¥{stats['mean_cost']:.2f}")
            print(f"  最低成本: ¥{stats['min_cost']:.2f}")
            print(f"  最高成本: ¥{stats['max_cost']:.2f}")
            print(f"  标准差: ¥{stats['std_cost']:.2f}")
            
            # 显示成本水平统计
            daily_data = result['daily_analysis']['daily_analysis']
            high_days = sum(1 for d in daily_data if d['level'] == 'high')
            low_days = sum(1 for d in daily_data if d['level'] == 'low')
            normal_days = sum(1 for d in daily_data if d['level'] == 'normal')
            
            print(f"\n  成本水平分布:")
            print(f"    高成本天数: {high_days} 天")
            print(f"    正常成本天数: {normal_days} 天")
            print(f"    低成本天数: {low_days} 天")
        
    elif args.action == 'predict':
        print(f"正在预测未来 {args.days} 天成本...")
        result = service.analyze_and_predict(
            args.provider,
            args.start_date,
            args.end_date,
            prediction_days=args.days
        )
        
        print(f"\n✓ 成本预测完成")
        if result['success'] and result['predictions']['success']:
            pred_stats = result['predictions']['statistics']
            print(f"  历史平均成本: ¥{pred_stats['recent_avg_cost']:.2f}")
            print(f"  预测平均成本: ¥{pred_stats['predicted_avg_cost']:.2f}")
            print(f"  成本趋势: {pred_stats['trend']}")
            
            # 显示前5天预测
            predictions = result['predictions']['predictions'][:5]
            print(f"\n  未来5天预测:")
            for pred in predictions:
                print(f"    {pred['date']}: ¥{pred['predicted_cost']:.2f}")
        
    elif args.action == 'anomaly':
        print("正在检测异常成本...")
        result = service.analyze_and_predict(
            args.provider,
            args.start_date,
            args.end_date,
            prediction_days=0
        )
        
        print(f"\n✓ 异常检测完成")
        anomalies = result.get('anomalies', [])
        if anomalies:
            print(f"  发现 {len(anomalies)} 个异常:")
            for anomaly in anomalies:
                status = "偏高" if anomaly['status'] == 'high' else "偏低"
                print(f"    {anomaly['date']}: ¥{anomaly['cost']:.2f} ({status})")
        else:
            print("  未发现异常成本")
    
    elif args.action == 'full':
        print("正在执行完整分析...")
        result = service.analyze_and_predict(
            args.provider,
            args.start_date,
            args.end_date,
            prediction_days=args.days
        )
        
        print(f"\n✓ 完整分析完成")
        print(f"\n📊 账单摘要:")
        print(f"  总成本: ¥{result['billing_summary']['total_cost']:.2f}")
        print(f"  天数: {result['billing_summary']['days_count']}")
        
        if result['daily_analysis']['success']:
            stats = result['daily_analysis']['statistics']
            print(f"\n📈 成本统计:")
            print(f"  平均: ¥{stats['mean_cost']:.2f}")
            print(f"  最小: ¥{stats['min_cost']:.2f}")
            print(f"  最大: ¥{stats['max_cost']:.2f}")
        
        if result['predictions']['success']:
            pred_stats = result['predictions']['statistics']
            print(f"\n🔮 成本预测:")
            print(f"  趋势: {pred_stats['trend']}")
            print(f"  预测平均: ¥{pred_stats['predicted_avg_cost']:.2f}")
        
        anomalies = result.get('anomalies', [])
        if anomalies:
            print(f"\n⚠️  异常检测: 发现 {len(anomalies)} 个异常")
    
    # 保存结果
    if result and args.output:
        service.export_to_json(result, args.output)
        print(f"\n✓ 结果已保存到: {args.output}")
    
    # 输出JSON（如果没有指定输出文件）
    if result and not args.output and '--json' in sys.argv:
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
    
    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
