"""
ThetaEstimator Demo
验证各场景下 θ 的动态更新行为，包含极端情况
"""

import math
from ThetaEstimator import ThetaEstimator, QuestionRecord


def print_header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"【{title}】")
    print(f"  {'第N题':>4}  {'题难度β':>6}  {'预测P':>6}  {'结果':>4}  {'K':>6}  {'θ变化':>8}  {'θ当前':>7}")


def print_update(r, correct: int, beta: float) -> None:
    result_str = "✓答对" if correct == 1 else "✗答错"
    delta_str = f"{r.delta:+.4f}"
    print(f"  {r.n:>4}  {beta:>6.2f}  {r.p:>6.4f}  {result_str:>4}  {r.k:>6.4f}  {delta_str:>8}  {r.theta_after:>7.4f}")


# ── 场景 1: 全部答对，题目从易到难 ────────────────────────────
# 预期: θ 持续上升，K 逐渐衰减
print_header("全部答对，题目从易到难（θ 应持续上升）")
est = ThetaEstimator(init_theta=0.0)
for beta in [-2.0, -1.0, 0.0, 0.5, 1.0, 1.5, 2.0]:
    r = est.update(correct=1, alpha=1.0, beta=beta)
    print_update(r, correct=1, beta=beta)

# ── 场景 2: 全部答错，题目从难到易 ────────────────────────────
# 预期: θ 持续下降，K 逐渐衰减
print_header("全部答错，题目从难到易（θ 应持续下降）")
est = ThetaEstimator(init_theta=0.0)
for beta in [2.0, 1.5, 1.0, 0.5, 0.0, -1.0, -2.0]:
    r = est.update(correct=0, alpha=1.0, beta=beta)
    print_update(r, correct=0, beta=beta)

# ── 场景 3: 混合答题，真实能力 θ≈1.0 ─────────────────────────
# 题目难度围绕 β=1.0，答题结果按 IRT 概率随机生成（seed=42）
print_header("混合答题（真实 θ≈1.0，预期最终收敛到 1.0 附近）")
import random
random.seed(42)
est = ThetaEstimator(init_theta=0.0)
TRUE_THETA = 1.0
betas = [-1.0, 0.0, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 0.3, 1.8]
for beta in betas:
    p_true = 1.0 / (1.0 + math.exp(-1.0 * (TRUE_THETA - beta)))
    correct = 1 if random.random() < p_true else 0
    r = est.update(correct=correct, alpha=1.0, beta=beta)
    print_update(r, correct=correct, beta=beta)
print(f"\n  真实 θ={TRUE_THETA}，估计 θ={est.theta:.4f}，误差={abs(est.theta - TRUE_THETA):.4f}")

# ── 场景 4: α 区分度的影响 ────────────────────────────────────
# 同样答错，高区分度题目对 θ 的拉力更大
print_header("α 区分度的影响（同样答错，β=1.0）")
for alpha in [0.5, 1.0, 1.5, 2.0]:
    est = ThetaEstimator(init_theta=0.0)
    r = est.update(correct=0, alpha=alpha, beta=1.0)
    print(f"  α={alpha:.1f}  K={r.k:.4f}  δθ={r.delta:+.4f}  θ→{r.theta_after:.4f}")

# ── 场景 5: 极端 - 连续答对触碰上限 ──────────────────────────
print_header("极端: 连续答对高难度题（θ 触碰上限 3.0）")
est = ThetaEstimator(init_theta=0.0)
for i in range(10):
    r = est.update(correct=1, alpha=1.0, beta=2.5)
    print_update(r, correct=1, beta=2.5)
    if est.theta >= 3.0:
        print(f"  → θ 已到达上限 3.0，后续更新无效")
        break

# ── 场景 6: 极端 - 连续答错触碰下限 ──────────────────────────
print_header("极端: 连续答错简单题（θ 触碰下限 -3.0）")
est = ThetaEstimator(init_theta=0.0)
for i in range(10):
    r = est.update(correct=0, alpha=1.0, beta=-2.5)
    print_update(r, correct=0, beta=-2.5)
    if est.theta <= -3.0:
        print(f"  → θ 已到达下限 -3.0，后续更新无效")
        break

