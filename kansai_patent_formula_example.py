#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関西電力 特許 JP 7377392 B1 の式の実装
具体例: 10kWh、5% → 90%、3時間
"""

def calculate_kansai_baseline(capacity_wh, soc_current_percent, 
                               soc_target_percent, block_hours):
    """
    関西電力の特許式に基づく基準値計算
    
    特許 JP 7377392 B1【００８２】段落の式1:
    B_{n+1} Ref = (X - (B_n SOC_N + B_n Ref × (T-N))) / T
    
    ゲートクローズ時（N=0）の簡略版:
    B_{n+1} Ref = (X - B_n SOC_0) / T
    
    Args:
        capacity_wh: 蓄電池定格容量 [Wh]
        soc_current_percent: 現在のSOC [%]
        soc_target_percent: 目標SOC [%]
        block_hours: ブロック時間 [h]
    
    Returns:
        dict: 計算結果の詳細
    """
    # SOCを容量(Wh)に変換
    current_capacity = capacity_wh * soc_current_percent / 100
    target_capacity = capacity_wh * soc_target_percent / 100
    
    # 必要な充電量
    delta_capacity = target_capacity - current_capacity
    
    # 基準値の計算（式1のゲートクローズ簡略版）
    # B_{n+1} Ref = (目標容量 - 現在容量) / ブロック時間
    baseline_w = delta_capacity / block_hours
    
    # 検証: この基準値でどれだけSOCが変化するか
    charge_energy = baseline_w * block_hours
    delta_soc = charge_energy / capacity_wh * 100
    final_soc = soc_current_percent + delta_soc
    
    return {
        'current_capacity_wh': current_capacity,
        'target_capacity_wh': target_capacity,
        'delta_capacity_wh': delta_capacity,
        'baseline_w': baseline_w,
        'baseline_kw': baseline_w / 1000,
        'charge_energy_wh': charge_energy,
        'delta_soc_percent': delta_soc,
        'final_soc_percent': final_soc
    }


def print_calculation_details(capacity, soc_current, soc_target, hours):
    """
    計算過程を詳細に表示
    """
    print("=" * 80)
    print("関西電力 特許 JP 7377392 B1 - 基準値計算")
    print("=" * 80)
    print()
    
    print("【特許情報】")
    print("  特許番号: JP 7377392 B1")
    print("  発行日: 2023年11月9日")
    print("  参照段落: 【００８２】")
    print()
    
    print("【使用する式】")
    print("  一般形（式1）:")
    print("    B_{n+1} Ref = (X - (B_n SOC_N + B_n Ref × (T-N))) / T")
    print()
    print("  ゲートクローズ時（N=0）の簡略版:")
    print("    B_{n+1} Ref = (X - B_n SOC_0) / T")
    print("    B_{n+1} Ref = (目標容量 - 現在容量) / ブロック時間")
    print()
    
    print("=" * 80)
    print("【入力パラメータ】")
    print("=" * 80)
    print(f"  蓄電池容量 X: {capacity} Wh ({capacity/1000} kWh)")
    print(f"  現在SOC: {soc_current}%")
    print(f"  目標SOC: {soc_target}%")
    print(f"  ブロック時間 T: {hours} 時間")
    print(f"  ゲートクローズ N: 0 時間（ブロック開始直後）")
    print()
    
    # 計算実行
    result = calculate_kansai_baseline(capacity, soc_current, soc_target, hours)
    
    print("=" * 80)
    print("【計算ステップ】")
    print("=" * 80)
    print()
    
    print("ステップ1: SOCを容量(Wh)に変換")
    print("-" * 80)
    print(f"  現在容量 = {capacity} × {soc_current} / 100")
    print(f"           = {result['current_capacity_wh']:.0f} Wh")
    print()
    print(f"  目標容量 = {capacity} × {soc_target} / 100")
    print(f"           = {result['target_capacity_wh']:.0f} Wh")
    print()
    
    print("ステップ2: 必要な充電量を計算")
    print("-" * 80)
    print(f"  必要充電量 = 目標容量 - 現在容量")
    print(f"            = {result['target_capacity_wh']:.0f} - {result['current_capacity_wh']:.0f}")
    print(f"            = {result['delta_capacity_wh']:.0f} Wh")
    print()
    
    print("ステップ3: 基準値を計算（式1）")
    print("-" * 80)
    print(f"  B_{{n+1}} Ref = (X - B_n SOC_0) / T")
    print(f"              = ({result['target_capacity_wh']:.0f} - {result['current_capacity_wh']:.0f}) / {hours}")
    print(f"              = {result['delta_capacity_wh']:.0f} / {hours}")
    print(f"              = {result['baseline_w']:.2f} W")
    print(f"              = {result['baseline_kw']:.3f} kW")
    print()
    
    print("=" * 80)
    print("【計算結果】")
    print("=" * 80)
    print()
    print(f"  📊 基準値: {result['baseline_w']:.2f} W")
    print(f"           = {result['baseline_kw']:.3f} kW")
    print()
    
    print("=" * 80)
    print("【検証】")
    print("=" * 80)
    print()
    print("この基準値で充電した場合のSOC変化:")
    print("-" * 80)
    print(f"  充電エネルギー = 基準値 × 時間")
    print(f"                = {result['baseline_w']:.2f} × {hours}")
    print(f"                = {result['charge_energy_wh']:.0f} Wh")
    print()
    print(f"  ΔSOC = 充電エネルギー / 容量 × 100")
    print(f"       = {result['charge_energy_wh']:.0f} / {capacity} × 100")
    print(f"       = {result['delta_soc_percent']:.2f}%")
    print()
    print(f"  最終SOC = 現在SOC + ΔSOC")
    print(f"         = {soc_current}% + {result['delta_soc_percent']:.2f}%")
    print(f"         = {result['final_soc_percent']:.2f}%")
    print()
    
    # 検証
    if abs(result['final_soc_percent'] - soc_target) < 0.01:
        print("  ✅ 目標SOCに正確に到達しました！")
    else:
        print(f"  ⚠️ 目標SOCとの差: {result['final_soc_percent'] - soc_target:.2f}%")
    
    print()
    print("=" * 80)
    print("【SOC変化の視覚化】")
    print("=" * 80)
    print()
    print("  時間軸:")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"    t=0h{' '*10}t=1h{' '*10}t=2h{' '*10}t=3h")
    print("    ├─────────────┼─────────────┼─────────────┤")
    print("    GC時点        充電中         充電中         ブロック終了")
    print("    (決定)")
    print()
    print("  SOC変化:")
    print(f"    {soc_current}% {'─' * 50}> {soc_target}%")
    print(f"       <{'─' * 20} 充電: {result['baseline_kw']:.3f} kW {'─' * 20}>")
    print()
    print(f"       ΔSOC = +{result['delta_soc_percent']:.2f}%")
    print(f"       充電量 = {result['charge_energy_wh']:.0f} Wh")
    print(f"       時間 = {hours} 時間")
    print(f"       基準値 = {result['baseline_w']:.2f} W")
    print()
    print("=" * 80)
    
    return result


# メイン実行
if __name__ == "__main__":
    # 具体例: 10kWh、5% → 90%、3時間
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "関西電力 特許式の具体例" + " " * 38 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # 例1: 10kWh（小規模）
    print("\n" + "▼" * 40)
    print("例1: 小規模バッテリー（10kWh）")
    print("▼" * 40 + "\n")
    
    result1 = print_calculation_details(
        capacity=10000,      # 10 kWh
        soc_current=5,       # 5%
        soc_target=90,       # 90%
        hours=3              # 3時間
    )
    
    # 例2: 1968kWh（大規模）
    print("\n\n" + "▼" * 40)
    print("例2: 大規模バッテリー（1968kWh）")
    print("▼" * 40 + "\n")
    
    result2 = print_calculation_details(
        capacity=1968000,    # 1968 kWh
        soc_current=5,       # 5%
        soc_target=90,       # 90%
        hours=3              # 3時間
    )
    
    # 比較
    print("\n" + "=" * 80)
    print("【2つの例の比較】")
    print("=" * 80)
    print()
    print("| 項目 | 10kWh | 1968kWh | スケール比 |")
    print("|------|-------|---------|-----------|")
    print(f"| 容量 | {result1['current_capacity_wh']:.0f} Wh | {result2['current_capacity_wh']:.0f} Wh | {result2['current_capacity_wh']/result1['current_capacity_wh']:.0f}x |")
    print(f"| 必要充電量 | {result1['delta_capacity_wh']:.0f} Wh | {result2['delta_capacity_wh']:.0f} Wh | {result2['delta_capacity_wh']/result1['delta_capacity_wh']:.0f}x |")
    print(f"| 基準値 | {result1['baseline_kw']:.3f} kW | {result2['baseline_kw']:.2f} kW | {result2['baseline_kw']/result1['baseline_kw']:.0f}x |")
    print(f"| ΔSOC | {result1['delta_soc_percent']:.2f}% | {result2['delta_soc_percent']:.2f}% | 同じ |")
    print()
    print("💡 ポイント:")
    print("   - 基準値（電力）は容量に比例してスケールする")
    print("   - ΔSOCは容量に依存しない（同じSOC変化）")
    print("   - 関西電力の式は任意の容量に適用可能！")
    print()
    print("=" * 80)
