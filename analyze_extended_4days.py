"""
Phân tích SOC với dữ liệu mở rộng: ngày 22, 23, 25, 26/9
Sử dụng 3-hour blocks như phương pháp ban đầu
"""

import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def analyze_extended_data():
    """
    Phân tích dữ liệu từ nhiều ngày hơn
    """
    
    print('='*100)
    print('PHÂN TÍCH MỞ RỘNG: DỮ LIỆU 4 NGÀY (22, 23, 25, 26/9)')
    print('='*100)
    
    # Đọc dữ liệu
    df = pd.read_csv('kotohira_integrated_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Danh sách các ngày cần phân tích
    target_dates = [
        pd.Timestamp('2025-09-22'),
        pd.Timestamp('2025-09-23'),
        pd.Timestamp('2025-09-25'),
        pd.Timestamp('2025-09-26'),
    ]
    
    print(f'\n📅 Các ngày phân tích:')
    for date in target_dates:
        print(f'   • {date.strftime("%Y-%m-%d")} ({date.strftime("%A")})')
    
    # Thu thập dữ liệu 3-hour blocks
    all_data = []
    
    for date in target_dates:
        print(f'\n{"="*100}')
        print(f'📊 Phân tích ngày {date.strftime("%Y-%m-%d")}')
        print(f'{"="*100}')
        
        # Lọc dữ liệu ngày này
        daily_data = df[
            (df['timestamp'] >= date) & 
            (df['timestamp'] < date + timedelta(days=1))
        ].copy()
        
        daily_soc = daily_data[daily_data['battery_soc_percent'].notna()].copy()
        daily_baseline = daily_data[daily_data['demand_plan_kw_baseline'].notna()].copy()
        
        if len(daily_baseline) == 0:
            print('   ⚠️  Không có dữ liệu 基準値')
            continue
            
        print(f'\n   SOC範囲: {daily_soc["battery_soc_percent"].min():.1f}% → {daily_soc["battery_soc_percent"].max():.1f}%')
        print(f'   基準値が設定されている時間帯:')
        
        # Phân tích từng baseline value
        for baseline_value in sorted(daily_baseline['demand_plan_kw_baseline'].unique()):
            group = daily_baseline[daily_baseline['demand_plan_kw_baseline'] == baseline_value]
            start_time = group['timestamp'].min()
            end_time = group['timestamp'].max()
            
            # Tìm SOC trong khoảng thời gian này
            period_soc = daily_soc[
                (daily_soc['timestamp'] >= start_time) & 
                (daily_soc['timestamp'] <= end_time)
            ]
            
            if len(period_soc) > 0:
                soc_start = period_soc['battery_soc_percent'].iloc[0]
                soc_end = period_soc['battery_soc_percent'].iloc[-1]
                soc_change = soc_end - soc_start
                duration_hours = (end_time - start_time).total_seconds() / 3600
                
                if duration_hours > 0:
                    soc_change_rate = soc_change / duration_hours
                    
                    all_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'time_start': start_time.strftime('%H:%M'),
                        'time_end': end_time.strftime('%H:%M'),
                        'baseline_kw': baseline_value,
                        'duration_hours': duration_hours,
                        'soc_start': soc_start,
                        'soc_end': soc_end,
                        'soc_change': soc_change,
                        'soc_change_rate': soc_change_rate
                    })
                    
                    print(f'\n      基準値 = {baseline_value:.0f} kW')
                    print(f'         期間: {start_time.strftime("%H:%M")} → {end_time.strftime("%H:%M")} ({duration_hours:.2f}時間)')
                    print(f'         SOC: {soc_start:.1f}% → {soc_end:.1f}% (変化: {soc_change:+.1f}%)')
                    print(f'         変化率: {soc_change_rate:+.2f} %/時間')
    
    # Tạo DataFrame
    analysis_df = pd.DataFrame(all_data)
    
    if len(analysis_df) == 0:
        print('\n❌ Không có dữ liệu để phân tích!')
        return None, None, None, None
    
    print(f'\n{"="*100}')
    print('📊 TỔNG HỢP DỮ LIỆU')
    print(f'{"="*100}')
    print(f'\nTổng số data points: {len(analysis_df)}')
    print('\n' + analysis_df.to_string(index=False))
    
    # Linear Regression
    print(f'\n{"="*100}')
    print('📈 LINEAR REGRESSION')
    print(f'{"="*100}')
    
    X = analysis_df['baseline_kw'].values
    y = analysis_df['soc_change_rate'].values
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
    
    print(f'\n🔬 Kết quả (tất cả {len(analysis_df)} điểm):')
    print(f'   Slope:     {slope:.6f}')
    print(f'   Intercept: {intercept:.4f}')
    print(f'   R²:        {r_value**2:.6f}')
    print(f'   P-value:   {p_value:.10f}')
    print(f'   Std Error: {std_err:.6f}')
    print(f'\n   📐 Công thức:')
    print(f'   SOC変化率 (%/時間) = {slope:.6f} × 基準値(kW) + ({intercept:.4f})')
    
    # So sánh với công thức ban đầu (chỉ 25-26/9)
    print(f'\n{"="*100}')
    print('📊 SO SÁNH VỚI CÔNG THỨC BAN ĐẦU')
    print(f'{"="*100}')
    
    # Lọc dữ liệu chỉ ngày 25-26
    df_25_26 = analysis_df[analysis_df['date'].isin(['2025-09-25', '2025-09-26'])]
    
    if len(df_25_26) > 0:
        X_old = df_25_26['baseline_kw'].values
        y_old = df_25_26['soc_change_rate'].values
        
        slope_old, intercept_old, r_value_old, p_value_old, std_err_old = \
            stats.linregress(X_old, y_old)
        
        print(f'\n1️⃣ Công thức cũ (chỉ ngày 25-26, {len(df_25_26)} điểm):')
        print(f'   SOC変化率 = {slope_old:.6f} × 基準値 + ({intercept_old:.4f})')
        print(f'   R² = {r_value_old**2:.6f}')
        
        print(f'\n2️⃣ Công thức mới (4 ngày: 22,23,25,26, {len(analysis_df)} điểm):')
        print(f'   SOC変化率 = {slope:.6f} × 基準値 + ({intercept:.4f})')
        print(f'   R² = {r_value**2:.6f}')
        
        print(f'\n3️⃣ Công thức gốc (từ file analyze_soc_optimization.py):')
        print(f'   SOC変化率 = 0.012804 × 基準値 - 1.9515')
        print(f'   R² = 0.9997')
    
    # Kiểm tra với các giá trị cụ thể
    print(f'\n{"="*100}')
    print('🔍 KIỂM TRA DỰ ĐOÁN')
    print(f'{"="*100}')
    
    test_baselines = [0, 532, 1998]
    
    print(f'\n{"基準値 (kW)":<15} {"Công thức cũ":<20} {"Công thức mới":<20} {"Thực tế TB":<20}')
    print('-'*100)
    
    for bl in test_baselines:
        # Công thức cũ
        pred_old = 0.012804 * bl - 1.9515
        
        # Công thức mới
        pred_new = slope * bl + intercept
        
        # Thực tế trung bình
        actual_data = analysis_df[analysis_df['baseline_kw'] == bl]
        if len(actual_data) > 0:
            actual_mean = actual_data['soc_change_rate'].mean()
            print(f'{bl:<15.0f} {pred_old:<20.2f} {pred_new:<20.2f} {actual_mean:<20.2f}')
        else:
            print(f'{bl:<15.0f} {pred_old:<20.2f} {pred_new:<20.2f} {"N/A":<20}')
    
    # Tạo visualization
    create_extended_visualization(analysis_df, slope, intercept, r_value)
    
    # Phân tích theo từng ngày
    print(f'\n{"="*100}')
    print('📊 PHÂN TÍCH THEO TỪNG NGÀY')
    print(f'{"="*100}')
    
    for date_str in sorted(analysis_df['date'].unique()):
        date_data = analysis_df[analysis_df['date'] == date_str]
        print(f'\n📅 {date_str}: {len(date_data)} blocks')
        
        for _, row in date_data.iterrows():
            print(f'   {row["time_start"]}-{row["time_end"]}: '
                  f'{row["baseline_kw"]:.0f}kW → '
                  f'SOC {row["soc_start"]:.0f}%-{row["soc_end"]:.0f}% '
                  f'({row["soc_change"]:+.1f}%, {row["soc_change_rate"]:+.2f}%/h)')
    
    return analysis_df, slope, intercept, r_value


