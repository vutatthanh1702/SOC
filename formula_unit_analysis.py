#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我々の回帰式と関西電力の式の単位・スケール分析
実際の数値での比較検証
"""

print("=" * 80)
print("我々の回帰式 vs 関西電力の式 - 実数値比較")
print("=" * 80)
print()

# パラメータ設定
capacity_kwh = 1968  # kWh
baseline_kw = 500    # kW
block_hours = 3      # h

print(f"【入力パラメータ】")
print(f"蓄電池容量: {capacity_kwh} kWh")
print(f"基準値: {baseline_kw} kW")
print(f"ブロック時間: {block_hours} 時間")
print()

# ==========================================
# 我々の回帰式
# ==========================================
print("=" * 80)
print("【我々の回帰式】")
print("=" * 80)

# 回帰式: ΔSOC = 0.040635 × 基準値 - 8.4591
# 注意: この式は特定の容量(10kWh)用に作られた可能性
delta_soc_ours_original = 0.040635 * baseline_kw - 8.4591
print(f"\n■ オリジナル回帰式:")
print(f"   ΔSOC = 0.040635 × {baseline_kw} - 8.4591")
print(f"   ΔSOC = {delta_soc_ours_original:.2f}%")
print(f"\n   ⚠️ 問題: この値は容量1968kWhには合わない！")

# 係数の意味を分析
print(f"\n■ 係数 0.040635 の分析:")
print(f"   0.040635 = 0.013545 × 3時間")

# この係数が想定している容量を逆算
# 0.013545 = 1 / (Capacity × 効率) の形だと仮定
# ΔWhを%に変換: ΔWh / Capacity × 100
# 基準値 × 時間 = ΔWh
# (基準値 × 時間) / Capacity × 100 = ΔSOC
# 基準値 / Capacity × 時間 × 100 = ΔSOC
# 係数 = 時間 / Capacity × 100

assumed_capacity_from_coef = 3 * 100 / 0.040635
print(f"   想定容量 = 3h × 100 / 0.040635 = {assumed_capacity_from_coef:.2f} kWh")
print(f"   → この係数は約7,383 kWh の容量を想定している")

# より厳密には
# 0.013545 = 1 / Capacity の場合
assumed_capacity_hourly = 1 / 0.013545
print(f"\n   または時間係数から:")
print(f"   想定容量 = 1 / 0.013545 = {assumed_capacity_hourly:.2f} kWh")
print(f"   → この係数は約73.8 kWh の容量を想定している")

# 実際のデータを見ると、10kWh用の可能性が高い
print(f"\n   💡 実際には10kWh用に回帰した式の可能性が高い")
print(f"   なぜなら: 0.040635 ≈ 3 / (10 × 効率係数)")

# ==========================================
# 関西電力の式（理論式）
# ==========================================
print()
print("=" * 80)
print("【関西電力の理論式】")
print("=" * 80)

# 理論式: ΔSOC = (基準値 × 時間) / 容量 × 100
delta_soc_kansai = (baseline_kw * block_hours) / capacity_kwh * 100
print(f"\n■ 理論式:")
print(f"   ΔSOC = (基準値 × 時間) / 容量 × 100")
print(f"   ΔSOC = ({baseline_kw} × {block_hours}) / {capacity_kwh} × 100")
print(f"   ΔSOC = {baseline_kw * block_hours} / {capacity_kwh} × 100")
print(f"   ΔSOC = {delta_soc_kansai:.2f}%")
print(f"\n   ✅ この値は容量に応じて正しくスケールする")

# ==========================================
# 比較分析
# ==========================================
print()
print("=" * 80)
print("【比較分析】")
print("=" * 80)

print(f"\n我々の式(オリジナル): {delta_soc_ours_original:.2f}%")
print(f"関西電力の式:          {delta_soc_kansai:.2f}%")
print(f"差分:                  {abs(delta_soc_ours_original - delta_soc_kansai):.2f}%")
print(f"比率:                  {delta_soc_ours_original / delta_soc_kansai:.2f}倍")

# ==========================================
# 我々の式を容量対応に修正
# ==========================================
print()
print("=" * 80)
print("【我々の式の修正版（容量対応）】")
print("=" * 80)

# 修正案1: 係数を容量でスケールする
print(f"\n■ 修正案1: 係数を容量比でスケール")
original_capacity = 10  # kWh (想定)
scale_factor = original_capacity / capacity_kwh
coefficient_scaled = 0.040635 * scale_factor
constant_scaled = 8.4591 * scale_factor

delta_soc_scaled = coefficient_scaled * baseline_kw - constant_scaled
print(f"   想定オリジナル容量: {original_capacity} kWh")
print(f"   スケール係数: {original_capacity}/{capacity_kwh} = {scale_factor:.6f}")
print(f"   修正係数: 0.040635 × {scale_factor:.6f} = {coefficient_scaled:.8f}")
print(f"   修正定数: 8.4591 × {scale_factor:.6f} = {constant_scaled:.6f}")
print(f"   ΔSOC = {coefficient_scaled:.8f} × {baseline_kw} - {constant_scaled:.6f}")
print(f"   ΔSOC = {delta_soc_scaled:.2f}%")

# 修正案2: 一般化した式
print(f"\n■ 修正案2: 容量を変数として一般化")
print(f"   ΔSOC = (基準値 × 時間 / 容量 × 100) - 効率損失")
print(f"   効率損失 ≈ 8.4591% (10kWh基準)")
print(f"   効率損失率 = 8.4591 / 10 = 0.84591 %/kWh")

efficiency_loss_rate = 8.4591 / 10  # %/kWh
efficiency_loss_actual = efficiency_loss_rate * capacity_kwh / 10
delta_soc_generalized = (baseline_kw * block_hours / capacity_kwh * 100) - efficiency_loss_actual

print(f"   実際の効率損失 = 0.84591 × {capacity_kwh}/10 = {efficiency_loss_actual:.2f}%")
print(f"   ΔSOC = {baseline_kw * block_hours / capacity_kwh * 100:.2f} - {efficiency_loss_actual:.2f}")
print(f"   ΔSOC = {delta_soc_generalized:.2f}%")

# 修正案3: 定数項を絶対値（%）として扱う
print(f"\n■ 修正案3: 定数項を固定損失として扱う")
delta_soc_fixed_loss = (baseline_kw * block_hours / capacity_kwh * 100) - 8.4591
print(f"   ΔSOC = (基準値 × 時間 / 容量 × 100) - 8.4591")
print(f"   ΔSOC = {baseline_kw * block_hours / capacity_kwh * 100:.2f} - 8.4591")
print(f"   ΔSOC = {delta_soc_fixed_loss:.2f}%")

# ==========================================
# 推奨される一般化式
# ==========================================
print()
print("=" * 80)
print("【推奨: 容量対応の一般化式】")
print("=" * 80)

print(f"""
■ 理論ベース（関西電力方式）:
   ΔSOC = (基準値[kW] × 時間[h]) / 容量[kWh] × 100

