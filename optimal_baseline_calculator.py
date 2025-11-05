import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_optimal_baseline(current_soc, target_soc_max=90, block_hours=3):
    """
    現在のSOCから最適な基準値を計算
    
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
    
    # 利用可能なSOC増加量
    available_soc_increase = target_soc_max - current_soc
    
    # 1時間あたりの最大SOC変化率
    max_rate_per_hour = available_soc_increase / block_hours
    
    # 基準値を計算: 基準値 = (SOC変化率 - INTERCEPT) / SLOPE
    optimal_baseline = (max_rate_per_hour - INTERCEPT) / SLOPE
    
    # 負の値を防ぐ
    optimal_baseline = max(0, optimal_baseline)
    
    # 予想されるSOC変化
    predicted_rate = SLOPE * optimal_baseline + INTERCEPT
    predicted_soc = current_soc + (predicted_rate * block_hours)
    
    return optimal_baseline, predicted_soc


def generate_daily_schedule(initial_soc, start_time, end_time, block_hours=3):
    """
    1日分の最適スケジュールを生成
    
    Parameters:
    -----------
    initial_soc : float
        開始時のSOC (%)
    start_time : str
        開始時刻 (例: "06:00")
    end_time : str
        終了時刻 (例: "18:00")
    block_hours : float
        時間ブロック (デフォルト: 3時間)
    
    Returns:
    --------
    schedule : list of dict
        時間帯ごとのスケジュール
    """
    
    schedule = []
    current_soc = initial_soc
    current_time = datetime.strptime(start_time, "%H:%M")
    end_datetime = datetime.strptime(end_time, "%H:%M")
    
    block_num = 1
    
    while current_time < end_datetime:
        # 最適基準値を計算
        optimal_baseline, predicted_soc = calculate_optimal_baseline(
            current_soc, 
            target_soc_max=90, 
            block_hours=block_hours
        )
        
        # 次の時間
        next_time = current_time + timedelta(hours=block_hours)
        
        schedule.append({
            'block': block_num,
            'start_time': current_time.strftime("%H:%M"),
            'end_time': next_time.strftime("%H:%M"),
            'duration_hours': block_hours,
            'soc_start': current_soc,
            'optimal_baseline_kw': round(optimal_baseline, 0),
            'predicted_soc_end': round(predicted_soc, 1),
            'soc_increase': round(predicted_soc - current_soc, 1)
        })
        
        # 次のブロックの準備
        current_soc = predicted_soc
        current_time = next_time
        block_num += 1
    
    return schedule


def print_schedule(schedule):
    """
    スケジュールを表形式で表示
    """
    print("\n" + "="*90)
    print("最適化スケジュール")
    print("="*90)
    print(f"{'Block':<6} {'時間帯':<15} {'開始SOC':<10} {'基準値':<12} {'予想SOC':<10} {'SOC増加':<10}")
    print("-"*90)
    
    total_baseline = 0
    
    for item in schedule:
        print(f"{item['block']:<6} "
              f"{item['start_time']}-{item['end_time']:<9} "
              f"{item['soc_start']:<9.1f}% "
              f"{item['optimal_baseline_kw']:<11.0f}kW "
              f"{item['predicted_soc_end']:<9.1f}% "
              f"{item['soc_increase']:+9.1f}%")
        
        total_baseline += item['optimal_baseline_kw']
    
    print("-"*90)
    print(f"{'合計基準値:':<40} {total_baseline:.0f} kW")
    print(f"{'最終SOC:':<40} {schedule[-1]['predicted_soc_end']:.1f} %")
    print("="*90)


def main():
    """
    メイン関数：複数のシナリオで最適化を実行
    """
    
    print("="*90)
    print("SOC最適化計算ツール")
    print("="*90)
    print("\n【公式】")
    print("  SOC変化率 (%/時間) = 0.012804 × 基準値(kW) - 1.9515")
    print("  相関係数 (R²) = 0.9997")
    print("\n【制約条件】")
    print("  - SOC ≤ 90%")
    print("  - 基準値設定: 3時間ブロック")
    
    # シナリオ1: 低SOCから開始
    print("\n" + "="*90)
    print("シナリオ1: 初期SOC 5% (9月25日実測に近い)")
    print("="*90)
    schedule1 = generate_daily_schedule(
        initial_soc=5.0,
        start_time="06:00",
        end_time="15:00",
        block_hours=3
    )
    print_schedule(schedule1)
    
    # シナリオ2: 中程度のSOCから開始
    print("\n" + "="*90)
    print("シナリオ2: 初期SOC 20%")
    print("="*90)
    schedule2 = generate_daily_schedule(
        initial_soc=20.0,
        start_time="06:00",
        end_time="15:00",
        block_hours=3
    )
    print_schedule(schedule2)
    
    # シナリオ3: 高SOCから開始
    print("\n" + "="*90)
    print("シナリオ3: 初期SOC 50%")
    print("="*90)
    schedule3 = generate_daily_schedule(
        initial_soc=50.0,
        start_time="06:00",
        end_time="15:00",
        block_hours=3
    )
    print_schedule(schedule3)
    
    # 全シナリオの比較
    print("\n" + "="*90)
    print("シナリオ比較")
    print("="*90)
    
    scenarios = [
        ('シナリオ1 (初期SOC 5%)', schedule1),
        ('シナリオ2 (初期SOC 20%)', schedule2),
        ('シナリオ3 (初期SOC 50%)', schedule3)
    ]
    
    print(f"{'シナリオ':<25} {'初期SOC':<12} {'最終SOC':<12} {'合計基準値':<15} {'平均基準値'}")
    print("-"*90)
    
    for name, schedule in scenarios:
        initial = schedule[0]['soc_start']
        final = schedule[-1]['predicted_soc_end']
        total = sum(item['optimal_baseline_kw'] for item in schedule)
        avg = total / len(schedule)
        
        print(f"{name:<25} {initial:<11.1f}% {final:<11.1f}% {total:<14.0f}kW {avg:<.0f}kW")
    
    print("="*90)
    
    # CSVに保存
    all_schedules = []
    for name, schedule in scenarios:
        for item in schedule:
            item['scenario'] = name
            all_schedules.append(item)
    
    df = pd.DataFrame(all_schedules)
    df.to_csv('optimal_baseline_schedule.csv', index=False, encoding='utf-8-sig')
    print("\n✅ スケジュールをCSVに保存: optimal_baseline_schedule.csv")
    
    # 実用的な使用例
    print("\n" + "="*90)
    print("💡 実用的な使用方法")
    print("="*90)
    print("\n【基準値計算の簡易式】")
    print("  最適基準値 = (利用可能SOC / 3時間 + 1.9515) / 0.012804")
    print("  利用可能SOC = 90% - 現在のSOC")
    print("\n【例】")
    print("  現在SOC 10% の場合:")
    print("    利用可能SOC = 90 - 10 = 80%")
    print("    最適基準値 = (80/3 + 1.9515) / 0.012804 = 2,235 kW")
    print("\n  現在SOC 60% の場合:")
    print("    利用可能SOC = 90 - 60 = 30%")
    print("    最適基準値 = (30/3 + 1.9515) / 0.012804 = 933 kW")


if __name__ == "__main__":
    main()
