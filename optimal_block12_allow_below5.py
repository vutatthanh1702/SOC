"""
BÀI TOÁN MỚI: Block 1,2 KHÔNG CÓ BASELINE, được phép SOC < 5%
Chỉ Block 3-7 có constraint SOC ≥ 5%

Ràng buộc:
  • Block 1,2: baseline = 0, CHO PHÉP SOC < 5%
  • Block 3,4,5,6,7: có baseline, SOC ≥ 5%
  • Tất cả blocks: SOC ≤ 90%
  • SOC bắt đầu = 5%, kết thúc trước JEPX = 90%
"""

import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt

# ===== CÔNG THỨC CƠ BẢN =====
def calc_delta_soc(baseline):
    """ΔSOC cho 1 block 3h"""
    return 0.040635 * baseline - 8.4591


SOC_MIN = 5.0
SOC_MAX = 90.0
BASELINE_MAX = 2000

print("=" * 80)
print("BÀI TOÁN: Block 1,2 không có baseline, ĐƯỢC PHÉP SOC < 5%")
print("=" * 80)

print("\n📋 ĐIỀU KIỆN MỚI:")
print("  • Block 1,2 (0-6h): baseline = 0, CHO PHÉP SOC < 5%")
print("  • Block 3-7 (6-21h): có baseline, PHẢI SOC ≥ 5%")
print("  • Tất cả: SOC ≤ 90%")
print("  • Block 8 (21-24h): JEPX discharge 90% → 5%")

# ===== PHÂN TÍCH SƠ BỘ =====
print("\n" + "=" * 80)
print("PHÂN TÍCH SƠ BỘ")
print("=" * 80)

print("\n📊 Block 1,2 (baseline = 0):")
delta_block12 = calc_delta_soc(0)
print(f"  ΔSOC per block = {delta_block12:+.4f}%")
print(f"  ΔSOC cho 2 blocks = {2 * delta_block12:+.4f}%")

soc_after_block2 = SOC_MIN + 2 * delta_block12
print(f"\n  SOC trajectory:")
print(f"    Start (Block 0):  {SOC_MIN:.2f}%")
print(f"    After Block 1:    {SOC_MIN + delta_block12:.2f}%")
print(f"    After Block 2:    {soc_after_block2:.2f}%")

if soc_after_block2 < SOC_MIN:
    print(f"\n  ⚠️ SOC < {SOC_MIN}% trong Block 1,2 (ĐƯỢC PHÉP)")
    print(f"  📌 Block 3 phải kéo SOC lên ≥ {SOC_MIN}%")
else:
    print(f"\n  ✅ SOC vẫn ≥ {SOC_MIN}%")

# ===== TÍNH TOÁN YÊU CẦU =====
print("\n" + "=" * 80)
print("TÍNH TOÁN YÊU CẦU CHO 5 BLOCKS (3-7)")
print("=" * 80)

print(f"\n🎯 Mục tiêu:")
print(f"  SOC sau Block 2:  {soc_after_block2:.2f}%")
print(f"  SOC sau Block 7:  {SOC_MAX:.1f}%")
print(f"  ⟹ Cần tăng:       {SOC_MAX - soc_after_block2:.2f}%")

required_delta = SOC_MAX - soc_after_block2
print(f"\n📐 Constraint cho 5 blocks (3-7):")
print(f"  Σ ΔSOC(b₃,...,b₇) = {required_delta:.4f}%")
print(f"  Σ (0.040635×bᵢ - 8.4591) = {required_delta:.4f}%")
print(f"  0.040635 × Σbᵢ = {required_delta + 5*8.4591:.4f}%")

required_sum = (required_delta + 5*8.4591) / 0.040635
print(f"\n✅ CONSTRAINT: Σ(b₃,...,b₇) = {required_sum:.2f} kW")

# ===== PHƯƠNG PHÁP 1: LINEAR PROGRAMMING =====
print("\n" + "=" * 80)
print("PHƯƠNG PHÁP 1: LINEAR PROGRAMMING")
print("=" * 80)

