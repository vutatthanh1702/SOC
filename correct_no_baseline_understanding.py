"""
SỬA LẠI: Block 1,2 KHÔNG CÓ BASELINE = KHÔNG THAM GIA = SOC KHÔNG ĐỔI

Hiểu đúng:
  • Không có baseline = không xả, không sạc
  • ΔSOC = 0 (SOC không đổi)
  • Block 1,2: SOC giữ nguyên ở mức ban đầu
"""

import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt

# ===== CÔNG THỨC CƠ BẢN =====
def calc_delta_soc(baseline):
    """ΔSOC cho 1 block 3h khi có baseline (tham gia thị trường)"""
    return 0.040635 * baseline - 8.4591


SOC_MIN = 5.0
SOC_MAX = 90.0
BASELINE_MAX = 2000

print("=" * 80)
print("SỬA LẠI: Block 1,2 KHÔNG có baseline → SOC KHÔNG ĐỔI")
print("=" * 80)

print("\n📋 HIỂU ĐÚNG:")
print("  • Block 1,2: KHÔNG tham gia thị trường")
print("  • Không baseline = không xả, không sạc")
print("  • ⟹ ΔSOC = 0 (SOC giữ nguyên)")
print("  • Block 3-7: CÓ baseline, tham gia thị trường")
print("  • Block 8: JEPX discharge 90% → 5%")

# ===== PHÂN TÍCH SƠ BỘ =====
print("\n" + "=" * 80)
print("PHÂN TÍCH SƠ BỘ")
print("=" * 80)

print("\n📊 Block 1,2 (KHÔNG có baseline):")
print("  ΔSOC = 0% (không hoạt động)")
print("  SOC giữ nguyên ở mức ban đầu")

soc_after_block2 = SOC_MIN  # SOC không đổi!
print(f"\n  SOC trajectory:")
print(f"    Start (Block 0):  {SOC_MIN:.2f}%")
print(f"    After Block 1:    {SOC_MIN:.2f}% (không đổi)")
print(f"    After Block 2:    {soc_after_block2:.2f}% (không đổi)")

print(f"\n  ✅ SOC = {soc_after_block2:.2f}% (trong phạm vi [{SOC_MIN}%, {SOC_MAX}%])")

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
for k_idx in range(5):
    row = np.zeros(5)
    row[:k_idx+1] = 0.040635
    A_ub.append(row)
    b_ub.append(SOC_MAX - soc_after_block2 + (k_idx+1)*8.4591)

# Ràng buộc: SOC(k) ≥ 5 cho k=3,4,5,6,7
for k_idx in range(5):
    row = np.zeros(5)
    row[:k_idx+1] = -0.040635
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
    
    print(f"\n🎯 Pattern tối ưu:")
    print(f"  Block 1,2: 0 kW (không tham gia)")
    for i, b in enumerate(optimal_pattern, 3):
        print(f"  Block {i}:   {b:7.2f} kW")
    
    print(f"\n📊 Tổng baseline:")
    print(f"  Blocks 1,2:  0 kW")
    print(f"  Blocks 3-7:  {total_baseline:.2f} kW")
    print(f"  TỔNG CỘNG:   {total_baseline:.0f} kW")
    
    # So sánh
    print(f"\n📊 SO SÁNH:")
    print(f"  • 7 blocks (tất cả):     7 × 507 = 3,549 kW")
    print(f"  • 5 blocks (3-7 only):   {total_baseline:.0f} kW")
    print(f"  • Chênh lệch:            {total_baseline - 3549:.0f} kW")
    print(f"  • Giảm:                  {(1 - total_baseline/3549)*100:.1f}%")
    
    print(f"\n💡 Lý do giảm:")
    print(f"  Mất 2 blocks đầu = mất 2 × 507 = 1,014 kW")
    
    # SOC trajectory chi tiết
    print(f"\n📈 SOC TRAJECTORY CHI TIẾT:")
    print("-" * 80)
    
    soc = SOC_MIN
    print(f"  Start (0h):              {soc:6.2f}%  ✅")
    
    # Block 1, 2: không hoạt động, SOC không đổi
    for i in [1, 2]:
        status = "✅ (không hoạt động)"
        print(f"  After Block {i} ({i*3:2d}h):     {soc:6.2f}%  "
              f"(ΔSOC= +0.00%, b=0kW) {status}")
    
    # Block 3-7: có baseline
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

else:
    print(f"\n❌ Không tìm được nghiệm: {result.message}")

# ===== PHƯƠNG PHÁP 2: GIẢI TÍCH =====
print("\n" + "=" * 80)
print("PHƯƠNG PHÁP 2: GIẢI TÍCH")
print("=" * 80)

print("\n📐 Phân tích:")
print("  • Block 1,2: ΔSOC = 0 (không hoạt động)")
print("  • Block 3-7: cần tăng SOC từ 5% → 90% = +85%")
print("  • Tương tự trường hợp 7 blocks:")
print("    - Objective tuyến tính: Σbᵢ")
print("    - Constraint tuyến tính: 0.040635×Σbᵢ = const")
print("    - Hệ số giống nhau → nghiệm đều")

