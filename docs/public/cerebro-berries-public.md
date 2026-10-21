# Cerebro del proyecto · berries-dashboard

**Versión pública** · 21 de octubre de 2026  
**Autor:** Andrés Gómez · Agribusiness Data Analyst  
**Repositorio:** `github.com/ag-agrodata/berries-dashboard`

Este documento es el registro de decisiones, supuestos, glosario y limitaciones del tablero comercial B2B. Su objetivo es que cualquier revisor pueda auditar el razonamiento detrás del dashboard sin necesidad de leer el código ni acceder a los datos originales.

---

## 1. Propósito y alcance

**Qué es:** un tablero que traduce transacciones de venta B2B de una empresa agroindustrial de berries en cuatro preguntas de decisión para un comité comercial: ventas por canal, dinámica regional, alertas de retención y portafolio de clientes.

**Qué no es:** no es un sistema transaccional, no reemplaza al ERP, no produce pronósticos, no recomienda precios. Es una capa de lectura sobre datos ya consolidados.

**Alcance del dataset público:** 33 clientes B2B, 3 canales comerciales (tras supresión), 2 macro-regiones, múltiples temporadas. Los datos son derivados k-anónimos del caso real, publicados conforme al NDA con el cliente (ver [`LICENSE-DATA`](LICENSE-DATA)).

**Fases del proyecto:** el caso pasó por cuatro fases antes de llegar aquí (trabajo con la empresa → entrega en Excel + Tableau → réplica en Streamlit → anonimización y publicación). La historia completa está en la sección "Las cuatro fases" de los READMEs. Esa cadena es parte del valor del caso y no debe perderse en la documentación interna.

---

## 2. Fuentes de datos y pipeline

**Fuente original:** hojas de cálculo de la empresa con pedidos, despachos, informe de ventas y facturación. Consolidadas localmente en `data/processed/anon/ventas_local.parquet` y `clientes_local.parquet` (pseudonimizados).

**Pipeline público:** `src/berrix/build_public.py` genera los 8 archivos en `data/public/` desde los datos locales pseudonimizados, aplicando las técnicas de anonimización de la sección 3.

**Consumo en la app:** `src/berrix/app_public.py` carga los 8 parquet con Polars y los renderiza con Streamlit + Plotly. La capa bilingüe ES/EN está en `src/berrix/i18n.py`.

**Frecuencia de actualización:** el dataset público es una foto estática del caso; no se refresca automáticamente. La versión interna (no publicada) sí se actualiza con la operación real.

---

## 3. Registro de decisiones (D01–D14)

Cada decisión está justificada. Las que no tienen evidencia cuantitativa lo indican explícitamente y remiten a la sección 6 (limitaciones).

### D01 · Métricas precio-neutrales en kilogramos para las alertas de retención

**Decisión:** las alertas del semáforo (tab 03) se calculan en kilogramos, no en pesos.  
**Justificación:** un cambio de precio no debe hacer parecer que un cliente compra menos cuando compra lo mismo. Usar valor monetario activaría falsas alertas de fuga por variación de precio.  
**Impacto:** elimina un sesgo clásico de alertas de retención. Es la decisión más citada del proyecto.

### D02 · Semáforo de retención con condición de sostenibilidad

**Decisión:** una caída de un solo mes no activa alerta. Se requieren **dos meses consecutivos** para confirmar tendencia.  
**Justificación:** la estacionalidad mensual del negocio de berries produce caídas de un mes que no son señal de fuga. Se probaron ventanas de 1, 2 y 3 meses: 1 disparaba ruido, 3 llegaba tarde al comité.  
**Evidencia:** operativa, no backtest formal (ver limitación L01).

### D03 · Regla de oro del universo B2B

**Decisión:** toda transacción que no hace match con la tabla de clientes objetivo queda fuera del análisis. No se imputa ni se aproxima.  
**Justificación:** mantener el universo limpio y evitar contaminación con transacciones no atribuibles (mostrador, devoluciones sin cliente, movimientos internos).  
**Impacto:** reduce el ruido del análisis y hace defendible cada cifra del tablero.

### D04 · Canales visibles solo con ≥10 contribuyentes

**Decisión:** el canal Retail (8 clientes) se suprime en el nivel público. Solo se muestran Food Service-HORECA y Mayoristas.  
**Justificación:** celdas con <10 contribuyentes violan el umbral `CELL_MIN = 10` del NDA.  
**Impacto:** el análisis público de canal queda incompleto por diseño; el análisis completo existe en el nivel local pseudonimizado.

### D05 · Regiones generalizadas a macro-regiones

**Decisión:** las 7 regiones originales se agrupan en 2 macro-regiones: "Centro" (Bogotá + Sabana) y "Resto de regiones".  
**Justificación:** varias regiones originales tenían <10 clientes; agruparlas garantiza k ≥ 5 y celdas ≥ 10.  
**Impacto:** se pierde granularidad regional fina. La vista D02 muestra solo concentración Centro vs Resto.

