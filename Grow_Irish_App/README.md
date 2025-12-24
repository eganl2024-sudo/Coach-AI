# 🏃 Grow Irish Performance Analytics

**GPS-based session intensity and metabolic power demand (MDP) analysis for soccer teams.**

A Streamlit web application that transforms raw GPS tracking data into actionable insights for coaches and performance analysts.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 What It Does

This app helps coaching staff understand **how hard players are working** during training sessions by analyzing:

- **Metabolic Power Demand (MDP)** — Peak power output over 10s, 20s, and 30s windows
- **Session Intensity Index** — A composite z-score combining explosiveness, repeatability, and volume
- **Workload Distribution** — Which players are overloaded vs. undertrained
- **Performance Highlights** — Top explosive efforts, sustained power, and biggest workloads

---

## 🖥️ Screenshots

### Session Explorer
Filter sessions by date and player, visualize intensity trends over time.

### Player Analysis
Deep dive into individual player metrics with rolling window breakdowns.

### Coach vs. Analyst Views
- **Coach View**: Quick headlines and key decisions
- **Analyst View**: Full metrics, charts, and CSV exports

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/eganl2024-sudo/MDP_APP.git
cd MDP_APP
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

### 4. Load Data

- Click **"Load Default Data"** to use the included sample dataset (48 sessions)
- Or upload your own CSV files with GPS tracking data

---

## 📁 Project Structure

```
MDP_APP/
├── app.py                          # Main Streamlit entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── pages/                          # Multi-page app screens
│   ├── 1_Home.py                   # Data loading & quick start
│   ├── 2_Sessions.py               # Session explorer & trends
│   ├── 3_Players.py                # Individual player analysis
│   ├── 4_Configuration.py          # Intensity weight settings
│   └── 5_Documentation.py          # Help & methodology
│
├── src/                            # Internal modules
│   ├── config.py                   # Configuration & constants
│   ├── display_names.py            # Player/session display formatting
│   ├── intensity_classification.py # Intensity scoring logic
│   └── ui/
│       └── nav.py                  # Global navigation component
│
├── utils.py                        # Core utility functions
├── mp_intensity_pipeline.py        # Data aggregation engine
├── coach_metrics_engine.py         # Coach insights calculation
├── intensity_utils.py              # Intensity computation helpers
│
└── data/                           # Sample data files
    ├── full_players_df.csv         # Player tracking data
    ├── session_summary.csv         # Aggregated sessions
    ├── mdp_catalog.csv             # MDP reference
    └── player_mdp_profiles.csv     # Player MDP profiles
```

---

## 📊 Key Metrics Explained

### Session Intensity Index (z-score)

A composite metric that captures overall session demand:

| Component | Weight | Description |
|-----------|--------|-------------|
| **Explosiveness** | 30% | Peak short-burst power (10s windows) |
| **Repeatability** | 50% | Ability to sustain high outputs across the session |
| **Volume** | 20% | Total accumulated metabolic load |

**Interpretation:**
- `z > 1.5` → Very hard session 🔴
- `1.0 < z ≤ 1.5` → Hard session 🟡
- `-0.5 < z ≤ 1.0` → Typical session ⚪
- `z < -0.5` → Light session 🟢

### Metabolic Power Demand (MDP)

Power output measured in Watts over rolling windows:

| Metric | Window | Use Case |
|--------|--------|----------|
| **MDP 10s** | 10 seconds | Explosive capacity (sprints, accelerations) |
| **MDP 20s** | 20 seconds | Sustained high-intensity efforts |
| **MDP 30s** | 30 seconds | Repeated sprint ability |

---

## ⚙️ Configuration

Adjust intensity weights on the **Configuration** page to match your training philosophy:

| Preset | Explosiveness | Repeatability | Volume | Best For |
|--------|---------------|---------------|--------|----------|
| **Match-like** | 30% | 50% | 20% | General preparation |
| **Speed emphasis** | 50% | 30% | 20% | Speed/power development |
| **Conditioning** | 20% | 40% | 40% | Fitness building |

---

## 📋 Data Requirements

Your CSV files should include these columns:

| Column | Type | Description |
|--------|------|-------------|
| `player_id` | string | Unique player identifier |
| `date` | datetime | Session date |
| `session_id` | string | Unique session identifier |
| `speed` | float | Instantaneous speed (m/s) |
| `acc` | float | Acceleration (m/s²) |
| `hr` | float | Heart rate (bpm) |
| `mp` | float | Metabolic power (W/kg) |

---

## 🔧 Development

### Running Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
streamlit run app.py
```

### Adding New Features

1. Create new page in `pages/` folder
2. Add navigation link in `app.py`
3. Use `src/ui/nav.py` for consistent navigation

---

## 📦 Dependencies

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
scikit-learn>=1.3.0
scipy>=1.11.0
matplotlib>=3.8.0
seaborn>=0.13.0
statsmodels>=0.14.0
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Metabolic Power methodology based on di Prampero et al. research
- Developed for Grow Irish Soccer

---

## 📬 Contact

**Liam Egan**  
GitHub: [@eganl2024-sudo](https://github.com/eganl2024-sudo)

---

<p align="center">
  <i>Transform GPS data into coaching decisions.</i>
</p>
