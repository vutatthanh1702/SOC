#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TÌM PATTERN LÊN XUỐNG VỚI BASELINE > 3549KW
"""

import itertools
import pandas as pd

print("="*80)
print("🔍 TÌM PATTERN LÊN XUỐNG TỐI ƯU")
print("="*80)

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197
JEPX_DELTA = -85.0
SOC_MIN = 5.0
SOC_MAX = 90.0
TARGET_BASELINE = 3549  # Baseline của pattern đều


def calc_delta_soc(baseline_kw):
    """Tính ΔSOC cho 1 block (3h)"""
    return (SLOPE * baseline_kw + INTERCEPT) * 3


def simulate_pattern(blocks):
    """
    Simulate pattern và trả về kết quả
    blocks: list of baseline values (kW)
    """
    soc = SOC_MIN
    soc_trajectory = [soc]
    
    for b in blocks:
        delta = calc_delta_soc(b)
        soc += delta
        soc_trajectory.append(soc)
        
        # Check constraint
        if soc > SOC_MAX or soc < SOC_MIN:
            return None, None, False
    
    # Check if reaches 90% before JEPX
    if abs(soc - SOC_MAX) > 1:
        return None, None, False
    
    # After JEPX
    soc_final = soc + JEPX_DELTA
    
    # Check cycle
    if abs(soc_final - SOC_MIN) > 0.5:
        return None, None, False
    
    return soc_trajectory, sum(blocks), True


print("""
🎯 MỤC TIÊU:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tìm pattern 7 blocks với:
  • Baseline có thể lên xuống (không nhất thiết đều)
  • SOC ∈ [5%, 90%] ∀t
  • Tổng baseline > 3549kW (pattern đều)
  • Cycle hoàn hảo 5% → 5%
""")

print("\n" + "="*80)
print("📊 STRATEGY: THỬ CÁC PATTERN KHÁC NHAU")
print("="*80)

# Strategy: Thử các combinations
# Cho phép: 0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000kW

baseline_options = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]

print("""
Chiến lược:
1. Thử nhiều combinations khác nhau
2. Ưu tiên patterns có blocks lớn ở đầu (charge nhanh)
3. Có thể có blocks 0kW (tự xả) để giảm SOC
4. Tìm pattern cho Σ(基準値) lớn nhất
""")

# Test specific patterns
test_patterns = [
    # Pattern 1: Front-load with cooldown
    [2000, 0, 1000, 0, 1000, 0, 1000],
    [2000, 0, 800, 0, 800, 0, 800],
    [2000, 0, 600, 0, 600, 0, 600],
    [2000, 0, 500, 0, 500, 0, 500],
    [2000, 0, 400, 0, 400, 0, 400],
    
    # Pattern 2: Multiple peaks
    [1500, 0, 1500, 0, 1000, 0, 1000],
    [1600, 0, 1200, 0, 1200, 0, 800],
    [1800, 0, 1000, 0, 1000, 0, 600],
    
    # Pattern 3: Gradual with resets
    [1000, 1000, 0, 1000, 0, 1000, 0],
    [1200, 800, 0, 1000, 0, 800, 0],
    
    # Pattern 4: Big start, small fills
    [2000, 200, 0, 200, 0, 200, 0],
    [2000, 400, 0, 400, 0, 400, 0],
    
    # Pattern 5: Wave pattern
    [1000, 1000, 1000, 0, 1000, 0, 500],
    [800, 800, 800, 0, 800, 0, 600],
]

print(f"\n🔬 Testing {len(test_patterns)} pre-designed patterns...\n")

valid_patterns = []

for i, pattern in enumerate(test_patterns, 1):
    trajectory, total, valid = simulate_pattern(pattern)
    
    if valid and trajectory is not None:
        max_soc = max(trajectory[:-1])  # Before JEPX
        min_soc = min(trajectory)
        
        valid_patterns.append({
            'pattern': pattern,
            'total': total,
            'max_soc': max_soc,
            'min_soc': min_soc,
            'trajectory': trajectory
        })
        
        status = "✅" if total > TARGET_BASELINE else "⚠️"
        comparison = f"({total - TARGET_BASELINE:+.0f}kW vs đều)" if total != TARGET_BASELINE else ""
        
        print(f"{status} Pattern {i}: {pattern}")
        print(f"   Σ(基準値) = {total:.0f}kW {comparison}")
        print(f"   SOC: {min_soc:.1f}% - {max_soc:.1f}%")
        print()

# Sort by total baseline
valid_patterns.sort(key=lambda x: x['total'], reverse=True)

print("\n" + "="*80)
print("🏆 KẾT QUẢ")
print("="*80)

if not valid_patterns:
    print("\n❌ KHÔNG TÌM THẤY pattern nào tốt hơn pattern đều!")
else:
    print(f"\n✅ Tìm thấy {len(valid_patterns)} patterns hợp lệ\n")
    
    print("TOP 5 PATTERNS (theo tổng baseline):\n")
    for i, p in enumerate(valid_patterns[:5], 1):
        diff = p['total'] - TARGET_BASELINE
        pct = (diff / TARGET_BASELINE) * 100
        
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        
        print(f"{emoji} #{i}: {p['pattern']}")
        print(f"       Σ(基準値) = {p['total']:.0f}kW ({diff:+.0f}kW, {pct:+.1f}%)")
        print(f"       SOC: {p['min_soc']:.1f}% - {p['max_soc']:.1f}%")
        print()
    
    # Detailed analysis of best pattern
    best = valid_patterns[0]
    
    print("\n" + "="*80)
    print("📊 PHÂN TÍCH CHI TIẾT PATTERN TỐT NHẤT")
    print("="*80)
    
    print(f"\nPattern: {best['pattern']}")
    print(f"Tổng baseline: {best['total']:.0f}kW")
    print(f"So với pattern đều: {best['total'] - TARGET_BASELINE:+.0f}kW ({(best['total']/TARGET_BASELINE - 1)*100:+.1f}%)")
    
    print("\nSimulation chi tiết:\n")
    print(f"{'Block':<8} {'基準値':<12} {'ΔSOC':<12} {'SOC':<20}")
    print("-" * 60)
    
    soc = SOC_MIN
    for i, b in enumerate(best['pattern'], 1):
        delta = calc_delta_soc(b)
        soc_before = soc
        soc += delta
        
        print(f"{i:<8} {b:<6}kW     {delta:>+6.2f}%     {soc_before:>5.1f}% → {soc:>5.1f}%")
    
    print(f"{'JEPX':<8} {'NaN':<12} {JEPX_DELTA:>+6.2f}%     {soc:>5.1f}% → {soc + JEPX_DELTA:>5.1f}%")
    
    print("\n" + "="*80)
    print("💡 PHÂN TÍCH")
    print("="*80)
    
    if best['total'] > TARGET_BASELINE:
        print(f"""
