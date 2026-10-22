# Herramientas de validación

Scripts que respaldan la sección de gobernanza del README y el reporte
`data/public/validacion.txt`.

## `validacion_anonimizacion.py` (maestro)

Ejecuta los **5 ataques estándar de anonimización** más el **test de
reconstrucción de precio** sobre todos los parquet en `data/public/`. Genera
un reporte en texto que reemplaza `data/public/validacion.txt`.

### Ataques que ejecuta

| # | Ataque | Qué verifica |
|---|---|---|
| 1 | Singularización | Ninguna celda con `n_clientes < K_MIN` |
| 2 | Membresía | Ninguna celda con `n_clientes == 1` |
| 3 | Divulgación de atributo | Ninguna celda es complemento de < `CELL_MIN` clientes |
| 4 | Identificadores | Ninguna columna con patrón de PII o ID |
| 5 | Celdas ≥ `CELL_MIN` | Todo agregado respeta el umbral |
| 6 | Reconstrucción de precio | Ningún ratio COP/kg estable (precio unitario reconstruible) |

### Uso

```bash
# Desde la raíz del repositorio
pip install polars pyarrow
python tools/validacion_anonimizacion.py --out data/public/validacion.txt
```

### Salida

- Reporte completo en `data/public/validacion.txt`.
- Código de salida `0` si PASS global, `1` si FAIL.

### Cuándo ejecutarlo

Cada vez que se regeneren los parquet públicos con `build_public.py`, antes
del commit. El reporte resultante es la evidencia que respalda el
`LICENSE-DATA` y el `cerebro-berries-public.md`.

### Riesgo de precio

El dataset actual contiene `venta_neta_cop` y `kg_total` coexistentes en
`d01`, `d02` y `d04`. El test 6 evalúa si el ratio COP/kg es lo suficientemente
disperso para no reconstruir un precio unitario estable. Si el veredicto es
`PASS-WITH-RISK`, debe quedar documentado en `cerebro-berries-public.md`
sección 6 (limitaciones), como hace la versión pública de `cosecha-public`.

---

## `validacion_precio.py` (standalone)

Versión reducida del test de precio, útil para CI o para ejecutar rápido
sin correr todos los ataques. Si usas el script maestro, este queda
redundante.

### Uso

```
python tools/validacion_precio.py --data-dir data/public
```

---

## Cómo integrarlo en el flujo de trabajo

```
# 1. Regenerar datos
uv run python -m berrix.build_public    # o: python src/berrix/build_public.py

# 2. Validar
python tools/validacion_anonimizacion.py --out data/public/validacion.txt

# 3. Verificar que PASS antes de commitear
if grep -q "^FAIL" data/public/validacion.txt; then
  echo "Validación fallida. No commitear."
  exit 1
fi

# 4. Commitear datos + reporte
git add data/public/ tools/
git commit -m "Regenerate public data and validation report"
```

---

## Dependencias

```
pip install polars pyarrow
