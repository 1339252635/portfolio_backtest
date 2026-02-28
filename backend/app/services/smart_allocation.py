"""
智能资产配置建议服务
基于风险承受能力和投资目标生成配置建议
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    CONSERVATIVE = "conservative"      # 保守型
    CAUTIOUS = "cautious"              # 谨慎型
    BALANCED = "balanced"              # 平衡型
    AGGRESSIVE = "aggressive"          # 进取型
    RADICAL = "radical"                # 激进型


class InvestmentGoal(Enum):
    """投资目标"""
    CAPITAL_PRESERVATION = "capital_preservation"  # 资产保值
    STEADY_INCOME = "steady_income"                # 稳定收益
    BALANCED_GROWTH = "balanced_growth"            # 平衡增长
    CAPITAL_GROWTH = "capital_growth"              # 资本增值
    AGGRESSIVE_GROWTH = "aggressive_growth"        # 激进增长


@dataclass
class RiskProfile:
    """风险画像"""
    age: int
    investment_experience: int  # 投资经验年数
    annual_income: float        # 年收入
    liquid_assets: float        # 流动资产
    investment_horizon: int     # 投资期限（年）
    loss_tolerance: float       # 可承受最大损失比例（0-1）
    monthly_investment: float   # 月投资金额


@dataclass
class AllocationSuggestion:
    """配置建议"""
    risk_level: RiskLevel
    investment_goal: InvestmentGoal
    allocations: Dict[str, float]  # 资产配置比例
    expected_return: float         # 预期年化收益率
    expected_volatility: float     # 预期波动率
    max_drawdown: float            # 预期最大回撤
    sharpe_ratio: float            # 预期夏普比率
    description: str               # 建议说明
    reasoning: List[str]           # 推荐理由


class SmartAllocationService:
    """智能配置服务"""
    
    # 预设资产配置模板
    ALLOCATION_TEMPLATES = {
        RiskLevel.CONSERVATIVE: {
            "混债基金": 50.0,
            "红利低波": 30.0,
            "中证A50": 10.0,
            "标普ETF": 5.0,
            "纳指ETF": 5.0
        },
        RiskLevel.CAUTIOUS: {
            "混债基金": 40.0,
            "红利低波": 25.0,
            "中证A50": 15.0,
            "标普ETF": 12.0,
            "纳指ETF": 8.0
        },
        RiskLevel.BALANCED: {
            "混债基金": 25.0,
            "红利低波": 20.0,
            "中证A50": 20.0,
            "标普ETF": 20.0,
            "纳指ETF": 15.0
        },
        RiskLevel.AGGRESSIVE: {
            "混债基金": 10.0,
            "红利低波": 15.0,
            "中证A50": 25.0,
            "标普ETF": 25.0,
            "纳指ETF": 25.0
        },
        RiskLevel.RADICAL: {
            "混债基金": 0.0,
            "红利低波": 10.0,
            "中证A50": 20.0,
            "标普ETF": 35.0,
            "纳指ETF": 35.0
        }
    }
    
    # 预期收益和风险指标（基于历史数据估算）
    EXPECTED_METRICS = {
        RiskLevel.CONSERVATIVE: {
            "return": 0.05,
            "volatility": 0.08,
            "max_drawdown": -0.10,
            "sharpe_ratio": 0.50
        },
        RiskLevel.CAUTIOUS: {
            "return": 0.07,
            "volatility": 0.12,
            "max_drawdown": -0.15,
            "sharpe_ratio": 0.60
        },
        RiskLevel.BALANCED: {
            "return": 0.10,
            "volatility": 0.18,
            "max_drawdown": -0.25,
            "sharpe_ratio": 0.70
        },
        RiskLevel.AGGRESSIVE: {
            "return": 0.13,
            "volatility": 0.25,
            "max_drawdown": -0.35,
            "sharpe_ratio": 0.75
        },
        RiskLevel.RADICAL: {
            "return": 0.16,
            "volatility": 0.32,
            "max_drawdown": -0.45,
            "sharpe_ratio": 0.70
        }
    }
    
    # 风险等级描述
    RISK_DESCRIPTIONS = {
        RiskLevel.CONSERVATIVE: "保守型配置，以保本为主，适合风险厌恶型投资者",
        RiskLevel.CAUTIOUS: "谨慎型配置，追求稳定收益，适合保守型投资者",
        RiskLevel.BALANCED: "平衡型配置，风险收益均衡，适合稳健型投资者",
        RiskLevel.AGGRESSIVE: "进取型配置，追求较高收益，适合积极型投资者",
        RiskLevel.RADICAL: "激进型配置，追求高收益，适合激进型投资者"
    }
    
    @classmethod
    def assess_risk_level(cls, profile: RiskProfile) -> RiskLevel:
        """
        评估风险承受能力等级
        
        评分维度：
        1. 年龄（权重25%）：越年轻风险承受能力越高
        2. 投资经验（权重20%）：经验越丰富风险承受能力越高
        3. 收入稳定性（权重15%）：收入越高越稳定风险承受能力越高
        4. 资产状况（权重15%）：资产越多风险承受能力越高
        5. 投资期限（权重10%）：期限越长风险承受能力越高
        6. 损失容忍度（权重15%）：可承受损失越大风险承受能力越高
        """
        score = 0.0
        
        # 年龄评分（25%）
        if profile.age < 30:
            score += 25
        elif profile.age < 40:
            score += 20
        elif profile.age < 50:
            score += 15
        elif profile.age < 60:
            score += 10
        else:
            score += 5
        
        # 投资经验评分（20%）
        if profile.investment_experience >= 10:
            score += 20
        elif profile.investment_experience >= 5:
            score += 15
        elif profile.investment_experience >= 2:
            score += 10
        else:
            score += 5
        
        # 收入评分（15%）
        income_score = min(profile.annual_income / 200000, 1.0) * 15
        score += income_score
        
        # 资产评分（15%）
        asset_score = min(profile.liquid_assets / 1000000, 1.0) * 15
        score += asset_score
        
        # 投资期限评分（10%）
        if profile.investment_horizon >= 20:
            score += 10
        elif profile.investment_horizon >= 10:
            score += 8
        elif profile.investment_horizon >= 5:
            score += 6
        elif profile.investment_horizon >= 3:
            score += 4
        else:
            score += 2
        
        # 损失容忍度评分（15%）
        loss_score = profile.loss_tolerance * 15
        score += loss_score
        
        # 根据总分确定风险等级
        if score >= 80:
            return RiskLevel.RADICAL
        elif score >= 65:
            return RiskLevel.AGGRESSIVE
        elif score >= 50:
            return RiskLevel.BALANCED
        elif score >= 35:
            return RiskLevel.CAUTIOUS
        else:
            return RiskLevel.CONSERVATIVE
    
    @classmethod
    def determine_investment_goal(cls, risk_level: RiskLevel, profile: RiskProfile) -> InvestmentGoal:
        """确定投资目标"""
        goal_mapping = {
            RiskLevel.CONSERVATIVE: InvestmentGoal.CAPITAL_PRESERVATION,
            RiskLevel.CAUTIOUS: InvestmentGoal.STEADY_INCOME,
            RiskLevel.BALANCED: InvestmentGoal.BALANCED_GROWTH,
            RiskLevel.AGGRESSIVE: InvestmentGoal.CAPITAL_GROWTH,
            RiskLevel.RADICAL: InvestmentGoal.AGGRESSIVE_GROWTH
        }
        return goal_mapping.get(risk_level, InvestmentGoal.BALANCED_GROWTH)
    
    @classmethod
    def generate_reasoning(cls, risk_level: RiskLevel, profile: RiskProfile) -> List[str]:
        """生成推荐理由"""
        reasoning = []
        
        # 基于年龄
        if profile.age < 30:
            reasoning.append("您处于年轻阶段，有较长的投资时间 horizon，可以承担较高的市场波动")
        elif profile.age < 40:
            reasoning.append("您处于职业发展的黄金期，收入稳定增长，适合进行长期投资")
        elif profile.age < 50:
            reasoning.append("您处于中年阶段，应在稳健基础上适当追求收益增长")
        elif profile.age < 60:
            reasoning.append("您接近退休年龄，建议以稳健投资为主，保护已有资产")
        else:
            reasoning.append("您已退休或即将退休，应以资产保值和稳定收益为主要目标")
        
        # 基于投资经验
        if profile.investment_experience >= 5:
            reasoning.append(f"您拥有{profile.investment_experience}年投资经验，对市场波动有较好的理解和承受能力")
        else:
            reasoning.append("您投资经验相对较少，建议从稳健配置开始，逐步积累经验")
        
        # 基于投资期限
        if profile.investment_horizon >= 10:
            reasoning.append(f"您的投资期限为{profile.investment_horizon}年，属于长期投资，可以平滑市场短期波动")
        elif profile.investment_horizon >= 5:
            reasoning.append(f"您的投资期限为{profile.investment_horizon}年，建议采用平衡配置策略")
        else:
            reasoning.append(f"您的投资期限较短({profile.investment_horizon}年)，应注重资产的流动性和安全性")
        
        # 基于损失容忍度
        if profile.loss_tolerance >= 0.30:
            reasoning.append(f"您可承受{profile.loss_tolerance*100:.0f}%的投资损失，表明您对市场波动有较高的容忍度")
        elif profile.loss_tolerance >= 0.15:
            reasoning.append(f"您可承受{profile.loss_tolerance*100:.0f}%的投资损失，属于中等风险承受能力")
        else:
            reasoning.append(f"您可承受{profile.loss_tolerance*100:.0f}%的投资损失，建议以稳健投资为主")
        
        return reasoning
    
    @classmethod
    def get_allocation_suggestion(cls, profile: RiskProfile) -> AllocationSuggestion:
        """获取资产配置建议"""
        # 评估风险等级
        risk_level = cls.assess_risk_level(profile)
        
        # 确定投资目标
        investment_goal = cls.determine_investment_goal(risk_level, profile)
        
        # 获取配置模板
        allocations = cls.ALLOCATION_TEMPLATES[risk_level].copy()
        
        # 获取预期指标
        metrics = cls.EXPECTED_METRICS[risk_level]
        
        # 生成推荐理由
        reasoning = cls.generate_reasoning(risk_level, profile)
        
        # 生成描述
        description = cls.RISK_DESCRIPTIONS[risk_level]
        
        return AllocationSuggestion(
            risk_level=risk_level,
            investment_goal=investment_goal,
            allocations=allocations,
            expected_return=metrics["return"],
            expected_volatility=metrics["volatility"],
            max_drawdown=metrics["max_drawdown"],
            sharpe_ratio=metrics["sharpe_ratio"],
            description=description,
            reasoning=reasoning
        )
    
    @classmethod
    def get_all_suggestions(cls) -> Dict[RiskLevel, AllocationSuggestion]:
        """获取所有风险等级的配置建议（用于展示对比）"""
        suggestions = {}
        
        # 使用默认画像生成各等级的建议
        default_profile = RiskProfile(
            age=35,
            investment_experience=3,
            annual_income=200000,
            liquid_assets=300000,
            investment_horizon=10,
            loss_tolerance=0.20,
            monthly_investment=5000
        )
        
        for risk_level in RiskLevel:
            # 手动设置风险等级，跳过评估
            investment_goal = cls.determine_investment_goal(risk_level, default_profile)
            allocations = cls.ALLOCATION_TEMPLATES[risk_level].copy()
            metrics = cls.EXPECTED_METRICS[risk_level]
            
            suggestions[risk_level] = AllocationSuggestion(
                risk_level=risk_level,
                investment_goal=investment_goal,
                allocations=allocations,
                expected_return=metrics["return"],
                expected_volatility=metrics["volatility"],
                max_drawdown=metrics["max_drawdown"],
                sharpe_ratio=metrics["sharpe_ratio"],
                description=cls.RISK_DESCRIPTIONS[risk_level],
                reasoning=[]
            )
        
        return suggestions
    
    @classmethod
    def adjust_allocation_by_market(cls, base_allocation: Dict[str, float], 
                                   market_condition: str) -> Dict[str, float]:
        """
        根据市场环境调整配置
        
        Args:
            base_allocation: 基础配置
            market_condition: 市场环境 (bull/bear/sideways)
        """
        adjusted = base_allocation.copy()
        
        if market_condition == "bull":  # 牛市
            # 增加权益类资产
            adjusted["纳指ETF"] = min(adjusted.get("纳指ETF", 0) * 1.2, 40)
            adjusted["标普ETF"] = min(adjusted.get("标普ETF", 0) * 1.2, 35)
            adjusted["混债基金"] = adjusted.get("混债基金", 0) * 0.8
        elif market_condition == "bear":  # 熊市
            # 增加防御性资产
            adjusted["混债基金"] = min(adjusted.get("混债基金", 0) * 1.3, 60)
            adjusted["红利低波"] = min(adjusted.get("红利低波", 0) * 1.2, 35)
            adjusted["纳指ETF"] = adjusted.get("纳指ETF", 0) * 0.7
            adjusted["标普ETF"] = adjusted.get("标普ETF", 0) * 0.8
        
        # 归一化到100%
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: round(v / total * 100, 2) for k, v in adjusted.items()}
        
        return adjusted


# 便捷函数
def get_smart_allocation(age: int, investment_experience: int, annual_income: float,
                        liquid_assets: float, investment_horizon: int, 
                        loss_tolerance: float, monthly_investment: float) -> AllocationSuggestion:
    """
    获取智能配置建议的便捷函数
    
    Args:
        age: 年龄
        investment_experience: 投资经验年数
        annual_income: 年收入
        liquid_assets: 流动资产
        investment_horizon: 投资期限（年）
        loss_tolerance: 可承受最大损失比例（0-1）
        monthly_investment: 月投资金额
    
    Returns:
        AllocationSuggestion: 配置建议
    """
    profile = RiskProfile(
        age=age,
        investment_experience=investment_experience,
        annual_income=annual_income,
        liquid_assets=liquid_assets,
        investment_horizon=investment_horizon,
        loss_tolerance=loss_tolerance,
        monthly_investment=monthly_investment
    )
    
    return SmartAllocationService.get_allocation_suggestion(profile)
