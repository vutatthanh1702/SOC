"""
Tối ưu hóa để MAXIMIZE tổng 基準値 trong ngày
- Mục tiêu: Tổng 基準値 lớn nhất có thể
- Ràng buộc: SOC trong giới hạn 10-90%
- Điều kiện: Có thể lặp lại hàng ngày (SOC cuối ≈ SOC đầu)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize

# Công thức
SLOPE = 0.013545
INTERCEPT = -2.8197

# Giới hạn
SOC_MIN = 10
SOC_MAX = 90
BASELINE_MIN = 0
BASELINE_MAX = 2000


def calculate_soc_change_rate(baseline_kw):
    """Tính SOC変化率"""
    return SLOPE * baseline_kw + INTERCEPT


def predict_soc(soc_start, baseline_kw, hours):
    """Dự đoán SOC sau N giờ"""
    change_rate = calculate_soc_change_rate(baseline_kw)
    return soc_start + (change_rate * hours)


def optimize_daily_baseline_max_sum(soc_initial=15, tolerance=5):
    """
    Tối ưu hóa để MAXIMIZE tổng 基準値
    
    Chiến lược:
    - Sử dụng 基準値 cao nhất có thể khi SOC thấp (sạc mạnh)
    - Sử dụng 基準値 = 0 khi SOC cao (xả)
    - Đảm bảo SOC cuối ngày = SOC đầu ngày (chu kỳ)
    
    Args:
        soc_initial: SOC ban đầu
        tolerance: Sai số cho phép giữa SOC cuối và đầu (%)
    
    Returns:
        DataFrame với lịch tối ưu
    """
    
    print('='*100)
    print('🎯 TỐI ƯU HÓA: MAXIMIZE TỔNG 基準値')
    print('='*100)
    
    print(f'\n📊 Mục tiêu:')
    print(f'   • MAXIMIZE: Σ(基準値) = lớn nhất')
    print(f'   • Ràng buộc: {SOC_MIN}% ≤ SOC ≤ {SOC_MAX}%')
    print(f'   • Điều kiện chu kỳ: |SOC_cuối - SOC_đầu| ≤ {tolerance}%')
    
    # Chiến lược tối ưu:
    # 1. Bắt đầu với SOC thấp (~15%)
    # 2. Sạc MỌI KHỐI có thể (基準値 = MAX) đến gần SOC_MAX
    # 3. Xả (基準値 = 0) để về SOC ban đầu
    
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
    
    # Tính toán: Cần bao nhiêu blocks để sạc và xả
    # Với 基準値 = 2000kW → +22.67%/h → +68% mỗi 3h
    # Với 基準値 = 0kW → -2.82%/h → -8.5% mỗi 3h
    
    # Target: Sạc từ 15% lên gần 90%, sau đó xả về 15%
    soc_range = SOC_MAX - 5 - soc_initial  # ~70%
    soc_per_charge_block = SLOPE * BASELINE_MAX * 3  # ~68% per block
    
    num_charge_blocks = int(np.ceil(soc_range / soc_per_charge_block))
    
    # Tính SOC sau khi sạc hết
    soc_after_charge = soc_initial + num_charge_blocks * soc_per_charge_block
    
    # Cần xả bao nhiêu để về SOC ban đầu
    soc_to_discharge = soc_after_charge - soc_initial
    soc_per_discharge_block = abs(INTERCEPT * 3)  # 8.5% per block
    num_discharge_blocks = int(np.ceil(soc_to_discharge / soc_per_discharge_block))
    
    print(f'\n🔬 Phân tích tối ưu:')
    print(f'   SOC ban đầu: {soc_initial}%')
    print(f'   SOC target max: {SOC_MAX - 5}%')
    print(f'   Cần tăng: {soc_range:.1f}%')
    print(f'   ')
    print(f'   → Số blocks SẠC (基準値=MAX): {num_charge_blocks}')
    print(f'   → SOC sau khi sạc: {soc_after_charge:.1f}%')
    print(f'   → Số blocks XẢ (基準値=0): {num_discharge_blocks}')
    print(f'   → Số blocks còn lại: {8 - num_charge_blocks - num_discharge_blocks}')
    
    # Tạo lịch tối ưu
    schedule = []
    soc_current = soc_initial
    
    # Chiến lược đơn giản hơn: 
    # - Sạc MAX cho đến khi gần SOC_MAX
    # - Sau đó xả về SOC ban đầu
    # - Luôn đảm bảo có đúng 8 blocks
    
    baselines = []
    
    # Tính toán thực tế: cần bao nhiêu blocks sạc và xả
    # Giả sử: sạc từ 15% → 85% = +70%
    # Mỗi block sạc: +68%, mỗi block xả: -8.5%
    # Cần: 1 block sạc, sau đó xả về
    
    # Strategy: Maximize số blocks sạc, minimize blocks xả
    # Với SOC range = 75% (10-85%), mỗi chu kỳ:
    # - Sạc X blocks: +68X%
    # - Xả Y blocks: -8.5Y%
    # Điều kiện: 68X - 8.5Y ≈ 0 và X + Y = 8
    
    # Giải: 68X = 8.5Y và X + Y = 8
    # → X = 8.5Y/68 và X + Y = 8
    # → 8.5Y/68 + Y = 8
    # → Y(8.5/68 + 1) = 8
    # → Y = 8 / (8.5/68 + 1) = 7.1 → 7 blocks xả
    # → X = 1 block sạc
    
    # Nhưng để maximize tổng baseline, ta muốn nhiều blocks sạc hơn
    # Giải pháp: Bắt đầu từ SOC thấp, sạc nhiều blocks, xả ít blocks
    
    # Thử strategy: 5 blocks sạc + 3 blocks xả
    num_charge = 5
    num_discharge = 3
    
    for i in range(num_charge):
        baselines.append(BASELINE_MAX)
    
    for i in range(num_discharge):
        baselines.append(0)
    
    # Điều chỉnh để SOC cuối = SOC đầu
    # Thử nghiệm và fine-tune
    baselines = optimize_baselines_for_cycle(soc_initial, baselines, tolerance)
    
    print(f'\n{"="*100}')
    print('📋 LỊCH TỐI ƯU 8 BLOCKS')
    print(f'{"="*100}')
    
    total_baseline = 0
    
    for i, (time_start, time_end, period_name) in enumerate(time_blocks):
        baseline_kw = baselines[i]
        
        # Tính SOC
        soc_predicted = predict_soc(soc_current, baseline_kw, 3.0)
        soc_change = soc_predicted - soc_current
        change_rate = calculate_soc_change_rate(baseline_kw)
        
        # Icon
        if baseline_kw >= 1500:
            action_icon = '⚡⚡⚡'
        elif baseline_kw >= 500:
            action_icon = '⚡⚡'
        elif baseline_kw > 0:
            action_icon = '⚡'
        else:
            action_icon = '🔋📉'
        
        schedule.append({
            'block': i + 1,
            'time_range': f'{time_start}-{time_end}',
            'period': period_name,
            'soc_start': soc_current,
            'soc_predicted': soc_predicted,
            'soc_change': soc_change,
            'baseline_kw': baseline_kw,
            'change_rate': change_rate,
            'duration_hours': 3.0
        })
        
        total_baseline += baseline_kw
        
        print(f'\n{i + 1}. {time_start}-{time_end} ({period_name}) {action_icon}')
        print(f'   SOC: {soc_current:.1f}% → {soc_predicted:.1f}% ({soc_change:+.1f}%)')
        print(f'   基準値: {baseline_kw:.0f} kW  (変化率: {change_rate:+.2f} %/h)')
        
        soc_current = soc_predicted
    
    schedule_df = pd.DataFrame(schedule)
    
    print(f'\n{"="*100}')
    print('📊 KẾT QUẢ TỐI ƯU')
    print(f'{"="*100}')
    
    soc_final = schedule_df['soc_predicted'].iloc[-1]
    soc_deviation = abs(soc_final - soc_initial)
    
    print(f'\n🎯 TỔNG 基準値: {total_baseline:.0f} kW')
    print(f'   (Trung bình: {total_baseline/8:.0f} kW/block)')
    
    print(f'\n🔋 SOC:')
    print(f'   Đầu ngày:  {soc_initial:.1f}%')
    print(f'   Cuối ngày: {soc_final:.1f}%')
    print(f'   Chênh lệch: {soc_final - soc_initial:+.1f}%')
    
    print(f'\n   SOC max: {schedule_df["soc_predicted"].max():.1f}%')
    print(f'   SOC min: {schedule_df["soc_start"].min():.1f}%')
    print(f'   Biên độ: {schedule_df["soc_predicted"].max() - schedule_df["soc_start"].min():.1f}%')
    
    if soc_deviation <= tolerance:
        print(f'\n✅ CHU KỲ ỔN ĐỊNH: Sai số {soc_deviation:.1f}% ≤ {tolerance}%')
        print(f'   → Lịch có thể lặp lại hàng ngày!')
    else:
        print(f'\n⚠️  CHU KỲ chưa hoàn hảo: Sai số {soc_deviation:.1f}% > {tolerance}%')
        print(f'   → Cần điều chỉnh thêm')
    
    # Phân tích blocks
    charge_blocks = schedule_df[schedule_df['baseline_kw'] > 0]
    discharge_blocks = schedule_df[schedule_df['baseline_kw'] == 0]
    
    print(f'\n📈 Phân bố:')
    print(f'   Blocks sạc: {len(charge_blocks)} blocks')
    print(f'   Tổng 基準値 sạc: {charge_blocks["baseline_kw"].sum():.0f} kW')
    print(f'   Blocks xả: {len(discharge_blocks)} blocks')
    
    return schedule_df


def optimize_baselines_for_cycle(soc_initial, baselines_init, tolerance=5):
    """
    Fine-tune baselines để đảm bảo SOC cuối = SOC đầu
    """
    
    # Hàm mục tiêu: Minimize (SOC_cuối - SOC_đầu)^2 - α * Σ(baseline)
    # α là weight để cân bằng giữa chu kỳ và maximize baseline
    alpha = 0.1  # Weight nhỏ để ưu tiên chu kỳ
    
    def objective(baselines):
        soc = soc_initial
        for bl in baselines:
            soc = predict_soc(soc, bl, 3.0)
        
        # Penalty cho việc không đóng chu kỳ
        cycle_penalty = (soc - soc_initial) ** 2 * 1000
        
        # Reward cho tổng baseline cao
        baseline_reward = -alpha * sum(baselines)
        
        # Penalty cho việc vượt giới hạn SOC
        soc_temp = soc_initial
        soc_penalty = 0
        for bl in baselines:
            soc_temp = predict_soc(soc_temp, bl, 3.0)
            if soc_temp > SOC_MAX:
                soc_penalty += (soc_temp - SOC_MAX) ** 2 * 10000
            elif soc_temp < SOC_MIN:
                soc_penalty += (SOC_MIN - soc_temp) ** 2 * 10000
        
        return cycle_penalty + baseline_reward + soc_penalty
    
    # Constraints: 0 <= baseline <= 2000
    bounds = [(BASELINE_MIN, BASELINE_MAX) for _ in range(8)]
    
    # Optimize
    result = minimize(
        objective,
        baselines_init,
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 1000}
    )
    
    if result.success:
        return result.x
    else:
        return baselines_init


def create_comparison_multi_strategies():
    """So sánh các chiến lược khác nhau"""
    
    print('\n' + '='*100)
    print('📊 SO SÁNH CÁC CHIẾN LƯỢC')
    print('='*100)
    
    strategies = []
    
    # Strategy 1: Maximize tổng baseline
    print('\n' + '─'*100)
    print('📋 CHIẾN LƯỢC 1: MAXIMIZE TỔNG 基準値')
    print('─'*100)
    df1 = optimize_daily_baseline_max_sum(soc_initial=15, tolerance=5)
    strategies.append(('Max Sum', df1))
    
    # Strategy 2: Balanced (để so sánh)
    print('\n' + '─'*100)
    print('📋 CHIẾN LƯỢC 2: BALANCED (tham chiếu)')
    print('─'*100)
    from new_day_scheduler import create_smart_schedule
    df2 = create_smart_schedule(20, 80, 'balanced')
    strategies.append(('Balanced', df2))
    
    # Strategy 3: Morning charge (để so sánh)
    print('\n' + '─'*100)
    print('📋 CHIẾN LƯỢC 3: MORNING CHARGE (tham chiếu)')
    print('─'*100)
    df3 = create_smart_schedule(15, 75, 'morning_charge')
    strategies.append(('Morning Charge', df3))
    
    # Tạo bảng so sánh
    print('\n' + '='*100)
    print('📊 BẢNG SO SÁNH')
    print('='*100)
    
    comparison = []
    for name, df in strategies:
        total_baseline = df['baseline_kw'].sum()
        avg_baseline = df['baseline_kw'].mean()
        soc_start = df['soc_start'].iloc[0]
        soc_end = df['soc_predicted'].iloc[-1]
        soc_deviation = abs(soc_end - soc_start)
        can_repeat = '✅' if soc_deviation <= 5 else '❌'
        
        comparison.append({
            'Strategy': name,
            'Total 基準値': f'{total_baseline:.0f} kW',
            'Avg 基準値': f'{avg_baseline:.0f} kW',
            'SOC Start': f'{soc_start:.1f}%',
            'SOC End': f'{soc_end:.1f}%',
            'Can Repeat': can_repeat
        })
    
    comparison_df = pd.DataFrame(comparison)
    print('\n' + comparison_df.to_string(index=False))
    
    # Tạo visualization
    create_comparison_visualization(strategies)
    
    return strategies


def create_comparison_visualization(strategies):
    """Tạo visualization so sánh các strategies"""
    
    fig = make_subplots(
        rows=2, cols=len(strategies),
        subplot_titles=[name for name, _ in strategies],
        specs=[[{"type": "scatter"}] * len(strategies),
               [{"type": "bar"}] * len(strategies)],
        vertical_spacing=0.15,
        horizontal_spacing=0.08
    )
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for idx, (name, df) in enumerate(strategies):
        col = idx + 1
        
        # Row 1: SOC curve
        times = []
        soc_values = []
        for _, row in df.iterrows():
            time_start = row['time_range'].split('-')[0]
            time_end = row['time_range'].split('-')[1]
            times.extend([time_start, time_end])
            soc_values.extend([row['soc_start'], row['soc_predicted']])
        
        fig.add_trace(
            go.Scatter(
                x=times,
                y=soc_values,
                mode='lines+markers',
                name=name,
                line=dict(color=colors[idx % len(colors)], width=3),
                marker=dict(size=8),
                showlegend=False
            ),
            row=1, col=col
        )
        
        # SOC limits
        fig.add_hline(y=SOC_MIN, line_dash="dot", line_color="orange", row=1, col=col)
        fig.add_hline(y=SOC_MAX, line_dash="dot", line_color="green", row=1, col=col)
        
        # Row 2: Baseline bars
        fig.add_trace(
            go.Bar(
                x=df['time_range'],
                y=df['baseline_kw'],
                name=name,
                marker_color=colors[idx % len(colors)],
                text=[f'{v:.0f}' for v in df['baseline_kw']],
                textposition='outside',
                showlegend=False
            ),
            row=2, col=col
        )
        
        # Add total sum annotation
        total_sum = df['baseline_kw'].sum()
        fig.add_annotation(
            text=f'Σ={total_sum:.0f}kW',
            xref=f'x{col + len(strategies)}', yref=f'y{col + len(strategies)}',
            x=3.5, y=df['baseline_kw'].max() * 1.2,
            showarrow=False,
            font=dict(size=14, color='red', family='Arial Black')
        )
    
    # Update axes
    for col in range(1, len(strategies) + 1):
        fig.update_xaxes(title_text="時刻", row=1, col=col)
        fig.update_xaxes(title_text="Block", row=2, col=col, tickangle=45)
        fig.update_yaxes(title_text="SOC (%)", row=1, col=col)
        fig.update_yaxes(title_text="基準値 (kW)", row=2, col=col)
    
    fig.update_layout(
        height=900,
        width=500 * len(strategies),
        title={
            'text': '比較: 各種最適化戦略<br><sub>目標: 基準値合計を最大化しながら毎日繰り返し可能</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        }
    )
    
    fig.write_html('strategy_comparison_maximize_baseline.html')
    print('\n✅ Đã lưu: strategy_comparison_maximize_baseline.html')


if __name__ == '__main__':
    print('='*100)
    print('🚀 TỐI ƯU HÓA: MAXIMIZE TỔNG 基準値 + LẶP LẠI HÀNG NGÀY')
    print('='*100)
    
    # Tạo lịch tối ưu
    optimal_df = optimize_daily_baseline_max_sum(soc_initial=15, tolerance=5)
    
    # Lưu file
    optimal_df.to_csv('optimal_maximize_baseline.csv', index=False, encoding='utf-8-sig')
    print(f'\n✅ Đã lưu: optimal_maximize_baseline.csv')
    
    # So sánh với các chiến lược khác
    strategies = create_comparison_multi_strategies()
    
    print('\n' + '='*100)
    print('💡 KẾT LUẬN')
    print('='*100)
    print("""
    Để MAXIMIZE tổng 基準値 VÀ lặp lại hàng ngày:
    
    1. Bắt đầu với SOC thấp (~15%)
    2. Sạc LIÊN TỤC với 基準値 = MAX (2000kW) càng nhiều blocks càng tốt
    3. Xả (基準値 = 0) để quay về SOC ban đầu
    4. Đảm bảo SOC cuối ≈ SOC đầu (sai số < 5%)
    
    → Đạt được TỔNG 基準値 LỚN NHẤT có thể trong giới hạn vật lý!
    """)
