#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TÌM PATTERN TỐI ƯU: JEPX XẢ TỪ 90% → 5% (THEO DATA NGÀY 22/9)
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("="*80)
print("🔍 TÌM PATTERN TỐI ƯU: JEPX 90% → 5%")
print("="*80)

print("""
📊 DATA THỰC TẾ (ngày 22/9):
• SOC bắt đầu: ~90%
• SOC kết thúc: ~5%
• JEPX xả: 90% → 5% = -85%

❌ TRƯỚC ĐÂY TÍNH SAI:
• Giả định JEPX xả từ 80% → 5% = -75%
• Dẫn đến pattern không khớp với thực tế

✅ TÍNH LẠI VỚI DATA THỰC:
• JEPX xả: 90% → 5% = -85%
• Tìm pattern tối ưu mới
""")

# Constants
SLOPE = 0.013545
INTERCEPT = -2.8197
JEPX_DELTA = -85.0  # % trong 3h (từ data thực tế ngày 22/9)
SOC_MIN = 5.0
SOC_MAX = 90.0
B_MIN = 0
B_MAX = 2000

print(f"""
📐 THÔNG SỐ HỆ THỐNG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Công thức baseline:
  ΔSOC = ({SLOPE} × 基準値 + {INTERCEPT}) × 3h
  ΔSOC = {SLOPE*3:.6f} × 基準値 + {INTERCEPT*3:.4f}

JEPX (từ data thực tế):
  ΔSOC_JEPX = {JEPX_DELTA}% (xả từ 90% → 5%)

Constraints:
  SOC ∈ [{SOC_MIN}%, {SOC_MAX}%]
  基準値 ∈ [{B_MIN}, {B_MAX}]kW
  1 ngày = 8 blocks × 3h
""")


def calc_delta_baseline(b):
    """ΔSOC cho 1 baseline block"""
    return (SLOPE * b + INTERCEPT) * 3


print("\n" + "="*80)
print("🎯 BÀI TOÁN TỐI ƯU")
print("="*80)

print("""
Maximize: Σ(基準値)

Subject to:
  1. Cycle constraint:
     Σ(ΔSOC_baseline) + ΔSOC_JEPX = 0
     → Σ(ΔSOC_baseline) = -(-85%) = +85%
  
  2. SOC bounds:
     5% ≤ SOC(t) ≤ 90%, ∀t
  
  3. Baseline bounds:
     0 ≤ 基準値 ≤ 2000kW
  
  4. Number of blocks:
     N_baseline + 1 JEPX + N_free = 8
""")

target_delta_baseline = -JEPX_DELTA
print(f"Cần: Σ(ΔSOC_baseline) = {target_delta_baseline}%\n")

print("="*80)
print("📖 BƯỚC 1: TÌM SỐ BASELINE BLOCKS TỐI ƯU")
print("="*80)

print("""
Từ constraint chu kỳ:
  Σ(ΔSOC_baseline) = 85%
  Σ[(SLOPE × b_i + INTERCEPT) × 3] = 85%
  3 × SLOPE × Σ(b_i) + 3 × N × INTERCEPT = 85%
  
  → Σ(b_i) = [85 - 3 × N × INTERCEPT] / (3 × SLOPE)
  → Σ(b_i) = [85 - 3 × N × (-2.8197)] / (3 × 0.013545)
  → Σ(b_i) = [85 + 8.4591 × N] / 0.040635
  → Σ(b_i) = 2091.9 + 208.2 × N
""")

print("Tính toán cho các giá trị N:\n")
for N in range(1, 8):
    sum_b = (target_delta_baseline - 3 * N * INTERCEPT) / (3 * SLOPE)
    print(f"  N = {N}: Σ(基準値) = {sum_b:.0f}kW")

print(f"""
✅ KẾT LUẬN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Để maximize Σ(基準値), cần N càng lớn càng tốt!
→ N = 7 cho MAX baseline

Nhưng phải kiểm tra SOC constraints!
""")

print("\n" + "="*80)
print("📖 BƯỚC 2: TÌM TẤT CẢ PATTERNS HỢP LỆ")
print("="*80)

results = []

