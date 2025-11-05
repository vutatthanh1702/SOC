"""
ケース: ブロック1,2不参加 & JEPX不参加の分析
- ブロック1,2: 参加できない (ΔSOC = 0)
- ブロック3-7: 1次調整力のみ (5ブロック)
- ブロック8(JEPX): 参加しない (ΔSOC = 0)
"""

print("="*80)
print("ケース: ブロック1,2不参加 & JEPX不参加")
print("="*80)

# 係数
coef = 0.040635  # 1ブロック(3時間)の係数
intercept = 8.4591  # 1ブロックの定数項

print("\n【1. 制約条件】")
print("-"*80)
print("参加ブロック: 3, 4, 5, 6, 7 (5ブロックのみ)")
print("ブロック1,2: 参加不可 → ΔSOC = 0")
print("ブロック8(JEPX): 参加しない → ΔSOC = 0")
print("\nサイクル制約:")
print("  Σ(ΔSOC_baseline) + ΔSOC_JEPX = 0")
print("  Σ(ΔSOC_baseline) + 0 = 0  (JEPXなし)")
print("  Σ(ΔSOC_baseline) = 0")

print("\n【2. 各ブロックの条件】")
print("-"*80)
print("ブロック1,2: ΔSOC = 0 (参加不可)")
print("ブロック3-7: ΔSOC = 0.040635 × b - 8.4591")
print("ブロック8: ΔSOC = 0 (JEPX不参加)")

print("\n【3. サイクル制約から基準値を求める】")
print("-"*80)
print("5ブロックの合計:")
print("  Σ(ΔSOCᵢ) = 5 × (0.040635 × b - 8.4591) = 0")
print("  0.040635 × b - 8.4591 = 0")
print("  0.040635 × b = 8.4591")
print("  b = 8.4591 / 0.040635")

b_required = 8.4591 / 0.040635
print(f"  b = {b_required:.2f} kW")

print("\n【4. 検証】")
print("-"*80)
delta_soc_per_block = coef * b_required - intercept
total_delta_soc = 5 * delta_soc_per_block

print(f"1ブロックのΔSOC: {coef:.6f} × {b_required:.2f} - {intercept:.4f} = {delta_soc_per_block:.6f}%")
print(f"5ブロックの合計ΔSOC: 5 × {delta_soc_per_block:.6f} = {total_delta_soc:.6f}%")

if abs(total_delta_soc) < 0.01:
    print("✓ サイクル制約を満たす (≈ 0)")
else:
    print(f"✗ サイクル制約違反 ({total_delta_soc:.4f}%)")

print("\n【5. 総容量】")
print("-"*80)
total_capacity = 5 * b_required
print(f"参加ブロック数: 5")
print(f"各ブロックの基準値: {b_required:.2f} kW")
print(f"総容量: 5 × {b_required:.2f} = {total_capacity:.2f} kW")

print("\n【6. SOC推移の確認】")
print("-"*80)
soc = 5.0  # 初期SOC
print(f"{'ブロック':<12} {'時間':<15} {'基準値(kW)':<12} {'ΔSOC(%)':<12} {'SOC(%)':<10}")
print("-"*80)

blocks = [
    (1, "0-3h", 0, 0),
    (2, "3-6h", 0, 0),
    (3, "6-9h", b_required, delta_soc_per_block),
    (4, "9-12h", b_required, delta_soc_per_block),
    (5, "12-15h", b_required, delta_soc_per_block),
    (6, "15-18h", b_required, delta_soc_per_block),
    (7, "18-21h", b_required, delta_soc_per_block),
    (8, "21-24h(JEPX)", 0, 0)
]

for block, time, kw, delta in blocks:
    print(f"ブロック{block:<4} {time:<15} {kw:>8.2f}    {delta:>8.4f}    {soc:>6.2f}")
    soc += delta

print("-"*80)
print(f"最終SOC: {soc:.2f}% (初期値5%に戻る必要)")
if abs(soc - 5.0) < 0.1:
    print("✓ サイクル完了")
else:
    print(f"✗ サイクル不完全 (差: {soc - 5.0:.4f}%)")

print("\n【7. 比較表】")
print("="*80)
print(f"{'ケース':<35} {'容量(kW)':<15} {'基準値/ブロック':<15} {'参加ブロック'}")
print("-"*80)
print(f"{'通常(7ブロック + JEPX)':<35} {'3,549':<15} {'507 kW':<15} {'7'}")
print(f"{'ブロック1,2不参加 + JEPX':<35} {'2,535':<15} {'507 kW':<15} {'5'}")
print(f"{'通常(7ブロック) - JEPX不参加':<35} {'1,457':<15} {'208 kW':<15} {'7'}")
print(f"{'ブロック1,2不参加 - JEPX不参加':<35} {f'{total_capacity:.0f}':<15} {f'{b_required:.0f} kW':<15} {'5'}")
print("="*80)

print("\n【8. 容量減少率】")
print("-"*80)
full_capacity = 3549
reduction_from_full = (1 - total_capacity / full_capacity) * 100
reduction_from_no12 = (1 - total_capacity / 2535) * 100
reduction_from_nojepx = (1 - total_capacity / 1457) * 100

print(f"通常ケースとの比較:           {total_capacity:.0f} / {full_capacity} = {total_capacity/full_capacity*100:.1f}% ({reduction_from_full:.1f}%減少)")
print(f"ブロック1,2不参加との比較:    {total_capacity:.0f} / 2,535 = {total_capacity/2535*100:.1f}% ({reduction_from_no12:.1f}%減少)")
print(f"JEPX不参加(7ブロック)との比較: {total_capacity:.0f} / 1,457 = {total_capacity/1457*100:.1f}% ({reduction_from_nojepx:.1f}%減少)")

print("\n【9. 重要な結論】")
print("="*80)
print(f"✓ ブロック1,2に参加できず、JEPXにも参加しない場合:")
print(f"  - 各ブロック: {b_required:.2f} kW (固定)")
print(f"  - 総容量: {total_capacity:.0f} kW")
print(f"  - 通常ケースの {total_capacity/full_capacity*100:.1f}% に減少")
print(f"  - サイクル制約により、基準値は {b_required:.2f} kW に固定される")
print(f"  - これは「JEPX不参加」の制約が支配的")
print("="*80)
