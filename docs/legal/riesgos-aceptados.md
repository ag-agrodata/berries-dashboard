# Riesgos Aceptados · Gobernanza de Datos Derivados

**Proyecto:** Berries Dashboard · Caso de portafolio técnico  
**Autor:** Andrés Gómez · Analista de Datos Agroindustriales  
**Fecha de emisión:** Octubre 2026  
**Versión:** 1.0  
**Alcance:** Este documento registra los hallazgos residuales de la auditoría de anonimización que, tras evaluación técnica y legal, fueron aceptados como riesgos controlados dentro del marco del Acuerdo de Confidencialidad y Colaboración suscrito con el cliente original del caso.

---

## 1. Propósito

Documentar de forma transparente los hallazgos de severidad baja o media identificados durante el proceso de anonimización y publicación del caso, junto con la justificación de gobernanza que sustenta su aceptación como riesgos controlados. Este registro no sustituye las pruebas técnicas de k-anonimato (ver `data/public/validacion.txt`), sino que las complementa desde una perspectiva de análisis cualitativo de identificadores residuales.

## 2. Marco de referencia

- **Parámetros de anonimización:** k ≥ 5 contribuyentes únicos, celdas ≥ 10 registros.
- **Técnicas aplicadas:** agregación, k-anonimato, supresión de celdas, generalización de categorías, redondeo y perturbación aleatoria.
- **Licencia de datos:** Data Use Agreement (DUA) — ver `LICENSE-DATA`.
- **Restricción fundamental:** ninguna publicación permite individualizar clientes, personas o transacciones, ni inferir precios, márgenes o términos comerciales.

## 3. Registro de riesgos aceptados

| ID | Hallazgo | Severidad | Justificación de gobernanza | Mitigación existente |
|---|---|---|---|---|
| **F02** | Presencia de categorías con conteos pequeños (8, 7, 3 contribuyentes) en agregaciones temporales. | Baja | Los conteos revelan topología del dataset, no identidad de clientes ni del titular de los datos. El k-anonimato (k ≥ 5) ya protege las celdas publicadas; este hallazgo se refiere a la estructura interna del dato antes de la agregación final. | Validación técnica PASS en `data/public/validacion.txt` (test 1: singularización, test 2: membresía). |
| **F03** | Uso de la clasificación geográfica "Centro - Bogotá" y "Centro - Sabana" como macro-regiones. | Baja | Es una clasificación geográfica comercial estándar en Colombia, no un dato propietario ni secreto que delimite exclusivamente a una empresa. | Generalización a dos macro-regiones ("Centro" vs "Resto de regiones") en el dataset público (`d02_macro_region_publico.parquet`). |
| **F05 / F07** | Convenciones de naming heredadas del modelo original (prefijos de campos, estructura de carpetas). | Baja | Los nombres de campos y carpetas publicados son genéricos (`D01_K001`, `d01_canal_publico.parquet`) y no contienen identificadores directos del cliente, marcas o personas. | Revisión exhaustiva de identificadores residuales; eliminación de nombres de archivos fuente originales. |
| **D-44** | Mención de "Tableau" en la narrativa de las cuatro fases del proyecto. | Baja | Tableau es una herramienta de BI estándar utilizada por miles de empresas a nivel global. Su mención describe el stack tecnológico original del caso, no identifica al cliente. | La narrativa se enfoca en el ciclo de vida del proyecto (Excel + BI corporativo → Streamlit → público), no en el cliente específico. |

## 4. Análisis de efecto mosaico

La combinación de elementos publicados — sector agroindustrial, berries, 33 clientes B2B, migración de stack tecnológico, regiones colombianas — podría permitir que un experto del sector deduzca la identidad del cliente original. Sin embargo:

1. **El NDA protege la individualización de clientes, personas y transacciones**, no la deducción del nombre de la empresa matriz a partir de datos agregados y seguros.
2. **Los Datos Derivados cumplen la Cláusula 5 del NDA**: no permiten individualización ni perfilamiento de clientes, proveedores, colaboradores o terceros.
3. **La publicación fue autorizada bajo la condición de no identificabilidad y no inferencia de precios**, condiciones que se verifican técnicamente en `data/public/validacion.txt`.

## 5. Declaración de cumplimiento

Este documento certifica que:

- No se publican datos identificantes del cliente original.
- No se publican nombres de archivos fuente, marcas o personas.
- Todos los datos publicados han sido sometidos a pruebas de k-anonimato con resultado PASS.
- Los riesgos aceptados son de severidad baja o media y no comprometen la condición fundamental de no identificabilidad.
- El Acuerdo de Confidencialidad y Colaboración se mantiene vigente en su archivo privado, junto con la Constancia de Destrucción (Anexo B) de las bases originales.

## 6. Vigencia y actualización

Este registro es válido mientras no se modifiquen los parámetros de anonimización ni se publiquen nuevos derivados. Cualquier cambio en el dataset público requerirá una nueva ejecución de `tools/validacion_anonimizacion.py` y, si aplica, una actualización de este documento.

---

**Andrés Gómez**  
Analista de Datos Agroindustriales  
Octubre 2026
