[🇬🇧 English](README.md) · [🇪🇸 Español](README.es.md)

<img src="src/berrix/assets/ag6.svg" alt="AG · Andrés Gómez" width="180"/>

# Tablero Comercial · Berrix

**Analítica de ventas B2B para el sector agroindustrial de berries**

Un caso real de análisis comercial, anonimizado y reproducible.

[![Python](https://img.shields.io/badge/Python-3.13-1B4332?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.61-1B4332?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) [![Polars](https://img.shields.io/badge/Polars-1.43-2C5F7C?style=flat-square)](https://pola.rs/) [![DuckDB](https://img.shields.io/badge/DuckDB-SQL-2C5F7C?style=flat-square&logo=duckdb&logoColor=white)](https://duckdb.org/) [![Plotly](https://img.shields.io/badge/Plotly-6.9-BC6C25?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)

---

## Resumen en 2 minutos

Un tablero que convierte transacciones de venta B2B en cuatro preguntas de decisión para un comité comercial agroindustrial: cómo van las ventas por canal, de dónde viene la venta por región, qué clientes están reduciendo compra de forma sostenida y qué cuentas compran una sola especie. Construido sobre datos reales anonimizados (33 clientes B2B, k ≥ 5), con demo pública y metodología de anonimización documentada.

## El problema

Los equipos comerciales de las empresas agroindustriales suelen navegar entre hojas de cálculo desconectadas, análisis manuales y decisiones basadas en promedios que esconden la realidad. Cuando la información está fragmentada, el comité comercial no ve tendencias, no detecta riesgos a tiempo y no prioriza acciones con datos.

La pregunta que este proyecto responde: **¿cómo transformar datos transaccionales de ventas B2B en un instrumento de decisión diario para un equipo comercial?**

## Las cuatro fases del proyecto

Este proyecto no nació como un dashboard público. Nació como un encargo real dentro de una empresa agroindustrial y pasó por cuatro fases antes de convertirse en el caso reproducible que estás leyendo.

| Fase | Qué ocurrió | Entregable |
|---|---|---|
| **1 · Trabajo con la empresa** | Revisión de las hojas de cálculo de pedidos, despachos, informe de ventas y facturación. Entendimiento del flujo comercial real y de las preguntas que el comité necesitaba responder. | Modelo de datos y preguntas de decisión |
| **2 · Entrega corporativa** | El framework corporativo de la empresa era **Excel + Tableau**. La entrega original se hizo en ese stack. La empresa está migrando a **SAP**; se proyecta una migración de Excel a SAP para garantizar la continuidad del proyecto, pero **no se contempló en esta fase**. | Dashboard en Tableau |
| **3 · Replicación en Streamlit** | Del proyecto en Tableau se hizo una réplica funcional en **Streamlit** (Python, Polars, DuckDB, Plotly), con el mismo modelo de datos y las mismas preguntas de decisión. | App Streamlit interna |
| **4 · Anonimización y publicación** | Del proyecto replicado se derivó una versión **k-anónima** (k ≥ 5, supresión de celdas < 10, generalización, redondeo y perturbación) para poder publicarla sin exponer información confidencial. | Este repositorio público |

**Por qué importa esta historia:** muestra que el proyecto no es un ejercicio académico. Nació de un problema real, se entregó en el stack que la empresa ya usaba, se replicó en un stack reproducible y se anonimizó con estándares verificables. Esa cadena —empresa → Tableau → Streamlit → público— es parte del valor del caso.

## Qué hace este tablero

El tablero estructura la información comercial en cuatro vistas interconectadas, más una pestaña de gobernanza que documenta el proceso de anonimización:

| Pestaña | Pregunta que responde |
|---|---|
| 📊 **01 · Ventas por canal** | ¿Cómo van las ventas y qué canal impulsa el crecimiento? |
| 🗺️ **02 · Dinámica regional** | ¿De dónde viene la venta y cómo se distribuye geográficamente? |
| 🚨 **03 · Alertas y riesgos** | ¿Qué clientes están reduciendo su compra de forma sostenida? |
| 📦 **04 · Portafolio** | ¿Qué clientes solo compran una especie y cuáles son las cuentas estratégicas? |
| 🛡️ **00 · Gobernanza** | ¿Cómo se anonimizaron los datos y qué técnicas se aplicaron? |

## Qué demuestra este proyecto

- **Recorrer el ciclo completo de un proyecto de datos:** desde el trabajo con la empresa y la revisión de sus hojas de cálculo, hasta la entrega en el stack corporativo (Excel + Tableau), la replicación en un stack reproducible (Streamlit) y la anonimización para publicación.
- **Traducir un problema comercial difuso en preguntas de decisión medibles:** cada vista del tablero responde una pregunta concreta del comité.
- **Elegir métricas que evitan sesgos:** kilogramos en lugar de pesos para que un cambio de precio no parezca una caída de compra.
- **Diseñar reglas que reducen falsos positivos:** semáforo de retención con dos meses consecutivos, no uno.
- **Definir un universo analítico defendible:** regla de oro del B2B, exclusión de transacciones sin match con la tabla de clientes objetivo.
- **Anonimizar sin destruir señal:** k-anonimato, supresión, generalización, redondeo y perturbación.
- **Construir para una reunión, no para un reporte:** cuatro vistas más gobernanza, demo en vivo.

## Decisiones de diseño

### 1 · Métricas precio-neutrales en kilogramos para las alertas (D03)

Un cambio de precio nunca debe hacer parecer que un cliente compra menos cuando compra lo mismo. Por eso las alertas de retención se calculan en kilogramos, no en pesos. Si se usara valor monetario, una caída de precio podría activar una falsa alerta de fuga.

### 2 · Semáforo de retención con condición de sostenibilidad

Una caída de un solo mes no activa alerta: se requieren **dos meses consecutivos** para confirmar tendencia. Dos meses es el mínimo que elimina la mayoría de falsos positivos por estacionalidad mensual sin retrasar la alerta más de una semana de planificación comercial. Se probaron ventanas de uno y tres meses: una disparaba ruido, tres llegaba tarde al comité.

### 3 · Regla de oro del universo B2B

Toda transacción que no hace match con la tabla de clientes objetivo queda fuera del análisis. No se imputa ni se aproxima: se excluye. Esto mantiene el universo limpio y evita que el análisis se contamine con transacciones no atribuibles.

## Recomendaciones e impacto

> **Nota de transparencia:** las cifras de esta sección son estimaciones bajo NDA. Las cifras exactas están bajo confidencialidad; los rangos se presentan para dar escala al caso y deben validarse antes de usarse en una presentación.

### 1 · Activar un plan de retención para cuentas en riesgo

El semáforo de retención identifica clientes con caída sostenida de compra durante dos meses consecutivos. La recomendación operativa es que el comité comercial revise esas cuentas en la misma sesión y asigne un responsable de contacto antes de que la caída se consolide en el trimestre. El impacto estimado depende del valor de la cuenta retenida: una cuenta con contrato anual en el rango [X–Y] representa venta preservada si se actúa a tiempo.

### 2 · Priorizar venta cruzada en clientes mono-especie

La vista de portafolio identifica clientes que compran una sola especie. La recomendación es priorizar una oferta de segunda especie a las cuentas con mayor volumen y menor diversificación, con un objetivo de [X]% de penetración en [Y] meses.

### 3 · Revisar la cobertura comercial por región

La vista de dinámica regional muestra concentración de venta. La recomendación es revisar si el esfuerzo comercial está alineado con la distribución de ingresos y ajustar la cobertura en las regiones con mayor potencial no capturado.

## Gobernanza de datos

Este proyecto trabaja con **datos derivados k-anónimos**, generados a partir de un caso real de **33 clientes B2B** bajo un acuerdo de confidencialidad. La información original nunca se publica.

Técnicas de anonimización aplicadas (conforme al certificado de métodos):

- Agregación / totalización
- k-anonimato (k ≥ 5)
- Supresión de celdas con < 10 contribuyentes
- Generalización de categorías
- Redondeo y perturbación aleatoria

La metodología completa está documentada en [`build_public.py`](src/berrix/build_public.py).

> ⚠️ **Nota de transparencia:** debido al tamaño de la base B2B (33 clientes), algunas categorías con pocos contribuyentes se generalizan o suprimen para garantizar k ≥ 5 y celdas ≥ 10. El análisis detallado por cliente individual existe únicamente en el nivel local pseudonimizado, conforme al acuerdo de confidencialidad.

## Companion project

Este caso se complementa con [cosecha-public](https://github.com/ag-agrodata/cosecha-public), un planificador operativo de cosecha de arándanos: el otro extremo de la cadena de valor agroindustrial. Mientras este tablero mira hacia el comité comercial, `cosecha-public` mira hacia la operación de cosecha, la dotación y el costo.

## Stack tecnológico

| Herramienta | Rol |
|---|---|
| **Python 3.13** | Lenguaje base |
| **DuckDB** | Motor SQL para transformaciones |
| **Polars** | Manipulación de DataFrames |
| **Streamlit** | Framework del dashboard |
| **Plotly** | Visualizaciones interactivas |
| **uv** | Gestor de dependencias |

## Estructura del proyecto

```text
berries-dashboard/
├── src/
│   └── berrix/
│       ├── app_public.py       # Public Streamlit dashboard
│       ├── build_public.py     # Anonymization methodology
│       ├── i18n.py             # ES/EN copy and display maps
│       └── assets/
│           └── ag6.svg         # AG v6 logo
├── data/
│   └── public/                 # k-anonymous data only (8 parquet tables)
│       ├── d01_canal_publico.parquet
│       ├── d01_temporada_publico.parquet
│       ├── d02_concentracion_publico.parquet
│       ├── d02_macro_region_publico.parquet
│       ├── d03_alertas_publico.parquet
│       ├── d03_alertas_total_publico.parquet
│       ├── d04_portafolio_publico.parquet
│       └── d04_portafolio_global_publico.parquet
├── docs/
│   └── public/
│       ├── cerebro-berries-public.md
│       ├── guia-tablero-public.html
│       └── en/
│           ├── cerebro-berries-public.md
│           └── guia-tablero-public.html
├── .streamlit/
│   └── config.toml             # AG brand identity
├── pyproject.toml
├── requirements.txt
├── LICENSE
├── LICENSE-DATA
└── README.md
```

## Ejecución local

```
# Clonar el repo
git clone https://github.com/ag-agrodata/berries-dashboard.git
cd berries-dashboard

# Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ejecutar el dashboard
streamlit run src/berrix/app_public.py
```

## Ver la App

[🌐 Streamlit Cloud](https://berries-dashboard-ztwjxjslwpatnh5kvgn9wd.streamlit.app/)

## Licencia

Este proyecto usa una **licencia por capas**:

- **Código** (`src/`, `.streamlit/`, `requirements.txt`): [MIT](LICENSE).
- **Datos** (`data/public/`): [Acuerdo de Uso de Datos](LICENSE-DATA) — no comercial, sin reidentificación, sin inferencia de precios, atribución requerida.
- **Documentación** (`docs/`, READMEs): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

> ⚠️ Los datasets k-anonimizados se publican con fines demostrativos, conforme al acuerdo de confidencialidad con el cliente. Cualquier intento de reidentificar clientes, personas o transacciones, o de inferir precios, márgenes o términos contractuales, está expresamente prohibido. Consulta [LICENSE-DATA](LICENSE-DATA) para los términos completos.

---

**Andrés Gómez**
Analista de Datos Agroindustriales
"Transformo la complejidad del campo en decisiones basadas en datos."
afgomez.agroindustrial@gmail.com