# Biến: b₃, b₄, b₅, b₆, b₇ (5 biến)
c = -np.ones(5)

# Ràng buộc bất đẳng thức
A_ub = []
b_ub = []

# Ràng buộc: SOC(k) ≤ 90 cho k=3,4,5,6,7
# SOC(k) = soc_after_block2 + Σⱼ₌₃ᵏ (0.040635×bⱼ - 8.4591)
for k_idx in range(5):  # k = 3,4,5,6,7
    row = np.zeros(5)
    row[:k_idx+1] = 0.040635
    # soc_after_block2 + 0.040635×Σbⱼ - (k_idx+1)×8.4591 ≤ 90
    A_ub.append(row)
    b_ub.append(SOC_MAX - soc_after_block2 + (k_idx+1)*8.4591)

# Ràng buộc: SOC(k) ≥ 5 cho k=3,4,5,6,7
for k_idx in range(5):
    row = np.zeros(5)
    row[:k_idx+1] = -0.040635
    # soc_after_block2 + 0.040635×Σbⱼ - (k_idx+1)×8.4591 ≥ 5
    A_ub.append(row)
    b_ub.append(soc_after_block2 - SOC_MIN - (k_idx+1)*8.4591)

A_ub = np.array(A_ub)
b_ub = np.array(b_ub)

# Ràng buộc đẳng thức: SOC(7) = 90
A_eq = np.array([[0.040635] * 5])
b_eq = np.array([required_delta + 5*8.4591])

# Giới hạn: 0 ≤ bᵢ ≤ 2000
bounds = [(0, BASELINE_MAX)] * 5

print("\n🔧 Giải bài toán LP...")
result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                 bounds=bounds, method='highs')

if result.success:
    print("\n✅ TÌM RA NGHIỆM TỐI ƯU!")
    
    optimal_pattern = result.x
    total_baseline = sum(optimal_pattern)
    
    print(f"\n🎯 Pattern tối ưu (Blocks 3-7):")
    for i, b in enumerate(optimal_pattern, 3):
        print(f"  Block {i}: {b:7.2f} kW")
    
    print(f"\n📊 Tổng baseline (5 blocks): {total_baseline:.2f} kW")
    
    # So sánh
    print(f"\n📊 SO SÁNH:")
    print(f"  • 7 blocks (tất cả):     7 × 507 = 3,549 kW")
    print(f"  • 5 blocks (3-7 only):   {total_baseline:.0f} kW")
    print(f"  • Chênh lệch:            {total_baseline - 3549:.0f} kW")
    if total_baseline < 3549:
        print(f"  • Giảm:                  {(1 - total_baseline/3549)*100:.1f}%")
    else:
        print(f"  • Tăng:                  {(total_baseline/3549 - 1)*100:.1f}%")
    
    # SOC trajectory chi tiết
    print(f"\n📈 SOC TRAJECTORY CHI TIẾT:")
    print("-" * 80)
    
    soc = SOC_MIN
    print(f"  Start (0h):              {soc:6.2f}%  ✅")
    
    # Block 1, 2: baseline = 0, cho phép < 5%
    for i in [1, 2]:
        delta = calc_delta_soc(0)
        soc += delta
        # Chỉ check upper bound
        if soc <= SOC_MAX:
            status = "✅ (< 5% OK)"
        else:
            status = "❌ (> 90%)"
        print(f"  After Block {i} ({i*3:2d}h):     {soc:6.2f}%  "
              f"(ΔSOC={delta:+6.2f}%, b=0kW) {status}")
    
    # Block 3-7: có baseline, phải ≥ 5%
    for i, b in enumerate(optimal_pattern, 3):
        delta = calc_delta_soc(b)
        soc += delta
        if SOC_MIN <= soc <= SOC_MAX:
            status = "✅"
        elif soc < SOC_MIN:
            status = "❌ (< 5%)"
        else:
            status = "❌ (> 90%)"
        print(f"  After Block {i} ({i*3:2d}h):     {soc:6.2f}%  "
              f"(ΔSOC={delta:+6.2f}%, b={b:4.0f}kW) {status}")
    
    # JEPX
    jepx_delta = SOC_MIN - soc
    print(f"  JEPX (21-24h):            {SOC_MIN:6.2f}%  "
          f"(ΔSOC={jepx_delta:+6.2f}%)")
    
    # Phân tích pattern
    print(f"\n🔍 PHÂN TÍCH PATTERN (5 blocks):")
    std = np.std(optimal_pattern)
    mean = np.mean(optimal_pattern)
    print(f"  Mean (trung bình):       {mean:.2f} kW")
    print(f"  Std (độ lệch chuẩn):     {std:.4f} kW")
    
    if std < 0.01:
        print(f"  ✅ Pattern ĐỀU: tất cả ≈ {mean:.2f} kW")
    else:
        print(f"  ⚠️ Pattern KHÔNG ĐỀU")
        print(f"  Min:  {min(optimal_pattern):.2f} kW")
        print(f"  Max:  {max(optimal_pattern):.2f} kW")
        print(f"  Range: {max(optimal_pattern) - min(optimal_pattern):.2f} kW")

