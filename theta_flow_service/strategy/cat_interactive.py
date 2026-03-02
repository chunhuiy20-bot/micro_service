"""
自适应答题模拟器（交互式）
根据你的实时作答动态调整题目难度并更新能力估计值 θ
"""

import math

from ThetaEstimator import ThetaEstimator
from IRTStrategy import solve_beta
from RewardStrategy import RewardStrategy

TOTAL = 20
TARGET_PROB = 0.6
ALPHA = 1.0
C = 0.0
THETA_MIN, THETA_MAX = -3.0, 3.0

def theta_bar(theta: float, width: int = 30) -> str:
    """将 θ 映射到 [-3,3] 的进度条，中点为 θ=0"""
    pos = int((theta + 3.0) / 6.0 * width)
    pos = max(0, min(width - 1, pos))
    bar = ["-"] * width
    bar[width // 2] = "│"
    bar[pos] = "●"
    return "".join(bar)

def k_bar(k: float, k_max: float = 0.8, width: int = 20) -> str:
    """K 值衰减进度条"""
    filled = int(k / k_max * width)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)

def difficulty_label(beta: float) -> str:
    if beta < -2.0: return "极易"
    if beta < -1.0: return "简单"
    if beta <  0.0: return "偏易"
    if beta <  1.0: return "适中"
    if beta <  2.0: return "偏难"
    return "极难"


print("=" * 55)
print("       自适应答题模拟器  （共 20 题）")
print("  系统根据你的答题情况动态调整题目难度")
print("  输入  1 = 答对    0 = 答错    q = 退出")
print("=" * 55)

est = ThetaEstimator(init_theta=0.0)
reward_engine = RewardStrategy(base_value=100)
history = []

for round_num in range(1, TOTAL + 1):

    # 根据当前 θ 推题
    theta_now = est.theta
    try:
        beta = solve_beta(theta_now, target_prob=TARGET_PROB, alpha=ALPHA, c=C)
    except ValueError:
        beta = max(THETA_MIN, min(THETA_MAX, theta_now))

    print(f"\n{'─' * 55}")
    print(f"  第 {round_num:02d} / {TOTAL} 题")
    k_now = 0.8 / math.log(est.n + math.e)
    print(f"  当前能力  θ = {theta_now:+.4f}   {theta_bar(theta_now)}")
    print(f"  学习速率  K = {k_now:.4f}      {k_bar(k_now)}  (第 {est.n} 题后)")
    print(f"  推送难度  β = {beta:+.4f}   [{difficulty_label(beta)}]  (预计答对率 60%)")

    # 接收输入
    while True:
        raw = input("  你的答案 (1=对 / 0=错 / q=退出): ").strip()
        if raw == "q":
            print("\n  已退出。")
            exit()
        if raw in ("0", "1"):
            correct = int(raw)
            break
        print("  请输入 0 或 1")

    # 更新 θ 与奖励
    result = est.update(correct=correct, alpha=ALPHA, beta=beta, c=C)
    reward = reward_engine.calc(correct=correct, p=TARGET_PROB)

    # 展示本题反馈
    result_str = "✓ 答对" if correct else "✗ 答错"
    delta_str  = f"{result.delta:+.4f}"
    reward_str = f"{reward.reward:+.1f}"
    print(f"\n  {result_str}   K = {result.k:.4f}   θ: {result.theta_before:+.4f} → {result.theta_after:+.4f}  (Δ{delta_str})")
    print(f"  本题奖励  {reward_str:>7} 分   累计得分  {reward.total:>8.1f} 分")
    print(f"  更新后     θ = {est.theta:+.4f}   {theta_bar(est.theta)}")

    history.append({
        "n": round_num, "beta": beta, "correct": correct, "k": result.k,
        "theta_before": result.theta_before, "theta_after": result.theta_after,
        "reward": reward.reward, "total": reward.total,
    })

# 最终汇总
print(f"\n{'=' * 55}")
print("  答题结束，能力评估汇总")
print(f"{'=' * 55}")
print(f"  {'轮次':>3}  {'题目难度β':>9}  {'K':>6}  {'结果':>4}  {'奖励':>7}  {'累计':>8}  {'θ变化':>15}")
for h in history:
    result_str = "✓" if h["correct"] else "✗"
    print(f"  {h['n']:>3}  {h['beta']:>+9.4f}  {h['k']:>6.4f}  {result_str:>4}  "
          f"{h['reward']:>+7.1f}  {h['total']:>8.1f}  "
          f"{h['theta_before']:+.4f} → {h['theta_after']:+.4f}")

correct_count = sum(h["correct"] for h in history)
print(f"\n  答对 {correct_count} / {TOTAL} 题   正确率 {correct_count/TOTAL*100:.0f}%")
print(f"  初始 θ = +0.0000   最终 θ = {est.theta:+.4f}")
print(f"  最终得分：{reward_engine.total:+.1f} 分   {'盈利' if reward_engine.total >= 0 else '亏损'}")
print(f"  能力变化：{theta_bar(est.theta)}")
print(f"  最终能力等级：{difficulty_label(est.theta).replace('极易','较弱').replace('简单','偏弱').replace('偏易','中下').replace('适中','中等').replace('偏难','中上').replace('极难','较强')}")