for n_baseline in range(1, 8):
    # Tính tổng baseline cần
    sum_baseline = (target_delta_baseline - 3 * n_baseline * INTERCEPT) / (
        3 * SLOPE)
    
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
        
        # Simulate SOC - BẮT ĐẦU TỪ 5%
        soc = SOC_MIN
        soc_trajectory = [soc]
        max_soc = soc
        min_soc = soc
        valid = True
        
        # Baseline blocks
        for _ in range(n_max):
            soc += calc_delta_baseline(2000)
            soc_trajectory.append(soc)
            max_soc = max(max_soc, soc)
            if soc > SOC_MAX:
                valid = False
                break
        
        if not valid:
            continue
        
        for _ in range(remaining):
            soc += calc_delta_baseline(x)
            soc_trajectory.append(soc)
            max_soc = max(max_soc, soc)
            if soc > SOC_MAX:
                valid = False
                break
        
        if not valid:
            continue
        
        # JEPX - phải đạt 90% trước khi xả
        soc_before_jepx = soc
        soc += JEPX_DELTA
        soc_trajectory.append(soc)
        min_soc = min(min_soc, soc)
        
        if soc < SOC_MIN or soc_before_jepx < (SOC_MAX - 1):
            # JEPX phải xả từ ~90%
            valid = False
            continue
        
        # Check cycle
        if abs(soc - SOC_MIN) > 0.5:
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
            'soc_before_jepx': soc_before_jepx,
            'soc_trajectory': soc_trajectory
        })

# Sort by sum_baseline
results.sort(key=lambda r: r['sum_baseline'], reverse=True)

print(f"\n✅ Tìm thấy {len(results)} patterns hợp lệ\n")

for i, r in enumerate(results[:5], 1):
    print(f"{i}. {r['n_baseline']} baseline + {r['n_jepx']} JEPX + "
          f"{r['n_free']} free:")
    print(f"   Pattern: {r['n_max']} blocks @2000kW + "
          f"{r['n_baseline']-r['n_max']} blocks @{r['x']:.0f}kW")
    print(f"   Σ(基準値) = {r['sum_baseline']:.0f}kW")
    print(f"   SOC range: {r['min_soc']:.1f}% - {r['max_soc']:.1f}%")
    print(f"   SOC trước JEPX: {r['soc_before_jepx']:.1f}%")
    print()

if not results:
    print("❌ KHÔNG TÌM THẤY PATTERN HỢP LỆ NÀO!")
    print("""
    Lý do: Với JEPX = -85%, cần:
    • Baseline tăng SOC lên 90%
    • JEPX xả từ 90% → 5%
    • Nhưng constraint SOC_MAX = 90% quá chặt!
    
    → Cần kiểm tra lại data thực tế!
    """)

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
- So với 8 blocks (1665kW): {best['sum_baseline'] - 1665:+.0f}kW """
          f"({(best['sum_baseline']/1665 - 1)*100:+.1f}%)"""
