"""
Tạo lịch tối ưu THỰC TẾ cho hoạt động hàng ngày
- SOC dao động trong ngày (sạc/xả)
- Có chu kỳ lặp lại hàng ngày
- Phù hợp với pattern thực tế từ dữ liệu
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Công thức regression
SLOPE = 0.013545
INTERCEPT = -2.8197

# Giới hạn
SOC_MIN = 10
SOC_MAX = 90
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
    """Tìm 基準値 cần thiết"""
    change_needed = soc_target - soc_current
    rate_needed = change_needed / hours
    baseline = (rate_needed - INTERCEPT) / SLOPE
    return max(BASELINE_MIN, min(BASELINE_MAX, baseline))


def create_realistic_daily_schedule(initial_soc=15):
    """
    Tạo lịch THỰC TẾ dựa trên pattern từ dữ liệu 4 ngày
    
    Pattern thực tế:
    - 00:00-05:59: SOC thấp (~10-20%), cần sạc nhẹ hoặc duy trì
    - 06:00-08:59: SẠC MẠNH (基準値 ~2000kW) → SOC tăng ~70% (lên 75-85%)
    - 09:00-11:59: XẢ (基準値 = 0kW) → SOC giảm ~10% (còn 65-75%)
    - 12:00-14:59: Sạc vừa (基準値 ~500kW) → SOC tăng ~15% (lên 80-90%)
    - 15:00-23:59: XẢ dần về ~10-20% cho ngày hôm sau
    
    Args:
        initial_soc: SOC ban đầu vào 00:00 (mặc định 15%)
    
    Returns:
        DataFrame với lịch 8 blocks
    """
    
    print('='*100)
    print('🔧 LỊCH TỐI ƯU THỰC TẾ - PHÙ HỢP VỚI HOẠT ĐỘNG HÀNG NGÀY')
    print('='*100)
    
    print(f'\n📊 Pattern hoạt động:')
    print(f'   00:00-05:59: Duy trì SOC thấp (chuẩn bị sạc)')
    print(f'   06:00-08:59: ⚡ SẠC MẠNH → tăng ~70%')
    print(f'   09:00-11:59: Xả nhẹ → giảm ~10%')
    print(f'   12:00-14:59: Sạc vừa → tăng ~15%')
    print(f'   15:00-23:59: Xả dần về SOC thấp cho ngày mai')
    
    # Định nghĩa mục tiêu cho từng block (dựa trên pattern thực tế)
    time_blocks = [
        ('00:00', '02:59', 'Đêm khuya', 'maintain', initial_soc + 2),
        ('03:00', '05:59', 'Sáng sớm', 'maintain', initial_soc + 2),
        ('06:00', '08:59', 'Buổi sáng', 'charge_heavy', 85),  # Sạc mạnh
        ('09:00', '11:59', 'Trưa', 'discharge', 75),  # Xả
        ('12:00', '14:59', 'Chiều', 'charge_medium', 85),  # Sạc vừa
        ('15:00', '17:59', 'Chiều muộn', 'discharge', 65),  # Xả
        ('18:00', '20:59', 'Tối', 'discharge', 40),  # Xả
        ('21:00', '23:59', 'Đêm', 'discharge', initial_soc),  # Xả về ban đầu
    ]
    
    schedule = []
    soc_current = initial_soc
    
    print(f'\n{"="*100}')
    print('📋 LỊCH TỐI ƯU 8 BLOCKS')
    print(f'{"="*100}')
    
    for i, (time_start, time_end, period_name, action, soc_target) in enumerate(time_blocks):
        # Đảm bảo target trong giới hạn
        soc_target = max(SOC_MIN, min(SOC_MAX, soc_target))
        
        # Tính baseline cần thiết
        baseline_optimal = find_required_baseline(soc_current, soc_target, 3.0)
        
        # Dự đoán SOC thực tế
        soc_predicted = predict_soc(soc_current, baseline_optimal, 3.0)
        
        # Thông tin
        change_rate = calculate_soc_change_rate(baseline_optimal)
        soc_change = soc_predicted - soc_current
        
        # Icon cho action
        if action == 'charge_heavy':
            action_icon = '⚡⚡⚡'
        elif action == 'charge_medium':
            action_icon = '⚡⚡'
        elif action == 'discharge':
            action_icon = '🔋📉'
        else:
            action_icon = '➡️'
        
        schedule.append({
            'block': i + 1,
            'time_range': f'{time_start}-{time_end}',
            'period': period_name,
            'action': action,
            'soc_start': soc_current,
            'soc_target': soc_target,
            'soc_predicted': soc_predicted,
            'soc_change': soc_change,
            'baseline_kw': baseline_optimal,
            'change_rate': change_rate,
            'duration_hours': 3.0
        })
        
        print(f'\n{i + 1}. {time_start}-{time_end} ({period_name}) {action_icon}')
        print(f'   SOC: {soc_current:.1f}% → 目標 {soc_target:.1f}% (予測: {soc_predicted:.1f}%)')
        print(f'   基準値: {baseline_optimal:.0f} kW')
        print(f'   変化率: {change_rate:+.2f} %/時間 (変化: {soc_change:+.1f}%)')
        
        # Cảnh báo
        if baseline_optimal >= BASELINE_MAX:
            print(f'   ⚠️  基準値 đạt giới hạn max!')
        elif baseline_optimal <= BASELINE_MIN and soc_target > soc_current:
            print(f'   ⚠️  Không thể tăng SOC với 基準値 = 0')
        
        soc_current = soc_predicted
    
    schedule_df = pd.DataFrame(schedule)
    
    print(f'\n{"="*100}')
    print('📊 TỔNG KẾT')
    print(f'{"="*100}')
    print(f'\nSOC ban đầu (00:00): {initial_soc:.1f}%')
    print(f'SOC cuối ngày (24:00): {schedule_df["soc_predicted"].iloc[-1]:.1f}%')
    print(f'→ Chênh lệch: {schedule_df["soc_predicted"].iloc[-1] - initial_soc:+.1f}%')
    
    print(f'\nSOC cao nhất trong ngày: {schedule_df["soc_predicted"].max():.1f}%')
    print(f'SOC thấp nhất trong ngày: {schedule_df["soc_start"].min():.1f}%')
    print(f'Biên độ dao động: {schedule_df["soc_predicted"].max() - schedule_df["soc_start"].min():.1f}%')
    
    print(f'\n基準値 trung bình: {schedule_df["baseline_kw"].mean():.0f} kW')
    print(f'基準値 max: {schedule_df["baseline_kw"].max():.0f} kW (Block {schedule_df["baseline_kw"].idxmax() + 1})')
    print(f'基準値 min: {schedule_df["baseline_kw"].min():.0f} kW (Block {schedule_df["baseline_kw"].idxmin() + 1})')
    
    # Phân tích chu kỳ
    soc_final = schedule_df["soc_predicted"].iloc[-1]
    if abs(soc_final - initial_soc) < 5:
        print(f'\n✅ CHU KỲ ỔN ĐỊNH: SOC cuối ngày ({soc_final:.1f}%) ≈ SOC đầu ngày ({initial_soc:.1f}%)')
        print(f'   → Lịch này có thể lặp lại hàng ngày!')
    else:
        print(f'\n⚠️  CHU KỲ KHÔNG ỔN ĐỊNH: SOC cuối {soc_final:.1f}% ≠ SOC đầu {initial_soc:.1f}%')
        print(f'   → Cần điều chỉnh để lặp lại được')
    
    return schedule_df


def create_comparison_chart(realistic_df, balanced_df):
    """So sánh lịch thực tế vs lịch balanced"""
    
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'SOC - Thực tế (có chu kỳ)',
            'SOC - Balanced (tăng mãi)',
            '基準値 - Thực tế',
            '基準値 - Balanced',
            'SOC変化率 - Thực tế',
            'SOC変化率 - Balanced'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Helper function để tạo timeline
    def create_timeline(df):
        times = []
        soc_values = []
        for _, row in df.iterrows():
            time_start = row['time_range'].split('-')[0]
            time_end = row['time_range'].split('-')[1]
            times.extend([time_start, time_end])
            soc_values.extend([row['soc_start'], row['soc_predicted']])
        return times, soc_values
    
    # Row 1: SOC curves
    times_real, soc_real = create_timeline(realistic_df)
    times_bal, soc_bal = create_timeline(balanced_df)
    
    fig.add_trace(
        go.Scatter(
            x=times_real,
            y=soc_real,
            mode='lines+markers',
            name='Thực tế',
            line=dict(color='blue', width=3),
            marker=dict(size=8, symbol='diamond')
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=times_bal,
            y=soc_bal,
            mode='lines+markers',
            name='Balanced',
            line=dict(color='red', width=3),
            marker=dict(size=8, symbol='circle')
        ),
        row=1, col=2
    )
    
    # SOC limits
    for col in [1, 2]:
        fig.add_hline(y=SOC_MIN, line_dash="dot", line_color="orange", row=1, col=col)
        fig.add_hline(y=SOC_MAX, line_dash="dot", line_color="green", row=1, col=col)
    
    # Row 2: Baseline bars
    block_labels = realistic_df['time_range'].tolist()
    
    fig.add_trace(
        go.Bar(
            x=block_labels,
            y=realistic_df['baseline_kw'],
            name='Thực tế',
            marker_color=['lightcoral' if x == 0 else 'lightgreen' if x < 1000 else 'lightblue' 
                         for x in realistic_df['baseline_kw']],
            text=[f'{v:.0f}' for v in realistic_df['baseline_kw']],
            textposition='outside'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=block_labels,
            y=balanced_df['baseline_kw'],
            name='Balanced',
            marker_color='orange',
            text=[f'{v:.0f}' for v in balanced_df['baseline_kw']],
            textposition='outside'
        ),
        row=2, col=2
    )
    
    # Row 3: Change rate
    fig.add_trace(
        go.Bar(
            x=block_labels,
            y=realistic_df['change_rate'],
            name='Thực tế',
            marker_color=['red' if x < 0 else 'green' for x in realistic_df['change_rate']],
            text=[f'{v:+.1f}' for v in realistic_df['change_rate']],
            textposition='outside'
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=block_labels,
            y=balanced_df['change_rate'],
            name='Balanced',
            marker_color='purple',
            text=[f'{v:+.1f}' for v in balanced_df['change_rate']],
            textposition='outside'
        ),
        row=3, col=2
    )
    
    # Zero lines
    for col in [1, 2]:
        fig.add_hline(y=0, line_dash="dash", line_color="black", row=3, col=col)
    
    # Update axes labels
    for row in range(1, 4):
        for col in [1, 2]:
            fig.update_xaxes(title_text="時刻/Block", row=row, col=col)
    
    fig.update_yaxes(title_text="SOC (%)", row=1, col=1)
    fig.update_yaxes(title_text="SOC (%)", row=1, col=2)
    fig.update_yaxes(title_text="基準値 (kW)", row=2, col=1)
    fig.update_yaxes(title_text="基準値 (kW)", row=2, col=2)
    fig.update_yaxes(title_text="変化率 (%/h)", row=3, col=1)
    fig.update_yaxes(title_text="変化率 (%/h)", row=3, col=2)
    
    # Layout
    fig.update_layout(
        height=1400,
        width=1600,
        title={
            'text': '比較: 実際スケジュール vs Balanced<br><sub>実際: 毎日繰り返し可能 | Balanced: 増加し続ける</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=False
    )
    
    return fig


def create_multi_day_simulation(initial_soc=15, num_days=3):
    """Mô phỏng lịch nhiều ngày liên tiếp"""
    
    print('\n' + '='*100)
    print(f'🔄 MÔ PHỎNG {num_days} NGÀY LIÊN TIẾP')
    print('='*100)
    
    all_schedules = []
    soc_start_of_day = initial_soc
    
    for day in range(1, num_days + 1):
        print(f'\n{"─"*100}')
        print(f'📅 NGÀY {day}')
        print(f'{"─"*100}')
        
        schedule_df = create_realistic_daily_schedule(initial_soc=soc_start_of_day)
        schedule_df['day'] = day
        all_schedules.append(schedule_df)
        
        # SOC cuối ngày = SOC đầu ngày hôm sau
        soc_start_of_day = schedule_df['soc_predicted'].iloc[-1]
        
        print(f'\n   → SOC cuối ngày {day}: {soc_start_of_day:.1f}%')
        print(f'   → SOC đầu ngày {day+1}: {soc_start_of_day:.1f}%')
    
    combined_df = pd.concat(all_schedules, ignore_index=True)
    
    print(f'\n{"="*100}')
    print('📊 TỔNG KẾT MÔ PHỎNG')
    print(f'{"="*100}')
    print(f'\nSOC ngày 1:       {initial_soc:.1f}%')
    print(f'SOC sau {num_days} ngày: {soc_start_of_day:.1f}%')
    print(f'Độ lệch tích lũy: {soc_start_of_day - initial_soc:+.1f}%')
    
    return combined_df


if __name__ == '__main__':
    print('='*100)
    print('🚀 LỊCH TỐI ƯU THỰC TẾ - CÓ CHU KỲ HÀNG NGÀY')
    print('='*100)
    
    # Tạo lịch thực tế
    realistic_df = create_realistic_daily_schedule(initial_soc=15)
    
    # Lưu file
    realistic_df.to_csv('realistic_daily_schedule.csv', index=False, encoding='utf-8-sig')
    print(f'\n✅ Đã lưu: realistic_daily_schedule.csv')
    
    # So sánh với balanced
    print(f'\n{"="*100}')
    print('📊 SO SÁNH VỚI SCENARIO BALANCED')
    print(f'{"="*100}')
    
    # Tạo balanced schedule để so sánh (giống scenario 1)
    from new_day_scheduler import create_smart_schedule
    balanced_df = create_smart_schedule(
        initial_soc=20,
        final_soc_target=80,
        strategy='balanced'
    )
    
    print('\n⚠️  VẤN ĐỀ VỚI BALANCED:')
    print(f'   Ngày 1: 20% → 80% (tăng +60%)')
    print(f'   Ngày 2: 80% → ? (không thể tiếp tục tăng, vượt 90%)')
    print(f'   → KHÔNG THỂ LẶP LẠI HÀNG NGÀY!')
    
    print('\n✅ ƯU ĐIỂM LỊCH THỰC TẾ:')
    print(f'   Ngày 1: {realistic_df["soc_start"].iloc[0]:.0f}% → {realistic_df["soc_predicted"].iloc[-1]:.0f}%')
    print(f'   Ngày 2: {realistic_df["soc_predicted"].iloc[-1]:.0f}% → ~{realistic_df["soc_predicted"].iloc[-1]:.0f}%')
    print(f'   → CÓ THỂ LẶP LẠI HÀNG NGÀY!')
    
    # Tạo visualization so sánh
    fig = create_comparison_chart(realistic_df, balanced_df)
    fig.write_html('realistic_vs_balanced_comparison.html')
    print(f'\n✅ Đã lưu: realistic_vs_balanced_comparison.html')
    
    # Mô phỏng nhiều ngày
    multi_day_df = create_multi_day_simulation(initial_soc=15, num_days=3)
    multi_day_df.to_csv('multi_day_simulation.csv', index=False, encoding='utf-8-sig')
    print(f'\n✅ Đã lưu: multi_day_simulation.csv')
