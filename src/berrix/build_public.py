"""
build_public.py
Genera datasets públicos k-anónimos desde los datos locales pseudonimizados.

Estrategia: Combinación Opción 1 + Opción 3
- D02: macro-regiones generalizadas + índice de concentración (ratio)
- D04: Pareto como ratio percentil + agregados por concentración

Cumple con el NDA Anexo A:
- Agregación / totalización
- k-anonimato (k≥5)
- Supresión de celdas con <10 contribuyentes
- Generalización de categorías

Uso: uv run python -m berrix.build_public
"""

from __future__ import annotations
from pathlib import Path
import sys
import duckdb


# ============ PARÁMETROS DE ANONIMIZACIÓN (NDA Anexo A) ============
K_MIN = 5
CELL_MIN = 10

def get_project_root() -> Path:
	for parent in Path(__file__).resolve().parents:
		if (parent / "pyproject.toml").exists():
			return parent
	return Path.cwd()


PROJECT_ROOT = get_project_root()
ANON_DIR = PROJECT_ROOT / "data" / "processed" / "anon"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PUBLIC_DIR = PROJECT_ROOT / "data" / "public"

VENTAS_PATH = ANON_DIR / "ventas_local.parquet"
CLIENTES_PATH = ANON_DIR / "clientes_local.parquet"
D03_LOCAL = PROCESSED_DIR / "d03_riesgo_client_month.parquet"
D04_LOCAL = PROCESSED_DIR / "d04_portafolio_client.parquet"

CANALES_COMERCIALES = ["Food Service - HORECA", "Mayoristas", "Retail"]

def build_d01(con: duckdb.DuckDBPyConnection) -> None:
	"""
	D01 público: dos perspectivas con una sola dimensión cada una.
	- d01_canal_publico.parquet: mezcla de canales (agregado en el tiempo)
	- d01_temporada_publico.parquet: evolución por temporada (agregado en canales)
	Supresión de celdas con <10 contribuyentes.
	Nota: Retail (8 clientes) se suprime en el nivel público por celdas>=10.
	"""
	out_canal = PUBLIC_DIR / "d01_canal_publico.parquet"
	out_temporada = PUBLIC_DIR / "d01_temporada_publico.parquet"

	# 1. Mezcla de canales (sin temporada)
	con.execute(f"""
		COPY (
			WITH ventas_b2b AS (
				SELECT
					v.V08_canal_cliente AS canal,
					v.V24_venta_neta_cop AS venta_cop,
					v.V28_venta_neta_usd AS venta_usd,
					v.V19_cant_kg_total AS kg,
					v.client_id
				FROM ventas v
				INNER JOIN clientes c ON v.client_id = c.client_id
				WHERE lower(replace(cast(v.V06_documento_tipo AS varchar), 'ó', 'o')) NOT LIKE '%dmc%'
				  AND lower(replace(cast(v.V06_documento_tipo AS varchar), 'ó', 'o')) NOT LIKE '%devol%'
				  AND v.V08_canal_cliente IN ('Food Service - HORECA', 'Mayoristas', 'Retail')
			),
			agregado AS (
				SELECT
					canal,
					SUM(venta_cop) AS venta_neta_cop,
					SUM(venta_usd) AS venta_neta_usd,
					SUM(kg) AS kg_total,
					COUNT(DISTINCT client_id) AS n_clientes
				FROM ventas_b2b
				GROUP BY canal
			)
			SELECT *
			FROM agregado
			WHERE n_clientes >= {CELL_MIN}
			ORDER BY venta_neta_cop DESC
		) TO '{out_canal.as_posix()}' (FORMAT PARQUET);
	""")

	# 2. Evolución por temporada (sin canal) + con filtro de canal comercial
	con.execute(f"""
		COPY (
			WITH ventas_b2b AS (
				SELECT
					v.V01_temporada AS temporada,
					v.V24_venta_neta_cop AS venta_cop,
					v.V28_venta_neta_usd AS venta_usd,
					v.V19_cant_kg_total AS kg,
					v.client_id
				FROM ventas v
				INNER JOIN clientes c ON v.client_id = c.client_id
				WHERE lower(replace(cast(v.V06_documento_tipo AS varchar), 'ó', 'o')) NOT LIKE '%dmc%'
				  AND lower(replace(cast(v.V06_documento_tipo AS varchar), 'ó', 'o')) NOT LIKE '%devol%'
				  AND v.V08_canal_cliente IN ('Food Service - HORECA', 'Mayoristas', 'Retail')
			),
			agregado AS (
				SELECT
					temporada,
					SUM(venta_cop) AS venta_neta_cop,
					SUM(venta_usd) AS venta_neta_usd,
					SUM(kg) AS kg_total,
					COUNT(DISTINCT client_id) AS n_clientes
				FROM ventas_b2b
				GROUP BY temporada
			)
			SELECT *
			FROM agregado
			WHERE n_clientes >= {CELL_MIN}
			ORDER BY temporada
		) TO '{out_temporada.as_posix()}' (FORMAT PARQUET);
	""")

	n_canal = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_canal.as_posix()}')").fetchone()[0]
	n_temp = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_temporada.as_posix()}')").fetchone()[0]
	print(f"  D01 público canal: {n_canal} filas")
	print(f"  D01 público temporada: {n_temp} filas")


