"""
毎日のパターン分析: 
- ブロック1,2: 参加しない (ΔSOC = 0)
- ブロック3-7: 1次調整力参加 (5ブロック)
- ブロック8: JEPX参加 (+85%)
"""

print("="*80)
print("実際の運用パターン: ブロック1,2不参加 + 5ブロック参加 + JEPX")
print("="*80)

# 係数
coef = 0.040635
intercept = 8.4591

print("\n【1. 運用パターン】")
print("-"*80)
print("ブロック1 (0-3h):   参加しない → ΔSOC = 0")
print("ブロック2 (3-6h):   参加しない → ΔSOC = 0")
print("ブロック3 (6-9h):   1次調整力参加 → ΔSOC = 0.040635 × b - 8.4591")
print("ブロック4 (9-12h):  1次調整力参加 → ΔSOC = 0.040635 × b - 8.4591")
print("ブロック5 (12-15h): 1次調整力参加 → ΔSOC = 0.040635 × b - 8.4591")
print("ブロック6 (15-18h): 1次調整力参加 → ΔSOC = 0.040635 × b - 8.4591")
print("ブロック7 (18-21h): 1次調整力参加 → ΔSOC = 0.040635 × b - 8.4591")
print("ブロック8 (21-24h): JEPX参加 → ΔSOC = +85%")

print("\n【2. サイクル制約】")
print("-"*80)
print("24時間でSOCが元に戻る条件:")
print("  Σ(ΔSOC) = 0")
print("  ブロック1,2 + ブロック3-7 + JEPX = 0")
print("  0 + 5 × (0.040635 × b - 8.4591) + 85 = 0")

print("\n【3. 基準値の計算】")
print("-"*80)
print("サイクル制約から:")
print("  5 × (0.040635 × b - 8.4591) + 85 = 0")
print("  5 × (0.040635 × b - 8.4591) = -85")
print("  0.040635 × b - 8.4591 = -17")
print("")
print("これは b ≥ 0 では実現不可能！")
print("(前の分析で示したように b = -210 kW となる)")

print("\n【4. ユーザーの式の検証】")
print("-"*80)
print("提案された式:")
print("  0.040635 × 5b = 144.2137")
print("  0.203175 × b = 144.2137")
print("  b = 144.2137 / 0.203175")

b_user = 144.2137 / 0.203175
print(f"  b = {b_user:.2f} kW")

print("\n【5. この式の意味】")
print("-"*80)
print("144.2137 の由来:")
print("  144.2137 = 85 + 5 × 8.4591")
print("  144.2137 = 85 + 42.2955")
print("  144.2137 = 127.2955  ❌ (計算が合わない)")
print("")
print("正しい計算:")
calc1 = 85 + 5 * 8.4591
print(f"  85 + 5 × 8.4591 = {calc1}")
print("")
print("または:")
calc2 = 85 + 7 * 8.4591
print(f"  85 + 7 × 8.4591 = {calc2}")

print("\n【6. 正しい最適化問題】")
print("-"*80)
print("実は、サイクル制約を満たしつつ容量を最大化するには:")
print("")
print("オプション1: JEPXのΔSOCを調整")
print("  5ブロックで相殺可能な最大ΔSOC:")
print("  5 × (0.040635 × b - 8.4591) の最小値")
print("  b = 0 のとき: 5 × (-8.4591) = -42.2955%")
print("  つまり、JEPXは最大 +42.3% まで")
print("")
print("オプション2: 定数項を無視した近似")
print("  もし -8.4591 を無視すると:")
print("  5 × 0.040635 × b = 85")
print("  0.203175 × b = 85")
b_approx = 85 / 0.203175
print(f"  b = {b_approx:.2f} kW")

print("\n【7. ユーザーの式 (144.2137) の解釈】")
print("-"*80)
print("もし 144.2137 が正しい値なら:")
print("  0.203175 × b = 144.2137")
b_calc = 144.2137 / 0.203175
print(f"  b = {b_calc:.2f} kW")
print("")
print("検証:")
delta_per_block = coef * b_calc - intercept
total_baseline = 5 * delta_per_block
total_with_jepx = total_baseline + 85

