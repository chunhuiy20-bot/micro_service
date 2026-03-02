"""
IRTCalibrator Demo
验证各种场景下难度 β 的校正行为，包含极端情况
"""

from IRTCalibrator import IRTCalibrator, StudentResponse, CalibrationResult


def print_result(title: str, result: CalibrationResult) -> None:
    print(result)
    direction = "→ 题目比预测更难" if result.beta_final > result.beta_init else \
                "→ 题目比预测更简单" if result.beta_final < result.beta_init else \
                "→ 初始难度准确"
    status = "收敛" if result.converged else "未收敛(达到最大迭代)"
    print(f"\n{'─' * 55}")
    print(f"【{title}】")
    print(f"  β: {result.beta_init:.4f} → {result.beta_final:.4f}  {direction}")
    print(f"  对数似然: {result.log_likelihood:.4f}")
    print(f"  迭代次数: {result.iterations}  状态: {status}")


calibrator = IRTCalibrator(learning_rate=0.01, max_iter=1000, tol=1e-6)
INIT_BETA = 1.0
ALPHA = 1

# ── 场景 1: 正常情况 ──────────────────────────────────────────
# 100 条数据，θ 均匀分布 [-3, 3]，真实 β=0.5，random.seed(42) 生成
responses_normal = [
    StudentResponse(theta=-3.00, correct=0),
    StudentResponse(theta=-2.94, correct=1),
    StudentResponse(theta=-2.88, correct=0),
    StudentResponse(theta=-2.82, correct=0),
    StudentResponse(theta=-2.76, correct=0),
    StudentResponse(theta=-2.70, correct=0),
    StudentResponse(theta=-2.64, correct=0),
    StudentResponse(theta=-2.58, correct=0),
    StudentResponse(theta=-2.52, correct=0),
    StudentResponse(theta=-2.45, correct=0),
    StudentResponse(theta=-2.39, correct=0),
    StudentResponse(theta=-2.33, correct=0),
    StudentResponse(theta=-2.27, correct=0),
    StudentResponse(theta=-2.21, correct=0),
    StudentResponse(theta=-2.15, correct=0),
    StudentResponse(theta=-2.09, correct=0),
    StudentResponse(theta=-2.03, correct=0),
    StudentResponse(theta=-1.97, correct=0),
    StudentResponse(theta=-1.91, correct=0),
    StudentResponse(theta=-1.85, correct=1),
    StudentResponse(theta=-1.79, correct=0),
    StudentResponse(theta=-1.73, correct=0),
    StudentResponse(theta=-1.67, correct=0),
    StudentResponse(theta=-1.61, correct=0),
    StudentResponse(theta=-1.55, correct=0),
    StudentResponse(theta=-1.48, correct=0),
    StudentResponse(theta=-1.42, correct=1),
    StudentResponse(theta=-1.36, correct=0),
    StudentResponse(theta=-1.30, correct=0),
    StudentResponse(theta=-1.24, correct=0),
    StudentResponse(theta=-1.18, correct=0),
    StudentResponse(theta=-1.12, correct=0),
    StudentResponse(theta=-1.06, correct=0),
    StudentResponse(theta=-1.00, correct=0),
    StudentResponse(theta=-0.94, correct=0),
    StudentResponse(theta=-0.88, correct=0),
    StudentResponse(theta=-0.82, correct=0),
    StudentResponse(theta=-0.76, correct=0),
    StudentResponse(theta=-0.70, correct=0),
    StudentResponse(theta=-0.64, correct=0),
    StudentResponse(theta=-0.58, correct=0),
    StudentResponse(theta=-0.52, correct=1),
    StudentResponse(theta=-0.45, correct=1),
    StudentResponse(theta=-0.39, correct=1),
    StudentResponse(theta=-0.33, correct=1),
    StudentResponse(theta=-0.27, correct=1),
    StudentResponse(theta=-0.21, correct=1),
    StudentResponse(theta=-0.15, correct=1),
    StudentResponse(theta=-0.09, correct=0),
    StudentResponse(theta=-0.03, correct=1),
    StudentResponse(theta= 0.03, correct=1),
    StudentResponse(theta= 0.09, correct=1),
    StudentResponse(theta= 0.15, correct=1),
    StudentResponse(theta= 0.21, correct=0),
    StudentResponse(theta= 0.27, correct=0),
    StudentResponse(theta= 0.33, correct=0),
    StudentResponse(theta= 0.39, correct=1),
    StudentResponse(theta= 0.45, correct=0),
    StudentResponse(theta= 0.52, correct=1),
    StudentResponse(theta= 0.58, correct=1),
    StudentResponse(theta= 0.64, correct=0),
    StudentResponse(theta= 0.70, correct=0),
    StudentResponse(theta= 0.76, correct=1),
    StudentResponse(theta= 0.82, correct=0),
    StudentResponse(theta= 0.88, correct=0),
    StudentResponse(theta= 0.94, correct=0),
    StudentResponse(theta= 1.00, correct=1),
    StudentResponse(theta= 1.06, correct=1),
    StudentResponse(theta= 1.12, correct=1),
    StudentResponse(theta= 1.18, correct=1),
    StudentResponse(theta= 1.24, correct=1),
    StudentResponse(theta= 1.30, correct=0),
    StudentResponse(theta= 1.36, correct=0),
    StudentResponse(theta= 1.42, correct=0),
    StudentResponse(theta= 1.48, correct=0),
    StudentResponse(theta= 1.55, correct=0),
    StudentResponse(theta= 1.61, correct=0),
    StudentResponse(theta= 1.67, correct=1),
    StudentResponse(theta= 1.73, correct=0),
    StudentResponse(theta= 1.79, correct=0),
    StudentResponse(theta= 1.85, correct=0),
    StudentResponse(theta= 1.91, correct=0),
    StudentResponse(theta= 1.97, correct=0),
    StudentResponse(theta= 2.03, correct=0),
    StudentResponse(theta= 2.09, correct=1),
    StudentResponse(theta= 2.15, correct=0),
    StudentResponse(theta= 2.21, correct=0),
    StudentResponse(theta= 2.27, correct=0),
    StudentResponse(theta= 2.33, correct=0),
    StudentResponse(theta= 2.39, correct=0),
    StudentResponse(theta= 2.45, correct=1),
    StudentResponse(theta= 2.52, correct=0),
    StudentResponse(theta= 2.58, correct=0),
    StudentResponse(theta= 2.64, correct=0),
    StudentResponse(theta= 2.70, correct=0),
    StudentResponse(theta= 2.76, correct=0),
    StudentResponse(theta= 2.82, correct=0),
    StudentResponse(theta= 2.88, correct=1),
    StudentResponse(theta= 2.94, correct=1),
    StudentResponse(theta= 3.00, correct=1),
]
result = calibrator.calibrate(responses_normal, init_beta=INIT_BETA, alpha=ALPHA)
print_result("正常情况（混合答对/错）", result)


