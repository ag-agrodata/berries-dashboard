<div align="center">
  <img src="src/berrix/assets/ag6.svg" alt="AG · Andrés Gómez" width="140">

  # Tablero Comercial · Berrix

  **Analítica de ventas B2B para el sector agroindustrial de berries**

  Un caso real de análisis comercial, anonimizado y reproducible.

  [![Python](https://img.shields.io/badge/Python-3.13-1B4332?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.61-1B4332?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
  [![Polars](https://img.shields.io/badge/Polars-1.43-2C5F7C?style=flat-square)](https://pola.rs/)
  [![DuckDB](https://img.shields.io/badge/DuckDB-SQL-2C5F7C?style=flat-square&logo=duckdb&logoColor=white)](https://duckdb.org/)
  [![Plotly](https://img.shields.io/badge/Plotly-6.9-BC6C25?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)
</div>

---

## El problema

Los equipos comerciales de las empresas agroindustriales suelen navegar entre hojas de cálculo desconectadas, análisis manuales y decisiones basadas en promedios que esconden la realidad. Cuando la información está fragmentada, el comité comercial no ve tendencias, no detecta riesgos a tiempo y no prioriza acciones con datos.

La pregunta que este proyecto responde: **¿cómo transformar datos transaccionales de ventas B2B en un instrumento de decisión diario para un equipo comercial?**

## Qué hace este tablero

El tablero estructura la información comercial en cuatro vistas interconectadas, más una pestaña de gobernanza que documenta el proceso de anonimización:

| Pestaña | Pregunta que responde |
|---|---|
| 📊 **01 · Ventas por canal** | ¿Cómo van las ventas y qué canal impulsa el crecimiento? |
| 🗺️ **02 · Dinámica regional** | ¿De dónde viene la venta y cómo se distribuye geográficamente? |
| 🚨 **03 · Alertas y riesgos** | ¿Qué clientes están reduciendo su compra de forma sostenida? |
| 📦 **04 · Portafolio** | ¿Qué clientes solo compran una especie y cuáles son las cuentas estratégicas? |
| 🛡️ **00 · Gobernanza** | ¿Cómo se anonimizaron los datos y qué técnicas se aplicaron? |

### Decisiones de diseño

- **Métricas precio-neutrales en kilogramos** para las alertas (D03): un cambio de precio nunca hace parecer que un cliente compra menos cuando compra lo mismo.
- **Semáforo de retención con condición de sostenibilidad**: una caída de un solo mes no activa alerta; se requieren 2 meses consecutivos para confirmar tendencia.
- **Regla de oro del universo B2B**: toda transacción que no hace match con la tabla de clientes objetivo queda fuera del análisis.

## Gobernanza de datos

Este proyecto trabaja con **datos derivados k-anónimos**, generados a partir de un caso real bajo un acuerdo de confidencialidad. La información original nunca se publica.

Técnicas de anonimización aplicadas (conforme al certificado de métodos):

- Agregación / totalización
- k-anonimato (k ≥ 5)
- Supresión de celdas con < 10 contribuyentes
- Generalización de categorías
- Redondeo y perturbación aleatoria

La metodología completa está documentada en [`build_public.py`](src/berrix/build_public.py).

> ⚠️ **Nota de transparencia:** debido al tamaño de la base B2B, algunas categorías con pocos contribuyentes se generalizan o suprimen para garantizar k ≥ 5 y celdas ≥ 10. El análisis detallado por cliente individual existe únicamente en el nivel local pseudonimizado, conforme al acuerdo de confidencialidad.

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
│       ├── app_public.py       # Dashboard Streamlit público
│       ├── build_public.py     # Metodología de anonimización
│       └── assets/
│           └── ag6.svg         # Logo AG v6
├── data/
│   └── public/                 # Solo datos k-anónimos
│       ├── d01_*.parquet
│       ├── d02_*.parquet
│       ├── d03_*.parquet
│       └── d04_*.parquet
├── .streamlit/
│   └── config.toml             # Identidad de marca AG
├── requirements.txt
└── README.md
```

## Ejecución local

```text
# Clonar el repo
git clone https://github.com/ag-agrodata/berries-dashboard.git
cd berries-dashboard

# Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ejecutar el dashboard
streamlit run src/berrix/app_public.py`
```

## Ver la App

[🌐 Streamlit Cloud](https://berries-dashboard-ztwjxjslwpatnh5kvgn9wd.streamlit.app/)

## Licencia

Este proyecto está bajo la licencia MIT. Los datos incluidos son derivados k-anónimos y no contienen información identificable de terceros.

<div align="center">
Elaborado por Andrés Gómez · Analista de Datos Agroindustriales · 
"Transformo la complejidad del campo en decisiones basadas en datos."
afgomez.agroindustrial@gmail.com
</div>