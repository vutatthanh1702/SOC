"""
CHỨNG MINH TOÁN HỌC: TÌM PATTERN TỐI ƯU
Maximize: Σ(基準値) với điều kiện SOC cuối = SOC đầu
"""

import numpy as np
import pandas as pd
from scipy.optimize import linprog, minimize
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Công thức
SLOPE = 0.013545
INTERCEPT = -2.8197

# Giới hạn
SOC_MIN = 10
SOC_MAX = 90
BASELINE_MIN = 0
BASELINE_MAX = 2000

HOURS_PER_BLOCK = 3.0
NUM_BLOCKS = 8


def prove_optimal_pattern():
    """
    Chứng minh toán học bằng Linear Programming
    
    Bài toán:
        Maximize: Σ(b_i) cho i=1..8
        
        Constraints:
        1. SOC balance: Σ(SLOPE * b_i * 3 + INTERCEPT * 3) = 0
        2. SOC limits: SOC_MIN ≤ SOC(t) ≤ SOC_MAX tại mọi thời điểm t
        3. Baseline limits: 0 ≤ b_i ≤ 2000
    
    Trong đó b_i là 基準値 cho block i
    """
    
    print('='*100)
    print('📐 CHỨNG MINH TOÁN HỌC: PATTERN TỐI ƯU')
    print('='*100)
    
    print('\n🎯 BÀI TOÁN TỐI ƯU:')
    print(f'   Maximize: Σ(基準値_i) cho i = 1..8')
    print(f'   ')
    print(f'   Ràng buộc:')
    print(f'   1. Chu kỳ: Σ(ΔSOCi) = 0  (SOC cuối = SOC đầu)')
    print(f'   2. SOC limits: {SOC_MIN}% ≤ SOC(t) ≤ {SOC_MAX}%')
    print(f'   3. Baseline: {BASELINE_MIN} ≤ 基準値_i ≤ {BASELINE_MAX} kW')
    
    # Phương trình SOC change
    print(f'\n📊 CÔNG THỨC:')
    print(f'   ΔSOC_i = (SLOPE × 基準値_i + INTERCEPT) × 3 giờ')
    print(f'   ΔSOC_i = ({SLOPE} × 基準値_i + {INTERCEPT}) × 3')
    print(f'   ΔSOC_i = {SLOPE * 3:.6f} × 基準値_i + {INTERCEPT * 3:.6f}')
    
    # Phân tích constraint chính
    print(f'\n🔬 PHÂN TÍCH CONSTRAINT CHU KỲ:')
    print(f'   Σ(ΔSOC_i) = 0')
    print(f'   Σ({SLOPE * 3:.6f} × 基準値_i + {INTERCEPT * 3:.6f}) = 0')
    print(f'   {SLOPE * 3:.6f} × Σ(基準値_i) + 8 × {INTERCEPT * 3:.6f} = 0')
    print(f'   {SLOPE * 3:.6f} × Σ(基準値_i) = {-8 * INTERCEPT * 3:.6f}')
    print(f'   Σ(基準値_i) = {-8 * INTERCEPT * 3 / (SLOPE * 3):.2f} kW')
    
    # Kết luận quan trọng
    baseline_sum_required = -8 * INTERCEPT / SLOPE
    print(f'\n✨ KẾT LUẬN QUAN TRỌNG:')
    print(f'   Để chu kỳ ổn định, TỔNG 基準値 phải CHÍNH XÁC = {baseline_sum_required:.2f} kW')
    print(f'   → Đây là HẰNG SỐ, KHÔNG PHỤ THUỘC vào cách phân bổ!')
    
    return baseline_sum_required


