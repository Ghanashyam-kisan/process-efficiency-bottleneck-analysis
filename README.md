# ⚙️ Process Efficiency & Bottleneck Analysis System

> A complete data-driven toolkit for identifying bottlenecks, measuring throughput,
> and improving manufacturing / workflow efficiency.

---

## 📌 Problem Statement

In manufacturing and service operations, **process inefficiency** costs time and money.
Delays at any single stage ripple through the entire workflow, inflating cycle times
and reducing throughput. Without data, engineers rely on guesswork to locate the culprit.

This system generates realistic process data, automatically pinpoints the **bottleneck
stage**, and surfaces actionable KPIs — all in a clean interactive dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| Synthetic data generation | 1 000+ realistic process runs with stage-level timings |
| Bottleneck detection | Identifies which stage causes the most delays |
| KPI dashboard | Throughput, efficiency %, idle time, cycle time |
| Delay flagging | Marks any run exceeding a configurable threshold |
| Matplotlib charts | Bar, line, contribution & histogram charts |
| Streamlit app | Live, interactive dashboard with adjustable threshold |
| CSV export | Download the full dataset from the dashboard |

---

## 📐 Metrics Explained

### Throughput (processes / hour)
How many complete process runs finish in one hour.
```
Throughput = 60 ÷ Average Total Cycle Time
```

### Idle / Waste Time (minutes)
How much time is lost compared to the theoretical best case.
```
Idle Time = Avg Cycle Time − Ideal Cycle Time
```
*Ideal Cycle Time* = sum of the 5th-percentile time for each stage (best realistic scenario).

### Efficiency (%)
How close actual performance is to the ideal.
```
Efficiency = (Ideal Cycle Time ÷ Avg Cycle Time) × 100
```
100 % = zero waste. Lower values indicate more room for improvement.

### Delay Flag
A binary column: **1** = process exceeded the delay threshold, **0** = on-time.

### Bottleneck Stage
The stage with the highest average time **among delayed processes**.
Targeting this stage yields the greatest improvement in overall throughput.

---

## 🗂️ Project Structure

```
process-efficiency-bottleneck-analysis/
│
├── data/
│   └── process_data.csv        ← auto-generated on first run
│
├── src/
│   ├── data_generator.py       ← synthetic data creation
│   ├── analysis.py             ← stage analysis & bottleneck logic
│   └── metrics.py              ← KPI computations
│
├── app/
│   └── streamlit_app.py        ← interactive dashboard
│
├── charts/                     ← PNG charts (created by main.py)
│
├── requirements.txt
├── README.md
└── main.py                     ← CLI entry-point
```

---

## 🚀 How to Run

### 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### 2 — Run the CLI pipeline (generates data + charts)

```bash
python main.py
```

This will:
- Generate `data/process_data.csv` (1 000 rows)
- Print a full analysis report to the terminal
- Save three charts to `charts/`

### 3 — Launch the Streamlit dashboard

```bash
streamlit run app/streamlit_app.py
```

Open the URL shown in your terminal (default: http://localhost:8501).

---

## 🎛️ Configuration

Edit constants at the top of each file to customise behaviour:

| File | Constant | Default | Purpose |
|---|---|---|---|
| `data_generator.py` | `N_ROWS` | 1000 | Number of process runs |
| `data_generator.py` | `DELAY_THRESHOLD` | 30 | Minutes above which a run is "delayed" |
| `data_generator.py` | `STAGE_CONFIG` | see file | Stage mean & std times |
| `main.py` | `DELAY_THRESHOLD` | 30 | Threshold used in charts |

---

## 📊 Sample Output

```
═══════════════════════════════════════════════════════
  PROCESS EFFICIENCY & BOTTLENECK ANALYSIS REPORT
═══════════════════════════════════════════════════════

📊  STAGE AVERAGE TIMES
    Stage 1: 15.03 min
    Stage 2: 25.11 min  ← BOTTLENECK
    Stage 3: 18.04 min

⚙️   KEY PERFORMANCE METRICS
    Avg Total Cycle Time  : 58.18 min
    Throughput            : 1.03 processes/hour
    Idle / Waste Time     : 13.08 min per process
    Process Efficiency    : 77.5%

🚨  DELAY ANALYSIS
    Delayed               : 487 / 1,000
    Delay Rate            : 48.7%

🔴  IDENTIFIED BOTTLENECK : Stage 2
```

---

## 🛠️ Built With

- **Python 3.9+**
- **pandas** — data manipulation
- **NumPy** — numerical computation
- **Matplotlib** — static chart generation
- **Streamlit** — interactive dashboard

---

*Built for manufacturing process optimisation, service workflow analysis,
and operations research education.*
