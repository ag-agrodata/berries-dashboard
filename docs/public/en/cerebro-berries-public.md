# Project brain · berries-dashboard

**Public version** · October 21, 2026  
**Author:** Andrés Gómez · Agribusiness Data Analyst  
**Repository:** `github.com/ag-agrodata/berries-dashboard`

This document is the register of decisions, assumptions, glossary, and limitations of the B2B commercial dashboard. Its purpose is to let any reviewer audit the reasoning behind the dashboard without needing to read the code or access the original data.

---

## 1. Purpose and scope

**What it is:** a dashboard that translates B2B sales transactions from a berry agro-industrial company into four decision questions for a commercial committee: sales by channel, regional dynamics, retention alerts, and customer portfolio.

**What it is not:** it is not a transactional system, does not replace the ERP, does not produce forecasts, does not recommend prices. It is a reading layer over already-consolidated data.

**Public dataset scope:** 33 B2B customers, 3 commercial channels (after suppression), 2 macro-regions, multiple seasons. The exact customer count is published for scale purposes; it does not identify individual customers or reveal the portfolio structure. The data are k-anonymous derivatives of the real case, published under the NDA with the client (see [`LICENSE-DATA`](LICENSE-DATA)).

**Project phases:** the case went through four phases before arriving here (working with the company → Excel + Tableau delivery → Streamlit replication → anonymization and publication). The full story is in the "The four phases of the project" section of the READMEs. That chain is part of the value of the case and must not be lost in the internal documentation.

---

## 2. Data sources and pipeline

**Original source:** the company's spreadsheets with orders, dispatches, sales reports, and billing. Consolidated locally into `data/processed/anon/ventas_local.parquet` and `clientes_local.parquet` (pseudonymized).

**Public pipeline:** `src/berrix/build_public.py` generates the 8 files in `data/public/` from the local pseudonymized data, applying the anonymization techniques of section 3.

**Consumption in the app:** `src/berrix/app_public.py` loads the 8 parquet files with Polars and renders them with Streamlit + Plotly. The ES/EN bilingual layer is in `src/berrix/i18n.py`.

**Update frequency:** the public dataset is a static snapshot of the case; it is not refreshed automatically. The internal version (not published) is updated with real operations.

---

## 3. Decision register (D01–D14)

Each decision is justified. Those without quantitative evidence say so explicitly and refer to section 6 (limitations).

### D01 · Price-neutral metrics in kilograms for retention alerts

**Decision:** the traffic light alerts (tab 03) are computed in kilograms, not in currency.  
**Justification:** a price change must not make a customer look like they are buying less when they are buying the same volume. Using monetary value would trigger false churn alerts due to price variation.  
**Impact:** eliminates a classic bias in retention alerts. It is the most cited decision of the project.

### D02 · Retention traffic light with a sustainability rule

**Decision:** a single-month drop does not trigger an alert. **Two consecutive months** are required to confirm a trend.  
**Justification:** the monthly seasonality of the berry business produces single-month drops that are not churn signals. Windows of 1, 2 and 3 months were tested: one fired noise, three arrived late to the committee.  
**Evidence:** operational, not a formal backtest (see limitation L01).

### D03 · Golden rule of the B2B universe

**Decision:** any transaction that does not match the target customer table is excluded from the analysis. It is not imputed or approximated.  
**Justification:** keep the universe clean and avoid contamination with non-attributable transactions (counter sales, returns without customer, internal movements).  
**Impact:** reduces analysis noise and makes every dashboard figure defensible.

### D04 · Visible channels only with ≥10 contributors

**Decision:** the Retail channel (8 customers) is suppressed at the public level. Only Food Service-HORECA and Wholesalers are shown.  
**Justification:** cells with < 10 contributors violate the `CELL_MIN = 10` threshold of the NDA.  
**Impact:** the public channel analysis is incomplete by design; the full analysis exists at the local pseudonymized level.

### D05 · Regions generalized to macro-regions

**Decision:** the 7 original regions are grouped into 2 macro-regions: "Central" (Bogotá + Sabana) and "Other regions".  
**Justification:** several original regions had < 10 customers; grouping them guarantees k ≥ 5 and cells ≥ 10.  
**Impact:** fine regional granularity is lost. View D02 shows only Central vs Other concentration.

