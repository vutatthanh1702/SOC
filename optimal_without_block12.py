"""
BÀI TOÁN MỚI: Block 1, 2 (0-6h) KHÔNG CÓ BASELINE
Chỉ có 5 blocks (3,4,5,6,7) có thể tham gia thị trường
JEPX vẫn discharge từ 90% → 5%

Ràng buộc mới:
  • Block 1,2: baseline = 0 (không tham gia)
  • Block 3,4,5,6,7: có baseline
  • SOC bắt đầu = 5%, kết thúc trước JEPX = 90%
  • SOC(t) ∈ [5%, 90%] ∀t
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
print("BÀI TOÁN MỚI: Block 1,2 không có baseline")
print("=" * 80)

print("\n📋 ĐIỀU KIỆN:")
print("  • Block 1,2 (0-6h): KHÔNG tham gia thị trường → baseline = 0")
print("  • Block 3,4,5,6,7 (6-21h): CÓ thể có baseline")
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
print(f"\n  SOC sau Block 2: {SOC_MIN:.1f}% → {soc_after_block2:.2f}%")

if soc_after_block2 < SOC_MIN:
    print(f"  ❌ CẢNH BÁO: SOC giảm xuống {soc_after_block2:.2f}% < {SOC_MIN}%!")
    print(f"  ⟹ VI PHẠM ràng buộc!")
    violation = SOC_MIN - soc_after_block2
    print(f"\n  📌 Cần bù: +{violation:.2f}% từ các blocks khác")
else:
    print(f"  ✅ SOC vẫn trong phạm vi [{SOC_MIN}%, {SOC_MAX}%]")

# ===== TÍNH TOÁN YÊU CẦU =====
print("\n" + "=" * 80)
print("TÍNH TOÁN YÊU CẦU CHO 5 BLOCKS (3-7)")
print("=" * 80)

print("\n🎯 Mục tiêu:")
print(f"  SOC sau Block 2: {soc_after_block2:.2f}%")
print(f"  SOC trước JEPX (sau Block 7): {SOC_MAX:.1f}%")
print(f"  ⟹ Cần tăng: {SOC_MAX - soc_after_block2:.2f}%")

required_delta = SOC_MAX - soc_after_block2
print(f"\n📐 Constraint cho 5 blocks:")
print(f"  Σ ΔSOC(b₃,...,b₇) = {required_delta:.4f}%")
print(f"  Σ (0.040635×bᵢ - 8.4591) = {required_delta:.4f}%")
print(f"  0.040635 × Σbᵢ - 5×8.4591 = {required_delta:.4f}%")
print(f"  0.040635 × Σbᵢ = {required_delta + 5*8.4591:.4f}%")

required_sum = (required_delta + 5*8.4591) / 0.040635
print(f"\n✅ CONSTRAINT: Σ(b₃,...,b₇) = {required_sum:.2f} kW")

# ===== PHƯƠNG PHÁP 1: LINEAR PROGRAMMING =====
print("\n" + "=" * 80)
print("PHƯƠNG PHÁP 1: LINEAR PROGRAMMING")
print("=" * 80)

# Biến: b₃, b₄, b₅, b₆, b₇ (5 biến)
# Objective: Maximize Σbᵢ ⟹ Minimize -Σbᵢ
c = -np.ones(5)

# Ràng buộc bất đẳng thức: SOC ∈ [5%, 90%]
A_ub = []
b_ub = []

# Bắt đầu từ SOC = soc_after_block2
# SOC(k) = soc_after_block2 + Σⱼ₌₃ᵏ ΔSOC(bⱼ)
#        = soc_after_block2 + 0.040635×Σⱼ₌₃ᵏ bⱼ - (k-2)×8.4591

# Ràng buộc: SOC(k) ≤ 90 cho k=3,4,5,6,7
for k_idx, k in enumerate(range(3, 8)):  # k_idx: 0,1,2,3,4
    row = np.zeros(5)
    row[:k_idx+1] = 0.040635
    # soc_after_block2 + 0.040635×Σbⱼ - (k-2)×8.4591 ≤ 90
    # 0.040635×Σbⱼ ≤ 90 - soc_after_block2 + (k-2)×8.4591
    A_ub.append(row)
    b_ub.append(SOC_MAX - soc_after_block2 + (k-2)*8.4591)

# Ràng buộc: SOC(k) ≥ 5 cho k=3,4,5,6,7
for k_idx, k in enumerate(range(3, 8)):
    row = np.zeros(5)
    row[:k_idx+1] = -0.040635
    # soc_after_block2 + 0.040635×Σbⱼ - (k-2)×8.4591 ≥ 5
    # -0.040635×Σbⱼ ≤ soc_after_block2 - 5 - (k-2)×8.4591
    A_ub.append(row)
    b_ub.append(soc_after_block2 - SOC_MIN - (k-2)*8.4591)

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
    
    # So sánh với trường hợp 7 blocks
    print(f"\n📊 SO SÁNH:")
    print(f"  • 7 blocks (tất cả):  7 × 507 = 3,549 kW")
    print(f"  • 5 blocks (3-7):     {total_baseline:.0f} kW")
    print(f"  • Chênh lệch:         {3549 - total_baseline:.0f} kW")
    print(f"  • Giảm:               {(1 - total_baseline/3549)*100:.1f}%")
    
    # Kiểm tra SOC trajectory
    print(f"\n📈 SOC TRAJECTORY CHI TIẾT:")
    print("-" * 80)
    
    soc = SOC_MIN
    print(f"  Start (0h):           {soc:6.2f}%")
    
    # Block 1, 2: baseline = 0
    for i in [1, 2]:
        delta = calc_delta_soc(0)
        soc += delta
        status = "✅" if SOC_MIN <= soc <= SOC_MAX else "❌"
        print(f"  After Block {i} ({i*3}h):   {soc:6.2f}% "
              f"(ΔSOC = {delta:+7.2f}%, b=0 kW) {status}")
    
    # Block 3-7: có baseline
    for i, b in enumerate(optimal_pattern, 3):
        delta = calc_delta_soc(b)
        soc += delta
        status = "✅" if SOC_MIN <= soc <= SOC_MAX else "❌"
        print(f"  After Block {i} ({i*3}h):   {soc:6.2f}% "
              f"(ΔSOC = {delta:+7.2f}%, b={b:.0f} kW) {status}")
    
    # JEPX
    print(f"  JEPX (21-24h):        {SOC_MIN:6.2f}% "
          f"(ΔSOC = {SOC_MIN - soc:+7.2f}%)")
    
    # Phân tích pattern
    print(f"\n🔍 PHÂN TÍCH PATTERN (5 blocks):")
    std = np.std(optimal_pattern)
    mean = np.mean(optimal_pattern)
    print(f"  Mean (trung bình):    {mean:.2f} kW")
    print(f"  Std (độ lệch chuẩn):  {std:.4f} kW")
    
    if std < 0.01:
        print(f"  ✅ Pattern ĐỀU: tất cả ≈ {mean:.2f} kW")
        print(f"\n  🧮 Xác minh công thức:")
        print(f"     5 × {mean:.2f} = {5 * mean:.0f} kW")
    else:
        print(f"  ⚠️ Pattern KHÔNG ĐỀU")
        print(f"  Min: {min(optimal_pattern):.2f} kW")
        print(f"  Max: {max(optimal_pattern):.2f} kW")

else:
    print(f"\n❌ Không tìm được nghiệm: {result.message}")

# ===== PHƯƠNG PHÁP 2: GIẢI TÍCH =====
print("\n" + "=" * 80)
print("PHƯƠNG PHÁP 2: GIẢI TÍCH")
print("=" * 80)

print("\n📐 Tương tự như trường hợp 7 blocks:")
print("  • Objective: tuyến tính Σbᵢ")
print("  • Constraint: tuyến tính 0.040635×Σbᵢ = const")
print("  • Hệ số GIỐNG NHAU cho mỗi bᵢ")
print("  ⟹ Nghiệm đều: b₃ = b₄ = b₅ = b₆ = b₇")

uniform_b = required_sum / 5
print(f"\n🧮 Tính toán:")
print(f"  Σ(b₃,...,b₇) = {required_sum:.2f} kW")
print(f"  ⟹ b = {required_sum:.2f} / 5 = {uniform_b:.2f} kW")

print(f"\n✅ PATTERN TỐI ƯU (GIẢI TÍCH):")
print(f"   5 blocks × {uniform_b:.2f} kW = {5 * uniform_b:.0f} kW")

# ===== VISUALIZATION =====
print("\n" + "=" * 80)
print("MINH HỌA")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: So sánh 7 blocks vs 5 blocks
ax1 = axes[0, 0]
cases = ['7 blocks\n(all)', '5 blocks\n(3-7 only)']
totals = [3549, 5 * uniform_b]
colors = ['#2ecc71', '#e74c3c']
bars = ax1.bar(cases, totals, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

for bar, total in zip(bars, totals):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{total:.0f} kW',
             ha='center', va='bottom', fontsize=14, fontweight='bold')

ax1.set_ylabel('Total Baseline (kW)', fontsize=12)
ax1.set_title('Comparison: 7 blocks vs 5 blocks', fontsize=14, fontweight='bold')
ax1.grid(True, axis='y', alpha=0.3)
ax1.set_ylim(0, 4000)

# Plot 2: SOC trajectory - 7 blocks
ax2 = axes[0, 1]
soc_7blocks = [5.0]
soc = 5.0
for b in [507] * 7:
    soc += calc_delta_soc(b)
    soc_7blocks.append(soc)

blocks_7 = list(range(0, 8))
ax2.plot(blocks_7, soc_7blocks, 'go-', linewidth=3, markersize=10,
         label='7 blocks (all @ 507kW)')
ax2.axhline(y=90, color='r', linestyle='--', linewidth=2, alpha=0.5)
ax2.axhline(y=5, color='b', linestyle='--', linewidth=2, alpha=0.5)
ax2.fill_between(blocks_7, 5, 90, alpha=0.1, color='gray')

ax2.set_xlabel('Block number', fontsize=12)
ax2.set_ylabel('SOC (%)', fontsize=12)
ax2.set_title('SOC Trajectory - 7 blocks scenario', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)
ax2.set_xlim(0, 7)
ax2.set_ylim(0, 100)

# Plot 3: SOC trajectory - 5 blocks
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

blocks_all = list(range(0, 8))
colors_blocks = ['red', 'red', 'green', 'green', 'green', 'green', 'green']

for i in range(len(blocks_all)-1):
    ax3.plot([blocks_all[i], blocks_all[i+1]],
             [soc_5blocks[i], soc_5blocks[i+1]],
             color=colors_blocks[i], linewidth=3, marker='o', markersize=10)

ax3.axhline(y=90, color='r', linestyle='--', linewidth=2, alpha=0.5,
            label='SOC max = 90%')
ax3.axhline(y=5, color='b', linestyle='--', linewidth=2, alpha=0.5,
            label='SOC min = 5%')
ax3.fill_between(blocks_all, 5, 90, alpha=0.1, color='gray')

# Annotate blocks
ax3.text(1, soc_5blocks[2] - 5, 'Blocks 1,2\n(no baseline)',
         ha='center', fontsize=10, bbox=dict(boxstyle='round',
         facecolor='red', alpha=0.3))
ax3.text(5, soc_5blocks[5] + 5, f'Blocks 3-7\n({uniform_b:.0f}kW each)',
         ha='center', fontsize=10, bbox=dict(boxstyle='round',
         facecolor='green', alpha=0.3))

ax3.set_xlabel('Block number', fontsize=12)
ax3.set_ylabel('SOC (%)', fontsize=12)
ax3.set_title('SOC Trajectory - 5 blocks scenario (blocks 1,2 excluded)',
              fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=10)
ax3.set_xlim(0, 7)
ax3.set_ylim(-5, 100)

# Plot 4: Bar chart - pattern comparison
ax4 = axes[1, 1]
x_7 = np.arange(1, 8)
x_5 = np.arange(3, 8)

bars_7 = ax4.bar(x_7, [507]*7, width=0.4, label='7 blocks (507kW each)',
                 color='#2ecc71', alpha=0.7, edgecolor='black', linewidth=2)
bars_5 = ax4.bar(x_5, [uniform_b]*5, width=0.4, label=f'5 blocks ({uniform_b:.0f}kW each)',
                 color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=2)

# Mark blocks 1,2 as excluded
for block in [1, 2]:
    ax4.axvspan(block-0.5, block+0.5, alpha=0.2, color='red')
    ax4.text(block, 50, 'NO\nBASELINE', ha='center', va='center',
             fontsize=10, fontweight='bold', color='red')

ax4.set_xlabel('Block number', fontsize=12)
ax4.set_ylabel('Baseline (kW)', fontsize=12)
ax4.set_title('Pattern Comparison', fontsize=14, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, axis='y', alpha=0.3)
ax4.set_xticks(range(1, 8))
ax4.set_ylim(0, 800)

plt.tight_layout()
plt.savefig('optimal_without_block12.png', dpi=150, bbox_inches='tight')
print("\n💾 Saved: optimal_without_block12.png")

# ===== FINAL SUMMARY =====
print("\n" + "=" * 80)
print("KẾT LUẬN")
print("=" * 80)

print(f"\n✅ TRƯỜNG HỢP 7 BLOCKS (tất cả tham gia):")
print(f"   Pattern: 7 × 507 kW = 3,549 kW")

print(f"\n✅ TRƯỜNG HỢP 5 BLOCKS (Block 1,2 không tham gia):")
print(f"   Pattern: 5 × {uniform_b:.0f} kW = {5*uniform_b:.0f} kW")
print(f"   Giảm: {3549 - 5*uniform_b:.0f} kW ({(1-5*uniform_b/3549)*100:.1f}%)")

print(f"\n📊 LÝ DO GIẢM:")
print(f"   • Block 1,2 không có baseline → ΔSOC = -8.4591% mỗi block")
print(f"   • Tổng giảm sau 2 blocks: {2*calc_delta_soc(0):.2f}%")
print(f"   • SOC sau Block 2: {soc_after_block2:.2f}%")
print(f"   • 5 blocks còn lại phải bù lên 90% → tải nặng hơn mỗi block")

print(f"\n💡 INSIGHT:")
print(f"   • Mất 2 blocks đầu → mất ~{(1-5*uniform_b/3549)*100:.0f}% capacity")
print(f"   • Mỗi block còn lại phải gánh {uniform_b:.0f}kW thay vì 507kW")
print(f"   • Tăng {uniform_b - 507:.0f}kW/block ({(uniform_b/507 - 1)*100:.1f}%)")

print("\n🏆 HOÀN THÀNH!")
print("=" * 80)
