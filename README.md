[🇬🇧 English](README.md) · [🇪🇸 Español](README.es.md)

<div align="center">
  <img src="src/berrix/assets/ag6.svg" alt="AG · Andrés Gómez" width="140">

  # Commercial Dashboard · Berrix

  **B2B sales analytics for the berry agro-industry**

  A real commercial analytics case — anonymized and reproducible.

  [![Python](https://img.shields.io/badge/Python-3.13-1B4332?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.61-1B4332?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
  [![Polars](https://img.shields.io/badge/Polars-1.43-2C5F7C?style=flat-square)](https://pola.rs/)
  [![DuckDB](https://img.shields.io/badge/DuckDB-SQL-2C5F7C?style=flat-square&logo=duckdb&logoColor=white)](https://duckdb.org/)
  [![Plotly](https://img.shields.io/badge/Plotly-6.9-BC6C25?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)
</div>

---

## The problem

Commercial teams at agro-industrial companies often navigate disconnected spreadsheets, manual analyses, and decisions based on averages that hide the real picture. When information is fragmented, the commercial committee misses trends, fails to spot risks in time, and cannot prioritize actions with data.

The question this project answers: **how do you turn B2B sales transactional data into a daily decision-making instrument for a commercial team?**

## What this dashboard does

The dashboard structures commercial information across four interconnected views, plus a governance tab that documents the anonymization process:

| Tab | Question it answers |
|---|---|
| 📊 **01 · Sales by channel** | How are sales going and which channel is driving growth? |
| 🗺️ **02 · Regional dynamics** | Where does revenue come from and how is it distributed geographically? |
| 🚨 **03 · Alerts & risks** | Which customers are steadily reducing their purchases? |
| 📦 **04 · Portfolio** | Which customers buy only one species, and which are the strategic accounts? |
| 🛡️ **00 · Governance** | How was the data anonymized and which techniques were applied? |

### Design decisions

- **Price-neutral metrics in kilograms** for retention alerts (D03): a price change should never make a customer look like they are buying less when they are buying the same volume.
- **Retention traffic light with sustainability rule**: a single-month dip does not trigger an alert; the signal must hold for 2 consecutive months to be confirmed.
- **Golden rule for the B2B universe**: any transaction that does not match the target customer table is excluded from the analysis.

## Data governance

This project works with **k-anonymous derived data**, generated from a real case under a confidentiality agreement. The original information is never published.

Anonymization techniques applied (per the Methods Certificate):

- Aggregation / roll-up
- k-anonymity (k ≥ 5)
- Cell suppression for cells with < 10 contributors
- Category generalization
- Rounding and random perturbation

The full methodology is documented in [`build_public.py`](src/berrix/build_public.py).

> ⚠️ **Transparency note:** due to the size of the B2B base, some categories with few contributors are generalized or suppressed to guarantee k ≥ 5 and cells ≥ 10. The detailed per-customer analysis exists only at the local pseudonymized level, under the confidentiality agreement.

## Tech stack

| Tool | Role |
|---|---|
| **Python 3.13** | Base language |
| **DuckDB** | SQL engine for transformations |
| **Polars** | DataFrame manipulation |
| **Streamlit** | Dashboard framework |
| **Plotly** | Interactive visualizations |
| **uv** | Dependency manager |

## Project structure

```text
berries-dashboard/
├── src/
│   └── berrix/
│       ├── app_public.py       # Public Streamlit dashboard
│       ├── build_public.py     # Anonymization methodology
│       └── assets/
│           └── ag6.svg         # AG v6 logo
├── data/
│   └── public/                 # k-anonymous data only
│       ├── d01_*.parquet
│       ├── d02_*.parquet
│       ├── d03_*.parquet
│       └── d04_*.parquet
├── .streamlit/
│   └── config.toml             # AG brand identity
├── requirements.txt
└── README.md
```

## Local execution

```text
# Clone the repo
git clone https://github.com/ag-agrodata/berries-dashboard.git
cd berries-dashboard

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the dashboard
streamlit run src/berrix/app_public.py
```

## Live demo

[🌐 Streamlit Cloud](https://berries-dashboard-ztwjxjslwpatnh5kvgn9wd.streamlit.app/)

## License

This project is released under the MIT License. The included data are k-anonymous derivatives and contain no identifiable information about third parties.

<div align="center">
Built by Andrés Gómez · Agribusiness Data Analyst · 
"I turn the complexity of the field into data-driven decisions."
afgomez.agroindustrial@gmail.com
</div>