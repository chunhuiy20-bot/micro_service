"""
文件名: IRTCalibrator.py
描述: 基于MLE(最大似然估计)的IRT题目难度校正器
     固定 α 和 c，通过梯度下降迭代更新 β(难度)
     更新公式: β_new = β_old + lr · α · Σ(Pᵢ - uᵢ)  # 梯度上升，最大化对数似然
"""

import math
from dataclasses import dataclass
from typing import List


@dataclass
class StudentResponse:
    """单条学生答题记录"""
    theta: float    # 学生能力值
    correct: int    # 1=答对, 0=答错


@dataclass
class CalibrationResult:
    """校正结果"""
    beta_init: float        # 初始难度
    beta_final: float       # 校正后难度
    iterations: int         # 实际迭代次数
    converged: bool         # 是否收敛
    log_likelihood: float   # 最终对数似然值


class IRTCalibrator:
    """
    IRT 题目难度校正器（只更新 β）

    固定参数:
        alpha: 区分度（不变）
        c:     猜测参数（不变）

    梯度推导:
        P(θ) = c + (1-c) / (1 + e^(-α(θ-β)))
        ∂L/∂β = α · Σᵢ(Pᵢ - uᵢ)
        β_new = β - lr · ∂L/∂β
    """

    BETA_RANGE = (-3.0, 3.0)
    THETA_RANGE = (-3.0, 3.0)

    def __init__(
        self,
        learning_rate: float = 0.01,
        max_iter: int = 1000,
        tol: float = 1e-6,
    ):
        self.lr = learning_rate
        self.max_iter = max_iter
        self.tol = tol

    def _predict(self, theta: float, beta: float, alpha: float, c: float) -> float:
        theta = max(self.THETA_RANGE[0], min(self.THETA_RANGE[1], theta))
        return c + (1 - c) / (1.0 + math.exp(-alpha * (theta - beta)))

    def _log_likelihood(
        self, responses: List[StudentResponse], beta: float, alpha: float, c: float
    ) -> float:
        ll = 0.0
        for r in responses:
            p = self._predict(r.theta, beta, alpha, c)
            p = max(1e-9, min(1 - 1e-9, p))   # 防止 log(0)
            ll += r.correct * math.log(p) + (1 - r.correct) * math.log(1 - p)
        return ll

    def calibrate(
        self,
        responses: List[StudentResponse],
        init_beta: float = 1.0,
        alpha: float = 1.0,
        c: float = 0.0,
    ) -> CalibrationResult:
        """
        执行难度校正

        Args:
            responses:  学生答题记录列表
            init_beta:  题目初始难度
            alpha:      题目区分度（固定不变）
            c:          猜测参数（固定不变）

        Returns:
            CalibrationResult
        """
        if not responses:
            raise ValueError("responses 不能为空")

        beta = float(init_beta)
        converged = False
        i = 0

        for i in range(self.max_iter):
            # 计算梯度: ∂L/∂β = α · Σ(Pᵢ - uᵢ)
            grad = alpha * sum(
                self._predict(r.theta, beta, alpha, c) - r.correct
                for r in responses
            )

            beta_new = beta + self.lr * grad   # 梯度上升：最大化对数似然
            beta_new = max(self.BETA_RANGE[0], min(self.BETA_RANGE[1], beta_new))

            if abs(beta_new - beta) < self.tol:
                beta = beta_new
                converged = True
                break

            beta = beta_new

        return CalibrationResult(
            beta_init=init_beta,
            beta_final=round(beta, 4),
            iterations=i + 1,
            converged=converged,
            log_likelihood=round(self._log_likelihood(responses, beta, alpha, c), 4),
        )