■ 実測補正版（我々の知見を追加）:
   ΔSOC = (基準値 × 時間 / 容量 × 100) - 損失補正
   
   損失補正の推定:
   - 自己放電: 約0.3%/時間 × 3時間 = 0.9%
   - 充電効率: (1 - 0.95) × ΔSOCideal = 5%の損失
   - システム損失: 容量に依存しない固定分 ≈ 3%
   
   合計損失 ≈ 5-10% (容量とΔSOCに応じて変動)
""")

# 実際の計算例
print(f"■ 実際の計算例（容量={capacity_kwh}kWh、基準値={baseline_kw}kW）:")

# 理論値
delta_soc_ideal = baseline_kw * block_hours / capacity_kwh * 100
print(f"\n   1. 理論値（損失なし）:")
print(f"      ΔSOC = {delta_soc_ideal:.2f}%")

# 充電効率補正（95%）
eta_charge = 0.95
delta_soc_with_eta = delta_soc_ideal * eta_charge
print(f"\n   2. 充電効率補正（η={eta_charge}）:")
print(f"      ΔSOC = {delta_soc_ideal:.2f} × {eta_charge} = {delta_soc_with_eta:.2f}%")

# 自己放電補正
self_discharge_rate = 0.003  # 0.3%/h
self_discharge_loss = self_discharge_rate * block_hours * 100
delta_soc_with_self_discharge = delta_soc_with_eta - self_discharge_loss
print(f"\n   3. 自己放電補正（{self_discharge_rate*100}%/h）:")
print(f"      損失 = {self_discharge_rate} × {block_hours} × 100 = {self_discharge_loss:.2f}%")
print(f"      ΔSOC = {delta_soc_with_eta:.2f} - {self_discharge_loss:.2f} = {delta_soc_with_self_discharge:.2f}%")

# システム損失（固定）
system_loss = 3.0  # %
delta_soc_final = delta_soc_with_self_discharge - system_loss
print(f"\n   4. システム損失（固定）:")
print(f"      損失 = {system_loss}%")
print(f"      ΔSOC = {delta_soc_with_self_discharge:.2f} - {system_loss} = {delta_soc_final:.2f}%")

# ==========================================
# 元の回帰式の適用範囲
# ==========================================
print()
print("=" * 80)
print("【元の回帰式の適用範囲】")
print("=" * 80)

print(f"""
我々の回帰式: ΔSOC = 0.040635 × 基準値 - 8.4591

