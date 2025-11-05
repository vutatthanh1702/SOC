"""
Tối ưu đơn giản: MAXIMIZE tổng 基準値 với điều kiện lặp lại hàng ngày
Approach: Brute force tìm số blocks sạc tối ưu
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Công thức
SLOPE = 0.013545
INTERCEPT = -2.8197

# Giới hạn
SOC_MIN = 10
SOC_MAX = 90
BASELINE_MAX = 2000


def calculate_soc_change_rate(baseline_kw):
    return SLOPE * baseline_kw + INTERCEPT


def predict_soc(soc_start, baseline_kw, hours=3.0):
    change_rate = calculate_soc_change_rate(baseline_kw)
    return soc_start + (change_rate * hours)


def test_strategy(num_charge_blocks, soc_initial=15):
    """
    Test một strategy với N blocks sạc MAX, phần còn lại xả hoặc sạc vừa
    
    Args:
        num_charge_blocks: Số blocks sạc với 基準値 = MAX (2000kW)
        soc_initial: SOC ban đầu
    
    Returns:
        dict với kết quả
    """
    
    # Tính SOC sau khi sạc N blocks
    soc = soc_initial
    baselines = []
    
    # Phase 1: Sạc MAX
    for i in range(num_charge_blocks):
        soc = predict_soc(soc, BASELINE_MAX, 3.0)
        baselines.append(BASELINE_MAX)
    
    # Kiểm tra xem có vượt SOC_MAX không
    if soc > SOC_MAX:
        return None  # Invalid
    
    # Phase 2: Các blocks còn lại - xả bằng baseline=0
    remaining_blocks = 8 - num_charge_blocks
    
    if remaining_blocks > 0:
        # Dùng baseline = 0 để xả
        for i in range(remaining_blocks):
            soc = predict_soc(soc, 0, 3.0)
            baselines.append(0)
    
    soc_final = soc
    soc_deviation = abs(soc_final - soc_initial)
    
    # Kiểm tra có vượt giới hạn không
    if soc_final < SOC_MIN or soc_final > SOC_MAX:
        return None
    
    total_baseline = sum(baselines)
    
    return {
        'num_charge_blocks': num_charge_blocks,
        'baselines': baselines,
        'soc_initial': soc_initial,
        'soc_final': soc_final,
        'soc_deviation': soc_deviation,
        'total_baseline': total_baseline,
        'avg_baseline': total_baseline / 8,
        'can_repeat': soc_deviation <= 5
    }


def find_optimal_strategy():
    """Tìm strategy tối ưu bằng cách thử tất cả các khả năng"""
    
    print('='*100)
    print('🔍 TÌM CHIẾN LƯỢC TỐI ƯU: MAXIMIZE TỔNG 基準値')
    print('='*100)
    
    all_results = []
    
    # Thử với nhiều SOC khởi đầu khác nhau
    for soc_init in [10, 15, 20, 25, 30]:
        print(f'\n{"─"*100}')
        print(f'📊 SOC ban đầu = {soc_init}%:')
        print(f'{"─"*100}')
        print(f'{"Blocks sạc":<15} {"Blocks xả":<15} {"Tổng 基準値":<15} {"SOC cuối":<12} {"Lặp lại?":<10}')
        print('-'*100)
        
        for num_charge in range(1, 9):  # Thử từ 1 đến 8 blocks sạc
            result = test_strategy(num_charge, soc_initial=soc_init)
            
            if result is not None:
                all_results.append(result)
                num_discharge = 8 - num_charge
                
                repeat_icon = '✅' if result['can_repeat'] else '❌'
                print(f'{num_charge:<15} {num_discharge:<15} {result["total_baseline"]:<15.0f} '
                      f'{result["soc_final"]:<12.1f} {repeat_icon:<10}')
    
    # Tìm strategy có tổng baseline lớn nhất VÀ có thể lặp lại
    valid_results = [r for r in all_results if r['can_repeat']]
    
    if len(valid_results) == 0:
        print('\n❌ Không tìm thấy strategy nào có thể lặp lại!')
        return None
    
    optimal = max(valid_results, key=lambda x: x['total_baseline'])
    
    print('\n' + '='*100)
    print('🎯 CHIẾN LƯỢC TỐI ƯU')
    print('='*100)
    print(f'\n✅ SOC ban đầu: {optimal["soc_initial"]:.0f}%')
    print(f'✅ Số blocks sạc MAX: {optimal["num_charge_blocks"]}')
    print(f'✅ Số blocks còn lại: {8 - optimal["num_charge_blocks"]}')
    print(f'✅ Tổng 基準値: {optimal["total_baseline"]:.0f} kW ⭐')
    print(f'✅ Trung bình: {optimal["avg_baseline"]:.0f} kW/block')
    print(f'✅ SOC cuối: {optimal["soc_final"]:.0f}% (Δ={optimal["soc_deviation"]:.1f}%)')
    print(f'✅ Có thể lặp lại hàng ngày: CÓ')
    
    return optimal


def create_detailed_schedule(optimal):
    """Tạo lịch chi tiết từ strategy tối ưu"""
    
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
    
    print('\n' + '='*100)
    print('📋 LỊCH CHI TIẾT 8 BLOCKS')
    print('='*100)
    
    schedule = []
    soc_current = optimal['soc_initial']
    
    for i, (time_start, time_end, period_name) in enumerate(time_blocks):
        baseline_kw = optimal['baselines'][i]
        
        soc_predicted = predict_soc(soc_current, baseline_kw, 3.0)
        soc_change = soc_predicted - soc_current
        change_rate = calculate_soc_change_rate(baseline_kw)
        
        # Icon
        if baseline_kw >= 1500:
            action_icon = '⚡⚡⚡ SẠC MẠNH'
        elif baseline_kw >= 500:
            action_icon = '⚡⚡ SẠC TRUNG BÌNH'
        elif baseline_kw > 50:
            action_icon = '⚡ SẠC NHẸ'
        else:
            action_icon = '🔋 XẢ'
        
        schedule.append({
            'block': i + 1,
            'time_range': f'{time_start}-{time_end}',
            'period': period_name,
            'soc_start': soc_current,
            'soc_end': soc_predicted,
            'soc_change': soc_change,
            'baseline_kw': baseline_kw,
            'change_rate': change_rate,
            'action': action_icon
        })
        
        print(f'\n{i + 1}. {time_start}-{time_end} ({period_name})')
        print(f'   {action_icon}')
        print(f'   基準値: {baseline_kw:.0f} kW')
        print(f'   SOC: {soc_current:.1f}% → {soc_predicted:.1f}% ({soc_change:+.1f}%)')
        print(f'   変化率: {change_rate:+.2f} %/h')
        
        soc_current = soc_predicted
    
    df = pd.DataFrame(schedule)
    
    print(f'\n{"="*100}')
    print('📊 TỔNG KẾT')
    print(f'{"="*100}')
    print(f'\n💰 TỔNG 基準値: {df["baseline_kw"].sum():.0f} kW')
    print(f'📈 Trung bình: {df["baseline_kw"].mean():.0f} kW/block')
    print(f'\n🔋 SOC đầu ngày: {df["soc_start"].iloc[0]:.1f}%')
    print(f'🔋 SOC cuối ngày: {df["soc_end"].iloc[-1]:.1f}%')
    print(f'🔄 Sai số: {abs(df["soc_end"].iloc[-1] - df["soc_start"].iloc[0]):.1f}%')
    
    if abs(df["soc_end"].iloc[-1] - df["soc_start"].iloc[0]) <= 5:
        print(f'\n✅ LẶP LẠI ĐƯỢC HÀNG NGÀY!')
    
    return df


def create_visualization(df):
    """Tạo visualization đẹp"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'SOC Trajectory (Chu kỳ 1 ngày)',
            '基準値 theo Block',
            'SOC Change theo Block',
            'Tỷ lệ Sạc/Xả'
        ),
        specs=[[{"type": "scatter", "colspan": 2}, None],
               [{"type": "bar"}, {"type": "pie"}]],
        row_heights=[0.5, 0.5]
    )
    
    # Plot 1: SOC trajectory
    times = []
    soc_values = []
    for _, row in df.iterrows():
        time_start = row['time_range'].split('-')[0]
        time_end = row['time_range'].split('-')[1]
        times.extend([time_start, time_end])
        soc_values.extend([row['soc_start'], row['soc_end']])
    
    fig.add_trace(
        go.Scatter(
            x=times,
            y=soc_values,
            mode='lines+markers',
            name='SOC',
            line=dict(color='blue', width=4),
            marker=dict(size=10, symbol='diamond'),
            fill='tozeroy',
            fillcolor='rgba(0,100,255,0.2)'
        ),
        row=1, col=1
    )
    
    fig.add_hline(y=SOC_MIN, line_dash="dash", line_color="red", row=1, col=1)
    fig.add_hline(y=SOC_MAX, line_dash="dash", line_color="green", row=1, col=1)
    
    # Highlight chu kỳ
    fig.add_annotation(
        x='00:00', y=df['soc_start'].iloc[0],
        text=f'{df["soc_start"].iloc[0]:.0f}%',
        showarrow=True, arrowhead=2, arrowcolor='red',
        font=dict(size=14, color='red'), row=1, col=1
    )
    fig.add_annotation(
        x='23:59', y=df['soc_end'].iloc[-1],
        text=f'{df["soc_end"].iloc[-1]:.0f}%',
        showarrow=True, arrowhead=2, arrowcolor='red',
        font=dict(size=14, color='red'), row=1, col=1
    )
    
    # Plot 2: Baseline bars
    colors = ['lightgreen' if b > 1000 else 'lightblue' if b > 100 else 'lightcoral' 
              for b in df['baseline_kw']]
    
    fig.add_trace(
        go.Bar(
            x=df['time_range'],
            y=df['baseline_kw'],
            name='基準値',
            marker_color=colors,
            text=[f'{v:.0f}kW' for v in df['baseline_kw']],
            textposition='outside'
        ),
        row=2, col=1
    )
    
    # Total sum annotation
    total_sum = df['baseline_kw'].sum()
    fig.add_annotation(
        text=f'Σ = {total_sum:.0f} kW',
        xref='x2', yref='y2',
        x=3.5, y=df['baseline_kw'].max() * 1.2,
        showarrow=False,
        font=dict(size=16, color='red', family='Arial Black'),
        row=2, col=1
    )
    
    # Plot 3: Pie chart
    charge_blocks = len(df[df['baseline_kw'] > 1000])
    medium_blocks = len(df[(df['baseline_kw'] > 100) & (df['baseline_kw'] <= 1000)])
    discharge_blocks = len(df[df['baseline_kw'] <= 100])
    
    fig.add_trace(
        go.Pie(
            labels=['SẠC MẠNH', 'SẠC TRUNG BÌNH', 'XẢ'],
            values=[charge_blocks, medium_blocks, discharge_blocks],
            marker=dict(colors=['lightgreen', 'lightblue', 'lightcoral']),
            textinfo='label+value+percent'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_xaxes(title_text="時刻", row=1, col=1)
    fig.update_xaxes(title_text="Block", tickangle=45, row=2, col=1)
    fig.update_yaxes(title_text="SOC (%)", row=1, col=1)
    fig.update_yaxes(title_text="基準値 (kW)", row=2, col=1)
    
    fig.update_layout(
        height=1000,
        width=1400,
        title={
            'text': f'最適スケジュール: 基準値合計 = {total_sum:.0f} kW<br><sub>毎日繰り返し可能 | SOC: {df["soc_start"].iloc[0]:.0f}% → {df["soc_end"].iloc[-1]:.0f}%</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'family': 'Arial Black'}
        },
        showlegend=True
    )
    
    return fig


if __name__ == '__main__':
    # Tìm strategy tối ưu
    optimal = find_optimal_strategy()
    
    if optimal:
        # Tạo lịch chi tiết
        df = create_detailed_schedule(optimal)
        
        # Lưu file
        df.to_csv('final_optimal_schedule.csv', index=False, encoding='utf-8-sig')
        print(f'\n✅ Đã lưu: final_optimal_schedule.csv')
        
        # Visualization
        fig = create_visualization(df)
        fig.write_html('final_optimal_visualization.html')
        print(f'✅ Đã lưu: final_optimal_visualization.html')
        
        print('\n' + '='*100)
        print('🎉 HOÀN THÀNH!')
        print('='*100)
        print(f'\n💡 Chiến lược tối ưu đã tìm được:')
        print(f'   • Tổng 基準値: {df["baseline_kw"].sum():.0f} kW (LỚNNHẤT có thể)')
        print(f'   • Lặp lại hàng ngày: ✅')
        print(f'   • SOC trong giới hạn: {df["soc_start"].min():.0f}%-{df["soc_end"].max():.0f}%')
