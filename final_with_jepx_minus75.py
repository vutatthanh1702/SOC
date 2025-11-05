#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHÂN TÍCH LẠI: JEPX XẢ TỪ 80% → 5% = -75%
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("="*80)
print("🔍 PHÂN TÍCH JEPX DISCHARGE THỰC TẾ")
print("="*80)

print("""
📊 DATA THỰC TẾ (từ bạn):
15:00-18:00 (3h): JEPX xả từ 80% → 5%
→ ΔSOC = -75% trong 3 giờ!

❌ TÍNH TOÁN TRƯỚC SAI:
- Dùng công thức: ΔSOC = (0.013545 × (-950) - 2.8197) × 3
- Kết quả: ΔSOC = -47.06%
- SAI vì: Công thức chỉ áp dụng cho BASELINE, không phải JEPX!

✅ HIỂU ĐÚNG:
JEPX = Bán điện ra thị trường trực tiếp
→ KHÔNG đi qua hệ thống baseline
→ Công thức regression KHÔNG áp dụng
→ Phải dùng GIÁ TRỊ THỰC TẾ từ data
""")

# JEPX effect thực tế
JEPX_DELTA_REAL = -75.0  # % trong 3h

print(f"\n✅ GIÁ TRỊ ĐÚNG:")
print(f"   JEPX discharge (3h): ΔSOC = {JEPX_DELTA_REAL}%")

print("\n" + "="*80)
print("🔄 TÍNH LẠI PATTERN TỐI ƯU")
print("="*80)

# Constants cho baseline
SLOPE = 0.013545
INTERCEPT = -2.8197

def calc_delta_baseline(b):
    """Chỉ dùng cho BASELINE blocks"""
    return (SLOPE * b + INTERCEPT) * 3

print("""
Cấu trúc pattern:
- N_baseline blocks: Tham gia 需給調整市場 (có 基準値)
- 1 JEPX block: Xả -75% (từ data thực tế)
- N_free blocks: Không ảnh hưởng (ΔSOC ≈ 0%)

Constraint cycle:
Σ(ΔSOC_baseline) + JEPX_delta + N_free × 0 = 0
Σ(ΔSOC_baseline) = -(-75%) = +75%
""")

target_delta_baseline = -JEPX_DELTA_REAL
print(f"\nCần: Σ(ΔSOC_baseline) = {target_delta_baseline}%")

# Thử các số lượng baseline blocks
results = []

for n_baseline in range(1, 8):
    # Tính tổng baseline cần
    # Σ(ΔSOC) = 3 × SLOPE × Σ(b) + 3 × n × INTERCEPT
    # → Σ(b) = (Σ(ΔSOC) - 3 × n × INTERCEPT) / (3 × SLOPE)
    
    sum_baseline = (target_delta_baseline - 3 * n_baseline * INTERCEPT) / (3 * SLOPE)
    
    if sum_baseline < 0:
        continue
    
    # Tìm pattern: N blocks @ 2000kW, rest @ X
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
        
        # Simulate SOC
        soc = 5.0
        max_soc = soc
        min_soc = soc
        valid = True
        
        # Baseline blocks
        for _ in range(n_max):
            soc += calc_delta_baseline(2000)
            max_soc = max(max_soc, soc)
            if soc > 90:
                valid = False
                break
        
        if not valid:
            continue
        
        for _ in range(remaining):
            soc += calc_delta_baseline(x)
            max_soc = max(max_soc, soc)
            if soc > 90:
                valid = False
                break
        
        if not valid:
            continue
        
        # JEPX
        soc_before_jepx = soc
        soc += JEPX_DELTA_REAL
        min_soc = min(min_soc, soc)
        
        if soc < 5:
            valid = False
            continue
        
        # Check cycle
        if abs(soc - 5.0) > 0.1:
            continue
        
        results.append({
            'n_baseline': n_baseline,
            'n_jepx': 1,
            'n_free': 8 - n_baseline - 1,
            'n_max': n_max,
            'x': x,
            'sum_baseline': sum_baseline,
            'max_soc': max_soc,
            'min_soc': min_soc,
            'soc_before_jepx': soc_before_jepx
        })
        break

# Sort by sum_baseline
results.sort(key=lambda r: r['sum_baseline'], reverse=True)

print(f"\n✅ Tìm thấy {len(results)} patterns hợp lệ\n")

