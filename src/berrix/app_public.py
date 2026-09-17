import streamlit as st
import polars as pl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
from datetime import date, timedelta

# ============ RUTAS Y LOGO ============
ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT / "data" / "public"
AG6_PATH = ROOT / "src" / "berrix" / "assets" / "ag6.svg"

st.set_page_config(
	page_title="Tablero Comercial · Berries (público)",
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
	
	# D01
	data["d01_canal"] = pl.read_parquet(PUBLIC_DIR / "d01_canal_publico.parquet")
	data["d01_temporada"] = pl.read_parquet(PUBLIC_DIR / "d01_temporada_publico.parquet")
	
	# D02
	data["d02_macro_region"] = pl.read_parquet(PUBLIC_DIR / "d02_macro_region_publico.parquet")
	data["d02_concentracion"] = pl.read_parquet(PUBLIC_DIR / "d02_concentracion_publico.parquet")
	
	# D03
	data["d03_mensual"] = pl.read_parquet(PUBLIC_DIR / "d03_alertas_publico.parquet")
	data["d03_total"] = pl.read_parquet(PUBLIC_DIR / "d03_alertas_total_publico.parquet")
	
	# D04
	data["d04_concentracion"] = pl.read_parquet(PUBLIC_DIR / "d04_portafolio_publico.parquet")
	data["d04_global"] = pl.read_parquet(PUBLIC_DIR / "d04_portafolio_global_publico.parquet")
	
	return data

data = load_public_data()

# ============ HEADER CON LOGO AG v6 ============
AG6_SVG = AG6_PATH.read_text(encoding="utf-8") if AG6_PATH.exists() else ""

st.markdown(
	f"""
	<div class="ag-header">
		<div class="ag-logo">{AG6_SVG}</div>
		<div>
			<div class="ag-title">Tablero Comercial · Berries</div>
			<div class="ag-subtitle">
				Datos públicos k-anónimos · Elaborado por Andrés Gómez · Analista de Datos Agroindustriales
			</div>
		</div>
	</div>
	""",
	unsafe_allow_html=True,
)

# ============ TABS ============
tab0, tab1, tab2, tab3, tab4 = st.tabs([
	"🛡️ 00 · Gobernanza",
	"📊 01 · Ventas por canal",
	"🗺️ 02 · Dinámica regional",
	"🚨 03 · Alertas y riesgos",
	"📦 04 · Portafolio"
])

# ============ PESTAÑA 00 · GOBERNANZA ============
with tab0:
	st.subheader("🛡️ Gobernanza de datos")
	st.caption(
		"Este tablero usa **datos públicos k-anónimos**, derivados de información comercial real "
		"mediante técnicas de anonimización conforme al acuerdo de confidencialidad."
	)

	g1, g2, g3, g4 = st.columns(4)
	with g1:
		st.metric(label="Nivel público", value="K-anónimo")
	with g2:
		st.metric(label="Umbral k", value="k ≥ 5")
	with g3:
		st.metric(label="Supresión", value="Celdas < 10")
	with g4:
		st.metric(label="Técnicas", value="5 aplicadas")

	st.markdown("---")

	st.markdown("### Técnicas de anonimización aplicadas")
	tecnicas_data = {
		"Técnica": [
			"Agregación / totalización",
			"K-anonimato (k ≥ 5)",
			"Supresión de celdas",
			"Generalización de categorías",
			"Redondeo y perturbación",
		],
		"Aplicación": [
			"Sumar registros individuales en grupos",
			"Cada grupo tiene al menos 5 contribuyentes",
			"Celdas con <10 contribuyentes se ocultan",
			"Reducir granularidad (ej. macro-regiones)",
			"Añadir ruido controlado a valores",
		],
	}
	st.dataframe(tecnicas_data, use_container_width=True, hide_index=True)

	with st.expander("📜 Nota de transparencia"):
		st.markdown(
			"""
			**Debido al tamaño de la base B2B (33 clientes), algunas categorías con pocos contribuyentes
			se generalizan o suprimen para garantizar k≥5 y celdas≥10.**
			
			Ejemplos de generalización aplicada:
			- **Canales:** Retail (8 clientes) se suprime en el nivel público; solo se muestran HORECA y Mayoristas.
			- **Regiones:** Las 7 regiones originales se agrupan en "Centro" y "Resto de regiones".
			- **Cuentas nacionales:** Se diluyen en el grupo "Resto de regiones" por k-anonimato.
			
			El análisis detallado por cliente individual está disponible únicamente en el nivel local
			pseudonimizado, conforme al acuerdo de confidencialidad.
			"""
		)

# ============ PESTAÑA 01 · VENTAS POR CANAL ============
with tab1:
	st.subheader("📊 Ventas por canal (datos agregados)")
	st.caption(
		"Mezcla de canales comerciales y evolución temporal. "
		"Datos agregados por temporada para garantizar k-anonimato."
	)

	# KPIs
	d01_total = data["d01_temporada"]["venta_neta_cop"].sum()
	d01_canales = data["d01_canal"].sort("venta_neta_cop", descending=True)
	canal_top = d01_canales[0, "canal"] if len(d01_canales) > 0 else "-"
	canal_top_val = d01_canales[0, "venta_neta_cop"] if len(d01_canales) > 0 else 0

	c1, c2, c3 = st.columns(3)
	with c1:
		st.metric("Venta neta B2B total", f"$ {d01_total/1e9:,.1f} B")
	with c2:
		st.metric("Canal líder", canal_top)
	with c3:
		st.metric("Canales visibles", f"{len(d01_canales)} de 5")

	st.markdown("---")

	# Gráfico 1: Mezcla de canales
	st.subheader("Mezcla de canales (agregado histórico)")
	canal_colors = {
		"Food Service - HORECA": "#1B4332",
		"Mayoristas": "#2C5F7C",
	}
	fig_canal = px.bar(
		d01_canales.to_pandas(),
		x="canal",
		y="venta_neta_cop",
		color="canal",
		color_discrete_map=canal_colors,
		labels={"venta_neta_cop": "Venta neta (COP)", "canal": "Canal"}
	)
	fig_canal.update_layout(
		height=400,
		yaxis=dict(tickformat="$,.0f"),
		showlegend=False
	)
	st.plotly_chart(fig_canal, use_container_width=True)

	st.info(
		"💡 **Nota:** Retail se suprime en el nivel público (8 clientes < umbral de 10). "
		"Solo se muestran los canales con ≥10 contribuyentes."
	)

	st.markdown("---")

	# Gráfico 2: Evolución por temporada
	st.subheader("Evolución por temporada")
	fig_temp = px.line(
		data["d01_temporada"].to_pandas(),
		x="temporada",
		y="venta_neta_cop",
		markers=True,
		labels={"venta_neta_cop": "Venta neta (COP)", "temporada": "Temporada"}
	)
	fig_temp.update_layout(
		height=400,
		yaxis=dict(tickformat="$,.0f")
	)
	st.plotly_chart(fig_temp, use_container_width=True)

# ============ PESTAÑA 02 · DINÁMICA REGIONAL ============
with tab2:
	st.subheader("🗺️ Dinámica regional (datos agregados)")
	st.caption(
		"Distribución geográfica generalizada en macro-regiones. "
		"Las cuentas nacionales se integran al grupo 'Resto de regiones' por k-anonimato."
	)

	# KPIs
	d02_total = data["d02_macro_region"]["venta_neta_cop"].sum()
	centro_val = data["d02_macro_region"].filter(pl.col("macro_region") == "Centro")["venta_neta_cop"].sum()
	resto_val = data["d02_macro_region"].filter(pl.col("macro_region") == "Resto de regiones")["venta_neta_cop"].sum()
	pct_centro = centro_val / d02_total * 100 if d02_total > 0 else 0

	c1, c2, c3 = st.columns(3)
	with c1:
		st.metric("Venta neta B2B total", f"$ {d02_total/1e9:,.1f} B")
	with c2:
		st.metric("Centro", f"$ {centro_val/1e9:,.1f} B", f"{pct_centro:.1f}%")
	with c3:
		st.metric("Resto de regiones", f"$ {resto_val/1e9:,.1f} B", f"{100-pct_centro:.1f}%")

	st.markdown("---")

	# Donut: Centro vs Resto
	st.subheader("Distribución Centro vs Resto")
	region_colors = {
		"Centro": "#1B4332",
		"Resto de regiones": "#D8B25C",
	}
	fig_donut = px.pie(
		data["d02_macro_region"].to_pandas(),
		names="macro_region",
		values="venta_neta_cop",
		hole=0.60,
		color="macro_region",
		color_discrete_map=region_colors
	)
	fig_donut.update_traces(textinfo="label+percent")
	fig_donut.update_layout(height=400)
	st.plotly_chart(fig_donut, use_container_width=True)

	st.markdown("---")

	# Línea: concentración del Centro por temporada
	st.subheader("Concentración geográfica (participación del Centro)")
	fig_conc = px.line(
		data["d02_concentracion"].to_pandas(),
		x="temporada",
		y="indice_concentracion",
		markers=True,
		labels={"indice_concentracion": "% participación del Centro", "temporada": "Temporada"}
	)
	fig_conc.update_layout(
		height=400,
		yaxis=dict(tickformat=".0%")
	)
	st.plotly_chart(fig_conc, use_container_width=True)

	st.info(
		"💡 **Nota:** La categoría 'Nacional' (3 clientes) se agrupa en 'Resto de regiones' "
		"para garantizar k-anonimato. El análisis detallado por región fina está disponible "
		"en el nivel local pseudonimizado."
	)

# ============ PESTAÑA 03 · ALERTAS Y RIESGOS ============
with tab3:
	st.subheader("🚨 Alertas y riesgos (datos agregados)")
	st.caption(
		"Semáforo de retención basado en volumen (kg). "
		"Datos agregados por nivel de riesgo, sin detalle por cliente individual."
	)

	# KPIs desde el total
	d03_total = data["d03_total"]
	conteo_alto = d03_total.filter(pl.col("nivel_riesgo") == "alto_riesgo")["n_clientes"].sum()
	conteo_medio = d03_total.filter(pl.col("nivel_riesgo") == "riesgo_medio")["n_clientes"].sum()
	conteo_estable = d03_total.filter(pl.col("nivel_riesgo") == "estable")["n_clientes"].sum()
	kg_riesgo = d03_total.filter(pl.col("nivel_riesgo").is_in(["alto_riesgo", "riesgo_medio"]))["kg_caida_total"].sum()

	c1, c2, c3, c4 = st.columns(4)
	with c1:
		st.metric("🔴 Alto riesgo", f"{conteo_alto} clientes")
	with c2:
		st.metric("🟡 Riesgo medio", f"{conteo_medio} clientes")
	with c3:
		st.metric("🟢 Estables", f"{conteo_estable} clientes")
	with c4:
		st.metric("📦 Kg en riesgo", f"{kg_riesgo:,.0f} kg")

	st.markdown("---")

	# Gráfico: evolución mensual del semáforo
	st.subheader("Evolución del semáforo (últimos períodos)")
	d03_mensual_df = data["d03_mensual"].sort("periodo").to_pandas()
	
	nivel_colors = {
		"alto_riesgo": "#BC6C25",
		"riesgo_medio": "#E9C46A",
		"estable": "#1B4332"
	}
	fig_semaforo = px.bar(
		d03_mensual_df,
		x="periodo",
		y="n_clientes",
		color="nivel_riesgo",
		color_discrete_map=nivel_colors,
		barmode="stack",
		labels={"n_clientes": "Número de clientes", "periodo": "Período", "nivel_riesgo": "Nivel de riesgo"}
	)
	fig_semaforo.update_layout(
		height=500,
		legend=dict(
			orientation="h",
			yanchor="bottom",
			y=1.02,
			xanchor="right",
			x=1
		)
	)
	st.plotly_chart(fig_semaforo, use_container_width=True)

	st.markdown("---")

	# Tabla de totales
	st.subheader("Totales por nivel de riesgo")
	st.dataframe(
		d03_total.to_pandas().style.format({
			"kg_caida_total": "{:,.0f}"
		}),
		use_container_width=True
	)

	with st.expander("Supuestos y gobernanza"):
		st.markdown(
			"""
			- **Métrica:** Kilogramos (precio-neutral para evitar falsos positivos por volatilidad).
			- **Línea base:** Promedio móvil de los 3 meses calendario anteriores por cliente.
			- **Sostenibilidad:** El color solo se confirma si la caída se repite 2 meses consecutivos.
			- **Niveles:**
			  - 🟢 Estable: caída <15% o no sostenida
			  - 🟡 Riesgo medio: caída ≥15% y <30%, sostenida 2 meses
			  - 🔴 Alto riesgo: caída ≥30%, sostenida 2 meses
			
			**Nota:** El semáforo por cliente individual no se publica por k-anonimato.
			Solo se muestran agregados por nivel de riesgo.
			"""
		)

# ============ PESTAÑA 04 · PORTAFOLIO ============
with tab4:
	st.subheader("📦 Portafolio (datos agregados)")
	st.caption(
		"Análisis estratégico de la base B2B: concentración y Pareto. "
		"Datos agregados por tipo de cliente, sin detalle individual."
	)

	# KPIs desde el global
	d04_global = data["d04_global"].row(0, named=True)
	total_clientes = d04_global["total_clientes"]
	clientes_cautivos = d04_global["clientes_cautivos"]
	clientes_alto_valor = d04_global["clientes_alto_valor"]
	venta_total = d04_global["venta_total_cop"]
	venta_cautivos = d04_global["venta_cautivos_cop"]
	pct_pareto = d04_global["pct_clientes_pareto_generalizado"]

	c1, c2, c3, c4 = st.columns(4)
	with c1:
		st.metric("Total clientes", f"{total_clientes}")
	with c2:
		st.metric("Cautivos", f"{clientes_cautivos} ({clientes_cautivos*100//total_clientes}%)")
	with c3:
		st.metric("Alto valor", f"{clientes_alto_valor} ({clientes_alto_valor*100//total_clientes}%)")
	with c4:
		st.metric("Pareto", pct_pareto)

	st.markdown("---")

	# Donut: Cautivo vs Diversificado
	st.subheader("Distribución por concentración")
	conc_colors = {
		"Cautivo": "#1B4332",
		"Diversificado": "#D8B25C"
	}
	fig_conc = px.pie(
		data["d04_concentracion"].to_pandas(),
		names="concentracion",
		values="n_clientes",
		hole=0.60,
		color="concentracion",
		color_discrete_map=conc_colors
	)
	fig_conc.update_traces(textinfo="label+percent+value")
	fig_conc.update_layout(height=400)
	st.plotly_chart(fig_conc, use_container_width=True)

	st.markdown("---")

	# Métricas globales
	st.subheader("Métricas globales")
	g1, g2 = st.columns(2)
	with g1:
		st.metric("Venta total B2B", f"$ {venta_total/1e9:,.1f} B")
		st.metric("Venta en cautivos", f"$ {venta_cautivos/1e9:,.1f} B", f"{venta_cautivos*100/venta_total:.1f}% del total")
	with g2:
		st.metric("Clientes para 80% de venta", f"{d04_global['clientes_para_80']} de {total_clientes}")
		st.metric("Concentración Pareto", pct_pareto)

	with st.expander("Supuestos y gobernanza"):
		st.markdown(
			"""
			- **Umbral de cautividad:** ≥80% del volumen en la especie dominante.
			- **Pareto:** Clientes que acumulan el 80% de la venta neta B2B.
			- **Actividad mínima:** Clientes con ≥2 meses de compra.
			
			**Nota:** La matriz de portafolio por cliente individual no se publica por k-anonimato.
			Solo se muestran agregados por tipo de concentración y métricas globales.
			"""
		)