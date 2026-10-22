#!/usr/bin/env python3
"""
validacion_anonimizacion.py — Validación de anonimización y precio
Repositorio: ag-agrodata/berries-dashboard

Ejecuta los 5 ataques estándar de anonimización más el test de reconstrucción
de precio sobre los parquet públicos en data/public/. Genera un reporte en
texto que reemplaza data/public/validacion.txt.

Ataques:
  1. Singularización          — ninguna celda con n_clientes < K_MIN
  2. Membresía                — ninguna combinación única de quasi-IDs aísla 1 cliente
  3. Divulgación de atributo  — solo aplica si n_clientes particiona el universo;
                                verifica que ninguna celda sea complemento de < CELL_MIN
  4. Identificadores          — ninguna columna con patrón de PII o ID
  5. Celdas ≥ CELL_MIN        — todo agregado respeta el umbral

Test adicional:
  6. Reconstrucción de precio — ninguna combinación COP+kg permite ratio estable
                                Solo evalúa si hay al menos MIN_RATIOS_OBS observaciones.

Uso:
    uv run python tools/validacion_anonimizacion.py --out data/public/validacion.txt
    python tools/validacion_anonimizacion.py --data-dir data/public

Salida:
    Reporte en texto + código de salida 0 (PASS global) o 1 (FAIL).

Dependencias: polars, pyarrow (ya en requirements.txt)
"""

from __future__ import annotations

import argparse
import hashlib
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import polars as pl
except ImportError:
    sys.exit("ERROR: se requiere polars. Instala con: pip install polars pyarrow")

# ============================================================================
# Parámetros de validación
# ============================================================================
K_MIN = 5
CELL_MIN = 10

# Patrones de identificadores directos e indirectos (case-insensitive)
IDENTIFIER_PATTERNS = [
    "client_id", "worker_id", "employee_id", "customer_id", "user_id",
    "_uuid", "uuid", "email", "phone", "telefono", "celular",
    "name", "nombre", "apellido", "cedula", "dni", "passport",
    "address", "direccion", "postal", "codigo_postal",
    "latitud", "longitud", "latitude", "longitude", "lat", "lon",
    "date", "fecha_exacta", "timestamp",
]

# Patrones de precio (para el test 6)
PRICE_HINTS = [
    "cop", "usd", "valor", "precio", "price", "revenue", "venta_valor",
    "facturacion", "margen", "margin", "descuento", "discount",
    "ingreso", "income", "monto", "amount", "total_cop", "total_usd",
    "valor_total", "valor_unitario", "precio_unitario", "ticket",
]

# Patrones de volumen (para el test de precio)
VOLUME_HINTS = ["kg", "kilo", "kilogramo", "weight", "peso", "volumen", "volume"]

# Tolerancia de CV para considerar que el ratio es "estable" (precio reconstruible)
PRICE_CV_TOLERANCE = 0.05

# Mínimo de observaciones para que el CV sea informativo
MIN_RATIOS_OBS = 5

# Tolerancia de suma para considerar que n_clientes particiona el universo
# (test 3). Si la suma se aleja más de 20% del total, el test no aplica.
PARTITION_TOLERANCE = 0.20

# ============================================================================
# Helpers
# ============================================================================

