#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra coverage của data - xem có đủ 24h không
"""

import pandas as pd
from datetime import datetime

# Load data
print("📂 Loading data...")
baseline_df = pd.read_csv('kotohira_kijyunchi_20250801~now (1).csv')
baseline_df['start_time'] = pd.to_datetime(baseline_df['start_time'])
baseline_df['date'] = baseline_df['start_time'].dt.date
baseline_df['hour'] = baseline_df['start_time'].dt.hour
baseline_df['基準値'] = baseline_df['需要計画kW'].fillna(0)

print("\n" + "="*80)
print("🔍 KIỂM TRA DATA COVERAGE - Ngày 2025-09-22")
print("="*80)

target_date = pd.to_datetime('2025-09-22').date()
day22 = baseline_df[baseline_df['date'] == target_date].copy()

print(f"\n📊 Tổng số records: {len(day22)}")
print(f"📊 Thời gian: {day22['start_time'].min()} → {day22['start_time'].max()}")

# Xem tất cả các giờ có data
hours_available = sorted(day22['hour'].unique())
print(f"\n⏰ Các giờ CÓ data: {hours_available}")
print(f"   Tổng: {len(hours_available)}/24 giờ")

# Các giờ THIẾU
all_hours = set(range(24))
missing_hours = sorted(all_hours - set(hours_available))
print(f"\n❌ Các giờ THIẾU data: {missing_hours}")

# Chi tiết từng giờ
print("\n📋 Chi tiết baseline theo giờ:")
hourly = day22.groupby('hour')['基準値'].agg(['count', 'mean', 'min', 'max'])
print(hourly.to_string())

print("\n" + "="*80)
print("🔍 KIỂM TRA DATA COVERAGE - Ngày 2025-09-25")
print("="*80)

target_date25 = pd.to_datetime('2025-09-25').date()
day25 = baseline_df[baseline_df['date'] == target_date25].copy()

print(f"\n📊 Tổng số records: {len(day25)}")
print(f"📊 Thời gian: {day25['start_time'].min()} → {day25['start_time'].max()}")

hours_available25 = sorted(day25['hour'].unique())
print(f"\n⏰ Các giờ CÓ data: {hours_available25}")
print(f"   Tổng: {len(hours_available25)}/24 giờ")

missing_hours25 = sorted(all_hours - set(hours_available25))
print(f"\n❌ Các giờ THIẾU data: {missing_hours25}")

print("\n📋 Chi tiết baseline theo giờ:")
hourly25 = day25.groupby('hour')['基準值'].agg(['count', 'mean', 'min', 'max'])
print(hourly25.to_string())

print("\n" + "="*80)
print("📊 SO SÁNH NGÀY 22, 23, 25, 26")
print("="*80)

for date_str in ['2025-09-22', '2025-09-23', '2025-09-25', '2025-09-26']:
    target = pd.to_datetime(date_str).date()
    day_data = baseline_df[baseline_df['date'] == target].copy()
    
    hours_avail = sorted(day_data['hour'].unique())
    missing = sorted(all_hours - set(hours_avail))
    
    print(f"\n{date_str}:")
    print(f"  Giờ CÓ data: {hours_avail}")
    print(f"  Giờ THIẾU: {missing}")
    print(f"  Coverage: {len(hours_avail)}/24 giờ")

print("\n" + "="*80)
print("💡 PHÂN TÍCH extended_4days_data.csv")
print("="*80)

# Đọc file analysis trước đó
ext_df = pd.read_csv('extended_4days_data.csv')
print("\n📋 Dữ liệu đã dùng cho regression:")
print(ext_df[['date', 'time_start', 'time_end', 'baseline_kw']].to_string())

print("\n" + "="*80)
print("🎯 KẾT LUẬN")
print("="*80)

print("""
1. File extended_4days_data.csv chỉ có 3 blocks:
   - 06:00-08:59 (3h)
   - 09:00-11:59 (3h)  
   - 12:00-14:59 (3h)
   → Tổng: 9 giờ/24 giờ = 37.5% coverage

2. THIẾU các block:
   - 15:00-17:59 (3h) ← Đây là block bạn hỏi!
   - 18:00-20:59 (3h)
   - 21:00-23:59 (3h)
   - 00:00-02:59 (3h)
   - 03:00-05:59 (3h)
   → Thiếu 15 giờ = 5 blocks × 3h

3. Baseline data gốc:
   - Có thể có hoặc không có cho các giờ còn lại
   - Cần kiểm tra xem 15-18h có data trong raw file không

4. Công thức hiện tại:
   ✅ VẪN HỢP LỆ cho 3 blocks đã phân tích (6-9h, 9-12h, 12-15h)
   ❓ CHƯA BIẾT về các blocks còn lại (vì chưa có data)
   
5. Tổng 基準値 = 1665kW:
   ✅ ĐÚNG nếu pattern lặp lại 8 blocks/ngày
   ❓ Cần xác nhận pattern thực tế có đủ 8 blocks không
""")

print("\n✅ Hoàn tất!")
