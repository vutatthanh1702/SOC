#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHÂN TÍCH GIỚI HẠN: Tổng baseline MAX khitích khi có JEPX
"""

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197

SOC_MIN = 10
SOC_MAX = 90
SOC_RANGE = SOC_MAX - SOC_MIN  # 80%

print("="*80)
print("📊 PHÂN TÍCH GIỚI HẠN VẬT LÝ")
print("="*80)

def calc_delta(b):
    return (SLOPE * b + INTERCEPT) * 3

# JEPX effect
jepx_delta = calc_delta(-950)

print(f"\nJEPX discharge: ΔSOC = {jepx_delta:.2f}%")
print(f"SOC range available: {SOC_RANGE}%")

print("\n" + "="*80)
print("🔬 TÍNH GIỚI HẠN LÝ THUYẾT")
print("="*80)

print("""
Điều kiện để pattern hợp lệ:
1. Chu kỳ: Σ(ΔSOC_baseline) + ΔSOC_jepx = 0
2. Range: SOC_max - SOC_min ≤ 80%

Giả sử pattern TỐT NHẤT:
- Bắt đầu từ SOC_min (10%)
- Charge lên đến SOC_max (90%) → Gain = +80%
- JEPX discharge -47.06% → về 42.94%
- Các blocks còn lại phải đưa về 10%

Hãy tính:
""")

# Scenario: Start 10%, charge lên 90%, JEPX xuống, về lại 10%
soc_start = SOC_MIN  # 10%
soc_peak = SOC_MAX   # 90%

# Gain từ charge
delta_charge = soc_peak - soc_start  # 80%

# Sau JEPX
soc_after_jepx = soc_peak + jepx_delta  # 90% - 47.06% = 42.94%

# Cần về lại start
delta_remaining = soc_start - soc_after_jepx  # 10% - 42.94% = -32.94%

print(f"Scenario 1: Maximize charge")
print(f"  Start: {soc_start}%")
print(f"  Charge lên: {soc_peak}% (gain +{delta_charge}%)")
print(f"  JEPX discharge: {soc_peak}% → {soc_after_jepx:.2f}%")
print(f"  Cần về lại {soc_start}%: phải giảm {delta_remaining:.2f}%")
print()

# Tổng ΔSOC cần
total_delta_needed = delta_charge + delta_remaining

print(f"Tổng ΔSOC baseline cần: {delta_charge:.2f}% + ({delta_remaining:.2f}%) = {total_delta_needed:.2f}%")
print(f"So với JEPX effect (+{-jepx_delta:.2f}%): ", end="")

if abs(total_delta_needed - (-jepx_delta)) < 0.1:
    print("✅ MATCH!")
else:
    print(f"❌ MIS-MATCH (diff: {total_delta_needed - (-jepx_delta):.2f}%)")

print("\n" + "="*80)
print("🔍 TÍNH TỔNG BASELINE VỚI PATTERN THỰC TẾ")
print("="*80)

print("""
Pattern có thể:
- N blocks charge @ 2000kW → +72.8% mỗi block
- M blocks discharge @ X kW → ΔSOC mỗi block

Constraint:
- N × 72.8% ≤ 80% (không vượt range)
  → N ≤ 1.1 → N_max = 1 block!
  
