#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phân tích chi tiết SOC và 基準値 trong khoảng 15-18h
Kiểm tra hiện tượng: SOC giảm mạnh từ 91%→5% khi không có 基準値
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time

# Load data
print("📂 Loading data...")
soc_df = pd.read_csv('kotohira_soc_20250801~now (1).csv')
baseline_df = pd.read_csv('kotohira_kijyunchi_20250801~now (1).csv')

# Parse datetime
soc_df['timestamp'] = pd.to_datetime(soc_df['time'])
soc_df['SOC(%)'] = soc_df['soc']
baseline_df['start_time'] = pd.to_datetime(baseline_df['start_time'])
baseline_df['end_time'] = pd.to_datetime(baseline_df['end_time'])
baseline_df['基準値'] = baseline_df['需要計画kW'].fillna(0)

# Tạo column để merge
soc_df['date'] = soc_df['timestamp'].dt.date
soc_df['hour'] = soc_df['timestamp'].dt.hour
soc_df['minute'] = soc_df['timestamp'].dt.minute

baseline_df['date'] = baseline_df['start_time'].dt.date
baseline_df['hour'] = baseline_df['start_time'].dt.hour

print("\n" + "="*80)
print("🔍 PHÂN TÍCH NGÀY 2025-09-22")
print("="*80)

target_date = pd.to_datetime('2025-09-22').date()

# Lọc data ngày 22
soc_day22 = soc_df[soc_df['date'] == target_date].copy()
baseline_day22 = baseline_df[baseline_df['date'] == target_date].copy()

print(f"\n📊 SOC data: {len(soc_day22)} records")
print(f"📊 Baseline data: {len(baseline_day22)} records")

# Tính baseline trung bình theo giờ
baseline_hourly = baseline_day22.groupby('hour')['基準値'].agg(['mean', 'min', 'max', 'count']).reset_index()

print("\n📈 Baseline theo giờ (ngày 22/9):")
print(baseline_hourly.to_string())

# Xem SOC trong khoảng 14-19h
print("\n" + "="*80)
print("🎯 FOCUS: Khoảng 14-19h (SOC từng phút)")
print("="*80)

soc_afternoon = soc_day22[(soc_day22['hour'] >= 14) & (soc_day22['hour'] < 19)].copy()

# Group theo giờ để xem xu hướng
soc_afternoon_summary = soc_afternoon.groupby('hour')['SOC(%)'].agg(['min', 'max', 'mean', 'count']).reset_index()
print("\nTóm tắt SOC theo giờ:")
print(soc_afternoon_summary.to_string())

# Xem chi tiết giờ 15, 16, 17
for h in [15, 16, 17]:
    soc_hour = soc_afternoon[soc_afternoon['hour'] == h]
    baseline_hour = baseline_day22[baseline_day22['hour'] == h]
    
    print(f"\n⏰ Giờ {h}:00-{h}:59")
    print(f"   SOC: {soc_hour['SOC(%)'].min():.1f}% → {soc_hour['SOC(%)'].max():.1f}%")
    print(f"   Baseline: {baseline_hour['基準値'].mean():.1f} kW (count: {len(baseline_hour)})")
    
    if soc_hour['SOC(%)'].max() - soc_hour['SOC(%)'].min() > 10:
        print(f"   ⚠️  SOC thay đổi lớn: {soc_hour['SOC(%)'].max() - soc_hour['SOC(%)'].min():.1f}%")

print("\n" + "="*80)
print("🔍 PHÂN TÍCH NGÀY 2025-09-25")
print("="*80)

target_date25 = pd.to_datetime('2025-09-25').date()

# Lọc data ngày 25
soc_day25 = soc_df[soc_df['date'] == target_date25].copy()
baseline_day25 = baseline_df[baseline_df['date'] == target_date25].copy()

print(f"\n📊 SOC data: {len(soc_day25)} records")
print(f"📊 Baseline data: {len(baseline_day25)} records")

# Baseline theo giờ
baseline_hourly25 = baseline_day25.groupby('hour')['基準値'].agg(['mean', 'min', 'max', 'count']).reset_index()

print("\n📈 Baseline theo giờ (ngày 25/9):")
print(baseline_hourly25.to_string())

# SOC afternoon
print("\n" + "="*80)
print("🎯 FOCUS: Khoảng 14-19h (SOC từng phút)")
print("="*80)