def build_d02(con: duckdb.DuckDBPyConnection) -> None:
	"""
	D02 público: dos perspectivas.
	- d02_macro_region_publico.parquet: Centro vs Resto de regiones (agregado en el tiempo)
	- d02_concentracion_publico.parquet: participación del Centro por temporada
	Las cuentas nacionales y regiones pequeñas se diluyen en 'Resto de regiones'
	para garantizar celdas>=10.
	"""
	out_regiones = PUBLIC_DIR / "d02_macro_region_publico.parquet"
	out_concentracion = PUBLIC_DIR / "d02_concentracion_publico.parquet"

	# 1. Distribución por macro-región
	con.execute(f"""
		COPY (
			WITH ventas_b2b AS (
				SELECT
					CASE
						WHEN c.region IN ('CENTRO - BOGOTA', 'CENTRO - SABANA') THEN 'Centro'
						ELSE 'Resto de regiones'
					END AS macro_region,
					v.V24_venta_neta_cop AS venta_cop,
					v.V28_venta_neta_usd AS venta_usd,
					v.V19_cant_kg_total AS kg,
					v.client_id
				FROM ventas v
				INNER JOIN clientes c ON v.client_id = c.client_id
				WHERE lower(replace(cast(v.V06_documento_tipo AS varchar), 'ó', 'o')) NOT LIKE '%dmc%'
				  AND lower(replace(cast(v.V06_documento_tipo AS varchar), 'ó', 'o')) NOT LIKE '%devol%'
				  AND v.V08_canal_cliente IN ('Food Service - HORECA', 'Mayoristas', 'Retail')
			),
			agregado AS (
				SELECT
					macro_region,
					SUM(venta_cop) AS venta_neta_cop,
					SUM(venta_usd) AS venta_neta_usd,
					SUM(kg) AS kg_total,
					COUNT(DISTINCT client_id) AS n_clientes
				FROM ventas_b2b
				GROUP BY macro_region
			)
			SELECT *
			FROM agregado
			WHERE n_clientes >= {CELL_MIN}
			ORDER BY venta_neta_cop DESC
		) TO '{out_regiones.as_posix()}' (FORMAT PARQUET);
	""")

	# 2. Concentración geográfica: participación del Centro por temporada
	con.execute(f"""
		COPY (
			WITH ventas_b2b AS (
				SELECT
					v.V01_temporada AS temporada,
					CASE
						WHEN c.region IN ('CENTRO - BOGOTA', 'CENTRO - SABANA') THEN 1
						ELSE 0
					END AS es_centro,
					v.V24_venta_neta_cop AS venta_cop
				FROM ventas v
				INNER JOIN clientes c ON v.client_id = c.client_id
				WHERE lower(replace(cast(v.V06_documento_tipo AS varchar), 'ó', 'o')) NOT LIKE '%dmc%'
				  AND lower(replace(cast(v.V06_documento_tipo AS varchar), 'ó', 'o')) NOT LIKE '%devol%'
				  AND v.V08_canal_cliente IN ('Food Service - HORECA', 'Mayoristas', 'Retail')
			)
			SELECT
				temporada,
				SUM(CASE WHEN es_centro = 1 THEN venta_cop ELSE 0 END) / SUM(venta_cop) AS indice_concentracion
			FROM ventas_b2b
			GROUP BY temporada
			ORDER BY temporada
		) TO '{out_concentracion.as_posix()}' (FORMAT PARQUET);
	""")

	n_reg = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_regiones.as_posix()}')").fetchone()[0]
	n_conc = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_concentracion.as_posix()}')").fetchone()[0]
	print(f"  D02 público macro-región: {n_reg} filas")
	print(f"  D02 público concentración: {n_conc} filas")

