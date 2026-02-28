# 理财配置回测系统 - 设计方案

## 一、系统概述

### 1.1 项目目标
构建一个专业的Web版理财配置回测系统，支持对支付宝上的基金产品进行历史回测分析。

### 1.2 支持产品
| 产品类型 | 示例产品 | 特点 |
|---------|---------|------|
| 纳指ETF | 纳斯达克100指数基金 | 美股科技龙头，高成长 |
| 标普ETF | 标普500指数基金 | 美股大盘，稳健增长 |
| 混债基金 | 偏债混合型基金 | 股债平衡，稳健收益 |
| 红利低波ETF | 红利低波动指数基金 | 高分红，低波动 |
| 中证A50ETF | 中证A50指数基金 | A股核心资产 |

---

## 二、技术架构

### 2.1 技术栈选择
- **后端**: Python + Flask
- **前端**: Vue 3 + Element Plus + ECharts
- **数据库**: SQLite (轻量级，适合个人使用)
- **数据获取**: AKShare / Yahoo Finance API
- **计算库**: NumPy, Pandas, SciPy

### 2.2 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Vue 3)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ 配置面板 │ │ 回测结果 │ │ 图表展示 │ │ 对比分析 │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 层 (Flask)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ 产品管理 │ │ 回测引擎 │ │ 数据服务 │ │ 分析指标 │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│  │ SQLite   │ │ 数据获取 │ │ 缓存机制 │                     │
│  │ 数据库   │ │ 服务     │ │          │                     │
│  └──────────┘ └──────────┘ └──────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、核心功能模块

### 3.1 产品管理模块
- 添加/编辑/删除基金产品
- 产品分类管理（股票型、债券型、混合型、指数型）
- 产品基础信息维护（代码、名称、费率等）

### 3.2 智能配置模块
- **风险评估**: 基于年龄、收入、经验等多维度评估风险承受能力
- **配置建议**: 根据风险等级推荐最优资产配置方案
- **市场调整**: 支持根据市场环境（牛市/熊市/震荡市）调整配置
- **一键应用**: 将推荐配置直接应用到回测方案

### 3.3 回测引擎模块
- **策略配置**:
  - 资产配置比例设置
  - 再平衡策略（定期/阈值/不调整）
  - 定投策略（定期定额/智能定投）
  
- **回测计算**:
  - 收益率计算
  - 净值曲线生成
  - 交易记录模拟

### 3.4 风险分析模块
- 收益指标：年化收益率、累计收益
- 风险指标：波动率、最大回撤、夏普比率、索提诺比率
- 其他指标：阿尔法、贝塔、信息比率

### 3.5 可视化模块
- 净值曲线对比图
- 资产配置饼图
- 收益分布直方图
- 回撤曲线图
- 蒙特卡洛模拟结果展示

### 3.6 方案对比模块
- 多方案并行回测
- 关键指标对比表
- 风险收益散点图

### 3.7 运维管理模块
- **一键启停**: PowerShell 脚本快速启动和停止前后端服务
- **进程管理**: PID 文件管理，精准控制服务进程
- **状态监控**: 实时查看服务运行状态

---

## 四、数据库设计

### 4.1 数据表结构

