# 🏃 Strava Fitness Data Analytics — Bellabeat Case Study

> What does it actually take to turn a raw Fitbit export into a live, queryable business dashboard? Cleaning 18 messy CSVs, merging them across five granularities, and surfacing the one insight that matters: over half of users never hit a basic activity benchmark.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Wrangling-150458?logo=pandas&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

This project analyzes public **Fitbit fitness tracker data** (Fitabase/Mobius, 30–33 users, Apr–May 2016) as a case study for **Bellabeat**, a wellness-tech company for women. The brief: uncover how people actually use smart fitness devices, then turn that into marketing-strategy recommendations for Bellabeat's executive team — backed by a **live MySQL-powered Streamlit dashboard**, not just a static report.

**The headline finding:** over half of tracked users never reach a 7,500-step/day activity benchmark, sedentary time is meaningfully correlated with shorter sleep (r ≈ -0.60), and engagement drops off a cliff for anything beyond basic step tracking — only ~24/33 users log sleep, and just 8/33 ever log weight.

---

## ✨ Features

- 🧹 **Full data pipeline** — 18 raw Fitabase files (daily/hourly/minute/second granularity) cleaned, deduplicated, and merged into two analysis-ready tables (940 daily rows, 22,099 hourly rows)
- 🗄️ **MySQL-backed analysis** — schema, a portable Python loader (works identically on local MySQL and Aiven cloud), and 12 SQL queries covering weekday patterns, user segmentation, sleep/sedentary correlation, and more
- 🖥️ **Live Streamlit dashboard** — 9 tabs, filterable by user and date range, every chart re-queries MySQL on the fly
- 🔍 **Built-in query explorer** — pick from preset SQL queries or write your own directly in the dashboard
- 💡 **Card-based insights & recommendations** — key findings and marketing recommendations computed live from whatever filter is currently applied, not hardcoded

---

## 🔑 Key Insights

| Finding | Detail |
|---|---|
| 📉 **Activity gap** | ~52% of users average fewer than 7,500 steps/day |
| 😴 **Sedentary ↔ sleep link** | Correlation of ≈ -0.60 between sedentary minutes and minutes asleep |
| 🔥 **Peak burn hours** | Calories burnt peak 5–7 PM — the after-work exercise window |
| ⌚ **Non-wear days** | A meaningful share of "fully sedentary" days likely reflect the tracker not being worn |
| 📊 **Feature adoption drops off** | Only ~24/33 users log sleep, ~8/33 log weight, vs. near-universal step tracking |

---

## 📂 Project Structure

```
STRAVA_FITNESS/
├── CSV_DATA/                          # 08 raw Fitabase source CSVs
├── plots/                             # EDA charts (PNG) from Step 1
├── 01_eda_bellabeat.py                # Step 1: load, merge, clean, EDA
├── 02_mysql_schema_and_load.sql       # Step 2: MySQL schema + LOAD DATA INFILE
├── 03_sql_analysis_queries.sql        # Step 2: 12 SQL analysis queries
├── Aiven schema setup.sql             # MySQL schema + Create Table for Aiven Schema
├── bellabeat_daily_clean.csv          # Cleaned daily-level output (940 rows)
├── bellabeat_hourly_clean.csv         # Cleaned hourly-level output (22,099 rows)
├── README.md  
├── .gitignore                         
└── streamlit_app/
    ├── .streamlit/
    │   ├── config.toml                # Dashboard theme (Strava-orange, dark)
    │   ├── secrets.toml               # Template for DB credentials
    │   └── secrets.toml.example       # Template for DB credentials
    ├── 00_load_to_mysql.py            # Portable loader — local MySQL or Aiven
    ├── db.py                          # MySQL connection + cached query layer
    ├── dashboard.py                   # Main dashboard app
    ├── requirements.txt               # Python dependencies (pinned versions)
    ├── ca.pem                         # CA_SSL Certificate
    └── bellabeat_daily_clean.csv / bellabeat_hourly_clean.csv   # loader inputs
```

---

## ⚙️ Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/strava-fitness-data-analytics.git
cd strava-fitness-data-analytics/streamlit_app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your database
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit secrets.toml with your local MySQL or Aiven credentials
```

---

## 🚀 Usage

**Run the EDA & data pipeline** (from the project root):
```bash
python 01_eda_bellabeat.py
```

**Load the cleaned data into MySQL** (from `streamlit_app/`):
```bash
python 00_load_to_mysql.py
```

**Launch the interactive dashboard:**
```bash
streamlit run dashboard.py
```
Then open **http://localhost:8501** in your browser.

---

## 🛠️ Tech Stack

`Python` · `Pandas` · `MySQL` · `SQLAlchemy` · `Streamlit` · `Plotly`

---

## 🌐 Live Demo

🔗 *https://strava-fitness-data-analytics-kcub5qlwvka7vop66qlayq.streamlit.app/*

---

## 📊 Dataset Source

- Fitabase Fitbit Tracker Data: [Kaggle — FitBit Fitness Tracker Data](https://www.kaggle.com/datasets/arashnic/fitbit) (uploaded by Möbius, CC0 license)
- Original case study brief: Google Data Analytics Capstone — Bellabeat

---

## 👤 Author

**Abhijit Sinha** — [@abhi-1009](https://github.com/abhi-1009)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">🙏 Thanks for stopping by — feedback and stars ⭐ are always welcome!</p>
