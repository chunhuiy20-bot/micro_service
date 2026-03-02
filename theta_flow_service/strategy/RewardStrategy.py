"""
文件名: RewardStrategy.py
描述: 基于难度的答题奖励机制
     Reward = Base_Value × (1 - P(θ)) × correct
     答对难题 → 高奖励
     答对易题 → 低奖励
     答错任意题 → 0（无惩罚）
"""

from dataclasses import dataclass


@dataclass
class RewardResult:
    reward: float           # 本题奖励（≥ 0）
    total: float            # 累计总奖励
    base_value: float       # 基础分值
    p: float                # 预测答对概率
    correct: int            # 实际结果


class RewardStrategy:
    """
    难度加权奖励策略

    公式: Reward = Base_Value × (1 - P(θ)) × correct

    示例:
        难题答对 P=0.2 → +80 分   （难度高，重奖）
        易题答对 P=0.8 → +20 分   （难度低，小奖）
        任意题答错     →   0 分   （无惩罚）
    """

    def __init__(self, base_value: float = 100):
        self.base_value = base_value
        self.total = 0.0

    def calc(self, correct: int, p: float) -> RewardResult:
        """
        计算本题奖励并累加

        Args:
            correct: 答题结果，1=答对，0=答错
            p:       模型预测答对概率 P(θ)

        Returns:
            RewardResult
        """
        reward = round(self.base_value * (1 - p) * correct, 2)
        self.total = round(self.total + reward, 2)

        return RewardResult(
            reward=reward,
            total=self.total,
            base_value=self.base_value,
            p=round(p, 4),
            correct=correct,
        )

    def reset(self) -> None:
        self.total = 0.0