```sql
-- 产品表
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,      -- 基金代码
    name VARCHAR(100) NOT NULL,             -- 基金名称
    type VARCHAR(20) NOT NULL,              -- 产品类型
    category VARCHAR(50),                   -- 细分分类
    fee_rate DECIMAL(5,4) DEFAULT 0,        -- 管理费率
    purchase_fee DECIMAL(5,4) DEFAULT 0,    -- 申购费率
    redemption_fee DECIMAL(5,4) DEFAULT 0,  -- 赎回费率
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 历史数据表
CREATE TABLE price_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    nav DECIMAL(10,4),                      -- 单位净值
    accumulated_nav DECIMAL(10,4),          -- 累计净值
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume BIGINT,
    UNIQUE(product_code, date)
);

-- 回测方案表
CREATE TABLE backtest_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_amount DECIMAL(15,2) DEFAULT 100000,
    rebalance_strategy VARCHAR(20),         -- 再平衡策略
    rebalance_period INTEGER,               -- 再平衡周期(月)
    rebalance_threshold DECIMAL(5,2),       -- 再平衡阈值(%)
    investment_strategy VARCHAR(20),        -- 定投策略
    monthly_amount DECIMAL(15,2),           -- 定投金额
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 方案资产配置表
CREATE TABLE scenario_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    product_code VARCHAR(20) NOT NULL,
    allocation_ratio DECIMAL(5,2) NOT NULL, -- 配置比例(%)
    FOREIGN KEY (scenario_id) REFERENCES backtest_scenarios(id)
);

-- 回测结果表
CREATE TABLE backtest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    date DATE NOT NULL,
    total_value DECIMAL(15,2),              -- 总资产价值
    cash_value DECIMAL(15,2),               -- 现金价值
    daily_return DECIMAL(8,4),              -- 日收益率
    cumulative_return DECIMAL(10,4),        -- 累计收益率
    drawdown DECIMAL(8,4),                  -- 回撤
    FOREIGN KEY (scenario_id) REFERENCES backtest_scenarios(id)
);

-- 持仓记录表
CREATE TABLE holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    product_code VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    shares DECIMAL(15,4),                   -- 持有份额
    cost_basis DECIMAL(15,4),               -- 成本
    market_value DECIMAL(15,4),             -- 市值
    FOREIGN KEY (scenario_id) REFERENCES backtest_scenarios(id)
);
```

---

## 五、API 接口设计

### 5.1 产品管理接口
```
GET    /api/products              # 获取产品列表
POST   /api/products              # 添加产品
PUT    /api/products/<id>         # 更新产品
DELETE /api/products/<id>         # 删除产品
GET    /api/products/<code>/data  # 获取产品历史数据
POST   /api/products/sync         # 同步产品数据
```

### 5.2 回测接口
```
POST   /api/backtest              # 执行回测
GET    /api/backtest/<id>         # 获取回测结果
GET    /api/backtest/<id>/metrics # 获取回测指标
DELETE /api/backtest/<id>         # 删除回测
```

### 5.3 分析接口
```
POST   /api/analysis/compare      # 多方案对比
POST   /api/analysis/monte-carlo  # 蒙特卡洛模拟
GET    /api/analysis/risk/<id>    # 风险分析
```

### 5.4 智能配置接口
```
POST   /api/smart-allocation/assess           # 风险评估与配置建议
GET    /api/smart-allocation/templates        # 获取配置模板
POST   /api/smart-allocation/adjust-by-market # 根据市场环境调整配置
GET    /api/smart-allocation/risk-questions   # 获取风险评估问卷
```

---

## 六、前端页面设计

### 6.1 页面结构
```
├── 首页 (Dashboard)
│   ├── 资产概览
│   ├── 今日收益
│   └── 快捷操作
│
├── 产品管理
│   ├── 产品列表
│   ├── 产品详情
│   └── 数据同步
│
├── 智能配置
│   ├── 风险评估问卷
│   ├── 配置建议展示
│   ├── 市场环境调整
│   └── 应用到回测
│
├── 回测中心
│   ├── 方案配置
│   │   ├── 基本信息
│   │   ├── 资产配置
│   │   └── 策略设置
│   ├── 回测结果
│   │   ├── 收益曲线
│   │   ├── 风险指标
│   │   └── 交易记录
│   └── 方案对比
│
└── 数据分析
    ├── 相关性分析
    ├── 蒙特卡洛模拟
    └── 情景分析
```

### 6.2 关键界面原型

