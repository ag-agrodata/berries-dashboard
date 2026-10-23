"""
i18n.py
Capa de internacionalización ES/EN del dashboard público Berrix.

Contiene:
- TEXT: diccionario de textos por idioma
- TECHNIQUES: tabla de técnicas de anonimización por idioma
- DISPLAY: mapas de categorías de negocio por idioma
- COLORS: paleta AG por familia de categoría
- detect_lang / lang_selector / t / tech_dataframe / map_col / color_map / disp
"""

from __future__ import annotations

import pandas as pd
import streamlit as st


# ============ TEXTOS POR IDIOMA ============
TEXT = {
	"es": {
		"page_title": "Tablero Comercial · Berrix (público)",
		"header_title": "Tablero Comercial · Berrix",
		"header_subtitle": "Datos públicos k-anónimos · Elaborado por Andrés Gómez · Analista de Datos Agroindustriales",
		"lang_label": "Idioma · Language",

		"tab0": "🛡️ 00 · Gobernanza",
		"tab1": "📊 01 · Ventas por canal",
		"tab2": "🗺️ 02 · Dinámica regional",
		"tab3": "🚨 03 · Alertas y riesgos",
		"tab4": "📦 04 · Portafolio",

		"gov_sub": "🛡️ Gobernanza de datos",
		"gov_caption": "Este tablero usa **datos públicos k-anónimos**, derivados de información comercial real mediante técnicas de anonimización conforme al acuerdo de confidencialidad.",
		"gov_m1_label": "Nivel público",
		"gov_m1_value": "K-anónimo",
		"gov_m2_label": "Umbral k",
		"gov_m2_value": "k ≥ 5",
		"gov_m3_label": "Supresión",
		"gov_m3_value": "Celdas < 10",
		"gov_m4_label": "Técnicas",
		"gov_m4_value": "5 aplicadas",
		"gov_tec_title": "### Técnicas de anonimización aplicadas",
		"gov_df_tec": "Técnica",
		"gov_df_app": "Aplicación",
		"gov_expander": "📜 Nota de transparencia",
		"gov_note": (
			"**Debido al tamaño de la base B2B (33 clientes), algunas categorías con pocos "
			"contribuyentes se generalizan o suprimen para garantizar k≥5 y celdas≥10.**\n\n"
			"Ejemplos de generalización aplicada:\n"
			"- **Canales:** Retail (8 clientes) se suprime en el nivel público; solo se muestran HORECA y Mayoristas.\n"
			"- **Regiones:** Las 7 regiones originales se agrupan en 'Centro' y 'Resto de regiones'.\n"
			"- **Cuentas nacionales:** Se diluyen en el grupo 'Resto de regiones' por k-anonimato.\n\n"
			"El análisis detallado por cliente individual está disponible únicamente en el nivel local "
			"pseudonimizado, conforme al acuerdo de confidencialidad."
		),

		"d01_sub": "📊 Ventas por canal (datos agregados)",
		"d01_caption": "Mezcla de canales comerciales y evolución temporal. Datos agregados por temporada para garantizar k-anonimato.",
		"d01_m1": "Venta neta B2B total",
		"d01_m2": "Canal líder",
		"d01_m3": "Canales visibles",
		"d01_m3_value": "{n} de 3",
		"d01_mix_title": "Mezcla de canales (agregado histórico)",
		"d01_axis_canal": "Canal",
		"d01_axis_venta": "Venta neta (COP)",
		"d01_info": "💡 **Nota:** Retail se suprime en el nivel público (8 clientes < umbral de 10). Solo se muestran los canales con ≥10 contribuyentes.",
		"d01_temp_title": "Evolución por temporada",
		"d01_axis_temp": "Temporada",

		"d02_sub": "🗺️ Dinámica regional (datos agregados)",
		"d02_caption": "Distribución geográfica generalizada en macro-regiones. Las cuentas nacionales se integran al grupo 'Resto de regiones' por k-anonimato.",
		"d02_m1": "Venta neta B2B total",
		"d02_m2": "Centro",
		"d02_m3": "Resto de regiones",
		"d02_donut_title": "Distribución Centro vs Resto",
		"d02_conc_title": "Concentración geográfica (participación del Centro)",
		"d02_conc_y": "% participación del Centro",
		"d02_info": "💡 **Nota:** La categoría 'Nacional' (3 clientes) se agrupa en 'Resto de regiones' para garantizar k-anonimato. El análisis detallado por región fina está disponible en el nivel local pseudonimizado.",

		"d03_sub": "🚨 Alertas y riesgos (datos agregados)",
		"d03_caption": "Semáforo de retención basado en volumen (kg). Datos agregados por nivel de riesgo, sin detalle por cliente individual.",
		"d03_m1": "🔴 Alto riesgo",
		"d03_m2": "🟡 Riesgo medio",
		"d03_m3": "🟢 Estables",
		"d03_m4": "📦 Kg en riesgo",
		"d03_clientes": "{n} clientes",
		"d03_kg": "{kg} kg",
		"d03_evo_title": "Evolución del semáforo (últimos períodos)",
		"d03_axis_periodo": "Período",
		"d03_axis_n": "Número de clientes",
		"d03_axis_nivel": "Nivel de riesgo",
		"d03_table_title": "Totales por nivel de riesgo",
		"d03_col_nivel": "Nivel de riesgo",
		"d03_col_clientes": "Clientes",
		"d03_col_kg": "Kg en riesgo",
		"d03_expander": "Supuestos y gobernanza",
		"d03_note": (
			"- **Métrica:** Kilogramos (precio-neutral para evitar falsos positivos por volatilidad).\n"
			"- **Línea base:** Promedio móvil de los 3 meses calendario anteriores por cliente.\n"
			"- **Sostenibilidad:** El color solo se confirma si la caída se repite 2 meses consecutivos.\n"
			"- **Niveles:**\n"
			"  - 🟢 Estable: caída <15% o no sostenida\n"
			"  - 🟡 Riesgo medio: caída ≥15% y <30%, sostenida 2 meses\n"
			"  - 🔴 Alto riesgo: caída ≥30%, sostenida 2 meses\n\n"
			"**Nota:** El semáforo por cliente individual no se publica por k-anonimato. "
			"Solo se muestran agregados por nivel de riesgo."
		),

		"d04_sub": "📦 Portafolio (datos agregados)",
		"d04_caption": "Análisis estratégico de la base B2B: concentración y Pareto. Datos agregados por tipo de cliente, sin detalle individual.",
		"d04_m1": "Total clientes",
		"d04_m2": "Cautivos",
		"d04_m3": "Alto valor",
		"d04_m4": "Pareto",
		"d04_pct": "{n} ({p}%)",
		"d04_donut_title": "Distribución por concentración",
		"d04_axis_conc": "Concentración",
		"d04_axis_clientes": "Clientes",
		"d04_global_title": "Métricas globales",
		"d04_g1": "Venta total B2B",
		"d04_g2": "Venta en cautivos",
		"d04_g2_delta": "{p}% del total",
		"d04_g3": "Clientes para 80% de venta",
		"d04_g3_value": "{a} de {b}",
		"d04_g4": "Concentración Pareto",
		"d04_expander": "Supuestos y gobernanza",
		"d04_note": (
			"- **Umbral de cautividad:** ≥80% del volumen en la especie dominante.\n"
			"- **Pareto:** Clientes que acumulan el 80% de la venta neta B2B.\n"
			"- **Actividad mínima:** Clientes con ≥2 meses de compra.\n\n"
			"**Nota:** La matriz de portafolio por cliente individual no se publica por k-anonimato. "
			"Solo se muestran agregados por tipo de concentración y métricas globales."
		),
	},

	"en": {
		"page_title": "Commercial Dashboard · Berrix (public)",
		"header_title": "Commercial Dashboard · Berrix",
		"header_subtitle": "k-anonymous public data · Built by Andrés Gómez · Agribusiness Data Analyst",
		"lang_label": "Idioma · Language",

		"tab0": "🛡️ 00 · Governance",
		"tab1": "📊 01 · Sales by channel",
		"tab2": "🗺️ 02 · Regional dynamics",
		"tab3": "🚨 03 · Alerts & risks",
		"tab4": "📦 04 · Portfolio",

		"gov_sub": "🛡️ Data governance",
		"gov_caption": "This dashboard uses **k-anonymous public data**, derived from real commercial information through anonymization techniques compliant with the confidentiality agreement.",
		"gov_m1_label": "Public level",
		"gov_m1_value": "k-anonymous",
		"gov_m2_label": "k threshold",
		"gov_m2_value": "k ≥ 5",
		"gov_m3_label": "Suppression",
		"gov_m3_value": "Cells < 10",
		"gov_m4_label": "Techniques",
		"gov_m4_value": "5 applied",
		"gov_tec_title": "### Anonymization techniques applied",
		"gov_df_tec": "Technique",
		"gov_df_app": "Application",
		"gov_expander": "📜 Transparency note",
		"gov_note": (
			"**Due to the size of the B2B base (33 customers), some categories with few contributors "
			"are generalized or suppressed to guarantee k≥5 and cells≥10.**\n\n"
			"Examples of applied generalization:\n"
			"- **Channels:** Retail (8 customers) is suppressed at the public level; only HORECA and Wholesalers are shown.\n"
			"- **Regions:** The 7 original regions are grouped into 'Central' and 'Other regions'.\n"
			"- **National accounts:** Diluted into the 'Other regions' group for k-anonymity.\n\n"
			"Detailed per-customer analysis is available only at the local pseudonymized level, "
			"under the confidentiality agreement."
		),

		"d01_sub": "📊 Sales by channel (aggregated data)",
		"d01_caption": "Commercial channel mix and time evolution. Data aggregated by season to guarantee k-anonymity.",
		"d01_m1": "Total B2B net sales",
		"d01_m2": "Leading channel",
		"d01_m3": "Visible channels",
		"d01_m3_value": "{n} of 5",
		"d01_mix_title": "Channel mix (historical aggregate)",
		"d01_axis_canal": "Channel",
		"d01_axis_venta": "Net sales (COP)",
		"d01_info": "💡 **Note:** Retail is suppressed at the public level (8 customers < threshold of 10). Only channels with ≥10 contributors are shown.",
		"d01_temp_title": "Evolution by season",
		"d01_axis_temp": "Season",

		"d02_sub": "🗺️ Regional dynamics (aggregated data)",
		"d02_caption": "Geographic distribution generalized into macro-regions. National accounts are integrated into the 'Other regions' group for k-anonymity.",
		"d02_m1": "Total B2B net sales",
		"d02_m2": "Central",
		"d02_m3": "Other regions",
		"d02_donut_title": "Central vs Other regions distribution",
		"d02_conc_title": "Geographic concentration (Central share)",
		"d02_conc_y": "Central share %",
		"d02_info": "💡 **Note:** The 'National' category (3 customers) is grouped into 'Other regions' to guarantee k-anonymity. Detailed fine-region analysis is available at the local pseudonymized level.",

		"d03_sub": "🚨 Alerts & risks (aggregated data)",
		"d03_caption": "Retention traffic light based on volume (kg). Data aggregated by risk level, without per-customer detail.",
		"d03_m1": "🔴 High risk",
		"d03_m2": "🟡 Medium risk",
		"d03_m3": "🟢 Stable",
		"d03_m4": "📦 Kg at risk",
		"d03_clientes": "{n} customers",
		"d03_kg": "{kg} kg",
		"d03_evo_title": "Traffic-light evolution (recent periods)",
		"d03_axis_periodo": "Period",
		"d03_axis_n": "Number of customers",
		"d03_axis_nivel": "Risk level",
		"d03_table_title": "Totals by risk level",
		"d03_col_nivel": "Risk level",
		"d03_col_clientes": "Customers",
		"d03_col_kg": "Kg at risk",
		"d03_expander": "Assumptions and governance",
		"d03_note": (
			"- **Metric:** Kilograms (price-neutral to avoid false positives from price volatility).\n"
			"- **Baseline:** Moving average of the previous 3 calendar months per customer.\n"
			"- **Sustainability:** A color is confirmed only if the drop repeats for 2 consecutive months.\n"
			"- **Levels:**\n"
			"  - 🟢 Stable: drop <15% or not sustained\n"
			"  - 🟡 Medium risk: drop ≥15% and <30%, sustained for 2 months\n"
			"  - 🔴 High risk: drop ≥30%, sustained for 2 months\n\n"
			"**Note:** The per-customer traffic light is not published due to k-anonymity. "
			"Only aggregates by risk level are shown."
		),

		"d04_sub": "📦 Portfolio (aggregated data)",
		"d04_caption": "Strategic analysis of the B2B base: concentration and Pareto. Data aggregated by customer type, without individual detail.",
		"d04_m1": "Total customers",
		"d04_m2": "Captive",
		"d04_m3": "High value",
		"d04_m4": "Pareto",
		"d04_pct": "{n} ({p}%)",
		"d04_donut_title": "Distribution by concentration",
		"d04_axis_conc": "Concentration",
		"d04_axis_clientes": "Customers",
		"d04_global_title": "Global metrics",
		"d04_g1": "Total B2B sales",
		"d04_g2": "Sales from captive customers",
		"d04_g2_delta": "{p}% of total",
		"d04_g3": "Customers driving 80% of sales",
		"d04_g3_value": "{a} of {b}",
		"d04_g4": "Pareto concentration",
		"d04_expander": "Assumptions and governance",
		"d04_note": (
			"- **Captivity threshold:** ≥80% of volume in the dominant species.\n"
			"- **Pareto:** Customers that accumulate 80% of B2B net sales.\n"
			"- **Minimum activity:** Customers with ≥2 months of purchases.\n\n"
			"**Note:** The per-customer portfolio matrix is not published due to k-anonymity. "
			"Only aggregates by concentration type and global metrics are shown."
		),
	},
}


