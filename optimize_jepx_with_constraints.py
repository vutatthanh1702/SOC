#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TỐI ƯU HÓA ĐÚNG VỚI JEPX - Xét ràng buộc SOC
"""

import pandas as pd
import numpy as np

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197
HOURS_PER_BLOCK = 3

SOC_MIN = 10  # %
SOC_MAX = 90  # %
BASELINE_MAX = 2000  # kW

print("="*80)
print("🔧 TỐI ƯU HÓA ĐÚNG VỚI JEPX")
print("="*80)

def calc_delta_soc(baseline_kw, hours=3):
    """Tính ΔSOC từ baseline"""
    return (SLOPE * baseline_kw + INTERCEPT) * hours

# JEPX effect từ data thực tế
# 950kW discharge × 3h, công thức: ΔSOC = (0.013545 × (-950) - 2.8197) × 3
jepx_delta = calc_delta_soc(-950, 3)
print(f"\nJEPX discharge (950kW × 3h): ΔSOC = {jepx_delta:.2f}%")

# Tính tổng baseline cần thiết
# Σ(ΔSOC_baseline) + ΔSOC_jepx = 0
# → Σ(ΔSOC_baseline) = -ΔSOC_jepx

n_baseline_blocks = 7
sum_delta_soc_needed = -jepx_delta

# Σ(ΔSOC) = 3 × SLOPE × Σ(b) + 3 × n × INTERCEPT
# → Σ(b) = (Σ(ΔSOC) - 3 × n × INTERCEPT) / (3 × SLOPE)

sum_baseline = (sum_delta_soc_needed - 3 * n_baseline_blocks * INTERCEPT) / (3 * SLOPE)

print(f"\nĐể cycle với JEPX:")
print(f"  Cần Σ(ΔSOC_baseline) = {sum_delta_soc_needed:.2f}%")
print(f"  → Σ(基準値) = {sum_baseline:.2f} kW")
print(f"  So với không JEPX (1665.38kW): +{sum_baseline - 1665.38:.2f}kW ({(sum_baseline/1665.38 - 1)*100:+.1f}%)")

print("\n" + "="*80)
print("❌ VẤN ĐỀ: Pattern 7×2000kW KHÔNG HỢP LỆ")
print("="*80)

print("""
Pattern: 7 blocks @ 2000kW + 1 block JEPX
→ SOC sẽ vượt quá 90% ngay từ block 2!

Block 1: 5% + 72.8% = 77.8% ✅
Block 2: 77.8% + 72.8% = 150.6% ❌ VU ỘT!