#
# ── 场景 2: 全部答对 ──────────────────────────────────────────
# 所有学生都答对 → 题目实际比 β=1 更简单 → β 应下降
# 实际上全队和全错，都是一种假收敛
responses_all_correct = [StudentResponse(theta=t, correct=1) for t in [-1.0, 0.0, 0.5, 1.0, 1.5]]
result = calibrator.calibrate(responses_all_correct, init_beta=INIT_BETA, alpha=ALPHA)
print_result("全部答对（预期 β 下降）", result)
#
# ── 场景 3: 全部答错 ──────────────────────────────────────────
# 所有学生都答错 → 题目实际比 β=1 更难 → β 应上升
responses_all_wrong = [StudentResponse(theta=t, correct=0) for t in [-0.5, 0.0, 0.5, 1.0, 1.5]]
result = calibrator.calibrate(responses_all_wrong, init_beta=INIT_BETA, alpha=ALPHA)
print_result("全部答错（预期 β 上升）", result)
#
# ── 场景 4: 极端 - 高能力学生全部答错 ────────────────────────
# θ 远高于 β 却全错 → β 应大幅上升，但受 BETA_RANGE 上限 3.0 截断
responses_high_theta_all_wrong = [StudentResponse(theta=t, correct=0) for t in [1.5, 2.0, 2.5, 3.0]]
result = calibrator.calibrate(responses_high_theta_all_wrong, init_beta=INIT_BETA, alpha=ALPHA)
print_result("极端: 高能力学生全错（β 触碰上限 3.0）", result)

# ── 场景 5: 极端 - 低能力学生全部答对 ────────────────────────
# θ 远低于 β 却全对 → β 应大幅下降，但受 BETA_RANGE 下限 -3.0 截断
responses_low_theta_all_correct = [StudentResponse(theta=t, correct=1) for t in [-3.0, -2.5, -2.0, -1.5]]
result = calibrator.calibrate(responses_low_theta_all_correct, init_beta=INIT_BETA, alpha=ALPHA)
print_result("极端: 低能力学生全对（β 触碰下限 -3.0）", result)
#
# ── 场景 6: 极端 - 高能力全错 & 低能力全对（矛盾数据）────────
# 两组数据相互矛盾：高θ全错 → 梯度推 β 上升；低θ全对 → 梯度推 β 下降
# 两股力量在某个平衡点抵消，β 会落在中间位置，但对数似然很低（模型拟合差）
responses_contradictory = (
    [StudentResponse(theta=t, correct=0) for t in [1.5, 2.0, 2.5, 3.0]]   # 高能力全错
  + [StudentResponse(theta=t, correct=1) for t in [-3.0, -2.5, -2.0, -1.5]]  # 低能力全对
)
result = calibrator.calibrate(responses_contradictory, init_beta=INIT_BETA, alpha=ALPHA)
print_result("极端: 高能力全错 + 低能力全对（矛盾数据，β 陷入拉锯平衡）", result)

