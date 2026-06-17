# Copa Libertadores 1996–2024
### Dataset reproducible de partidos con QA, normalización y EDA

## Descripción general

Este proyecto construye un **dataset reproducible y auditable de partidos de Copa Libertadores entre 1996 y 2024**, a partir de fuentes textuales (RSSSF), aplicando parsing robusto, control de calidad (QA), normalización de entidades, enriquecimiento con metadatos y análisis exploratorio de datos (EDA).

El resultado es un **dataset listo para análisis**, documentado, versionado y extensible, siguiendo buenas prácticas de ingeniería de datos y pensado como pieza publicable de un portfolio profesional.

---

## Objetivos del proyecto

- Construir un dataset histórico consistente de partidos de Copa Libertadores (1996–2024).
- Garantizar reproducibilidad total desde datos crudos.
- Aplicar reglas de QA explícitas y documentadas.
- Resolver problemas reales de datos históricos (formatos inconsistentes, nombres variables, información incompleta).
- Dejar una base sólida para análisis, dashboards y modelos posteriores.

---

## Estructura del repositorio

```
Libertadores-1996-2024/
│
├── datos/
│   ├── rsssf/          # Archivos .txt RSSSF por temporada (1996–2024)
│   ├── crudos/         # CSV generado por el parser (partidos_rsssf_raw.csv)
│   ├── intermedios/    # CSV post-transformación, pre-QA
│   ├── procesados/     # CSV validados y normalizados (dataset final)
│   └── referencias/    # Tablas maestras (equipos_referencia.csv, equipos_alias.csv)
│
├── src/
│   ├── rsssf/          # Parser RSSSF y transformación a esquema v1
│   ├── qa/             # Chequeos de calidad automáticos
│   └── referencia/     # Normalización de alias y enriquecimiento
│
├── notebooks/
│   └── 01_eda_mock.ipynb   # EDA exploratorio sobre el dataset procesado
│
├── reportes/
│   ├── qa/             # Reportes de registros inválidos por tipo de error
│   └── referencias/    # Reporte de equipos sin match en tabla de referencia
│
├── docs/
│   ├── alcance_dataset_v1.md
│   ├── reglas_qa.md
│   ├── diccionario_datos.md
│   └── decisiones.md
│
└── README.md
```

---

## Fuente de datos

- **RSSSF (Rec.Sport.Soccer Statistics Foundation)**
  Fuente histórica ampliamente utilizada para estadísticas de fútbol.

Características:
- Texto plano (`.txt`), un archivo por temporada
- Formato no estructurado con convenciones distintas entre fases (grupos vs. eliminatorias)
- Nombres de equipos variables a lo largo del tiempo

Esto motiva la construcción de un parser propio en lugar de scraping estructurado.

Los 29 archivos `.txt` (1996–2024) están commiteados en `datos/rsssf/`, lo que garantiza reproducibilidad sin acceso a internet.

---

## Pipeline de datos

El proceso se divide en cinco etapas secuenciales, cada una con entrada y salida explícitas:

### 1. Parsing RSSSF
```bash
python src/rsssf/parser_rsssf.py
```
- Entrada: `datos/rsssf/*.txt`
- Salida: `datos/crudos/partidos_rsssf_raw.csv`

Parsea dos formatos: partidos de grupos (`Mar 13: Equipo A - Equipo B 3-2`) y series eliminatorias (`Equipo A Arg Equipo B Bra 1-0 1-2 2-2`).

### 2. Transformación a esquema v1
```bash
python src/rsssf/transformar_rsssf_a_v1.py
```
- Entrada: `datos/crudos/partidos_rsssf_raw.csv`
- Salida: `datos/intermedios/partidos_rsssf.csv`

Estandariza columnas, tipos y convenciones al esquema v1 (ver `docs/diccionario_datos.md`).

### 3. QA automático
```bash
python src/qa/chequeos_qa.py
```
- Entrada: `datos/intermedios/partidos_rsssf.csv`
- Salida: `datos/procesados/partidos_rsssf1_validos.csv` + `partidos_rsssf1_invalidos.csv`
- Reportes: `reportes/qa/`

Aplica las reglas documentadas en `docs/reglas_qa.md`.

### 4. Normalización de equipos (alias)
```bash
python src/referencia/alias_robusto.py
```
- Entrada: `datos/procesados/partidos_rsssf1_validos.csv` + `datos/referencias/equipos_alias.csv`
- Salida: `datos/procesados/partidos_rsssf1_validos_normalizado.csv`

### 5. Enriquecimiento con metadatos
```bash
python src/referencia/enriquecer_partidos_con_referencia.py
```
- Entrada: `datos/procesados/partidos_rsssf1_validos_normalizado.csv` + `datos/referencias/equipos_referencia.csv`
- Salida: `datos/procesados/partidos_rsssf1_enriquecido.csv`

Incorpora país, ciudad y estadio de cada equipo desde la tabla maestra.

---

## Control de Calidad (QA)

Las reglas están documentadas en `docs/reglas_qa.md`. Resumen:

| Tipo | Regla |
|------|-------|
| Estructural | Sin duplicados por (temporada, fecha, local, visitante) |
| Estructural | Goles ≥ 0, temporada entre 1996 y 2024 |
| Lógica | `resultado` consistente con goles (L/V/E) |
| Cobertura | Todas las temporadas presentes con al menos un partido |

Los registros inválidos se excluyen del dataset final y se guardan en `reportes/qa/` para revisión manual.

---

## Normalización de equipos

RSSSF presenta múltiples variantes para un mismo club. La normalización se hace con una tabla explícita de alias (`datos/referencias/equipos_alias.csv`) en lugar de fuzzy matching, para garantizar reproducibilidad y trazabilidad. Ver `docs/decisiones.md` para el razonamiento completo.

---

## Enriquecimiento con metadatos

La tabla maestra `datos/referencias/equipos_referencia.csv` contiene país, ciudad y estadio de cada club. Se une al dataset normalizado para completar los campos de sede.

---

## Diccionario de datos

El esquema completo (21 columnas) está documentado en `docs/diccionario_datos.md`.

---

## Reproducibilidad

### Requisitos
- Python 3.10+
- pandas, matplotlib, requests, lxml

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### Ejecución completa
```bash
python src/rsssf/parser_rsssf.py
python src/rsssf/transformar_rsssf_a_v1.py
python src/qa/chequeos_qa.py
python src/referencia/alias_robusto.py
python src/referencia/enriquecer_partidos_con_referencia.py
```

---

## Estado del Proyecto

- **Versión**: v1
- **Estado**: Terminado y publicable.
- **Cobertura**: 29 temporadas (1996–2024), dataset con QA aplicado y normalización completa.

## Próximos pasos (v2)

- Parsing de penales y estructura de llaves (ida/vuelta separadas)
- Dashboard interactivo con Streamlit
- Métricas avanzadas (xG, ELO por club)