# ── 场景 7: K 衰减曲线 ────────────────────────────────────────
print(f"\n{'─' * 60}")
print("【K 衰减曲线（随答题数增加，学习速率递减）】")
print(f"  {'n':>5}  {'K':>8}")
est = ThetaEstimator()
for n in [0, 1, 2, 5, 10, 20, 50, 100]:
    est.n = n
    k = est._k()
    bar = "█" * int(k * 30)
    print(f"  {n:>5}  {k:>8.4f}  {bar}")

# ── 场景 8: batch_update 接口 ─────────────────────────────────
print(f"\n{'─' * 60}")
print("【batch_update 接口示例】")
est = ThetaEstimator(init_theta=0.0)
records = [
    QuestionRecord(alpha=1.0, beta=-1.0, correct=1),
    QuestionRecord(alpha=1.0, beta= 0.0, correct=1),
    QuestionRecord(alpha=1.0, beta= 0.5, correct=0),
    QuestionRecord(alpha=1.5, beta= 1.0, correct=1),
    QuestionRecord(alpha=1.0, beta= 1.5, correct=0),
]
result = est.batch_update(records)
print(f"  θ: {result.theta_init} → {result.theta_final:.4f}  (共 {result.n} 题)")

# ── 场景 9: 分区间正确率模拟（含题型）──────────────────────────
# 每区间 3 道选择题(c=0.25) + 2 道填空题(c=0)
# β∈[-3, 0)：全对   β∈[0,1)：60%   β∈[1,2)：40%   β∈[2,3]：全错
print(f"\n{'─' * 65}")
print("【分区间正确率模拟（每区间 3 选择题 + 2 填空题，共 20 题）】")
print(f"  {'第N题':>4}  {'题型':>4}  {'题难度β':>6}  {'猜测c':>5}  {'预测P':>6}  {'结果':>4}  {'K':>6}  {'θ变化':>8}  {'θ当前':>7}")

zone_questions = [
    # (beta, correct,  c)       选择题 c=0.25，填空题 c=0
    # β ∈ [-3, 0)  全对
    (-2.50, 1, 0.25), (-2.00, 1, 0.25), (-1.50, 1, 0.25),
    (-1.00, 1, 0.00), (-0.50, 1, 0.00),
    # β ∈ [0, 1)   60% 正确（3对2错）
    ( 0.10, 1, 0.25), ( 0.30, 1, 0.25), ( 0.50, 1, 0.25),
    ( 0.70, 1, 0.00), ( 0.90, 1, 0.00),
    # β ∈ [1, 2)   40% 正确（2对3错）
    ( 1.10, 1, 0.25), ( 1.30, 1, 0.25), ( 1.50, 0, 0.25),
    ( 1.70, 1, 0.00), ( 1.90, 0, 0.00),
    # β ∈ [2, 3]   全错
    ( 2.10, 1, 0.25), ( 2.30, 1, 0.25), ( 2.50, 1, 0.25),
    ( 2.70, 0, 0.00), ( 2.90, 0, 0.00),
]

est = ThetaEstimator(init_theta=0.0)
zone_labels = {0: "β∈[-3, 0)", 5: "β∈[ 0, 1)", 10: "β∈[ 1, 2)", 15: "β∈[ 2, 3]"}

for i, (beta, correct, c) in enumerate(zone_questions):
    if i in zone_labels:
        print(f"  {'·' * 63}")
        print(f"  {zone_labels[i]}")
    r = est.update(correct=correct, alpha=1.0, beta=beta, c=c)
    type_str = "选择" if c > 0 else "填空"
    result_str = "✓答对" if correct == 1 else "✗答错"
    print(f"  {r.n:>4}  {type_str:>4}  {beta:>6.2f}  {c:>5.2f}  {r.p:>6.4f}  {result_str}  {r.k:>6.4f}  {r.delta:>+8.4f}  {r.theta_after:>7.4f}")

print(f"\n  最终 θ 估计值: {est.theta:.4f}")