def sha256_of(path: Path) -> str:
    """Hash SHA-256 truncado para el reporte."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

def find_cols(columns: list[str], patterns: list[str]) -> list[str]:
    """Columnas cuyo nombre coincida (parcial, case-insensitive) con algún patrón."""
    out = []
    for col in columns:
        low = col.lower()
        if any(p in low for p in patterns):
            out.append(col)
    return out

def write_section(lines: list[str], title: str) -> None:
    lines.append("")
    lines.append("=" * 80)
    lines.append(title)
    lines.append("=" * 80)

# ============================================================================
# Test 1 · Singularización
# ============================================================================

def test_singularization(df: pl.DataFrame, name: str) -> tuple[bool, str]:
    """Verifica que ninguna celda tenga n_clientes < K_MIN."""
    if "n_clientes" not in df.columns:
        return True, "sin columna n_clientes (aplica por diseño)"

    bad = df.filter(pl.col("n_clientes") < K_MIN)
    if bad.height == 0:
        return True, f"OK — {df.height} celdas, min(n_clientes)={df['n_clientes'].min()}"

    return False, f"FAIL — {bad.height} celdas con n_clientes < {K_MIN}"

# ============================================================================
# Test 2 · Membresía
# ============================================================================

def test_membership(df: pl.DataFrame, name: str) -> tuple[bool, str]:
    """
    Riesgo de membresía: ¿alguna combinación de quasi-ID aísla 1 cliente?
    Aproximación: verificar que ninguna celda tenga n_clientes == 1.
    """
    if "n_clientes" not in df.columns:
        return True, "sin columna n_clientes — riesgo bajo por agregación"

    with_one = df.filter(pl.col("n_clientes") == 1)
    if with_one.height == 0:
        return True, "OK — ninguna celda con n_clientes == 1"

    return False, f"FAIL — {with_one.height} celdas con n_clientes == 1"

# ============================================================================
# Test 3 · Divulgación de atributo
# ============================================================================

def test_attribute_disclosure(
    df: pl.DataFrame, name: str, total_clients: int | None
) -> tuple[bool, str]:
    """
    ¿Alguna celda representa "todos menos < CELL_MIN clientes"?

    IMPORTANTE: este test solo tiene sentido cuando la columna n_clientes
    PARTICIONA el universo (cada cliente pertenece a una y solo una fila).
    Ejemplos donde NO aplica:
      - Series temporales (un cliente puede estar en varias temporadas)
      - Agregados por canal donde un cliente compra por varios canales

    Heurística: si la suma de n_clientes se aleja más del 20% del total
    de referencia, el test no aplica (no hay partición).
    """
    if "n_clientes" not in df.columns or total_clients is None:
        return True, "sin n_clientes o sin total de referencia — no verificable"

    suma = int(df["n_clientes"].sum())
    diff_rel = abs(suma - total_clients) / total_clients if total_clients else 0

    if diff_rel > PARTITION_TOLERANCE:
        return True, (
            f"no aplicable — n_clientes no particiona el universo "
            f"(suma={suma}, total={total_clients}, diff={diff_rel:.0%} > {PARTITION_TOLERANCE:.0%})"
        )

    risky = df.filter(
        (pl.col("n_clientes") > 0)
        & (pl.col("n_clientes") < total_clients)
        & ((total_clients - pl.col("n_clientes")) < CELL_MIN)
    )
    if risky.height == 0:
        return True, (
            f"OK — partición detectada (suma={suma}, total={total_clients}); "
            f"ninguna celda complementaria de tamaño < {CELL_MIN}"
        )

    return False, (
        f"FAIL — {risky.height} celdas representan complemento de < {CELL_MIN} clientes"
    )

# ============================================================================
# Test 4 · Identificadores directos e indirectos
# ============================================================================

def test_identifiers(columns: list[str], name: str) -> tuple[bool, str, list[str]]:
    """Escanear columnas contra patrones de PII / IDs."""
    suspects = find_cols(columns, IDENTIFIER_PATTERNS)
    if not suspects:
        return True, f"OK — {len(columns)} columnas sin patrones de PII", []

    return False, f"FAIL — columnas sospechosas: {suspects}", suspects

# ============================================================================
# Test 5 · Celdas ≥ CELL_MIN
# ============================================================================

def test_cell_threshold(df: pl.DataFrame, name: str) -> tuple[bool, str]:
    """Verifica n_clientes >= CELL_MIN en archivos con esa columna."""
    if "n_clientes" not in df.columns:
        return True, "sin n_clientes — aplica por diseño (agregado global o índice)"

    below = df.filter(pl.col("n_clientes") < CELL_MIN)
    if below.height == 0:
        return True, f"OK — todas las celdas ≥ {CELL_MIN}"

    return False, f"FAIL — {below.height} celdas con n_clientes < {CELL_MIN}"

# ============================================================================
# Test 6 · Reconstrucción de precio
# ============================================================================

def test_price_reconstruction(
    df: pl.DataFrame, name: str
) -> tuple[bool, str, list[str]]:
    """
    Detecta vectores de reconstrucción de precio unitario.
    PASS si no hay columnas de precio.
    PASS si hay precio y volumen pero pocas observaciones (< MIN_RATIOS_OBS).
    PASS-WITH-RISK si el ratio es disperso.
    FAIL si hay columnas de precio explícitas (precio_unitario, margen, etc.)
       o si el ratio es estable (CV < PRICE_CV_TOLERANCE).
    """
    cols = df.columns
    price_cols = find_cols(cols, PRICE_HINTS)
    volume_cols = find_cols(cols, VOLUME_HINTS)

    # FAIL directo si hay columnas explícitamente de precio unitario o margen
    hard_fail = [
        c for c in price_cols
        if any(k in c.lower() for k in ["unitario", "unit", "margen", "margin", "descuento"])
    ]
    if hard_fail:
        return False, f"FAIL — columnas de precio explícitas: {hard_fail}", hard_fail

    if not price_cols:
        return True, "OK — sin columnas de precio", []

    if not volume_cols:
        return True, (
            f"PASS — precio sin volumen ({price_cols}); ratio no reconstruible"
        ), []

    # Hay precio y volumen: evaluar estabilidad del ratio
    p = price_cols[0]
    v = volume_cols[0]
    try:
        ratios = (
            df.select((pl.col(p) / pl.col(v)).alias("ratio"))
            .filter(pl.col("ratio").is_not_null() & pl.col("ratio").is_finite())
        )

        if ratios.height < MIN_RATIOS_OBS:
            return True, (
                f"PASS — ratio {p}/{v} no evaluable "
                f"(n={ratios.height} < {MIN_RATIOS_OBS})"
            ), []

        mean = ratios["ratio"].mean()
        std = ratios["ratio"].std()
        cv = (std / mean) if mean and mean != 0 else None

        if cv is None:
            return True, f"PASS — ratio {p}/{v} no evaluable (media nula)", []

        if cv < PRICE_CV_TOLERANCE:
            return False, (
                f"FAIL — ratio {p}/{v} estable (CV={cv:.4f} < {PRICE_CV_TOLERANCE}); "
                f"precio unitario reconstruible"
            ), [f"{p}/{v}"]

        return True, (
            f"PASS-WITH-RISK — ratio {p}/{v} presente pero disperso "
            f"(CV={cv:.4f}); no reconstruye precio unitario estable"
        ), []

    except Exception as exc:  # noqa: BLE001
        return False, f"ERROR — no se pudo evaluar ratio {p}/{v}: {exc}", []

# ============================================================================
# Orquestación
# ============================================================================

def run(data_dir: Path) -> tuple[str, bool]:
    parquet_files = sorted(data_dir.glob("*.parquet"))
    if not parquet_files:
        return f"ERROR: no hay parquet en {data_dir}", False

    # Total de clientes (para test 3): se toma del global si existe
    total_clients = None
    global_path = data_dir / "d04_portafolio_global_publico.parquet"
    if global_path.exists():
        try:
            g = pl.read_parquet(global_path)
            if "total_clientes" in g.columns and g.height == 1:
                total_clients = int(g["total_clientes"][0])
        except Exception:
            pass

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("REPORTE DE VALIDACIÓN DE ANONIMIZACIÓN")
    lines.append("berries-dashboard · data/public/")
    lines.append("=" * 80)
    lines.append("")
    lines.append(
        f"Fecha de ejecución:   {datetime.now(timezone.utc).isoformat(timespec='seconds')}"
    )
    lines.append(f"Python:               {platform.python_version()}")
    lines.append(f"Polars:               {pl.__version__}")
    lines.append(f"Directorio:           {data_dir.resolve()}")
    lines.append(f"Archivos .parquet:    {len(parquet_files)}")
    lines.append(
        f"Total de clientes:    {total_clients if total_clients else 'no detectado'}"
    )
    lines.append(f"Parámetros:           K_MIN={K_MIN}, CELL_MIN={CELL_MIN}")

    write_section(lines, "HASHES SHA-256 (truncados)")
    for p in parquet_files:
        lines.append(f"  {p.name:45s}  {sha256_of(p)}")

    global_pass = True
    all_suspects: dict[str, list[str]] = {}

    for p in parquet_files:
        try:
            df = pl.read_parquet(p)
        except Exception as exc:  # noqa: BLE001
            write_section(lines, f"{p.name} — ERROR DE LECTURA")
            lines.append(f"  {exc}")
            global_pass = False
            continue

        write_section(
            lines, f"{p.name}  ({df.height} filas, {len(df.columns)} columnas)"
        )

        ok1, msg1 = test_singularization(df, p.name)
        lines.append(f"  [1] Singularización:          {'PASS' if ok1 else 'FAIL'} — {msg1}")
        global_pass &= ok1

        ok2, msg2 = test_membership(df, p.name)
        lines.append(f"  [2] Membresía:                {'PASS' if ok2 else 'FAIL'} — {msg2}")
        global_pass &= ok2

        ok3, msg3 = test_attribute_disclosure(df, p.name, total_clients)
        lines.append(f"  [3] Divulgación de atributo:  {'PASS' if ok3 else 'FAIL'} — {msg3}")
        global_pass &= ok3

        ok4, msg4, suspects = test_identifiers(df.columns, p.name)
        lines.append(f"  [4] Identificadores:          {'PASS' if ok4 else 'FAIL'} — {msg4}")
        global_pass &= ok4
        if suspects:
            all_suspects[p.name] = suspects

        ok5, msg5 = test_cell_threshold(df, p.name)
        lines.append(
            f"  [5] Celdas ≥ {CELL_MIN}:           {'PASS' if ok5 else 'FAIL'} — {msg5}"
        )
        global_pass &= ok5

        ok6, msg6, _ = test_price_reconstruction(df, p.name)
        lines.append(f"  [6] Reconstrucción de precio: {'PASS' if ok6 else 'FAIL'} — {msg6}")
        global_pass &= ok6

    write_section(lines, "VEREDICTO GLOBAL")
    if global_pass:
        lines.append(
            "PASS — todos los ataques superados. Reporte válido como verificación."
        )
    else:
        lines.append("FAIL — al menos un ataque no superado. Resolver antes de publicar.")

    if all_suspects:
        lines.append("")
        lines.append("Columnas sospechosas (revisar manualmente):")
        for name, cols in all_suspects.items():
            lines.append(f"  {name}: {cols}")

    return "\n".join(lines), global_pass

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validación de anonimización y precio sobre data/public/*.parquet"
    )
    parser.add_argument(
        "--data-dir", default="data/public", help="Directorio con parquet públicos"
    )
    parser.add_argument(
        "--out", default="validacion_anonimizacion.txt", help="Archivo de salida"
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        sys.exit(f"ERROR: no existe {data_dir}")

    report, ok = run(data_dir)
    print(report)
    Path(args.out).write_text(report + "\n", encoding="utf-8")
    print(f"\nReporte guardado en: {args.out}")

    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
