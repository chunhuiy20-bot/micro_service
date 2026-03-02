"""
文件名: ThetaEstimator.py
描述: 基于在线梯度上升的学生能力值 θ 估计器
     每答完一道题即更新一次 θ，适用于自适应推题场景

     更新公式: θ_new = θ_old + K · α · (u - P(θ))
     衰减因子: K = 0.8 / ln(n + e)   # n 为已答题数，e ≈ 2.718
"""

import math
from dataclasses import dataclass, field
from typing import List


@dataclass
class QuestionRecord:
    """单次答题记录"""
    alpha: float        # 题目区分度
    beta: float         # 题目难度
    correct: int        # 实际结果：1=答对, 0=答错
    c: float = 0.0      # 猜测参数


@dataclass
class UpdateResult:
    """单次更新结果"""
    theta_before: float     # 更新前 θ
    theta_after: float      # 更新后 θ
    delta: float            # 变化量
    k: float                # 本次学习速率
    p: float                # 模型预测概率
    n: int                  # 本次是第 n 题（更新后）


@dataclass
class EstimationResult:
    """完整估计结果（批量答题后汇总）"""
    theta_init: float
    theta_final: float
    n: int                          # 总答题数
    history: List[UpdateResult] = field(default_factory=list)


class ThetaEstimator:
    """
    学生能力值 θ 在线估计器

    用法：
        estimator = ThetaEstimator()           # 冷启动 θ=0
        result = estimator.update(correct, alpha, beta, c)  # 每答一题调用一次
        print(estimator.theta)                 # 当前 θ 值
    """

    THETA_RANGE = (-3.0, 3.0)
    K_MAX = 0.8

    def __init__(self, init_theta: float = 0.0):
        self.theta = float(init_theta)
        self.n = 0                  # 已答题数

    def _predict(self, theta: float, alpha: float, beta: float, c: float) -> float:
        return c + (1 - c) / (1.0 + math.exp(-alpha * (theta - beta)))

    def _k(self) -> float:
        """K = 0.8 / ln(n + e)，n 为当前已答题数（更新前）"""
        return self.K_MAX / math.log(self.n + math.e)

    def update(
        self,
        correct: int,
        alpha: float,
        beta: float,
        c: float = 0.0,
    ) -> UpdateResult:
        """
        根据一道题的答题结果更新 θ

        Args:
            correct: 答题结果，1=答对，0=答错
            alpha:   题目区分度
            beta:    题目难度
            c:       猜测参数，默认 0.0

        Returns:
            UpdateResult
        """
        theta_before = self.theta
        p = self._predict(self.theta, alpha, beta, c)
        k = self._k()

        theta_new = self.theta + k * alpha * (correct - p)
        theta_new = max(self.THETA_RANGE[0], min(self.THETA_RANGE[1], theta_new))

        self.n += 1
        self.theta = theta_new

        return UpdateResult(
            theta_before=round(theta_before, 4),
            theta_after=round(theta_new, 4),
            delta=round(theta_new - theta_before, 4),
            k=round(k, 4),
            p=round(p, 4),
            n=self.n,
        )

    def batch_update(self, records: List[QuestionRecord]) -> EstimationResult:
        """
        批量答题后统一更新（按顺序逐题更新）

        Args:
            records: 答题记录列表，顺序即作答顺序

        Returns:
            EstimationResult
        """
        if not records:
            raise ValueError("records 不能为空")

        theta_init = self.theta
        history = []

        for r in records:
            result = self.update(r.correct, r.alpha, r.beta, r.c)
            history.append(result)

        return EstimationResult(
            theta_init=theta_init,
            theta_final=self.theta,
            n=self.n,
            history=history,
        )

    def reset(self, init_theta: float = 0.0) -> None:
        """重置估计器（换新学生时调用）"""
        self.theta = float(init_theta)
        self.n = 0