else:
    print(f"\n❌ Không tìm được nghiệm: {result.message}")

# ===== PHƯƠNG PHÁP 2: GIẢI TÍCH =====
print("\n" + "=" * 80)
print("PHƯƠNG PHÁP 2: GIẢI TÍCH")
print("=" * 80)

print("\n📐 Phân tích:")
print("  • Objective: Maximize Σbᵢ (tuyến tính)")
print("  • Constraint: 0.040635×Σbᵢ = const (tuyến tính)")
print("  • Hệ số GIỐNG NHAU cho mọi bᵢ")
print("  ⟹ Nghiệm đều: b₃ = b₄ = b₅ = b₆ = b₇")

uniform_b = required_sum / 5
print(f"\n🧮 Tính toán:")
print(f"  Σ(b₃,...,b₇) = {required_sum:.2f} kW")
print(f"  ⟹ b = {required_sum:.2f} / 5 = {uniform_b:.2f} kW")

print(f"\n✅ PATTERN TỐI ƯU (GIẢI TÍCH):")
print(f"   5 blocks × {uniform_b:.2f} kW = {5 * uniform_b:.0f} kW")

# Verify SOC trajectory với pattern đều
print(f"\n🔍 Xác minh SOC trajectory với pattern đều:")
soc = SOC_MIN
print(f"  Block 0:  SOC = {soc:.2f}%")

for i in [1, 2]:
    delta = calc_delta_soc(0)
    soc += delta
    print(f"  Block {i}:  SOC = {soc:.2f}% (b=0kW, ΔSOC={delta:+.2f}%)")

for i in range(3, 8):
    delta = calc_delta_soc(uniform_b)
    soc += delta
    print(f"  Block {i}:  SOC = {soc:.2f}% (b={uniform_b:.0f}kW, ΔSOC={delta:+.2f}%)")

# ===== VISUALIZATION =====
print("\n" + "=" * 80)
print("MINH HỌA")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Baseline comparison
ax1 = axes[0, 0]
blocks_all = np.arange(1, 8)
baseline_7blocks = [507] * 7
baseline_5blocks = [0, 0] + [uniform_b] * 5

colors = ['red', 'red', 'green', 'green', 'green', 'green', 'green']
bars = ax1.bar(blocks_all, baseline_5blocks, color=colors, alpha=0.7,
               edgecolor='black', linewidth=2)

# Annotate
ax1.text(1.5, 50, 'NO\nBASELINE', ha='center', fontsize=12,
         fontweight='bold', color='darkred')
ax1.axhline(y=507, color='blue', linestyle='--', linewidth=2, alpha=0.5,
            label='7-blocks case: 507kW each')
ax1.axhline(y=uniform_b, color='green', linestyle='--', linewidth=2,
            alpha=0.5, label=f'5-blocks case: {uniform_b:.0f}kW each')

