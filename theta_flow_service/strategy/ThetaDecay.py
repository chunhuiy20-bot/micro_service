import math
from dataclasses import dataclass

# 常量定义
GAMMA_MIN = 0.01
GAMMA_MAX = 0.05
THETA_RANGE = (-3.0, 3.0)  # 能力值范围 [最小值, 最大值]


@dataclass
class DecayResult:
    """单次衰退结果"""
    theta_before: float  # 衰退前 θ
    theta_after: float  # 衰退后 θ
    delta: float  # 变化量 (始终 ≤ 0)
    gamma: float  # 本次衰退速率
    delta_t: float  # 经过天数


class ThetaDecay:
    """
    方案 C: 平移缩放衰退器

    逻辑:
        将 θ 映射到全正数区间 [0, Range_Max - Range_Min] 后进行指数衰退。
        这保证了无论初始 θ 是正还是负，衰退后数值一定会减小（即能力下降）。

    公式:
        θ_shifted = θ - MIN_BOUND
        θ_shifted_decayed = θ_shifted * e^(-γ · Δt)
        θ_new = θ_shifted_decayed + MIN_BOUND
    """

    def __init__(self, gamma: float = 0.03):
        if not (GAMMA_MIN <= gamma <= GAMMA_MAX):
            raise ValueError(f"gamma={gamma} 须在 [{GAMMA_MIN}, {GAMMA_MAX}] 范围内")
        self.gamma = gamma

    def apply(self, theta: float, delta_t: float) -> DecayResult:
        if delta_t < 0:
            raise ValueError(f"delta_t={delta_t} 不能为负数")

        # 1. 初始值裁剪，确保在 [-3, 3] 内
        theta_before = max(THETA_RANGE[0], min(THETA_RANGE[1], theta))

        # 2. 坐标平移：让最小值 -3.0 对应 0
        # offset = -3.0
        offset = THETA_RANGE[0]
        normalized_theta = theta_before - offset  # 范围变为 [0, 6.0]

        # 3. 执行指数衰退
        # 在全正数区间乘法，数值只会向 0（即原区间的 -3.0）靠近
        decay_factor = math.exp(-self.gamma * delta_t)
        decayed_normalized = normalized_theta * decay_factor

        # 4. 还原坐标系
        theta_new = decayed_normalized + offset

        # 5. 再次裁剪（防止浮点计算极小误差）
        theta_new = max(THETA_RANGE[0], min(THETA_RANGE[1], theta_new))

        return DecayResult(
            theta_before=round(theta_before, 4),
            theta_after=round(theta_new, 4),
            delta=round(theta_new - theta_before, 4),
            gamma=self.gamma,
            delta_t=delta_t,
        )


# --- 测试验证 ---
if __name__ == "__main__":
    decay = ThetaDecay(gamma=0.03)

    # 测试 1: 强学生 (2.0)
    res1 = decay.apply(theta=2.0, delta_t=30)
    print(f"强学生: {res1.theta_before} -> {res1.theta_after} (掉分: {res1.delta})")
    # 逻辑: (2 - (-3)) * e^-0.9 - 3 = 5 * 0.406 - 3 = 2.03 - 3 = -0.97

    # 测试 2: 弱学生 (-1.5)
    res2 = decay.apply(theta=-1.5, delta_t=30)
    print(f"弱学生: {res2.theta_before} -> {res2.theta_after} (掉分: {res2.delta})")
    # 逻辑: (-1.5 - (-3)) * e^-0.9 - 3 = 1.5 * 0.406 - 3 = 0.61 - 3 = -2.39

    # 测试 3: 极弱学生 (-2.9)
    res3 = decay.apply(theta=-2.9, delta_t=30)
    print(f"底线学生: {res3.theta_before} -> {res3.theta_after} (掉分: {res3.delta})")