**回测配置页面:**
```
┌─────────────────────────────────────────────────────────┐
│  回测配置                                                │
├─────────────────────────────────────────────────────────┤
│  基本信息                                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ 方案名称     │ │ 开始日期     │ │ 结束日期     │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
│  ┌──────────────┐ ┌──────────────┐                      │
│  │ 初始资金     │ │ 基准对比     │                      │
│  └──────────────┘ └──────────────┘                      │
├─────────────────────────────────────────────────────────┤
│  资产配置                                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 纳指ETF    [████████░░] 40%                     │   │
│  │ 标普ETF    [████░░░░░░] 20%                     │   │
│  │ 混债基金   [████░░░░░░] 20%                     │   │
│  │ 红利低波   [██░░░░░░░░] 10%                     │   │
│  │ 中证A50    [██░░░░░░░░] 10%                     │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  再平衡策略                                              │
│  ○ 不调整  ○ 定期再平衡(每[12]月)  ○ 阈值再平衡(偏离[5]%)│
├─────────────────────────────────────────────────────────┤
│  定投策略                                                │
│  ○ 不定投  ○ 定期定额(每月[5000]元)                    │
├─────────────────────────────────────────────────────────┤
│                    [开始回测]                           │
└─────────────────────────────────────────────────────────┘
```

**回测结果页面:**
```
┌─────────────────────────────────────────────────────────┐
│  回测结果 - 保守型配置                                    │
├─────────────────────────────────────────────────────────┤
│  关键指标                                                │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │
│  │年化收益│ │最大回撤│ │夏普比率│ │波动率  │           │
│  │ 12.5%  │ │ -15.3% │ │  1.25  │ │ 18.2%  │           │
│  └────────┘ └────────┘ └────────┘ └────────┘           │
├─────────────────────────────────────────────────────────┤
│  收益曲线                                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │    ╱╲        ╱╲                                 │   │
│  │   ╱  ╲      ╱  ╲       方案净值                 │   │
│  │  ╱    ╲____╱    ╲____                          │   │
│  │ ╱                   基准                        │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  回撤曲线  │  资产配置变化  │  收益分布                    │
└─────────────────────────────────────────────────────────┘
```

---

## 七、核心算法设计

### 7.1 回测引擎算法
```python
def run_backtest(scenario):
    """
    回测主流程
    """
    # 1. 初始化
    portfolio = initialize_portfolio(scenario.initial_amount)
    holdings = initialize_holdings(scenario.allocations)
    
    # 2. 获取历史数据
    price_data = fetch_historical_data(scenario.products, 
                                       scenario.start_date, 
                                       scenario.end_date)
    
    # 3. 按日遍历
    for date in trading_days:
        # 3.1 处理定投
        if is_investment_day(date, scenario.investment_strategy):
            execute_investment(portfolio, holdings, date, price_data)
        
        # 3.2 计算当日市值
        update_portfolio_value(portfolio, holdings, date, price_data)
        
        # 3.3 检查再平衡
        if should_rebalance(date, portfolio, holdings, scenario):
            execute_rebalance(portfolio, holdings, date, price_data, scenario)
        
        # 3.4 记录结果
        record_daily_result(portfolio, holdings, date)
    
    # 4. 计算指标
    metrics = calculate_metrics(portfolio.daily_returns)
    
    return portfolio, metrics
```

### 7.2 风险指标计算
```python
def calculate_metrics(returns):
    """
    计算风险指标
    """
    metrics = {}
    
    # 年化收益率
    metrics['annual_return'] = (1 + returns.mean()) ** 252 - 1
    
    # 年化波动率
    metrics['annual_volatility'] = returns.std() * np.sqrt(252)
    
    # 夏普比率 (假设无风险利率3%)
    risk_free_rate = 0.03
    metrics['sharpe_ratio'] = (metrics['annual_return'] - risk_free_rate) / metrics['annual_volatility']
    
    # 最大回撤
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    metrics['max_drawdown'] = drawdown.min()
    
    # 索提诺比率
    downside_returns = returns[returns < 0]
    downside_std = downside_returns.std() * np.sqrt(252)
    metrics['sortino_ratio'] = (metrics['annual_return'] - risk_free_rate) / downside_std
    
    # 卡玛比率
    metrics['calmar_ratio'] = metrics['annual_return'] / abs(metrics['max_drawdown'])
    
    return metrics
```

