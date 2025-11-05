#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TỐI ƯU HÓA KHI CÓ JEPX - Có thể xả nhanh bằng cách bán cho JEPX
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197
HOURS_PER_BLOCK = 3

SOC_MIN = 10  # %
SOC_MAX = 90  # %
BASELINE_MAX = 2000  # kW
JEPX_DISCHARGE = 950  # kW (từ data thực tế)

print("="*80)
print("🚀 TỐI ƯU HÓA VỚI KHẢ NĂNG BÁN JEPX")
print("="*80)

print("""
💡 Ý TƯỞNG MỚI:
- Có thể xả NHANH bằng JEPX (950kW) thay vì chờ tự nhiên (0kW)
- Điều này cho phép:
  1. Xả nhanh về SOC thấp để sẵn sàng sạc lại
  2. Tăng được tổng 基準値 trong ngày
  3. Kiếm thêm tiền từ bán điện JEPX

📊 PHÂN TÍCH:
""")

def calculate_soc_change(baseline_kw, hours=3):
    """Tính thay đổi SOC (%) dựa trên baseline và thời gian"""
    rate = SLOPE * baseline_kw + INTERCEPT
    return rate * hours

def calculate_jepx_discharge_effect(hours=3):
    """Tính hiệu ứng xả qua JEPX"""
    # Từ data thực tế: 950kW × 3h, SOC giảm ~87%
    # → Rate ≈ -29%/h
    # Nhưng để chính xác, tính theo công thức:
    rate = SLOPE * (-JEPX_DISCHARGE) + INTERCEPT  # Negative vì xả
    return rate * hours

# Test JEPX discharge
jepx_effect = calculate_jepx_discharge_effect(3)
print(f"JEPX discharge (950kW × 3h): ΔSOC = {jepx_effect:.1f}%")

# Tính các mốc quan trọng
charge_max_3h = calculate_soc_change(BASELINE_MAX, 3)
discharge_zero_3h = calculate_soc_change(0, 3)
discharge_jepx_3h = jepx_effect

print(f"\nCác rate cơ bản (3h):")
print(f"  Sạc MAX (2000kW):     +{charge_max_3h:.1f}%")
print(f"  Nghỉ (0kW):           {discharge_zero_3h:.1f}%")
print(f"  Xả JEPX (950kW):      {discharge_jepx_3h:.1f}%")

print("\n" + "="*80)
print("🎯 STRATEGY MỚI: Tối đa hóa charge bằng cách xả nhanh qua JEPX")
print("="*80)

print("""
Pattern ý tưởng của bạn:
- Block 8 (21:00-24:00): Xả JEPX xuống SOC thấp (~5%)
- Block 1 (00:00-03:00): Sạc mạnh (2000kW)
- Block 2-7: Điều chỉnh để duy trì chu kỳ

Nhưng có VẤN ĐỀ:
1. Công thức: ΔSOC = 0.013545 × 基準値 - 2.8197
   → Với 基準値 là CHARGE/DISCHARGE trong hệ thống baseline
   → JEPX là bán điện RA NGOÀI, không phải trong công thức này

2. Để chu kỳ ổn định (SOC cuối = SOC đầu):
   Σ(ΔSOC_baseline) + ΔSOC_jepx = 0
   
Hãy tính toán cụ thể:
""")

print("\n" + "="*80)
print("📊 SCENARIO 1: Dùng JEPX để xả, tăng charge ở blocks khác")
print("="*80)

# Scenario: 3 blocks charge MAX, 1 block JEPX discharge, 4 blocks điều chỉnh
scenarios = []

# Pattern 1: Charge mạnh nhiều blocks, cuối ngày xả JEPX
pattern1 = {
    'name': 'Pattern 1: 3 blocks MAX charge + 1 JEPX + 4 blocks điều chỉnh',
    'blocks': [
        {'time': '00:00-03:00', 'baseline': 2000, 'type': 'charge'},
        {'time': '03:00-06:00', 'baseline': 2000, 'type': 'charge'},
        {'time': '06:00-09:00', 'baseline': 2000, 'type': 'charge'},
        {'time': '09:00-12:00', 'baseline': 0, 'type': 'rest'},
        {'time': '12:00-15:00', 'baseline': 0, 'type': 'rest'},
        {'time': '15:00-18:00', 'baseline': 0, 'type': 'rest'},
        {'time': '18:00-21:00', 'baseline': 0, 'type': 'rest'},
        {'time': '21:00-24:00', 'baseline': 'JEPX', 'type': 'jepx_discharge'},
    ]
}

