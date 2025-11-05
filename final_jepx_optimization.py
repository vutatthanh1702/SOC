#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TỐI ƯU HÓA ĐÚNG: SOC về 5% và baseline KHÔNG ÂM
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197

SOC_MIN = 5   # ✅ Sửa: Cho phép về 5%
SOC_MAX = 90
BASELINE_MIN = 0  # ✅ Baseline không được âm!
BASELINE_MAX = 2000

print("="*80)
print("🚀 TỐI ƯU HÓA ĐÚNG VỚI JEPX")
print("="*80)

print("""
✅ ĐIỀU KIỆN MỚI:
1. SOC range: 5% - 90% (85% range)
2. Baseline: 0 - 2000kW (KHÔNG ÂM!)
3. Nếu cần xả → Dùng JEPX thay vì baseline âm
""")

def calc_delta(b):
    return (SLOPE * b + INTERCEPT) * 3

# JEPX effect
jepx_delta = calc_delta(-950)

print(f"\nJEPX discharge: ΔSOC = {jepx_delta:.2f}%")
print(f"SOC range: {SOC_MAX - SOC_MIN}%")

print("\n" + "="*80)
print("🔬 TÍNH TOÁN VỚI SOC MIN = 5%")
print("="*80)

# Bắt đầu từ 5%, charge MAX lên bao nhiêu?
delta_charge_max = calc_delta(BASELINE_MAX)
soc_after_charge = SOC_MIN + delta_charge_max

print(f"1 block @ 2000kW:")
print(f"  Start: {SOC_MIN}%")
print(f"  ΔSOC = +{delta_charge_max:.2f}%")
print(f"  End: {soc_after_charge:.2f}%")

if soc_after_charge > SOC_MAX:
    print(f"  ❌ VƯỢT SOC_MAX ({SOC_MAX}%)")
    # Tính baseline tối đa để không vượt
    max_delta = SOC_MAX - SOC_MIN
    # (SLOPE × b + INTERCEPT) × 3 = max_delta
    baseline_safe = (max_delta / 3 - INTERCEPT) / SLOPE
    print(f"  → Baseline MAX an toàn: {baseline_safe:.2f}kW")
else:
    print(f"  ✅ OK (< {SOC_MAX}%)")

# Tính số blocks charge MAX tối đa
available_range = SOC_MAX - SOC_MIN  # 85%
n_max_blocks = int(available_range / delta_charge_max)

print(f"\nSố blocks @ 2000kW tối đa:")
print(f"  Range available: {available_range}%")
print(f"  Per block: +{delta_charge_max:.2f}%")
print(f"  → N_max = {n_max_blocks} blocks")

print("\n" + "="*80)
print("🎯 STRATEGY: Maximize blocks @ 2000kW")
print("="*80)

print("""
Ý tưởng:
- Dùng nhiều blocks @ 2000kW nhất có thể
- Các blocks còn lại @ 0kW (rest, không xả)
- JEPX ở cuối để xả về 5%

Tính toán:
""")

# Với N blocks @ 2000kW
for n in range(n_max_blocks + 1, 0, -1):
    total_charge = n * delta_charge_max
    soc_peak = SOC_MIN + total_charge
    
    if soc_peak > SOC_MAX:
        continue
    
    print(f"\n{n} blocks @ 2000kW:")
    print(f"  SOC: {SOC_MIN}% → {soc_peak:.2f}%")
    
    # Sau JEPX
    soc_after_jepx = soc_peak + jepx_delta
    print(f"  Sau JEPX: {soc_after_jepx:.2f}%")
    
    # Cần về 5%
    delta_remaining = SOC_MIN - soc_after_jepx
    print(f"  Cần về {SOC_MIN}%: {delta_remaining:+.2f}%")
    
    # Số blocks còn lại
    remaining_blocks = 7 - n
    
    if remaining_blocks == 0:
        if abs(delta_remaining) < 0.1:
            print(f"  ✅ Perfect cycle! (dùng hết 7 blocks)")
            n_optimal = n
            break
        else:
            print(f"  ❌ Không cycle được")
            continue
    
    # ΔSOC per block cần thiết
    delta_per_block = delta_remaining / remaining_blocks
    
    # Tính baseline tương ứng
    baseline_needed = (delta_per_block / 3 - INTERCEPT) / SLOPE
    
    print(f"  {remaining_blocks} blocks còn lại:")
    print(f"    Cần ΔSOC = {delta_per_block:.2f}% per block")
    print(f"    → Baseline = {baseline_needed:.2f}kW")
    
    if baseline_needed < BASELINE_MIN:
        print(f"    ❌ Baseline < 0 (KHÔNG HỢP LỆ)")
        print(f"    → Nếu cần xả thì dùng JEPX thêm, không dùng baseline âm!")
    elif baseline_needed > BASELINE_MAX:
        print(f"    ❌ Baseline > 2000kW")
    else:
        print(f"    ✅ HỢP LỆ!")
        n_optimal = n
        baseline_rest = baseline_needed
        break