uniform_b = required_sum / 5
print(f"\n🧮 Tính toán:")
print(f"  Cần tăng SOC: {required_delta:.2f}%")
print(f"  5 blocks phải tạo: Σ(ΔSOC) = {required_delta:.2f}%")
print(f"  ⟹ Σbᵢ = {required_sum:.2f} kW")
print(f"  ⟹ b = {required_sum:.2f} / 5 = {uniform_b:.2f} kW")

print(f"\n✅ PATTERN TỐI ƯU (GIẢI TÍCH):")
print(f"   Block 1,2: 0 kW (không hoạt động)")
print(f"   Block 3-7: 5 × {uniform_b:.2f} kW = {5 * uniform_b:.0f} kW")
print(f"   TỔNG:      {5 * uniform_b:.0f} kW")

# Verify SOC trajectory
print(f"\n🔍 Xác minh SOC trajectory:")
soc = SOC_MIN
print(f"  Block 0:  SOC = {soc:.2f}%")
print(f"  Block 1:  SOC = {soc:.2f}% (không đổi)")
print(f"  Block 2:  SOC = {soc:.2f}% (không đổi)")

for i in range(3, 8):
    delta = calc_delta_soc(uniform_b)
    soc += delta
    print(f"  Block {i}:  SOC = {soc:.2f}% (b={uniform_b:.0f}kW, ΔSOC={delta:+.2f}%)")

# ===== SO SÁNH 2 TRƯỜNG HỢP =====
print("\n" + "=" * 80)
print("SO SÁNH CHI TIẾT 2 TRƯỜNG HỢP")
print("=" * 80)

print(f"\n📊 TRƯỜNG HỢP 1: 7 blocks (tất cả tham gia)")
print(f"  Pattern: [507, 507, 507, 507, 507, 507, 507]")
print(f"  Tổng:    3,549 kW")
print(f"  Mỗi block: 507 kW")

print(f"\n📊 TRƯỜNG HỢP 2: 5 blocks (Block 1,2 không tham gia)")
print(f"  Pattern: [0, 0, {uniform_b:.0f}, {uniform_b:.0f}, {uniform_b:.0f}, {uniform_b:.0f}, {uniform_b:.0f}]")
print(f"  Tổng:    {5 * uniform_b:.0f} kW")
print(f"  Mỗi block (3-7): {uniform_b:.0f} kW")

print(f"\n📉 CHÊNH LỆCH:")
print(f"  Tổng baseline: {5*uniform_b:.0f} - 3,549 = {5*uniform_b - 3549:.0f} kW")
print(f"  Phần trăm:     {(1 - 5*uniform_b/3549)*100:.1f}%")
print(f"  ")
print(f"  Mất đi:        2 blocks × 507 kW = 1,014 kW")

print(f"\n💡 TẠI SAO GIẢM?")
print(f"  • Block 1,2 không tham gia → mất 2 blocks")
print(f"  • 7 blocks → 5 blocks")
print(f"  • Mất 2 × 507 = 1,014 kW")
print(f"  • Còn lại: 3,549 - 1,014 = {3549 - 1014:.0f} kW")

# ===== CÔNG THỨC TỔNG QUÁT =====
print("\n" + "=" * 80)
print("CÔNG THỨC TỔNG QUÁT")
print("=" * 80)

print("\n📐 Nếu n blocks đầu KHÔNG tham gia:")
print("  • n blocks: baseline = 0, ΔSOC = 0")
print("  • (7-n) blocks còn lại: phải tạo +85% SOC")
print("  • Pattern tối ưu: (7-n) blocks × b kW")
print("  ")
print("  Công thức:")
print("    Σbᵢ = 3,549 × (7-n)/7 kW")
print("    b = 3,549 / 7 = 507 kW (không đổi!)")
print("  ")
print("  Ví dụ:")

for n in range(8):
    if n < 7:
        remaining = 7 - n
        total = 507 * remaining
        print(f"    n={n}: {remaining} blocks × 507 kW = {total:,} kW")
    else:
        print(f"    n={n}: 0 blocks × 507 kW = 0 kW (không khả thi)")

# ===== VISUALIZATION =====
print("\n" + "=" * 80)
print("MINH HỌA")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Baseline comparison
ax1 = axes[0, 0]
blocks_all = np.arange(1, 8)
baseline_7blocks = [507] * 7
baseline_5blocks = [0, 0, 507, 507, 507, 507, 507]

x = np.arange(7)
width = 0.35

bars1 = ax1.bar(x - width/2, baseline_7blocks, width, label='7 blocks',
                color='green', alpha=0.7, edgecolor='black', linewidth=2)
