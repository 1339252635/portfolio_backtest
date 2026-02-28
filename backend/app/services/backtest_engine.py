import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app import db
from app.models import BacktestScenario, BacktestResult, Holding, PriceData
from app.services.data_service import DataService


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, scenario):
        self.scenario = scenario
        self.allocations = {a.product_code: float(a.allocation_ratio) / 100 
                           for a in scenario.allocations.all()}
        self.price_data = {}
        self.holdings = {}  # 当前持仓 {code: shares}
        self.cash = float(scenario.initial_amount)
        self.total_invested = float(scenario.initial_amount)
        self.daily_results = []
        
    def run(self):
        """执行回测"""
        # 1. 加载价格数据
        self._load_price_data()
        
        # 2. 获取交易日序列
        trading_days = self._get_trading_days()
        
        if not trading_days:
            raise ValueError("No trading days found in the specified date range")
        
        # 3. 初始化持仓
        self._initialize_holdings(trading_days[0])
        
        # 4. 按日遍历
        for i, date in enumerate(trading_days):
            # 4.1 处理定投
            if self._is_investment_day(date):
                self._execute_investment(date)
            
            # 4.2 计算当日市值
            self._update_portfolio_value(date)
            
            # 4.3 检查再平衡
            if self._should_rebalance(date, i):
                self._execute_rebalance(date)
            
            # 4.4 记录结果
            self._record_daily_result(date)
        
        # 5. 保存结果到数据库
        self._save_results()
        
    def _load_price_data(self):
        """加载价格数据"""
        for code in self.allocations.keys():
            df = DataService.get_price_data(
                code, 
                self.scenario.start_date, 
                self.scenario.end_date
            )
            if df.empty:
                raise ValueError(f"No price data available for {code}")
            self.price_data[code] = df.set_index('date')
    
    def _get_trading_days(self):
        """获取交易日序列"""
        # 使用第一个产品的日期作为交易日
        first_code = list(self.allocations.keys())[0]
        df = self.price_data[first_code]
        return df.index.tolist()
    
    def _initialize_holdings(self, first_date):
        """初始化持仓"""
        for code, ratio in self.allocations.items():
            amount = self.cash * ratio
            price = self._get_price(code, first_date)
            
            if price and price > 0:
                shares = amount / price
                self.holdings[code] = shares
                self.cash -= amount
                
                # 记录持仓
                holding = Holding(
                    scenario_id=self.scenario.id,
                    product_code=code,
                    date=first_date,
                    shares=shares,
                    cost_basis=amount,
                    market_value=amount
                )
                db.session.add(holding)
        
        db.session.commit()
    
    def _get_price(self, code, date):
        """获取指定日期的价格"""
        if code not in self.price_data:
            return None
        
        df = self.price_data[code]
        if date in df.index:
            price = df.loc[date, 'nav'] or df.loc[date, 'close']
            return float(price) if price else None
        
        return None
    
    def _is_investment_day(self, date):
        """判断是否为定投日"""
        if self.scenario.investment_strategy == 'none':
            return False
        
        if self.scenario.investment_strategy == 'fixed':
            # 检查是否为每月的定投日
            return date.day == self.scenario.investment_day
        
        return False
    
    def _execute_investment(self, date):
        """执行定投"""
        if not self.scenario.monthly_amount:
            return
        
        amount = float(self.scenario.monthly_amount)
        self.cash += amount
        self.total_invested += amount
        
        # 按配置比例买入
        for code, ratio in self.allocations.items():
            invest_amount = amount * ratio
            price = self._get_price(code, date)
            
            if price and price > 0:
                shares = invest_amount / price
                if code in self.holdings:
                    self.holdings[code] += shares
                else:
                    self.holdings[code] = shares
    
    def _update_portfolio_value(self, date):
        """更新组合市值"""
        total_value = self.cash
        
        for code, shares in self.holdings.items():
            price = self._get_price(code, date)
            if price:
                total_value += shares * price
        
        return total_value
    
    def _should_rebalance(self, date, day_index):
        """判断是否需要再平衡"""
        if self.scenario.rebalance_strategy == 'none':
            return False
        
        if self.scenario.rebalance_strategy == 'periodic':
            # 定期再平衡
            if day_index == 0:
                return False
            
            period_months = self.scenario.rebalance_period or 12
            prev_date = self.daily_results[-1]['date'] if self.daily_results else None
            
            if prev_date:
                months_diff = (date.year - prev_date.year) * 12 + (date.month - prev_date.month)
                return months_diff >= period_months
        
        elif self.scenario.rebalance_strategy == 'threshold':
            # 阈值再平衡
            if not self.daily_results:
                return False
            
            threshold = float(self.scenario.rebalance_threshold or 5) / 100
            total_value = self._update_portfolio_value(date)
            
            for code, target_ratio in self.allocations.items():
                price = self._get_price(code, date)
                if not price:
                    continue
                
                current_value = self.holdings.get(code, 0) * price
                current_ratio = current_value / total_value if total_value > 0 else 0
                
                if abs(current_ratio - target_ratio) > threshold:
                    return True
        
        return False
    
    def _execute_rebalance(self, date):
        """执行再平衡"""
        total_value = self._update_portfolio_value(date)
        
        # 卖出所有持仓
        self.cash = total_value
        
        # 按目标比例重新买入
        new_holdings = {}
        for code, ratio in self.allocations.items():
            target_amount = total_value * ratio
            price = self._get_price(code, date)
            
            if price and price > 0:
                shares = target_amount / price
                new_holdings[code] = shares
                self.cash -= target_amount
        
        self.holdings = new_holdings
        
        # 记录持仓
        for code, shares in self.holdings.items():
            price = self._get_price(code, date)
            market_value = shares * price if price else 0
            
            holding = Holding(
                scenario_id=self.scenario.id,
                product_code=code,
                date=date,
                shares=shares,
                cost_basis=market_value,
                market_value=market_value
            )
            db.session.add(holding)
        
        db.session.commit()
    
    def _record_daily_result(self, date):
        """记录每日结果"""
        total_value = self._update_portfolio_value(date)
        
        # 计算日收益率
        daily_return = 0
        if self.daily_results:
            prev_value = self.daily_results[-1]['total_value']
            if prev_value > 0:
                daily_return = (total_value - prev_value) / prev_value
        
        # 计算累计收益率
        cumulative_return = (total_value - self.total_invested) / self.total_invested if self.total_invested > 0 else 0
        
        # 计算回撤
        drawdown = 0
        if self.daily_results:
            peak = max(r['total_value'] for r in self.daily_results)
            if peak > 0:
                drawdown = (total_value - peak) / peak
        
        result = {
            'date': date,
            'total_value': total_value,
            'cash_value': self.cash,
            'invested_amount': self.total_invested,
            'daily_return': daily_return,
            'cumulative_return': cumulative_return,
            'drawdown': drawdown
        }
        
        self.daily_results.append(result)
    
    def _save_results(self):
        """保存回测结果到数据库"""
        for result in self.daily_results:
            backtest_result = BacktestResult(
                scenario_id=self.scenario.id,
                date=result['date'],
                total_value=result['total_value'],
                cash_value=result['cash_value'],
                invested_amount=result['invested_amount'],
                daily_return=result['daily_return'],
                cumulative_return=result['cumulative_return'],
                drawdown=result['drawdown']
            )
            db.session.add(backtest_result)
        
        db.session.commit()
