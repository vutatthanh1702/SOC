"""
荒尾発電所データの可視化
- 30分粒度: JEPX計画値（基準値）
- 1分粒度: バッテリ1-2とバッテリ3-4のSOC値
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# データ読み込み
print("データを読み込んでいます...")
schedule_df = pd.read_csv('arao_202406-202504/arao_schedule_202406-202504.csv')
soc_battery12_df = pd.read_csv('arao_202406-202504/arao_soc_battery1-2_202406-202504.csv')
soc_battery34_df = pd.read_csv('arao_202406-202504/arao_soc_battery3-4_202406-202504.csv')

# 時刻をdatetimeに変換
schedule_df['開始時刻'] = pd.to_datetime(schedule_df['開始時刻'])
schedule_df['終了時刻'] = pd.to_datetime(schedule_df['終了時刻'])
soc_battery12_df['時刻'] = pd.to_datetime(soc_battery12_df['時刻'])
soc_battery34_df['時刻'] = pd.to_datetime(soc_battery34_df['時刻'])

print(f"スケジュールデータ: {len(schedule_df)} 行 (30分粒度)")
print(f"バッテリ1-2 SOCデータ: {len(soc_battery12_df)} 行 (1分粒度)")
print(f"バッテリ3-4 SOCデータ: {len(soc_battery34_df)} 行 (1分粒度)")
print(f"\n期間: {schedule_df['開始時刻'].min()} ~ {schedule_df['終了時刻'].max()}")

# サブプロットを作成（2つのY軸）
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.1,
    subplot_titles=(
        '荒尾発電所 - 計画値（JEPX + 二次・三次調整力）- 30分粒度',
        '荒尾発電所 - バッテリSOC - 1分粒度'
    ),
    row_heights=[0.4, 0.6]
)

# 1. 計画値を計画リソース別に表示 - 30分粒度
# JEPXデータ
jepx_df = schedule_df[schedule_df['計画リソース'] == 'JEPX']
if len(jepx_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=jepx_df['開始時刻'],
            y=jepx_df['計画値'],
            name='JEPX計画値',
            line=dict(color='blue', width=2),
            mode='lines',
            hovertemplate='<b>JEPX計画値</b>: %{y:.1f} kW<br>時刻: %{x}<extra></extra>'
        ),
        row=1, col=1
    )

# 二次・三次調整力データ
nijisanji_df = schedule_df[schedule_df['計画リソース'] == '二次・三次']
if len(nijisanji_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=nijisanji_df['開始時刻'],
            y=nijisanji_df['計画値'],
            name='二次・三次調整力計画値',
            line=dict(color='red', width=2),
            mode='lines',
            hovertemplate='<b>二次・三次計画値</b>: %{y:.1f} kW<br>時刻: %{x}<extra></extra>'
        ),
        row=1, col=1
    )

# 2. バッテリ1-2のSOC - 1分粒度
# 蓄電池1と蓄電池2を分離
battery1_df = soc_battery12_df[soc_battery12_df['蓄電池名'] == '蓄電池1']
battery2_df = soc_battery12_df[soc_battery12_df['蓄電池名'] == '蓄電池2']

if len(battery1_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=battery1_df['時刻'],
            y=battery1_df['SOC'],
            name='バッテリ1 SOC',
            line=dict(color='green', width=1),
            mode='lines',
            hovertemplate='<b>バッテリ1 SOC</b>: %{y:.1f}%<br>時刻: %{x}<extra></extra>'
        ),
        row=2, col=1
    )

if len(battery2_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=battery2_df['時刻'],
            y=battery2_df['SOC'],
            name='バッテリ2 SOC',
            line=dict(color='lightgreen', width=1),
            mode='lines',
            hovertemplate='<b>バッテリ2 SOC</b>: %{y:.1f}%<br>時刻: %{x}<extra></extra>'
        ),
        row=2, col=1
    )

# 3. バッテリ3-4のSOC - 1分粒度
battery3_df = soc_battery34_df[soc_battery34_df['蓄電池名'] == '蓄電池3']
battery4_df = soc_battery34_df[soc_battery34_df['蓄電池名'] == '蓄電池4']

if len(battery3_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=battery3_df['時刻'],
            y=battery3_df['SOC'],
            name='バッテリ3 SOC',
            line=dict(color='orange', width=1),
            mode='lines',
            hovertemplate='<b>バッテリ3 SOC</b>: %{y:.1f}%<br>時刻: %{x}<extra></extra>'
        ),
        row=2, col=1
    )

if len(battery4_df) > 0:
    fig.add_trace(
        go.Scatter(
            x=battery4_df['時刻'],
            y=battery4_df['SOC'],
            name='バッテリ4 SOC',
            line=dict(color='red', width=1),
            mode='lines',
            hovertemplate='<b>バッテリ4 SOC</b>: %{y:.1f}%<br>時刻: %{x}<extra></extra>'
        ),
        row=2, col=1
    )

# レイアウト更新
fig.update_xaxes(title_text="時刻", row=2, col=1)
fig.update_yaxes(title_text="計画値 (kW)", row=1, col=1)
fig.update_yaxes(title_text="SOC (%)", row=2, col=1)

fig.update_layout(
    title={
        'text': '荒尾発電所 - 二次・三次調整力市場データ<br><sub>2024年6月～2025年4月</sub>',
        'x': 0.5,
        'xanchor': 'center'
    },
    height=900,
    hovermode='x unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    template='plotly_white'
)

# 統計情報を計算
print("\n=== 統計情報 ===")

# 計画リソース別の統計
print("\n計画リソース別データ数:")
print(f"  JEPX: {len(jepx_df)} 行")
print(f"  二次・三次: {len(nijisanji_df)} 行")
print(f"  合計: {len(schedule_df)} 行")

if len(jepx_df) > 0:
    print(f"\nJEPX計画値:")
    print(f"  平均: {jepx_df['計画値'].mean():.2f} kW")
    print(f"  最大: {jepx_df['計画値'].max():.2f} kW")
    print(f"  最小: {jepx_df['計画値'].min():.2f} kW")
    non_zero_pct = (jepx_df['計画値'] != 0).sum() / len(jepx_df) * 100
    print(f"  非ゼロの割合: {non_zero_pct:.1f}%")

if len(nijisanji_df) > 0:
    print(f"\n二次・三次調整力計画値:")
    print(f"  平均: {nijisanji_df['計画値'].mean():.2f} kW")
    print(f"  最大: {nijisanji_df['計画値'].max():.2f} kW")
    print(f"  最小: {nijisanji_df['計画値'].min():.2f} kW")
    non_zero_pct = (nijisanji_df['計画値'] != 0).sum() / len(nijisanji_df) * 100
    print(f"  非ゼロの割合: {non_zero_pct:.1f}%")

if len(battery1_df) > 0:
    print(f"\nバッテリ1 SOC:")
    print(f"  平均: {battery1_df['SOC'].mean():.2f}%")
    print(f"  最大: {battery1_df['SOC'].max():.2f}%")
    print(f"  最小: {battery1_df['SOC'].min():.2f}%")

if len(battery2_df) > 0:
    print(f"\nバッテリ2 SOC:")
    print(f"  平均: {battery2_df['SOC'].mean():.2f}%")
    print(f"  最大: {battery2_df['SOC'].max():.2f}%")
    print(f"  最小: {battery2_df['SOC'].min():.2f}%")

if len(battery3_df) > 0:
    print(f"\nバッテリ3 SOC:")
    print(f"  平均: {battery3_df['SOC'].mean():.2f}%")
    print(f"  最大: {battery3_df['SOC'].max():.2f}%")
    print(f"  最小: {battery3_df['SOC'].min():.2f}%")

if len(battery4_df) > 0:
    print(f"\nバッテリ4 SOC:")
    print(f"  平均: {battery4_df['SOC'].mean():.2f}%")
    print(f"  最大: {battery4_df['SOC'].max():.2f}%")
    print(f"  最小: {battery4_df['SOC'].min():.2f}%")

# HTML出力
output_file = 'arao_visualization.html'
fig.write_html(output_file)
print(f"\n✅ 可視化完了: {output_file}")

# ブラウザで開く
import webbrowser
webbrowser.open(output_file)