Vậy CHỈ ĐƯỢC 1 block @ 2000kW!
""")

# Với 1 block @ 2000kW
n_max_blocks = 1
delta_from_max = n_max_blocks * calc_delta(2000)

print(f"Với {n_max_blocks} block @ 2000kW:")
print(f"  ΔSOC = +{delta_from_max:.2f}%")
print()

# Còn 6 blocks
remaining_blocks = 6
# Cần: n_max × 72.8% + 6 × ΔX + JEPX = 0
# → 6 × ΔX = -(72.8% + JEPX)
# → 6 × ΔX = -(72.8% - 47.06%) = -25.74%
# → ΔX = -4.29% per block

delta_x_needed = -(delta_from_max + jepx_delta) / remaining_blocks

print(f"6 blocks còn lại cần:")
print(f"  Total ΔSOC = -({delta_from_max:.2f}% + {jepx_delta:.2f}%) = {-(delta_from_max + jepx_delta):.2f}%")
print(f"  ΔSOC per block = {delta_x_needed:.2f}%")
print()

# Tính baseline tương ứng
# ΔSOC = (SLOPE × b + INTERCEPT) × 3
# → b = (ΔSOC / 3 - INTERCEPT) / SLOPE

baseline_x = (delta_x_needed / 3 - INTERCEPT) / SLOPE

print(f"Baseline tương ứng:")
print(f"  X = ({delta_x_needed:.2f}/3 - {INTERCEPT}) / {SLOPE}")
print(f"  X = {baseline_x:.2f} kW")
print()

# Tổng baseline
total_baseline = n_max_blocks * 2000 + remaining_blocks * baseline_x

print(f"Tổng 基準値:")
print(f"  {n_max_blocks} × 2000 + {remaining_blocks} × {baseline_x:.2f}")
print(f"  = {total_baseline:.2f} kW")
print()

print(f"So sánh:")
print(f"  Không có JEPX: 1665.38 kW")
print(f"  Có JEPX (1 block MAX): {total_baseline:.2f} kW")
print(f"  Chênh lệch: {total_baseline - 1665.38:+.2f} kW ({(total_baseline/1665.38 - 1)*100:+.1f}%)")

print("\n" + "="*80)
print("🎯 PATTERN KHẢ THI DUY NHẤT")
print("="*80)

# Simulate
print(f"\nSimulation với SOC_start = {SOC_MIN}%:")
print(f"{'Block':<6} {'Time':<15} {'Baseline':<12} {'ΔSOC':<10} {'SOC':<20}")
print("-" * 70)

soc = float(SOC_MIN)

# 1 block charge MAX
time_str = "00:00-03:00"
delta = calc_delta(2000)
soc_before = soc
soc += delta
print(f"{1:<6} {time_str:<15} {2000:>6}kW       {delta:>+6.2f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")

# 6 blocks @ X
for i in range(6):
    block_num = i + 2
    time_start = block_num * 3 - 3
    time_end = block_num * 3
    time_str = f"{time_start:02d}:00-{time_end:02d}:00"
    
    delta = calc_delta(baseline_x)
    soc_before = soc
    soc += delta
    print(f"{block_num:<6} {time_str:<15} {baseline_x:>6.2f}kW       {delta:>+6.2f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")

# JEPX
time_str = "21:00-24:00"
soc_before = soc
soc += jepx_delta
print(f"{8:<6} {time_str:<15} {'JEPX 950kW':<12} {jepx_delta:>+6.2f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")

print(f"\n{'='*70}")
print(f"Tổng 基準値: {total_baseline:.2f} kW")
print(f"SOC range: {SOC_MIN}% - {SOC_MIN + delta_from_max:.2f}%")
print(f"Cycle error: {soc - SOC_MIN:.4f}%")

if soc < SOC_MIN or (SOC_MIN + delta_from_max) > SOC_MAX:
    print("❌ Pattern KHÔNG hợp lệ (vượt range)")
else:
    print("✅ Pattern HỢP LỆ!")

print("\n" + "="*80)
print("💡 KẾT LUẬN")
print("="*80)

print(f"""
1. Với JEPX discharge (-47.06%) và SOC range [10%, 90%]:
   → CHỈ CÓ THỂ dùng TỐI ĐA {n_max_blocks} block @ 2000kW
   
2. Tổng 基準値 tối đa đạt được:
   → {total_baseline:.2f} kW
   → Tăng {total_baseline - 1665.38:.2f}kW so với không JEPX
   → Tăng {(total_baseline/1665.38 - 1)*100:.1f}%
   
3. KHÔNG THỂ đạt được 2615kW như tính toán lý thuyết
   → Vì bị giới hạn bởi SOC range (80%)
   
4. Để tăng thêm, cần:
   - Mở rộng SOC range (ví dụ 5%-95%)
   - Giảm JEPX discharge power
   - Hoặc chấp nhận không cycle hoàn hảo
""")

print("\n✅ Hoàn tất!")
