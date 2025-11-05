#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHÂN TÍCH LẠI: Baseline và JEPX là 2 HỆ THỐNG RIÊNG BIỆT
"""

print("="*80)
print("🔍 PHÂN TÍCH LẠI: BASELINE vs JEPX")
print("="*80)

print("""
✅ HIỂU ĐÚNG:
1. 需給調整市場 (Baseline): Blocks có giá trị 基準値
2. JEPX: Blocks bán điện ra thị trường
3. ❌ KHÔNG THỂ dùng ĐỒNG THỜI cả 2 trong 1 block

Ví dụ từ data thực tế ngày 22/9:
- 06:00-15:00: CÓ baseline (1998kW, 0kW, 532kW)
- 15:00-18:00: JEPX discharge (950kW) → baseline = NaN
- 18:00-06:00: Không có data (có thể nghỉ hoặc chế độ khác)

VẬY NÊN:
""")

print("\n" + "="*80)
print("📊 MÔ HÌNH ĐÚNG")
print("="*80)

print("""
Có 3 loại blocks:
1. BASELINE blocks: Tham gia 需給調整市場 (có 基準値)
2. JEPX blocks: Bán điện ra JEPX (không có 基準値)
3. FREE blocks: Không tham gia gì (baseline = NaN, nghỉ tự nhiên)

Tối ưu hóa:
- Maximize Σ(基準値) trong BASELINE blocks
- JEPX blocks để xả nhanh
- FREE blocks để SOC tự giảm

Constraint:
- Tổng ΔSOC từ tất cả blocks = 0 (chu kỳ)
""")

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197

def calc_delta(b):
    return (SLOPE * b + INTERCEPT) * 3

# JEPX effect
jepx_delta = calc_delta(-950)

# FREE block effect (không có baseline, SOC tự giảm)
free_delta = calc_delta(0)

print(f"\nCác hiệu ứng (3h per block):")
print(f"  Baseline = 2000kW:  ΔSOC = +{calc_delta(2000):.2f}%")
print(f"  Baseline = 0kW:     ΔSOC = {free_delta:.2f}%")
print(f"  JEPX discharge:     ΔSOC = {jepx_delta:.2f}%")

print("\n" + "="*80)
print("🎯 BÀI TOÁN MỚI")
print("="*80)

print("""
Giả sử:
- N_baseline blocks: Tham gia 需給調整市場
- N_jepx blocks: Bán điện JEPX
- N_free blocks: Nghỉ tự do

Constraint:
1. N_baseline + N_jepx + N_free = 8 (tổng 24h)
2. Σ(ΔSOC_baseline) + N_jepx × JEPX_delta + N_free × FREE_delta = 0
3. SOC trong range [5%, 90%]
4. Baseline >= 0

Mục tiêu:
- Maximize: Σ(基準値) trong N_baseline blocks
""")

print("\n" + "="*80)
print("💡 CHIẾN LƯỢC")
print("="*80)

print("""
Từ data thực tế ngày 22/9:
- 3 blocks baseline (06:00-15:00): 1998, 0, 532 kW
- 1 block JEPX (15:00-18:00): 950kW discharge
- 4 blocks free (18:00-06:00): nghỉ

Pattern này cho:
- Tổng baseline = 1998 + 0 + 532 = 2530 kW (3 blocks)
- So với 8 blocks không JEPX (1665kW): tăng nhiều hơn!

Nhưng cần verify có cycle không?
""")

print("\n" + "="*80)
print("🔬 VERIFY DATA THỰC TẾ")
print("="*80)

# Pattern từ data thực tế
baselines_real = [1998, 0, 532]  # 3 blocks
n_jepx = 1
n_free = 4

# Tính tổng ΔSOC
total_delta = 0

print("Tính ΔSOC từng phần:")
print()

# Baseline blocks
for i, b in enumerate(baselines_real, 1):
    delta = calc_delta(b)
    total_delta += delta
    print(f"  Block {i} baseline {b}kW: ΔSOC = {delta:+.2f}%")

baseline_sum_delta = total_delta
print(f"  → Tổng từ baseline: {baseline_sum_delta:+.2f}%")
print()

# JEPX blocks
jepx_sum_delta = n_jepx * jepx_delta
total_delta += jepx_sum_delta
print(f"  {n_jepx} block JEPX: ΔSOC = {jepx_sum_delta:+.2f}%")
print()

# FREE blocks
free_sum_delta = n_free * free_delta
total_delta += free_sum_delta
print(f"  {n_free} blocks FREE: ΔSOC = {free_sum_delta:+.2f}%")
print()

print(f"TỔNG ΔSOC: {total_delta:+.2f}%")

if abs(total_delta) < 0.1:
    print("✅ CYCLE hoàn hảo!")
else:
    print(f"❌ Không cycle (lệch {total_delta:+.2f}%)")

total_baseline_real = sum(baselines_real)
print(f"\nTổng 基準値: {total_baseline_real} kW (3 blocks)")
print(f"So với 8 blocks không JEPX (1665kW): {total_baseline_real - 1665:.0f}kW ({(total_baseline_real/1665 - 1)*100:+.1f}%)")

print("\n" + "="*80)
print("🚀 TỐI ƯU HÓA MỚI")
print("="*80)

print("""
Strategy:
1. Chọn số blocks cho mỗi loại (baseline, JEPX, free)
2. Trong baseline blocks: maximize bằng cách dùng 2000kW
3. JEPX blocks: fix 950kW discharge
4. FREE blocks: để tự nhiên (0kW baseline)

