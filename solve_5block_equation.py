"""
5 × (0.040635 × b - 8.4591) + 85 = 0 を解く
"""

print("="*80)
print("式: 5 × (0.040635 × b - 8.4591) + 85 = 0 を解く")
print("="*80)

coef = 0.040635
intercept = 8.4591

print("\n【1. 元の式】")
print("-"*80)
print("5 × (0.040635 × b - 8.4591) + 85 = 0")

print("\n【2. ステップバイステップで解く】")
print("-"*80)

print("\nステップ1: 括弧を展開")
print("  5 × 0.040635 × b - 5 × 8.4591 + 85 = 0")
coef_5 = 5 * coef
const_5 = 5 * intercept
print(f"  {coef_5} × b - {const_5} + 85 = 0")

print("\nステップ2: 定数項をまとめる")
const_sum = -const_5 + 85
print(f"  {coef_5} × b + ({-const_5} + 85) = 0")
print(f"  {coef_5} × b + {const_sum} = 0")

print("\nステップ3: bについて解く")
print(f"  {coef_5} × b = -{const_sum}")
print(f"  {coef_5} × b = {-const_sum}")

b = -const_sum / coef_5
print(f"  b = {-const_sum} / {coef_5}")
print(f"  b = {b:.2f} kW")

print("\n【3. 検算】")
print("-"*80)
print(f"b = {b:.2f} を代入:")
delta_per_block = coef * b - intercept
total_5blocks = 5 * delta_per_block
total_with_jepx = total_5blocks + 85

print(f"\n1ブロックのΔSOC:")
print(f"  ΔSOC = 0.040635 × {b:.2f} - 8.4591")
print(f"       = {coef * b:.4f} - 8.4591")
print(f"       = {delta_per_block:.4f}%")

print(f"\n5ブロックの合計ΔSOC:")
print(f"  5 × {delta_per_block:.4f} = {total_5blocks:.4f}%")

print(f"\nJEPX後の合計:")
print(f"  {total_5blocks:.4f} + 85 = {total_with_jepx:.4f}%")

if abs(total_with_jepx) < 0.01:
    print("\n✓ 検算OK: 合計 ≈ 0")
else:
    print(f"\n✗ 検算NG: 合計 = {total_with_jepx:.4f} ≠ 0")

print("\n【4. 結果の解釈】")
print("-"*80)
if b < 0:
    print(f"❌ b = {b:.2f} kW (負の値)")
    print("\n基準値が負になる = この式には正の解が存在しない")
    print("\n理由:")
    print("  5ブロックだけでは JEPX +85% を相殺できない")
    print("  各ブロックは最小で ΔSOC = -8.4591% (b=0のとき)")
    print("  5ブロックの最小合計: 5 × (-8.4591) = -42.2955%")
    print("  これは -85% より小さい (絶対値)")
    print("  つまり、JEPX +85% を打ち消すには不十分")
elif b > 2000:
    print(f"❌ b = {b:.2f} kW (上限2000 kW超過)")
    print("\n基準値の上限制約に違反")
else:
    print(f"✓ b = {b:.2f} kW (有効な範囲)")
    
    # SOC推移を確認
    print("\nSOC推移:")
    soc = 5.0
    print(f"  初期SOC: {soc:.2f}%")
    
    # ブロック1,2
    print(f"  ブロック1,2: 不参加 → SOC = {soc:.2f}%")
    
    # ブロック3-7
    for i in range(3, 8):
        soc += delta_per_block
        print(f"  ブロック{i}後: {soc:.2f}%")
    
    # JEPX
    soc += 85
    print(f"  JEPX後: {soc:.2f}%")
    
    if soc > 90:
        print(f"\n❌ SOC上限超過 ({soc:.2f}% > 90%)")
    elif soc < 5:
        print(f"\n❌ SOC下限違反 ({soc:.2f}% < 5%)")
    else:
        print(f"\n✓ SOC制約を満たす ({soc:.2f}%)")

print("\n【5. 数値の意味】")
print("-"*80)
print(f"定数項の合計: {const_sum:.4f}")
print(f"  = -5 × 8.4591 + 85")
print(f"  = -42.2955 + 85")
print(f"  = 42.7045")
print("")
print("これが正の値なので:")
print("  0.203175 × b = -42.7045")
print("  b = 負の値になる")
print("")
print("もし JEPXが逆方向（放電）なら:")
print("  5 × (0.040635 × b - 8.4591) - 85 = 0")
print("  0.203175 × b = 127.2955")
b_reverse = (const_5 + 85) / coef_5
print(f"  b = {b_reverse:.2f} kW  ✓ (正の値)")

print("\n【6. 結論】")
print("="*80)
print(f"式: 5 × (0.040635 × b - 8.4591) + 85 = 0")
print(f"解: b = {b:.2f} kW")
print("")
if b < 0:
    print("❌ 負の値なので実現不可能")
    print("")
    print("実現可能な選択肢:")
    print("  1. 7ブロック参加 → b = 507 kW")
    print("  2. 5ブロック、JEPX不参加 → b = 208 kW")
    print("  3. JEPXの参加量を調整 (85%より小さく)")
else:
    print("✓ 数学的には解が存在")
print("="*80)
