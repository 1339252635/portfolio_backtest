import numpy as np
import pandas as pd
from scipy import stats


class RiskAnalyzer:
    """风险分析器"""
    
    def __init__(self, results):
        """
        results: List[BacktestResult] 回测结果列表
        """
        self.results = results
        # 将Decimal转换为float
        self.returns = np.array([float(r.daily_return) for r in results if r.daily_return is not None])
        self.values = np.array([float(r.total_value) for r in results])
        self.dates = [r.date for r in results]
    
    def calculate_all_metrics(self):
        """计算所有指标"""
        if len(self.returns) == 0:
            return {}
        
        metrics = {}
        
        # 收益指标
        metrics.update(self._calculate_return_metrics())
        
        # 风险指标
        metrics.update(self._calculate_risk_metrics())
        
        # 风险调整收益指标
        metrics.update(self._calculate_risk_adjusted_metrics())
        
        # 其他指标
        metrics.update(self._calculate_other_metrics())
        
        return metrics
    
    def _calculate_return_metrics(self):
        """计算收益指标"""
        metrics = {}
        
        # 总收益率
        initial_value = self.values[0] if len(self.values) > 0 else 0
        final_value = self.values[-1] if len(self.values) > 0 else 0
        metrics['total_return'] = float((final_value - initial_value) / initial_value) if initial_value > 0 else 0
        
        # 年化收益率
        n_years = len(self.returns) / 252  # 假设每年252个交易日
        if n_years > 0:
            metrics['annual_return'] = float((1 + metrics['total_return']) ** (1 / n_years) - 1)
        else:
            metrics['annual_return'] = 0
        
        # 日收益率统计
        metrics['daily_return_mean'] = float(np.mean(self.returns))
        metrics['daily_return_std'] = float(np.std(self.returns))
        metrics['daily_return_min'] = float(np.min(self.returns))
        metrics['daily_return_max'] = float(np.max(self.returns))
        
        # 正收益天数比例
        positive_days = np.sum(self.returns > 0)
        metrics['positive_days_ratio'] = float(positive_days / len(self.returns)) if len(self.returns) > 0 else 0
        
        return metrics
    
    def _calculate_risk_metrics(self):
        """计算风险指标"""
        metrics = {}
        
        # 年化波动率
        metrics['annual_volatility'] = float(np.std(self.returns) * np.sqrt(252))
        
        # 下行波动率（只计算负收益的波动）
        downside_returns = self.returns[self.returns < 0]
        if len(downside_returns) > 0:
            metrics['downside_volatility'] = float(np.std(downside_returns) * np.sqrt(252))
        else:
            metrics['downside_volatility'] = 0
        
        # 最大回撤
        cumulative = np.maximum.accumulate(self.values)
        drawdowns = (self.values - cumulative) / cumulative
        metrics['max_drawdown'] = float(np.min(drawdowns))
        
        # 最大回撤持续时间
        peak_idx = 0
        max_duration = 0
        current_duration = 0
        
        for i in range(len(self.values)):
            if self.values[i] >= self.values[peak_idx]:
                peak_idx = i
                current_duration = 0
            else:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
        
        metrics['max_drawdown_duration'] = int(max_duration)
        
        # 回撤恢复时间（从最大回撤点恢复到新高的平均天数）
        # 这里简化计算
        metrics['avg_recovery_time'] = int(max_duration / 2) if max_duration > 0 else 0
        
        # VaR (Value at Risk) - 95%置信度
        if len(self.returns) > 0:
            metrics['var_95'] = float(np.percentile(self.returns, 5))
            metrics['var_99'] = float(np.percentile(self.returns, 1))
        else:
            metrics['var_95'] = 0
            metrics['var_99'] = 0
        
        # CVaR (Conditional Value at Risk) - 95%置信度
        if len(self.returns) > 0:
            var_95 = metrics['var_95']
            cvar_95_returns = self.returns[self.returns <= var_95]
            metrics['cvar_95'] = float(np.mean(cvar_95_returns)) if len(cvar_95_returns) > 0 else var_95
        else:
            metrics['cvar_95'] = 0
        
        return metrics
    
    def _calculate_risk_adjusted_metrics(self):
        """计算风险调整收益指标"""
        metrics = {}
        
        # 假设无风险利率为3%
        risk_free_rate = 0.03
        
        annual_return = self._calculate_return_metrics()['annual_return']
        annual_volatility = self._calculate_risk_metrics()['annual_volatility']
        downside_volatility = self._calculate_risk_metrics()['downside_volatility']
        max_drawdown = self._calculate_risk_metrics()['max_drawdown']
        
        # 夏普比率
        if annual_volatility > 0:
            metrics['sharpe_ratio'] = float((annual_return - risk_free_rate) / annual_volatility)
        else:
            metrics['sharpe_ratio'] = 0
        
        # 索提诺比率
        if downside_volatility > 0:
            metrics['sortino_ratio'] = float((annual_return - risk_free_rate) / downside_volatility)
        else:
            metrics['sortino_ratio'] = 0
        
        # 卡玛比率
        if max_drawdown < 0:
            metrics['calmar_ratio'] = float(annual_return / abs(max_drawdown))
        else:
            metrics['calmar_ratio'] = 0
        
        # 特雷诺比率 (需要市场数据，这里简化计算)
        metrics['treynor_ratio'] = metrics['sharpe_ratio']  # 简化处理
        
        # 信息比率 (需要基准数据，这里简化)
        metrics['information_ratio'] = 0  # 需要与基准对比计算
        
        return metrics
    
    def _calculate_other_metrics(self):
        """计算其他指标"""
        metrics = {}
        
        # 胜率（日收益率>0的比例）
        positive_returns = np.sum(self.returns > 0)
        metrics['win_rate'] = float(positive_returns / len(self.returns)) if len(self.returns) > 0 else 0
        
        # 盈亏比
        positive_mean = np.mean(self.returns[self.returns > 0]) if np.any(self.returns > 0) else 0
        negative_mean = abs(np.mean(self.returns[self.returns < 0])) if np.any(self.returns < 0) else 1
        metrics['profit_loss_ratio'] = float(positive_mean / negative_mean) if negative_mean > 0 else 0
        
        # 偏度
        if len(self.returns) > 2:
            metrics['skewness'] = float(stats.skew(self.returns))
        else:
            metrics['skewness'] = 0
        
        # 峰度
        if len(self.returns) > 3:
            metrics['kurtosis'] = float(stats.kurtosis(self.returns))
        else:
            metrics['kurtosis'] = 0
        
        # 阿尔法 (需要基准，简化计算)
        metrics['alpha'] = 0
        
        # 贝塔 (需要基准，简化计算)
        metrics['beta'] = 1.0
        
        return metrics
    
    def get_monthly_returns(self):
        """获取月度收益率"""
        # 将日收益率转换为月度收益率
        df = pd.DataFrame({
            'date': self.dates,
            'return': self.returns
        })
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # 按月聚合
        monthly_returns = df['return'].resample('M').apply(lambda x: (1 + x).prod() - 1)
        
        return monthly_returns.tolist()
    
    def get_drawdown_series(self):
        """获取回撤序列"""
        cumulative = np.maximum.accumulate(self.values)
        drawdowns = (self.values - cumulative) / cumulative
        
        return [
            {'date': self.dates[i], 'drawdown': float(drawdowns[i])}
            for i in range(len(drawdowns))
        ]
