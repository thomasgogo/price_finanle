import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class CostPredictionService:
    """
    云成本预测服务
    支持多种预测算法：线性回归、移动平均、Prophet时间序列
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {
            'linear': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
    def prepare_data(self, daily_costs):
        """
        准备训练数据
        :param daily_costs: 字典 {date: cost}
        :return: DataFrame with features
        """
        if not daily_costs:
            return None
            
        # 转换为DataFrame
        df = pd.DataFrame(list(daily_costs.items()), columns=['date', 'cost'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # 创建特征
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
        
        # 滚动统计特征
        df['cost_ma7'] = df['cost'].rolling(window=7, min_periods=1).mean()
        df['cost_ma30'] = df['cost'].rolling(window=30, min_periods=1).mean()
        df['cost_std7'] = df['cost'].rolling(window=7, min_periods=1).std().fillna(0)
        
        return df
    
    def train_models(self, df):
        """训练预测模型"""
        if df is None or len(df) < 7:
            return False
            
        feature_cols = ['day_of_week', 'day_of_month', 'month', 'days_since_start', 
                       'cost_ma7', 'cost_ma30', 'cost_std7']
        
        X = df[feature_cols].values
        y = df['cost'].values
        
        # 训练多个模型
        for name, model in self.models.items():
            try:
                model.fit(X, y)
            except Exception as e:
                print(f"Error training {name} model: {e}")
                return False
        
        return True
    
    def predict_costs(self, daily_costs, days_ahead=30, method='ensemble'):
        """
        预测未来成本
        :param daily_costs: 历史每日成本 {date: cost}
        :param days_ahead: 预测未来多少天
        :param method: 预测方法 'linear', 'random_forest', 'moving_average', 'ensemble'
        :return: 预测结果字典
        """
        df = self.prepare_data(daily_costs)
        
        if df is None or len(df) < 7:
            return {
                'success': False,
                'message': '历史数据不足，至少需要7天的数据',
                'predictions': []
            }
        
        # 训练模型
        if not self.train_models(df):
            return {
                'success': False,
                'message': '模型训练失败',
                'predictions': []
            }
        
        # 生成未来日期
        last_date = df['date'].max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
        
        # 构建预测特征
        predictions = []
        
        for future_date in future_dates:
            features = self._create_future_features(df, future_date)
            
            if method == 'ensemble':
                # 集成多个模型的预测
                pred_values = []
                for model in self.models.values():
                    pred = model.predict([features])[0]
                    pred_values.append(max(0, pred))  # 确保非负
                predicted_cost = np.mean(pred_values)
            elif method in self.models:
                predicted_cost = max(0, self.models[method].predict([features])[0])
            elif method == 'moving_average':
                # 移动平均预测
                predicted_cost = df['cost'].tail(7).mean()
            else:
                predicted_cost = df['cost'].mean()
            
            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_cost': round(predicted_cost, 2)
            })
        
        # 分析预测趋势
        recent_avg = df['cost'].tail(7).mean()
        predicted_avg = np.mean([p['predicted_cost'] for p in predictions])
        
        trend = 'stable'
        if predicted_avg > recent_avg * 1.1:
            trend = 'increasing'
        elif predicted_avg < recent_avg * 0.9:
            trend = 'decreasing'
        
        return {
            'success': True,
            'predictions': predictions,
            'statistics': {
                'recent_avg_cost': round(recent_avg, 2),
                'predicted_avg_cost': round(predicted_avg, 2),
                'trend': trend,
                'historical_days': len(df),
                'prediction_days': days_ahead
            }
        }
    
    def _create_future_features(self, df, future_date):
        """为未来日期创建特征"""
        last_date = df['date'].max()
        days_since_start = (future_date - df['date'].min()).days
        
        features = [
            future_date.dayofweek,
            future_date.day,
            future_date.month,
            days_since_start,
            df['cost'].tail(7).mean(),  # 最近7天平均
            df['cost'].tail(30).mean() if len(df) >= 30 else df['cost'].mean(),  # 最近30天平均
            df['cost'].tail(7).std() if len(df) >= 7 else 0  # 最近7天标准差
        ]
        
        return features
    
    def detect_anomalies(self, daily_costs, threshold=2.0):
        """
        检测异常成本
        :param daily_costs: 每日成本 {date: cost}
        :param threshold: 异常阈值（标准差倍数）
        :return: 异常日期列表
        """
        df = self.prepare_data(daily_costs)
        
        if df is None or len(df) < 7:
            return []
        
        # 计算z-score
        mean_cost = df['cost'].mean()
        std_cost = df['cost'].std()
        
        if std_cost == 0:
            return []
        
        df['z_score'] = (df['cost'] - mean_cost) / std_cost
        
        # 找出异常值
        anomalies = df[abs(df['z_score']) > threshold]
        
        return [{
            'date': row['date'].strftime('%Y-%m-%d'),
            'cost': round(row['cost'], 2),
            'z_score': round(row['z_score'], 2),
            'status': 'high' if row['z_score'] > 0 else 'low'
        } for _, row in anomalies.iterrows()]
    
    def daily_cost_analysis(self, daily_costs):
        """
        每日成本分析，判断成本高低
        :param daily_costs: 每日成本 {date: cost}
        :return: 分析结果
        """
        df = self.prepare_data(daily_costs)
        
        if df is None or len(df) == 0:
            return {
                'success': False,
                'message': '无可用数据'
            }
        
        # 计算统计指标
        mean_cost = df['cost'].mean()
        median_cost = df['cost'].median()
        std_cost = df['cost'].std()
        
        # 对每天进行分类
        daily_analysis = []
        for _, row in df.iterrows():
            cost = row['cost']
            
            # 判断成本水平
            if cost > mean_cost + std_cost:
                level = 'high'
                description = '成本偏高'
            elif cost < mean_cost - std_cost:
                level = 'low'
                description = '成本偏低'
            else:
                level = 'normal'
                description = '成本正常'
            
            daily_analysis.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'cost': round(cost, 2),
                'level': level,
                'description': description,
                'deviation_pct': round(((cost - mean_cost) / mean_cost) * 100, 2)
            })
        
        return {
            'success': True,
            'daily_analysis': daily_analysis,
            'statistics': {
                'mean_cost': round(mean_cost, 2),
                'median_cost': round(median_cost, 2),
                'std_cost': round(std_cost, 2),
                'min_cost': round(df['cost'].min(), 2),
                'max_cost': round(df['cost'].max(), 2),
                'total_days': len(df)
            }
        }
    
    def compare_with_baseline(self, daily_costs, baseline_cost):
        """
        与基线成本比较
        :param daily_costs: 每日成本 {date: cost}
        :param baseline_cost: 基线成本（预算）
        :return: 比较结果
        """
        df = self.prepare_data(daily_costs)
        
        if df is None:
            return {'success': False, 'message': '无可用数据'}
        
        comparison = []
        over_budget_days = 0
        
        for _, row in df.iterrows():
            cost = row['cost']
            diff = cost - baseline_cost
            diff_pct = (diff / baseline_cost) * 100 if baseline_cost > 0 else 0
            
            status = 'over_budget' if cost > baseline_cost else 'within_budget'
            if cost > baseline_cost:
                over_budget_days += 1
            
            comparison.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'cost': round(cost, 2),
                'baseline': baseline_cost,
                'difference': round(diff, 2),
                'difference_pct': round(diff_pct, 2),
                'status': status
            })
        
        total_cost = df['cost'].sum()
        total_baseline = baseline_cost * len(df)
        
        return {
            'success': True,
            'comparison': comparison,
            'summary': {
                'total_cost': round(total_cost, 2),
                'total_baseline': round(total_baseline, 2),
                'total_difference': round(total_cost - total_baseline, 2),
                'over_budget_days': over_budget_days,
                'total_days': len(df),
                'over_budget_rate': round((over_budget_days / len(df)) * 100, 2)
            }
        }