### D06 · National accounts diluted into "Other regions"

**Decision:** the 3 customers with national coverage are grouped into "Other regions".  
**Justification:** a "National" category with 3 customers would be singularizable.  
**Impact:** consistent with D05; reinforces protection of atypical customers.

### D07 · Pareto as a generalized percentile ratio

**Decision:** the Pareto index is not published as an exact number, but as a bucket: `≤10%`, `10-20%`, `20-30%`, `>30%`.  
**Justification:** publishing the exact number of "customers concentrating 80% of sales" would allow inferring the base distribution.  
**Impact:** the qualitative reading (how concentrated the base is) is preserved without exposing the fine data.

### D08 · D04 aggregated by concentration, not customer matrix

**Decision:** the portfolio view (tab 04) shows aggregates by concentration type (Captive / Diversified) and global metrics, not the customer × species matrix.  
**Justification:** the per-customer matrix would identify individual customers.  
**Impact:** the committee loses the operational view of individual accounts; it gains NDA protection.

### D09 · Captivity threshold

**Decision:** a customer is "Captive" if ≥ 80% of their volume is in a single species.  
**Justification:** operational criterion of the commercial committee. It is a defensible threshold of mono-dependence.  
**Evidence:** business criterion, not statistical.

### D10 · Minimum customer activity

**Decision:** a customer is considered active if they have ≥ 2 months of purchases in the analyzed window.  
**Justification:** customers with a single purchase produce unstable metrics (retention, Pareto, average).  
**Impact:** reduces the universe to customers with sufficient signal.

### D11 · Alert baseline

**Decision:** retention drop is measured against the moving average of the previous 3 calendar months.  
**Justification:** smooths weekly and monthly seasonality without losing sensitivity to trends.  
**Evidence:** operational criterion.

### D12 · Risk level thresholds

**Decision:**
- 🟢 Stable: drop < 15% or not sustained
- 🟡 Medium risk: drop ≥ 15% and < 30%, sustained for 2 months
- 🔴 High risk: drop ≥ 30%, sustained for 2 months

**Justification:** operational calibration of the commercial committee. No formal backtest.  
**Impact:** the traffic light discriminates three urgency levels without drowning the committee in alerts.

### D13 · Anonymization parameters

**Decision:** `K_MIN = 5`, `CELL_MIN = 10` in `build_public.py`.  
**Justification:** thresholds defined in Annex A of the NDA.  
**Impact:** every published cell meets both thresholds by construction.

### D14 · Commercial universe filter

**Decision:** the universe is filtered to net commercial sales transactions, excluding documents that do not represent sales (internal movements, accounting returns) and channels outside the target B2B universe.  
**Justification:** internal movements and returns do not represent net commercial sales; their inclusion would distort the analysis.
**Impact:** the dashboard measures net commercial sales, not gross accounting movement.

---

## 4. Assumption register (S01–S09)

| ID | Assumption | Implication if it fails |
|---|---|---|
| S01 | The local pseudonymized data are representative of the real business | The analysis would be an artifact without operational value |
| S02 | Season is the main time unit of the berry business | Switching to month-year would alter views D01/D02 |
| S03 | Calendar month is the appropriate unit for retention alerts | Switching to week would increase noise; to quarter, the latency |
| S04 | Risk thresholds (15%, 30%) are aligned with the client's commercial policy | A different threshold would change the distribution of levels |
| S05 | A 2-month window is the minimum acceptable operational threshold to confirm a trend | Without a formal backtest, it is a business criterion |
| S06 | Commercial channel is the relevant axis for reading sales | If the client prioritizes species or region, view D01 loses relevance |
| S07 | Grouping Bogotá + Sabana into "Central" is an acceptable generalization | If commercial dynamics differ between them, the macro-region hides signal |
| S08 | Pareto is computed on net sales, not on kg | Changing the metric would alter the resulting bucket |
| S09 | A customer with ≥ 2 months of purchase is "active" | If the purchase cycle is longer, the threshold underestimates the active base |

---

## 5. Operational glossary