Cần tìm pattern khác thỏa mãn:
1. Σ(基準値) = 2615.38 kW
2. SOC_min ≤ SOC(t) ≤ SOC_max
""")

print("\n" + "="*80)
print("🔍 TÌM PATTERN KHẢ THI")
print("="*80)

def simulate_pattern(baselines, soc_start=5.0):
    """Simulate pattern và check constraints"""
    soc = soc_start
    soc_trajectory = [soc]
    
    for b in baselines:
        delta = calc_delta_soc(b, 3)
        soc += delta
        soc_trajectory.append(soc)
    
    # Add JEPX
    soc += jepx_delta
    soc_trajectory.append(soc)
    
    min_soc = min(soc_trajectory)
    max_soc = max(soc_trajectory)
    
    valid = (min_soc >= SOC_MIN) and (max_soc <= SOC_MAX)
    cycle_error = soc_trajectory[-1] - soc_start
    
    return {
        'valid': valid,
        'min_soc': min_soc,
        'max_soc': max_soc,
        'soc_trajectory': soc_trajectory,
        'cycle_error': cycle_error
    }

# Strategy: Mix charge và discharge để giữ SOC trong range
# Thử các patterns khác nhau

print("\nThử các patterns:")
print()

patterns_to_test = []

# Pattern 1: Luân phiên charge-discharge
# 1 charge MAX, 1 discharge, repeat
baselines_1 = []
charge_blocks = 4
discharge_blocks = 3

# Tính discharge level cần thiết
# charge_blocks × 2000 + discharge_blocks × x = 2615.38
discharge_level = (sum_baseline - charge_blocks * 2000) / discharge_blocks

baselines_1 = ([2000, discharge_level] * 3) + [2000]  # 4 charge, 3 discharge

patterns_to_test.append(('Pattern 1: Luân phiên 2000 / discharge', baselines_1))

# Pattern 2: Charge nhiều đầu, discharge cuối
charge_blocks_2 = 3
discharge_level_2 = (sum_baseline - charge_blocks_2 * 2000) / (7 - charge_blocks_2)
baselines_2 = [2000] * charge_blocks_2 + [discharge_level_2] * 4
patterns_to_test.append(('Pattern 2: 3 charge đầu, 4 discharge cuối', baselines_2))

# Pattern 3: Charge đều
avg_baseline = sum_baseline / 7
baselines_3 = [avg_baseline] * 7
patterns_to_test.append(('Pattern 3: Phân bố đều', baselines_3))

# Pattern 4: 2 charge MAX, rest moderate
charge_blocks_4 = 2
moderate_level = (sum_baseline - charge_blocks_4 * 2000) / (7 - charge_blocks_4)
baselines_4 = [2000] * charge_blocks_4 + [moderate_level] * 5
patterns_to_test.append(('Pattern 4: 2 charge MAX, 5 moderate', baselines_4))

# Test all patterns
valid_patterns = []

for name, baselines in patterns_to_test:
    result = simulate_pattern(baselines, soc_start=5.0)
    
    print(f"{name}")
    print(f"  Baselines: {[f'{b:.0f}' for b in baselines]}")
    print(f"  Σ(基準値): {sum(baselines):.2f} kW")
    print(f"  SOC range: {result['min_soc']:.1f}% - {result['max_soc']:.1f}%")
    print(f"  Cycle error: {result['cycle_error']:+.2f}%")
    print(f"  Status: {'✅ Valid' if result['valid'] else '❌ Invalid'}")
    print()
    
    if result['valid']:
        valid_patterns.append({
            'name': name,
            'baselines': baselines,
            'result': result
        })

print("="*80)
print(f"✅ Tìm thấy {len(valid_patterns)} pattern hợp lệ")
print("="*80)

if valid_patterns:
    # Chọn pattern tốt nhất (nhiều charge MAX nhất)
    best = valid_patterns[0]
    
    print(f"\n🏆 PATTERN TỐT NHẤT: {best['name']}")
    print(f"\nChi tiết:")
    print(f"{'Block':<6} {'Time':<15} {'Baseline':<12} {'ΔSOC':<10} {'SOC':<12}")
    print("-" * 70)
    
    soc = 5.0
    for i, b in enumerate(best['baselines'], 1):
        time_start = (i - 1) * 3
        time_end = i * 3
        time_str = f"{time_start:02d}:00-{time_end:02d}:00"
        
        delta = calc_delta_soc(b, 3)
        soc_before = soc
        soc = soc + delta
        
        action = "Charge" if b > 0 else "Discharge"
        print(f"{i:<6} {time_str:<15} {b:>6.0f}kW       {delta:>+6.1f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")
    
    # JEPX
    soc_before = soc
    soc = soc + jepx_delta
    print(f"{8:<6} {'21:00-24:00':<15} {'JEPX 950kW':<12} {jepx_delta:>+6.1f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")
    
    print(f"\n{'='*70}")
    print(f"Tổng 基準値: {sum(best['baselines']):.2f} kW")
    print(f"JEPX discharge: 950kW")
    print(f"Grand Total: {sum(best['baselines']):.2f}kW (baseline) + 950kW (JEPX)")
    print(f"So với không JEPX: +{sum(best['baselines']) - 1665.38:.2f}kW")
    
    # Save
    schedule_data = []
    soc = 5.0
    for i, b in enumerate(best['baselines'], 1):
        time_start = (i - 1) * 3
        time_end = i * 3
        delta = calc_delta_soc(b, 3)
        schedule_data.append({
            'block': i,
            'time': f"{time_start:02d}:00-{time_end:02d}:00",
            'baseline_kw': b,
            'delta_soc': delta,
            'soc_start': soc,
            'soc_end': soc + delta
        })
        soc += delta
    
    # JEPX block
    schedule_data.append({
        'block': 8,
        'time': '21:00-24:00',
        'baseline_kw': 'JEPX -950',
        'delta_soc': jepx_delta,
        'soc_start': soc,
        'soc_end': soc + jepx_delta
    })
    
    df = pd.DataFrame(schedule_data)
    df.to_csv('optimal_jepx_schedule_valid.csv', index=False)
    print("\n✅ Đã lưu: optimal_jepx_schedule_valid.csv")

else:
    print("\n❌ KHÔNG TÌM THẤY pattern hợp lệ nào!")
    print("\nNguyên nhân có thể:")
    print("- SOC range quá hẹp (10-90%)")
    print("- Tổng baseline quá lớn (2615kW) so với capacity")
    print("- Cần điều chỉnh JEPX discharge hoặc target SOC")

print("\n✅ Hoàn tất!")
