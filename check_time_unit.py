"""
時間単位の確認 - 2025/2/16 15:30のケースを詳細分析
"""

import pandas as pd

# データ読み込み
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

# 2025/2/16のデータを抽出
target_date = '2025-02-16'
target_time_start = pd.Timestamp('2025-02-16 15:00:00')
target_time_end = pd.Timestamp('2025-02-16 17:00:00')

# スケジュールデータ
schedule_target = schedule_df[
    (schedule_df['開始時刻'] >= target_time_start) &
    (schedule_df['開始時刻'] < target_time_end)
]

print("=" * 70)
print("2025年2月16日 15:30のデータ詳細分析")
print("=" * 70)

print("\n【スケジュールデータ】")
for idx, row in schedule_target.iterrows():
    print(f"\n開始時刻: {row['開始時刻']}")
    print(f"終了時刻: {row['終了時刻']}")
    duration = (row['終了時刻'] - row['開始時刻']).total_seconds() / 60
    print(f"期間: {duration:.0f} 分")
    print(f"計画リソース: {row['計画リソース']}")
    print(f"計画値: {row['計画値']:.2f} kW")

# SOCデータ（15:00～16:30の範囲）
soc_start_time = pd.Timestamp('2025-02-16 15:00:00')
soc_end_time = pd.Timestamp('2025-02-16 16:30:00')

print("\n" + "=" * 70)
print("【SOCデータ】15:00～16:30の範囲")
print("=" * 70)

# バッテリ1-2
soc12_period = soc_battery12_df[
    (soc_battery12_df['時刻'] >= soc_start_time) &
    (soc_battery12_df['時刻'] <= soc_end_time)
].copy()

# バッテリ3-4
soc34_period = soc_battery34_df[
    (soc_battery34_df['時刻'] >= soc_start_time) &
    (soc_battery34_df['時刻'] <= soc_end_time)
].copy()

# 全バッテリの平均
all_soc = pd.concat([soc12_period, soc34_period])
avg_soc_per_time = all_soc.groupby('時刻')['SOC'].mean().reset_index()

print(f"\nSOC推移（全バッテリ平均、1分粒度の一部）:")
print("-" * 70)

# 主要な時刻のみ表示
key_times = [
    '2025-02-16 15:00:00',
    '2025-02-16 15:15:00',
    '2025-02-16 15:30:00',
    '2025-02-16 15:45:00',
    '2025-02-16 16:00:00',
    '2025-02-16 16:15:00',
    '2025-02-16 16:30:00',
]

for key_time in key_times:
    key_ts = pd.Timestamp(key_time)
    nearest = avg_soc_per_time[
        avg_soc_per_time['時刻'] >= key_ts
    ].head(1)
    if len(nearest) > 0:
        print(f"{key_time}: SOC = {nearest.iloc[0]['SOC']:.2f}%")

# 15:30と16:00の正確な値を取得
soc_1530 = avg_soc_per_time[
    avg_soc_per_time['時刻'] >= pd.Timestamp('2025-02-16 15:30:00')
].head(1)

soc_1600 = avg_soc_per_time[
    avg_soc_per_time['時刻'] >= pd.Timestamp('2025-02-16 16:00:00')
].head(1)

if len(soc_1530) > 0 and len(soc_1600) > 0:
    soc_start_val = soc_1530.iloc[0]['SOC']
    soc_end_val = soc_1600.iloc[0]['SOC']
    delta_soc = soc_end_val - soc_start_val
    
    print("\n" + "=" * 70)
    print("【ΔSOC計算】")
    print("=" * 70)
    print(f"\n15:30時点のSOC: {soc_start_val:.2f}%")
    print(f"16:00時点のSOC: {soc_end_val:.2f}%")
    print(f"ΔSOC (30分間): {delta_soc:.2f}%")
    print(f"ΔSOC (絶対値): {abs(delta_soc):.2f}%")

# 15:30-16:00の計画値を取得
schedule_1530_1600 = schedule_df[
    (schedule_df['開始時刻'] == pd.Timestamp('2025-02-16 15:30:00'))
]

# 計画値との関係を計算
if len(schedule_1530_1600) > 0:
    plan_value = schedule_1530_1600.iloc[0]['計画値']
    
    print("\n" + "=" * 70)
    print("【回帰式の検証】")
    print("=" * 70)
    print(f"\n計画値: {plan_value:.2f} kW")
    print(f"実測ΔSOC: {delta_soc:.2f}%")
    
    # 30分あたりの係数を計算
    if plan_value != 0:
        coef_30min = delta_soc / plan_value
        print(f"\n30分あたりの係数: {coef_30min:.6f} (%/kW)")
        print(f"  → 計画値1kWあたり {coef_30min:.6f}% のSOC変化")
        
        # 容量の推定
        # ΔSOC% = (電力kW × 時間h / 容量kWh) × 100
        # 容量 = (電力 × 時間 / ΔSOC) × 100
        power_kw = abs(plan_value)
        time_h = 0.5  # 30分 = 0.5時間
        capacity_kwh = (power_kw * time_h / abs(delta_soc)) * 100
        
        print(f"\n【容量の推定】")
        print(f"  電力: {power_kw:.2f} kW")
        print(f"  時間: {time_h:.2f} 時間 (30分)")
        print(f"  ΔSOC: {abs(delta_soc):.2f}%")
        print(f"  → 推定容量: {capacity_kwh:.2f} kWh")
        
        # 1時間あたりの係数
        coef_1h = coef_30min * 2
        print(f"\n1時間あたりの係数: {coef_1h:.6f} (%/kW)")

print("\n" + "=" * 70)
print("【結論】")
print("=" * 70)
print("""
回帰式の係数 0.004553 は30分間の変化を表している可能性が高い。

検証:
  計画値: -1962.24 kW
  予測ΔSOC: 0.004553 × (-1962.24) = -8.94%
  実測ΔSOC: 約-13%（あなたの観測）
  
時間単位の確認が必要:
  1. 回帰式が何分間のΔSOCを予測しているか
  2. スケジュールの「期間」が正しく反映されているか
  3. SOCのサンプリング時刻が適切か
""")
