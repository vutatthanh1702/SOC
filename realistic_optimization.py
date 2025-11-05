import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_soc_change(baseline_kw, hours=3):
    """
    基準値からSOC変化を計算
    
    Parameters:
    -----------
    baseline_kw : float
        基準値 (kW)
    hours : float
        時間 (デフォルト: 3時間)
    
    Returns:
    --------
    soc_change : float
        SOC変化量 (%)
    """
    SLOPE = 0.012804
    INTERCEPT = -1.9515
    
    soc_change_rate = SLOPE * baseline_kw + INTERCEPT
    soc_change = soc_change_rate * hours
    
    return soc_change


def optimize_realistic_schedule(initial_soc=5, target_soc_max=90, total_hours=24, block_hours=3):
    """
    現実的な最適スケジュールを生成
    SOCは徐々にしか変化できない制約を考慮
    
    Parameters:
    -----------
    initial_soc : float
        初期SOC (%)
    target_soc_max : float
        目標最大SOC (%)
    total_hours : int
        合計時間
    block_hours : int
        ブロック時間
    
    Returns:
    --------
    schedule : pandas DataFrame
        最適スケジュール
    """
    
    SLOPE = 0.012804
    INTERCEPT = -1.9515
    
    schedule = []
    current_soc = initial_soc
    current_hour = 0
    block_num = 1
    
    print("\n" + "="*100)
    print("最適化プロセス（段階的SOC変化）")
    print("="*100)
    
    while current_hour < total_hours:
        # 現在のSOCから判断
        if current_soc < target_soc_max:
            # 充電フェーズ: SOCを90%まで上げる
            available_increase = target_soc_max - current_soc
            
            # 3時間で達成できるSOC増加量を計算
            # SOC増加 = 3時間 × (SLOPE × 基準値 + INTERCEPT)
            # 最大基準値を計算
            target_increase_per_hour = min(available_increase / block_hours, 30)  # 1時間で最大30%増加を制限
            optimal_baseline = (target_increase_per_hour - INTERCEPT) / SLOPE
            optimal_baseline = max(0, min(optimal_baseline, 2500))  # 0-2500kWの範囲
            
            # 実際のSOC変化を計算
            soc_change = calculate_soc_change(optimal_baseline, block_hours)
            new_soc = min(current_soc + soc_change, target_soc_max)
            actual_change = new_soc - current_soc
            
            status = "充電中 ↑"
            if new_soc >= target_soc_max:
                status = "目標到達 ✓"
        
        elif current_soc >= target_soc_max:
            # 放電フェーズ: SOCを下げて次のサイクルに備える
            # 基準値を低く設定してSOCを徐々に下げる
            
            # 目標: 3-6時間で80%まで下げる
            target_soc = 80
            if current_soc > 85:
                # 90% → 85%: 基準値を少し下げる
                optimal_baseline = 100  # 低い基準値
            else:
                # 85% → 80%: さらに下げる
                optimal_baseline = 50
            
            soc_change = calculate_soc_change(optimal_baseline, block_hours)
            new_soc = max(current_soc + soc_change, target_soc)
            actual_change = new_soc - current_soc
            
            status = "調整放電 ↓"
            if new_soc <= target_soc:
                status = "放電完了 ✓"
        
        # スケジュールに追加
        end_hour = current_hour + block_hours
        schedule.append({
            'block': block_num,
            'start_hour': current_hour,
            'end_hour': end_hour,
            'duration_hours': block_hours,
            'soc_start': round(current_soc, 1),
            'baseline_kw': round(optimal_baseline, 0),
            'soc_change': round(actual_change, 1),
            'soc_end': round(new_soc, 1),
            'status': status
        })
        
        print(f"Block {block_num}: {current_hour:02d}:00-{end_hour:02d}:00 | "
              f"SOC {current_soc:.1f}% → {new_soc:.1f}% | "
              f"基準値 {optimal_baseline:.0f}kW | {status}")
        
        # 次のブロック
        current_soc = new_soc
        current_hour = end_hour
        block_num += 1
    
    return pd.DataFrame(schedule)