def find_all_optimal_patterns(baseline_sum_required):
    """
    Với tổng cố định, tìm tất cả các patterns khác nhau
    """
    
    print('\n' + '='*100)
    print('🔍 TÌM TẤT CẢ CÁC PATTERNS TỐI ƯU')
    print('='*100)
    
    print(f'\n💡 Với tổng 基準値 = {baseline_sum_required:.2f} kW (cố định)')
    print(f'   Bài toán trở thành: Tìm cách PHÂN BỔ để:')
    print(f'   1. Σ(基準値_i) = {baseline_sum_required:.2f}')
    print(f'   2. SOC không vượt giới hạn [{SOC_MIN}%, {SOC_MAX}%]')
    print(f'   3. Mỗi 基準値_i trong [0, {BASELINE_MAX}] kW')
    
    # Chiến lược khác nhau với cùng tổng
    patterns = []
    
    # Pattern 1: Phân bố đều
    b_even = baseline_sum_required / 8
    if b_even <= BASELINE_MAX:
        patterns.append({
            'name': 'Phân bố đều',
            'baselines': [b_even] * 8,
            'description': f'Tất cả {b_even:.0f}kW'
        })
    
    # Pattern 2: Tập trung vào 1 block MAX
    # Nếu 1 block = 2000, các block khác = (sum - 2000) / 7
    b_remain = (baseline_sum_required - BASELINE_MAX) / 7
    if b_remain >= 0 and b_remain <= BASELINE_MAX:
        baselines = [BASELINE_MAX] + [b_remain] * 7
        patterns.append({
            'name': 'Sạc mạnh 1 block',
            'baselines': baselines,
            'description': f'1 block {BASELINE_MAX:.0f}kW, 7 blocks {b_remain:.0f}kW'
        })
    
    # Pattern 3: 2 blocks MAX
    if baseline_sum_required >= 2 * BASELINE_MAX:
        b_remain = (baseline_sum_required - 2 * BASELINE_MAX) / 6
        if b_remain >= 0 and b_remain <= BASELINE_MAX:
            baselines = [BASELINE_MAX, BASELINE_MAX] + [b_remain] * 6
            patterns.append({
                'name': 'Sạc mạnh 2 blocks',
                'baselines': baselines,
                'description': f'2 blocks {BASELINE_MAX:.0f}kW, 6 blocks {b_remain:.0f}kW'
            })
    
    # Pattern 4: 3 blocks MAX
    if baseline_sum_required >= 3 * BASELINE_MAX:
        b_remain = (baseline_sum_required - 3 * BASELINE_MAX) / 5
        if b_remain >= 0 and b_remain <= BASELINE_MAX:
            baselines = [BASELINE_MAX] * 3 + [b_remain] * 5
            patterns.append({
                'name': 'Sạc mạnh 3 blocks',
                'baselines': baselines,
                'description': f'3 blocks {BASELINE_MAX:.0f}kW, 5 blocks {b_remain:.0f}kW'
            })
    
    # Pattern 5: Theo data thực tế (1 block 2000, 1 block 532, còn lại thấp)
    # 2000 + 532 + 6x = 1665 → x = (1665 - 2532) / 6 < 0 (không khả thi)
    # Thử: 1 block 2000, 1 block X, 6 blocks = 0
    # 2000 + X = 1665 → X = -335 < 0 (không khả thi)
    
    # Pattern 6: Dùng baseline = 0 (xả)
    # Nếu N blocks = 0, các blocks còn lại = sum / (8-N)
    for n_zero in range(1, 8):
        b_others = baseline_sum_required / (8 - n_zero)
        if 0 <= b_others <= BASELINE_MAX:
            baselines = [b_others] * (8 - n_zero) + [0] * n_zero
            patterns.append({
                'name': f'{n_zero} blocks xả',
                'baselines': baselines,
                'description': f'{8-n_zero} blocks {b_others:.0f}kW, {n_zero} blocks 0kW'
            })
    
    # Pattern 7: Mix MAX và 0
    # N blocks MAX, M blocks = 0, còn lại = X
    for n_max in range(1, 8):
        for n_zero in range(1, 8 - n_max):
            n_mid = 8 - n_max - n_zero
            if n_mid > 0:
                b_mid = (baseline_sum_required - n_max * BASELINE_MAX) / n_mid
                if 0 <= b_mid <= BASELINE_MAX:
                    baselines = [BASELINE_MAX] * n_max + [b_mid] * n_mid + [0] * n_zero
                    patterns.append({
                        'name': f'{n_max}MAX+{n_mid}mid+{n_zero}zero',
                        'baselines': baselines,
                        'description': f'{n_max}×{BASELINE_MAX:.0f}kW + {n_mid}×{b_mid:.0f}kW + {n_zero}×0kW'
                    })
    
    print(f'\n✅ Tìm thấy {len(patterns)} patterns khả thi!')
    
    return patterns


