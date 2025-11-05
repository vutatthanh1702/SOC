"""
正しい式: 5ブロック参加 + JEPX放電の場合
0.040635 × 5b - 5 × 8.4591 = 85
"""

print("="*80)
print("正しい式: 5ブロック参加 + JEPX放電")
print("="*80)

coef = 0.040635
intercept = 8.4591

print("\n【1. 状況の理解】")
print("-"*80)
print("ブロック1,2: 参加しない")
print("ブロック3-7: 1次調整力参加 (5ブロック) → 充電")
print("ブロック8: JEPX参加 → 放電 (ΔSOC = -85%)")
print("")
print("サイクル制約:")
print("  Σ(ΔSOC_baseline) + ΔSOC_JEPX = 0")
print("  Σ(ΔSOC_baseline) = -ΔSOC_JEPX")
print("  Σ(ΔSOC_baseline) = -(-85) = +85%")
print("")
print("つまり、baselineで+85%充電し、JEPXで-85%放電する")

print("\n【2. 正しい式】")
print("-"*80)
print("5ブロックで+85%充電する必要:")
print("  5 × (0.040635 × b - 8.4591) = 85")
print("")
print("展開:")
print("  5 × 0.040635 × b - 5 × 8.4591 = 85")
print("  0.203175 × b - 42.2955 = 85")

print("\n【3. bを解く】")
print("-"*80)
coef_5 = 5 * coef
const_5 = 5 * intercept

print(f"  {coef_5} × b = 85 + {const_5}")
right_side = 85 + const_5
print(f"  {coef_5} × b = {right_side}")

b = right_side / coef_5
print(f"  b = {right_side} / {coef_5}")
print(f"  b = {b:.2f} kW")

print("\n【4. 検算】")
print("-"*80)
delta_per_block = coef * b - intercept
total_5blocks = 5 * delta_per_block
jepx_delta = -85  # 放電なので負
total = total_5blocks + jepx_delta

print(f"1ブロックのΔSOC:")
print(f"  ΔSOC = 0.040635 × {b:.2f} - 8.4591")
print(f"       = {coef * b:.4f} - 8.4591")
print(f"       = {delta_per_block:.4f}%")

print(f"\n5ブロックの合計ΔSOC:")
print(f"  5 × {delta_per_block:.4f} = {total_5blocks:.4f}%")

print(f"\nJEPX (放電):")
print(f"  ΔSOC = -85.00%")

print(f"\n合計:")
print(f"  {total_5blocks:.4f} + (-85) = {total:.4f}%")

if abs(total) < 0.01:
    print("\n✓ サイクル制約を満たす (合計 ≈ 0)")
else:
    print(f"\n✗ サイクル制約違反 ({total:.4f}% ≠ 0)")

print("\n【5. 制約チェック】")
print("-"*80)
if 0 <= b <= 2000:
    print(f"✓ 基準値制約OK: 0 ≤ {b:.2f} ≤ 2000 kW")
else:
    print(f"✗ 基準値制約違反: {b:.2f} kW")

# SOC推移
print("\n【6. SOC推移】")
print("-"*80)
soc = 5.0
print(f"{'ブロック':<12} {'時間':<15} {'基準値(kW)':<12} "
      f"{'ΔSOC(%)':<12} {'SOC(%)':<10}")
print("-"*80)

blocks = [
    (1, "0-3h", 0, 0, "(不参加)"),
    (2, "3-6h", 0, 0, "(不参加)"),
    (3, "6-9h", b, delta_per_block, ""),
    (4, "9-12h", b, delta_per_block, ""),
    (5, "12-15h", b, delta_per_block, ""),
    (6, "15-18h", b, delta_per_block, ""),
    (7, "18-21h", b, delta_per_block, ""),
    (8, "21-24h", 0, -85, "(JEPX放電)")
]

for block_num, time, kw, delta, note in blocks:
    print(f"ブロック{block_num:<4} {time:<15} {kw:>8.2f}    "
          f"{delta:>8.4f}    {soc:>6.2f}  {note}")
    soc += delta

print("-"*80)
print(f"最終SOC: {soc:.2f}%")

if abs(soc - 5.0) < 0.1:
    print("✓ サイクル完了 (初期値5%に戻る)")
elif soc > 90:
    print(f"✗ SOC上限超過 ({soc:.2f}% > 90%)")
elif soc < 5:
    print(f"✗ SOC下限違反 ({soc:.2f}% < 5%)")
else:
    print(f"⚠ SOC: {soc:.2f}% (差: {soc - 5.0:.2f}%)")

# SOC範囲チェック
print("\nSOC範囲チェック:")
soc_check = 5.0
max_soc = 5.0
min_soc = 5.0
for block_num, time, kw, delta, note in blocks:
    soc_check += delta
    max_soc = max(max_soc, soc_check)
    min_soc = min(min_soc, soc_check)

print(f"  最大SOC: {max_soc:.2f}%")
print(f"  最小SOC: {min_soc:.2f}%")
if 5 <= min_soc and max_soc <= 90:
    print("  ✓ SOC制約 (5%-90%) を満たす")
else:
    if max_soc > 90:
        print(f"  ✗ 上限超過: {max_soc:.2f}% > 90%")
    if min_soc < 5:
        print(f"  ✗ 下限違反: {min_soc:.2f}% < 5%")

print("\n【7. 総容量】")
print("-"*80)
total_capacity = 5 * b
print(f"参加ブロック数: 5")
print(f"各ブロックの基準値: {b:.2f} kW")
print(f"総容量: 5 × {b:.2f} = {total_capacity:.2f} kW")

print("\n【8. 比較】")
print("-"*80)
normal = 3549
no_jepx = 1041
ratio_normal = total_capacity / normal * 100
ratio_no_jepx = total_capacity / no_jepx * 100

print(f"通常ケース (7ブロック+JEPX充電): 3,549 kW (100%)")
print(f"このケース (5ブロック+JEPX放電): {total_capacity:.0f} kW ({ratio_normal:.1f}%)")
print(f"JEPX不参加 (5ブロック):          1,041 kW ({ratio_no_jepx:.1f}%)")

print("\n【9. 結論】")
print("="*80)
if abs(total) < 0.01 and 0 <= b <= 2000 and 5 <= min_soc and max_soc <= 90:
    print(f"✓ 正しい式: 5 × (0.040635 × b - 8.4591) = 85")
    print(f"✓ 解: b = {b:.2f} kW")
    print(f"✓ 総容量: {total_capacity:.0f} kW")
    print(f"✓ すべての制約を満たす")
    print("")
    print("この運用パターンは実現可能！")
else:
    print("制約違反あり:")
    if abs(total) >= 0.01:
        print(f"  - サイクル制約: {total:.4f}% ≠ 0")
    if b < 0 or b > 2000:
        print(f"  - 基準値制約: {b:.2f} kW")
    if max_soc > 90:
        print(f"  - SOC上限: {max_soc:.2f}% > 90%")
    if min_soc < 5:
        print(f"  - SOC下限: {min_soc:.2f}% < 5%")
print("="*80)

print("\n【10. 重要な発見】")
print("-"*80)
print("JEPXの方向を変えると:")
print("")
print("パターンA: JEPX充電 (+85%)")
print("  → 5ブロックで-85%放電が必要")
print("  → b = -210 kW  ❌ (実現不可能)")
print("")
print("パターンB: JEPX放電 (-85%)")
print("  → 5ブロックで+85%充電が必要")
print(f"  → b = {b:.0f} kW  ✓ (実現可能)")
print("")
print("結論: JEPXで放電する場合のみ、5ブロックで運用可能！")
print("="*80)
