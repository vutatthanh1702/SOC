#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HIỂU ĐÚNG VỀ FREE BLOCKS
"""

print("="*80)
print("🔍 PHÂN TÍCH LẠI: FREE BLOCKS LÀ GÌ?")
print("="*80)

print("""
❌ SAI LẦM TRƯỚC ĐÓ:
- Nghĩ rằng: FREE block (baseline = NaN) → ΔSOC = -8.5%
- Lý do sai: Công thức ΔSOC = (0.013545 × 基準値 - 2.8197) × 3
              chỉ áp dụng khi CÓ 基準値 (baseline plan)

✅ HIỂU ĐÚNG:
- FREE blocks: KHÔNG CÓ baseline plan (NaN)
- Công thức regression KHÔNG ÁP DỤNG
- SOC thay đổi do:
  1. Load thực tế (actual demand)
  2. Tự xả của pin (self-discharge)
  3. Các yếu tố khác ngoài baseline plan

📊 TỪ DATA THỰC TẾ:
Ngày 22/9:
- 06:00-09:00: Baseline 1998kW → SOC tăng
- 09:00-12:00: Baseline 0kW → SOC giảm -9% (theo công thức)
- 12:00-15:00: Baseline 532kW → SOC tăng
- 15:00-18:00: JEPX 950kW → SOC giảm mạnh -87%
- 18:00-06:00: FREE (NaN) → ???

Vấn đề: Chúng ta KHÔNG BIẾT SOC thay đổi như thế nào trong FREE blocks!
""")

print("\n" + "="*80)
print("💡 HAI KHẢ NĂNG")
print("="*80)

print("""
KHẢ NĂNG 1: FREE blocks = KHÔNG VẬN HÀNH
- Pin không sạc, không xả qua hệ thống
- SOC gần như KHÔNG ĐỔI (chỉ tự xả nhẹ ~0.1%/h)
- ΔSOC ≈ 0%

KHẢ NĂNG 2: FREE blocks = CÓ LOAD THỰC TẾ
- Pin xả để đáp ứng demand thực tế
- ΔSOC phụ thuộc vào actual load (không biết trước)

QUAN TRỌNG:
→ Nếu FREE blocks có ΔSOC ≠ 0 mà không biết trước
→ KHÔNG THỂ tối ưu hóa được!
→ Phải giả định ΔSOC ≈ 0 hoặc có data thực tế
""")

print("\n" + "="*80)
print("🔬 KIỂM TRA DATA THỰC TẾ")
print("="*80)

print("""
Cần kiểm tra từ SOC data:
- SOC lúc 18:00 (sau JEPX)
- SOC lúc 06:00 sáng hôm sau (trước baseline)
- ΔSOC trong khoảng 18:00-06:00 (12 giờ FREE)

Nếu có data này → Biết được FREE blocks ảnh hưởng thế nào
Nếu không → Phải giả định
""")

print("\n" + "="*80)
print("🎯 GIẢI PHÁP")
print("="*80)

print("""
OPTION 1: Giả định FREE blocks KHÔNG ẢNH HƯỞNG
- ΔSOC_free ≈ 0%
- Bỏ qua trong tính toán cycle
- Chỉ tối ưu baseline + JEPX

OPTION 2: Ước lượng từ data
- Xem SOC thực tế trong giờ FREE
- Tính average ΔSOC
- Dùng giá trị đó trong optimization

OPTION 3: Conservative approach
- Giả định FREE blocks xả nhẹ (ví dụ -1%/h)
- Tính vào constraint cycle
- An toàn hơn nhưng có thể không tối ưu

