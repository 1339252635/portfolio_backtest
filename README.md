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
- **产品管理**：添加/编辑/删除基金产品，同步历史数据
- **智能配置**：基于风险承受能力自动生成资产配置建议
- **回测引擎**：支持资产配置、再平衡策略、定投策略
- **风险分析**：夏普比率、最大回撤、波动率、索提诺比率、卡玛比率
- **可视化**：净值曲线、回撤曲线、收益分布、蒙特卡洛模拟
- **方案对比**：多方案并行回测，风险收益对比
- **一键启停**：PowerShell脚本快速启动和停止前后端服务

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

### 方式一：手动启动（推荐）

在单独的终端窗口中分别启动前后端服务：

**终端 1 - 启动后端：**
```bash
cd backend
py run.py
```
后端服务将在 http://localhost:5000 启动

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```
前端服务将在 http://localhost:3000 启动

**或使用批处理脚本一键启动：**
```bash
# 启动服务（会打开两个独立的命令行窗口）
start-manual.bat

# 停止服务
stop-manual.bat
```

### 方式二：PowerShell 脚本（高级用户）

系统提供 PowerShell 脚本管理工具：

```powershell
# 启动所有服务
.\start-all.ps1

# 或
.\manage.ps1 start
```

**其他常用命令：**

```powershell
# 查看服务状态
.\manage.ps1 status

# 停止所有服务
.\stop-all.ps1

# 重启服务
.\manage.ps1 restart

# 强制停止（清理残留进程）
.\stop-all.ps1 -Force
```

> **注意**：首次运行脚本可能需要设置 PowerShell 执行策略：
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

### 方式二：手动启动

如需手动控制服务，可以分别启动前后端。

#### 1. 安装后端依赖

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

#### 2. 启动后端服务

```bash
python run.py
```

后端服务将在 http://localhost:5000 启动

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

#### 4. 启动前端开发服务器

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

### 智能配置
- `POST /api/smart-allocation/assess` - 风险评估与配置建议
- `GET /api/smart-allocation/templates` - 获取配置模板
- `POST /api/smart-allocation/adjust-by-market` - 根据市场环境调整配置
- `GET /api/smart-allocation/risk-questions` - 获取风险评估问卷

## 项目结构

```
portfolio_backtest/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── models.py          # 数据模型
│   │   ├── routes/            # API路由
│   │   │   ├── products.py
│   │   │   ├── backtest.py
│   │   │   ├── analysis.py
│   │   │   └── smart_allocation.py  # 智能配置API
│   │   ├── services/          # 业务逻辑
│   │   │   ├── data_service.py
│   │   │   ├── backtest_engine.py
│   │   │   ├── risk_analyzer.py
│   │   │   └── smart_allocation.py  # 智能配置服务
│   │   └── utils/
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── api/               # API接口
│   │   │   └── smartAllocation.js   # 智能配置API
│   │   ├── stores/            # Pinia状态管理
│   │   ├── views/             # 页面组件
│   │   │   ├── Dashboard/
│   │   │   ├── Products/
│   │   │   ├── SmartAllocation/     # 智能配置页面
│   │   │   ├── Backtest/
│   │   │   └── Analysis/
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
├── docs/                       # 文档目录
│   └── 操作手册.md
│
├── data/                       # 数据库文件
│   └── portfolio.db
│
├── start-all.ps1              # 一键启动脚本
├── stop-all.ps1               # 一键停止脚本
├── manage.ps1                 # 统一管理脚本
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
- [x] Phase 5: 智能配置建议
- [x] Phase 6: 一键启停脚本
- [ ] Phase 7: 前端可视化优化
- [ ] Phase 8: 测试与优化

## 后续扩展

1. ~~**智能配置建议**: 基于风险承受能力的配置推荐~~ ✅ 已完成
2. ~~**一键启停脚本**: PowerShell 脚本管理服务~~ ✅ 已完成
3. **实时数据接入**: 接入实时行情数据
4. **预警系统**: 配置偏离预警、市场波动预警
5. **多因子模型**: 加入更多因子进行收益分析
6. **机器学习**: 预测模型、智能调仓

## 许可证

MIT License