ax1.set_xlabel('Block number', fontsize=12)
ax1.set_ylabel('Baseline (kW)', fontsize=12)
ax1.set_title('Baseline Distribution - Blocks 1,2 excluded', fontsize=14,
              fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, axis='y', alpha=0.3)
ax1.set_xticks(blocks_all)
ax1.set_ylim(0, 1000)

# Plot 2: SOC trajectory - 7 blocks
ax2 = axes[0, 1]
soc_7blocks = [5.0]
soc = 5.0
for b in [507] * 7:
    soc += calc_delta_soc(b)
    soc_7blocks.append(soc)

blocks_range = list(range(0, 8))
ax2.plot(blocks_range, soc_7blocks, 'go-', linewidth=3, markersize=10,
         label='7 blocks (all @ 507kW)')
ax2.axhline(y=90, color='r', linestyle='--', linewidth=2, alpha=0.5,
            label='SOC max = 90%')
ax2.axhline(y=5, color='b', linestyle='--', linewidth=2, alpha=0.5,
            label='SOC min = 5%')
ax2.fill_between(blocks_range, 5, 90, alpha=0.1, color='gray')

ax2.set_xlabel('Block number', fontsize=12)
ax2.set_ylabel('SOC (%)', fontsize=12)
ax2.set_title('SOC Trajectory - 7 blocks (baseline)', fontsize=14,
              fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)
ax2.set_xlim(0, 7)
ax2.set_ylim(0, 100)

# Plot 3: SOC trajectory - 5 blocks (allow < 5% for blocks 1,2)
ax3 = axes[1, 0]
soc_5blocks = [5.0]
soc = 5.0

# Block 1, 2: baseline = 0
for _ in [1, 2]:
    soc += calc_delta_soc(0)
    soc_5blocks.append(soc)

# Block 3-7: baseline = uniform_b
for _ in range(5):
    soc += calc_delta_soc(uniform_b)
    soc_5blocks.append(soc)

blocks_all_range = list(range(0, 8))

# Plot with different colors for different regions
ax3.plot([0, 1, 2], soc_5blocks[0:3], 'ro-', linewidth=3, markersize=10,
         label=f'Blocks 1-2: 0kW (allow < 5%)', zorder=3)
ax3.plot(list(range(2, 8)), soc_5blocks[2:], 'go-', linewidth=3, markersize=10,
         label=f'Blocks 3-7: {uniform_b:.0f}kW each', zorder=3)

ax3.axhline(y=90, color='r', linestyle='--', linewidth=2, alpha=0.5)
ax3.axhline(y=5, color='b', linestyle='--', linewidth=2, alpha=0.5)

# Highlight region where SOC < 5% is allowed
ax3.axvspan(0, 2, alpha=0.1, color='red', label='SOC < 5% allowed')
ax3.fill_between([2, 7], 5, 90, alpha=0.1, color='gray', label='Must: 5% ≤ SOC ≤ 90%')

# Mark minimum SOC
min_soc = min(soc_5blocks)
min_idx = soc_5blocks.index(min_soc)
ax3.plot(min_idx, min_soc, 'r*', markersize=20, zorder=4)
ax3.text(min_idx + 0.3, min_soc, f'Min: {min_soc:.1f}%',
         fontsize=10, fontweight='bold', color='red')

ax3.set_xlabel('Block number', fontsize=12)
ax3.set_ylabel('SOC (%)', fontsize=12)
ax3.set_title('SOC Trajectory - 5 blocks (Blocks 1,2: no baseline, allow < 5%)',
              fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=9, loc='upper left')
ax3.set_xlim(0, 7)
ax3.set_ylim(-15, 100)

# Plot 4: Comparison summary
ax4 = axes[1, 1]
ax4.axis('off')