# ============ TÉCNICAS DE ANONIMIZACIÓN (tabla de Gobernanza) ============
TECHNIQUES = {
	"es": {
		"names": [
			"Agregación / totalización",
			"k-anonimato (k ≥ 5)",
			"Supresión de celdas",
			"Generalización de categorías",
			"Redondeo y perturbación",
		],
		"descs": [
			"Sumar registros individuales en grupos",
			"Cada grupo tiene al menos 5 contribuyentes",
			"Celdas con <10 contribuyentes se ocultan",
			"Reducir granularidad (ej. macro-regiones)",
			"Añadir ruido controlado a valores",
		],
	},
	"en": {
		"names": [
			"Aggregation / roll-up",
			"k-anonymity (k ≥ 5)",
			"Cell suppression",
			"Category generalization",
			"Rounding and perturbation",
		],
		"descs": [
			"Sum individual records into groups",
			"Every group holds at least 5 contributors",
			"Cells with <10 contributors are hidden",
			"Reduce granularity (e.g., macro-regions)",
			"Add controlled noise to values",
		],
	},
}


# ============ MAPAS DE DISPLAY POR FAMILIA ============
DISPLAY = {
	"es": {
		"canal": {},
		"macro_region": {},
		"nivel_riesgo": {
			"alto_riesgo": "Alto riesgo",
			"riesgo_medio": "Riesgo medio",
			"estable": "Estable",
		},
		"concentracion": {},
	},
	"en": {
		"canal": {
			"Food Service - HORECA": "Food Service - HORECA",
			"Mayoristas": "Wholesalers",
			"Retail": "Retail",
		},
		"macro_region": {
			"Centro": "Central",
			"Resto de regiones": "Other regions",
		},
		"nivel_riesgo": {
			"alto_riesgo": "High risk",
			"riesgo_medio": "Medium risk",
			"estable": "Stable",
		},
		"concentracion": {
			"Cautivo": "Captive",
			"Diversificado": "Diversified",
		},
	},
}


