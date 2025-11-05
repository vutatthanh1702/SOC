import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def calculate_optimal_baseline_smart(current_soc, target_soc_max=90, block_hours=3):
    """
    現在のSOCから最適な基準値を計算（90%制約付き）
    
    Parameters:
    -----------
    current_soc : float
        現在のSOC (%)
    target_soc_max : float
        目標最大SOC (デフォルト: 90%)
    block_hours : float
        基準値設定の時間ブロック (デフォルト: 3時間)
    
    Returns:
    --------
    optimal_baseline : float
        最適な基準値 (kW)
    predicted_soc : float
        予想される到達SOC (%)
    """
    
    # 線形回帰式: SOC変化率 = 0.012804 × 基準値 - 1.9515 (%/時間)
    SLOPE = 0.012804
    INTERCEPT = -1.9515
    
    # SOCが既に90%以上の場合
    if current_soc >= target_soc_max:
        # 基準値を0に設定してSOCを下げる（自然放電）
        optimal_baseline = 0
        predicted_rate = SLOPE * optimal_baseline + INTERCEPT
        predicted_soc = current_soc + (predicted_rate * block_hours)
        return optimal_baseline, max(predicted_soc, target_soc_max - 10)  # 最大でも80%まで下がる
    
    # SOCが90%未満の場合
    available_soc_increase = target_soc_max - current_soc
    
    # 1時間あたりの最大SOC変化率
    max_rate_per_hour = available_soc_increase / block_hours
    
    # 基準値を計算
    optimal_baseline = (max_rate_per_hour - INTERCEPT) / SLOPE
    
    # 負の値を防ぐ
    optimal_baseline = max(0, optimal_baseline)
    
    # 予想されるSOC変化
    predicted_rate = SLOPE * optimal_baseline + INTERCEPT
    predicted_soc = current_soc + (predicted_rate * block_hours)
    
    # 90%を超えないように調整
    if predicted_soc > target_soc_max:
        predicted_soc = target_soc_max
    
    return optimal_baseline, predicted_soc


def generate_optimal_daily_schedule(initial_soc, start_hour=6, total_hours=24, block_hours=3):
    """
    1日分の最適スケジュールを生成（24時間）
    
    Parameters:
    -----------
    initial_soc : float
        開始時のSOC (%)
    start_hour : int
        開始時刻 (0-23)
    total_hours : int
        スケジュール時間 (デフォルト: 24時間)
    block_hours : int
        時間ブロック (デフォルト: 3時間)
    
    Returns:
    --------
    schedule : pandas DataFrame
        時間帯ごとのスケジュール
    """
    
    schedule = []
    current_soc = initial_soc
    current_hour = start_hour
    block_num = 1
    
    hours_processed = 0
    
    while hours_processed < total_hours:
        # 最適基準値を計算
        optimal_baseline, predicted_soc = calculate_optimal_baseline_smart(
            current_soc, 
            target_soc_max=90, 
            block_hours=block_hours
        )
        
        # 時間の計算
        end_hour = (current_hour + block_hours) % 24
        
        schedule.append({
            'block': block_num,
            'start_hour': current_hour,
            'end_hour': end_hour,
            'duration_hours': block_hours,
            'soc_start': round(current_soc, 1),
            'optimal_baseline_kw': round(optimal_baseline, 0),
            'soc_end': round(predicted_soc, 1),
            'soc_change': round(predicted_soc - current_soc, 1)
        })
        
        # 次のブロックの準備
        current_soc = predicted_soc
        current_hour = end_hour
        hours_processed += block_hours
        block_num += 1
    
    return pd.DataFrame(schedule)


