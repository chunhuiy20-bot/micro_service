from IRTStrategy import IRTStrategyFactory, QuestionParam

s2 = IRTStrategyFactory.get_strategy("2pl")
s3 = IRTStrategyFactory.get_strategy("3pl")

# 场景1: 不同能力学生 vs 同一道题
question_2pl = QuestionParam(alpha=0.5, beta=0.5)
question_3pl = QuestionParam(alpha=1.5, beta=0.5, c=0.25)
print("=== 不同能力学生答同一道题 (β=0.5, α=1.5, 四选一c=0.25) ===")
print(f"  {'θ':>5}  {'2PL':>6}  {'3PL':>6}  {'差值':>6}")
for theta in [-3, -2, -1, 0, 0.5, 1, 2, 3]:
    r2 = s2.predict(theta, question_2pl)
    r3 = s3.predict(theta, question_3pl)
    bar2 = "░" * int(r2.probability * 20)
    bar3 = "█" * int(r3.probability * 20)
    print(f"  θ={theta:+.1f}  2PL={r2.probability:.4f}  3PL={r3.probability:.4f}  +{r3.probability - r2.probability:.4f}  {bar2}|{bar3}")

# 场景2: 不同猜测参数对低能力学生的影响
theta = -2.0
print(f"\n=== 低能力学生(θ={theta}) 在不同猜测参数下的概率 (α=1.0, β=0.0) ===")
for c in [0.0, 0.2, 0.25, 0.33, 0.5]:
    r = s3.predict(theta, QuestionParam(alpha=1.0, beta=0.0, c=c))
    bar = "█" * int(r.probability * 20)
    label = {0.0: "主观题", 0.2: "五选一", 0.25: "四选一", 0.33: "三选一", 0.5: "判断题"}.get(c, "")
    print(f"  c={c:.2f} ({label})  P={r.probability:.4f}  {bar}")
