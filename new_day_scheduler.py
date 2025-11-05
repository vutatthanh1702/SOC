"""
Công cụ tạo lịch tối ưu cho ngày mới (chưa có dữ liệu thực tế)
Input: SOC ban đầu, mục tiêu SOC cuối ngày
Output: Lịch 基準値 tối ưu cho 8 blocks 3 giờ
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Công thức regression
SLOPE = 0.013545
INTERCEPT = -2.8197

# Giới hạn SOC
SOC_MIN = 10
SOC_MAX = 90

# Giới hạn 基準値 (dựa trên dữ liệu thực tế)
BASELINE_MIN = 0
BASELINE_MAX = 2000


def calculate_soc_change_rate(baseline_kw):
    """Tính SOC変化率 từ 基準値"""
    return SLOPE * baseline_kw + INTERCEPT


def predict_soc(soc_start, baseline_kw, hours):
    """Dự đoán SOC sau N giờ"""
    change_rate = calculate_soc_change_rate(baseline_kw)
    return soc_start + (change_rate * hours)


def find_required_baseline(soc_current, soc_target, hours):
    """Tìm 基準値 cần thiết để đạt SOC mục tiêu"""
    change_needed = soc_target - soc_current
    rate_needed = change_needed / hours
    baseline = (rate_needed - INTERCEPT) / SLOPE
    return max(BASELINE_MIN, min(BASELINE_MAX, baseline))


def create_smart_schedule(initial_soc, final_soc_target, strategy='balanced'):
    """
    Tạo lịch thông minh cho cả ngày
    
    Args:
        initial_soc: SOC ban đầu (%)
        final_soc_target: SOC mục tiêu cuối ngày (%)
        strategy: Chiến lược tối ưu
            - 'balanced': Cân bằng, tăng dần đều
            - 'morning_charge': Sạc mạnh vào buổi sáng
            - 'evening_charge': Sạc mạnh vào buổi tối
            - 'maintain': Duy trì SOC ổn định
    
    Returns:
        DataFrame với lịch cho 8 blocks
    """
    
    print('='*100)
    print('🔧 TẠO LỊCH TỐI ƯU CHO NGÀY MỚI')
    print('='*100)
    
    print(f'\n📊 Thông tin đầu vào:')
    print(f'   SOC ban đầu: {initial_soc:.1f}%')
    print(f'   SOC mục tiêu cuối ngày: {final_soc_target:.1f}%')
    print(f'   Chiến lược: {strategy}')
    
    # 8 blocks trong ngày
    time_blocks = [
        ('00:00', '02:59', 'Đêm khuya'),
        ('03:00', '05:59', 'Sáng sớm'),
        ('06:00', '08:59', 'Buổi sáng'),
        ('09:00', '11:59', 'Trưa'),
        ('12:00', '14:59', 'Chiều'),
        ('15:00', '17:59', 'Chiều muộn'),
        ('18:00', '20:59', 'Tối'),
        ('21:00', '23:59', 'Đêm'),
    ]
    
    schedule = []
    soc_current = initial_soc
    
    # Xác định SOC targets cho từng block theo strategy
    if strategy == 'balanced':
        # Tăng đều từ initial đến final
        soc_increment = (final_soc_target - initial_soc) / 8
        soc_targets = [initial_soc + soc_increment * (i + 1) for i in range(8)]
        
    elif strategy == 'morning_charge':
        # Sạc mạnh 06:00-09:00, sau đó duy trì
        soc_targets = []
        for i in range(8):
            if i < 2:  # 00:00-06:00: tăng nhẹ
                soc_targets.append(initial_soc + 5)
            elif i == 2:  # 06:00-09:00: sạc mạnh
                soc_targets.append(initial_soc + (final_soc_target - initial_soc) * 0.7)
            else:  # sau 09:00: tăng nhẹ đến target
                remaining = final_soc_target - soc_targets[-1]
                soc_targets.append(soc_targets[-1] + remaining / (8 - i))
                
    elif strategy == 'evening_charge':
        # Duy trì ban ngày, sạc mạnh tối
        soc_targets = []
        for i in range(8):
            if i < 6:  # 00:00-18:00: duy trì
                soc_targets.append(initial_soc + 5)
            else:  # 18:00-24:00: sạc mạnh
                progress = (i - 5) / 3
                soc_targets.append(initial_soc + (final_soc_target - initial_soc) * progress)
                
    elif strategy == 'maintain':
        # Duy trì SOC ổn định quanh giá trị hiện tại
        target_soc = (initial_soc + final_soc_target) / 2
        soc_targets = [target_soc] * 8
        
    else:
        # Default: balanced
        soc_increment = (final_soc_target - initial_soc) / 8
        soc_targets = [initial_soc + soc_increment * (i + 1) for i in range(8)]
    
    # Đảm bảo targets trong giới hạn
    soc_targets = [max(SOC_MIN, min(SOC_MAX, t)) for t in soc_targets]
    
    print(f'\n{"="*100}')
    print('📋 LỊCH TỐI ƯU 8 BLOCKS')
    print(f'{"="*100}')
    
    for i, (time_start, time_end, period_name) in enumerate(time_blocks):
        soc_target = soc_targets[i]
        
        # Tính baseline cần thiết
        baseline_optimal = find_required_baseline(soc_current, soc_target, 3.0)
        
        # Dự đoán SOC thực tế đạt được
        soc_predicted = predict_soc(soc_current, baseline_optimal, 3.0)
        
        # Thông tin thêm
        change_rate = calculate_soc_change_rate(baseline_optimal)
        soc_change = soc_predicted - soc_current
        
        schedule.append({
            'block': i + 1,
            'time_range': f'{time_start}-{time_end}',
            'period': period_name,
            'soc_start': soc_current,
            'soc_target': soc_target,
            'soc_predicted': soc_predicted,
            'soc_change': soc_change,
            'baseline_kw': baseline_optimal,
            'change_rate': change_rate,
            'duration_hours': 3.0
        })
        
        print(f'\n{i + 1}. {time_start}-{time_end} ({period_name})')
        print(f'   SOC: {soc_current:.1f}% → 目標 {soc_target:.1f}% (予測: {soc_predicted:.1f}%)')
        print(f'   基準値: {baseline_optimal:.0f} kW')
        print(f'   変化率: {change_rate:+.2f} %/時間 (変化: {soc_change:+.1f}%)')
        
        # Cảnh báo nếu baseline quá cao/thấp
        if baseline_optimal >= BASELINE_MAX:
            print(f'   ⚠️  基準値 đạt giới hạn max!')
        elif baseline_optimal <= BASELINE_MIN and soc_target > soc_current:
            print(f'   ⚠️  Không thể đạt mục tiêu với 基準値 >= 0')
        
        # Update cho block tiếp theo
        soc_current = soc_predicted
    
    schedule_df = pd.DataFrame(schedule)
    
    print(f'\n{"="*100}')
    print('📊 TỔNG KẾT')
    print(f'{"="*100}')
    print(f'\nSOC ban đầu:  {initial_soc:.1f}%')
    print(f'SOC cuối ngày: {schedule_df["soc_predicted"].iloc[-1]:.1f}%')
    print(f'SOC mục tiêu:  {final_soc_target:.1f}%')
    print(f'Chênh lệch:    {schedule_df["soc_predicted"].iloc[-1] - final_soc_target:+.1f}%')
    
    print(f'\n基準値 trung bình: {schedule_df["baseline_kw"].mean():.0f} kW')
    print(f'基準値 max:       {schedule_df["baseline_kw"].max():.0f} kW')
    print(f'基準値 min:       {schedule_df["baseline_kw"].min():.0f} kW')
    
    return schedule_df


def visualize_schedule(schedule_df, title='最適スケジュール'):
    """Tạo visualization cho lịch"""
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            'SOC予測',
            '基準値',
            'SOC変化率'
        ),
        vertical_spacing=0.1,
        row_heights=[0.4, 0.3, 0.3]
    )
    
    # Tạo timeline
    times = []
    soc_values = []
    
    for _, row in schedule_df.iterrows():
        time_start = row['time_range'].split('-')[0]
        time_end = row['time_range'].split('-')[1]
        times.extend([time_start, time_end])
        soc_values.extend([row['soc_start'], row['soc_predicted']])
    
    # Plot 1: SOC prediction
    fig.add_trace(
        go.Scatter(
            x=times,
            y=soc_values,
            mode='lines+markers',
            name='SOC予測',
            line=dict(color='blue', width=3),
            marker=dict(size=8, symbol='diamond'),
            text=[f'{v:.1f}%' for v in soc_values],
            textposition='top center'
        ),
        row=1, col=1
    )
    
    # SOC limits
    fig.add_hline(y=SOC_MIN, line_dash="dot", line_color="red", 
                  annotation_text="SOC MIN", row=1, col=1)
    fig.add_hline(y=SOC_MAX, line_dash="dot", line_color="green", 
                  annotation_text="SOC MAX", row=1, col=1)
    
    # Plot 2: Baseline bars
    block_labels = schedule_df['time_range'].tolist()
    baseline_values = schedule_df['baseline_kw'].tolist()
    
    colors = []
    for bl in baseline_values:
        if bl < 500:
            colors.append('lightcoral')
        elif bl < 1000:
            colors.append('lightgreen')
        else:
            colors.append('lightblue')
    
    fig.add_trace(
        go.Bar(
            x=block_labels,
            y=baseline_values,
            name='基準値',
            marker_color=colors,
            text=[f'{v:.0f}kW' for v in baseline_values],
            textposition='outside'
        ),
        row=2, col=1
    )
    
    # Plot 3: Change rate
    change_rates = schedule_df['change_rate'].tolist()
    bar_colors = ['green' if x > 0 else 'red' for x in change_rates]
    
    fig.add_trace(
        go.Bar(
            x=block_labels,
            y=change_rates,
            name='変化率',
            marker_color=bar_colors,
            text=[f'{v:+.2f}' for v in change_rates],
            textposition='outside'
        ),
        row=3, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", row=3, col=1)
    
    # Update axes
    fig.update_xaxes(title_text="時刻", row=1, col=1)
    fig.update_xaxes(title_text="Block", row=2, col=1)
    fig.update_xaxes(title_text="Block", row=3, col=1)
    
    fig.update_yaxes(title_text="SOC (%)", row=1, col=1)
    fig.update_yaxes(title_text="基準値 (kW)", row=2, col=1)
    fig.update_yaxes(title_text="変化率 (%/h)", row=3, col=1)
    
    # Layout
    fig.update_layout(
        height=1200,
        width=1400,
        title={
            'text': f'{title}<br><sub>公式: SOC変化率 = {SLOPE:.6f} × 基準値 + {INTERCEPT:.4f}</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True
    )
    
    return fig


def generate_schedule_scenarios():
    """Tạo nhiều kịch bản lịch khác nhau"""
    
    print('='*100)
    print('📅 TẠO CÁC KỊCH BẢN LỊCH TỐI ƯU')
    print('='*100)
    
    scenarios = [
        {
            'name': 'Scenario 1: Sạc từ 20% lên 80%',
            'initial_soc': 20,
            'final_soc': 80,
            'strategy': 'balanced'
        },
        {
            'name': 'Scenario 2: Duy trì quanh 50%',
            'initial_soc': 50,
            'final_soc': 50,
            'strategy': 'maintain'
        },
        {
            'name': 'Scenario 3: Sạc mạnh buổi sáng',
            'initial_soc': 15,
            'final_soc': 75,
            'strategy': 'morning_charge'
        },
        {
            'name': 'Scenario 4: Sạc buổi tối',
            'initial_soc': 30,
            'final_soc': 80,
            'strategy': 'evening_charge'
        }
    ]
    
    all_schedules = []
    
    for scenario in scenarios:
        print(f'\n{"="*100}')
        print(f'📋 {scenario["name"]}')
        print(f'{"="*100}')
        
        schedule_df = create_smart_schedule(
            initial_soc=scenario['initial_soc'],
            final_soc_target=scenario['final_soc'],
            strategy=scenario['strategy']
        )
        
        schedule_df['scenario'] = scenario['name']
        all_schedules.append(schedule_df)
        
        # Visualization
        fig = visualize_schedule(schedule_df, title=scenario['name'])
        filename = f"scenario_{len(all_schedules)}.html"
        fig.write_html(filename)
        print(f'\n✅ Đã lưu: {filename}')
    
    # Kết hợp tất cả
    combined_df = pd.concat(all_schedules, ignore_index=True)
    combined_df.to_csv('all_scenarios.csv', index=False, encoding='utf-8-sig')
    print(f'\n{"="*100}')
    print('✅ Đã lưu tất cả kịch bản: all_scenarios.csv')
    print(f'{"="*100}')
    
    return combined_df


if __name__ == '__main__':
    print('='*100)
    print('🚀 CÔNG CỤ LẬP LỊCH CHO NGÀY MỚI')
    print('='*100)
    print(f'\n📐 Công thức:')
    print(f'   SOC変化率 = {SLOPE:.6f} × 基準値 + {INTERCEPT:.4f}')
    print(f'   (R² = 0.996, 12 điểm từ 4 ngày)')
    
    # Tạo các kịch bản
    generate_schedule_scenarios()
    
    print(f'\n{"="*100}')
    print('💡 HƯỚNG DẪN SỬ DỤNG')
    print(f'{"="*100}')
    print("""
    Để tạo lịch tùy chỉnh, sử dụng:
    
    schedule_df = create_smart_schedule(
        initial_soc=20,      # SOC ban đầu
        final_soc_target=80, # SOC mục tiêu cuối ngày
        strategy='balanced'  # Chiến lược: balanced/morning_charge/evening_charge/maintain
    )
    
    Chiến lược:
    - 'balanced': Tăng đều trong ngày
    - 'morning_charge': Sạc mạnh buổi sáng (06:00-09:00)
    - 'evening_charge': Sạc mạnh buổi tối (18:00-24:00)
    - 'maintain': Duy trì SOC ổn định
    """)