Hãy thử các combinations:
""")

SOC_MIN = 5
SOC_MAX = 90

results = []

# Thử các combinations
for n_baseline in range(1, 8):
    for n_jepx in range(0, 8 - n_baseline):
        n_free = 8 - n_baseline - n_jepx
        
        # Với n_baseline blocks, tối đa bao nhiêu blocks @ 2000kW?
        # Giới hạn: SOC không vượt 90%
        
        # Tính tổng ΔSOC cần từ baseline
        # Σ(ΔSOC_baseline) = -(n_jepx × jepx_delta + n_free × free_delta)
        target_delta = -(n_jepx * jepx_delta + n_free * free_delta)
        
        # Tính tổng baseline cần
        # Σ(ΔSOC) = 3 × SLOPE × Σ(b) + 3 × n × INTERCEPT
        # → Σ(b) = (Σ(ΔSOC) - 3 × n × INTERCEPT) / (3 × SLOPE)
        sum_baseline = (target_delta - 3 * n_baseline * INTERCEPT) / (3 * SLOPE)
        
        # Check if valid (>= 0)
        if sum_baseline < 0:
            continue
        
        # Tính pattern: N blocks @ 2000, rest @ X
        # Maximize N
        for n_max in range(n_baseline, -1, -1):
            remaining = n_baseline - n_max
            
            if remaining == 0:
                x = 0
                if n_max * 2000 != sum_baseline:
                    continue
            else:
                x = (sum_baseline - n_max * 2000) / remaining
            
            # Check constraints
            if x < 0:
                continue
            if x > 2000:
                continue
            
            # Simulate SOC
            soc = SOC_MIN
            max_soc = soc
            min_soc = soc
            valid = True
            
            # N_max blocks @ 2000
            for _ in range(n_max):
                soc += calc_delta(2000)
                max_soc = max(max_soc, soc)
                if soc > SOC_MAX:
                    valid = False
                    break
            
            if not valid:
                continue
            
            # Remaining baseline blocks @ x
            for _ in range(remaining):
                soc += calc_delta(x)
                max_soc = max(max_soc, soc)
                if soc > SOC_MAX or soc < SOC_MIN:
                    valid = False
                    break
            
            if not valid:
                continue
            
            # JEPX blocks
            for _ in range(n_jepx):
                soc += jepx_delta
                min_soc = min(min_soc, soc)
                if soc < SOC_MIN:
                    valid = False
                    break
            
            if not valid:
                continue
            
            # FREE blocks
            for _ in range(n_free):
                soc += free_delta
                min_soc = min(min_soc, soc)
                if soc < SOC_MIN:
                    valid = False
                    break
            
            if not valid:
                continue
            
            # Check cycle
            if abs(soc - SOC_MIN) > 0.1:
                continue
            
            # Valid pattern!
            results.append({
                'n_baseline': n_baseline,
                'n_jepx': n_jepx,
                'n_free': n_free,
                'n_max': n_max,
                'x': x,
                'sum_baseline': sum_baseline,
                'max_soc': max_soc,
                'min_soc': min_soc
            })
            break  # Found best for this combination

# Sort by sum_baseline descending
results.sort(key=lambda r: r['sum_baseline'], reverse=True)

print(f"\nTìm thấy {len(results)} patterns hợp lệ")
print("\nTop 5 patterns (sorted by Σ基準値):\n")

for i, r in enumerate(results[:5], 1):
    print(f"{i}. Baseline:{r['n_baseline']} + JEPX:{r['n_jepx']} + Free:{r['n_free']}")
    print(f"   Pattern: {r['n_max']} blocks @2000kW + {r['n_baseline']-r['n_max']} blocks @{r['x']:.0f}kW")
    print(f"   Σ(基準値) = {r['sum_baseline']:.0f}kW")
    print(f"   SOC range: {r['min_soc']:.1f}% - {r['max_soc']:.1f}%")
    print()

if results:
    best = results[0]
    
    print("="*80)
    print("🏆 PATTERN TỐI ƯU NHẤT")
    print("="*80)
    
    print(f"""
    Cấu trúc:
    - {best['n_baseline']} blocks BASELINE (需給調整市場)
    - {best['n_jepx']} blocks JEPX (bán điện)
    - {best['n_free']} blocks FREE (nghỉ)
    
    Chi tiết baseline:
    - {best['n_max']} blocks @ 2000kW (charge MAX)
    - {best['n_baseline'] - best['n_max']} blocks @ {best['x']:.0f}kW
    
    Kết quả:
    - Tổng 基準値: {best['sum_baseline']:.0f}kW
    - So với 8 blocks (1665kW): +{best['sum_baseline'] - 1665:.0f}kW (+{(best['sum_baseline']/1665 - 1)*100:.1f}%)
    - SOC range: {best['min_soc']:.1f}% - {best['max_soc']:.1f}%
    """)
    
    print("\n✅ Đây là pattern TỐI ƯU với constraint:")
    print("   - Baseline và JEPX không đồng thời")
    print("   - Baseline luôn >= 0")
    print("   - SOC trong range [5%, 90%]")

print("\n✅ Hoàn tất!")