def evaluate_pattern(baselines, soc_initial=15):
    """
    Đánh giá một pattern: kiểm tra SOC có vượt giới hạn không
    """
    
    soc = soc_initial
    soc_trajectory = [soc]
    valid = True
    
    for b in baselines:
        delta_soc = (SLOPE * b + INTERCEPT) * HOURS_PER_BLOCK
        soc += delta_soc
        soc_trajectory.append(soc)
        
        if soc < SOC_MIN or soc > SOC_MAX:
            valid = False
    
    soc_final = soc_trajectory[-1]
    cycle_error = abs(soc_final - soc_initial)
    
    return {
        'valid': valid and cycle_error < 1,
        'soc_trajectory': soc_trajectory,
        'soc_min': min(soc_trajectory),
        'soc_max': max(soc_trajectory),
        'cycle_error': cycle_error
    }


def compare_all_patterns(patterns, soc_initial=15):
    """
    So sánh tất cả patterns
    """
    
    print('\n' + '='*100)
    print('📊 SO SÁNH TẤT CẢ PATTERNS')
    print('='*100)
    
    print(f'\nSOC ban đầu: {soc_initial}%')
    print(f'\n{"Pattern":<30} {"SOC min-max":<20} {"Valid?":<10} {"Cycle Error":<15}')
    print('-'*100)
    
    valid_patterns = []
    
    for pattern in patterns:
        eval_result = evaluate_pattern(pattern['baselines'], soc_initial)
        pattern['evaluation'] = eval_result
        
        valid_icon = '✅' if eval_result['valid'] else '❌'
        soc_range = f"{eval_result['soc_min']:.1f}%-{eval_result['soc_max']:.1f}%"
        
        print(f"{pattern['name']:<30} {soc_range:<20} {valid_icon:<10} {eval_result['cycle_error']:.4f}%")
        
        if eval_result['valid']:
            valid_patterns.append(pattern)
    
    print(f'\n✅ Có {len(valid_patterns)} patterns HỢP LỆ (thỏa mãn tất cả constraints)')
    
    return valid_patterns