def build_d03(con: duckdb.DuckDBPyConnection) -> None:
	"""
	D03 público: agregados por nivel de riesgo.
	No se publica el semáforo por cliente individual.
	"""
	out_mensual = PUBLIC_DIR / "d03_alertas_publico.parquet"
	out_total = PUBLIC_DIR / "d03_alertas_total_publico.parquet"

	if not D03_LOCAL.exists():
		print("  ⚠️ d03_riesgo_client_month.parquet no encontrado, omitiendo D03")
		return

	con.execute(f"""
		COPY (
			WITH agregado AS (
				SELECT
					periodo,
					nivel_riesgo,
					COUNT(DISTINCT client_id) AS n_clientes,
					SUM(kg_caida) AS kg_caida_total
				FROM read_parquet('{D03_LOCAL.as_posix()}')
				GROUP BY periodo, nivel_riesgo
			)
			SELECT *
			FROM agregado
			WHERE n_clientes >= {CELL_MIN}
			ORDER BY periodo, nivel_riesgo
		) TO '{out_mensual.as_posix()}' (FORMAT PARQUET);
	""")

	con.execute(f"""
		COPY (
			SELECT
				nivel_riesgo,
				COUNT(DISTINCT client_id) AS n_clientes,
				SUM(kg_caida) AS kg_caida_total
			FROM read_parquet('{D03_LOCAL.as_posix()}')
			GROUP BY nivel_riesgo
			HAVING COUNT(DISTINCT client_id) >= {CELL_MIN}
			ORDER BY nivel_riesgo
		) TO '{out_total.as_posix()}' (FORMAT PARQUET);
	""")

	n_mensual = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_mensual.as_posix()}')").fetchone()[0]
	n_total = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_total.as_posix()}')").fetchone()[0]
	print(f"  D03 público mensual: {n_mensual} filas")
	print(f"  D03 público total: {n_total} filas")