この式は以下の条件で導出されたと推定:
  - 蓄電池容量: 約10 kWh
  - 基準値範囲: 0.3 - 0.7 kW (300-700W)
  - ブロック時間: 3時間
  - データ: kotohira実測データ

⚠️ 適用範囲外の使用:
  容量1968kWhは想定の約200倍
  → 係数を容量に応じてスケールする必要がある

✅ 正しい使用方法:
  1. 関西電力の理論式を使う（容量に依存しない）
  2. または回帰式を容量対応に修正する
""")

# ==========================================
# 検証: 10kWhで元の式を確認
# ==========================================
print()
print("=" * 80)
print("【検証: 元の式が10kWh用だった場合】")
print("=" * 80)

capacity_10kwh = 10  # kWh
baseline_kw_small = 0.5  # kW (500W)

# 理論値
delta_soc_theory_10kwh = (baseline_kw_small * block_hours) / capacity_10kwh * 100
print(f"\n容量10kWh、基準値0.5kW (500W)の場合:")
print(f"  理論式: ΔSOC = ({baseline_kw_small} × {block_hours}) / {capacity_10kwh} × 100 = {delta_soc_theory_10kwh:.2f}%")

# 我々の式
delta_soc_ours_10kwh = 0.040635 * baseline_kw_small - 8.4591
print(f"  我々の式: ΔSOC = 0.040635 × {baseline_kw_small} - 8.4591 = {delta_soc_ours_10kwh:.2f}%")

print(f"\n  差分: {abs(delta_soc_theory_10kwh - delta_soc_ours_10kwh):.2f}%")
print(f"  → 10kWhでも合わない！定数項が大きすぎる")

# より現実的な基準値で試す
baseline_kw_realistic = 3.0  # kW
delta_soc_theory_realistic = (baseline_kw_realistic * block_hours) / capacity_10kwh * 100
delta_soc_ours_realistic = 0.040635 * baseline_kw_realistic - 8.4591

print(f"\n容量10kWh、基準値3.0kW (3000W)の場合:")
print(f"  理論式: ΔSOC = ({baseline_kw_realistic} × {block_hours}) / {capacity_10kwh} × 100 = {delta_soc_theory_realistic:.2f}%")
print(f"  我々の式: ΔSOC = 0.040635 × {baseline_kw_realistic} - 8.4591 = {delta_soc_ours_realistic:.2f}%")
print(f"  差分: {abs(delta_soc_theory_realistic - delta_soc_ours_realistic):.2f}%")

# ==========================================
# 最終推奨
# ==========================================
print()
print("=" * 80)
print("【最終推奨】")
print("=" * 80)

print(f"""
✅ 容量非依存の一般化式を使用すべき:

   ΔSOC[%] = (基準値[kW] × 時間[h] / 容量[kWh] × 100) / 充電効率 - 損失

   具体的には:
   
   def calculate_delta_soc(baseline_kw, block_hours, capacity_kwh, 
                          eta_charge=0.95, self_discharge_rate=0.003):
       # 理論的なSOC変化
       delta_soc_ideal = (baseline_kw * block_hours / capacity_kwh * 100)
       
       # 充電効率補正
       delta_soc = delta_soc_ideal / eta_charge
       
       # 自己放電補正
       self_discharge_loss = self_discharge_rate * block_hours * 100
       delta_soc -= self_discharge_loss
       
       return delta_soc

📊 あなたのケースでの推奨値:
   容量: {capacity_kwh} kWh
   基準値: {baseline_kw} kW
   → ΔSOC ≈ {delta_soc_with_self_discharge:.2f}% (充電効率・自己放電考慮)
   
   関西電力の理論値 {delta_soc_kansai:.2f}% に効率補正を加えた値

❌ 避けるべき:
   元の回帰式 ΔSOC = 0.040635 × 基準値 - 8.4591 を
   異なる容量に直接適用すること
""")

print()
print("=" * 80)
print("分析完了")
print("=" * 80)
