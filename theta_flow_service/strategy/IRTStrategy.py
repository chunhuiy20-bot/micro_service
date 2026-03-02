"""
文件名: IRTStrategy.py
描述: 基于IRT(项目反应理论)的学生答题概率预测策略
     1PL: P(θ) = 1 / (1 + e^(-(θ-β)))
     2PL: P(θ) = 1 / (1 + e^(-α(θ-β)))
     3PL: P(θ) = c + (1-c) / (1 + e^(-α(θ-β)))
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class QuestionParam:
    """题目参数"""
    alpha: float        # 区分度，题目知识点覆盖与融合程度
    beta: float         # 难度，取值 (-3, 3)
    c: float = 0.0      # 猜测参数，选择题取 1/选项数（如四选一=0.25），主观题=0


@dataclass
class IRTResult:
    """IRT预测结果"""
    theta: float        # 学生能力值
    probability: float  # 答对概率
    alpha: float
    beta: float
    c: float = 0.0      # 猜测参数


class IRTStrategy(ABC):
    """IRT策略抽象基类"""

    @abstractmethod
    def predict(self, theta: float, question: QuestionParam) -> IRTResult:
        pass


class TwoPLStrategy(IRTStrategy):
    """2参数逻辑斯蒂模型: P(θ) = 1 / (1 + e^(-α(θ-β)))"""

    THETA_RANGE = (-3.0, 3.0)
    BETA_RANGE = (-3.0, 3.0)

    def predict(self, theta: float, question: QuestionParam) -> IRTResult:
        theta = max(self.THETA_RANGE[0], min(self.THETA_RANGE[1], theta))
        beta = max(self.BETA_RANGE[0], min(self.BETA_RANGE[1], question.beta))

        prob = 1.0 / (1.0 + math.exp(-question.alpha * (theta - beta)))

        return IRTResult(
            theta=theta,
            probability=round(prob, 4),
            alpha=question.alpha,
            beta=beta
        )


class ThreePLStrategy(IRTStrategy):
    """3参数逻辑斯蒂模型: P(θ) = c + (1-c) / (1 + e^(-α(θ-β)))"""

    THETA_RANGE = (-3.0, 3.0)
    BETA_RANGE = (-3.0, 3.0)

    def predict(self, theta: float, question: QuestionParam) -> IRTResult:
        theta = max(self.THETA_RANGE[0], min(self.THETA_RANGE[1], theta))
        beta = max(self.BETA_RANGE[0], min(self.BETA_RANGE[1], question.beta))
        c = max(0.0, min(1.0, question.c))

        prob = c + (1 - c) / (1.0 + math.exp(-question.alpha * (theta - beta)))

        return IRTResult(
            theta=theta,
            probability=round(prob, 4),
            alpha=question.alpha,
            beta=beta,
            c=c
        )


class OnePLStrategy(IRTStrategy):
    """1参数逻辑斯蒂模型(Rasch): α固定为1"""

    def predict(self, theta: float, question: QuestionParam) -> IRTResult:
        fixed = QuestionParam(alpha=1.0, beta=question.beta)
        return TwoPLStrategy().predict(theta, fixed)


class IRTStrategyFactory:

    _strategies = {
        "1pl": OnePLStrategy,
        "2pl": TwoPLStrategy,
        "3pl": ThreePLStrategy,
    }

    @staticmethod
    def get_strategy(model: str = "2pl") -> IRTStrategy:
        cls = IRTStrategyFactory._strategies.get(model.lower())
        if not cls:
            raise ValueError(f"不支持的IRT模型: {model}，可选: {list(IRTStrategyFactory._strategies.keys())}")
        return cls()


def solve_beta(theta: float, target_prob: float, alpha: float = 1.0, c: float = 0.0) -> float:
    """
    已知学生能力 θ 和目标答对概率，反推题目难度 β（解析解）

    推导（以 3PL 为例）:
        P = c + (1-c) / (1 + e^(-α(θ-β)))
        令 P' = (P-c) / (1-c)          # 去除猜测下限后的净概率
        β = θ - ln(P'/(1-P')) / α      # logit 反变换

    Args:
        theta:       学生能力值，取值 [-3, 3]
        target_prob: 目标答对概率，取值 (c, 1)
        alpha:       题目区分度，默认 1.0
        c:           猜测参数，默认 0.0

    Returns:
        β 难度值（已 clip 到 [-3, 3]）

    Raises:
        ValueError: target_prob 不在合法范围 (c, 1) 内
    """
    if not (c < target_prob < 1.0):
        raise ValueError(
            f"target_prob={target_prob} 须满足 c < target_prob < 1，当前 c={c}"
        )
    if alpha <= 0:
        raise ValueError(f"alpha 须大于 0，当前 alpha={alpha}")

    # 去除猜测下限，换算为净概率
    p_net = (target_prob - c) / (1.0 - c)

    # β = θ - logit(P') / α
    beta = theta - math.log(p_net / (1.0 - p_net)) / alpha

    return round(max(-3.0, min(3.0, beta)), 4)