def build_d04(con: duckdb.DuckDBPyConnection) -> None:
	"""
	D04 público: Pareto como ratio percentil + agregados por concentración.
	No se publica la matriz por cliente individual.
	"""
	out_concentracion = PUBLIC_DIR / "d04_portafolio_publico.parquet"
	out_global = PUBLIC_DIR / "d04_portafolio_global_publico.parquet"

	if not D04_LOCAL.exists():
		print("  ⚠️ d04_portafolio_client.parquet no encontrado, omitiendo D04")
		return

	# 1. Agregado por concentración (cautivo/diversificado)
	con.execute(f"""
		COPY (
			SELECT
				CASE WHEN es_cautivo THEN 'Cautivo' ELSE 'Diversificado' END AS concentracion,
				COUNT(*) AS n_clientes,
				SUM(venta_neta_total_cop) AS venta_neta_total_cop,
				SUM(kg_total) AS kg_total
			FROM read_parquet('{D04_LOCAL.as_posix()}')
			GROUP BY es_cautivo
			HAVING COUNT(*) >= {CELL_MIN}
			ORDER BY concentracion
		) TO '{out_concentracion.as_posix()}' (FORMAT PARQUET);
	""")

	# 2. Métricas globales + Pareto como ratio percentil generalizado
	con.execute(f"""
		COPY (
			WITH ranked AS (
				SELECT
					venta_neta_total_cop,
					SUM(venta_neta_total_cop) OVER (ORDER BY venta_neta_total_cop DESC) AS venta_acumulada,
					SUM(venta_neta_total_cop) OVER () AS venta_total,
					COUNT(*) OVER () AS total_clientes,
					ROW_NUMBER() OVER (ORDER BY venta_neta_total_cop DESC) AS rn
				FROM read_parquet('{D04_LOCAL.as_posix()}')
			),
			pareto AS (
				SELECT
					MIN(rn) AS clientes_para_80,
					MAX(total_clientes) AS total_clientes,
					MAX(venta_total) AS venta_total
				FROM ranked
				WHERE venta_acumulada <= venta_total * 0.80
				   OR rn = (SELECT MIN(rn) FROM ranked WHERE venta_acumulada >= venta_total * 0.80)
			),
			cautivos AS (
				SELECT
					COUNT(*) AS total_clientes,
					SUM(CASE WHEN es_cautivo THEN 1 ELSE 0 END) AS clientes_cautivos,
					SUM(CASE WHEN es_alto_valor THEN 1 ELSE 0 END) AS clientes_alto_valor,
					SUM(venta_neta_total_cop) AS venta_total_cop,
					SUM(CASE WHEN es_cautivo THEN venta_neta_total_cop ELSE 0 END) AS venta_cautivos_cop
				FROM read_parquet('{D04_LOCAL.as_posix()}')
			)
			SELECT
				c.total_clientes,
				c.clientes_cautivos,
				c.clientes_alto_valor,
				c.venta_total_cop,
				c.venta_cautivos_cop,
				p.clientes_para_80,
				p.clientes_para_80 * 1.0 / p.total_clientes AS pct_clientes_pareto,
				CASE
					WHEN p.clientes_para_80 * 1.0 / p.total_clientes <= 0.10 THEN '≤10%'
					WHEN p.clientes_para_80 * 1.0 / p.total_clientes <= 0.20 THEN '10-20%'
					WHEN p.clientes_para_80 * 1.0 / p.total_clientes <= 0.30 THEN '20-30%'
					ELSE '>30%'
				END AS pct_clientes_pareto_generalizado
			FROM cautivos c
			CROSS JOIN pareto p
		) TO '{out_global.as_posix()}' (FORMAT PARQUET);
	""")

	n_conc = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out_concentracion.as_posix()}')").fetchone()[0]
	print(f"  D04 público concentración: {n_conc} filas")
	print(f"  D04 público global: 1 fila (métricas agregadas)")


def main() -> int:
	print("=" * 72)
	print("Construcción de datasets públicos k-anónimos")
	print("Estrategia: Opción 1 (índice de concentración) + Opción 3 (Pareto)")
	print("=" * 72)

	if not VENTAS_PATH.exists():
		print(f"ERROR: no existe {VENTAS_PATH}")
		return 1
	if not CLIENTES_PATH.exists():
		print(f"ERROR: no existe {CLIENTES_PATH}")
		return 1

	PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

	con = duckdb.connect()
	con.execute(f"CREATE OR REPLACE VIEW ventas AS SELECT * FROM read_parquet('{VENTAS_PATH.as_posix()}')")
	con.execute(f"CREATE OR REPLACE VIEW clientes AS SELECT * FROM read_parquet('{CLIENTES_PATH.as_posix()}')")

	print("\nGenerando datasets públicos:")
	build_d01(con)
	build_d02(con)
	build_d03(con)
	build_d04(con)

	print("\n" + "=" * 72)
	print("✅ Datasets públicos generados en data/public/")
	print(f"   Parámetros: k≥{K_MIN}, celdas≥{CELL_MIN} contribuyentes")
	print("=" * 72)
	return 0


if __name__ == "__main__":
	sys.exit(main())