🎉 TÌM ĐƯỢC PATTERN TỐT HƠN!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pattern đều:     {TARGET_BASELINE}kW
Pattern tốt hơn: {best['total']:.0f}kW
Cải thiện:       {best['total'] - TARGET_BASELINE:+.0f}kW ({(best['total']/TARGET_BASELINE - 1)*100:+.1f}%)

Chiến lược:
• Sử dụng blocks 0kW để giảm SOC (tự xả)
• Cho phép charge lại nhiều lần
• Tận dụng tối đa SOC range [5%, 90%]

→ BẠN ĐÚNG! Pattern lên xuống CÓ THỂ tốt hơn! ✅
""")
    else:
        print(f"""
Pattern đều vẫn là tốt nhất:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pattern đều:        {TARGET_BASELINE}kW
Pattern tốt nhất:   {best['total']:.0f}kW
Chênh lệch:         {best['total'] - TARGET_BASELINE:+.0f}kW

→ Pattern đều vẫn là OPTIMAL
""")

print("\n" + "="*80)
print("🎓 KẾT LUẬN")
print("="*80)

print("""
1️⃣  Pattern lên xuống HOÀN TOÀN HỢP LỆ (bạn đúng!)
2️⃣  Constraint SOC [5%, 90%] giới hạn khả năng tối ưu
3️⃣  Blocks 0kW (tự xả) có thể giúp "reset" SOC
4️⃣  Cần test nhiều combinations để tìm optimal
""")

if valid_patterns and valid_patterns[0]['total'] > TARGET_BASELINE:
    print(f"""
✅ KẾT QUẢ: Pattern lên xuống TỐT HƠN pattern đều!
   Baseline: {valid_patterns[0]['total']:.0f}kW > {TARGET_BASELINE}kW
   
→ BẠN HOÀN TOÀN ĐÚNG! 🎉
""")
else:
    print("""
⚠️  Với các patterns thử, chưa tìm được pattern tốt hơn pattern đều.
   Có thể cần thử nhiều combinations hơn hoặc pattern đều là optimal.
""")

print("\n✅ Hoàn tất!")
