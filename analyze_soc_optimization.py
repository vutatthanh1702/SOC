import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def analyze_soc_baseline_relationship():
    """
    SOCと基準値の関係を分析して最適化公式を見つける
    目標: SOC < 90%を維持しながら基準値の合計を最大化
    """
    
    print("="*70)
    print("SOCと基準値の関係分析")
    print("="*70)
    
    # 統合データを読み込む
    df = pd.read_csv('kotohira_integrated_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 9月25日のデータを抽出
    target_date = pd.Timestamp('2025-09-25')
    df_sep25 = df[(df['timestamp'] >= target_date) & 
                  (df['timestamp'] < target_date + timedelta(days=1))].copy()
    
    # 9月26日のデータも抽出（比較用）
    df_sep26 = df[(df['timestamp'] >= target_date + timedelta(days=1)) & 
                  (df['timestamp'] < target_date + timedelta(days=2))].copy()
    
    print(f"\n📅 9月25日のデータ: {len(df_sep25)} レコード")
    print(f"📅 9月26日のデータ: {len(df_sep26)} レコード")
    
    # SOCの変化を分析
    print("\n" + "="*70)
    print("9月25日 SOC変化分析")
    print("="*70)
    
    # SOCが存在する時間帯を取得
    df_sep25_with_soc = df_sep25[df_sep25['battery_soc_percent'].notna()].copy()
    
    if len(df_sep25_with_soc) > 0:
        print(f"\nSOC範囲: {df_sep25_with_soc['battery_soc_percent'].min():.1f}% → {df_sep25_with_soc['battery_soc_percent'].max():.1f}%")
        
        # 基準値が設定されている期間を特定
        df_with_baseline = df_sep25[df_sep25['demand_plan_kw_baseline'].notna()].copy()
        
        if len(df_with_baseline) > 0:
            print(f"\n基準値が設定されている時間帯:")
            
            # 基準値ごとにグループ化
            baseline_groups = df_with_baseline.groupby('demand_plan_kw_baseline').agg({
                'timestamp': ['min', 'max', 'count']
            })
            
            for baseline_value in baseline_groups.index:
                group = df_with_baseline[df_with_baseline['demand_plan_kw_baseline'] == baseline_value]
                start_time = group['timestamp'].min()
                end_time = group['timestamp'].max()
                
                # この期間のSOC変化を計算
                period_data = df_sep25_with_soc[
                    (df_sep25_with_soc['timestamp'] >= start_time) & 
                    (df_sep25_with_soc['timestamp'] <= end_time)
                ]
                
                if len(period_data) > 0:
                    soc_start = period_data['battery_soc_percent'].iloc[0]
                    soc_end = period_data['battery_soc_percent'].iloc[-1]
                    soc_change = soc_end - soc_start
                    duration_hours = (end_time - start_time).total_seconds() / 3600
                    
                    print(f"\n  基準値: {baseline_value:.0f} kW")
                    print(f"    期間: {start_time.strftime('%H:%M')} ～ {end_time.strftime('%H:%M')} ({duration_hours:.1f}時間)")
                    print(f"    SOC変化: {soc_start:.1f}% → {soc_end:.1f}% (変化量: {soc_change:+.1f}%)")
                    print(f"    SOC変化率: {soc_change/duration_hours:+.2f}%/時間")
    
    # 9月26日も同様に分析
    print("\n" + "="*70)
    print("9月26日 SOC変化分析")
    print("="*70)
    
    df_sep26_with_soc = df_sep26[df_sep26['battery_soc_percent'].notna()].copy()
    
    if len(df_sep26_with_soc) > 0:
        print(f"\nSOC範囲: {df_sep26_with_soc['battery_soc_percent'].min():.1f}% → {df_sep26_with_soc['battery_soc_percent'].max():.1f}%")
        
        df_with_baseline_26 = df_sep26[df_sep26['demand_plan_kw_baseline'].notna()].copy()
        
        if len(df_with_baseline_26) > 0:
            print(f"\n基準値が設定されている時間帯:")
            
            for baseline_value in df_with_baseline_26['demand_plan_kw_baseline'].unique():
                group = df_with_baseline_26[df_with_baseline_26['demand_plan_kw_baseline'] == baseline_value]
                start_time = group['timestamp'].min()
                end_time = group['timestamp'].max()
                
                period_data = df_sep26_with_soc[
                    (df_sep26_with_soc['timestamp'] >= start_time) & 
                    (df_sep26_with_soc['timestamp'] <= end_time)
                ]
                
                if len(period_data) > 0:
                    soc_start = period_data['battery_soc_percent'].iloc[0]
                    soc_end = period_data['battery_soc_percent'].iloc[-1]
                    soc_change = soc_end - soc_start
                    duration_hours = (end_time - start_time).total_seconds() / 3600
                    
                    print(f"\n  基準値: {baseline_value:.0f} kW")
                    print(f"    期間: {start_time.strftime('%H:%M')} ～ {end_time.strftime('%H:%M')} ({duration_hours:.1f}時間)")
                    print(f"    SOC変化: {soc_start:.1f}% → {soc_end:.1f}% (変化量: {soc_change:+.1f}%)")
                    print(f"    SOC変化率: {soc_change/duration_hours:+.2f}%/時間")
    
    # 最適化モデルを作成
    print("\n" + "="*70)
    print("最適化モデル")
    print("="*70)
    
    # 3時間ブロックでの分析（基準値は3時間ごとに設定）
    print("\n📊 3時間ブロックの分析:")
    
    # 全データから基準値とSOC変化の関係を抽出
    all_data = []
    
    for date in [target_date, target_date + timedelta(days=1)]:
        daily_data = df[(df['timestamp'] >= date) & 
                       (df['timestamp'] < date + timedelta(days=1))].copy()
        
        daily_soc = daily_data[daily_data['battery_soc_percent'].notna()].copy()
        daily_baseline = daily_data[daily_data['demand_plan_kw_baseline'].notna()].copy()
        
        if len(daily_baseline) > 0:
            for baseline_value in daily_baseline['demand_plan_kw_baseline'].unique():
                group = daily_baseline[daily_baseline['demand_plan_kw_baseline'] == baseline_value]
                start_time = group['timestamp'].min()
                end_time = group['timestamp'].max()
                
                period_soc = daily_soc[
                    (daily_soc['timestamp'] >= start_time) & 
                    (daily_soc['timestamp'] <= end_time)
                ]
                
                if len(period_soc) > 0:
                    soc_start = period_soc['battery_soc_percent'].iloc[0]
                    soc_end = period_soc['battery_soc_percent'].iloc[-1]
                    duration_hours = (end_time - start_time).total_seconds() / 3600
                    
                    all_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'baseline_kw': baseline_value,
                        'duration_hours': duration_hours,
                        'soc_start': soc_start,
                        'soc_end': soc_end,
                        'soc_change': soc_end - soc_start,
                        'soc_change_rate': (soc_end - soc_start) / duration_hours if duration_hours > 0 else 0
                    })
    
    analysis_df = pd.DataFrame(all_data)
    
    if len(analysis_df) > 0:
        print("\n収集されたデータポイント:")
        print(analysis_df.to_string())
        
        # 線形回帰でSOC変化率と基準値の関係を求める
        print("\n📈 SOC変化率と基準値の関係:")
        
        # 基準値が0でないデータで回帰分析
        non_zero_data = analysis_df[analysis_df['baseline_kw'] > 0]
        
        if len(non_zero_data) > 0:
            # 簡単な線形関係を求める
            from scipy import stats
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                non_zero_data['baseline_kw'], 
                non_zero_data['soc_change_rate']
            )
            
            print(f"\n  線形回帰結果:")
            print(f"    SOC変化率 = {slope:.6f} × 基準値 + {intercept:.4f}")
            print(f"    相関係数 (R²): {r_value**2:.4f}")
            print(f"    P値: {p_value:.4f}")
            
            # 最適化公式を提案
            print("\n" + "="*70)
            print("💡 最適化公式の提案")
            print("="*70)
            
            print(f"\n【前提条件】")
            print(f"  - SOCは90%以下を維持")
            print(f"  - 基準値は3時間ブロックで設定")
            print(f"  - SOC変化率 ≈ {slope:.6f} × 基準値 + {intercept:.4f} (%/時間)")
            
            # 3時間で90%に達しないための最大基準値を計算
            print(f"\n【最適化戦略】")
            
            # 現在のSOCから計算
            for current_soc in [5, 10, 20, 30, 40, 50, 60, 70, 80]:
                available_soc_increase = 90 - current_soc
                max_rate_per_hour = available_soc_increase / 3  # 3時間ブロック
                
                # 基準値を計算
                if slope > 0:
                    max_baseline = (max_rate_per_hour - intercept) / slope
                    max_baseline = max(0, max_baseline)  # 負の値を防ぐ
                    
                    print(f"\n  現在SOC {current_soc}%の場合:")
                    print(f"    最大基準値: {max_baseline:.0f} kW (3時間ブロック)")
                    print(f"    予想SOC増加: {max_rate_per_hour * 3:.1f}% (3時間後)")
                    print(f"    到達SOC: {current_soc + max_rate_per_hour * 3:.1f}%")
    
    # グラフを作成
    create_optimization_visualization(df_sep25, df_sep26, analysis_df)
    
    return analysis_df