- **Net sales (COP/USD):** sales after discounts, without returns or internal movements.
- **kg:** kilograms of product sold. Price-neutral metric.
- **Commercial channel:** customer segment (Food Service-HORECA, Wholesalers, Retail).
- **Macro-region:** geographic grouping (Central, Other regions). Replaces the 7 original regions.
- **Season:** time unit of the business (per harvest calendar).
- **Risk level:** retention traffic light classification (high, medium, stable).
- **Captive:** customer with ≥ 80% of their volume in a single species.
- **Diversified:** customer with volume spread across ≥ 2 species.
- **Pareto (bucket):** concentration of sales in the customer top, expressed as a range (≤10%, 10-20%, etc.).
- **k-anonymity:** property by which each published cell has at least k contributors (here k ≥ 5).
- **Cell suppression:** eliminating cells with < 10 contributors to avoid singularization.
- **Generalization:** reducing the granularity of a category (e.g., 7 regions → 2 macro-regions).

---

## 6. Known limitations

### L01 · No formal backtest of the retention window

The 2-month window (D02) is an operational criterion. A historical backtest on real data would allow calibrating the sensitivity/latency trade-off. It is pending work.

### L02 · Residual re-identification risk

The report [`data/public/validacion.txt`](data/public/validacion.txt) documents the status of the 5 standard attacks and the price-reconstruction test. Any residual risk is stated there and must be read before interpreting the anonymization guarantee as absolute.

### L03 · Incomplete channel analysis at the public level

Retail (8 customers) is suppressed by D04. The public analysis covers only 2 of the 3 commercial channels. The full reading exists at the local pseudonymized level.

### L04 · Reduced regional granularity

The 7 original regions collapse into 2 macro-regions (D05). The public analysis does not distinguish Bogotá from Sabana, nor the regions of "Other".

### L05 · Pareto generalized to buckets

The Pareto index is published as a range (D07), not as a number. The fine quantitative reading is not available at the public level.

### L06 · No margin or cost information

The dataset contains only net sales and kg. There is no cost, margin, or profitability. The analysis is of commercial volume and mix, not of profitability.

### L07 · No price information

By express condition of the NDA, no prices, margins, or contractual terms are published. The public dataset does not allow reconstructing unit prices (verified by `tools/validacion_precio.py`).

---

## 7. Governance and validation

- **Parameters:** `K_MIN = 5`, `CELL_MIN = 10` (D13).
- **Techniques applied:** aggregation, k-anonymity, cell suppression, generalization, rounding, and perturbation.
- **Validation report:** [`data/public/validacion.txt`](data/public/validacion.txt).
- **Verification tools:** [`tools/validacion_precio.py`](tools/validacion_precio.py) (price-reconstruction test) and [`tools/validacion_anonimizacion.py`](tools/validacion_anonimizacion.py) (full 5-attack suite).
- **Data license:** [`LICENSE-DATA`](LICENSE-DATA) (DUA).
- **Legal framework:** NDA with the client. Publication of derivatives was authorized under the condition of non-identifiability and non-price-inference. The full NDA is kept in the consultant's private archive; the destruction of original bases and identifiable products was documented under clause 6 of the NDA, and the Annex B record is kept in the private archive.

---

## 8. Public roadmap

Pending work, in order of priority:

1. **Run and publish the full validation report** (`data/public/validacion.txt`) with the 5 standard attacks and the price test.
2. **Formal backtest of the retention window** (L01): test windows of 1, 2, 3 and 4 months on history and measure the detection precision of real churn.
3. **Data dictionary** (`data/public/README.md`): schema of each parquet, columns, types, and coverage.
4. **Add the price test to `validacion.txt`** once the full report exists.
5. **Synthetic version of the dataset** for analysis without NDA: same schema, generated data, zero link to the client.
6. **Extend the portfolio view** with a species-mix reading (without identifying customers), if the NDA allows.

---

## 9. Contact

**Andrés Gómez**  
Agribusiness Data Analyst  
afgomez.agroindustrial@gmail.com  
[github.com/ag-agrodata](https://github.com/ag-agrodata)

For questions about decisions, assumptions, or limitations of this document, or to report a possible breach of the confidentiality agreement, write to the email above.
