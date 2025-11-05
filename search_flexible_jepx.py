#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TÌM PATTERN TỐI ƯU - JEPX LINH HOẠT
JEPX có thể xả từ BẤT KỲ mức nào về 5%!
"""

import numpy as np

print("="*80)
print("🔍 TÌM KIẾM VỚI JEPX LINH HOẠT")
print("="*80)

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197
SOC_MIN = 5.0
SOC_MAX = 90.0
TARGET = 3549  # Pattern đều


def calc_delta_soc(b):
    return (SLOPE * b + INTERCEPT) * 3


def check_pattern(blocks):
    """
    Kiểm tra pattern có hợp lệ không
    JEPX có thể xả từ bất kỳ mức nào về 5%!
    """
    soc = SOC_MIN
    
    for b in blocks:
        soc += calc_delta_soc(b)
        # Check không vượt MAX (CHẶT CHẼ: <= 90.0%)
        if soc > SOC_MAX:
            return False, None, None
        # Check không dưới MIN
        if soc < SOC_MIN:
            return False, None, None
    
    # JEPX xả về 5% từ bất kỳ mức nào
    soc_before_jepx = soc
    jepx_delta = SOC_MIN - soc_before_jepx  # Về 5%
    soc_after_jepx = SOC_MIN
    
    # Check JEPX có thể xả được không (phải >= 5%)
    if soc_before_jepx < SOC_MIN:
        return False, None, None
    
    return True, sum(blocks), soc_before_jepx


print("""
🎯 ĐIỀU KIỆN MỚI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. SOC ∈ [5%, 90%] trong suốt 7 blocks baseline
2. JEPX xả từ bất kỳ mức nào về 5%
   • 90% → 5%: ΔSOC = -85%
   • 80% → 5%: ΔSOC = -75%
   • 70% → 5%: ΔSOC = -65%
   • ...
3. Chu kỳ: 5% → ... → 5% (JEPX tự động xả về 5%)