def create_optimization_visualization(df_sep25, df_sep26, analysis_df):
    """
    最適化分析の可視化
    """
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('9月25-26日のSOCと基準値の関係', '基準値とSOC変化率の関係'),
        vertical_spacing=0.15
    )
    
    # 9月25日
    df_25_soc = df_sep25[df_sep25['battery_soc_percent'].notna()]
    df_25_baseline = df_sep25[df_sep25['demand_plan_kw_baseline'].notna()]
    
    fig.add_trace(
        go.Scatter(
            x=df_25_soc['timestamp'],
            y=df_25_soc['battery_soc_percent'],
            mode='markers',
            name='SOC (9/25)',
            marker=dict(color='blue', size=3),
        ),
        row=1, col=1
    )
    
    if len(df_25_baseline) > 0:
        fig.add_trace(
            go.Scatter(
                x=df_25_baseline['timestamp'],
                y=df_25_baseline['demand_plan_kw_baseline'],
                mode='lines',
                name='基準値 (9/25)',
                line=dict(color='green', width=2, dash='dash'),
                yaxis='y2'
            ),
            row=1, col=1
        )
    
    # 9月26日
    df_26_soc = df_sep26[df_sep26['battery_soc_percent'].notna()]
    df_26_baseline = df_sep26[df_sep26['demand_plan_kw_baseline'].notna()]
    
    fig.add_trace(
        go.Scatter(
            x=df_26_soc['timestamp'],
            y=df_26_soc['battery_soc_percent'],
            mode='markers',
            name='SOC (9/26)',
            marker=dict(color='navy', size=3),
        ),
        row=1, col=1
    )
    
    if len(df_26_baseline) > 0:
        fig.add_trace(
            go.Scatter(
                x=df_26_baseline['timestamp'],
                y=df_26_baseline['demand_plan_kw_baseline'],
                mode='lines',
                name='基準値 (9/26)',
                line=dict(color='darkgreen', width=2, dash='dash'),
                yaxis='y2'
            ),
            row=1, col=1
        )
    
    # 散布図：基準値 vs SOC変化率
    if len(analysis_df) > 0:
        fig.add_trace(
            go.Scatter(
                x=analysis_df['baseline_kw'],
                y=analysis_df['soc_change_rate'],
                mode='markers',
                name='実測値',
                marker=dict(color='red', size=10),
                text=[f"{row['date']}<br>SOC: {row['soc_start']:.1f}%→{row['soc_end']:.1f}%" 
                      for _, row in analysis_df.iterrows()],
                hovertemplate='基準値: %{x} kW<br>SOC変化率: %{y:.2f} %/時間<br>%{text}'
            ),
            row=2, col=1
        )
    
    # レイアウト
    fig.update_xaxes(title_text="時間", row=1, col=1)
    fig.update_xaxes(title_text="基準値 (kW)", row=2, col=1)
    fig.update_yaxes(title_text="SOC (%)", row=1, col=1)
    fig.update_yaxes(title_text="SOC変化率 (%/時間)", row=2, col=1)
    
    fig.update_layout(
        height=900,
        width=1400,
        title_text="SOCと基準値の最適化分析",
        showlegend=True
    )
    
    fig.write_html("soc_optimization_analysis.html")
    print("\n✅ 分析グラフを作成: soc_optimization_analysis.html")


if __name__ == "__main__":
    analysis_result = analyze_soc_baseline_relationship()