### 7.3 蒙特卡洛模拟
```python
def monte_carlo_simulation(returns, weights, n_simulations=1000, n_days=252*5):
    """
    蒙特卡洛模拟未来收益路径
    """
    # 计算历史统计量
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    results = []
    for _ in range(n_simulations):
        # 生成随机收益路径
        random_returns = np.random.multivariate_normal(mean_returns, cov_matrix, n_days)
        portfolio_returns = random_returns @ weights
        
        # 计算累计收益
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        results.append(cumulative_returns)
    
    return np.array(results)
```

---

## 八、项目目录结构

```
portfolio_backtest/
├── backend/                          # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py                 # 数据模型
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── products.py           # 产品接口
│   │   │   ├── backtest.py           # 回测接口
│   │   │   └── analysis.py           # 分析接口
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── data_service.py       # 数据服务
│   │   │   ├── backtest_engine.py    # 回测引擎
│   │   │   └── risk_analyzer.py      # 风险分析
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/                         # 前端代码
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/               # 公共组件
│   │   │   ├── Charts/
│   │   │   ├── Tables/
│   │   │   └── Forms/
│   │   ├── views/                    # 页面
│   │   │   ├── Dashboard/
│   │   │   ├── Products/
│   │   │   ├── Backtest/
│   │   │   └── Analysis/
│   │   ├── stores/                   # Pinia状态管理
│   │   ├── api/                      # API接口
│   │   ├── utils/                    # 工具函数
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
├── data/                             # 数据文件
│   └── portfolio.db
│
├── docs/                             # 文档
│   ├── DESIGN.md
│   └── API.md
│
└── README.md
```

---

## 九、实现步骤

### Phase 1: 基础架构搭建 (Week 1)
1. 搭建 Flask 后端框架
2. 设计并实现数据库模型
3. 搭建 Vue 3 前端项目
4. 配置开发环境

### Phase 2: 数据层开发 (Week 1-2)
1. 实现基金数据获取服务
2. 实现数据存储和缓存机制
3. 开发产品管理接口
4. 前端产品管理页面

### Phase 3: 回测引擎开发 (Week 2-3)
1. 实现核心回测算法
2. 实现再平衡策略
3. 实现定投策略
4. 开发回测接口

### Phase 4: 分析模块开发 (Week 3)
1. 实现风险指标计算
2. 实现蒙特卡洛模拟
3. 实现方案对比功能
4. 开发分析接口

### Phase 5: 前端可视化 (Week 3-4)
1. 开发回测配置页面
2. 开发结果展示页面
3. 集成 ECharts 图表
4. 实现方案对比功能

### Phase 6: 测试与优化 (Week 4)
1. 单元测试
2. 集成测试
3. 性能优化
4. 文档完善

---

## 十、关键技术点

### 10.1 数据获取方案
```python
# 方案1: AKShare (推荐，免费)
import akshare as ak
fund_data = ak.fund_etf_hist_em(symbol="513100", period="daily")

# 方案2: Yahoo Finance
import yfinance as yf
ticker = yf.Ticker("QQQ")
hist = ticker.history(period="5y")
```

### 10.2 性能优化
- 使用 Pandas 向量化运算
- 数据库索引优化
- 数据缓存机制
- 异步任务处理

### 10.3 精度处理
- 金额保留2位小数
- 收益率保留4位小数
- 份额保留4位小数
- 避免浮点数精度问题

---

## 十一、后续扩展方向

1. **智能配置建议**: 基于风险承受能力的配置推荐
2. **实时数据接入**: 接入实时行情数据
3. **预警系统**: 配置偏离预警、市场波动预警
4. **多因子模型**: 加入更多因子进行收益分析
5. **机器学习**: 预测模型、智能调仓
