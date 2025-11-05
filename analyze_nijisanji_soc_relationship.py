"""
荒尾発電所 - 二次・三次調整力の計画値とSOC変化の関係分析
JEPX影響を除外し、純粋に二次・三次のみのデータで回帰式を導出
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from scipy import stats

print("=" * 60)
print("二次・三次調整力 計画値 vs ΔSOC 分析")
print("=" * 60)

# データ読み込み
print("\nデータを読み込んでいます...")
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

# 二次・三次のデータのみを抽出
nijisanji_df = schedule_df[
    schedule_df['計画リソース'] == '二次・三次'
].copy()

print(f"\n二次・三次データ数: {len(nijisanji_df)} 行")
print(f"期間: {nijisanji_df['開始時刻'].min()} ~ "
      f"{nijisanji_df['終了時刻'].max()}")

# SOCデータを30分ごとに集約（平均）
def aggregate_soc_30min(soc_df):
    """SOCデータを30分ごとに集約"""
    soc_df = soc_df.copy()
    soc_df['時刻_30min'] = soc_df['時刻'].dt.floor('30min')
    return soc_df.groupby(
        ['蓄電池名', '時刻_30min']
    )['SOC'].mean().reset_index()

soc12_30min = aggregate_soc_30min(soc_battery12_df)
soc34_30min = aggregate_soc_30min(soc_battery34_df)

# 全バッテリの平均SOCを計算
all_soc = pd.concat([soc12_30min, soc34_30min])
avg_soc = all_soc.groupby('時刻_30min')['SOC'].mean().reset_index()
avg_soc.columns = ['時刻', 'SOC平均']

print(f"30分平均SOCデータ数: {len(avg_soc)} 行")

# 二次・三次の各期間について、開始時と終了時のSOCを取得
analysis_data = []

for idx, row in nijisanji_df.iterrows():
    start_time = row['開始時刻']
    end_time = row['終了時刻']
    plan_value = row['計画値']
    
    # 開始時刻のSOCを取得（前の時刻の値）
    soc_before = avg_soc[
        avg_soc['時刻'] <= start_time
    ].tail(1)
    
    # 終了時刻のSOCを取得
    soc_after = avg_soc[
        (avg_soc['時刻'] >= start_time) & 
        (avg_soc['時刻'] <= end_time)
    ].tail(1)
    
    if len(soc_before) > 0 and len(soc_after) > 0:
        soc_start = soc_before.iloc[0]['SOC平均']
        soc_end = soc_after.iloc[0]['SOC平均']
        delta_soc = soc_end - soc_start
        
        # 時間差（分）
        time_diff_min = (end_time - start_time).total_seconds() / 60
        
        analysis_data.append({
            '開始時刻': start_time,
            '終了時刻': end_time,
            '計画値': plan_value,
            'SOC開始': soc_start,
            'SOC終了': soc_end,
            'ΔSOC': delta_soc,
            '時間_分': time_diff_min,
            'ΔSOC_per_30min': delta_soc * (30 / time_diff_min) if time_diff_min > 0 else 0
        })

result_df = pd.DataFrame(analysis_data)

print(f"\n分析対象データ数: {len(result_df)} 件")
print(f"計画値の範囲: {result_df['計画値'].min():.2f} ~ "
      f"{result_df['計画値'].max():.2f} kW")
print(f"ΔSOCの範囲: {result_df['ΔSOC'].min():.2f} ~ "
      f"{result_df['ΔSOC'].max():.2f} %")

# 非ゼロの計画値のみを抽出
result_nonzero = result_df[result_df['計画値'] != 0].copy()
print(f"\n非ゼロ計画値データ数: {len(result_nonzero)} 件")

# 統計情報
print("\n" + "=" * 60)
print("統計情報（非ゼロ計画値のみ）")
print("=" * 60)
print(f"\n計画値:")
print(f"  平均: {result_nonzero['計画値'].mean():.2f} kW")
print(f"  標準偏差: {result_nonzero['計画値'].std():.2f} kW")
print(f"  中央値: {result_nonzero['計画値'].median():.2f} kW")

print(f"\nΔSOC:")
print(f"  平均: {result_nonzero['ΔSOC'].mean():.2f} %")
print(f"  標準偏差: {result_nonzero['ΔSOC'].std():.2f} %")
print(f"  中央値: {result_nonzero['ΔSOC'].median():.2f} %")

# 線形回帰分析
X = result_nonzero['計画値'].values.reshape(-1, 1)
y = result_nonzero['ΔSOC'].values

model = LinearRegression()
model.fit(X, y)

slope = model.coef_[0]
intercept = model.intercept_
r_squared = model.score(X, y)

# 予測値
y_pred = model.predict(X)

# 統計検定
pearson_r, pearson_p = stats.pearsonr(
    result_nonzero['計画値'], 
    result_nonzero['ΔSOC']
)

print("\n" + "=" * 60)
print("回帰分析結果")
print("=" * 60)
print(f"\n回帰式: ΔSOC = {slope:.6f} × 計画値 + {intercept:.4f}")
print(f"R² = {r_squared:.4f}")
print(f"相関係数 r = {pearson_r:.4f}")
print(f"p値 = {pearson_p:.2e}")

if pearson_p < 0.01:
    print("→ 統計的に非常に有意（p < 0.01）✅")
elif pearson_p < 0.05:
    print("→ 統計的に有意（p < 0.05）✅")
else:
    print("→ 統計的に有意ではない")

# 具体例での検証
print("\n" + "=" * 60)
print("具体例での検証")
print("=" * 60)

# 2025/2/16の例を探す
example_date = pd.Timestamp('2025-02-16 15:30:00')
example_row = result_df[
    result_df['開始時刻'] == example_date
]

if len(example_row) > 0:
    row = example_row.iloc[0]
    print(f"\n2025/2/16 15:30の実例:")
    print(f"  計画値: {row['計画値']:.2f} kW")
    print(f"  SOC変化: {row['SOC開始']:.2f}% → {row['SOC終了']:.2f}%")
    print(f"  ΔSOC実測: {row['ΔSOC']:.2f}%")
    
    predicted = slope * row['計画値'] + intercept
    print(f"  ΔSOC予測: {predicted:.2f}%")
    print(f"  誤差: {abs(row['ΔSOC'] - predicted):.2f}%")

# 追加の検証例
print("\n他の検証例:")
for plan_value in [-2000, -1500, -1000, -500, 0]:
    predicted = slope * plan_value + intercept
    print(f"  計画値 {plan_value:5.0f} kW → ΔSOC予測 {predicted:6.2f}%")

# 可視化
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        '計画値 vs ΔSOC（散布図）',
        '残差プロット',
        'ΔSOC分布（ヒストグラム）',
        '時系列プロット'
    ),
    specs=[
        [{"type": "scatter"}, {"type": "scatter"}],
        [{"type": "histogram"}, {"type": "scatter"}]
    ]
)

# 1. 散布図 + 回帰線
fig.add_trace(
    go.Scatter(
        x=result_nonzero['計画値'],
        y=result_nonzero['ΔSOC'],
        mode='markers',
        name='実測値',
        marker=dict(
            color='blue',
            size=5,
            opacity=0.5
        ),
        hovertemplate=(
            '計画値: %{x:.1f} kW<br>'
            'ΔSOC: %{y:.2f}%<extra></extra>'
        )
    ),
    row=1, col=1
)

# 回帰線
x_line = np.linspace(
    result_nonzero['計画値'].min(),
    result_nonzero['計画値'].max(),
    100
)
y_line = slope * x_line + intercept

fig.add_trace(
    go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name=f'回帰線 (R²={r_squared:.3f})',
        line=dict(color='red', width=2)
    ),
    row=1, col=1
)

# 2. 残差プロット
residuals = result_nonzero['ΔSOC'].values - y_pred
fig.add_trace(
    go.Scatter(
        x=result_nonzero['計画値'],
        y=residuals,
        mode='markers',
        name='残差',
        marker=dict(color='green', size=5, opacity=0.5),
        hovertemplate=(
            '計画値: %{x:.1f} kW<br>'
            '残差: %{y:.2f}%<extra></extra>'
        )
    ),
    row=1, col=2
)

fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=2)

# 3. ΔSOCのヒストグラム
fig.add_trace(
    go.Histogram(
        x=result_nonzero['ΔSOC'],
        name='ΔSOC分布',
        marker=dict(color='purple'),
        nbinsx=50
    ),
    row=2, col=1
)

# 4. 時系列プロット
fig.add_trace(
    go.Scatter(
        x=result_nonzero['開始時刻'],
        y=result_nonzero['ΔSOC'],
        mode='markers',
        name='ΔSOC時系列',
        marker=dict(
            color=result_nonzero['計画値'],
            colorscale='RdYlBu',
            size=5,
            colorbar=dict(title="計画値<br>(kW)", x=1.15)
        ),
        hovertemplate=(
            '時刻: %{x}<br>'
            'ΔSOC: %{y:.2f}%<extra></extra>'
        )
    ),
    row=2, col=2
)

# レイアウト
fig.update_xaxes(title_text="計画値 (kW)", row=1, col=1)
fig.update_yaxes(title_text="ΔSOC (%)", row=1, col=1)
fig.update_xaxes(title_text="計画値 (kW)", row=1, col=2)
fig.update_yaxes(title_text="残差 (%)", row=1, col=2)
fig.update_xaxes(title_text="ΔSOC (%)", row=2, col=1)
fig.update_yaxes(title_text="頻度", row=2, col=1)
fig.update_xaxes(title_text="時刻", row=2, col=2)
fig.update_yaxes(title_text="ΔSOC (%)", row=2, col=2)

fig.update_layout(
    title={
        'text': (
            f'荒尾発電所 - 二次・三次調整力 計画値 vs ΔSOC<br>'
            f'<sub>ΔSOC = {slope:.6f} × 計画値 + {intercept:.4f} '
            f'(R² = {r_squared:.4f})</sub>'
        ),
        'x': 0.5,
        'xanchor': 'center'
    },
    height=900,
    showlegend=True,
    template='plotly_white'
)

# HTML出力
output_file = 'arao_nijisanji_soc_analysis.html'
fig.write_html(output_file)
print(f"\n✅ 可視化完了: {output_file}")

# CSVで結果を保存
result_nonzero.to_csv(
    'arao_nijisanji_soc_data.csv',
    index=False,
    encoding='utf-8-sig'
)
print(f"✅ データ保存完了: arao_nijisanji_soc_data.csv")

# サマリー
print("\n" + "=" * 60)
print("分析まとめ")
print("=" * 60)
print(f"""
荒尾発電所 二次・三次調整力データ分析結果:

【回帰式】
  ΔSOC = {slope:.6f} × 計画値 + {intercept:.4f}

【精度】
  R² = {r_squared:.4f}
  相関係数 = {pearson_r:.4f}
  p値 = {pearson_p:.2e}

【解釈】
  - 計画値が負（放電）→ SOC減少
  - 計画値が正（充電）→ SOC増加
  - 係数 {slope:.6f} = 1kWあたりのSOC変化率
  
【信頼度】
  データ数: {len(result_nonzero)} 件
  JEPX影響除外: ✅
  統計的有意性: {'✅' if pearson_p < 0.05 else '❌'}
""")

import webbrowser
webbrowser.open(output_file)
