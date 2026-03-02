"""
自适应测试 Demo（CAT: Computerized Adaptive Testing）
结合 ThetaEstimator + solve_beta，实现：
  1. 根据学生当前估计能力 θ，推送答对概率 60% 的题目
  2. 根据答题结果动态更新 θ 估计值
  3. θ 估计值不断收敛至学生真实能力
"""

import math
import random
from ThetaEstimator import ThetaEstimator
from IRTStrategy import solve_beta, IRTStrategyFactory, QuestionParam

SEP = "─" * 70


def simulate_response(true_theta: float, beta: float, alpha: float = 1.0, c: float = 0.0) -> int:
    """根据学生真实能力和题目参数，模拟答题结果"""
    p = c + (1 - c) / (1.0 + math.exp(-alpha * (true_theta - beta)))
    return 1 if random.random() < p else 0


def run_cat(true_theta: float, rounds: int = 20, alpha: float = 1.0, c: float = 0.0,
            target_prob: float = 0.6, seed: int = 42) -> list:
    """
    运行一次自适应测试

    Returns:
        每轮记录的列表，每条包含 theta_est, beta, correct, p_true, error
    """
    random.seed(seed)
    est = ThetaEstimator(init_theta=0.0)
    history = []

    for _ in range(rounds):
        theta_est = est.theta

        # 推送题目：根据当前估计 θ 计算目标难度
        try:
            beta = solve_beta(theta_est, target_prob=target_prob, alpha=alpha, c=c)
        except ValueError:
            beta = max(-3.0, min(3.0, theta_est))

        # 模拟学生作答（基于真实 θ）
        correct = simulate_response(true_theta, beta, alpha, c)

        # 真实答对概率（仅用于展示，实际系统不可见）
        p_true = c + (1 - c) / (1.0 + math.exp(-alpha * (true_theta - beta)))

        # 更新 θ 估计
        est.update(correct=correct, alpha=alpha, beta=beta, c=c)

        history.append({
            "n":          est.n,
            "theta_est":  round(theta_est, 4),       # 推题前的估计值
            "beta":       beta,
            "p_true":     round(p_true, 4),          # 真实答对概率
            "correct":    correct,
            "theta_new":  round(est.theta, 4),       # 更新后的估计值
            "error":      round(abs(est.theta - true_theta), 4),
        })

    return history


def print_history(history: list, true_theta: float) -> None:
    print(f"  {'轮次':>3}  {'推题β':>7}  {'真实P':>6}  {'结果':>4}  "
          f"{'θ(更新前)':>9}  {'θ(更新后)':>9}  {'误差':>6}  收敛图")
    for h in history:
        result_str = "✓" if h["correct"] else "✗"
        # 误差柱状图：误差越小，柱越短
        bar_len = int(h["error"] / 6.0 * 30)
        bar = "█" * bar_len
        print(f"  {h['n']:>3}  {h['beta']:>7.4f}  {h['p_true']:>6.4f}  {result_str:>4}  "
              f"{h['theta_est']:>9.4f}  {h['theta_new']:>9.4f}  {h['error']:>6.4f}  {bar}")
    final_error = history[-1]["error"]
    print(f"\n  真实 θ={true_theta:+.2f}  最终估计 θ={history[-1]['theta_new']:+.4f}  "
          f"最终误差={final_error:.4f}")


# ══════════════════════════════════════════════════════════════════════
# 场景 1: 高能力学生（真实 θ=1.5）
# ══════════════════════════════════════════════════════════════════════
TRUE_THETA = 1.5
print(SEP)
print(f"【场景 1】高能力学生  真实 θ={TRUE_THETA}，冷启动 θ=0，共 20 轮")
history = run_cat(true_theta=TRUE_THETA, rounds=20, seed=42)
print_history(history, TRUE_THETA)

# ══════════════════════════════════════════════════════════════════════
# 场景 2: 低能力学生（真实 θ=-1.5）
# ══════════════════════════════════════════════════════════════════════
TRUE_THETA = -1.5
print(f"\n{SEP}")
print(f"【场景 2】低能力学生  真实 θ={TRUE_THETA}，冷启动 θ=0，共 20 轮")
history = run_cat(true_theta=TRUE_THETA, rounds=20, seed=42)
print_history(history, TRUE_THETA)

# ══════════════════════════════════════════════════════════════════════
# 场景 3: 中等能力学生（真实 θ=0，与冷启动相同）
# ══════════════════════════════════════════════════════════════════════
TRUE_THETA = 0.0
print(f"\n{SEP}")
print(f"【场景 3】中等能力学生  真实 θ={TRUE_THETA}，冷启动 θ=0，共 20 轮")
history = run_cat(true_theta=TRUE_THETA, rounds=20, seed=42)
print_history(history, TRUE_THETA)

# ══════════════════════════════════════════════════════════════════════
# 场景 4: 选择题（c=0.25），高能力学生
# ══════════════════════════════════════════════════════════════════════
TRUE_THETA = 1.5
print(f"\n{SEP}")
print(f"【场景 4】选择题 c=0.25  真实 θ={TRUE_THETA}，冷启动 θ=0，共 20 轮")
history = run_cat(true_theta=TRUE_THETA, rounds=20, c=0.25, seed=42)
print_history(history, TRUE_THETA)

# ══════════════════════════════════════════════════════════════════════
# 场景 5: 多轮收敛对比（不同真实 θ，统一观察误差收敛速度）
# ══════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("【场景 5】误差收敛对比（不同真实 θ，每 5 轮取样误差）")
print(f"  {'真实θ':>6}  {'第5轮':>8}  {'第10轮':>8}  {'第15轮':>8}  {'第20轮':>8}")

for true_theta in [-2.0, -1.0, 0.0, 1.0, 2.0]:
    h = run_cat(true_theta=true_theta, rounds=20, seed=99)
    errors = [h[i]["error"] for i in [4, 9, 14, 19]]
    print(f"  {true_theta:>+6.1f}  {errors[0]:>8.4f}  {errors[1]:>8.4f}  "
          f"{errors[2]:>8.4f}  {errors[3]:>8.4f}")
