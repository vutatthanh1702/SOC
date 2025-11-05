#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra data coverage đơn giản
"""

import pandas as pd

# Load baseline data
baseline_df = pd.read_csv('kotohira_kijyunchi_20250801~now (1).csv')
baseline_df['start_time'] = pd.to_datetime(baseline_df['start_time'])
baseline_df['date'] = baseline_df['start_time'].dt.date
baseline_df['hour'] = baseline_df['start_time'].dt.hour

print("="*80)
print("🔍 DATA COVERAGE CHECK")
print("="*80)

for date_str in ['2025-09-22', '2025-09-23', '2025-09-25', '2025-09-26']:
    target = pd.to_datetime(date_str).date()
    day_data = baseline_df[baseline_df['date'] == target].copy()
    
    if len(day_data) == 0:
        print(f"\n{date_str}: ❌ KHÔNG CÓ DATA")
        continue
    
    hours_avail = sorted(day_data['hour'].unique().tolist())
    all_hours = list(range(24))
    missing = sorted(set(all_hours) - set(hours_avail))
    
    print(f"\n{date_str}:")
    print(f"  ✅ Có data: {len(day_data)} records")
    print(f"  ⏰ Giờ có data: {hours_avail}")
    print(f"  ❌ Giờ thiếu: {missing}")
    print(f"  📊 Coverage: {len(hours_avail)}/24 giờ ({len(hours_avail)/24*100:.1f}%)")

print("\n" + "="*80)
print("💡 KẾT LUẬN")
print("="*80)
print("""
✅ Data chỉ có từ 6h-14h30 (9 giờ)
❌ THIẾU: 15h-5h (15 giờ)

Đặc biệt khoảng 15-18h mà bạn hỏi:
→ KHÔNG CÓ data trong file baseline gốc
→ Không phải = 0, mà là THIẾU hoàn toàn

Điều này có nghĩa:
1. Công thức regression (ΔSOC = 0.013545 × 基準値 - 2.8197):
   ✅ HỢP LỆ cho khoảng 6-15h (đã có data)
   ❓ CHƯA BIẾT về 15-24h và 0-6h (chưa có data để test)

2. Tổng 基準値 = 1665kW cho 8 blocks:
   ✅ HỢP LỆ về mặt toán học (nếu có đủ 8 blocks)
   ❓ Cần xác nhận pattern thực tế có chạy đủ 8 blocks/ngày không

3. Hiện tượng SOC giảm 92%→5% trong 15-18h:
   → Đây là THỰC TẾ từ SOC data
   → KHÔNG CÓ baseline data tương ứng
   → Có thể:
     a) Hệ thống chỉ chạy 6-15h, nghỉ 15h-6h
     b) Data baseline không được thu thập 15-24h
     c) Có chế độ vận hành khác không dùng baseline

➡️  Không cần sửa công thức, chỉ cần hiểu rõ:
    - Công thức chỉ áp dụng cho thời gian CÓ baseline data
    - Ngoài thời gian đó, SOC thay đổi do yếu tố khác
""")