soc_afternoon25 = soc_day25[(soc_day25['hour'] >= 14) & (soc_day25['hour'] < 19)].copy()

soc_afternoon_summary25 = soc_afternoon25.groupby('hour')['SOC(%)'].agg(['min', 'max', 'mean', 'count']).reset_index()
print("\nTóm tắt SOC theo giờ:")
print(soc_afternoon_summary25.to_string())

# Xem chi tiết
for h in [15, 16, 17]:
    soc_hour = soc_afternoon25[soc_afternoon25['hour'] == h]
    baseline_hour = baseline_day25[baseline_day25['hour'] == h]
    
    print(f"\n⏰ Giờ {h}:00-{h}:59")
    print(f"   SOC: {soc_hour['SOC(%)'].min():.1f}% → {soc_hour['SOC(%)'].max():.1f}%")
    print(f"   Baseline: {baseline_hour['基準値'].mean():.1f} kW (count: {len(baseline_hour)})")
    
    if soc_hour['SOC(%)'].max() - soc_hour['SOC(%)'].min() > 10:
        print(f"   ⚠️  SOC thay đổi lớn: {soc_hour['SOC(%)'].max() - soc_hour['SOC(%)'].min():.1f}%")

print("\n" + "="*80)
print("📊 TẠO VISUALIZATION")
print("="*80)

# Tạo figure với 4 subplots (2 ngày x 2 metrics)
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Ngày 22/9 - Baseline', 'Ngày 22/9 - SOC',
                    'Ngày 25/9 - Baseline', 'Ngày 25/9 - SOC'),
    specs=[[{"secondary_y": False}, {"secondary_y": False}],
           [{"secondary_y": False}, {"secondary_y": False}]],
    vertical_spacing=0.12,
    horizontal_spacing=0.1
)

# Ngày 22 - Baseline
baseline_day22_sorted = baseline_day22.sort_values('start_time')
fig.add_trace(
    go.Scatter(
        x=baseline_day22_sorted['start_time'],
        y=baseline_day22_sorted['基準値'],
        mode='lines+markers',
        name='基準値 (22/9)',
        line=dict(color='blue', width=2),
        marker=dict(size=4)
    ),
    row=1, col=1
)

# Highlight 15-18h
fig.add_vrect(
    x0=pd.Timestamp('2025-09-22 15:00:00'),
    x1=pd.Timestamp('2025-09-22 18:00:00'),
    fillcolor="red", opacity=0.1,
    layer="below", line_width=0,
    row=1, col=1
)

# Ngày 22 - SOC
soc_day22_sorted = soc_day22.sort_values('timestamp')
fig.add_trace(
    go.Scatter(
        x=soc_day22_sorted['timestamp'],
        y=soc_day22_sorted['SOC(%)'],
        mode='lines',
        name='SOC (22/9)',
        line=dict(color='green', width=1.5)
    ),
    row=1, col=2
)

fig.add_vrect(
    x0=pd.Timestamp('2025-09-22 15:00:00'),
    x1=pd.Timestamp('2025-09-22 18:00:00'),
    fillcolor="red", opacity=0.1,
    layer="below", line_width=0,
    row=1, col=2
)

# Ngày 25 - Baseline
baseline_day25_sorted = baseline_day25.sort_values('start_time')
fig.add_trace(
    go.Scatter(
        x=baseline_day25_sorted['start_time'],
        y=baseline_day25_sorted['基準値'],
        mode='lines+markers',
        name='基準値 (25/9)',
        line=dict(color='blue', width=2),
        marker=dict(size=4)
    ),
    row=2, col=1
)

fig.add_vrect(
    x0=pd.Timestamp('2025-09-25 15:00:00'),
    x1=pd.Timestamp('2025-09-25 18:00:00'),
    fillcolor="red", opacity=0.1,
    layer="below", line_width=0,
    row=2, col=1
)

# Ngày 25 - SOC
soc_day25_sorted = soc_day25.sort_values('timestamp')
fig.add_trace(
    go.Scatter(
        x=soc_day25_sorted['timestamp'],
        y=soc_day25_sorted['SOC(%)'],
        mode='lines',
        name='SOC (25/9)',
        line=dict(color='green', width=1.5)
    ),
    row=2, col=2
)

fig.add_vrect(
    x0=pd.Timestamp('2025-09-25 15:00:00'),
    x1=pd.Timestamp('2025-09-25 18:00:00'),
    fillcolor="red", opacity=0.1,
    layer="below", line_width=0,
    row=2, col=2
)