➡️ KHUYẾN NGHỊ:
Nếu không có data FREE blocks → Dùng OPTION 1 (giả định ΔSOC ≈ 0)
Lý do:
- FREE = không tham gia thị trường = không có load plan
- SOC chỉ thay đổi nhẹ do self-discharge
- Ảnh hưởng nhỏ, có thể bỏ qua
""")

print("\n" + "="*80)
print("🔄 TÍN TOÁN LẠI VỚI FREE ΔSOC = 0")
print("="*80)

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197

def calc_delta(b):
    return (SLOPE * b + INTERCEPT) * 3

# JEPX effect
jepx_delta = calc_delta(-950)

print(f"Giả định:")
print(f"  FREE blocks: ΔSOC ≈ 0%")
print(f"  JEPX block: ΔSOC = {jepx_delta:.2f}%")
print()

print(f"Để cycle với 3 baseline + 1 JEPX + 4 FREE:")
print(f"  Σ(ΔSOC_baseline) + 1 × {jepx_delta:.2f}% + 4 × 0% = 0")
print(f"  Σ(ΔSOC_baseline) = {-jepx_delta:.2f}%")
print()

# Tính tổng baseline cần
n_baseline = 3
target_delta = -jepx_delta
sum_baseline = (target_delta - 3 * n_baseline * INTERCEPT) / (3 * SLOPE)

print(f"Tổng 基準値 cần cho 3 blocks:")
print(f"  Σ(基準値) = ({target_delta:.2f} - 3 × {n_baseline} × {INTERCEPT}) / (3 × {SLOPE})")
print(f"  Σ(基準値) = {sum_baseline:.2f} kW")
print()

print(f"Pattern tối ưu:")
# Tìm N blocks @ 2000kW
for n_max in range(n_baseline, -1, -1):
    remaining = n_baseline - n_max
    
    if remaining == 0:
        if abs(n_max * 2000 - sum_baseline) > 1:
            continue
        x = 0
    else:
        x = (sum_baseline - n_max * 2000) / remaining
    
    if x < 0 or x > 2000:
        continue
    
    print(f"  {n_max} blocks @ 2000kW + {remaining} blocks @ {x:.0f}kW")
    print(f"  Total: {n_max * 2000 + remaining * x:.0f}kW")
    
    # Simulate
    soc = 5.0
    print(f"\n  Simulation (start SOC = {soc}%):")
    
    # FREE 1-2
    print(f"    Block 1-2 (FREE): {soc:.1f}% → {soc:.1f}% (ΔSOC = 0%)")
    
    # Baseline
    for i in range(n_max):
        delta = calc_delta(2000)
        soc_before = soc
        soc += delta
        print(f"    Block {3+i} (2000kW): {soc_before:.1f}% → {soc:.1f}% (ΔSOC = {delta:+.1f}%)")
    
    for i in range(remaining):
        delta = calc_delta(x)
        soc_before = soc
        soc += delta
        print(f"    Block {3+n_max+i} ({x:.0f}kW): {soc_before:.1f}% → {soc:.1f}% (ΔSOC = {delta:+.1f}%)")
    
    # JEPX
    soc_before = soc
    soc += jepx_delta
    print(f"    Block {3+n_baseline} (JEPX): {soc_before:.1f}% → {soc:.1f}% (ΔSOC = {jepx_delta:+.1f}%)")
    
    # FREE 7-8
    print(f"    Block 7-8 (FREE): {soc:.1f}% → {soc:.1f}% (ΔSOC = 0%)")
    
    print(f"\n  Kết quả: SOC về {soc:.1f}% (Error: {soc - 5.0:.2f}%)")
    
    if abs(soc - 5.0) < 0.1:
        print(f"  ✅ CYCLE hoàn hảo!")
    else:
        print(f"  ❌ Không cycle (cần điều chỉnh)")
    
    break

print("\n" + "="*80)
print("📝 KẾT LUẬN")
print("="*80)

print(f"""
✅ HIỂU ĐÚNG VỀ FREE BLOCKS:
- FREE = Không có baseline plan (NaN)
- Công thức regression KHÔNG áp dụng
- Giả định: ΔSOC ≈ 0% (self-discharge không đáng kể)

✅ PATTERN TỐI ƯU (với giả định FREE = 0):
- 3 baseline blocks: tối đa {sum_baseline:.0f}kW
- 1 JEPX block: 950kW discharge
- 4 FREE blocks: không ảnh hưởng (ΔSOC ≈ 0)

⚠️  LƯU Ý:
Nếu FREE blocks THỰC TẾ có ΔSOC ≠ 0:
→ Cần data thực tế để điều chỉnh
→ Hoặc thêm margin trong tính toán
→ Hoặc giảm số FREE blocks

🔍 CẦN LÀM TIẾP:
Kiểm tra SOC data thực tế trong khoảng 18:00-06:00
để xác nhận FREE blocks ảnh hưởng thế nào
""")

print("\n✅ Hoàn tất!")