def create_extended_visualization(analysis_df, slope, intercept, r_value):
    """
    Tạo visualization cho phân tích mở rộng
    """
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '基準値 vs SOC変化率 (tất cả điểm)',
            'Phân bố theo ngày',
            'SOC変化 theo 基準値 và ngày',
            'Residuals (sai số)'
        ),
        specs=[[{"type": "scatter"}, {"type": "box"}],
               [{"type": "scatter"}, {"type": "scatter"}]],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Màu sắc cho từng ngày
    colors = {
        '2025-09-22': 'red',
        '2025-09-23': 'orange',
        '2025-09-25': 'blue',
        '2025-09-26': 'green'
    }
    
    # Plot 1: Scatter plot với regression line
    for date in sorted(analysis_df['date'].unique()):
        date_data = analysis_df[analysis_df['date'] == date]
        
        fig.add_trace(
            go.Scatter(
                x=date_data['baseline_kw'],
                y=date_data['soc_change_rate'],
                mode='markers',
                name=date,
                marker=dict(
                    size=12,
                    color=colors.get(date, 'gray'),
                    symbol='diamond'
                ),
                text=[f'{date}<br>SOC: {row["soc_start"]:.0f}%→{row["soc_end"]:.0f}%' 
                      for _, row in date_data.iterrows()],
                hovertemplate='%{text}<br>基準値: %{x} kW<br>変化率: %{y:.2f} %/h<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Regression line
    x_range = np.linspace(
        analysis_df['baseline_kw'].min() - 100,
        analysis_df['baseline_kw'].max() + 100,
        100
    )
    y_pred = slope * x_range + intercept
    
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_pred,
            mode='lines',
            name=f'Regression<br>R²={r_value**2:.4f}',
            line=dict(color='black', width=2, dash='dash')
        ),
        row=1, col=1
    )
    
    # Plot 2: Box plot theo baseline
    for baseline in sorted(analysis_df['baseline_kw'].unique()):
        baseline_data = analysis_df[analysis_df['baseline_kw'] == baseline]
        
        fig.add_trace(
            go.Box(
                y=baseline_data['soc_change_rate'],
                name=f'{baseline:.0f}kW',
                boxmean='sd',
                marker_color=colors.get(baseline_data['date'].iloc[0], 'gray')
            ),
            row=1, col=2
        )
    
    # Plot 3: SOC change vs baseline với ngày
    for date in sorted(analysis_df['date'].unique()):
        date_data = analysis_df[analysis_df['date'] == date]
        
        fig.add_trace(
            go.Scatter(
                x=date_data['baseline_kw'],
                y=date_data['soc_change'],
                mode='markers+lines',
                name=date,
                marker=dict(size=10, color=colors.get(date, 'gray')),
                line=dict(color=colors.get(date, 'gray'), width=1, dash='dot')
            ),
            row=2, col=1
        )
    
    # Plot 4: Residuals
    y_pred_all = slope * analysis_df['baseline_kw'] + intercept
    residuals = analysis_df['soc_change_rate'] - y_pred_all
    
    for date in sorted(analysis_df['date'].unique()):
        date_indices = analysis_df['date'] == date
        
        fig.add_trace(
            go.Scatter(
                x=analysis_df[date_indices]['baseline_kw'],
                y=residuals[date_indices],
                mode='markers',
                name=date,
                marker=dict(size=10, color=colors.get(date, 'gray')),
                showlegend=False
            ),
            row=2, col=2
        )
    
    # Zero line for residuals
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=2)
    
    # Update axes
    fig.update_xaxes(title_text="基準値 (kW)", row=1, col=1)
    fig.update_xaxes(title_text="基準値", row=1, col=2)
    fig.update_xaxes(title_text="基準値 (kW)", row=2, col=1)
    fig.update_xaxes(title_text="基準値 (kW)", row=2, col=2)
    
    fig.update_yaxes(title_text="SOC変化率 (%/h)", row=1, col=1)
    fig.update_yaxes(title_text="SOC変化率 (%/h)", row=1, col=2)
    fig.update_yaxes(title_text="SOC変化 (% / 3h)", row=2, col=1)
    fig.update_yaxes(title_text="Residuals (%/h)", row=2, col=2)
    
    # Update layout
    fig.update_layout(
        height=1000,
        width=1600,
        title={
            'text': f'拡張分析: 4日間データ (22,23,25,26/9)<br><sub>y = {slope:.6f}x + {intercept:.4f}, R² = {r_value**2:.6f}</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True,
        legend=dict(x=1.02, y=1)
    )
    
    fig.write_html('extended_4days_analysis.html')
    print('\n✅ Đã lưu visualization: extended_4days_analysis.html')
    
    # Lưu CSV
    analysis_df.to_csv('extended_4days_data.csv', index=False, encoding='utf-8-sig')
    print('✅ Đã lưu dữ liệu: extended_4days_data.csv')


if __name__ == '__main__':
    analysis_df, slope, intercept, r_value = analyze_extended_data()
    
    if analysis_df is not None:
        print(f'\n{"="*100}')
        print('💡 KẾT LUẬN')
        print(f'{"="*100}')
        
        print(f'\n✅ CÔNG THỨC MỚI (với dữ liệu mở rộng):')
        print(f'   SOC変化率 (%/時間) = {slope:.6f} × 基準値(kW) + ({intercept:.4f})')
        print(f'   R² = {r_value**2:.6f}')
        print(f'   Số điểm dữ liệu: {len(analysis_df)}')
        
        print(f'\n📊 So với công thức ban đầu:')
        print(f'   Ban đầu: 0.012804 × 基準値 - 1.9515 (R² = 0.9997, 6 điểm)')
        print(f'   Mới:     {slope:.6f} × 基準値 + {intercept:.4f} (R² = {r_value**2:.6f}, {len(analysis_df)} điểm)')
        
        if r_value**2 > 0.95:
            print(f'\n   ✅ R² > 0.95 → Công thức mới rất tốt!')
        else:
            print(f'\n   ⚠️  R² < 0.95 → Có thể có biến động giữa các ngày')
        
        print(f'\n{"="*100}')