# Tính toán cho pattern 1
soc = 5.0  # Start từ 5% sau khi xả JEPX của ngày trước
print(f"\nPattern 1 Simulation:")
print(f"{'Block':<5} {'Time':<15} {'Baseline':<12} {'SOC Start':<12} {'ΔSOC':<10} {'SOC End':<12}")
print("-" * 80)

total_baseline = 0
soc_changes = []

for i, block in enumerate(pattern1['blocks'], 1):
    soc_start = soc
    
    if block['baseline'] == 'JEPX':
        # JEPX: Xả 950kW, nhưng KHÔNG tính vào baseline plan
        delta_soc = jepx_effect
        print(f"  {i:<5} {block['time']:<15} {'JEPX 950kW':<12} {soc_start:>6.1f}%     {delta_soc:>+6.1f}%   ", end="")
    else:
        delta_soc = calculate_soc_change(block['baseline'], 3)
        total_baseline += block['baseline']
        print(f"  {i:<5} {block['time']:<15} {block['baseline']:>6}kW     {soc_start:>6.1f}%     {delta_soc:>+6.1f}%   ", end="")
    
    soc = soc_start + delta_soc
    soc_changes.append(delta_soc)
    
    # Check limits
    if soc < SOC_MIN or soc > SOC_MAX:
        print(f"{soc:>6.1f}% ❌ VƯỢT HẠN")
    else:
        print(f"{soc:>6.1f}% ✅")

print(f"\n{'='*80}")
print(f"Tổng 基準値 (baseline only): {total_baseline} kW")
print(f"SOC cycle: {5.0}% → {soc:.1f}% (Error: {soc - 5.0:+.1f}%)")
print(f"Tổng ΔSOC: {sum(soc_changes):.1f}%")

print("\n" + "="*80)
print("⚠️  VẤN ĐỀ PHÁT HIỆN")
print("="*80)

print("""
Vấn đề 1: KHÔNG CYCLE được!
- 3 blocks × 2000kW × 3h: ΔSOC ≈ +75% × 3 = +225%
- 4 blocks × 0kW × 3h: ΔSOC ≈ -8.5% × 4 = -34%
- 1 block JEPX: ΔSOC ≈ -40.8%
- Tổng: +225% - 34% - 40.8% = +150.2%
→ SOC tăng liên tục, không về được 5%!

Vấn đề 2: Tổng 基準値 KHÔNG TỰ DO
- Để cycle (không kể JEPX): Σ(基準値_baseline) phải thỏa mãn
  Σ(ΔSOC_baseline) = -ΔSOC_jepx
  
Hãy tính chính xác:
""")

print("\n" + "="*80)
print("🔬 TÍNH TOÁN CHÍNH XÁC: Tổng 基準値 khi có JEPX")
print("="*80)

# JEPX effect
delta_soc_jepx = jepx_effect

# Để cycle: Σ(ΔSOC_baseline) + ΔSOC_jepx = 0
# → Σ(ΔSOC_baseline) = -ΔSOC_jepx
sum_delta_soc_needed = -delta_soc_jepx

print(f"JEPX discharge effect: ΔSOC = {delta_soc_jepx:.2f}%")
print(f"Cần: Σ(ΔSOC_baseline) = {sum_delta_soc_needed:.2f}%")
print()

# Với N blocks baseline:
# Σ(ΔSOC) = Σ((SLOPE × b_i + INTERCEPT) × 3)
#         = 3 × SLOPE × Σ(b_i) + 3 × N × INTERCEPT

# Giải: Σ(b_i) = (Σ(ΔSOC) - 3 × N × INTERCEPT) / (3 × SLOPE)

n_baseline_blocks = 7  # 8 blocks total - 1 JEPX

sum_baseline_needed = (sum_delta_soc_needed - 3 * n_baseline_blocks * INTERCEPT) / (3 * SLOPE)

