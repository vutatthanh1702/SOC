# Kotohira Energy Data Visualization

This repository contains Python scripts to visualize energy data from three CSV files using Plotly.

## Files

### Data Files
- `kotohira_soc_20250801~now (1).csv` - Battery State of Charge (SOC) data over time
- `kotohira_jiseki_20250801~now (1).csv` - Actual power consumption/generation data (実績値kW)
- `kotohira_kijyunchi_20250801~now (1).csv` - Planned generation and demand data (発電計画kW, 需要計画kW)

### Visualization Scripts
1. **`single_graph_visualization.py`** - Shows all data in one comprehensive graph
2. **`focused_visualization.py`** - Shows a focused 7-day view for better readability
3. **`visualize_data.py`** - Multi-subplot visualization with separate charts

## Installation

1. Install required packages:
```bash
pip3 install -r requirements.txt
```

## Usage

### Run the single graph visualization (recommended):
```bash
python3 single_graph_visualization.py
```
This creates `kotohira_single_graph.html` showing all three datasets in one graph with dual y-axes.

### Run the focused 7-day view:
```bash
python3 focused_visualization.py
```
This creates `kotohira_focused_7day_view.html` showing just the first 7 days of data for better readability.

### Run the multi-subplot visualization:
```bash
python3 visualize_data.py
```
This creates `kotohira_energy_data_visualization.html` with separate subplots for different data types.

## Data Description

### SOC Data (蓄電池データ)
- **Columns**: name, time, soc
- **Description**: Battery state of charge percentage over time
- **Color**: Blue line

### Actual Power Data (実績値データ)
- **Columns**: time, 実績値kW
- **Description**: Actual power consumption/generation in kilowatts
- **Color**: Red line

### Planned Data (計画値データ)
- **Columns**: start_time, end_time, 発電計画kW, 需要計画kW
- **Description**: Planned generation and demand values with time ranges
- **Colors**: Green (planned generation), Orange (planned demand)

## Features

- **Interactive plots**: Zoom, pan, and hover for detailed information
- **Dual y-axes**: SOC percentage on left, power values on right
- **Time series visualization**: All data plotted against time
- **HTML output**: View in any web browser
- **Data filtering**: Removes outliers (SOC > 100%) for cleaner visualization

## Output Files

All scripts generate HTML files that can be opened in a web browser:
- Interactive plots with zoom and pan capabilities
- Hover tooltips showing exact values
- Legend to toggle data series on/off
- Professional styling with clear axes labels

## Data Summary

The visualization shows:
- Battery SOC ranging from 5% to 99% (filtered to remove errors)
- Actual power ranging from -2,217kW to 2,138kW (negative = generation, positive = consumption)
- Planned values showing scheduled generation and demand periods
- Time coverage from August 2025 to October 2025