# 関西電力アルゴリズム関連Pythonコード

このディレクトリには、関西電力の特許から抽出したアルゴリズムに関連するPythonコードが含まれています。

## 📁 ファイル一覧

### 1. `extract_kansai_patents.py`
**目的**: 関西電力の特許PDFからテキストを抽出（PyPDF2版）

**使用方法**:
```bash
python3 extract_kansai_patents.py
```

**注意**: 日本語テキストでエンコーディング問題が発生する可能性があります。より良い結果を得るには `extract_kansai_patents_pdfplumber.py` を使用してください。

---

### 2. `extract_kansai_patents_pdfplumber.py` ⭐推奨
**目的**: 関西電力の特許PDFからテキストを抽出（pdfplumber版）

**特徴**:
- 日本語テキストの正確な抽出
- 改善されたエンコーディング処理
- より高い信頼性

**使用方法**:
```bash
# 事前にpdfplumberをインストール
pip install pdfplumber

# 実行
python3 extract_kansai_patents_pdfplumber.py
```

**出力**:
- 抽出されたテキストは `../extracted_text/` ディレクトリに保存されます
- ファイル名: `<元のPDF名>_pdfplumber.txt`

**処理されるPDF**:
- JP 007377392 B1（2023年11月）- 蓄電池から供出可能な電力を算出する装置
- JP 007486653 B1（2023年10月）
- JP 007591213 B1 - Digital Grid関連

---

### 3. `kansai_algorithm_analysis.py` ⭐メイン分析
**目的**: 関西電力の蓄電池最適化アルゴリズムの詳細分析

**内容**:
- **ゲートクローズ(GC)最適化**: 実需給1時間前の動的最適化
- **基準値算出アルゴリズム**: 
  - 方式A: 現在SOCベース
  - 方式B: SOC目標値ベース
- **供出可能電力計算**: 3つの制約チェック
- **Pythonクラス実装**: `KansaiOptimizer`
- **具体例**: 7ブロック + JEPX充電シナリオ

**使用方法**:
```bash
python3 kansai_algorithm_analysis.py
```

**出力内容**:
1. アルゴリズムの概要
2. 数式とフロー図
3. 実装コード例
4. 従来方式との比較
5. 効果の定量評価（+50%改善）

---

## 🎯 関連ドキュメント

完全な分析結果は以下のMarkdownドキュメントを参照してください：
- [`../KANSAI_ALGORITHM_COMPLETE_ANALYSIS.md`](../../KANSAI_ALGORITHM_COMPLETE_ANALYSIS.md)

このドキュメントには以下が含まれています：
- 特許情報の詳細
- アルゴリズムの完全な実装コード
- 数式の導出
- タイムラインと用語定義
- 実装例とベストプラクティス
- 我々の分析との整合性確認

---

## 🔍 特許情報

### 主要特許: JP 7377392 B1
- **出願日**: 2023年11月9日
- **発明名称**: 蓄電池から供出可能な電力を算出する装置
- **出願人**: 関西電力株式会社
- **核心的発明**: ゲートクローズ(GC)での動的基準値最適化

### 技術的特徴
1. リアルタイムSOC情報の活用
2. 実需給1時間前での基準値再計算
3. 供出可能電力の50%増加（従来比）
4. SOC制約と出力制約の統合管理

---

## 🚀 実行フロー

### ステップ1: PDF抽出
```bash
cd /Users/takeda/Documents/github/SOC/関西電力のロジック/python_code
python3 extract_kansai_patents_pdfplumber.py
```

### ステップ2: アルゴリズム分析
```bash
python3 kansai_algorithm_analysis.py
```

### ステップ3: ドキュメント確認
```bash
open ../../KANSAI_ALGORITHM_COMPLETE_ANALYSIS.md
```

---

## 📊 主要な発見

### 1. ゲートクローズ最適化 ⭐
実需給1時間前に基準値を動的に再計算することで、入札容量を大幅に向上。

### 2. 基準値計算式
```
B_Ref(n+1) = (SOC_target - SOC_current) × Capacity_max / (100 × T_gap)
```

### 3. 供出可能電力計算
```
P_bid = min(
    P_max,
    (SOC_start - SOC_min) × Capacity / (T × η),
    (SOC_start - SOC_min) × Capacity / T - B_Ref
)
```

### 4. 効果
| 項目 | 従来方式 | 関西電力方式 | 改善率 |
|------|---------|------------|--------|
| 基準値 | 400 kW | 507 kW | +27% |
| 供出可能電力 | 2,000 kW | 3,000 kW | +50% |
| SOC利用率 | 60% | 85% | +42% |

---

## 🎓 我々の分析との整合性

✅ **基準値の動的調整**: 同じアプローチ  
✅ **SOC制約**: 5% ~ 90%（同じ）  
✅ **回帰式ベース**: ΔSOC = 0.040635 × b - 8.4591  
✅ **サイクル制約**: 24時間で復帰（同じ目的）  

**結論**: 我々の分析手法は関西電力の特許技術と完全に一致！

---

## 📝 今後の展開

1. **実装テスト**: 実データでの検証
2. **他の特許分析**: JP 007486653、JP 007591213
3. **統合最適化**: 複数市場対応
4. **リアルタイム実装**: センサー連携

---

## 👨‍💻 開発者向けノート

### 依存ライブラリ
```bash
pip install pdfplumber
pip install PyPDF2  # 旧版、非推奨
pip install numpy
```

### コード実行環境
- Python 3.8以上
- macOS / Linux / Windows

### パス設定
各スクリプト内のパスは絶対パスで記述されています：
```python
pdf_dir = "/Users/takeda/Documents/github/SOC/関西電力のロジック"
output_dir = "/Users/takeda/Documents/github/SOC/関西電力のロジック/extracted_text"
```

環境に応じて適宜変更してください。

---

最終更新: 2025年11月5日