print(f"Với {n_baseline_blocks} blocks baseline:")
print(f"Σ(基準値) = ({sum_delta_soc_needed:.2f} - 3 × {n_baseline_blocks} × {INTERCEPT}) / (3 × {SLOPE})")
print(f"Σ(基準値) = {sum_baseline_needed:.2f} kW")
print()

print(f"So sánh:")
print(f"  Không có JEPX (8 blocks): Σ(基準値) = 1665.38 kW")
print(f"  Có JEPX (7 blocks):       Σ(基準値) = {sum_baseline_needed:.2f} kW")
print(f"  Chênh lệch:                          {sum_baseline_needed - 1665.38:+.2f} kW")
print()

if sum_baseline_needed > 1665.38:
    print(f"✅ TĂNG ĐƯỢC {sum_baseline_needed - 1665.38:.2f} kW!")
    print(f"   Tăng {(sum_baseline_needed - 1665.38) / 1665.38 * 100:.1f}%")
else:
    print(f"❌ GIẢM {1665.38 - sum_baseline_needed:.2f} kW")

print("\n" + "="*80)
print("🎯 PATTERN TỐI ƯU VỚI JEPX")
print("="*80)

# Tính pattern tối ưu
# Để maximize charge, dùng càng nhiều blocks ở 2000kW càng tốt

print(f"\nTarget: Σ(基準値) = {sum_baseline_needed:.2f} kW cho 7 blocks")
print(f"Trung bình: {sum_baseline_needed / 7:.2f} kW/block")
print()

# Strategy: N blocks @ 2000kW, (7-N) blocks @ X kW
# N × 2000 + (7-N) × X = sum_baseline_needed

print("Các pattern khả thi:\n")

patterns = []
for n_max in range(0, 8):
    if n_max > 7:
        continue
    
    remaining_blocks = 7 - n_max
    if remaining_blocks == 0:
        x = 0
    else:
        x = (sum_baseline_needed - n_max * 2000) / remaining_blocks
    
    # Check constraints
    if x < 0 or x > BASELINE_MAX:
        status = "❌ Invalid (X out of range)"
    else:
        status = "✅ Valid"
    
    patterns.append({
        'n_max': n_max,
        'remaining': remaining_blocks,
        'x': x,
        'status': status
    })
    
    print(f"  {n_max} blocks @ 2000kW + {remaining_blocks} blocks @ {x:.1f}kW → {status}")

print("\n" + "="*80)
print("💎 PATTERN TỐI ƯU NHẤT")
print("="*80)

# Tìm pattern với max blocks @ 2000kW
valid_patterns = [p for p in patterns if '✅' in p['status']]