# Update axes
fig.update_xaxes(title_text="Time", row=1, col=1)
fig.update_xaxes(title_text="Time", row=1, col=2)
fig.update_xaxes(title_text="Time", row=2, col=1)
fig.update_xaxes(title_text="Time", row=2, col=2)

fig.update_yaxes(title_text="基準値 (kW)", row=1, col=1)
fig.update_yaxes(title_text="SOC (%)", row=1, col=2, range=[0, 100])
fig.update_yaxes(title_text="基準値 (kW)", row=2, col=1)
fig.update_yaxes(title_text="SOC (%)", row=2, col=2, range=[0, 100])

fig.update_layout(
    title_text="⚠️ PHÂN TÍCH HIỆN TƯỢNG: SOC giảm mạnh 15-18h khi không có 基準値<br>" +
               "<sub>Vùng đỏ: 15:00-18:00 (thời gian nghi ngờ)</sub>",
    height=800,
    showlegend=True
)

fig.write_html('anomaly_15_18h_analysis.html')
print("✅ Đã lưu: anomaly_15_18h_analysis.html")

# Phân tích sâu hơn: Tính SOC change rate trong 15-18h
print("\n" + "="*80)
print("🔬 PHÂN TÍCH SÂU: Tính tốc độ thay đổi SOC")
print("="*80)

def analyze_soc_change_rate(soc_data, hour_start, hour_end, day_name):
    """Tính tốc độ thay đổi SOC trong khoảng thời gian"""
    subset = soc_data[(soc_data['hour'] >= hour_start) & (soc_data['hour'] < hour_end)].copy()
    
    if len(subset) == 0:
        print(f"\n{day_name}: Không có data trong {hour_start}-{hour_end}h")
        return
    
    subset = subset.sort_values('timestamp')
    
    soc_start = subset.iloc[0]['SOC(%)']
    soc_end = subset.iloc[-1]['SOC(%)']
    time_start = subset.iloc[0]['timestamp']
    time_end = subset.iloc[-1]['timestamp']
    
    duration_hours = (time_end - time_start).total_seconds() / 3600
    soc_change = soc_end - soc_start
    
    if duration_hours > 0:
        rate = soc_change / duration_hours
    else:
        rate = 0
    
    print(f"\n{day_name} ({hour_start}:00-{hour_end}:00):")
    print(f"  SOC: {soc_start:.1f}% → {soc_end:.1f}% (Δ = {soc_change:+.1f}%)")
    print(f"  Thời gian: {duration_hours:.2f} giờ")
    print(f"  Tốc độ: {rate:.2f} %/giờ")
    
    if abs(rate) > 10:
        print(f"  ⚠️  Tốc độ thay đổi BẤT THƯỜNG (>{10}%/giờ)!")

analyze_soc_change_rate(soc_day22, 15, 18, "Ngày 22/9")
analyze_soc_change_rate(soc_day25, 15, 18, "Ngày 25/9")

# So sánh với các giờ khác
analyze_soc_change_rate(soc_day22, 9, 12, "Ngày 22/9 (09-12h)")
analyze_soc_change_rate(soc_day25, 9, 12, "Ngày 25/9 (09-12h)")

print("\n" + "="*80)
print("💡 KẾT LUẬN")
print("="*80)
print("""
Nếu thực sự có hiện tượng:
- SOC giảm từ ~91% → ~5% trong 3 giờ (15-18h)
- Khi không có 基準値 (baseline = 0)

Thì có thể có các giả thuyết:
1. ⚡ Pin đang XẢ (discharge) mà không được ghi nhận trong 基準値
   → Có thể do: load thực tế, tổn thất, hoặc lỗi đo
   
2. 📊 Dữ liệu 基準値 bị thiếu hoặc lỗi trong khoảng 15-18h
   → Thực tế có xả nhưng không được ghi
   
3. 🔧 Có hệ thống khác (không phải baseline) đang sử dụng pin
   → Ví dụ: emergency load, backup system

Điều này ảnh hưởng ĐẾN:
- Công thức hồi quy hiện tại (giả định ΔSOC chỉ phụ thuộc 基準値)
- Tổng 基準値 = 1665kW (tính toán dựa trên công thức)
- Độ chính xác của mô hình tối ưu

➡️  CẦN KIỂM TRA KỸ DỮ LIỆU GỐC!
""")

print("\n✅ Script hoàn tất!")