# ── 场景 6.1: 极端 - 高能力对 & 低能力全错  少量数据的无法拟合────────
responses_contradictory = (
    [StudentResponse(theta=t, correct=1) for t in [1.5, 2.0, 2.5, 3.0]]   # 高能力全错
  + [StudentResponse(theta=t, correct=0) for t in [-3.0, -2.5, -2.0, -1.5]]  # 低能力全对
)
result = calibrator.calibrate(responses_contradictory, init_beta=INIT_BETA, alpha=ALPHA)
print_result("极端: 高能力全对 + 低能力全错（矛盾数据，β 陷入拉锯平衡）", result)

import random

# 模拟 100 名学生的响应
responses_realistic = []

# 1. 生成 70 名低能力学生 (theta 在 -3 到 0 之间)
for _ in range(950):
    t = random.uniform(-3.0, 0.0)
    # 低能力学生做对概率低，这里简单模拟：如果随机数 > 0.8 才做对
    is_correct = 1 if random.random() > 0.75 else 0
    responses_realistic.append(StudentResponse(theta=t, correct=is_correct))

# 2. 生成 30 名高能力学生 (theta 在 0 到 3 之间)
for _ in range(50):
    is_correct = 1 if random.random() > 0.1 else 0
    responses_realistic.append(StudentResponse(theta=3, correct=1))

# 运行校准
result = calibrator.calibrate(responses_realistic, init_beta=INIT_BETA, alpha=ALPHA,c=0.25)
print_result("大规模真实分布：低能力者居多 (N=100)", result)

#
# # ── 场景 7: 极端 - θ 超出范围（会被 clip 到 ±3）────────────
# responses_out_of_range = [
#     StudentResponse(theta=-99.0, correct=0),   # 会被 c 到 -3.0
#     StudentResponse(theta=99.0,  correct=1),   # 会被 clip 到  3.0
#     StudentResponse(theta=0.5,   correct=1),
# ]
# result = calibrator.calibrate(responses_out_of_range, init_beta=INIT_BETA, alpha=ALPHA)
# print_result("极端: θ 超出 ±3 范围（自动 clip）", result)
#
# # ── 场景 8: 极端 - 仅 1 条数据 ───────────────────────────────
# responses_single = [StudentResponse(theta=0.0, correct=1)]
# result = calibrator.calibrate(responses_single, init_beta=INIT_BETA, alpha=ALPHA)
# print_result("极端: 仅 1 条数据（数据不足，结果仅供参考）", result)
#
# # ── 场景 9: 极端 - 空数据（预期抛出异常）────────────────────
# print(f"\n{'─' * 55}")
# print("【极端: 空数据（预期抛出 ValueError）】")
# try:
#     calibrator.calibrate([], init_beta=INIT_BETA, alpha=ALPHA)
# except ValueError as e:
#     print(f"  捕获异常: {e}")
#
# # ── 场景 10: 大量数据验证收敛性 ──────────────────────────────
# # 真实 β=0.0，用大量数据验证是否能从 β=1.0 收敛到 0.0 附近
# import math
#
# TRUE_BETA = 0.0
#
# def simulate_response(theta: float, true_beta: float, alpha: float = 1.0) -> int:
#     """根据真实参数模拟答题结果（伯努利采样）"""
#     import random
#     p = 1.0 / (1.0 + math.exp(-alpha * (theta - true_beta)))
#     return 1 if random.random() < p else 0
#
# random_responses = [
#     StudentResponse(theta=t, correct=simulate_response(t, TRUE_BETA))
#     for t in [i * 0.1 for i in range(-30, 31)]   # θ 均匀分布在 [-3, 3]
# ]
# result = calibrator.calibrate(random_responses, init_beta=INIT_BETA, alpha=ALPHA)
# print_result(f"大量数据（真实 β={TRUE_BETA}，初始 β={INIT_BETA}，样本量={len(random_responses)}）", result)
# print(f"  校正误差: {abs(result.beta_final - TRUE_BETA):.4f}")


