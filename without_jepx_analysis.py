"""
TRƯỜNG HỢP: KHÔNG THAM GIA JEPX

Block 8 (21-24h) sẽ như thế nào nếu không có JEPX discharge?

Phân tích:
  • Không JEPX = Block 8 không hoạt động
  • ΔSOC_block8 = 0 (không xả từ 90% → 5%)
  • ⟹ Cycle constraint thay đổi!
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
print("TRƯỜNG HỢP: KHÔNG THAM GIA JEPX")
print("=" * 80)

print("\n📋 PHÂN TÍCH:")
print("  • Không JEPX = Block 8 KHÔNG hoạt động")
print("  • ΔSOC_block8 = 0 (SOC giữ nguyên)")
print("  • Cycle constraint: Σ(ΔSOC_baseline) = 0 (not -85%!)")

# ===== CYCLE CONSTRAINT =====
print("\n" + "=" * 80)
print("CYCLE CONSTRAINT MỚI")
print("=" * 80)

print("\n📐 Với JEPX:")
print("  Σ(ΔSOC_baseline) + ΔSOC_JEPX = 0")
print("  Σ(ΔSOC_baseline) + (-85%) = 0")
print("  ⟹ Σ(ΔSOC_baseline) = +85%")

print("\n📐 KHÔNG JEPX:")
print("  Σ(ΔSOC_baseline) + 0 = 0")
print("  ⟹ Σ(ΔSOC_baseline) = 0%")
print("  ⟹ SOC kết thúc = SOC ban đầu")

print("\n💡 Ý NGHĨA:")
print("  • Với JEPX: SOC tăng từ 5% → 90% (baseline), rồi giảm 90% → 5% (JEPX)")
print("  • Không JEPX: SOC phải quay về điểm ban đầu (5%)")

# ===== TÍNH TOÁN CHO 7 BLOCKS =====
print("\n" + "=" * 80)
print("TÍNH TOÁN CHO 7 BLOCKS (KHÔNG JEPX)")
print("=" * 80)

print("\n🎯 Mục tiêu:")
print(f"  SOC bắt đầu: {SOC_MIN:.1f}%")
print(f"  SOC kết thúc: {SOC_MIN:.1f}% (quay về ban đầu)")
print(f"  ⟹ Tổng ΔSOC: 0%")

print("\n📐 Constraint:")
print("  Σ (0.040635×bᵢ - 8.4591) = 0")
print("  0.040635 × Σbᵢ - 7 × 8.4591 = 0")
print("  0.040635 × Σbᵢ = 59.2137")

required_sum_no_jepx = 59.2137 / 0.040635
print(f"  ⟹ Σbᵢ = {required_sum_no_jepx:.2f} kW")

uniform_b_no_jepx = required_sum_no_jepx / 7
print(f"\n✅ Pattern đều: 7 × {uniform_b_no_jepx:.2f} kW = {7 * uniform_b_no_jepx:.0f} kW")

# ===== SO SÁNH 2 TRƯỜNG HỢP =====
print("\n" + "=" * 80)
print("SO SÁNH: CÓ JEPX vs KHÔNG JEPX")
print("=" * 80)

print("\n📊 CÓ JEPX (discharge 90% → 5%):")
print("  • Constraint: Σ(ΔSOC) = +85%")
print("  • Pattern: 7 × 507 kW = 3,549 kW")
print("  • SOC trajectory: 5% → 17% → 29% → ... → 90% → [JEPX] → 5%")

print(f"\n📊 KHÔNG JEPX:")
print(f"  • Constraint: Σ(ΔSOC) = 0%")
print(f"  • Pattern: 7 × {uniform_b_no_jepx:.0f} kW = {7*uniform_b_no_jepx:.0f} kW")
print(f"  • SOC trajectory: 5% → ... → 5% (quay về)")

print(f"\n📉 CHÊNH LỆCH:")
print(f"  • Giảm: {3549 - 7*uniform_b_no_jepx:.0f} kW ({(1 - 7*uniform_b_no_jepx/3549)*100:.1f}%)")
print(f"  • Lý do: Không có JEPX discharge 85%")

# ===== PHÂN TÍCH CHI TIẾT =====
print("\n" + "=" * 80)
print("PHÂN TÍCH CHI TIẾT KHÔNG JEPX")
print("=" * 80)

print("\n🔍 Tại sao giảm capacity?")
print(f"  Với JEPX:")
print(f"    • 7 blocks tăng SOC: +85%")
print(f"    • JEPX discharge: -85%")
print(f"    • Net: 0% (cycle hoàn thành)")
print(f"  ")
print(f"  Không JEPX:")
print(f"    • 7 blocks phải tự cân bằng: net = 0%")
print(f"    • Không thể tăng SOC nhiều như với JEPX")
print(f"    • Capacity giảm đáng kể")

# Verify SOC trajectory không JEPX
print(f"\n📈 SOC TRAJECTORY (Không JEPX):")
print("-" * 80)
soc = SOC_MIN
print(f"  Start:         {soc:6.2f}%")

for i in range(1, 8):
    delta = calc_delta_soc(uniform_b_no_jepx)
    soc += delta
    print(f"  After Block {i}: {soc:6.2f}% (ΔSOC = {delta:+7.2f}%, b={uniform_b_no_jepx:.0f}kW)")

print(f"\n✅ SOC cuối = {soc:.2f}% ≈ {SOC_MIN:.1f}% (quay về ban đầu)")

# ===== LINEAR PROGRAMMING VERIFICATION =====
print("\n" + "=" * 80)
print("XÁC MINH BẰNG LINEAR PROGRAMMING")
print("=" * 80)

# Biến: b₁, ..., b₇ (7 biến)
c = -np.ones(7)

# Ràng buộc bất đẳng thức: SOC ∈ [5%, 90%]
A_ub = []
b_ub = []

# Ràng buộc: SOC(k) ≤ 90 cho k=1..7
for k_idx in range(7):
    row = np.zeros(7)
    row[:k_idx+1] = 0.040635
    # SOC(k) = 5 + Σⱼ₌₁ᵏ (0.040635×bⱼ - 8.4591) ≤ 90
    A_ub.append(row)
    b_ub.append(SOC_MAX - SOC_MIN + (k_idx+1)*8.4591)

# Ràng buộc: SOC(k) ≥ 5 cho k=1..7
for k_idx in range(7):
    row = np.zeros(7)
    row[:k_idx+1] = -0.040635
    # SOC(k) = 5 + Σⱼ₌₁ᵏ (0.040635×bⱼ - 8.4591) ≥ 5
    A_ub.append(row)
    b_ub.append(-(k_idx+1)*8.4591)

A_ub = np.array(A_ub)
b_ub = np.array(b_ub)

# Ràng buộc đẳng thức: SOC(7) = 5 (quay về ban đầu)
A_eq = np.array([[0.040635] * 7])
b_eq = np.array([7 * 8.4591])

# Giới hạn: 0 ≤ bᵢ ≤ 2000
bounds = [(0, BASELINE_MAX)] * 7

print("\n🔧 Giải bài toán LP...")
result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                 bounds=bounds, method='highs')

if result.success:
    print("\n✅ TÌM RA NGHIỆM TỐI ƯU!")
    
    optimal_pattern = result.x
    total_baseline = sum(optimal_pattern)
    
    print(f"\n🎯 Pattern tối ưu:")
    for i, b in enumerate(optimal_pattern, 1):
        print(f"  Block {i}: {b:7.2f} kW")
    
    print(f"\n📊 Tổng baseline: {total_baseline:.2f} kW")
    
    # Verify
    std = np.std(optimal_pattern)
    mean = np.mean(optimal_pattern)
    print(f"\n🔍 Phân tích:")
    print(f"  Mean: {mean:.2f} kW")
    print(f"  Std:  {std:.4f} kW")
    if std < 0.01:
        print(f"  ✅ Pattern ĐỀU: {mean:.2f} kW")

else:
    print(f"\n❌ Không tìm được nghiệm: {result.message}")

# ===== CÔNG THỨC TỔNG QUÁT =====
print("\n" + "=" * 80)
print("CÔNG THỨC TỔNG QUÁT")
print("=" * 80)

print("\n📐 Công thức cho n blocks:")
print("  ")
print("  CÓ JEPX:")
print("    n × (0.040635 × b - 8.4591) = 85")
print("    b = (85 + n × 8.4591) / (n × 0.040635)")
print("  ")
print("  KHÔNG JEPX:")
print("    n × (0.040635 × b - 8.4591) = 0")
print("    b = (n × 8.4591) / (n × 0.040635)")
print("    b = 8.4591 / 0.040635")
print("    b = 208.17 kW (KHÔNG phụ thuộc n!)")

print("\n🧮 Tính toán:")
b_no_jepx = 8.4591 / 0.040635
print(f"  b = 8.4591 / 0.040635 = {b_no_jepx:.2f} kW")

print(f"\n📊 BẢNG SO SÁNH:")
print(f"┌──────────┬───────────────┬─────────────────┬──────────────┐")
print(f"│ Blocks   │ CÓ JEPX       │ KHÔNG JEPX      │ Chênh lệch   │")
print(f"│ (n)      │ (kW/block)    │ (kW/block)      │              │")
print(f"├──────────┼───────────────┼─────────────────┼──────────────┤")

for n in range(1, 8):
    b_with = (85 + n * 8.4591) / (n * 0.040635)
    b_without = 208.17
    total_with = n * b_with
    total_without = n * b_without
    diff = total_with - total_without
    
    if b_with <= 2000:
        print(f"│ {n:8} │ {b_with:7.0f} kW     │ {b_without:7.0f} kW      │ -{diff:6.0f} kW   │")
    else:
        print(f"│ {n:8} │ {b_with:7.0f} kW ❌  │ {b_without:7.0f} kW      │ -{diff:6.0f} kW   │")

print(f"└──────────┴───────────────┴─────────────────┴──────────────┘")

# ===== VISUALIZATION =====
print("\n" + "=" * 80)
print("MINH HỌA")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Baseline comparison
ax1 = axes[0, 0]
blocks = np.arange(1, 8)
baseline_with_jepx = [507] * 7
baseline_without_jepx = [208.17] * 7

x = np.arange(7)
width = 0.35

bars1 = ax1.bar(x - width/2, baseline_with_jepx, width, label='Có JEPX',
                color='green', alpha=0.7, edgecolor='black', linewidth=2)
bars2 = ax1.bar(x + width/2, baseline_without_jepx, width, label='KHÔNG JEPX',
                color='red', alpha=0.7, edgecolor='black', linewidth=2)

ax1.set_xlabel('Block number', fontsize=12)
ax1.set_ylabel('Baseline (kW)', fontsize=12)
ax1.set_title('Baseline per Block: With vs Without JEPX', fontsize=14,
              fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(blocks)
ax1.legend(fontsize=11)
ax1.grid(True, axis='y', alpha=0.3)
ax1.set_ylim(0, 600)

# Plot 2: SOC trajectory - WITH JEPX
ax2 = axes[0, 1]
soc_with = [5.0]
soc = 5.0
for b in [507] * 7:
    soc += calc_delta_soc(b)
    soc_with.append(soc)

# Add JEPX
soc_with.append(5.0)

blocks_with = list(range(0, 9))
ax2.plot(blocks_with[:-1], soc_with[:-1], 'go-', linewidth=3, markersize=10,
         label='Baseline blocks', zorder=3)
ax2.plot([7, 8], [soc_with[7], soc_with[8]], 'r*-', linewidth=3, markersize=15,
         label='JEPX discharge', zorder=3)

ax2.axhline(y=90, color='r', linestyle='--', linewidth=2, alpha=0.5)
ax2.axhline(y=5, color='b', linestyle='--', linewidth=2, alpha=0.5)
ax2.fill_between(blocks_with, 5, 90, alpha=0.1, color='gray')

ax2.text(7.5, 47.5, 'JEPX\n-85%', ha='center', fontsize=11, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))

ax2.set_xlabel('Block number (8 = JEPX)', fontsize=12)
ax2.set_ylabel('SOC (%)', fontsize=12)
ax2.set_title('SOC Trajectory - WITH JEPX', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)
ax2.set_xlim(0, 8)
ax2.set_ylim(0, 100)

# Plot 3: SOC trajectory - WITHOUT JEPX
ax3 = axes[1, 0]
soc_without = [5.0]
soc = 5.0
for b in [208.17] * 7:
    soc += calc_delta_soc(b)
    soc_without.append(soc)

blocks_without = list(range(0, 8))
ax3.plot(blocks_without, soc_without, 'ro-', linewidth=3, markersize=10,
         label=f'All blocks @ {b_no_jepx:.0f}kW', zorder=3)

ax3.axhline(y=90, color='r', linestyle='--', linewidth=2, alpha=0.5)
ax3.axhline(y=5, color='b', linestyle='--', linewidth=2, alpha=0.5, label='Start/End')
ax3.fill_between(blocks_without, 5, 90, alpha=0.1, color='gray')

# Circle the final point
ax3.plot(7, soc_without[7], 'go', markersize=20, markerfacecolor='none',
         markeredgewidth=3, label=f'End ≈ {soc_without[7]:.1f}%')

ax3.text(3.5, 8, 'SOC returns to start (≈5%)', ha='center', fontsize=11,
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

ax3.set_xlabel('Block number', fontsize=12)
ax3.set_ylabel('SOC (%)', fontsize=12)
ax3.set_title('SOC Trajectory - WITHOUT JEPX', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=10)
ax3.set_xlim(0, 7)
ax3.set_ylim(0, 100)

# Plot 4: Total capacity comparison
ax4 = axes[1, 1]
n_values = np.arange(1, 8)
total_with = [(85 + n * 8.4591) / (n * 0.040635) * n for n in n_values]
total_without = [208.17 * n for n in n_values]

ax4.plot(n_values, total_with, 'go-', linewidth=3, markersize=10,
         label='Có JEPX', marker='s')
ax4.plot(n_values, total_without, 'ro-', linewidth=3, markersize=10,
         label='KHÔNG JEPX', marker='o')

# Annotate 7 blocks
ax4.plot(7, total_with[6], 'g*', markersize=20)
ax4.text(7, total_with[6] + 200, f'{total_with[6]:.0f} kW', ha='center',
         fontsize=10, fontweight='bold', color='green')
ax4.plot(7, total_without[6], 'r*', markersize=20)
ax4.text(7, total_without[6] - 200, f'{total_without[6]:.0f} kW', ha='center',
         fontsize=10, fontweight='bold', color='red')

ax4.set_xlabel('Number of blocks', fontsize=12)
ax4.set_ylabel('Total Baseline (kW)', fontsize=12)
ax4.set_title('Total Capacity: With vs Without JEPX', fontsize=14, fontweight='bold')
ax4.legend(fontsize=11)
ax4.grid(True, alpha=0.3)
ax4.set_xticks(n_values)
ax4.set_ylim(0, 4000)

plt.tight_layout()
plt.savefig('with_vs_without_jepx.png', dpi=150, bbox_inches='tight')
print("\n💾 Saved: with_vs_without_jepx.png")

# ===== FINAL SUMMARY =====
print("\n" + "=" * 80)
print("KẾT LUẬN")
print("=" * 80)

print("\n✅ CÓ JEPX (discharge 90% → 5%):")
print("  • Constraint: Σ(ΔSOC) = +85%")
print("  • Pattern: 7 × 507 kW = 3,549 kW")
print("  • Block 8: JEPX discharge -85%")

print(f"\n✅ KHÔNG JEPX:")
print(f"  • Constraint: Σ(ΔSOC) = 0% (cycle closes)")
print(f"  • Pattern: 7 × {b_no_jepx:.0f} kW = {7*b_no_jepx:.0f} kW")
print(f"  • Block 8: KHÔNG hoạt động (ΔSOC = 0)")

print(f"\n📉 CHÊNH LỆCH:")
print(f"  • Giảm: {3549 - 7*b_no_jepx:.0f} kW ({(1 - 7*b_no_jepx/3549)*100:.1f}%)")
print(f"  • Lý do: Không có JEPX để discharge 85%")

print("\n💡 CÔNG THỨC:")
print("  CÓ JEPX:    b = (85 + n × 8.4591) / (n × 0.040635)")
print("  KHÔNG JEPX: b = 8.4591 / 0.040635 = 208.17 kW (cố định!)")

print("\n🎯 INSIGHT:")
print("  • JEPX cho phép tăng capacity ~2.4 lần (3,549 / 1,457)")
print("  • Không JEPX: mỗi block chỉ 208 kW (vs 507 kW với JEPX)")
print("  • Block 8 không JEPX = không hoạt động, SOC không đổi")

print("\n🏆 HOÀN THÀNH!")
print("=" * 80)