def create_comparison_visualization(valid_patterns, soc_initial=15):
    """
    Visualization so sánh các patterns hợp lệ
    """
    
    if len(valid_patterns) == 0:
        print('\n❌ Không có pattern nào hợp lệ để vẽ!')
        return
    
    # Chọn top 6 patterns để hiển thị
    patterns_to_show = valid_patterns[:min(6, len(valid_patterns))]
    
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[p['name'] for p in patterns_to_show],
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
        specs=[[{"secondary_y": True}] * 2] * 3
    )
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    for idx, pattern in enumerate(patterns_to_show):
        row = idx // 2 + 1
        col = idx % 2 + 1
        color = colors[idx]
        
        # SOC trajectory
        blocks = list(range(9))  # 0-8
        soc_traj = pattern['evaluation']['soc_trajectory']
        
        fig.add_trace(
            go.Scatter(
                x=blocks,
                y=soc_traj,
                mode='lines+markers',
                name=f'SOC - {pattern["name"]}',
                line=dict(color=color, width=2),
                marker=dict(size=8),
                showlegend=False
            ),
            row=row, col=col, secondary_y=False
        )
        
        # SOC limits
        fig.add_hline(y=SOC_MIN, line_dash="dot", line_color="red", 
                     opacity=0.5, row=row, col=col, secondary_y=False)
        fig.add_hline(y=SOC_MAX, line_dash="dot", line_color="green", 
                     opacity=0.5, row=row, col=col, secondary_y=False)
        
        # Baseline bars
        fig.add_trace(
            go.Bar(
                x=list(range(1, 9)),
                y=pattern['baselines'],
                name=f'基準値 - {pattern["name"]}',
                marker_color='lightblue',
                opacity=0.6,
                showlegend=False,
                yaxis='y2'
            ),
            row=row, col=col, secondary_y=True
        )
        
        # Annotations
        total_baseline = sum(pattern['baselines'])
        fig.add_annotation(
            text=f"Σ={total_baseline:.0f}kW",
            xref=f'x{idx+1}', yref=f'y{idx+1}',
            x=4.5, y=pattern['evaluation']['soc_max'] * 0.95,
            showarrow=False,
            font=dict(size=12, color='red', family='Arial Black'),
            row=row, col=col
        )
    
    # Update axes
    for row in range(1, 4):
        for col in [1, 2]:
            fig.update_xaxes(title_text="Block", row=row, col=col)
            fig.update_yaxes(title_text="SOC (%)", row=row, col=col, secondary_y=False)
            fig.update_yaxes(title_text="基準値 (kW)", row=row, col=col, secondary_y=True)
    
    fig.update_layout(
        height=1400,
        width=1600,
        title={
            'text': 'すべての最適パターン比較<br><sub>総基準値は一定 (数学的制約)</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22}
        }
    )
    
    return fig


def prove_uniqueness_of_sum():
    """
    Chứng minh tổng 基準値 là DUY NHẤT
    """
    
    print('\n' + '='*100)
    print('🔬 CHỨNG MINH: TỔNG 基準値 LÀ DUY NHẤT')
    print('='*100)
    
    print(f'\n📐 Bằng đại số:')
    print(f'   Điều kiện chu kỳ: Σ(ΔSOC_i) = 0')
    print(f'   ')
    print(f'   ΔSOC_i = (a × b_i + c) × h')
    print(f'   trong đó:')
    print(f'     a = SLOPE = {SLOPE}')
    print(f'     c = INTERCEPT = {INTERCEPT}')
    print(f'     h = hours per block = {HOURS_PER_BLOCK}')
    print(f'     b_i = 基準値_i')
    print(f'   ')
    print(f'   Σ(ΔSOC_i) = Σ((a × b_i + c) × h) = 0')
    print(f'   ')
    print(f'   h × Σ(a × b_i + c) = 0')
    print(f'   ')
    print(f'   Σ(a × b_i + c) = 0')
    print(f'   ')
    print(f'   a × Σ(b_i) + n × c = 0    (n = số blocks = 8)')
    print(f'   ')
    print(f'   Σ(b_i) = -n × c / a')
    print(f'   ')
    print(f'   Σ(b_i) = -8 × {INTERCEPT} / {SLOPE}')
    
    baseline_sum = -8 * INTERCEPT / SLOPE
    
    print(f'   ')
    print(f'   Σ(b_i) = {baseline_sum:.6f} kW')
    
    print(f'\n✅ KẾT LUẬN:')
    print(f'   Tổng 基準値 PHẢI bằng {baseline_sum:.2f} kW')
    print(f'   → Đây là HẰNG SỐ, không phụ thuộc vào cách phân bổ!')
    print(f'   → KHÔNG THỂ tăng thêm được!')
    
    print(f'\n💡 Ý NGHĨA:')
    print(f'   Tất cả các patterns "tối ưu" đều có CÙNG tổng 基準値')
    print(f'   Sự khác biệt chỉ là cách PHÂN BỔ, không phải tổng!')
    print(f'   Không có pattern nào "tốt hơn" về mặt tổng 基準値!')
    
    return baseline_sum


