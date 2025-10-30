import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def create_three_metrics_graph():
    """
    3つのメトリクスを1つのグラフに表示:
    1. 需要計画kW (基準値) - kotohira_kijyunchi
    2. SOC (%) - kotohira_soc
    3. 実績値kW - kotohira_jiseki
    """
    
    print("データを読み込んでいます...")
    
    # 1. SOCデータの読み込み
    soc_df = pd.read_csv('kotohira_soc_20250801~now (1).csv')
    soc_df['time'] = pd.to_datetime(soc_df['time'])
    # SOCの異常値をフィルタリング (100%以下のみ)
    soc_df = soc_df[soc_df['soc'] <= 100]
    
    # 2. 実績値kWデータの読み込み
    jiseki_df = pd.read_csv('kotohira_jiseki_20250801~now (1).csv')
    jiseki_df['time'] = pd.to_datetime(jiseki_df['time'])
    
    # 3. 基準値(需要計画kW)データの読み込み
    kijyunchi_df = pd.read_csv('kotohira_kijyunchi_20250801~now (1).csv')
    kijyunchi_df['start_time'] = pd.to_datetime(kijyunchi_df['start_time'])
    kijyunchi_df['end_time'] = pd.to_datetime(kijyunchi_df['end_time'])
    
    # 需要計画kWのデータのみを抽出
    kijyunchi_demand = kijyunchi_df[pd.notna(kijyunchi_df['需要計画kW']) & (kijyunchi_df['需要計画kW'] != '')]
    
    print(f"SOCデータ: {len(soc_df):,} レコード")
    print(f"実績値kWデータ: {len(jiseki_df):,} レコード")
    print(f"需要計画kW(基準値)データ: {len(kijyunchi_demand):,} レコード")
    
    # グラフの作成 (2つのy軸を使用)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 1. SOC (%) - 左側のy軸
    fig.add_trace(
        go.Scatter(
            x=soc_df['time'],
            y=soc_df['soc'],
            mode='markers',  # 線ではなくマーカーで表示
            name='SOC (%)',
            marker=dict(color='blue', size=3),
            yaxis='y'
        ),
        secondary_y=False
    )
    
    # 2. 実績値kW - 右側のy軸
    fig.add_trace(
        go.Scatter(
            x=jiseki_df['time'],
            y=jiseki_df['実績値kW'],
            mode='lines',
            name='実績値kW',
            line=dict(color='rgba(255, 100, 100, 0.5)', width=1),  # 薄い赤色、細い線
            yaxis='y2'
        ),
        secondary_y=True
    )
    
    # 3. 需要計画kW (基準値) - 右側のy軸、階段状に表示
    kijyun_times = []
    kijyun_values = []
    
    for _, row in kijyunchi_demand.iterrows():
        try:
            value = float(row['需要計画kW'])
            # 階段状のグラフを作成するため、start_timeとend_timeの両方に同じ値を設定
            kijyun_times.extend([row['start_time'], row['end_time'], row['end_time']])
            kijyun_values.extend([value, value, None])  # Noneで線を区切る
        except:
            continue
    
    fig.add_trace(
        go.Scatter(
            x=kijyun_times,
            y=kijyun_values,
            mode='lines',
            name='需要計画kW (基準値)',
            line=dict(color='green', width=3, dash='dash'),
            connectgaps=False,
            yaxis='y2'
        ),
        secondary_y=True
    )
    
    # レイアウトの設定
    fig.update_layout(
        title={
            'text': '琴平エネルギーデータ統合グラフ<br><sub>SOC (%) / 実績値kW / 需要計画kW (基準値)</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        xaxis=dict(
            title='時間',
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title=dict(text='SOC (%)', font=dict(color='blue', size=16)),
            tickfont=dict(color='blue', size=12),
            showgrid=True,
            gridcolor='lightblue',
            range=[0, 100]
        ),
        yaxis2=dict(
            title=dict(text='電力 (kW)', font=dict(color='darkred', size=16)),
            tickfont=dict(color='darkred', size=12),
            showgrid=False,
            overlaying='y',
            side='right'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=14)
        ),
        height=700,
        width=1400,
        hovermode='x unified',
        plot_bgcolor='white'
    )
    
    # グラフを表示して保存
    fig.show()
    fig.write_html("kotohira_3metrics_integrated.html")
    print("\n✅ 統合グラフを作成しました: kotohira_3metrics_integrated.html")
    
    # 統計情報の表示
    print("\n" + "="*70)
    print("📊 データ統計サマリー")
    print("="*70)
    
    print(f"\n1️⃣  SOC (蓄電池残量):")
    print(f"   期間: {soc_df['time'].min()} ～ {soc_df['time'].max()}")
    print(f"   範囲: {soc_df['soc'].min():.1f}% ～ {soc_df['soc'].max():.1f}%")
    print(f"   平均: {soc_df['soc'].mean():.1f}%")
    print(f"   レコード数: {len(soc_df):,}")
    
    print(f"\n2️⃣  実績値kW (実際の電力):")
    print(f"   期間: {jiseki_df['time'].min()} ～ {jiseki_df['time'].max()}")
    print(f"   範囲: {jiseki_df['実績値kW'].min():,.1f}kW ～ {jiseki_df['実績値kW'].max():,.1f}kW")
    print(f"   平均: {jiseki_df['実績値kW'].mean():.1f}kW")
    print(f"   レコード数: {len(jiseki_df):,}")
    
    print(f"\n3️⃣  需要計画kW (基準値):")
    print(f"   期間: {kijyunchi_demand['start_time'].min()} ～ {kijyunchi_demand['end_time'].max()}")
    if len(kijyun_values) > 0:
        kijyun_values_clean = [v for v in kijyun_values if v is not None]
        if kijyun_values_clean:
            print(f"   範囲: {min(kijyun_values_clean):,.1f}kW ～ {max(kijyun_values_clean):,.1f}kW")
            print(f"   平均: {sum(kijyun_values_clean)/len(kijyun_values_clean):.1f}kW")
    print(f"   レコード数: {len(kijyunchi_demand):,}")
    
    print("\n" + "="*70)
    
    return fig