print("\n" + "="*80)
print("💎 PATTERN TỐI ƯU")
print("="*80)

if 'n_optimal' in locals():
    print(f"\n✅ Tìm thấy pattern tối ưu:")
    print(f"  {n_optimal} blocks @ 2000kW (charge MAX)")
    print(f"  {7 - n_optimal} blocks @ {baseline_rest:.2f}kW")
    print(f"  1 block JEPX discharge (950kW)")
    
    total_baseline = n_optimal * 2000 + (7 - n_optimal) * baseline_rest
    
    print(f"\n  Tổng 基準値: {total_baseline:.2f}kW")
    print(f"  So với không JEPX (1665.38kW): +{total_baseline - 1665.38:.2f}kW")
    print(f"  Tăng: {(total_baseline / 1665.38 - 1) * 100:.1f}%")
    
    print("\n" + "="*80)
    print("📊 SIMULATION")
    print("="*80)
    
    soc = float(SOC_MIN)
    print(f"\n{'Block':<6} {'Time':<15} {'Type':<20} {'Baseline':<12} {'ΔSOC':<10} {'SOC':<20}")
    print("-" * 85)
    
    schedule = []
    
    # N blocks charge MAX
    for i in range(n_optimal):
        time_start = i * 3
        time_end = (i + 1) * 3
        time_str = f"{time_start:02d}:00-{time_end:02d}:00"
        
        delta = calc_delta(2000)
        soc_before = soc
        soc += delta
        
        schedule.append({
            'block': i + 1,
            'time': time_str,
            'type': 'Charge MAX',
            'baseline_kw': 2000,
            'delta_soc': delta,
            'soc_start': soc_before,
            'soc_end': soc
        })
        
        print(f"{i+1:<6} {time_str:<15} {'Charge MAX':<20} {2000:>6}kW       {delta:>+6.2f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")
    
    # Remaining blocks
    for i in range(7 - n_optimal):
        block_num = n_optimal + i + 1
        time_start = (block_num - 1) * 3
        time_end = block_num * 3
        time_str = f"{time_start:02d}:00-{time_end:02d}:00"
        
        delta = calc_delta(baseline_rest)
        soc_before = soc
        soc += delta
        
        type_str = 'Rest' if baseline_rest < 10 else f'Charge {baseline_rest:.0f}kW'
        
        schedule.append({
            'block': block_num,
            'time': time_str,
            'type': type_str,
            'baseline_kw': baseline_rest,
            'delta_soc': delta,
            'soc_start': soc_before,
            'soc_end': soc
        })
        
        print(f"{block_num:<6} {time_str:<15} {type_str:<20} {baseline_rest:>6.2f}kW       {delta:>+6.2f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")
    
    # JEPX
    time_str = "21:00-24:00"
    soc_before = soc
    soc += jepx_delta
    
    schedule.append({
        'block': 8,
        'time': time_str,
        'type': 'JEPX Discharge',
        'baseline_kw': 'JEPX -950',
        'delta_soc': jepx_delta,
        'soc_start': soc_before,
        'soc_end': soc
    })
    
    print(f"{8:<6} {time_str:<15} {'JEPX Discharge':<20} {'950kW':>9}   {jepx_delta:>+6.2f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")
    
    print(f"\n{'='*85}")
    print(f"Tổng 基準値: {total_baseline:.2f}kW")
    print(f"JEPX: 950kW (bán điện)")
    print(f"Cycle: {SOC_MIN}% → {soc:.2f}% (Error: {soc - SOC_MIN:.4f}%)")
    
    # Create visualization
    print("\n" + "="*80)
    print("📊 TẠO VISUALIZATION")
    print("="*80)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            f'Pattern Tối Ưu: {n_optimal} blocks MAX + {7-n_optimal} blocks Rest + 1 JEPX',
            'SOC Evolution'
        ),
        vertical_spacing=0.15,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Plot baseline
    blocks = list(range(1, 8))
    baselines_plot = [2000] * n_optimal + [baseline_rest] * (7 - n_optimal)
    
    colors = ['lightblue'] * n_optimal + ['lightgreen'] * (7 - n_optimal)
    
    fig.add_trace(
        go.Bar(
            x=blocks,
            y=baselines_plot,
            name='基準値',
            marker_color=colors,
            text=[f'{b:.0f}kW' for b in baselines_plot],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Add JEPX
    fig.add_trace(
        go.Bar(
            x=[8],
            y=[950],
            name='JEPX Discharge',
            marker_color='red',
            text=['JEPX<br>950kW'],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Plot SOC
    soc_trajectory = [s['soc_start'] for s in schedule] + [schedule[-1]['soc_end']]
    
    fig.add_trace(
        go.Scatter(
            x=list(range(0, 9)),
            y=soc_trajectory,
            mode='lines+markers',
            name='SOC',
            line=dict(color='green', width=3),
            marker=dict(size=10),
            text=[f'{s:.1f}%' for s in soc_trajectory],
            textposition='top center'
        ),
        row=2, col=1
    )
    
    # Add SOC limits
    fig.add_hline(y=SOC_MIN, line_dash="dash", line_color="orange", 
                  annotation_text=f"SOC Min ({SOC_MIN}%)", row=2, col=1)
    fig.add_hline(y=SOC_MAX, line_dash="dash", line_color="red", 
                  annotation_text=f"SOC Max ({SOC_MAX}%)", row=2, col=1)
    
    fig.update_xaxes(title_text="Block", row=1, col=1)
    fig.update_xaxes(title_text="Block", row=2, col=1)
    fig.update_yaxes(title_text="Power (kW)", row=1, col=1)
    fig.update_yaxes(title_text="SOC (%)", row=2, col=1, range=[0, 100])
    
    fig.update_layout(
        title_text=f"🚀 PATTERN TỐI ƯU VỚI JEPX<br>" +
                   f"<sub>Tổng 基準値: {total_baseline:.0f}kW " +
                   f"(+{total_baseline - 1665.38:.0f}kW, +{(total_baseline/1665.38 - 1)*100:.1f}%)</sub>",
        height=900,
        showlegend=True
    )
    
    fig.write_html('optimal_jepx_pattern_final.html')
    print("✅ Đã lưu: optimal_jepx_pattern_final.html")
    
    # Save schedule
    df = pd.DataFrame(schedule)
    df.to_csv('optimal_jepx_schedule_final.csv', index=False)
    print("✅ Đã lưu: optimal_jepx_schedule_final.csv")
    
    # Summary
    print("\n" + "="*80)
    print("📝 TÓM TẮT")
    print("="*80)
    
    print(f"""
    ✅ PATTERN TỐI ƯU:
    - {n_optimal} blocks @ 2000kW (charge MAX)
    - {7 - n_optimal} blocks @ {baseline_rest:.0f}kW (rest/maintain)
    - 1 block JEPX @ 950kW (discharge bán điện)
    
    ✅ KẾT QUẢ:
    - Tổng 基準値: {total_baseline:.0f}kW
    - Tăng: +{total_baseline - 1665.38:.0f}kW so với không JEPX
    - Tăng: +{(total_baseline / 1665.38 - 1) * 100:.1f}%
    - SOC range: {SOC_MIN}% - {max([s['soc_end'] for s in schedule[:-1]]):.1f}%
    - Cycle perfect: ✅ ({soc - SOC_MIN:.4f}% error)
    
    ✅ LỢI ÍCH:
    - Xử lý nhiều năng lượng hơn (+{(total_baseline / 1665.38 - 1) * 100:.0f}%)
    - Kiếm tiền từ bán điện JEPX
    - Baseline luôn >= 0 (không xả âm)
    - Chu kỳ ổn định hàng ngày
    """)

else:
    print("\n❌ KHÔNG TÌM THẤY pattern hợp lệ!")

print("\n✅ Hoàn tất!")