# ============ PALETA AG POR FAMILIA (clave = valor ES) ============
COLORS = {
	"canal": {
		"Food Service - HORECA": "#1B4332",
		"Mayoristas": "#2C5F7C",
		"Retail": "#D8B25C",
	},
	"macro_region": {
		"Centro": "#1B4332",
		"Resto de regiones": "#D8B25C",
	},
	"nivel_riesgo": {
		"alto_riesgo": "#BC6C25",
		"riesgo_medio": "#E9C46A",
		"estable": "#1B4332",
	},
	"concentracion": {
		"Cautivo": "#1B4332",
		"Diversificado": "#D8B25C",
	},
}


# ============ HELPERS ============
def detect_lang() -> str:
	"""Fija el idioma inicial según el locale del navegador (default: es)."""
	if "lang" not in st.session_state:
		locale = ""
		try:
			locale = st.context.locale or ""
		except Exception:
			locale = ""
		st.session_state.lang = "en" if locale.lower().startswith("en") else "es"
	return st.session_state.lang


def lang_selector() -> str:
	"""Renderiza el selector ES/EN y devuelve el idioma activo."""
	st.radio(
		TEXT["es"]["lang_label"],
		["es", "en"],
		format_func=lambda c: "🇪 Español" if c == "es" else "🇬🇧 English",
		horizontal=True,
		key="lang",
		label_visibility="collapsed",
	)
	return st.session_state.lang