### D06 · Cuentas nacionales diluidas en "Resto de regiones"

**Decisión:** los 3 clientes con cobertura nacional se agrupan en "Resto de regiones".  
**Justificación:** una categoría "Nacional" con 3 clientes sería singularizable.  
**Impacto:** coherente con D05; refuerza la protección de clientes atípicos.

### D07 · Pareto como ratio percentil generalizado

**Decisión:** el índice de Pareto no se publica como número exacto, sino como bucket: `≤10%`, `10-20%`, `20-30%`, `>30%`.  
**Justificación:** publicar el número exacto de "clientes que acumulan el 80% de la venta" permitiría inferir la distribución de la base.  
**Impacto:** se conserva la lectura cualitativa (cuán concentrada es la base) sin exponer el dato fino.

### D08 · D04 agregado por concentración, no matriz por cliente

**Decisión:** la vista de portafolio (tab 04) muestra agregados por tipo de concentración (Cautivo / Diversificado) y métricas globales, no la matriz cliente × especie.  
**Justificación:** la matriz por cliente identificaría a los clientes individuales.  
**Impacto:** el comité pierde la vista operativa de cuentas individuales; la gana la protección del NDA.

### D09 · Umbral de cautividad

**Decisión:** un cliente es "Cautivo" si ≥80% de su volumen está en una sola especie.  
**Justificación:** criterio operativo del comité comercial. Es un umbral defendible de mono-dependencia.  
**Evidencia:** criterio de negocio, no estadístico.

### D10 · Actividad mínima del cliente

**Decisión:** un cliente se considera activo si tiene ≥2 meses de compra en la ventana analizada.  
**Justificación:** clientes con 1 sola compra producen métricas inestables (retención, Pareto, promedio).  
**Impacto:** reduce el universo a clientes con señal suficiente.

### D11 · Línea base de alertas

**Decisión:** la caída de retención se mide contra el promedio móvil de los 3 meses calendario anteriores.  
**Justificación:** suaviza la estacionalidad semanal y mensual sin perder sensibilidad a tendencias.  
**Evidencia:** criterio operativo.

### D12 · Umbrales de nivel de riesgo

**Decisión:**
- 🟢 Estable: caída <15% o no sostenida
- 🟡 Riesgo medio: caída ≥15% y <30%, sostenida 2 meses
- 🔴 Alto riesgo: caída ≥30%, sostenida 2 meses

**Justificación:** calibración operativa del comité comercial. No hay backtest formal.  
**Impacto:** el semáforo discrimina tres niveles de urgencia sin ahogar al comité en alertas.

### D13 · Parámetros de anonimización

**Decisión:** `K_MIN = 5`, `CELL_MIN = 10` en `build_public.py`.  
**Justificación:** umbrales definidos en el Anexo A del NDA.  
**Impacto:** toda celda publicada cumple ambos umbrales por construcción.

### D14 · Filtro del universo comercial

**Decisión:** el universo se filtra a transacciones de venta comercial neta, excluyendo documentos que no representan venta (movimientos internos, devoluciones contables) y canales fuera del universo B2B objetivo.
**Justificación:** los movimientos internos y las devoluciones no representan venta comercial neta; su inclusión distorsionaría el análisis.
**Impacto:** el tablero mide venta comercial neta, no movimiento contable bruto.

---

## 4. Registro de supuestos (S01–S09)

| ID | Supuesto | Implicación si falla |
|---|---|---|
| S01 | Los datos locales pseudonimizados son representativos del negocio real | El análisis sería un artefacto sin valor operativo |
| S02 | La temporada es la unidad temporal principal del negocio de berries | Cambiar a mes-año alteraría las vistas D01/D02 |
| S03 | El mes calendario es la unidad adecuada para las alertas de retención | Cambiar a semana aumentaría el ruido; a trimestre, la latencia |
| S04 | Los umbrales de riesgo (15%, 30%) están alineados con la política comercial del cliente | Un umbral distinto cambiaría la distribución de niveles |
| S05 | Una ventana de 2 meses es el mínimo operativo aceptable para confirmar tendencia | Sin backtest formal, es un criterio de negocio |
| S06 | El canal comercial es el eje relevante para la lectura de ventas | Si el cliente prioriza especie o región, la vista D01 pierde relevancia |
| S07 | Agrupar Bogotá + Sabana en "Centro" es una generalización aceptable | Si la dinámica comercial difiere entre ambas, la macro-región oculta señal |
| S08 | El Pareto se calcula sobre venta neta, no sobre kg | Cambiar la métrica alteraría el bucket resultante |
| S09 | Un cliente con ≥2 meses de compra es "activo" | Si el ciclo de compra es más largo, el umbral subestima la base activa |

