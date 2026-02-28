from datetime import datetime
from app import db


class Product(db.Model):
    """基金产品表"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 产品类型
    category = db.Column(db.String(50))  # 细分分类
    fee_rate = db.Column(db.Numeric(5, 4), default=0)  # 管理费率
    purchase_fee = db.Column(db.Numeric(5, 4), default=0)  # 申购费率
    redemption_fee = db.Column(db.Numeric(5, 4), default=0)  # 赎回费率
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    price_data = db.relationship('PriceData', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'type': self.type,
            'category': self.category,
            'fee_rate': float(self.fee_rate) if self.fee_rate else 0,
            'purchase_fee': float(self.purchase_fee) if self.purchase_fee else 0,
            'redemption_fee': float(self.redemption_fee) if self.redemption_fee else 0,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PriceData(db.Model):
    """历史价格数据表"""
    __tablename__ = 'price_data'
    
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(20), db.ForeignKey('products.code'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    nav = db.Column(db.Numeric(10, 4))  # 单位净值
    accumulated_nav = db.Column(db.Numeric(10, 4))  # 累计净值
    open_price = db.Column(db.Numeric(10, 4))
    high_price = db.Column(db.Numeric(10, 4))
    low_price = db.Column(db.Numeric(10, 4))
    close_price = db.Column(db.Numeric(10, 4))
    volume = db.Column(db.BigInteger)
    
    __table_args__ = (
        db.UniqueConstraint('product_code', 'date', name='uix_price_data'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_code': self.product_code,
            'date': self.date.isoformat() if self.date else None,
            'nav': float(self.nav) if self.nav else None,
            'accumulated_nav': float(self.accumulated_nav) if self.accumulated_nav else None,
            'open_price': float(self.open_price) if self.open_price else None,
            'high_price': float(self.high_price) if self.high_price else None,
            'low_price': float(self.low_price) if self.low_price else None,
            'close_price': float(self.close_price) if self.close_price else None,
            'volume': self.volume
        }


class BacktestScenario(db.Model):
    """回测方案表"""
    __tablename__ = 'backtest_scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    initial_amount = db.Column(db.Numeric(15, 2), default=100000)  # 初始资金
    
    # 再平衡策略
    rebalance_strategy = db.Column(db.String(20), default='none')  # none, periodic, threshold
    rebalance_period = db.Column(db.Integer)  # 再平衡周期(月)
    rebalance_threshold = db.Column(db.Numeric(5, 2))  # 再平衡阈值(%)
    
    # 定投策略
    investment_strategy = db.Column(db.String(20), default='none')  # none, fixed
    monthly_amount = db.Column(db.Numeric(15, 2))  # 定投金额
    investment_day = db.Column(db.Integer, default=1)  # 定投日
    
    # 基准对比
    benchmark_code = db.Column(db.String(20))  # 基准产品代码
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    allocations = db.relationship('ScenarioAllocation', backref='scenario', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('BacktestResult', backref='scenario', lazy='dynamic', cascade='all, delete-orphan')
    holdings = db.relationship('Holding', backref='scenario', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'initial_amount': float(self.initial_amount) if self.initial_amount else 100000,
            'rebalance_strategy': self.rebalance_strategy,
            'rebalance_period': self.rebalance_period,
            'rebalance_threshold': float(self.rebalance_threshold) if self.rebalance_threshold else None,
            'investment_strategy': self.investment_strategy,
            'monthly_amount': float(self.monthly_amount) if self.monthly_amount else None,
            'investment_day': self.investment_day,
            'benchmark_code': self.benchmark_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'allocations': [a.to_dict() for a in self.allocations.all()]
        }


class ScenarioAllocation(db.Model):
    """方案资产配置表"""
    __tablename__ = 'scenario_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('backtest_scenarios.id'), nullable=False)
    product_code = db.Column(db.String(20), nullable=False)
    allocation_ratio = db.Column(db.Numeric(5, 2), nullable=False)  # 配置比例(%)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scenario_id': self.scenario_id,
            'product_code': self.product_code,
            'allocation_ratio': float(self.allocation_ratio) if self.allocation_ratio else 0
        }


class BacktestResult(db.Model):
    """回测结果表"""
    __tablename__ = 'backtest_results'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('backtest_scenarios.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_value = db.Column(db.Numeric(15, 2))  # 总资产价值
    cash_value = db.Column(db.Numeric(15, 2))  # 现金价值
    invested_amount = db.Column(db.Numeric(15, 2))  # 已投入金额
    daily_return = db.Column(db.Numeric(8, 4))  # 日收益率
    cumulative_return = db.Column(db.Numeric(10, 4))  # 累计收益率
    drawdown = db.Column(db.Numeric(8, 4))  # 回撤
    
    def to_dict(self):
        return {
            'id': self.id,
            'scenario_id': self.scenario_id,
            'date': self.date.isoformat() if self.date else None,
            'total_value': float(self.total_value) if self.total_value else 0,
            'cash_value': float(self.cash_value) if self.cash_value else 0,
            'invested_amount': float(self.invested_amount) if self.invested_amount else 0,
            'daily_return': float(self.daily_return) if self.daily_return else 0,
            'cumulative_return': float(self.cumulative_return) if self.cumulative_return else 0,
            'drawdown': float(self.drawdown) if self.drawdown else 0
        }


class Holding(db.Model):
    """持仓记录表"""
    __tablename__ = 'holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('backtest_scenarios.id'), nullable=False)
    product_code = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shares = db.Column(db.Numeric(15, 4))  # 持有份额
    cost_basis = db.Column(db.Numeric(15, 4))  # 成本
    market_value = db.Column(db.Numeric(15, 4))  # 市值
    
    def to_dict(self):
        return {
            'id': self.id,
            'scenario_id': self.scenario_id,
            'product_code': self.product_code,
            'date': self.date.isoformat() if self.date else None,
            'shares': float(self.shares) if self.shares else 0,
            'cost_basis': float(self.cost_basis) if self.cost_basis else 0,
            'market_value': float(self.market_value) if self.market_value else 0
        }