summary_text = f"""
📊 SUMMARY COMPARISON

┌─────────────────────────────────────────────────┐
│  7 BLOCKS (All participate)                    │
├─────────────────────────────────────────────────┤
│  Pattern:     7 × 507 kW                       │
│  Total:       3,549 kW                         │
│  SOC range:   5.0% → 90.0%                     │
│  All blocks:  ✅ SOC ≥ 5%                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  5 BLOCKS (Blocks 1,2 excluded)                │
├─────────────────────────────────────────────────┤
│  Blocks 1,2:  0 kW (no baseline)               │
│  Blocks 3-7:  5 × {uniform_b:.0f} kW                     │
│  Total:       {5*uniform_b:.0f} kW                         │
│  SOC range:   {min(soc_5blocks):.1f}% → 90.0%                   │
│  Blocks 1,2:  ⚠️ SOC < 5% (ALLOWED)             │
│  Blocks 3-7:  ✅ SOC ≥ 5%                      │
└─────────────────────────────────────────────────┘

📈 KEY INSIGHTS:
  • Total baseline: {5*uniform_b:.0f} kW (SAME as 7-blocks!)
  • Each block (3-7): {uniform_b:.0f} kW vs 507kW (+{uniform_b-507:.0f}kW, +{(uniform_b/507-1)*100:.0f}%)
  • Blocks 1,2: SOC drops to {min(soc_5blocks):.1f}% (< 5% OK)
  • Constraint: Only blocks 3-7 need SOC ≥ 5%
  
💡 CONCLUSION:
  Removing blocks 1,2 doesn't reduce total capacity!
  But each remaining block must work harder (+{(uniform_b/507-1)*100:.0f}%)
"""

ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes,
         fontsize=11, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('optimal_block12_allow_below5.png', dpi=150, bbox_inches='tight')
print("\n💾 Saved: optimal_block12_allow_below5.png")

# ===== FINAL SUMMARY =====
print("\n" + "=" * 80)
print("KẾT LUẬN")
print("=" * 80)

print(f"\n✅ TRƯỜNG HỢP 7 BLOCKS (tất cả tham gia):")
print(f"   Pattern: 7 × 507 kW = 3,549 kW")
print(f"   SOC: 5.0% → 90.0% (tất cả blocks ≥ 5%)")

print(f"\n✅ TRƯỜNG HỢP 5 BLOCKS (Block 1,2 không có baseline):")
print(f"   Pattern: 5 × {uniform_b:.0f} kW = {5*uniform_b:.0f} kW")
print(f"   SOC: {min(soc_5blocks):.1f}% → 90.0%")
print(f"   Blocks 1,2: SOC < 5% (ĐƯỢC PHÉP)")
print(f"   Blocks 3-7: SOC ≥ 5% (✅)")

print(f"\n📊 SO SÁNH:")
print(f"   • Tổng baseline: {5*uniform_b:.0f} kW vs 3,549 kW → BẰNG NHAU!")
print(f"   • Mỗi block (3-7): {uniform_b:.0f}kW vs 507kW → tăng {uniform_b-507:.0f}kW (+{(uniform_b/507-1)*100:.0f}%)")
print(f"   • SOC min: {min(soc_5blocks):.1f}% vs 5.0% → giảm {5.0 - min(soc_5blocks):.1f}%")

print(f"\n💡 INSIGHT QUAN TRỌNG:")
print(f"   ✅ Tổng baseline KHÔNG ĐỔI: 3,549 kW")
print(f"      Lý do: JEPX vẫn -85%, nên Σ(ΔSOC_baseline) = +85%")
print(f"   ")
print(f"   ⚠️ Mỗi block phải làm việc nặng hơn:")
print(f"      5 blocks phải gánh công việc của 7 blocks")
print(f"      {uniform_b:.0f}kW thay vì 507kW (+{(uniform_b/507-1)*100:.0f}%)")
print(f"   ")
print(f"   ⚠️ SOC giảm xuống {min(soc_5blocks):.1f}% trong Blocks 1,2:")
print(f"      Nhưng ĐƯỢC PHÉP theo constraint mới")

print("\n🏆 HOÀN THÀNH!")
print("=" * 80)