if valid_patterns:
    best = max(valid_patterns, key=lambda p: p['n_max'])
    
    print(f"\nPattern tối ưu:")
    print(f"  {best['n_max']} blocks @ 2000kW (charge MAX)")
    print(f"  {best['remaining']} blocks @ {best['x']:.1f}kW")
    print(f"  1 block JEPX discharge (950kW)")
    print(f"  Tổng 基準値: {sum_baseline_needed:.2f} kW")
    
    # Simulate pattern tối ưu
    print(f"\nSimulation:")
    
    soc = 5.0
    print(f"{'Block':<6} {'Time':<15} {'Type':<20} {'Baseline':<12} {'ΔSOC':<10} {'SOC':<10}")
    print("-" * 85)
    
    schedule = []
    
    # Arrange blocks: JEPX ở cuối để kết thúc ngày
    for i in range(best['n_max']):
        time_start = i * 3
        time_end = (i + 1) * 3
        time_str = f"{time_start:02d}:00-{time_end:02d}:00"
        
        delta = calculate_soc_change(2000, 3)
        schedule.append({
            'block': i + 1,
            'time': time_str,
            'type': 'Charge MAX',
            'baseline': 2000,
            'delta_soc': delta,
            'soc_start': soc
        })
        
        print(f"  {i+1:<6} {time_str:<15} {'Charge MAX':<20} {2000:>6}kW      {delta:>+6.1f}%   {soc:>6.1f}% → {soc+delta:>6.1f}%")
        soc += delta
    
    for i in range(best['remaining']):
        block_num = best['n_max'] + i
        time_start = block_num * 3
        time_end = (block_num + 1) * 3
        time_str = f"{time_start:02d}:00-{time_end:02d}:00"
        
        delta = calculate_soc_change(best['x'], 3)
        type_str = f'Charge {best["x"]:.0f}kW'
        schedule.append({
            'block': block_num + 1,
            'time': time_str,
            'type': type_str,
            'baseline': best['x'],
            'delta_soc': delta,
            'soc_start': soc
        })
        
        print(f"  {block_num+1:<6} {time_str:<15} {type_str:<20} {best['x']:>6.0f}kW      {delta:>+6.1f}%   {soc:>6.1f}% → {soc+delta:>6.1f}%")
        soc += delta
    
    # JEPX block cuối
    time_str = "21:00-24:00"
    delta = jepx_effect
    schedule.append({
        'block': 8,
        'time': time_str,
        'type': 'JEPX Discharge',
        'baseline': 'JEPX',
        'delta_soc': delta,
        'soc_start': soc
    })
    
    print(f"  {8:<6} {time_str:<15} {'JEPX Discharge':<20} {'950kW':>9}   {delta:>+6.1f}%   {soc:>6.1f}% → {soc+delta:>6.1f}%")
    soc += delta
    
    print(f"\n{'='*85}")
    print(f"Kết quả:")
    print(f"  SOC: 5.0% → {soc:.1f}% (Cycle error: {soc - 5.0:+.2f}%)")
    print(f"  Tổng 基準値 (7 blocks baseline): {sum_baseline_needed:.2f} kW")
    print(f"  JEPX discharge: 950kW (block 8)")
    
    # Create visualization
    print("\n" + "="*80)
    print("📊 TẠO VISUALIZATION")
    print("="*80)
    
    # Prepare data for plotting
    blocks = list(range(1, 9))
    baselines = [2000] * best['n_max'] + [best['x']] * best['remaining'] + [0]  # 0 for JEPX display
    socs = [5.0]
    
    current_soc = 5.0
    for item in schedule:
        current_soc += item['delta_soc']
        socs.append(current_soc)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('基準値 + JEPX Discharge', 'SOC Evolution'),
        vertical_spacing=0.15,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Plot baseline
    fig.add_trace(
        go.Bar(
            x=blocks[:-1],
            y=baselines[:-1],
            name='基準値 (Baseline)',
            marker_color='lightblue'
        ),
        row=1, col=1
    )
    
    # Mark JEPX
    fig.add_trace(
        go.Bar(
            x=[8],
            y=[950],
            name='JEPX Discharge',
            marker_color='red'
        ),
        row=1, col=1
    )
    
    # Plot SOC
    fig.add_trace(
        go.Scatter(
            x=list(range(0, 9)),
            y=socs,
            mode='lines+markers',
            name='SOC',
            line=dict(color='green', width=3),
            marker=dict(size=8)
        ),
        row=2, col=1
    )
    
    # Add SOC limits
    fig.add_hline(y=SOC_MIN, line_dash="dash", line_color="red", annotation_text="SOC Min (10%)", row=2, col=1)
    fig.add_hline(y=SOC_MAX, line_dash="dash", line_color="red", annotation_text="SOC Max (90%)", row=2, col=1)
    
    fig.update_xaxes(title_text="Block", row=1, col=1)
    fig.update_xaxes(title_text="Block", row=2, col=1)
    fig.update_yaxes(title_text="Power (kW)", row=1, col=1)
    fig.update_yaxes(title_text="SOC (%)", row=2, col=1, range=[0, 100])
    
    fig.update_layout(
        title_text=f"🚀 PATTERN TỐI ƯU VỚI JEPX<br><sub>Tổng 基準値: {sum_baseline_needed:.0f}kW (+{sum_baseline_needed - 1665.38:.0f}kW so với không JEPX)</sub>",
        height=800,
        showlegend=True
    )
    
    fig.write_html('optimal_pattern_with_jepx.html')
    print("✅ Đã lưu: optimal_pattern_with_jepx.html")
    
    # Save schedule
    schedule_df = pd.DataFrame(schedule)
    schedule_df.to_csv('optimal_schedule_with_jepx.csv', index=False)
    print("✅ Đã lưu: optimal_schedule_with_jepx.csv")

print("\n✅ Hoàn tất!")
