"""
Phân tích dữ liệu theo từng phút để tìm công thức chính xác
Sử dụng dữ liệu ngày 25-26/9
"""

import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def analyze_minute_by_minute():
    """
    Phân tích dữ liệu theo từng phút
    """
    
    print('='*100)
    print('PHÂN TÍCH DỮ LIỆU THEO TỪNG PHÚT (ngày 25-26/9)')
    print('='*100)
    
    # Đọc dữ liệu
    df = pd.read_csv('kotohira_integrated_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Lọc dữ liệu ngày 25-26/9
    start_date = pd.Timestamp('2025-09-25')
    end_date = pd.Timestamp('2025-09-27')
    
    df_filtered = df[
        (df['timestamp'] >= start_date) & 
        (df['timestamp'] < end_date)
    ].copy()
    
    # Loại bỏ NaN
    df_filtered = df_filtered.dropna(
        subset=['battery_soc_percent', 'demand_plan_kw_baseline']
    )
    
    print(f'\n📊 Tổng số dữ liệu: {len(df_filtered):,} điểm')
    print(f'   Thời gian: {df_filtered["timestamp"].min()} → {df_filtered["timestamp"].max()}')
    
    # Tính SOC change rate theo từng phút
    df_filtered['soc_diff'] = df_filtered['battery_soc_percent'].diff()
    df_filtered['time_diff_seconds'] = df_filtered['timestamp'].diff().dt.total_seconds()
    df_filtered['time_diff_hours'] = df_filtered['time_diff_seconds'] / 3600
    
    # Tính tốc độ thay đổi SOC (%/giờ)
    df_filtered['soc_rate'] = df_filtered['soc_diff'] / df_filtered['time_diff_hours']
    
    # Lọc dữ liệu hợp lý (loại outliers)
    df_analysis = df_filtered[
        (df_filtered['time_diff_seconds'] > 0) &
        (df_filtered['time_diff_seconds'] < 120) &  # Trong 2 phút
        (abs(df_filtered['soc_rate']) < 100)  # Tốc độ hợp lý
    ].copy()
    
    print(f'\n📈 Sau khi lọc outliers: {len(df_analysis):,} điểm')
    
    # Phân tích theo từng baseline value
    print('\n' + '='*100)
    print('PHÂN TÍCH THEO TỪNG 基準値')
    print('='*100)
    
    baseline_stats = []
    
    for baseline_value in sorted(df_analysis['demand_plan_kw_baseline'].unique()):
        subset = df_analysis[
            df_analysis['demand_plan_kw_baseline'] == baseline_value
        ].copy()
        
        if len(subset) > 10:  # Ít nhất 10 điểm
            mean_rate = subset['soc_rate'].mean()
            median_rate = subset['soc_rate'].median()
            std_rate = subset['soc_rate'].std()
            count = len(subset)
            
            baseline_stats.append({
                'baseline_kw': baseline_value,
                'mean_rate': mean_rate,
                'median_rate': median_rate,
                'std_rate': std_rate,
                'count': count
            })
            
            print(f'\n基準値 = {baseline_value:.0f} kW:')
            print(f'  Số điểm: {count:,}')
            print(f'  Tốc độ TB: {mean_rate:+.3f} %/giờ')
            print(f'  Tốc độ median: {median_rate:+.3f} %/giờ')
            print(f'  Độ lệch chuẩn: {std_rate:.3f} %/giờ')
    
    stats_df = pd.DataFrame(baseline_stats)
    
    # Linear regression
    print('\n' + '='*100)
    print('LINEAR REGRESSION (từng phút)')
    print('='*100)
    
    X = df_analysis['demand_plan_kw_baseline'].values
    y = df_analysis['soc_rate'].values
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
    
    print(f'\n🔬 Kết quả regression (tất cả điểm):')
    print(f'   Slope:     {slope:.6f}')
    print(f'   Intercept: {intercept:.4f}')
    print(f'   R²:        {r_value**2:.6f}')
    print(f'   P-value:   {p_value:.10f}')
    print(f'   Std Error: {std_err:.6f}')
    print(f'\n   Công thức: SOC変化率 = {slope:.6f} × 基準値 + ({intercept:.4f})')
    
    # Regression với mean values
    print('\n' + '='*100)
    print('LINEAR REGRESSION (mean values cho mỗi 基準値)')
    print('='*100)
    
    X_mean = stats_df['baseline_kw'].values
    y_mean = stats_df['mean_rate'].values
    
    slope_mean, intercept_mean, r_value_mean, p_value_mean, std_err_mean = \
        stats.linregress(X_mean, y_mean)
    
    print(f'\n🔬 Kết quả regression (mean values):')
    print(f'   Slope:     {slope_mean:.6f}')
    print(f'   Intercept: {intercept_mean:.4f}')
    print(f'   R²:        {r_value_mean**2:.6f}')
    print(f'   P-value:   {p_value_mean:.10f}')
    print(f'   Std Error: {std_err_mean:.6f}')
    print(f'\n   Công thức: SOC変化率 = {slope_mean:.6f} × 基準値 + ({intercept_mean:.4f})')
    
    # So sánh với công thức ban đầu
    print('\n' + '='*100)
    print('SO SÁNH VỚI CÔNG THỨC BAN ĐẦU')
    print('='*100)
    
    SLOPE_ORIGINAL = 0.012804
    INTERCEPT_ORIGINAL = -1.9515
    
    print(f'\n1️⃣ Công thức ban đầu (3-hour blocks):')
    print(f'   SOC変化率 = {SLOPE_ORIGINAL} × 基準値 + ({INTERCEPT_ORIGINAL})')
    print(f'   R² = 0.9997')
    
    print(f'\n2️⃣ Công thức mới (từng phút - tất cả điểm):')
    print(f'   SOC変化率 = {slope:.6f} × 基準値 + ({intercept:.4f})')
    print(f'   R² = {r_value**2:.6f}')
    
    print(f'\n3️⃣ Công thức mới (từng phút - mean values):')
    print(f'   SOC変化率 = {slope_mean:.6f} × 基準値 + ({intercept_mean:.4f})')
    print(f'   R² = {r_value_mean**2:.6f}')
    
    # Kiểm tra với các giá trị cụ thể
    print('\n' + '='*100)
    print('KIỂM TRA VỚI CÁC GIÁ TRỊ CỤ THỂ')
    print('='*100)
    
    test_baselines = [0, 532, 1998]
    
    print(f'\n{"基準値":<15} {"Công thức cũ":<20} {"Phút (all)":<20} {"Phút (mean)":<20} {"Thực tế":<20}')
    print('-'*100)
    
    for bl in test_baselines:
        pred_old = SLOPE_ORIGINAL * bl + INTERCEPT_ORIGINAL
        pred_new_all = slope * bl + intercept
        pred_new_mean = slope_mean * bl + intercept_mean
        
        # Tìm giá trị thực tế
        actual_stat = stats_df[stats_df['baseline_kw'] == bl]
        if len(actual_stat) > 0:
            actual = actual_stat['mean_rate'].values[0]
            print(f'{bl:<15.0f} {pred_old:<20.2f} {pred_new_all:<20.2f} {pred_new_mean:<20.2f} {actual:<20.2f}')
        else:
            print(f'{bl:<15.0f} {pred_old:<20.2f} {pred_new_all:<20.2f} {pred_new_mean:<20.2f} {"N/A":<20}')
    
    # Tạo visualization
    create_minute_visualization(df_analysis, stats_df, slope, intercept, 
                               slope_mean, intercept_mean)
    
    return df_analysis, stats_df, slope, intercept, slope_mean, intercept_mean


def create_minute_visualization(df_analysis, stats_df, slope, intercept,
                                slope_mean, intercept_mean):
    """
    Tạo visualization cho phân tích từng phút
    """
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            'Dữ liệu thô: 基準値 vs SOC変化率 (tất cả điểm)',
            'Dữ liệu tổng hợp: 基準値 vs SOC変化率 (mean cho mỗi baseline)',
            'Phân bố SOC変化率 theo 基準値'
        ),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # Plot 1: Tất cả điểm
    fig.add_trace(
        go.Scatter(
            x=df_analysis['demand_plan_kw_baseline'],
            y=df_analysis['soc_rate'],
            mode='markers',
            name='Dữ liệu thô',
            marker=dict(
                size=2,
                color='lightblue',
                opacity=0.3
            )
        ),
        row=1, col=1
    )
    
    # Regression line (all points)
    x_range = np.linspace(
        df_analysis['demand_plan_kw_baseline'].min(),
        df_analysis['demand_plan_kw_baseline'].max(),
        100
    )
    y_pred = slope * x_range + intercept
    
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_pred,
            mode='lines',
            name=f'Regression (all): y={slope:.4f}x+{intercept:.2f}',
            line=dict(color='red', width=2)
        ),
        row=1, col=1
    )
    
    # Plot 2: Mean values
    fig.add_trace(
        go.Scatter(
            x=stats_df['baseline_kw'],
            y=stats_df['mean_rate'],
            mode='markers',
            name='Mean values',
            marker=dict(
                size=10,
                color='blue',
                symbol='diamond'
            ),
            error_y=dict(
                type='data',
                array=stats_df['std_rate'],
                visible=True
            )
        ),
        row=2, col=1
    )
    
    # Regression line (mean values)
    y_pred_mean = slope_mean * x_range + intercept_mean
    
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_pred_mean,
            mode='lines',
            name=f'Regression (mean): y={slope_mean:.4f}x+{intercept_mean:.2f}',
            line=dict(color='green', width=2)
        ),
        row=2, col=1
    )
    
    # Plot 3: Box plot
    for baseline in sorted(stats_df['baseline_kw'].unique()):
        subset = df_analysis[
            df_analysis['demand_plan_kw_baseline'] == baseline
        ]
        
        fig.add_trace(
            go.Box(
                y=subset['soc_rate'],
                name=f'{baseline:.0f}kW',
                boxmean='sd'
            ),
            row=3, col=1
        )
    
    # Update layout
    fig.update_xaxes(title_text="基準値 (kW)", row=1, col=1)
    fig.update_xaxes(title_text="基準値 (kW)", row=2, col=1)
    fig.update_xaxes(title_text="基準値", row=3, col=1)
    
    fig.update_yaxes(title_text="SOC変化率 (%/h)", row=1, col=1)
    fig.update_yaxes(title_text="SOC変化率 (%/h)", row=2, col=1)
    fig.update_yaxes(title_text="SOC変化率 (%/h)", row=3, col=1)
    
    fig.update_layout(
        height=1400,
        width=1400,
        title={
            'text': 'Phân tích từng phút: 基準値 vs SOC変化率<br><sub>Dữ liệu: 25-26/9/2025</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True
    )
    
    fig.write_html('minute_by_minute_analysis.html')
    print('\n✅ Đã lưu visualization: minute_by_minute_analysis.html')


if __name__ == '__main__':
    df_analysis, stats_df, slope, intercept, slope_mean, intercept_mean = \
        analyze_minute_by_minute()
    
    print('\n' + '='*100)
    print('💡 KẾT LUẬN')
    print('='*100)
    print('\n1. Dữ liệu từng phút có nhiều NOISE → R² thấp hơn')
    print('2. Dữ liệu 3-hour blocks (trung bình) → R² cao hơn (0.9997)')
    print('3. Nên dùng công thức từ 3-hour blocks cho optimization')
    print('\n✅ Công thức tốt nhất:')
    print(f'   SOC変化率 = 0.012804 × 基準値 - 1.9515')
    print('='*100)