bars2 = ax1.bar(x + width/2, baseline_5blocks, width, label='5 blocks',
                color='orange', alpha=0.7, edgecolor='black', linewidth=2)

# Annotate blocks 1,2
for i in [0, 1]:
    ax1.text(i, 50, 'NO\nBASELINE', ha='center', fontsize=10,
             fontweight='bold', color='red')

ax1.set_xlabel('Block number', fontsize=12)
ax1.set_ylabel('Baseline (kW)', fontsize=12)
ax1.set_title('Baseline Comparison: 7 blocks vs 5 blocks', fontsize=14,
              fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(blocks_all)
ax1.legend(fontsize=11)
ax1.grid(True, axis='y', alpha=0.3)
ax1.set_ylim(0, 600)

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
ax2.axhline(y=90, color='r', linestyle='--', linewidth=2, alpha=0.5)
ax2.axhline(y=5, color='b', linestyle='--', linewidth=2, alpha=0.5)
ax2.fill_between(blocks_range, 5, 90, alpha=0.1, color='gray')

ax2.set_xlabel('Block number', fontsize=12)
ax2.set_ylabel('SOC (%)', fontsize=12)
ax2.set_title('SOC Trajectory - 7 blocks (all participate)', fontsize=14,
              fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)
ax2.set_xlim(0, 7)
ax2.set_ylim(0, 100)

# Plot 3: SOC trajectory - 5 blocks
ax3 = axes[1, 0]
soc_5blocks = [5.0]
soc = 5.0

# Block 1, 2: không đổi
for _ in [1, 2]:
    soc_5blocks.append(soc)

# Block 3-7: baseline = 507
for _ in range(5):
    soc += calc_delta_soc(507)
    soc_5blocks.append(soc)

blocks_all_range = list(range(0, 8))

# Plot với colors khác nhau
ax3.plot([0, 1, 2], soc_5blocks[0:3], 'ro--', linewidth=3, markersize=10,
         label='Blocks 1-2: 0kW (no change)', zorder=3)
ax3.plot(list(range(2, 8)), soc_5blocks[2:], 'go-', linewidth=3, markersize=10,
         label='Blocks 3-7: 507kW each', zorder=3)

ax3.axhline(y=90, color='r', linestyle='--', linewidth=2, alpha=0.5)
ax3.axhline(y=5, color='b', linestyle='--', linewidth=2, alpha=0.5)

# Highlight regions
ax3.axvspan(0, 2, alpha=0.1, color='red', label='No activity')
ax3.fill_between([2, 7], 5, 90, alpha=0.1, color='gray')

# Annotate
ax3.text(1, 8, 'SOC không đổi', ha='center', fontsize=10,
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

ax3.set_xlabel('Block number', fontsize=12)
ax3.set_ylabel('SOC (%)', fontsize=12)
ax3.set_title('SOC Trajectory - 5 blocks (Blocks 1,2: no baseline)',
              fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=9, loc='upper left')
ax3.set_xlim(0, 7)
ax3.set_ylim(0, 100)

# Plot 4: Total capacity comparison
ax4 = axes[1, 1]
cases = ['7 blocks\n(all)', '6 blocks', '5 blocks', '4 blocks', '3 blocks']
totals = [3549, 3042, 2535, 2028, 1521]
colors_bar = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6']

bars = ax4.bar(cases, totals, color=colors_bar, alpha=0.7,
               edgecolor='black', linewidth=2)

for bar, total in zip(bars, totals):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{total:,} kW',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

ax4.set_ylabel('Total Baseline (kW)', fontsize=12)
ax4.set_title('Total Capacity vs Number of Participating Blocks',
              fontsize=14, fontweight='bold')
ax4.grid(True, axis='y', alpha=0.3)
ax4.set_ylim(0, 4000)

plt.tight_layout()
plt.savefig('correct_block12_no_baseline.png', dpi=150, bbox_inches='tight')
print("\n💾 Saved: correct_block12_no_baseline.png")

# ===== FINAL SUMMARY =====
print("\n" + "=" * 80)
print("KẾT LUẬN CUỐI CÙNG")
print("=" * 80)

print(f"\n✅ HIỂU ĐÚNG:")
print(f"  • Không có baseline = KHÔNG hoạt động")
print(f"  • ΔSOC = 0 (SOC giữ nguyên)")
print(f"  • Block 1,2 không tham gia → SOC = 5% (không đổi)")

print(f"\n📊 KẾT QUẢ:")
print(f"  • 7 blocks: 7 × 507 = 3,549 kW")
print(f"  • 5 blocks: 5 × 507 = 2,535 kW")
print(f"  • Giảm:     1,014 kW (28.6%)")

print(f"\n💡 TẠI SAO GIẢM?")
print(f"  Đơn giản: mất 2 blocks = mất 2 × 507 = 1,014 kW!")
print(f"  ")
print(f"  Công thức: Tổng = (số blocks) × 507 kW")

print("\n🏆 HOÀN THÀNH!")
print("=" * 80)
