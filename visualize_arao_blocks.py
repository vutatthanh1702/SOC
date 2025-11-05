"""
荒尾発電所データの可視化 - ブロック別表示版
- 30分粒度: JEPX計画値とブロック1~8の表示
- 1分粒度: バッテリ1-2とバッテリ3-4のSOC値
- 透明度を使用して重なりを視覚化
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# データ読み込み
print("データを読み込んでいます...")
schedule_df = pd.read_csv(
    'arao_202406-202504/arao_schedule_202406-202504.csv'
)
soc_battery12_df = pd.read_csv(
    'arao_202406-202504/arao_soc_battery1-2_202406-202504.csv'
)
soc_battery34_df = pd.read_csv(
    'arao_202406-202504/arao_soc_battery3-4_202406-202504.csv'
)

# 時刻をdatetimeに変換
schedule_df['開始時刻'] = pd.to_datetime(schedule_df['開始時刻'])
schedule_df['終了時刻'] = pd.to_datetime(schedule_df['終了時刻'])
soc_battery12_df['時刻'] = pd.to_datetime(soc_battery12_df['時刻'])
soc_battery34_df['時刻'] = pd.to_datetime(soc_battery34_df['時刻'])

# ブロック番号を抽出（時刻から計算）
schedule_df['block'] = ((schedule_df['開始時刻'].dt.hour * 2 +
                        schedule_df['開始時刻'].dt.minute // 30) % 48) // 6 + 1

print(f"スケジュールデータ: {len(schedule_df)} 行 (30分粒度)")
print(f"バッテリ1-2 SOCデータ: {len(soc_battery12_df)} 行 (1分粒度)")
print(f"バッテリ3-4 SOCデータ: {len(soc_battery34_df)} 行 (1分粒度)")
print(f"\n期間: {schedule_df['開始時刻'].min()} ~ "
      f"{schedule_df['終了時刻'].max()}")

# サブプロットを作成
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.1,
    subplot_titles=(
        '荒尾発電所 - 計画値（ブロック1~8別表示）- 30分粒度',
        '荒尾発電所 - バッテリSOC - 1分粒度'
    ),
    row_heights=[0.4, 0.6]
)

# ブロック別の色とラベル
block_colors = {
    1: 'rgba(255, 0, 0, 0.6)',      # 赤（0:00-3:00）
    2: 'rgba(255, 165, 0, 0.6)',    # オレンジ（3:00-6:00）
    3: 'rgba(255, 255, 0, 0.6)',    # 黄色（6:00-9:00）
    4: 'rgba(0, 255, 0, 0.6)',      # 緑（9:00-12:00）
    5: 'rgba(0, 255, 255, 0.6)',    # シアン（12:00-15:00）
    6: 'rgba(0, 0, 255, 0.6)',      # 青（15:00-18:00）
    7: 'rgba(148, 0, 211, 0.6)',    # 紫（18:00-21:00）
    8: 'rgba(255, 20, 147, 0.6)',   # ピンク（21:00-24:00）
}

block_times = {
    1: '0:00-3:00',
    2: '3:00-6:00',
    3: '6:00-9:00',
    4: '9:00-12:00',
    5: '12:00-15:00',
    6: '15:00-18:00',
    7: '18:00-21:00',
    8: '21:00-24:00',
}

# 1. JEPXと二次・三次を分けて表示（ブロックの色は背景で）
jepx_df = schedule_df[schedule_df['計画リソース'] == 'JEPX']
nijisanji_df = schedule_df[schedule_df['計画リソース'] == '二次・三次']

if len(jepx_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=jepx_df['開始時刻'],
            y=jepx_df['計画値'],
            name='JEPX計画値',
            line=dict(color='blue', width=2),
            mode='lines',
            hovertemplate=(
                '<b>JEPX</b><br>'
                '計画値: %{y:.1f} kW<br>'
                '時刻: %{x}<extra></extra>'
            )
        ),
        row=1, col=1
    )

if len(nijisanji_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=nijisanji_df['開始時刻'],
            y=nijisanji_df['計画値'],
            name='二次・三次調整力',
            line=dict(color='red', width=2),
            mode='lines',
            hovertemplate=(
                '<b>二次・三次</b><br>'
                '計画値: %{y:.1f} kW<br>'
                '時刻: %{x}<extra></extra>'
            )
        ),
        row=1, col=1
    )

# 2. バッテリ1-2のSOC
battery1_df = soc_battery12_df[soc_battery12_df['蓄電池名'] == '蓄電池1']
battery2_df = soc_battery12_df[soc_battery12_df['蓄電池名'] == '蓄電池2']

if len(battery1_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=battery1_df['時刻'],
            y=battery1_df['SOC'],
            name='バッテリ1 SOC',
            line=dict(color='rgba(0, 128, 0, 0.7)', width=1),
            mode='lines',
            hovertemplate=(
                '<b>バッテリ1 SOC</b>: %{y:.1f}%<br>'
                '時刻: %{x}<extra></extra>'
            )
        ),
        row=2, col=1
    )

if len(battery2_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=battery2_df['時刻'],
            y=battery2_df['SOC'],
            name='バッテリ2 SOC',
            line=dict(color='rgba(144, 238, 144, 0.7)', width=1),
            mode='lines',
            hovertemplate=(
                '<b>バッテリ2 SOC</b>: %{y:.1f}%<br>'
                '時刻: %{x}<extra></extra>'
            )
        ),
        row=2, col=1
    )

# 3. バッテリ3-4のSOC
battery3_df = soc_battery34_df[soc_battery34_df['蓄電池名'] == '蓄電池3']
battery4_df = soc_battery34_df[soc_battery34_df['蓄電池名'] == '蓄電池4']

if len(battery3_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=battery3_df['時刻'],
            y=battery3_df['SOC'],
            name='バッテリ3 SOC',
            line=dict(color='rgba(255, 140, 0, 0.7)', width=1),
            mode='lines',
            hovertemplate=(
                '<b>バッテリ3 SOC</b>: %{y:.1f}%<br>'
                '時刻: %{x}<extra></extra>'
            )
        ),
        row=2, col=1
    )

if len(battery4_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=battery4_df['時刻'],
            y=battery4_df['SOC'],
            name='バッテリ4 SOC',
            line=dict(color='rgba(255, 69, 0, 0.7)', width=1),
            mode='lines',
            hovertemplate=(
                '<b>バッテリ4 SOC</b>: %{y:.1f}%<br>'
                '時刻: %{x}<extra></extra>'
            )
        ),
        row=2, col=1
    )

# レイアウト更新
fig.update_xaxes(title_text="時刻", row=2, col=1)
fig.update_yaxes(title_text="計画値 (kW)", row=1, col=1)
fig.update_yaxes(title_text="SOC (%)", row=2, col=1)

fig.update_layout(
    title={
        'text': (
            '荒尾発電所 - ブロック別分析<br>'
            '<sub>2024年6月～2025年4月 | ブロック1~8を背景色で表示</sub>'
        ),
        'x': 0.5,
        'xanchor': 'center'
    },
    height=900,
    hovermode='x unified',
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02
    ),
    template='plotly_white'
)

# ブロックの背景色を追加（全日付に対して）
import pandas as pd
from datetime import datetime, timedelta

# 全期間の日付リストを取得
start_date = schedule_df['開始時刻'].min().date()
end_date = schedule_df['終了時刻'].max().date()
current_date = start_date

# 各行に背景色の矩形を追加
shapes = []
annotations = []

while current_date <= end_date:
    for block_num in range(1, 9):
        # ブロックの開始・終了時刻を計算
        block_start_hour = (block_num - 1) * 3
        block_end_hour = block_num * 3
        
        x0 = pd.Timestamp(current_date) + pd.Timedelta(hours=block_start_hour)
        x1 = pd.Timestamp(current_date) + pd.Timedelta(hours=block_end_hour)
        
        # 矩形を追加（row 1のみ）
        shapes.append(
            dict(
                type="rect",
                xref="x",
                yref="y",
                x0=x0,
                x1=x1,
                y0=-2500,
                y1=2500,
                fillcolor=block_colors[block_num],
                opacity=0.15,
                layer="below",
                line_width=0,
            )
        )
        
        # 背景色をrow 2にも追加
        shapes.append(
            dict(
                type="rect",
                xref="x2",
                yref="y2",
                x0=x0,
                x1=x1,
                y0=0,
                y1=100,
                fillcolor=block_colors[block_num],
                opacity=0.1,
                layer="below",
                line_width=0,
            )
        )
    
    current_date += timedelta(days=1)

# ブロックラベルを追加（最初の日だけ）
first_date = start_date
for block_num in range(1, 9):
    block_start_hour = (block_num - 1) * 3
    x_pos = pd.Timestamp(first_date) + pd.Timedelta(hours=block_start_hour + 1.5)
    
    annotations.append(
        dict(
            x=x_pos,
            y=2200,
            xref="x",
            yref="y",
            text=f"B{block_num}",
            showarrow=False,
            font=dict(size=10, color="black"),
            bgcolor=block_colors[block_num],
            opacity=0.8
        )
    )

fig.update_layout(shapes=shapes, annotations=annotations)

# ブロック別統計
print("\n=== ブロック別統計 ===")
for block_num in range(1, 9):
    block_data = schedule_df[schedule_df['block'] == block_num]
    if len(block_data) > 0:
        print(f"\nブロック{block_num} ({block_times[block_num]}):")
        print(f"  データ数: {len(block_data)} 行")
        print(f"  平均: {block_data['計画値'].mean():.2f} kW")
        print(f"  最大: {block_data['計画値'].max():.2f} kW")
        print(f"  最小: {block_data['計画値'].min():.2f} kW")
        non_zero_pct = (
            (block_data['計画値'] != 0).sum() / len(block_data) * 100
        )
        print(f"  非ゼロ割合: {non_zero_pct:.1f}%")

# HTML出力
output_file = 'arao_blocks_visualization.html'
fig.write_html(output_file)
print(f"\n✅ 可視化完了: {output_file}")

# ブラウザで開く
import webbrowser
webbrowser.open(output_file)