for i, r in enumerate(results[:5], 1):
    print(f"{i}. {r['n_baseline']} baseline + {r['n_jepx']} JEPX + {r['n_free']} free:")
    print(f"   Pattern: {r['n_max']} blocks @2000kW + {r['n_baseline']-r['n_max']} blocks @{r['x']:.0f}kW")
    print(f"   Σ(基準値) = {r['sum_baseline']:.0f}kW")
    print(f"   SOC range: {r['min_soc']:.1f}% - {r['max_soc']:.1f}%")
    print(f"   SOC trước JEPX: {r['soc_before_jepx']:.1f}%")
    print()

if results:
    best = results[0]
    
    print("="*80)
    print("🏆 PATTERN TỐI ƯU NHẤT")
    print("="*80)
    
    n_free = best['n_free']
    
    print(f"""
Cấu trúc:
- {best['n_baseline']} blocks BASELINE (需給調整市場)
- {best['n_jepx']} block JEPX (bán điện)
- {n_free} blocks FREE (nghỉ)

Chi tiết baseline:
- {best['n_max']} blocks @ 2000kW (charge MAX)
- {best['n_baseline'] - best['n_max']} blocks @ {best['x']:.0f}kW

Kết quả:
- Tổng 基準値: {best['sum_baseline']:.0f}kW
- So với 8 blocks (1665kW): {best['sum_baseline'] - 1665:+.0f}kW ({(best['sum_baseline']/1665 - 1)*100:+.1f}%)
- SOC range: {best['min_soc']:.1f}% - {best['max_soc']:.1f}%
- SOC trước JEPX: {best['soc_before_jepx']:.1f}%
""")
    
    print("\n" + "="*80)
    print("📊 SIMULATION CHI TIẾT")
    print("="*80)
    
    # Create schedule
    schedule = []
    soc = 5.0
    block_num = 1
    
    print(f"\n{'Block':<6} {'Time':<15} {'Type':<15} {'Baseline':<12} {'ΔSOC':<10} {'SOC':<20}")
    print("-" * 85)
    
    # FREE blocks đầu
    for i in range(n_free):
        time_start = (block_num - 1) * 3
        time_end = block_num * 3
        time_str = f"{time_start:02d}:00-{time_end:02d}:00"
        
        schedule.append({
            'block': block_num,
            'time': time_str,
            'type': 'FREE',
            'baseline': float('nan'),
            'delta_soc': 0,
            'soc_start': soc,
            'soc_end': soc
        })
        
        print(f"{block_num:<6} {time_str:<15} {'FREE':<15} {'NaN':<12} {0:>+6.1f}%   {soc:>5.1f}% → {soc:>5.1f}%")
        block_num += 1
    
    # Baseline blocks - MAX charge
    for i in range(best['n_max']):
        time_start = (block_num - 1) * 3
        time_end = block_num * 3
        time_str = f"{time_start:02d}:00-{time_end:02d}:00"
        
        delta = calc_delta_baseline(2000)
        soc_before = soc
        soc += delta
        
        schedule.append({
            'block': block_num,
            'time': time_str,
            'type': 'BASELINE',
            'baseline': 2000,
            'delta_soc': delta,
            'soc_start': soc_before,
            'soc_end': soc
        })
        
        print(f"{block_num:<6} {time_str:<15} {'BASELINE':<15} {2000:<6}kW     {delta:>+6.1f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")
        block_num += 1
    
    # Baseline blocks - X charge
    for i in range(best['n_baseline'] - best['n_max']):
        time_start = (block_num - 1) * 3
        time_end = block_num * 3
        time_str = f"{time_start:02d}:00-{time_end:02d}:00"
        
        delta = calc_delta_baseline(best['x'])
        soc_before = soc
        soc += delta
        
        schedule.append({
            'block': block_num,
            'time': time_str,
            'type': 'BASELINE',
            'baseline': best['x'],
            'delta_soc': delta,
            'soc_start': soc_before,
            'soc_end': soc
        })
        
        print(f"{block_num:<6} {time_str:<15} {'BASELINE':<15} {best['x']:<6.0f}kW     {delta:>+6.1f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")
        block_num += 1
    
    # JEPX block
    time_start = (block_num - 1) * 3
    time_end = block_num * 3
    time_str = f"{time_start:02d}:00-{time_end:02d}:00"
    
    soc_before = soc
    soc += JEPX_DELTA_REAL
    
    schedule.append({
        'block': block_num,
        'time': time_str,
        'type': 'JEPX',
        'baseline': float('nan'),
        'delta_soc': JEPX_DELTA_REAL,
        'soc_start': soc_before,
        'soc_end': soc
    })
    
    print(f"{block_num:<6} {time_str:<15} {'JEPX':<15} {'NaN':<12} {JEPX_DELTA_REAL:>+6.1f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")
    
    print(f"\n{'='*85}")
    print(f"Kết quả: Cycle {5.0}% → {soc:.1f}% (Error: {soc - 5.0:.2f}%)")
    
    # Visualization
    print("\n" + "="*80)
    print("📊 TẠO VISUALIZATION")
    print("="*80)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            'Baseline Schedule + JEPX',
            'SOC Evolution'
        ),
        vertical_spacing=0.15
    )
    
    # Plot 1: Baseline (chỉ blocks có baseline)
    baseline_blocks = [s for s in schedule if s['type'] == 'BASELINE']
    baseline_idx = [s['block'] for s in baseline_blocks]
    baseline_values = [s['baseline'] for s in baseline_blocks]
    
    fig.add_trace(
        go.Bar(
            x=baseline_idx,
            y=baseline_values,
            name='基準値',
            marker_color='lightblue',
            text=[f'{v:.0f}kW' for v in baseline_values],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Mark JEPX
    jepx_block = [s for s in schedule if s['type'] == 'JEPX'][0]
    fig.add_trace(
        go.Scatter(
            x=[jepx_block['block']],
            y=[0],
            mode='markers+text',
            marker=dict(size=20, color='red', symbol='x'),
            text=['JEPX<br>-75%'],
            textposition='top center',
            name='JEPX',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Plot 2: SOC
    soc_trajectory = [5.0] + [s['soc_end'] for s in schedule]
    
    fig.add_trace(
        go.Scatter(
            x=list(range(0, len(schedule) + 1)),
            y=soc_trajectory,
            mode='lines+markers',
            name='SOC',
            line=dict(color='green', width=3),
            marker=dict(size=10)
        ),
        row=2, col=1
    )
    
    # Mark JEPX discharge
    fig.add_annotation(
        x=jepx_block['block'],
        y=jepx_block['soc_start'],
        text=f"JEPX<br>{jepx_block['soc_start']:.0f}%→{jepx_block['soc_end']:.0f}%",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-60,
        row=2, col=1
    )
    
    # SOC limits
    fig.add_hline(y=5, line_dash="dash", line_color="orange", 
                  annotation_text="Min 5%", row=2, col=1)
    fig.add_hline(y=90, line_dash="dash", line_color="red", 
                  annotation_text="Max 90%", row=2, col=1)
    
    fig.update_xaxes(title_text="Block", row=1, col=1)
    fig.update_xaxes(title_text="Block", row=2, col=1)
    fig.update_yaxes(title_text="基準値 (kW)", row=1, col=1)
    fig.update_yaxes(title_text="SOC (%)", row=2, col=1, range=[0, 100])
    
    fig.update_layout(
        title_text=f"🏆 PATTERN TỐI ƯU (JEPX = -75%)<br>" +
                   f"<sub>Tổng 基準値: {best['sum_baseline']:.0f}kW " +
                   f"({(best['sum_baseline']/1665 - 1)*100:+.1f}% vs 8 blocks)</sub>",
        height=900
    )
    
    fig.write_html('optimal_pattern_jepx_minus75.html')
    print("✅ Đã lưu: optimal_pattern_jepx_minus75.html")
    
    # Save schedule
    df = pd.DataFrame(schedule)
    df.to_csv('optimal_schedule_jepx_minus75.csv', index=False)
    print("✅ Đã lưu: optimal_schedule_jepx_minus75.csv")
    
    print("\n" + "="*80)
    print("💡 KẾT LUẬN")
    print("="*80)
    
    print(f"""
✅ VỚI JEPX THỰC TẾ = -75%:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pattern tối ưu:
- {best['n_baseline']} blocks BASELINE: Tổng {best['sum_baseline']:.0f}kW
- 1 block JEPX: Xả từ ~{best['soc_before_jepx']:.0f}% → 5%
- {n_free} blocks FREE: Không ảnh hưởng

So sánh:
- 8 blocks không JEPX: 1,665kW
- Pattern này: {best['sum_baseline']:.0f}kW
- Chênh lệch: {best['sum_baseline'] - 1665:+.0f}kW ({(best['sum_baseline']/1665 - 1)*100:+.1f}%)

✅ LỢI ÍCH:
- Tăng baseline {(best['sum_baseline']/1665 - 1)*100:.1f}%
- JEPX xả mạnh (-75%) giúp về đúng 5%
- Chu kỳ ổn định hàng ngày
""")

print("\n✅ Hoàn tất!")