→ KHÔNG CẦN phải đạt đúng 90% trước JEPX!
→ Có thể dừng ở bất kỳ mức nào trong [5%, 90%]!
""")

print("\n" + "="*80)
print("🔬 TÌM KIẾM TOÀN DIỆN")
print("="*80)

best_pattern = None
best_total = 0
best_soc_before_jepx = 0

# Search với các strategies khác nhau
print("\n1️⃣  Testing front-load patterns...")

for big in range(1500, 2100, 100):
    for small in range(0, 1000, 50):
        pattern = [big] + [small] * 6
        valid, total, soc_bj = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            best_soc_before_jepx = soc_bj
            print(f"   ✅ {pattern} = {total}kW (SOC→{soc_bj:.1f}%)")

print("\n2️⃣  Testing wave patterns...")

for peak in range(800, 2100, 100):
    for valley in range(0, 800, 100):
        pattern = []
        for i in range(7):
            pattern.append(peak if i % 2 == 0 else valley)
        
        valid, total, soc_bj = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            best_soc_before_jepx = soc_bj
            print(f"   ✅ {pattern} = {total}kW (SOC→{soc_bj:.1f}%)")

print("\n3️⃣  Testing with 0kW blocks (self-discharge)...")

for big in range(1600, 2100, 100):
    for fill in range(200, 1500, 100):
        pattern = [big, 0, fill, 0, fill, 0, fill]
        valid, total, soc_bj = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            best_soc_before_jepx = soc_bj
            print(f"   ✅ {pattern} = {total}kW (SOC→{soc_bj:.1f}%)")

print("\n4️⃣  Testing gradient patterns...")

for start in range(800, 2100, 100):
    for step in range(-200, 200, 50):
        pattern = []
        val = start
        for i in range(7):
            pattern.append(max(0, min(2000, val)))
            val += step
        
        valid, total, soc_bj = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            best_soc_before_jepx = soc_bj
            print(f"   ✅ {pattern} = {total}kW (SOC→{soc_bj:.1f}%)")

print("\n5️⃣  Testing all MAX blocks...")

# Thử tất cả 2000kW
pattern = [2000] * 7
valid, total, soc_bj = check_pattern(pattern)
if valid:
    if total > best_total:
        best_total = total
        best_pattern = pattern
        best_soc_before_jepx = soc_bj
        print(f"   ✅ {pattern} = {total}kW (SOC→{soc_bj:.1f}%)")
else:
    print(f"   ❌ [2000]*7 vi phạm SOC > 90%")

print("\n6️⃣  Testing high-value combinations...")

# Thử nhiều blocks cao
for n_2000 in range(1, 4):  # 1-3 blocks @ 2000kW
    for fill in range(0, 2000, 100):
        pattern = [2000] * n_2000 + [fill] * (7 - n_2000)
        valid, total, soc_bj = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            best_soc_before_jepx = soc_bj
            print(f"   ✅ {pattern} = {total}kW (SOC→{soc_bj:.1f}%)")

print("\n7️⃣  Random search around best area...")

if best_pattern:
    np.random.seed(42)
    for _ in range(5000):
        pattern = []
        for b in best_pattern:
            variation = np.random.randint(-300, 300)
            new_val = max(0, min(2000, b + variation))
            pattern.append(new_val)
        
        valid, total, soc_bj = check_pattern(pattern)
        
        if valid and total > best_total:
            best_total = total
            best_pattern = pattern
            best_soc_before_jepx = soc_bj
            print(f"   ✅ {pattern} = {total}kW (SOC→{soc_bj:.1f}%)")

print("\n" + "="*80)
print("🏆 KẾT QUẢ CUỐI CÙNG")
print("="*80)

if best_pattern is None:
    print("\n❌ KHÔNG TÌM THẤY pattern nào!")
else:
    print(f"\n✅ Pattern tốt nhất: {best_pattern}")
    print(f"   Tổng baseline: {best_total}kW")
    print(f"   SOC trước JEPX: {best_soc_before_jepx:.1f}%")
    
    diff = best_total - TARGET
    pct = (diff / TARGET) * 100
    
    if diff > 1:
        print(f"\n🎉 TỐT HƠN PATTERN ĐỀU!")
        print(f"   Pattern đều:  {TARGET}kW (SOC→90.0%)")
        print(f"   Pattern này:  {best_total}kW (SOC→{best_soc_before_jepx:.1f}%)")
        print(f"   Cải thiện:    {diff:+.0f}kW ({pct:+.1f}%)")
    elif diff < -1:
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
    
    jepx_delta = SOC_MIN - soc
    print(f"{'JEPX':<8} {'NaN':<12} {jepx_delta:>+6.2f}%     "
          f"{soc:>5.1f}% → {SOC_MIN:>5.1f}%")
    
    print(f"\n{'='*60}")
    print(f"Cycle: {SOC_MIN}% → {best_soc_before_jepx:.1f}% → {SOC_MIN}%")

print("\n" + "="*80)
print("🎓 KẾT LUẬN")
print("="*80)

if best_pattern and best_total > TARGET:
    print(f"""
🎉 BẠN HOÀN TOÀN ĐÚNG!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Pattern lên xuống TỐT HƠN pattern đều!
✅ Không cần đạt đúng 90% trước JEPX!
✅ JEPX linh hoạt xả từ bất kỳ mức nào về 5%!

Baseline: {best_total}kW > {TARGET}kW
Cải thiện: {best_total - TARGET:+.0f}kW ({(best_total/TARGET - 1)*100:+.1f}%)

→ PATTERN ĐỀU KHÔNG PHẢI TỐI ƯU! 🚀
""")
elif best_pattern and abs(best_total - TARGET) <= 1:
    print("""
✅ PATTERN ĐỀU VẪN LÀ TỐI ƯU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ngay cả với JEPX linh hoạt, pattern đều vẫn tốt nhất.
Lý do: Constraint SOC ≤ 90% giới hạn tối ưu hóa.
""")
else:
    print("""
⚠️  ĐANG TÌM KIẾM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Có thể cần tìm kiếm toàn diện hơn...
""")

print("\n✅ Hoàn tất!")