print(f"  1ブロックのΔSOC: 0.040635 × {b_calc:.2f} - 8.4591")
print(f"                  = {delta_per_block:.4f}%")
print(f"  5ブロックの合計: 5 × {delta_per_block:.4f}")
print(f"                  = {total_baseline:.4f}%")
print(f"  JEPX後の合計: {total_baseline:.4f} + 85")
print(f"              = {total_with_jepx:.4f}%")
print("")
if abs(total_with_jepx) < 0.01:
    print("  ✓ サイクル制約を満たす")
else:
    print(f"  ✗ サイクル制約違反 ({total_with_jepx:.4f}% ≠ 0)")

print("\n【8. SOC推移の確認】")
print("-"*80)
soc = 5.0
print(f"{'ブロック':<12} {'時間':<15} {'基準値(kW)':<12} "
      f"{'ΔSOC(%)':<12} {'SOC(%)':<10}")
print("-"*80)

blocks = [
    (1, "0-3h", 0, 0),
    (2, "3-6h", 0, 0),
    (3, "6-9h", b_calc, delta_per_block),
    (4, "9-12h", b_calc, delta_per_block),
    (5, "12-15h", b_calc, delta_per_block),
    (6, "15-18h", b_calc, delta_per_block),
    (7, "18-21h", b_calc, delta_per_block),
    (8, "21-24h(JEPX)", 0, 85)
]

for block, time, kw, delta in blocks:
    if kw == 0 and delta == 0 and block <= 2:
        status = "(不参加)"
    elif kw == 0 and delta == 85:
        status = "(JEPX)"
    else:
        status = ""
    
    print(f"ブロック{block:<4} {time:<15} {kw:>8.2f}    "
          f"{delta:>8.4f}    {soc:>6.2f}  {status}")
    soc += delta

print("-"*80)
print(f"最終SOC: {soc:.2f}%")
if abs(soc - 5.0) < 0.1:
    print("✓ サイクル完了 (初期値に戻る)")
elif soc > 90:
    print(f"✗ SOC上限超過 ({soc:.2f}% > 90%)")
elif soc < 5:
    print(f"✗ SOC下限違反 ({soc:.2f}% < 5%)")
else:
    print(f"✗ サイクル不完全 (差: {soc - 5.0:.2f}%)")

print("\n【9. 総容量】")
print("-"*80)
total_capacity = 5 * b_calc
print(f"参加ブロック数: 5")
print(f"各ブロックの基準値: {b_calc:.2f} kW")
print(f"総容量: 5 × {b_calc:.2f} = {total_capacity:.2f} kW")

print("\n【10. 通常ケースとの比較】")
print("-"*80)
normal_capacity = 3549
ratio = total_capacity / normal_capacity * 100
reduction = 100 - ratio

print(f"通常ケース (7ブロック + JEPX): 3,549 kW")
print(f"このケース (5ブロック + JEPX):  {total_capacity:.0f} kW")
print(f"比率: {ratio:.1f}%")
print(f"減少: {reduction:.1f}%")

print("\n【11. 結論】")
print("="*80)
if abs(total_with_jepx) < 0.01:
    print(f"✓ 基準値 {b_calc:.0f} kW でサイクル制約を満たす")
    print(f"✓ 総容量 {total_capacity:.0f} kW を実現可能")
    print(f"✓ ただし、SOC上限 ({soc:.2f}%) に注意")
else:
    print(f"✗ サイクル制約を満たさない ({total_with_jepx:.4f}% ≠ 0)")
    print("✗ この運用パターンは実現不可能")
    print("")
    print("代替案:")
    print("  1. JEPXのΔSOCを調整")
    print("  2. ブロック1,2も参加")
    print("  3. 初期SOCを調整")
print("="*80)