def create_focused_three_metrics_graph():
    """
    3つのメトリクスを1つのグラフに表示 (7日間の集中ビュー)
    """
    
    print("\nデータを読み込んでいます (7日間表示)...")
    
    # データの読み込み
    soc_df = pd.read_csv('kotohira_soc_20250801~now (1).csv')
    soc_df['time'] = pd.to_datetime(soc_df['time'])
    soc_df = soc_df[soc_df['soc'] <= 100]
    
    jiseki_df = pd.read_csv('kotohira_jiseki_20250801~now (1).csv')
    jiseki_df['time'] = pd.to_datetime(jiseki_df['time'])
    
    kijyunchi_df = pd.read_csv('kotohira_kijyunchi_20250801~now (1).csv')
    kijyunchi_df['start_time'] = pd.to_datetime(kijyunchi_df['start_time'])
    kijyunchi_df['end_time'] = pd.to_datetime(kijyunchi_df['end_time'])
    kijyunchi_demand = kijyunchi_df[pd.notna(kijyunchi_df['需要計画kW']) & (kijyunchi_df['需要計画kW'] != '')]
    
    # 7日間のデータにフィルタリング
    start_date = pd.Timestamp('2025-08-01', tz='Asia/Tokyo')
    end_date = start_date + timedelta(days=7)
    
    soc_filtered = soc_df[(soc_df['time'] >= start_date) & (soc_df['time'] <= end_date)]
    jiseki_filtered = jiseki_df[(jiseki_df['time'] >= start_date) & (jiseki_df['time'] <= end_date)]
    kijyun_filtered = kijyunchi_demand[(kijyunchi_demand['start_time'] >= start_date) & 
                                        (kijyunchi_demand['end_time'] <= end_date)]
    
    # グラフの作成
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # SOC
    fig.add_trace(
        go.Scatter(
            x=soc_filtered['time'],
            y=soc_filtered['soc'],
            mode='lines',
            name='SOC (%)',
            line=dict(color='blue', width=2),
        ),
        secondary_y=False
    )
    
    # 実績値kW
    fig.add_trace(
        go.Scatter(
            x=jiseki_filtered['time'],
            y=jiseki_filtered['実績値kW'],
            mode='lines',
            name='実績値kW',
            line=dict(color='red', width=2),
        ),
        secondary_y=True
    )
    
    # 需要計画kW (基準値)
    kijyun_times = []
    kijyun_values = []
    for _, row in kijyun_filtered.iterrows():
        try:
            value = float(row['需要計画kW'])
            kijyun_times.extend([row['start_time'], row['end_time'], row['end_time']])
            kijyun_values.extend([value, value, None])
        except:
            continue
    
    fig.add_trace(
        go.Scatter(
            x=kijyun_times,
            y=kijyun_values,
            mode='lines',
            name='需要計画kW (基準値)',
            line=dict(color='green', width=3, dash='dash'),
            connectgaps=False,
        ),
        secondary_y=True
    )
    
    # レイアウト
    fig.update_layout(
        title={
            'text': '琴平エネルギーデータ (7日間表示)<br><sub>2025年8月1日～8月7日</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        xaxis=dict(title='時間', showgrid=True),
        yaxis=dict(
            title=dict(text='SOC (%)', font=dict(color='blue', size=16)),
            tickfont=dict(color='blue'),
            range=[0, 100]
        ),
        yaxis2=dict(
            title=dict(text='電力 (kW)', font=dict(color='darkred', size=16)),
            tickfont=dict(color='darkred'),
            overlaying='y',
            side='right'
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=700,
        width=1400,
        hovermode='x unified',
        plot_bgcolor='white'
    )
    
    fig.show()
    fig.write_html("kotohira_3metrics_7days.html")
    print("✅ 7日間グラフを作成しました: kotohira_3metrics_7days.html")
    
    return fig


if __name__ == "__main__":
    print("="*70)
    print("琴平エネルギーデータ統合可視化")
    print("="*70)
    
    # 全期間のグラフを作成
    create_three_metrics_graph()
    
    # 7日間の集中ビューを作成
    print("\n" + "-"*70)
    create_focused_three_metrics_graph()
    
    print("\n" + "="*70)
    print("🎉 可視化が完了しました!")
    print("="*70)
    print("\n作成されたファイル:")
    print("  1. kotohira_3metrics_integrated.html (全期間)")
    print("  2. kotohira_3metrics_7days.html (7日間)")
    print("\nこれらのHTMLファイルをブラウザで開いてください。")
