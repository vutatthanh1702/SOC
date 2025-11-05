#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TÌM PATTERN TỐI ƯU BẰNG SEARCH TOÀN DIỆN
"""

import numpy as np
from itertools import product

print("="*80)
print("🔍 TÌM KIẾM TOÀN DIỆN: PATTERN TỐI ƯU")
print("="*80)

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197
JEPX_DELTA = -85.0
SOC_MIN = 5.0
SOC_MAX = 90.0
TARGET = 3549


def calc_delta_soc(b):
    return (SLOPE * b + INTERCEPT) * 3


def check_pattern(blocks):
    """Kiểm tra pattern có hợp lệ không"""
    soc = SOC_MIN
    
    for b in blocks:
        soc += calc_delta_soc(b)
        if soc > SOC_MAX + 0.1 or soc < SOC_MIN - 0.1:
            return False, None
    
    # After JEPX - must return to 5%
    # JEPX can discharge from any level back to 5%
    soc_after_jepx = soc + JEPX_DELTA
    
    # Check cycle: must end at 5%
    if abs(soc_after_jepx - SOC_MIN) > 0.5:
        return False, None
    
    return True, sum(blocks)


print("""
🎯 CHIẾN LƯỢC TÌM KIẾM:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Thử tất cả combinations có thể
2. Baseline values: 0, 100, 200, ..., 2000 (step 100)
3. Tìm pattern cho Σ(基準値) MAX
4. Constraint: SOC ∈ [5%, 90%], cycle hoàn hảo
""")

# Simplified search: limit to reasonable values
baseline_values = list(range(0, 2100, 100))  # 0, 100, 200, ..., 2000

print(f"\nBaseline values: {baseline_values[0]} to {baseline_values[-1]} (step 100)")
print(f"Total combinations: {len(baseline_values)**7:,}")
print("\n⚠️  Quá nhiều! Sẽ dùng heuristic search...\n")

# Heuristic: Start with high values, then adjust
print("="*80)
print("🔬 HEURISTIC SEARCH")
print("="*80)

best_pattern = None
best_total = 0

# Strategy 1: Try patterns with front-loading
print("\n1️⃣  Testing front-load patterns (1 big block + smaller fills)...")

for big in range(1500, 2100, 100):
    for small in range(0, 1000, 100):
        # Pattern: [big, small, small, small, small, small, small]
        pattern = [big] + [small] * 6
        valid, total = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            print(f"   ✅ Found: {pattern} = {total}kW")

# Strategy 2: Try wave patterns
print("\n2️⃣  Testing wave patterns (up-down-up-down)...")

for peak in range(1000, 2100, 200):
    for valley in range(0, 600, 100):
        # Pattern: [peak, valley, peak, valley, peak, valley, peak]
        pattern = []
        for i in range(7):
            pattern.append(peak if i % 2 == 0 else valley)
        
        valid, total = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            print(f"   ✅ Found: {pattern} = {total}kW")

# Strategy 3: Try with 0kW blocks (self-discharge)
print("\n3️⃣  Testing patterns with 0kW blocks (self-discharge)...")

for big in range(1800, 2100, 100):
    for fill in range(400, 1200, 100):
        # Pattern: [big, 0, fill, 0, fill, 0, fill]
        pattern = [big, 0, fill, 0, fill, 0, fill]
        valid, total = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            print(f"   ✅ Found: {pattern} = {total}kW")

# Strategy 4: Try gradient patterns
print("\n4️⃣  Testing gradient patterns (decreasing or increasing)...")

for start in range(1000, 2100, 200):
    for step in range(-300, 300, 100):
        pattern = []
        val = start
        for i in range(7):
            pattern.append(max(0, min(2000, val)))
            val += step
        
        valid, total = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            print(f"   ✅ Found: {pattern} = {total}kW")

# Strategy 5: Random targeted search around promising areas
print("\n5️⃣  Testing random variations around best pattern...")

if best_pattern:
    np.random.seed(42)
    for _ in range(1000):
        # Create variation
        pattern = []
        for b in best_pattern:
            variation = np.random.randint(-200, 200, step=100)
            new_val = max(0, min(2000, b + variation))
            pattern.append(new_val)
        
        valid, total = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            print(f"   ✅ Found: {pattern} = {total}kW")

print("\n" + "="*80)
print("🏆 KẾT QUẢ CUỐI CÙNG")
print("="*80)

if best_pattern is None:
    print("\n❌ KHÔNG TÌM THẤY pattern nào!")
else:
    print(f"\n✅ Pattern tốt nhất: {best_pattern}")
    print(f"   Tổng baseline: {best_total}kW")
    
    diff = best_total - TARGET
    pct = (diff / TARGET) * 100
    
    if diff > 0:
        print(f"\n🎉 TỐT HƠN PATTERN ĐỀU!")
        print(f"   Pattern đều: {TARGET}kW")
        print(f"   Pattern này: {best_total}kW")
        print(f"   Cải thiện:   {diff:+.0f}kW ({pct:+.1f}%)")
    elif diff < 0:
        print(f"\n⚠️  KÉM HƠN pattern đều")
        print(f"   Pattern đều: {TARGET}kW")
        print(f"   Pattern này: {best_total}kW")
        print(f"   Chênh lệch:  {diff:+.0f}kW ({pct:+.1f}%)")
    else:
        print(f"\n✅ BẰNG pattern đều: {TARGET}kW")
    
    # Detailed simulation
    print("\n" + "="*80)
    print("📊 SIMULATION CHI TIẾT")
    print("="*80)
    
    print(f"\n{'Block':<8} {'基準値':<12} {'ΔSOC':<12} {'SOC':<20}")
    print("-" * 60)
    
    soc = SOC_MIN
    for i, b in enumerate(best_pattern, 1):
        delta = calc_delta_soc(b)
        soc_before = soc
        soc += delta
        
        print(f"{i:<8} {b:<6}kW     {delta:>+6.2f}%     "
              f"{soc_before:>5.1f}% → {soc:>5.1f}%")
    
    print(f"{'JEPX':<8} {'NaN':<12} {JEPX_DELTA:>+6.2f}%     "
          f"{soc:>5.1f}% → {soc + JEPX_DELTA:>5.1f}%")

print("\n" + "="*80)
print("🎓 KẾT LUẬN")
print("="*80)

if best_pattern and best_total > TARGET:
    print(f"""
✅ TÌM ĐƯỢC PATTERN TỐT HƠN!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ BẠN ĐÚNG! Pattern lên xuống CÓ THỂ tốt hơn pattern đều!
→ Constraint SOC [5%, 90%] không ngăn cản tối ưu hóa
→ Cần tìm kiếm kỹ lưỡng để tìm pattern tốt nhất
""")
elif best_pattern and best_total == TARGET:
    print("""
✅ PATTERN ĐỀU LÀ TỐI ƯU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Với constraints cho trước, pattern đều là tối ưu
→ Mọi pattern khác đều ≤ 3549kW
""")
else:
    print("""
⚠️  CẦN TÌM KIẾM TOÀN DIỆN HƠN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Có thể có pattern tốt hơn chưa được tìm thấy
→ Hoặc pattern đều thực sự là optimal
""")

print("\n✅ Hoàn tất!")
