import streamlit as st
import polars as pl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path

from i18n import t, detect_lang, lang_selector, tech_dataframe, map_col, color_map

# ============ RUTAS Y LOGO ============
ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT / "data" / "public"
AG6_PATH = Path(__file__).resolve().parent / "assets" / "ag6.svg"

# Idioma inicial según locale del navegador (antes de set_page_config)
LANG = detect_lang()

st.set_page_config(
	page_title=t("page_title"),
	layout="wide",
	page_icon=str(AG6_PATH) if AG6_PATH.exists() else "🫐"
)

# ============ IDENTIDAD DE MARCA AG ============
st.markdown(
	"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
	html, body, [class*="css"], button, input, select, textarea {
		font-family: 'Inter', sans-serif;
	}
	h1, h2, h3, h4, h5, h6 {
		font-family: 'Sora', sans-serif !important;
		color: #1B4332;
		letter-spacing: -0.02em;
	}
	h1 { font-weight: 800; }
	.stCaption, p { color: #2c5b48; }

	[data-testid="stMetric"] {
		background: linear-gradient(135deg, #FFFFFF 0%, #FAFAF8 100%);
		border: 1px solid rgba(27, 67, 50, 0.08);
		border-left: 4px solid #D8B25C;
		border-radius: 12px;
		padding: 16px 20px;
		box-shadow: 0 2px 8px rgba(27, 67, 50, 0.06);
		transition: all 0.25s ease;
	}
	[data-testid="stMetric"]:hover {
		box-shadow: 0 6px 20px rgba(27, 67, 50, 0.12);
		transform: translateY(-2px);
	}
	[data-testid="stMetricValue"] {
		color: #1B4332;
		font-weight: 700;
	}
	[data-testid="stMetricLabel"] {
		color: #1B4332;
		font-weight: 500;
	}

	.stTabs [data-baseweb="tab-list"] {
		gap: 8px;
		background: transparent;
		padding: 4px;
		border-bottom: 2px solid rgba(216, 178, 92, 0.30);
	}
	.stTabs [data-baseweb="tab"] {
		background: transparent;
		border-radius: 10px 10px 0 0;
		padding: 12px 28px;
		border: 1px solid transparent;
		font-family: 'Sora', sans-serif;
		font-weight: 600;
		transition: all 0.25s ease;
	}
	.stTabs [data-baseweb="tab"][aria-selected="true"] {
		background-color: #1B4332 !important;
		border-color: #1B4332 !important;
		box-shadow: 0 4px 12px rgba(27, 67, 50, 0.25);
	}
	.stTabs [data-baseweb="tab"][aria-selected="true"],
	.stTabs [data-baseweb="tab"][aria-selected="true"] p,
	.stTabs [data-baseweb="tab"][aria-selected="true"] span,
	.stTabs [data-baseweb="tab"][aria-selected="true"] div {
		color: #FAFAF8 !important;
	}
	.stTabs [data-baseweb="tab"][aria-selected="false"],
	.stTabs [data-baseweb="tab"][aria-selected="false"] p {
		color: #1B4332 !important;
	}
	.stTabs [data-baseweb="tab"][aria-selected="false"]:hover {
		background-color: rgba(27, 67, 50, 0.08);
	}

	[data-testid="stExpander"] {
		background: #FFFFFF;
		border: 1px solid rgba(27, 67, 50, 0.12);
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 1px 4px rgba(27, 67, 50, 0.05);
	}
	[data-testid="stExpander"] summary {
		background: #FAFAF8;
		color: #1B4332;
		font-family: 'Sora', sans-serif;
		font-weight: 600;
	}

	[data-testid="stDataFrame"] {
		border: 1px solid rgba(27, 67, 50, 0.10);
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 2px 8px rgba(27, 67, 50, 0.05);
	}

	hr {
		border: none;
		border-top: 2px solid rgba(216, 178, 92, 0.45);
		margin: 28px 0;
	}

	::-webkit-scrollbar { width: 10px; height: 10px; }
	::-webkit-scrollbar-track { background: #FAFAF8; }
	::-webkit-scrollbar-thumb {
		background: rgba(27, 67, 50, 0.40);
		border-radius: 6px;
	}
	::-webkit-scrollbar-thumb:hover { background: #1B4332; }

	.ag-header {
		display: flex;
		align-items: center;
		gap: 20px;
		padding-bottom: 20px;
		margin-bottom: 24px;
		border-bottom: 2px solid rgba(216, 178, 92, 0.45);
	}
	.ag-logo {
		width: 96px;
		flex-shrink: 0;
		padding: 6px;
	}
	.ag-logo svg {
		width: 100%;
		height: auto;
		display: block;
	}
	.ag-title {
		font-family: 'Sora', sans-serif;
		font-weight: 800;
		font-size: 1.9rem;
		line-height: 1.2;
		color: #1B4332;
		letter-spacing: -0.02em;
	}
	.ag-subtitle {
		font-family: 'Inter', sans-serif;
		font-size: 0.85rem;
		color: #2c5b48;
		margin-top: 6px;
		line-height: 1.5;
	}
</style>
""",
	unsafe_allow_html=True,
)

# ============ TEMPLATE PLOTLY AG ============
AG_PALETTE = ["#1B4332", "#2C5F7C", "#D8B25C", "#BC6C25", "#E9C46A"]

ag_template = go.layout.Template(
	layout=dict(
		colorway=AG_PALETTE,
		font=dict(family="Inter, sans-serif", color="#1B4332"),
		title=dict(font=dict(family="Sora, sans-serif", color="#1B4332")),
		paper_bgcolor="#FAFAF8",
		plot_bgcolor="#FAFAF8",
		xaxis=dict(
			gridcolor="rgba(27, 67, 50, 0.08)",
			linecolor="rgba(27, 67, 50, 0.15)",
			zerolinecolor="rgba(27, 67, 50, 0.10)",
		),
		yaxis=dict(
			gridcolor="rgba(27, 67, 50, 0.08)",
			linecolor="rgba(27, 67, 50, 0.15)",
			zerolinecolor="rgba(27, 67, 50, 0.10)",
		),
		legend=dict(
			bgcolor="rgba(250, 250, 248, 0.85)",
			bordercolor="rgba(27, 67, 50, 0.12)",
			borderwidth=1,
		),
	)
)

pio.templates["ag_berrix"] = ag_template
pio.templates.default = "ag_berrix"

# ============ CARGA DE DATOS PÚBLICOS ============
@st.cache_data
def load_public_data():
	data = {}
	data["d01_canal"] = pl.read_parquet(PUBLIC_DIR / "d01_canal_publico.parquet")
	data["d01_temporada"] = pl.read_parquet(PUBLIC_DIR / "d01_temporada_publico.parquet")
	data["d02_macro_region"] = pl.read_parquet(PUBLIC_DIR / "d02_macro_region_publico.parquet")
	data["d02_concentracion"] = pl.read_parquet(PUBLIC_DIR / "d02_concentracion_publico.parquet")
	data["d03_mensual"] = pl.read_parquet(PUBLIC_DIR / "d03_alertas_publico.parquet")
	data["d03_total"] = pl.read_parquet(PUBLIC_DIR / "d03_alertas_total_publico.parquet")
	data["d04_concentracion"] = pl.read_parquet(PUBLIC_DIR / "d04_portafolio_publico.parquet")
	data["d04_global"] = pl.read_parquet(PUBLIC_DIR / "d04_portafolio_global_publico.parquet")
	return data

data = load_public_data()

# ============ HEADER CON LOGO AG v6 + SELECTOR DE IDIOMA ============
AG6_SVG = AG6_PATH.read_text(encoding="utf-8") if AG6_PATH.exists() else ""

h_left, h_right = st.columns([7, 1], vertical_alignment="center")
with h_left:
	st.markdown(
		f"""
		<div class="ag-header">
			<div class="ag-logo">{AG6_SVG}</div>
			<div>
				<div class="ag-title">{t("header_title")}</div>
				<div class="ag-subtitle">{t("header_subtitle")}</div>
			</div>
		</div>
		""",
		unsafe_allow_html=True,
	)
with h_right:
	lang_selector()

# ============ TABS ============
tab0, tab1, tab2, tab3, tab4 = st.tabs([
	t("tab0"),
	t("tab1"),
	t("tab2"),
	t("tab3"),
	t("tab4"),
])

# ============ PESTAÑA 00 · GOBERNANZA ============
with tab0:
	st.subheader(t("gov_sub"))
	st.caption(t("gov_caption"))

	g1, g2, g3, g4 = st.columns(4)
	with g1:
		st.metric(label=t("gov_m1_label"), value=t("gov_m1_value"))
	with g2:
		st.metric(label=t("gov_m2_label"), value=t("gov_m2_value"))
	with g3:
		st.metric(label=t("gov_m3_label"), value=t("gov_m3_value"))
	with g4:
		st.metric(label=t("gov_m4_label"), value=t("gov_m4_value"))

	st.markdown("---")

	st.markdown(t("gov_tec_title"))
	st.dataframe(tech_dataframe(), use_container_width=True, hide_index=True)

	with st.expander(t("gov_expander")):
		st.markdown(t("gov_note"))

# ============ PESTAÑA 01 · VENTAS POR CANAL ============
with tab1:
	st.subheader(t("d01_sub"))
	st.caption(t("d01_caption"))

	d01_total = data["d01_temporada"]["venta_neta_cop"].sum()
	d01_canales = data["d01_canal"].sort("venta_neta_cop", descending=True)
	canal_top = d01_canales[0, "canal"] if len(d01_canales) > 0 else "-"
	from i18n import disp as _disp
	canal_top_disp = _disp(canal_top, "canal") if canal_top != "-" else "-"

	c1, c2, c3 = st.columns(3)
	with c1:
		st.metric(t("d01_m1"), f"$ {d01_total/1e9:,.1f} B")
	with c2:
		st.metric(t("d01_m2"), canal_top_disp)
	with c3:
		st.metric(t("d01_m3"), t("d01_m3_value", n=len(d01_canales)))

	st.markdown("---")

	st.subheader(t("d01_mix_title"))
	pdf_canal = map_col(d01_canales.to_pandas(), "canal", "canal")
	fig_canal = px.bar(
		pdf_canal,
		x="canal",
		y="venta_neta_cop",
		color="canal",
		color_discrete_map=color_map("canal"),
		labels={"venta_neta_cop": t("d01_axis_venta"), "canal": t("d01_axis_canal")}
	)
	fig_canal.update_layout(height=400, yaxis=dict(tickformat="$,.0f"), showlegend=False)
	st.plotly_chart(fig_canal, use_container_width=True)

	st.info(t("d01_info"))

	st.markdown("---")

	st.subheader(t("d01_temp_title"))
	fig_temp = px.line(
		data["d01_temporada"].to_pandas(),
		x="temporada",
		y="venta_neta_cop",
		markers=True,
		labels={"venta_neta_cop": t("d01_axis_venta"), "temporada": t("d01_axis_temp")}
	)
	fig_temp.update_layout(height=400, yaxis=dict(tickformat="$,.0f"))
	st.plotly_chart(fig_temp, use_container_width=True)

# ============ PESTAÑA 02 · DINÁMICA REGIONAL ============
with tab2:
	st.subheader(t("d02_sub"))
	st.caption(t("d02_caption"))

	d02_total = data["d02_macro_region"]["venta_neta_cop"].sum()
	centro_val = data["d02_macro_region"].filter(pl.col("macro_region") == "Centro")["venta_neta_cop"].sum()
	resto_val = data["d02_macro_region"].filter(pl.col("macro_region") == "Resto de regiones")["venta_neta_cop"].sum()
	pct_centro = centro_val / d02_total * 100 if d02_total > 0 else 0

	c1, c2, c3 = st.columns(3)
	with c1:
		st.metric(t("d02_m1"), f"$ {d02_total/1e9:,.1f} B")
	with c2:
		st.metric(t("d02_m2"), f"$ {centro_val/1e9:,.1f} B", f"{pct_centro:.1f}%")
	with c3:
		st.metric(t("d02_m3"), f"$ {resto_val/1e9:,.1f} B", f"{100-pct_centro:.1f}%")

	st.markdown("---")

	st.subheader(t("d02_donut_title"))
	pdf_reg = map_col(data["d02_macro_region"].to_pandas(), "macro_region", "macro_region")
	fig_donut = px.pie(
		pdf_reg,
		names="macro_region",
		values="venta_neta_cop",
		hole=0.60,
		color="macro_region",
		color_discrete_map=color_map("macro_region")
	)
	fig_donut.update_traces(textinfo="label+percent")
	fig_donut.update_layout(height=400)
	st.plotly_chart(fig_donut, use_container_width=True)

	st.markdown("---")

	st.subheader(t("d02_conc_title"))
	fig_conc = px.line(
		data["d02_concentracion"].to_pandas(),
		x="temporada",
		y="indice_concentracion",
		markers=True,
		labels={"indice_concentracion": t("d02_conc_y"), "temporada": t("d01_axis_temp")}
	)
	fig_conc.update_layout(height=400, yaxis=dict(tickformat=".0%"))
	st.plotly_chart(fig_conc, use_container_width=True)

	st.info(t("d02_info"))

# ============ PESTAÑA 03 · ALERTAS Y RIESGOS ============
with tab3:
	st.subheader(t("d03_sub"))
	st.caption(t("d03_caption"))

	d03_total = data["d03_total"]
	conteo_alto = d03_total.filter(pl.col("nivel_riesgo") == "alto_riesgo")["n_clientes"].sum()
	conteo_medio = d03_total.filter(pl.col("nivel_riesgo") == "riesgo_medio")["n_clientes"].sum()
	conteo_estable = d03_total.filter(pl.col("nivel_riesgo") == "estable")["n_clientes"].sum()
	kg_riesgo = d03_total.filter(pl.col("nivel_riesgo").is_in(["alto_riesgo", "riesgo_medio"]))["kg_caida_total"].sum()

	c1, c2, c3, c4 = st.columns(4)
	with c1:
		st.metric(t("d03_m1"), t("d03_clientes", n=conteo_alto))
	with c2:
		st.metric(t("d03_m2"), t("d03_clientes", n=conteo_medio))
	with c3:
		st.metric(t("d03_m3"), t("d03_clientes", n=conteo_estable))
	with c4:
		st.metric(t("d03_m4"), t("d03_kg", kg=f"{kg_riesgo:,.0f}"))

	st.markdown("---")

	st.subheader(t("d03_evo_title"))
	pdf_sem = map_col(data["d03_mensual"].sort("periodo").to_pandas(), "nivel_riesgo", "nivel_riesgo")
	fig_semaforo = px.bar(
		pdf_sem,
		x="periodo",
		y="n_clientes",
		color="nivel_riesgo",
		color_discrete_map=color_map("nivel_riesgo"),
		barmode="stack",
		labels={
			"n_clientes": t("d03_axis_n"),
			"periodo": t("d03_axis_periodo"),
			"nivel_riesgo": t("d03_axis_nivel"),
		}
	)
	fig_semaforo.update_layout(
		height=500,
		legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
	)
	st.plotly_chart(fig_semaforo, use_container_width=True)

	st.markdown("---")

	st.subheader(t("d03_table_title"))
	pdf_tab = d03_total.to_pandas()
	pdf_tab = map_col(pdf_tab, "nivel_riesgo", "nivel_riesgo")
	pdf_tab["kg_caida_total"] = pdf_tab["kg_caida_total"].round(0)
	pdf_tab = pdf_tab.rename(columns={
		"nivel_riesgo": t("d03_col_nivel"),
		"n_clientes": t("d03_col_clientes"),
		"kg_caida_total": t("d03_col_kg"),
	})
	st.dataframe(pdf_tab, use_container_width=True, hide_index=True)

	with st.expander(t("d03_expander")):
		st.markdown(t("d03_note"))

# ============ PESTAÑA 04 · PORTAFOLIO ============
with tab4:
	st.subheader(t("d04_sub"))
	st.caption(t("d04_caption"))

	d04_global = data["d04_global"].row(0, named=True)
	total_clientes = d04_global["total_clientes"]
	clientes_cautivos = d04_global["clientes_cautivos"]
	clientes_alto_valor = d04_global["clientes_alto_valor"]
	venta_total = d04_global["venta_total_cop"]
	venta_cautivos = d04_global["venta_cautivos_cop"]
	pct_pareto = d04_global["pct_clientes_pareto_generalizado"]

	c1, c2, c3, c4 = st.columns(4)
	with c1:
		st.metric(t("d04_m1"), f"{total_clientes}")
	with c2:
		st.metric(t("d04_m2"), t("d04_pct", n=clientes_cautivos, p=clientes_cautivos*100//total_clientes))
	with c3:
		st.metric(t("d04_m3"), t("d04_pct", n=clientes_alto_valor, p=clientes_alto_valor*100//total_clientes))
	with c4:
		st.metric(t("d04_m4"), pct_pareto)

	st.markdown("---")

	st.subheader(t("d04_donut_title"))
	pdf_conc = map_col(data["d04_concentracion"].to_pandas(), "concentracion", "concentracion")
	fig_conc4 = px.pie(
		pdf_conc,
		names="concentracion",
		values="n_clientes",
		hole=0.60,
		color="concentracion",
		color_discrete_map=color_map("concentracion")
	)
	fig_conc4.update_traces(textinfo="label+percent+value")
	fig_conc4.update_layout(height=400)
	st.plotly_chart(fig_conc4, use_container_width=True)

	st.markdown("---")

	st.subheader(t("d04_global_title"))
	g1, g2 = st.columns(2)
	with g1:
		st.metric(t("d04_g1"), f"$ {venta_total/1e9:,.1f} B")
		st.metric(
			t("d04_g2"),
			f"$ {venta_cautivos/1e9:,.1f} B",
			t("d04_g2_delta", p=f"{venta_cautivos*100/venta_total:.1f}")
		)
	with g2:
		st.metric(
			t("d04_g3"),
			t("d04_g3_value", a=d04_global["clientes_para_80"], b=total_clientes)
		)
		st.metric(t("d04_g4"), pct_pareto)

	with st.expander(t("d04_expander")):
		st.markdown(t("d04_note"))