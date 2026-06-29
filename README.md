# 🌍 USF Emissions Analysis Dashboard

An interactive GHG emissions analysis and machine learning dashboard built for the **University of South Florida** in collaboration with **Patel's College of Global Sustainability**. The dashboard calculates, visualizes, and forecasts Scope 1 and Scope 3 transportation-related greenhouse gas emissions across five categories using GHG Protocol standards.

**Live Demo:** [usf-emissions-dashboard.streamlit.app](https://usf-emissions-dashboard.streamlit.app)

---

## 📊 Overview

This project processes synthetic transportation and logistics datasets to produce a full emissions analysis pipeline — from raw activity data to ML-powered anomaly detection and forecasting. It was built as part of a sustainability consulting engagement with an airport industry client.

**Total emissions analyzed:** ~83.8M kg CO₂  
**Datasets:** 5 synthetic datasets, ~10,000 records each  
**Standards:** GHG Protocol Corporate Standard, EPA SmartWay emission factors

---

## 🗂️ Emission Categories Covered

| Page | Scope | GHG Protocol Category |
|---|---|---|
| EV / Fleet Transport | Scope 1 | Owned fleet vehicles |
| Upstream Logistics | Scope 3 | Category 4 — Upstream transportation |
| Business Travel | Scope 3 | Category 6 — Business travel |
| Employee Commuting | Scope 3 | Category 7 — Employee commuting |
| Downstream Transport | Scope 3 | Category 9 — Downstream transportation |

---

## 🤖 ML Models

### Anomaly Detection — IsolationForest
- Detects statistically abnormal shipments across emission, cost, and distance features
- Cross-dataset summary comparing anomaly rates across all 5 categories
- Feature importance analysis — identifies which features drive anomaly flags
- Carrier/supplier breakdown of anomalies
- Emission savings potential if anomalies are corrected
- CSV export of all flagged records

### Emissions Forecasting — Prophet
- Time-series forecasting of monthly emissions up to 24 months ahead
- Per-dataset or combined forecasts
- Trend and seasonality decomposition
- Year-over-year comparison
- 95% confidence intervals
- CSV export of forecast table

---

## 📈 Dashboard Features

### Per-Category Analysis Pages
Each emission category page includes:
- **Emissions by transport mode** — bar charts with volume and rate
- **Emissions by route/origin-destination** — top routes ranked by CO₂
- **Emissions by carrier or supplier** — % share and ranked breakdown
- **Cost analysis** — invoice vs emissions scatter, $/tonne by mode
- **Shipment volume analysis** — quartile breakdowns

### Overview Page
- KPI cards for each scope + total
- Emissions distribution donut chart
- Category comparison bar chart
- Key insights and methodology note

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Dashboard framework |
| Plotly | Interactive charts |
| Pandas / NumPy | Data processing |
| scikit-learn | IsolationForest anomaly detection |
| Prophet | Time-series forecasting |
| GitHub | Version control |
| Streamlit Cloud | Deployment |

---

## 📂 Project Structure

```
usf-emissions-dashboard/
├── dashboard.py                              # Main Streamlit app — all pages
├── logistics_emissions.py                   # Scope 3 Cat 4 calculation engine
├── business_travel_emissions.py             # Scope 3 Cat 6 calculation engine
├── commute_emissions.py                     # Scope 3 Cat 7 calculation engine
├── downstream_emissions.py                  # Scope 3 Cat 9 calculation engine
├── ev_emissions.py                          # Scope 1 calculation engine
├── requirements.txt                         # Python dependencies
├── synthetic_logistics_emissions_data.csv
├── synthetic_business_travel_data_v2.csv
├── synthetic_commute_data_v2.csv
├── synthetic_downstream_transport_data_v2.csv
├── synthetic_ev_transport_data_with_emissions.csv
└── .streamlit/
    └── config.toml                          # Light theme configuration
```

---

## ⚙️ Emission Calculation Methodology

All calculations follow GHG Protocol Corporate Standard using EPA SmartWay emission factors.

**Scope 1 — EV/Fleet Transport**
- Pre-calculated per-trip emissions broken down by fuel type (gasoline, diesel, electric, hybrid)

**Scope 3 Cat 4 — Upstream Logistics**
- Formula: `shipment_weight (tons) × distance (miles) × mode factor`
- Factors: Truck 0.161, Rail 0.027, Air 0.800, Ship 0.040 kg CO₂/ton-mile

**Scope 3 Cat 6 — Business Travel**
- Air (short/medium/long haul): 0.207 / 0.129 / 0.163 kg CO₂/passenger-mile
- Rail: 0.096 · Road: 0.297 · Bus: 0.066 kg CO₂/mile

**Scope 3 Cat 7 — Employee Commuting**
- Formula: `round_trip_distance × commuting_days × mode factor`

**Scope 3 Cat 9 — Downstream Transport**
- Formula: `shipment_weight (tons) × distance (miles) × mode factor`
- Factors: Road 0.186, Rail 0.021, Water 0.077, Air 1.086 kg CO₂/ton-mile

All results displayed in **kg CO₂**.

---

## 🚀 Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/moosaabbasii/usf-emissions-dashboard.git
cd usf-emissions-dashboard
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the dashboard**
```bash
streamlit run dashboard.py
```

**4. Open in browser**
```
http://localhost:8501
```

---

## 📦 Requirements

```
streamlit
pandas
numpy
plotly
openpyxl
scikit-learn
prophet
statsmodels
```

---

## 🔑 Key Findings

- **Total ~83.8M kg CO₂** calculated across all 5 emission categories
- **Downstream transport (Cat 9)** is the largest contributor at **66.2%** of total emissions
- **Air transport** dominates emissions in both logistics and business travel
- **IsolationForest** flagged 500 anomalous logistics shipments with an estimated **6.3M kg CO₂ savings potential** if corrected
- **Prophet forecasting** projects emissions trends up to 24 months forward with 95% confidence intervals

---

## 🏛️ Project Context

**Institution:** University of South Florida  
**College:** Patel's College of Global Sustainability  
**Supervisor:** Dr. Kaleemunnisa  
**Research Role:** COT 4400 Undergraduate Research  
**Standards:** GHG Protocol Corporate Standard (WRI / WBCSD)  
**Presented to:** Airport industry client (Tampa Bay region)

---

## ⚠️ Data Notice

All datasets used in this dashboard are **synthetic** — artificially generated to simulate realistic transportation operations. No real company data is included. Synthetic data was used to enable full pipeline development while preserving data privacy and complying with confidentiality requirements.

---

*Developed by Moosa Abbasi — University of South Florida*