def create_optimization_visualization(schedule_df, initial_soc):
    """
    最適化スケジュールの可視化
    """
    
    # 時間軸データを作成（1分刻み）
    time_points = []
    soc_values = []
    baseline_values = []
    
    for _, row in schedule_df.iterrows():
        # 各ブロックの時間範囲を分割
        start_minutes = row['start_hour'] * 60
        end_minutes = start_minutes + (row['duration_hours'] * 60)
        
        # 時間ポイントを生成
        for minute in range(int(start_minutes), int(end_minutes) + 1, 10):  # 10分刻み
            hours = minute / 60
            time_points.append(hours)
            
            # SOCの線形補間
            progress = (minute - start_minutes) / (end_minutes - start_minutes)
            soc = row['soc_start'] + (row['soc_end'] - row['soc_start']) * progress
            soc_values.append(soc)
            
            # 基準値は一定
            baseline_values.append(row['optimal_baseline_kw'])
    
    # グラフ作成
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('最適化スケジュール: SOCと基準値の24時間変化', 
                       '各時間ブロックの詳細'),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
    )
    
    # 上部グラフ: SOCと基準値の時間変化（棒グラフ）
    # SOCを棒グラフで表示
    fig.add_trace(
        go.Bar(
            x=time_points,
            y=soc_values,
            name='SOC (%)',
            marker=dict(
                color=soc_values,
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="SOC (%)", x=1.15)
            ),
            opacity=0.7,
            width=0.15
        ),
        row=1, col=1,
        secondary_y=False
    )
    
    # 基準値を棒グラフで表示
    fig.add_trace(
        go.Bar(
            x=time_points,
            y=baseline_values,
            name='基準値 (kW)',
            marker=dict(
                color=baseline_values,
                colorscale='Greens',
                showscale=True,
                colorbar=dict(title="基準値 (kW)", x=1.3)
            ),
            opacity=0.6,
            width=0.15
        ),
        row=1, col=1,
        secondary_y=True
    )
    
    # 90%の目標ラインを追加
    fig.add_hline(
        y=90, 
        line_dash="dot", 
        line_color="red",
        annotation_text="目標SOC上限 (90%)",
        annotation_position="right",
        row=1, col=1,
        secondary_y=False
    )
    
    # 下部グラフ: 各ブロックの詳細（棒グラフ）
    block_centers = schedule_df['start_hour'] + schedule_df['duration_hours'] / 2
    
    fig.add_trace(
        go.Bar(
            x=block_centers,
            y=schedule_df['optimal_baseline_kw'],
            name='基準値 (kW)',
            marker_color='green',
            opacity=0.6,
            text=schedule_df['optimal_baseline_kw'].astype(int),
            textposition='outside'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=block_centers,
            y=schedule_df['soc_start'],
            mode='markers+lines',
            name='開始SOC',
            marker=dict(size=10, color='blue'),
            line=dict(color='blue', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=block_centers,
            y=schedule_df['soc_end'],
            mode='markers+lines',
            name='終了SOC',
            marker=dict(size=10, color='navy', symbol='diamond'),
            line=dict(color='navy', width=2, dash='dot')
        ),
        row=2, col=1
    )
    
    # レイアウト設定
    fig.update_xaxes(
        title_text="時刻 (時)", 
        range=[0, 24],
        tickmode='linear',
        tick0=0,
        dtick=3,
        row=1, col=1
    )
    
    fig.update_xaxes(
        title_text="時刻 (時)", 
        range=[0, 24],
        tickmode='linear',
        tick0=0,
        dtick=3,
        row=2, col=1
    )
    
    fig.update_yaxes(
        title_text="SOC (%)", 
        range=[0, 100],
        row=1, col=1,
        secondary_y=False
    )
    
    fig.update_yaxes(
        title_text="基準値 (kW)", 
        row=1, col=1,
        secondary_y=True
    )
    
    fig.update_yaxes(
        title_text="値", 
        row=2, col=1
    )
    
    fig.update_layout(
        height=1000,
        width=1400,
        title={
            'text': f'SOC最適化スケジュール (初期SOC: {initial_soc}%)<br><sub>制約: SOC ≤ 90%, 3時間ブロック</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    return fig


def print_schedule_table(schedule_df):
    """
    スケジュールを表形式で表示
    """
    print("\n" + "="*100)
    print("24時間最適化スケジュール")
    print("="*100)
    print(f"{'Block':<6} {'時間帯':<15} {'開始SOC':<10} {'基準値':<15} {'終了SOC':<10} {'SOC変化':<12} {'状態':<15}")
    print("-"*100)
    
    total_baseline = 0
    
    for _, row in schedule_df.iterrows():
        time_range = f"{int(row['start_hour']):02d}:00-{int(row['end_hour']):02d}:00"
        
        # 状態判定
        if row['soc_end'] >= 90:
            status = "目標到達 ✓"
        elif row['soc_change'] > 0:
            status = "充電中 ↑"
        elif row['soc_change'] < 0:
            status = "放電中 ↓"
        else:
            status = "維持 →"
        
        print(f"{int(row['block']):<6} "
              f"{time_range:<15} "
              f"{row['soc_start']:<9.1f}% "
              f"{row['optimal_baseline_kw']:<14.0f}kW "
              f"{row['soc_end']:<9.1f}% "
              f"{row['soc_change']:+11.1f}% "
              f"{status:<15}")
        
        total_baseline += row['optimal_baseline_kw']
    
    print("-"*100)
    print(f"{'合計基準値:':<45} {total_baseline:.0f} kW")
    print(f"{'平均基準値:':<45} {total_baseline/len(schedule_df):.0f} kW/block")
    print(f"{'初期SOC:':<45} {schedule_df.iloc[0]['soc_start']:.1f} %")
    print(f"{'最終SOC:':<45} {schedule_df.iloc[-1]['soc_end']:.1f} %")
    print(f"{'総SOC変化:':<45} {schedule_df.iloc[-1]['soc_end'] - schedule_df.iloc[0]['soc_start']:+.1f} %")
    print("="*100)


def main():
    """
    メイン関数：複数シナリオで最適スケジュールを生成
    """
    
    print("="*100)
    print("SOC最適化スケジュール生成ツール")
    print("="*100)
    print("\n【公式】")
    print("  SOC変化率 (%/時間) = 0.012804 × 基準値(kW) - 1.9515")
    print("  相関係数 (R²) = 0.9997")
    print("\n【制約条件】")
    print("  - SOC ≤ 90% (90%到達後は基準値0で自然放電)")
    print("  - 基準値設定: 3時間ブロック")
    print("  - 24時間スケジュール")
    
    # シナリオ1: 低SOC (5%)
    print("\n" + "="*100)
    print("シナリオ1: 初期SOC 5% (最大基準値)")
    print("="*100)
    schedule1 = generate_optimal_daily_schedule(initial_soc=5.0, start_hour=6, total_hours=24, block_hours=3)
    print_schedule_table(schedule1)
    
    fig1 = create_optimization_visualization(schedule1, initial_soc=5.0)
    fig1.write_html("optimal_schedule_soc5.html")
    print("\n✅ グラフを保存: optimal_schedule_soc5.html")
    
    # シナリオ2: 中SOC (30%)
    print("\n" + "="*100)
    print("シナリオ2: 初期SOC 30%")
    print("="*100)
    schedule2 = generate_optimal_daily_schedule(initial_soc=30.0, start_hour=6, total_hours=24, block_hours=3)
    print_schedule_table(schedule2)
    
    fig2 = create_optimization_visualization(schedule2, initial_soc=30.0)
    fig2.write_html("optimal_schedule_soc30.html")
    print("\n✅ グラフを保存: optimal_schedule_soc30.html")
    
    # シナリオ3: 高SOC (70%)
    print("\n" + "="*100)
    print("シナリオ3: 初期SOC 70%")
    print("="*100)
    schedule3 = generate_optimal_daily_schedule(initial_soc=70.0, start_hour=6, total_hours=24, block_hours=3)
    print_schedule_table(schedule3)
    
    fig3 = create_optimization_visualization(schedule3, initial_soc=70.0)
    fig3.write_html("optimal_schedule_soc70.html")
    print("\n✅ グラフを保存: optimal_schedule_soc70.html")
    
    # 全スケジュールをCSVに保存
    schedule1['scenario'] = 'SOC 5%'
    schedule2['scenario'] = 'SOC 30%'
    schedule3['scenario'] = 'SOC 70%'
    
    all_schedules = pd.concat([schedule1, schedule2, schedule3], ignore_index=True)
    all_schedules.to_csv('optimal_24h_schedules.csv', index=False, encoding='utf-8-sig')
    print("\n✅ 全スケジュールをCSVに保存: optimal_24h_schedules.csv")
    
    # サマリー比較
    print("\n" + "="*100)
    print("シナリオ比較サマリー")
    print("="*100)
    
    scenarios = [
        ('初期SOC 5%', schedule1),
        ('初期SOC 30%', schedule2),
        ('初期SOC 70%', schedule3)
    ]
    
    print(f"{'シナリオ':<15} {'初期SOC':<12} {'最終SOC':<12} {'合計基準値':<15} {'平均基準値':<15} {'90%到達時刻'}")
    print("-"*100)
    
    for name, schedule in scenarios:
        initial = schedule.iloc[0]['soc_start']
        final = schedule.iloc[-1]['soc_end']
        total = schedule['optimal_baseline_kw'].sum()
        avg = schedule['optimal_baseline_kw'].mean()
        
        # 90%到達時刻を探す
        reached_90 = schedule[schedule['soc_end'] >= 90]
        if len(reached_90) > 0:
            reach_hour = int(reached_90.iloc[0]['end_hour'])
            reach_time = f"{reach_hour:02d}:00"
        else:
            reach_time = "未到達"
        
        print(f"{name:<15} {initial:<11.1f}% {final:<11.1f}% {total:<14.0f}kW {avg:<14.0f}kW {reach_time}")
    
    print("="*100)
    
    # グラフを開く
    print("\n🎉 完了！ブラウザでグラフを開きます...")
    return fig1


if __name__ == "__main__":
    fig = main()
    fig.show()
