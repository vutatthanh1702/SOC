import pandas as pd
from datetime import datetime

def merge_three_csv_files():
    """
    3つのCSVファイルを1つに統合する
    - kotohira_soc_20250801~now (1).csv
    - kotohira_jiseki_20250801~now (1).csv
    - kotohira_kijyunchi_20250801~now (1).csv
    """
    
    print("="*70)
    print("3つのCSVファイルを統合中...")
    print("="*70)
    
    # 1. SOCデータの読み込み
    print("\n1️⃣  SOCデータを読み込んでいます...")
    soc_df = pd.read_csv('kotohira_soc_20250801~now (1).csv')
    soc_df['time'] = pd.to_datetime(soc_df['time'])
    # nameカラムは不要なので削除
    soc_df = soc_df[['time', 'soc']]
    print(f"   レコード数: {len(soc_df):,}")
    
    # 2. 実績値kWデータの読み込み
    print("\n2️⃣  実績値kWデータを読み込んでいます...")
    jiseki_df = pd.read_csv('kotohira_jiseki_20250801~now (1).csv')
    jiseki_df['time'] = pd.to_datetime(jiseki_df['time'])
    # カラム名を変更
    jiseki_df = jiseki_df.rename(columns={'実績値kW': 'actual_power_kw'})
    print(f"   レコード数: {len(jiseki_df):,}")
    
    # 3. 基準値(需要計画kW)データの読み込み
    print("\n3️⃣  需要計画kW(基準値)データを読み込んでいます...")
    kijyunchi_df = pd.read_csv('kotohira_kijyunchi_20250801~now (1).csv')
    kijyunchi_df['start_time'] = pd.to_datetime(kijyunchi_df['start_time'])
    kijyunchi_df['end_time'] = pd.to_datetime(kijyunchi_df['end_time'])
    
    # 需要計画kWのみを抽出
    kijyunchi_demand = kijyunchi_df[['start_time', 'end_time', '需要計画kW']].copy()
    kijyunchi_demand = kijyunchi_demand[pd.notna(kijyunchi_demand['需要計画kW'])]
    kijyunchi_demand['需要計画kW'] = pd.to_numeric(kijyunchi_demand['需要計画kW'], errors='coerce')
    print(f"   レコード数: {len(kijyunchi_demand):,}")
    
    # SOCと実績値kWをマージ（時間で結合）
    print("\n🔄 データをマージしています...")
    merged_df = pd.merge(soc_df, jiseki_df, on='time', how='outer')
    merged_df = merged_df.sort_values('time')
    print(f"   SOC + 実績値kW: {len(merged_df):,} レコード")
    
    # 需要計画kWを追加（時間範囲に基づいて）
    print("\n🔄 需要計画kW(基準値)を追加しています...")
    merged_df['demand_plan_kw'] = None
    
    for idx, row in kijyunchi_demand.iterrows():
        mask = (merged_df['time'] >= row['start_time']) & (merged_df['time'] <= row['end_time'])
        merged_df.loc[mask, 'demand_plan_kw'] = row['需要計画kW']
    
    # カラム名を分かりやすく変更
    merged_df = merged_df.rename(columns={
        'time': 'timestamp',
        'soc': 'battery_soc_percent',
        'actual_power_kw': 'actual_power_kw',
        'demand_plan_kw': 'demand_plan_kw_baseline'
    })
    
    # タイムゾーン情報を削除（CSVで見やすくするため）
    merged_df['timestamp'] = merged_df['timestamp'].dt.tz_localize(None)
    
    # CSVに保存
    output_file = 'kotohira_integrated_data.csv'
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ 統合完了！")
    print(f"   出力ファイル: {output_file}")
    print(f"   総レコード数: {len(merged_df):,}")
    
    # データのサマリーを表示
    print("\n" + "="*70)
    print("📊 統合データのサマリー")
    print("="*70)
    
    print(f"\n【カラム情報】")
    print(f"  1. timestamp              : 時刻")
    print(f"  2. battery_soc_percent    : 蓄電池SOC (%)")
    print(f"  3. actual_power_kw        : 実績値 (kW)")
    print(f"  4. demand_plan_kw_baseline: 需要計画kW (基準値)")
    
    print(f"\n【時間範囲】")
    print(f"  開始: {merged_df['timestamp'].min()}")
    print(f"  終了: {merged_df['timestamp'].max()}")
    
    print(f"\n【データ統計】")
    print(f"  SOC:")
    print(f"    - 有効レコード数: {merged_df['battery_soc_percent'].notna().sum():,}")
    print(f"    - 範囲: {merged_df['battery_soc_percent'].min():.1f}% ～ {merged_df['battery_soc_percent'].max():.1f}%")
    print(f"    - 平均: {merged_df['battery_soc_percent'].mean():.1f}%")
    
    print(f"\n  実績値kW:")
    print(f"    - 有効レコード数: {merged_df['actual_power_kw'].notna().sum():,}")
    print(f"    - 範囲: {merged_df['actual_power_kw'].min():.1f}kW ～ {merged_df['actual_power_kw'].max():.1f}kW")
    print(f"    - 平均: {merged_df['actual_power_kw'].mean():.1f}kW")
    
    print(f"\n  需要計画kW(基準値):")
    print(f"    - 有効レコード数: {merged_df['demand_plan_kw_baseline'].notna().sum():,}")
    if merged_df['demand_plan_kw_baseline'].notna().sum() > 0:
        print(f"    - 範囲: {merged_df['demand_plan_kw_baseline'].min():.1f}kW ～ {merged_df['demand_plan_kw_baseline'].max():.1f}kW")
        print(f"    - 平均: {merged_df['demand_plan_kw_baseline'].mean():.1f}kW")
    
    # サンプルデータを表示
    print(f"\n【データサンプル（最初の10行）】")
    print(merged_df.head(10).to_string())
    
    print("\n" + "="*70)
    print("🎉 完了！")
    print("="*70)
    
    return merged_df


if __name__ == "__main__":
    merged_data = merge_three_csv_files()