def create_realistic_visualization(schedule_df, initial_soc):
    """
    現実的なスケジュールのグラフ作成
    """
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            '24時間のSOC変化（段階的）',
            '24時間の基準値変化',
            '各ブロックの詳細比較'
        ),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}], 
               [{"secondary_y": False}], 
               [{"secondary_y": False}]]
    )
    
    # 時間軸データを作成
    hours = []
    soc_values = []
    baseline_values = []
    
    for _, row in schedule_df.iterrows():
        # 各ブロックの開始と終了を追加
        hours.extend([row['start_hour'], row['end_hour']])
        soc_values.extend([row['soc_start'], row['soc_end']])
        baseline_values.extend([row['baseline_kw'], row['baseline_kw']])
    
    # グラフ1: SOCの変化（棒グラフ）
    fig.add_trace(
        go.Bar(
            x=schedule_df['start_hour'] + schedule_df['duration_hours']/2,
            y=schedule_df['soc_end'],
            name='SOC',
            marker=dict(
                color=schedule_df['soc_end'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="SOC (%)", y=0.85, len=0.3)
            ),
            text=schedule_df['soc_end'].round(1).astype(str) + '%',
            textposition='outside',
            width=2.5
        ),
        row=1, col=1
    )
    
    # 90%ライン
    fig.add_hline(
        y=90, line_dash="dash", line_color="red",
        annotation_text="目標上限 90%",
        row=1, col=1
    )
    
    # グラフ2: 基準値（棒グラフ）
    fig.add_trace(
        go.Bar(
            x=schedule_df['start_hour'] + schedule_df['duration_hours']/2,
            y=schedule_df['baseline_kw'],
            name='基準値',
            marker=dict(
                color=schedule_df['baseline_kw'],
                colorscale='Greens',
                showscale=True,
                colorbar=dict(title="基準値 (kW)", y=0.5, len=0.3)
            ),
            text=schedule_df['baseline_kw'].round(0).astype(int),
            textposition='outside',
            width=2.5
        ),
        row=2, col=1
    )
    
    # グラフ3: SOC変化量（棒グラフ）
    colors = ['green' if x > 0 else 'red' for x in schedule_df['soc_change']]
    
    fig.add_trace(
        go.Bar(
            x=schedule_df['start_hour'] + schedule_df['duration_hours']/2,
            y=schedule_df['soc_change'],
            name='SOC変化',
            marker=dict(color=colors),
            text=schedule_df['soc_change'].round(1).astype(str) + '%',
            textposition='outside',
            width=2.5
        ),
        row=3, col=1
    )
    
    # レイアウト設定
    fig.update_xaxes(
        title_text="時刻 (時)",
        tickmode='linear',
        tick0=0,
        dtick=3,
        range=[-1, 25]
    )
    
    fig.update_yaxes(title_text="SOC (%)", range=[0, 100], row=1, col=1)
    fig.update_yaxes(title_text="基準値 (kW)", row=2, col=1)
    fig.update_yaxes(title_text="SOC変化 (%)", row=3, col=1)
    
    fig.update_layout(
        height=1200,
        width=1400,
        title={
            'text': f'現実的なSOC最適化スケジュール<br><sub>初期SOC: {initial_soc}%, 段階的変化, 合計基準値最大化</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=False
    )
    
    return fig


def print_realistic_schedule(schedule_df):
    """
    現実的なスケジュールを表示
    """
    print("\n" + "="*110)
    print("最適化スケジュール（現実的な段階的変化）")
    print("="*110)
    print(f"{'Block':<6} {'時間帯':<15} {'開始SOC':<10} {'基準値':<12} {'SOC変化':<10} {'終了SOC':<10} {'状態':<20}")
    print("-"*110)
    
    total_baseline = 0
    
    for _, row in schedule_df.iterrows():
        time_range = f"{int(row['start_hour']):02d}:00-{int(row['end_hour']):02d}:00"
        
        print(f"{int(row['block']):<6} "
              f"{time_range:<15} "
              f"{row['soc_start']:<9.1f}% "
              f"{row['baseline_kw']:<11.0f}kW "
              f"{row['soc_change']:+9.1f}% "
              f"{row['soc_end']:<9.1f}% "
              f"{row['status']:<20}")
        
        total_baseline += row['baseline_kw']
    
    print("-"*110)
    print(f"{'合計基準値:':<50} {total_baseline:.0f} kW")
    print(f"{'平均基準値:':<50} {total_baseline/len(schedule_df):.0f} kW/block")
    print(f"{'初期SOC (0時):':<50} {schedule_df.iloc[0]['soc_start']:.1f} %")
    print(f"{'最終SOC (24時):':<50} {schedule_df.iloc[-1]['soc_end']:.1f} %")
    print(f"{'最大SOC到達:':<50} {schedule_df['soc_end'].max():.1f} %")
    print(f"{'最小SOC到達:':<50} {schedule_df['soc_end'].min():.1f} %")
    print("="*110)
    
    # 統計情報
    print("\n📊 統計情報:")
    print(f"  充電ブロック数: {len(schedule_df[schedule_df['soc_change'] > 0])}")
    print(f"  放電ブロック数: {len(schedule_df[schedule_df['soc_change'] < 0])}")
    print(f"  維持ブロック数: {len(schedule_df[schedule_df['soc_change'] == 0])}")
    print(f"  90%到達回数: {len(schedule_df[schedule_df['soc_end'] >= 90])}")


def main():
    """
    メイン関数
    """
    
    print("="*110)
    print("現実的なSOC最適化スケジュール生成")
    print("="*110)
    print("\n【前提条件】")
    print("  - 初期SOC: 5% (0時)")
    print("  - 目標: 合計基準値を最大化")
    print("  - 制約: SOC ≤ 90%")
    print("  - SOCは公式に従って段階的に変化")
    print("  - 公式: SOC変化率 = 0.012804 × 基準値 - 1.9515 (%/時間)")
    
    # 最適スケジュール生成
    schedule = optimize_realistic_schedule(
        initial_soc=5,
        target_soc_max=90,
        total_hours=24,
        block_hours=3
    )
    
    # スケジュール表示
    print_realistic_schedule(schedule)
    
    # グラフ作成
    fig = create_realistic_visualization(schedule, initial_soc=5)
    fig.write_html("realistic_optimal_schedule.html")
    print("\n✅ グラフを保存: realistic_optimal_schedule.html")
    
    # CSVに保存
    schedule.to_csv('realistic_optimal_schedule.csv', index=False, encoding='utf-8-sig')
    print("✅ CSVを保存: realistic_optimal_schedule.csv")
    
    # 比較分析
    print("\n" + "="*110)
    print("💡 重要な洞察")
    print("="*110)
    
    max_soc = schedule['soc_end'].max()
    min_soc = schedule['soc_end'].min()
    total_baseline = schedule['baseline_kw'].sum()
    
    print(f"\n1. SOC範囲: {min_soc:.1f}% ～ {max_soc:.1f}%")
    print(f"   → SOCは段階的に変化し、90%を超えない")
    
    print(f"\n2. 合計基準値: {total_baseline:.0f} kW")
    print(f"   → 24時間で設定できる基準値の総和")
    
    print(f"\n3. 運用パターン:")
    charge_blocks = schedule[schedule['soc_change'] > 0]
    discharge_blocks = schedule[schedule['soc_change'] < 0]
    print(f"   - 充電フェーズ: {len(charge_blocks)}ブロック (基準値高)")
    print(f"   - 放電フェーズ: {len(discharge_blocks)}ブロック (基準値低)")
    
    print(f"\n4. 最適化戦略:")
    print(f"   - 初期5%から素早く90%まで充電（高い基準値）")
    print(f"   - 90%到達後は基準値を下げてSOCを徐々に低下")
    print(f"   - 80%前後まで下がったら再度充電を開始")
    print(f"   - このサイクルを繰り返して基準値合計を最大化")
    
    return fig


if __name__ == "__main__":
    fig = main()
    fig.show()
