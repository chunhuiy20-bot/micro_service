"""
solve_beta Demo
已知学生能力 θ，反推目标答对概率对应的题目难度 β
"""

from IRTStrategy import solve_beta, IRTStrategyFactory, QuestionParam

strategy = IRTStrategyFactory.get_strategy("2pl")
s3 = IRTStrategyFactory.get_strategy("3pl")

SEP = "─" * 60


def verify(theta, beta, alpha=1.0, c=0.0) -> float:
    """反向验证：用预测模型算出 P，确认与目标一致"""
    r = strategy.predict(theta, QuestionParam(alpha=alpha, beta=beta, c=c)) if c == 0 \
        else s3.predict(theta, QuestionParam(alpha=alpha, beta=beta, c=c))
    return r.probability


# ── 场景 1: 不同 θ，固定目标 P=0.60 ─────────────────────────
print(SEP)
print("【场景 1】不同能力学生，推送答对率 60% 的题目（α=1，c=0）")
print(f"  {'θ':>5}  {'β':>8}  {'验证P':>6}  {'β-θ偏移':>8}")
for theta in [-2.0, -1.0, 0.0, 0.5, 1.0, 1.5, 2.0]:
    beta = solve_beta(theta, target_prob=0.6)
    p = verify(theta, beta)
    print(f"  {theta:>+5.1f}  {beta:>8.4f}  {p:>6.4f}  {beta - theta:>+8.4f}")

# ── 场景 2: 不同目标概率，同一个学生 θ=1.0 ──────────────────
print(f"\n{SEP}")
print("【场景 2】同一学生 θ=1.0，不同目标答对概率对应的题目难度（α=1，c=0）")
print(f"  {'目标P':>6}  {'β':>8}  {'验证P':>6}  含义")
labels = {0.9: "非常简单", 0.7: "偏简单", 0.6: "适中", 0.5: "恰好匹配", 0.4: "偏难", 0.3: "非常难"}
for p_target in [0.9, 0.7, 0.6, 0.5, 0.4, 0.3]:
    beta = solve_beta(theta=1.0, target_prob=p_target)
    p = verify(1.0, beta)
    print(f"  {p_target:>6.1f}  {beta:>8.4f}  {p:>6.4f}  {labels[p_target]}")

# ── 场景 3: 选择题 vs 填空题，相同 θ 和目标 P ────────────────
print(f"\n{SEP}")
print("【场景 3】选择题(c=0.25) vs 填空题(c=0)，θ=1.0，目标 P=0.60")
print(f"  {'题型':>4}  {'c':>5}  {'β':>8}  {'验证P':>6}  说明")
for c, label in [(0.0, "填空题"), (0.25, "四选一"), (0.33, "三选一"), (0.5, "判断题")]:
    beta = solve_beta(theta=1.0, target_prob=0.6, c=c)
    p = verify(1.0, beta, c=c)
    note = "无猜测底线，β 更低" if c == 0 else f"猜测底线 {c}，β 需更高才能维持净 60%"
    print(f"  {label:>4}  {c:>5.2f}  {beta:>8.4f}  {p:>6.4f}  {note}")

# ── 场景 4: 区分度 α 的影响 ──────────────────────────────────
print(f"\n{SEP}")
print("【场景 4】不同区分度 α，θ=1.0，目标 P=0.60，c=0")
print(f"  {'α':>5}  {'β':>8}  {'验证P':>6}  说明")
for alpha in [0.5, 1.0, 1.5, 2.0]:
    beta = solve_beta(theta=1.0, target_prob=0.6, alpha=alpha)
    p = verify(1.0, beta, alpha=alpha)
    note = "区分度低，β 偏移量大" if alpha < 1 else ("区分度高，β 偏移量小" if alpha > 1 else "标准")
    print(f"  {alpha:>5.1f}  {beta:>8.4f}  {p:>6.4f}  {note}")

# ── 场景 5: 推题场景模拟 ──────────────────────────────────────
# 给不同能力学生，推送三档难度：热身(P=0.8)，适中(P=0.6)，挑战(P=0.4)
print(f"\n{SEP}")
print("【场景 5】推题场景：按三档难度为不同能力学生匹配题目（α=1，c=0）")
print(f"  {'θ':>5}  {'热身β(P=0.8)':>12}  {'适中β(P=0.6)':>12}  {'挑战β(P=0.4)':>12}")
for theta in [-1.0, 0.0, 0.5, 1.0, 1.5]:
    b_easy   = solve_beta(theta, target_prob=0.8)
    b_medium = solve_beta(theta, target_prob=0.6)
    b_hard   = solve_beta(theta, target_prob=0.4)
    print(f"  {theta:>+5.1f}  {b_easy:>12.4f}  {b_medium:>12.4f}  {b_hard:>12.4f}")

# ── 场景 6: 异常情况 ─────────────────────────────────────────
print(f"\n{SEP}")
print("【场景 6】异常情况")

cases = [
    dict(theta=0.0, target_prob=0.25, c=0.25, desc="target_prob == c（等于猜测下限）"),
    dict(theta=0.0, target_prob=0.10, c=0.25, desc="target_prob < c（低于猜测下限，不可能）"),
    dict(theta=0.0, target_prob=1.00, c=0.00, desc="target_prob == 1（需要 β→-∞）"),
    dict(theta=0.0, target_prob=0.60, alpha=-1.0, c=0.00, desc="alpha <= 0（无效区分度）"),
]
for case in cases:
    desc = case.pop("desc")
    try:
        beta = solve_beta(**case)
        print(f"  β={beta}  ← {desc}")
    except ValueError as e:
        print(f"  ValueError: {e}")
        print(f"    ↑ {desc}")

# ── 场景 7: θ 动态变化，固定目标 P=0.60 ─────────────────────
# 模拟学生能力从 -3 成长到 3，追踪对应推送题目难度的变化
print(f"\n{SEP}")
print("【场景 7】θ 动态变化，目标答对概率固定 P=0.60（α=1，c=0）")
print(f"  {'θ':>5}  {'β':>8}  图示（β 随 θ 线性平移）")

thetas = [round(-3.0 + i * 0.5, 1) for i in range(13)]  # -3.0 到 3.0，步长 0.5
for theta in thetas:
    beta = solve_beta(theta, target_prob=0.6)
    # 将 beta 映射到 [-3,3] 区间做可视化，偏移 3 后 /6 得到 [0,1]
    bar_pos = int((beta + 3.0) / 6.0 * 40)
    bar_pos = max(0, min(39, bar_pos))
    axis = [" "] * 40
    axis[20] = "│"           # β=0 的参考线
    axis[bar_pos] = "●"
    print(f"  {theta:>+5.1f}  {beta:>8.4f}  {''.join(axis)}  β={beta:+.2f}")
