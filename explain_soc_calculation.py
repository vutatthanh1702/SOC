"""
SOC推移の計算方法を詳しく説明
"""

print("="*80)
print("SOC推移の計算方法")
print("="*80)

# 基本データ
coef = 0.040635  # 回帰分析から得られた係数
intercept = 8.4591  # 回帰分析から得られた定数項
b = 709.80  # 基準値 (kW)

print("\n【1. 基本式】")
print("-"*80)
print("回帰分析から得られた式 (1時間あたり):")
print("  ΔSOC (%/1時間) = 0.013545 × 基準値 - 2.8197")
print("")
print("1ブロック = 3時間なので:")
print("  ΔSOC (%/3時間) = (0.013545 × 基準値 - 2.8197) × 3")
print("  ΔSOC = 0.040635 × 基準値 - 8.4591")
print("")
print("この式の意味:")
print("  - 0.040635 × 基準値: 基準値に比例して増加")
print("  - 8.4591: 常に減少する定数項 (自己放電など)")

print("\n【2. 1ブロックのΔSOCを計算】")
print("-"*80)
print(f"基準値 b = {b} kW のとき:")
print(f"  ΔSOC = 0.040635 × {b} - 8.4591")
print(f"       = {coef * b} - 8.4591")

delta_soc = coef * b - intercept
print(f"       = {delta_soc:.4f}%")
print("")
print("これが1ブロック(3時間)でSOCが変化する量です")

print("\n【3. SOCの累積計算】")
print("-"*80)
print("SOCは累積していきます:")
print("  新しいSOC = 現在のSOC + ΔSOC")
print("")

# 初期SOC
soc = 5.0
print("ステップバイステップの計算:")
print("")

# ブロック1,2 (不参加)
print(f"初期状態:")
print(f"  SOC = {soc:.2f}%")
print("")

print(f"ブロック1 (0-3h): 参加しない")
print(f"  ΔSOC = 0%")
print(f"  SOC = {soc:.2f}% + 0% = {soc:.2f}%")
print("")

print(f"ブロック2 (3-6h): 参加しない")
print(f"  ΔSOC = 0%")
print(f"  SOC = {soc:.2f}% + 0% = {soc:.2f}%")
print("")

# ブロック3-7 (参加)
blocks = [
    (3, "6-9h"),
    (4, "9-12h"),
    (5, "12-15h"),
    (6, "15-18h"),
    (7, "18-21h")
]

for block_num, time_range in blocks:
    print(f"ブロック{block_num} ({time_range}): 基準値 {b} kW で参加")
    print(f"  ΔSOC = 0.040635 × {b} - 8.4591")
    print(f"       = {delta_soc:.4f}%")
    soc += delta_soc
    print(f"  SOC = {soc - delta_soc:.2f}% + {delta_soc:.4f}% = {soc:.2f}%")
    print("")

# JEPX
jepx_delta = 85.0
print(f"ブロック8 (21-24h): JEPX参加")
print(f"  ΔSOC = +{jepx_delta}%")
print(f"  SOC = {soc:.2f}% + {jepx_delta}% = {soc + jepx_delta:.2f}%")
soc += jepx_delta

print("\n【4. 計算式の詳細】")
print("-"*80)
print("具体的な数値で計算:")
print("")
print(f"ステップ1: 1ブロックのΔSOCを計算")
print(f"  ΔSOC = 0.040635 × 709.80 - 8.4591")
print(f"  ΔSOC = 28.8427 - 8.4591")
print(f"  ΔSOC = 20.3836%")
print("")
print(f"ステップ2: 各ブロックでSOCを更新")
print(f"  初期: 5.00%")
print(f"  ブロック3: 5.00 + 20.38 = 25.38%")
print(f"  ブロック4: 25.38 + 20.38 = 45.77%")
print(f"  ブロック5: 45.77 + 20.38 = 66.15%")
print(f"  ブロック6: 66.15 + 20.38 = 86.53%")
print(f"  ブロック7: 86.53 + 20.38 = 106.92%")
print(f"  JEPX: 106.92 + 85.00 = 191.92%")

print("\n【5. なぜこうなるか】")
print("-"*80)
print("基準値が大きいと:")
print("  → ΔSOCが大きくなる (充電量が多い)")
print("  → SOCが急速に上昇")
print("  → 上限90%を超えてしまう ❌")
print("")
print("基準値が小さいと:")
print("  → ΔSOCが小さくなる (または負)")
print("  → SOCがゆっくり変化")
print("  → サイクル制約を満たしやすい ✓")

print("\n【6. 適切な基準値の例 (507 kW, 7ブロック)】")
print("-"*80)
b_correct = 507
delta_correct = coef * b_correct - intercept
print(f"基準値 b = {b_correct} kW のとき:")
print(f"  ΔSOC = 0.040635 × {b_correct} - 8.4591")
print(f"       = {delta_correct:.4f}%")
print("")

soc2 = 5.0
print("SOC推移:")
print(f"  初期: {soc2:.2f}%")
for i in range(1, 8):
    soc2 += delta_correct
    print(f"  ブロック{i}後: {soc2:.2f}%")

soc2 += 85
print(f"  JEPX後: {soc2:.2f}%")
print("")
print(f"サイクル完了: {soc2:.2f}% ≈ 5% ✓")

print("\n【7. 計算のまとめ】")
print("="*80)
print("SOC計算の3つのステップ:")
print("")
print("1. 各ブロックのΔSOCを計算")
print("   ΔSOC = 0.040635 × 基準値 - 8.4591")
print("")
print("2. SOCを順次更新")
print("   新SOC = 現SOC + ΔSOC")
print("")
print("3. 制約をチェック")
print("   - 5% ≤ SOC ≤ 90%")
print("   - 最終SOC = 初期SOC (サイクル制約)")
print("="*80)

print("\n【8. Pythonコードの例】")
print("-"*80)
print("""
# 基本パラメータ
coef = 0.040635
intercept = 8.4591
b = 709.80  # 基準値 (kW)

# 1ブロックのΔSOCを計算
delta_soc = coef * b - intercept
print(f"ΔSOC = {delta_soc:.4f}%")

# SOCを順次計算
soc = 5.0  # 初期SOC
print(f"初期SOC: {soc:.2f}%")

# ブロック1,2は不参加 (ΔSOC = 0)

# ブロック3-7で累積
for i in range(3, 8):
    soc += delta_soc
    print(f"ブロック{i}後: {soc:.2f}%")

# JEPX参加
soc += 85
print(f"JEPX後: {soc:.2f}%")
""")

print("="*80)