if __name__ == '__main__':
    print('='*100)
    print('🎓 CHỨNG MINH TOÁN HỌC: PATTERN TỐI ƯU CHO BÀI TOÁN LỊCH PIN')
    print('='*100)
    
    # Step 1: Chứng minh tổng baseline là hằng số
    baseline_sum_required = prove_optimal_pattern()
    
    # Step 2: Chứng minh sự duy nhất
    prove_uniqueness_of_sum()
    
    # Step 3: Tìm tất cả patterns khả thi
    patterns = find_all_optimal_patterns(baseline_sum_required)
    
    # Step 4: Đánh giá và lọc patterns hợp lệ
    valid_patterns = compare_all_patterns(patterns, soc_initial=15)
    
    # Step 5: Visualization
    if len(valid_patterns) > 0:
        fig = create_comparison_visualization(valid_patterns, soc_initial=15)
        if fig:
            fig.write_html('all_optimal_patterns_comparison.html')
            print(f'\n✅ Đã lưu: all_optimal_patterns_comparison.html')
    
    # Step 6: Kết luận cuối cùng
    print('\n' + '='*100)
    print('🎯 KẾT LUẬN CUỐI CÙNG')
    print('='*100)
    
    print(f'\n1️⃣ TỔNG 基準値 LÀ HẰNG SỐ:')
    print(f'   Σ(基準値) = {baseline_sum_required:.2f} kW (DUY NHẤT)')
    print(f'   → Được xác định bởi công thức và điều kiện chu kỳ')
    print(f'   → KHÔNG THỂ tăng hoặc giảm!')
    
    print(f'\n2️⃣ CÓ {len(valid_patterns)} PATTERNS HỢP LỆ:')
    for i, p in enumerate(valid_patterns[:5], 1):
        print(f'   {i}. {p["name"]}: {p["description"]}')
    if len(valid_patterns) > 5:
        print(f'   ... và {len(valid_patterns) - 5} patterns khác')
    
    print(f'\n3️⃣ TẤT CẢ PATTERNS ĐỀU "TỐI ƯU" NHƯ NHAU:')
    print(f'   ✅ Cùng tổng 基準値 = {baseline_sum_required:.2f} kW')
    print(f'   ✅ Đều thỏa mãn điều kiện chu kỳ')
    print(f'   ✅ Khác nhau chỉ là cách PHÂN BỔ')
    
    print(f'\n4️⃣ LỰA CHỌN PATTERN TỐT NHẤT:')
    print(f'   Tiêu chí lựa chọn KHÔNG phải tổng 基準値 (vì bằng nhau)')
    print(f'   mà dựa trên:')
    print(f'   • Tận dụng thời gian điện rẻ')
    print(f'   • Tránh peak load')
    print(f'   • Phù hợp với nhu cầu thực tế')
    print(f'   • Giảm số lần chuyển đổi (wear & tear)')
    
    print(f'\n5️⃣ PATTERN TỪ DATA THỰC TẾ:')
    print(f'   Data cho thấy: sạc mạnh buổi sáng (06:00-09:00)')
    print(f'   → Có lý do kinh tế (giá điện, solar, nhu cầu)')
    print(f'   → Đây là pattern "tối ưu thực tế", không phải "tối ưu toán học"')
    
    print('\n' + '='*100)
    print('📝 Lưu kết quả')
    print('='*100)
    
    # Lưu summary
    summary_df = pd.DataFrame([{
        'Pattern': p['name'],
        'Description': p['description'],
        'Total_baseline': sum(p['baselines']),
        'SOC_min': p['evaluation']['soc_min'],
        'SOC_max': p['evaluation']['soc_max'],
        'Cycle_error': p['evaluation']['cycle_error']
    } for p in valid_patterns])
    
    summary_df.to_csv('all_optimal_patterns_summary.csv', index=False, encoding='utf-8-sig')
    print('\n✅ Đã lưu: all_optimal_patterns_summary.csv')
    
    print('\n' + '='*100)
