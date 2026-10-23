[🇬🇧 English](README.md) · [🇪🇸 Español](README.es.md)

<div align="center">

<img src="src/berrix/assets/ag6.svg" alt="AG · Andrés Gómez/Agrodata" width="180"/>

# 🎛️ Commercial Dashboard · Berrix
### Public Release

**B2B sales analytics for the berry agribusiness**

A real commercial analytics case — anonymized and reproducible.

[![Python](https://img.shields.io/badge/Python-3.13-1B4332?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.61-1B4332?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) [![Polars](https://img.shields.io/badge/Polars-1.43-2C5F7C?style=flat-square)](https://pola.rs/) [![DuckDB](https://img.shields.io/badge/DuckDB-SQL-2C5F7C?style=flat-square&logo=duckdb&logoColor=white)](https://duckdb.org/) [![Plotly](https://img.shields.io/badge/Plotly-6.9-BC6C25?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)

[🚀 Live Demo](https://berries-dashboard-ztwjxjslwpatnh5kvgn9wd.streamlit.app/) · [📖 Docs](docs/public/) · [📊 Internal Spec](docs/public/cerebro-berries-public.md)

*Elaborated by **Andrés Gómez** · Agribusiness Data Analyst*

</div>

---

## 2-minute summary

A dashboard that turns B2B sales transactions into four decision questions for an agribusiness commercial committee: how sales are trending by channel, where revenue comes from by region, which customers are steadily reducing purchases, and which accounts buy only one species. Built on real anonymized data (33 B2B customers, k ≥ 5), with a public demo and a documented anonymization methodology.

> **Disclaimer:** The exact customer count is published for scale purposes; it does not identify individual customers or reveal the portfolio structure.

## The problem

Commercial teams at agribusiness companies often navigate disconnected spreadsheets, manual analyses, and decisions based on averages that hide the real picture. When information is fragmented, the commercial committee misses trends, fails to spot risks in time, and cannot prioritize actions with data.

The question this project answers: **how do you turn B2B sales transactional data into a daily decision-making instrument for a commercial team?**

## The four phases of the project

This project did not start as a public dashboard. It started as a real engagement inside an agribusiness company, and went through four phases before becoming the reproducible case you are reading.

| Phase | What happened | Deliverable |
|---|---|---|
| **1 · Working with the company** | Review of the spreadsheets behind orders, dispatches, sales reports and billing. Understanding of the real commercial flow and the questions the committee needed to answer. | Data model and decision questions |
| **2 · Corporate delivery** | The company's corporate framework was **Excel + Tableau**. The original delivery was built in that stack. The company is migrating to **SAP**; an Excel-to-SAP migration is projected to ensure continuity, but **it was not part of this phase**. | Tableau dashboard |
| **3 · Streamlit replication** | The Tableau project was replicated as a functional **Streamlit** app (Python, Polars, DuckDB, Plotly), with the same data model and the same decision questions. | Internal Streamlit app |
| **4 · Anonymization and publication** | A **k-anonymous** version (k ≥ 5, cell suppression < 10, generalization, rounding and perturbation) was derived from the replicated project so it could be published without exposing confidential information. | This public repository |

**Why this history matters:** it shows the project is not an academic exercise. It was born from a real problem, delivered in the stack the company already used, replicated in a reproducible stack, and anonymized with verifiable standards. That chain —company → Tableau → Streamlit → public— is part of the value of the case.

## What this dashboard does

The dashboard structures commercial information across four interconnected views, plus a governance tab that documents the anonymization process:

| Tab | Question it answers |
|---|---|
| 📊 **01 · Sales by channel** | How are sales going and which channel is driving growth? |
| 🗺️ **02 · Regional dynamics** | Where does revenue come from and how is it distributed geographically? |
| 🚨 **03 · Alerts & risks** | Which customers are steadily reducing their purchases? |
| 📦 **04 · Portfolio** | Which customers buy only one species, and which are the strategic accounts? |
| 🛡️ **00 · Governance** | How was the data anonymized and which techniques were applied? |

## What this project demonstrates

- **Covering the full lifecycle of a data project:** from working with the company and reviewing its spreadsheets, through delivery in the corporate stack (Excel + Tableau), replication in a reproducible stack (Streamlit), and anonymization for publication.
- **Translating a diffuse commercial problem into measurable decision questions:** every view answers a specific committee question.
- **Choosing metrics that avoid bias:** kilograms instead of currency so a price change does not look like a drop in purchase.
- **Designing rules that reduce false positives:** retention traffic light with two consecutive months, not one.
- **Defining a defensible analytical universe:** B2B golden rule, excluding transactions without a match in the target customer table.
- **Anonymizing without destroying signal:** k-anonymity, suppression, generalization, rounding and perturbation.
- **Building for a meeting, not for a report:** four views plus governance, live demo.

## Design decisions

### 1 · Price-neutral metrics in kilograms for alerts

A price change should never make a customer look like they are buying less when they are buying the same volume. That is why retention alerts are computed in kilograms, not in currency. Using monetary value, a price drop could trigger a false churn alert.

### 2 · Retention traffic light with a sustainability rule

A single-month dip does not trigger an alert: **two consecutive months** are required to confirm a trend. Two months is the minimum that removes most false positives from monthly seasonality without delaying the alert more than one week of commercial planning. One-month and three-month windows were tested: one fired noise, three arrived late to the committee.

### 3 · Golden rule for the B2B universe

Any transaction that does not match the target customer table is excluded from the analysis. It is not imputed or approximated: it is excluded. This keeps the universe clean and prevents the analysis from being contaminated by non-attributable transactions.

## Recommendations and impact

> **Transparency note:** the figures in this section are estimates under NDA. Exact figures are confidential; ranges are presented to give scale to the case and must be validated before being used in a presentation.

### 1 · Activate a retention plan for at-risk accounts

The retention traffic light identifies customers with a sustained purchase decline over two consecutive months. The operational recommendation is for the commercial committee to review those accounts in the same session and assign a contact owner before the decline consolidates over the quarter. The estimated impact depends on the value of the retained account: an account with an annual contract in the [X–Y] range represents preserved revenue if action is taken in time.

### 2 · Prioritize cross-selling to single-species customers

The portfolio view identifies customers who buy only one species. The recommendation is to prioritize a second-species offer to accounts with the highest volume and lowest diversification, with a target of [X]% penetration in [Y] months.

### 3 · Review commercial coverage by region

The regional dynamics view shows revenue concentration. The recommendation is to review whether commercial effort is aligned with revenue distribution and adjust coverage in regions with the highest uncaptured potential.

## Data governance

This project works with **k-anonymous derived data**, generated from a real case of **33 B2B customers** under a confidentiality agreement. The original information is never published.

Anonymization techniques applied (per the Methods Certificate):

- Aggregation / roll-up
- k-anonymity (k ≥ 5)
- Cell suppression for cells with < 10 contributors
- Category generalization
- Rounding and random perturbation

The full methodology is documented in [`build_public.py`](src/berrix/build_public.py).

> ⚠️ **Transparency note:** due to the size of the B2B base (33 customers), some categories with few contributors are generalized or suppressed to guarantee k ≥ 5 and cells ≥ 10. The detailed per-customer analysis exists only at the local pseudonymized level, under the confidentiality agreement.

## Companion project: End-to-End Agribusiness Analytics

This case is complemented by [cosecha-public](https://github.com/ag-agrodata/cosecha-public), a prescriptive harvest planner for blueberries: the other end of the agribusiness value chain. While this dashboard looks at the commercial committee, `cosecha-public` looks at harvest operations, headcount and cost.

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
│       ├── app_public.py                           # Public Streamlit dashboard
│       ├── build_public.py                         # Anonymization methodology
│       ├── i18n.py                                 # ES/EN copy and display maps
│       └── assets/
│           └── ag6.svg                             # AG v6 logo
├── data/
│   └── public/                                     # k-anonymous data only (8 parquet tables)
│       ├── d01_canal_publico.parquet
│       ├── d01_temporada_publico.parquet
│       ├── d02_concentracion_publico.parquet
│       ├── d02_macro_region_publico.parquet
│       ├── d03_alertas_publico.parquet
│       ├── d03_alertas_total_publico.parquet
│       ├── d04_portafolio_publico.parquet
│       └── d04_portafolio_global_publico.parquet
├── tools/
│   ├── validacion_anonimizacion.py
│   └── README.md
├── docs/
│   ├── legal
│   │   └── riesgos-aceptados.md
│   └── public/
│       ├── cerebro-berries-public.md
│       ├── guia-tablero-public.html
│       └── en/
│           ├── cerebro-berries-public.md
│           └── guia-tablero-public.html
├── .streamlit/
│   └── config.toml                                  # AG brand identity
├── uv.lock
├── pyproject.toml
├── requirements.txt
├── LICENSE
├── LICENSE-DATA
└── README.md
```
> 👨🏻‍💻 **Technical note:** `berrix` is the internal package name (a contraction of berries + *analytics) that houses the analytical engine and forecasting modules for this project suite. It is kept as a namespace to maintain architectural coherence with the companion repository (cosecha-public).

## Local execution

### Option A · uv (recommended)

```
# Clone the repo
git clone https://github.com/ag-agrodata/berries-dashboard.git
cd berries-dashboard

# Sync and install dependencies
uv sync

# Run the dashboard
uv run streamlit run src/berrix/app_public.py
```

### Option B · pip
```
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

Open `http://localhost:8501`. The toggle **ES | EN** is at the top-right of the dashboard.

## Live demo

[🌐 Streamlit Cloud](https://berries-dashboard-ztwjxjslwpatnh5kvgn9wd.streamlit.app/)

## License

This project uses a layered license:

- **Code** (`src/`, `.streamlit/`, `requirements.txt`): [MIT](LICENSE).
- **Data** (`data/public/`): [Data Use Agreement](LICENSE-DATA) — non-commercial, no re-identification, no price inference, attribution required.
- **Documentation** (`docs/`, READMEs): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

> ⚠️ k-anonymized datasets are published for demonstration purposes, in accordance with the confidentiality agreement with the client. Any attempt to re-identify clients, individuals, or transactions, or to infer prices, margins, or contractual terms, is expressly prohibited. See [LICENSE-DATA](LICENSE-DATA) for the full terms.

---

<div align="center">

**Andrés Gómez**<br/>
Agribusiness Data Analyst<br/>

[🌐 Portfolio](https://github.com/ag-agrodata) · [📧 Contact](mailto:afgomez.agroindustrial@gmail.com)

</div>
