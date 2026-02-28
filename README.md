# 理财配置回测系统

一个专业的Web版理财配置回测系统，支持对支付宝上的基金产品进行历史回测分析。

## 功能特性

### 支持的理财产品
- **纳指ETF** - 纳斯达克100指数基金，美股科技龙头
- **标普ETF** - 标普500指数基金，美股大盘
- **混债基金** - 偏债混合型基金，股债平衡
- **红利低波ETF** - 红利低波动指数基金，高分红低波动
- **中证A50ETF** - 中证A50指数基金，A股核心资产

### 核心功能
- 产品管理：添加/编辑/删除基金产品，同步历史数据
- 回测引擎：支持资产配置、再平衡策略、定投策略
- 风险分析：夏普比率、最大回撤、波动率、索提诺比率、卡玛比率
- 可视化：净值曲线、回撤曲线、收益分布、蒙特卡洛模拟
- 方案对比：多方案并行回测，风险收益对比

### 再平衡策略
1. **不调整** - 买入持有
2. **定期再平衡** - 按月/季度/年调整
3. **阈值再平衡** - 偏离目标配置一定比例时调整

### 定投策略
1. **不定投** - 一次性投入
2. **定期定额** - 每月固定金额

## 技术架构

### 后端
- **框架**: Python + Flask
- **数据库**: SQLite
- **数据源**: AKShare / Yahoo Finance
- **计算库**: NumPy, Pandas, SciPy

### 前端
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **图表**: ECharts
- **状态管理**: Pinia

## 快速开始

### 1. 安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
# 方式1：直接启动
python run.py

# 方式2：使用启动脚本
cd ..
python start_backend.py
```

后端服务将在 http://localhost:5000 启动

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动前端开发服务器

```bash
npm run dev
```

前端将在 http://localhost:3000 启动

### 5. 初始化数据

1. 打开前端页面 http://localhost:3000
2. 进入"产品管理"页面
3. 点击"初始化默认产品"按钮
4. 选择产品并点击"同步数据"获取历史数据

## API 接口

### 产品管理
- `GET /api/products` - 获取产品列表
- `POST /api/products` - 添加产品
- `PUT /api/products/<id>` - 更新产品
- `DELETE /api/products/<id>` - 删除产品
- `GET /api/products/<code>/data` - 获取产品历史数据
- `POST /api/products/sync` - 同步产品数据

### 回测
- `GET /api/backtest` - 获取回测方案列表
- `POST /api/backtest` - 创建回测方案并执行回测
- `GET /api/backtest/<id>/results` - 获取回测结果
- `GET /api/backtest/<id>/metrics` - 获取回测指标

### 分析
- `POST /api/analysis/compare` - 多方案对比
- `POST /api/analysis/monte-carlo` - 蒙特卡洛模拟
- `POST /api/analysis/correlation` - 相关性分析

## 项目结构

```
portfolio_backtest/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── models.py          # 数据模型
│   │   ├── routes/            # API路由
│   │   │   ├── products.py
│   │   │   ├── backtest.py
│   │   │   └── analysis.py
│   │   ├── services/          # 业务逻辑
│   │   │   ├── data_service.py
│   │   │   ├── backtest_engine.py
│   │   │   └── risk_analyzer.py
│   │   └── utils/
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── api/               # API接口
│   │   ├── stores/            # Pinia状态管理
│   │   ├── views/             # 页面组件
│   │   │   ├── Dashboard/
│   │   │   ├── Products/
│   │   │   ├── Backtest/
│   │   │   └── Analysis/
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
├── data/                       # 数据库文件
│   └── portfolio.db
│
└── README.md
```

## 使用示例

### 创建回测方案

```json
{
  "name": "保守型配置",
  "description": "稳健的长期投资策略",
  "start_date": "2020-01-01",
  "end_date": "2024-01-01",
  "initial_amount": 100000,
  "rebalance_strategy": "periodic",
  "rebalance_period": 12,
  "investment_strategy": "fixed",
  "monthly_amount": 5000,
  "allocations": [
    {"product_code": "513100", "allocation_ratio": 40},
    {"product_code": "513500", "allocation_ratio": 20},
    {"product_code": "000171", "allocation_ratio": 20},
    {"product_code": "515080", "allocation_ratio": 10},
    {"product_code": "560050", "allocation_ratio": 10}
  ]
}
```

## 风险指标说明

| 指标 | 说明 |
|------|------|
| 年化收益率 | 投资在一年内的收益率 |
| 年化波动率 | 收益率的标准差，衡量风险 |
| 最大回撤 | 从峰值到谷底的最大跌幅 |
| 夏普比率 | 风险调整后的收益指标 |
| 索提诺比率 | 只考虑下行风险的收益指标 |
| 卡玛比率 | 年化收益与最大回撤的比值 |
| VaR | 在特定置信水平下的最大可能损失 |

## 开发计划

- [x] Phase 1: 基础架构搭建
- [x] Phase 2: 数据层开发
- [x] Phase 3: 回测引擎开发
- [x] Phase 4: 分析模块开发
- [ ] Phase 5: 前端可视化（部分完成）
- [ ] Phase 6: 测试与优化

## 后续扩展

1. **智能配置建议**: 基于风险承受能力的配置推荐
2. **实时数据接入**: 接入实时行情数据
3. **预警系统**: 配置偏离预警、市场波动预警
4. **多因子模型**: 加入更多因子进行收益分析
5. **机器学习**: 预测模型、智能调仓

## 许可证

MIT License