def t(key: str, **kwargs) -> str:
	"""Devuelve el texto de la clave en el idioma activo, con formato opcional."""
	lang = st.session_state.get("lang", "es")
	value = TEXT.get(lang, {}).get(key, TEXT["es"].get(key, key))
	if kwargs:
		value = value.format(**kwargs)
	return value


def disp(value: str, family: str) -> str:
	"""Mapea un valor de dato al display del idioma activo."""
	lang = st.session_state.get("lang", "es")
	return DISPLAY.get(lang, {}).get(family, {}).get(value, value)


def map_col(pdf: pd.DataFrame, column: str, family: str) -> pd.DataFrame:
	"""Devuelve una copia del DataFrame con la columna mapeada al idioma activo."""
	lang = st.session_state.get("lang", "es")
	mapping = DISPLAY.get(lang, {}).get(family, {})
	if not mapping:
		return pdf
	out = pdf.copy()
	out[column] = out[column].map(lambda v: mapping.get(v, v))
	return out


def color_map(family: str) -> dict:
	"""Paleta AG con claves en el display del idioma activo."""
	return {disp(k, family): v for k, v in COLORS.get(family, {}).items()}


def tech_dataframe() -> pd.DataFrame:
	"""Tabla de técnicas de anonimización en el idioma activo."""
	lang = st.session_state.get("lang", "es")
	tech = TECHNIQUES.get(lang, TECHNIQUES["es"])
	return pd.DataFrame({
		t("gov_df_tec"): tech["names"],
		t("gov_df_app"): tech["descs"],
	})