f"""
- SOC range: {best['min_soc']:.1f}% - {best['max_soc']:.1f}%
- SOC trước JEPX: {best['soc_before_jepx']:.1f}%
""")
    
    print("\n" + "="*80)
    print("📐 CHỨNG MINH TOÁN HỌC")
    print("="*80)
    
    print(f"""
BƯỚC 1: TẠI SAO N={best['n_baseline']} LÀ TỐI ƯU?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Từ công thức:
  Σ(基準値) = 2091.9 + 208.2 × N
  
Với N={best['n_baseline']}:
  Σ(基準値) = 2091.9 + 208.2 × {best['n_baseline']} = """
          f"{best['sum_baseline']:.0f}kW")
    
    if best['n_baseline'] < 7:
        sum_n7 = (target_delta_baseline - 3 * 7 * INTERCEPT) / (3 * SLOPE)
        print(f"""
Tại sao không dùng N=7?
  N=7: Σ(基準値) = {sum_n7:.0f}kW (cao hơn!)
  
  Nhưng: Vi phạm SOC constraint!
  → Với N=7, SOC sẽ vượt 90% trước JEPX
  → Pattern không hợp lệ ❌
  
→ N={best['n_baseline']} là MAX có thể trong constraints
""")
    
    print(f"""
BƯỚC 2: TẠI SAO {best['n_max']}@2000 + {best['n_baseline']-best['n_max']}@"""
          f"{best['x']:.0f}?")
    print("""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    print(f"""
Cần phân bổ {best['sum_baseline']:.0f}kW vào {best['n_baseline']} blocks.

Kiểm tra thêm 1 block @2000kW:
  ({best['n_max']+1}) × 2000 + ({best['n_baseline']-best['n_max']-1}) × X = """
          f"{best['sum_baseline']:.0f}")
    
    if best['n_max'] < best['n_baseline']:
        x_test = (best['sum_baseline'] - (best['n_max']+1) * 2000) / (
            best['n_baseline'] - best['n_max'] - 1) if (
                best['n_baseline'] - best['n_max'] - 1) > 0 else float('inf')
        
        if x_test < 0:
            print(f"  X = {x_test:.0f}kW < 0 → KHÔNG HỢP LỆ! ❌")
        else:
            # Simulate to check SOC
            soc_test = SOC_MIN
            for _ in range(best['n_max']+1):
                soc_test += calc_delta_baseline(2000)
            if soc_test > SOC_MAX:
                print(f"  → SOC = {soc_test:.1f}% > 90% → VI PHẠM! ❌")
            else:
                print(f"  X = {x_test:.0f}kW → Có thể hợp lệ")
                print(f"  Nhưng tổng baseline vẫn = {best['sum_baseline']:.0f}kW")
                print(f"  → Pattern {best['n_max']}@2000 + "
                      f"{best['n_baseline']-best['n_max']}@{best['x']:.0f} "
                      f"là tối ưu do phân bổ đều")
    
    print(f"""
→ Pattern {best['n_max']}@2000 + {best['n_baseline']-best['n_max']}@"""
          f"{best['x']:.0f} thỏa mãn tất cả constraints")
    
    print("""
BƯỚC 3: TẠI SAO KHÔNG CÓ FREE BLOCKS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    if n_free == 0:
        print(f"""
Pattern tối ưu có {n_free} FREE blocks.

Nếu thêm FREE blocks:
  N={best['n_baseline']-1}: Σ(基準値) = """
              f"{(target_delta_baseline - 3 * (best['n_baseline']-1) * INTERCEPT) / (3 * SLOPE):.0f}kW")
        print(f"  → Giảm {best['sum_baseline'] - (target_delta_baseline - 3 * (best['n_baseline']-1) * INTERCEPT) / (3 * SLOPE):.0f}kW!")
        print("""
→ FREE blocks làm GIẢM tổng baseline
→ Không dùng FREE là tối ưu
""")
    else:
        print(f"""
Pattern tối ưu có {n_free} FREE blocks.

Tại sao không giảm xuống còn {n_free-1} FREE?
  → Vì N={best['n_baseline']+1} vi phạm SOC constraint
  → N={best['n_baseline']} là MAX có thể
""")
    
    print("\n" + "="*80)
    print("📊 SIMULATION CHI TIẾT")
    print("="*80)
    
    # Create schedule
    schedule = []
    soc = SOC_MIN
    block_num = 1
    
    print(f"\n{'Block':<6} {'Time':<15} {'Type':<15} {'Baseline':<12} "
          f"{'ΔSOC':<10} {'SOC':<20}")
    print("-" * 85)
    
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
        
        print(f"{block_num:<6} {time_str:<15} {'BASELINE':<15} "
              f"{2000:<6}kW     {delta:>+6.1f}%   "
              f"{soc_before:>5.1f}% → {soc:>5.1f}%")
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
        
        print(f"{block_num:<6} {time_str:<15} {'BASELINE':<15} "
              f"{best['x']:<6.0f}kW     {delta:>+6.1f}%   "
              f"{soc_before:>5.1f}% → {soc:>5.1f}%")
        block_num += 1
    
    # JEPX block
    time_start = (block_num - 1) * 3
    time_end = block_num * 3
    time_str = f"{time_start:02d}:00-{time_end:02d}:00"
    
    soc_before = soc
    soc += JEPX_DELTA
    
    schedule.append({
        'block': block_num,
        'time': time_str,
        'type': 'JEPX',
        'baseline': float('nan'),
        'delta_soc': JEPX_DELTA,
        'soc_start': soc_before,
        'soc_end': soc
    })
    
    print(f"{block_num:<6} {time_str:<15} {'JEPX':<15} {'NaN':<12} "
          f"{JEPX_DELTA:>+6.1f}%   {soc_before:>5.1f}% → {soc:>5.1f}%")
    block_num += 1
    
    # FREE blocks
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
        
        print(f"{block_num:<6} {time_str:<15} {'FREE':<15} {'NaN':<12} "
              f"{0:>+6.1f}%   {soc:>5.1f}% → {soc:>5.1f}%")
        block_num += 1
    
    print(f"\n{'='*85}")
    print(f"Kết quả: Cycle {SOC_MIN}% → {soc:.1f}% (Error: {soc - SOC_MIN:.2f}%)")
    
    # Visualization
    print("\n" + "="*80)
    print("📊 TẠO VISUALIZATION")
    print("="*80)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Baseline Schedule',
            'SOC Evolution',
            'Comparison: N baseline blocks',
            'Baseline Distribution'
        ),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "bar"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.15
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
            text=['JEPX<br>-85%'],
            textposition='top center',
            name='JEPX',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Plot 2: SOC
    soc_trajectory = [s['soc_start'] for s in schedule] + [schedule[-1]['soc_end']]
    
    fig.add_trace(
        go.Scatter(
            x=list(range(len(soc_trajectory))),
            y=soc_trajectory,
            mode='lines+markers',
            name='SOC',
            line=dict(color='green', width=3),
            marker=dict(size=10)
        ),
        row=1, col=2
    )
    
    # Mark JEPX discharge
    fig.add_annotation(
        x=jepx_block['block']-0.5,
        y=jepx_block['soc_start'],
        text=f"JEPX<br>{jepx_block['soc_start']:.0f}%→{jepx_block['soc_end']:.0f}%",
        showarrow=True,
        arrowhead=2,
        ax=30,
        ay=-60,
        row=1, col=2
    )
    
    # SOC limits
    fig.add_hline(y=5, line_dash="dash", line_color="orange",
                  annotation_text="Min 5%", row=1, col=2)
    fig.add_hline(y=90, line_dash="dash", line_color="red",
                  annotation_text="Max 90%", row=1, col=2)
    
    # Plot 3: Comparison
    comp_data = []
    for N in range(1, 8):
        sum_b = (target_delta_baseline - 3 * N * INTERCEPT) / (3 * SLOPE)
        comp_data.append({'N': N, 'sum': sum_b})
    
    fig.add_trace(
        go.Bar(
            x=[d['N'] for d in comp_data],
            y=[d['sum'] for d in comp_data],
            text=[f"{d['sum']:.0f}kW" for d in comp_data],
            textposition='outside',
            marker_color=['red' if d['N'] == best['n_baseline'] 
                          else 'lightblue' for d in comp_data],
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Plot 4: Distribution
    all_blocks = []
    for s in schedule:
        if s['type'] == 'BASELINE':
            all_blocks.append(s['baseline'])
    
    fig.add_trace(
        go.Bar(
            x=list(range(1, len(all_blocks)+1)),
            y=all_blocks,
            text=[f"{b:.0f}kW" for b in all_blocks],
            textposition='outside',
            marker_color=['red' if b == 2000 else 'lightblue' 
                          for b in all_blocks],
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Update axes
    fig.update_xaxes(title_text="Block", row=1, col=1)
    fig.update_xaxes(title_text="Block", row=1, col=2)
    fig.update_xaxes(title_text="N baseline blocks", row=2, col=1)
    fig.update_xaxes(title_text="Baseline block", row=2, col=2)
    
    fig.update_yaxes(title_text="基準値 (kW)", row=1, col=1)
    fig.update_yaxes(title_text="SOC (%)", row=1, col=2, range=[0, 100])
    fig.update_yaxes(title_text="Σ(基準値) (kW)", row=2, col=1)
    fig.update_yaxes(title_text="基準値 (kW)", row=2, col=2)
    
    fig.update_layout(
        title_text=f"🏆 PATTERN TỐI ƯU (JEPX = -85%): 90% → 5%<br>" +
                   f"<sub>{best['n_baseline']} baseline "
                   f"({best['n_max']}×2000 + "
                   f"{best['n_baseline']-best['n_max']}×{best['x']:.0f})kW = "
                   f"{best['sum_baseline']:.0f}kW "
                   f"({(best['sum_baseline']/1665 - 1)*100:+.1f}% vs 8 blocks)</sub>",
        height=900,
        showlegend=False
    )
    
    fig.write_html('optimal_pattern_90_to_5.html')
    print("✅ Đã lưu: optimal_pattern_90_to_5.html")
    
    # Save schedule
    df = pd.DataFrame(schedule)
    df.to_csv('optimal_schedule_90_to_5.csv', index=False)
    print("✅ Đã lưu: optimal_schedule_90_to_5.csv")
    
    print("\n" + "="*80)
    print("💡 KẾT LUẬN")
    print("="*80)
    
    print(f"""
✅ VỚI JEPX XẢ 90% → 5% (DATA NGÀY 22/9):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pattern tối ưu:
- {best['n_baseline']} blocks BASELINE: """
          f"{best['n_max']}@2000kW + "
          f"{best['n_baseline']-best['n_max']}@{best['x']:.0f}kW = "
          f"{best['sum_baseline']:.0f}kW")
    print(f"- 1 block JEPX: Xả từ {best['soc_before_jepx']:.0f}% → 5%")
    print(f"- {n_free} blocks FREE")
    print(f"""
So sánh:
- 8 blocks không JEPX: 1,665kW
- Pattern này: {best['sum_baseline']:.0f}kW
- Tăng: {best['sum_baseline'] - 1665:+.0f}kW """
          f"({(best['sum_baseline']/1665 - 1)*100:+.1f}%)")
    print("""
✅ ĐÃ CHỨNG MINH:
1. N={} là tối ưu (maximize baseline trong constraints)
2. Pattern {}@2000 + {}@{:.0f} thỏa mãn SOC [5%, 90%]
3. JEPX xả từ ~90% → 5% (khớp với data thực tế)
4. Pattern này là GLOBAL OPTIMUM!
""".format(best['n_baseline'], best['n_max'], 
           best['n_baseline']-best['n_max'], best['x']))

print("\n✅ Hoàn tất!")