---

## 5. Glosario operativo

- **Venta neta (COP/USD):** venta después de descuentos, sin devoluciones ni movimientos internos.
- **kg:** kilogramos de producto vendidos. Métrica precio-neutral.
- **Canal comercial:** segmento de cliente (Food Service-HORECA, Mayoristas, Retail).
- **Macro-región:** agrupación geográfica (Centro, Resto de regiones). Reemplaza las 7 regiones originales.
- **Temporada:** unidad temporal del negocio (según calendario de cosecha).
- **Nivel de riesgo:** clasificación del semáforo de retención (alto, medio, estable).
- **Cautivo:** cliente con ≥80% de su volumen en una sola especie.
- **Diversificado:** cliente con volumen repartido en ≥2 especies.
- **Pareto (bucket):** concentración de venta en el top de clientes, expresada en rango (≤10%, 10-20%, etc.).
- **k-anonimato:** propiedad por la cual cada celda publicada tiene al menos k contribuyentes (aquí k ≥ 5).
- **Supresión de celdas:** eliminar celdas con <10 contribuyentes para evitar singularización.
- **Generalización:** reducir granularidad de una categoría (ej. 7 regiones → 2 macro-regiones).

---

## 6. Limitaciones conocidas

### L01 · Sin backtest formal de la ventana de retención

La ventana de 2 meses (D02) es un criterio operativo. Un backtest histórico sobre datos reales permitiría calibrar el trade-off sensibilidad/latencia. Es un trabajo pendiente.

### L02 · Riesgo residual de reidentificación

El reporte [`data/public/validacion.txt`](data/public/validacion.txt) documenta el estado de los 5 ataques estándar y el test de reconstrucción de precio. Cualquier riesgo residual está explicitado allí y debe leerse antes de interpretar la garantía de anonimización como absoluta.

### L03 · Análisis de canal incompleto en el nivel público

Retail (8 clientes) está suprimido por D04. El análisis público cubre solo 2 de los 3 canales comerciales. La lectura completa existe en el nivel local pseudonimizado.

### L04 · Granularidad regional reducida

Las 7 regiones originales se colapsan a 2 macro-regiones (D05). El análisis público no distingue Bogotá de Sabana, ni las regiones del Resto.

### L05 · Pareto generalizado a buckets

El índice de Pareto se publica como rango (D07), no como número. La lectura cuantitativa fina no está disponible en el nivel público.

### L06 · Sin información de margen ni costo

El dataset solo contiene venta neta y kg. No hay costo, margen ni rentabilidad. El análisis es de volumen y mezcla comercial, no de rentabilidad.

### L07 · Sin información de precio

Por condición expresa del NDA, no se publican precios, márgenes ni términos contractuales. El dataset público no permite reconstruir precios unitarios (verificado por `tools/validacion_precio.py`).

---

## 7. Gobernanza y validación

- **Parámetros:** `K_MIN = 5`, `CELL_MIN = 10` (D13).
- **Técnicas aplicadas:** agregación, k-anonimato, supresión de celdas, generalización, redondeo y perturbación.
- **Reporte de validación:** [`data/public/validacion.txt`](data/public/validacion.txt).
- **Herramientas de verificación:** [`tools/validacion_precio.py`](tools/validacion_precio.py) (test de reconstrucción de precio).
- **Licencia de los datos:** [`LICENSE-DATA`](LICENSE-DATA) (DUA).
- **Marco legal:** NDA con el cliente. La publicación de derivados fue autorizada bajo la condición de no identificabilidad y no inferencia de precios.

---

## 8. Roadmap público

Trabajo pendiente, en orden de prioridad:

1. **Ejecutar y publicar el reporte de validación completo** (`data/public/validacion.txt`) con los 5 ataques estándar y el test de precio.
2. **Backtest formal de la ventana de retención** (L01): probar ventanas de 1, 2, 3 y 4 meses sobre histórico y medir precisión de detección de fugas reales.
3. **Diccionario de datos** (`data/public/README.md`): esquema de cada parquet, columnas, tipos y cobertura.
4. **Añadir el test de precio a `validacion.txt`** cuando exista el reporte completo.
5. **Versión sintética del dataset** para análisis sin NDA: mismo esquema, datos generados, cero vínculo con el cliente.
6. **Ampliar la vista de portafolio** con una lectura de mezcla por especie (sin identificar clientes), si el NDA lo permite.

---

## 9. Contacto

**Andrés Gómez**  
Agribusiness Data Analyst  
afgomez.agroindustrial@gmail.com  
[github.com/ag-agrodata](https://github.com/ag-agrodata)

Para consultas sobre decisiones, supuestos o limitaciones de este documento, o para reportar un posible incumplimiento del acuerdo de confidencialidad, escribir al correo arriba.
