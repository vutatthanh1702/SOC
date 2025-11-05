"""
Công cụ tối ưu hóa lịch hàng ngày
- SOC theo phút (từ dữ liệu thực tế)
- 基準値 theo 3h block
- Sử dụng công thức: SOC変化率 = 0.013545 × 基準値 - 2.8197
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Công thức regression từ phân tích 4 ngày
SLOPE = 0.013545
INTERCEPT = -2.8197

# Giới hạn SOC
SOC_MIN = 10  # %
SOC_MAX = 90  # %

# Các khung thời gian 3 giờ
TIME_BLOCKS = [
    ('00:00', '02:59'),
    ('03:00', '05:59'),
    ('06:00', '08:59'),
    ('09:00', '11:59'),
    ('12:00', '14:59'),
    ('15:00', '17:59'),
    ('18:00', '20:59'),
    ('21:00', '23:59'),
]


def calculate_soc_change_rate(baseline_kw):
    """
    Tính SOC変化率 dựa trên 基準値
    
    Args:
        baseline_kw: Giá trị 基準値 (kW)
    
    Returns:
        SOC変化率 (%/時間)
    """
    return SLOPE * baseline_kw + INTERCEPT


def predict_soc_after_period(soc_start, baseline_kw, duration_hours):
    """
    Dự đoán SOC sau một khoảng thời gian
    
    Args:
        soc_start: SOC ban đầu (%)
        baseline_kw: 基準値 (kW)
        duration_hours: Thời gian (giờ)
    
    Returns:
        SOC sau khoảng thời gian (%)
    """
    change_rate = calculate_soc_change_rate(baseline_kw)
    soc_change = change_rate * duration_hours
    soc_end = soc_start + soc_change
    return soc_end


def find_optimal_baseline(soc_current, soc_target, duration_hours):
    """
    Tìm 基準値 tối ưu để đạt được SOC mục tiêu
    
    Args:
        soc_current: SOC hiện tại (%)
        soc_target: SOC mục tiêu (%)
        duration_hours: Thời gian (giờ)
    
    Returns:
        基準値 tối ưu (kW)
    """
    # SOC_change_needed = soc_target - soc_current
    # change_rate_needed = SOC_change_needed / duration_hours
    # change_rate = SLOPE * baseline + INTERCEPT
    # baseline = (change_rate - INTERCEPT) / SLOPE
    
    soc_change_needed = soc_target - soc_current
    change_rate_needed = soc_change_needed / duration_hours
    baseline_optimal = (change_rate_needed - INTERCEPT) / SLOPE
    
    return max(0, baseline_optimal)  # Không âm


def optimize_daily_schedule(target_date_str, initial_soc=None):
    """
    Tối ưu hóa lịch cho một ngày cụ thể
    
    Args:
        target_date_str: Ngày cần tối ưu (format: 'YYYY-MM-DD')
        initial_soc: SOC ban đầu (nếu None sẽ lấy từ data)
    
    Returns:
        DataFrame với lịch tối ưu
    """
    print('='*100)
    print(f'🔧 TỐI ƯU HÓA LỊCH NGÀY {target_date_str}')
    print('='*100)
    
    # Đọc dữ liệu
    df = pd.read_csv('kotohira_integrated_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Lọc dữ liệu ngày target
    target_date = pd.to_datetime(target_date_str)
    daily_data = df[
        (df['timestamp'] >= target_date) & 
        (df['timestamp'] < target_date + timedelta(days=1))
    ].copy()
    
    if len(daily_data) == 0:
        print(f'❌ Không có dữ liệu cho ngày {target_date_str}')
        return None
    
    # Lấy SOC theo phút
    soc_data = daily_data[daily_data['battery_soc_percent'].notna()].copy()
    
    if len(soc_data) == 0:
        print('❌ Không có dữ liệu SOC')
        return None
    
    # SOC ban đầu
    if initial_soc is None:
        initial_soc = soc_data['battery_soc_percent'].iloc[0]
    
    print(f'\n📊 Thông tin ngày:')
    print(f'   SOC ban đầu: {initial_soc:.1f}%')
    print(f'   SOC cuối ngày (thực tế): {soc_data["battery_soc_percent"].iloc[-1]:.1f}%')
    print(f'   SOC min: {soc_data["battery_soc_percent"].min():.1f}%')
    print(f'   SOC max: {soc_data["battery_soc_percent"].max():.1f}%')
    
    # Tạo lịch tối ưu cho từng block 3 giờ
    schedule = []
    soc_current = initial_soc
    
    print(f'\n{"="*100}')
    print('📋 LỊCH TỐI ƯU HÓA THEO 3H BLOCK')
    print(f'{"="*100}')
    
    for block_idx, (time_start, time_end) in enumerate(TIME_BLOCKS):
        block_start = datetime.combine(target_date.date(), 
                                       datetime.strptime(time_start, '%H:%M').time())
        block_end = datetime.combine(target_date.date(), 
                                     datetime.strptime(time_end, '%H:%M').time())
        
        # Lấy SOC thực tế trong block này
        block_soc = soc_data[
            (soc_data['timestamp'] >= block_start) & 
            (soc_data['timestamp'] <= block_end)
        ]
        
        if len(block_soc) == 0:
            continue
        
        soc_actual_start = block_soc['battery_soc_percent'].iloc[0]
        soc_actual_end = block_soc['battery_soc_percent'].iloc[-1]
        soc_actual_change = soc_actual_end - soc_actual_start
        
        duration_hours = 3.0
        actual_change_rate = soc_actual_change / duration_hours
        
        # Tính 基準値 thực tế (reverse engineer)
        # change_rate = SLOPE * baseline + INTERCEPT
        # baseline = (change_rate - INTERCEPT) / SLOPE
        baseline_actual = (actual_change_rate - INTERCEPT) / SLOPE
        
        # Xác định mục tiêu cho block tiếp theo
        if block_idx < len(TIME_BLOCKS) - 1:
            # Giữ SOC trong khoảng an toàn
            if soc_current < SOC_MIN + 10:
                soc_target = SOC_MIN + 30  # Sạc lên
            elif soc_current > SOC_MAX - 10:
                soc_target = SOC_MAX - 10  # Giữ ổn định
            else:
                soc_target = soc_current + 5  # Tăng nhẹ
        else:
            # Block cuối: chuẩn bị cho ngày mai
            soc_target = 80.0
        
        # Đảm bảo target trong giới hạn
        soc_target = max(SOC_MIN, min(SOC_MAX, soc_target))
        
        # Tính 基準値 tối ưu
        baseline_optimal = find_optimal_baseline(soc_current, soc_target, duration_hours)
        
        # Dự đoán SOC với baseline tối ưu
        soc_predicted = predict_soc_after_period(soc_current, baseline_optimal, duration_hours)
        
        schedule.append({
            'block': f'Block {block_idx + 1}',
            'time_range': f'{time_start}-{time_end}',
            'soc_start': soc_current,
            'soc_target': soc_target,
            'soc_predicted': soc_predicted,
            'soc_actual_start': soc_actual_start,
            'soc_actual_end': soc_actual_end,
            'baseline_optimal': baseline_optimal,
            'baseline_actual': max(0, baseline_actual),
            'duration_hours': duration_hours
        })
        
        print(f'\n{block_idx + 1}. {time_start}-{time_end} (3h)')
        print(f'   SOC: {soc_current:.1f}% → 目標 {soc_target:.1f}% (予測: {soc_predicted:.1f}%)')
        print(f'   基準値 最適: {baseline_optimal:.0f} kW')
        print(f'   基準値 実際: {max(0, baseline_actual):.0f} kW')
        print(f'   実際のSOC: {soc_actual_start:.1f}% → {soc_actual_end:.1f}%')
        
        # Update SOC hiện tại cho block tiếp theo
        soc_current = soc_predicted
    
    schedule_df = pd.DataFrame(schedule)
    
    # Visualization
    create_schedule_visualization(schedule_df, target_date_str, soc_data)
    
    # Lưu file
    schedule_df.to_csv(f'optimal_schedule_{target_date_str}.csv', 
                       index=False, encoding='utf-8-sig')
    print(f'\n✅ Đã lưu lịch tối ưu: optimal_schedule_{target_date_str}.csv')
    
    return schedule_df


def create_schedule_visualization(schedule_df, target_date, soc_data):
    """
    Tạo visualization cho lịch tối ưu
    """
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            f'SOC theo thời gian - Ngày {target_date}',
            '基準値 (Optimal vs Actual)'
        ),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )
    
    # Plot 1: SOC curve
    # SOC thực tế (minute-by-minute)
    fig.add_trace(
        go.Scatter(
            x=soc_data['timestamp'],
            y=soc_data['battery_soc_percent'],
            mode='lines',
            name='SOC thực tế',
            line=dict(color='blue', width=2),
            hovertemplate='%{x|%H:%M}<br>SOC: %{y:.1f}%<extra></extra>'
        ),
        row=1, col=1
    )
    
    # SOC predicted từ optimal baseline
    block_times = []
    soc_predicted_values = []
    
    for idx, row in schedule_df.iterrows():
        time_start = row['time_range'].split('-')[0]
        time_end = row['time_range'].split('-')[1]
        
        start_dt = datetime.combine(
            pd.to_datetime(target_date).date(),
            datetime.strptime(time_start, '%H:%M').time()
        )
        end_dt = datetime.combine(
            pd.to_datetime(target_date).date(),
            datetime.strptime(time_end, '%H:%M').time()
        )
        
        block_times.extend([start_dt, end_dt])
        soc_predicted_values.extend([row['soc_start'], row['soc_predicted']])
    
    fig.add_trace(
        go.Scatter(
            x=block_times,
            y=soc_predicted_values,
            mode='lines+markers',
            name='SOC dự đoán (optimal)',
            line=dict(color='red', width=2, dash='dash'),
            marker=dict(size=8, symbol='diamond'),
            hovertemplate='%{x|%H:%M}<br>SOC: %{y:.1f}%<extra></extra>'
        ),
        row=1, col=1
    )
    
    # SOC limits
    fig.add_hline(y=SOC_MIN, line_dash="dot", line_color="orange", 
                  annotation_text="SOC MIN", row=1, col=1)
    fig.add_hline(y=SOC_MAX, line_dash="dot", line_color="green", 
                  annotation_text="SOC MAX", row=1, col=1)
    
    # Plot 2: Baseline comparison
    block_centers = []
    baseline_optimal = []
    baseline_actual = []
    block_labels = []
    
    for idx, row in schedule_df.iterrows():
        time_start = row['time_range'].split('-')[0]
        time_end = row['time_range'].split('-')[1]
        
        start_dt = datetime.combine(
            pd.to_datetime(target_date).date(),
            datetime.strptime(time_start, '%H:%M').time()
        )
        end_dt = datetime.combine(
            pd.to_datetime(target_date).date(),
            datetime.strptime(time_end, '%H:%M').time()
        )
        
        center_dt = start_dt + (end_dt - start_dt) / 2
        block_centers.append(center_dt)
        baseline_optimal.append(row['baseline_optimal'])
        baseline_actual.append(row['baseline_actual'])
        block_labels.append(row['time_range'])
    
    fig.add_trace(
        go.Bar(
            x=block_centers,
            y=baseline_optimal,
            name='基準値 最適',
            marker_color='lightgreen',
            text=[f'{v:.0f}kW' for v in baseline_optimal],
            textposition='outside',
            hovertemplate='%{x|%H:%M}<br>Optimal: %{y:.0f} kW<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=block_centers,
            y=baseline_actual,
            name='基準値 実際',
            marker_color='lightcoral',
            text=[f'{v:.0f}kW' for v in baseline_actual],
            textposition='outside',
            hovertemplate='%{x|%H:%M}<br>Actual: %{y:.0f} kW<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_xaxes(title_text="時刻", row=1, col=1)
    fig.update_xaxes(title_text="時刻", row=2, col=1)
    fig.update_yaxes(title_text="SOC (%)", row=1, col=1)
    fig.update_yaxes(title_text="基準値 (kW)", row=2, col=1)
    
    fig.update_layout(
        height=1000,
        width=1400,
        title={
            'text': f'最適スケジュール - {target_date}<br><sub>公式: SOC変化率 = {SLOPE:.6f} × 基準値 + {INTERCEPT:.4f}</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True,
        hovermode='x unified'
    )
    
    filename = f'optimal_schedule_{target_date}.html'
    fig.write_html(filename)
    print(f'✅ Đã lưu visualization: {filename}')


def batch_optimize(start_date_str, end_date_str):
    """
    Tối ưu hóa hàng loạt cho nhiều ngày
    """
    print('='*100)
    print('📅 TỐI ƯU HÓA HÀNG LOẠT')
    print('='*100)
    
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)
    
    current_date = start_date
    all_schedules = []
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        print(f'\n{"="*100}')
        
        schedule_df = optimize_daily_schedule(date_str)
        
        if schedule_df is not None:
            schedule_df['date'] = date_str
            all_schedules.append(schedule_df)
        
        current_date += timedelta(days=1)
    
    if len(all_schedules) > 0:
        combined_df = pd.concat(all_schedules, ignore_index=True)
        combined_df.to_csv('optimal_schedules_batch.csv', 
                          index=False, encoding='utf-8-sig')
        print(f'\n{"="*100}')
        print('✅ Đã lưu tất cả lịch tối ưu: optimal_schedules_batch.csv')
        print(f'{"="*100}')
        
        return combined_df
    
    return None


if __name__ == '__main__':
    # Ví dụ: Tối ưu hóa cho ngày cụ thể
    print('='*100)
    print('🚀 CÔNG CỤ TỐI ƯU HÓA LỊCH HÀNG NGÀY')
    print('='*100)
    print(f'\n📐 Công thức sử dụng:')
    print(f'   SOC変化率 = {SLOPE:.6f} × 基準値 + {INTERCEPT:.4f}')
    print(f'   (R² = 0.996, dựa trên 12 điểm từ 4 ngày)')
    
    # Tối ưu hóa cho từng ngày
    dates_to_optimize = ['2025-09-22', '2025-09-23', '2025-09-25', '2025-09-26']
    
    for date_str in dates_to_optimize:
        print(f'\n{"="*100}')
        optimize_daily_schedule(date_str)
    
    # Hoặc tối ưu hóa hàng loạt
    # batch_optimize('2025-09-22', '2025-09-26')
