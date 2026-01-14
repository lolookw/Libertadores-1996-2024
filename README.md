# Copa Libertadores 1996–2024  
### Dataset reproducible de partidos con QA, normalización y EDA

## 📌 Descripción general

Este proyecto construye un **dataset reproducible y auditable de partidos de Copa Libertadores entre 1996 y 2024**, a partir de fuentes textuales (RSSSF), aplicando parsing robusto, control de calidad (QA), normalización de entidades, enriquecimiento con metadatos y análisis exploratorio de datos (EDA).

El resultado es un **dataset listo para análisis**, documentado, versionado y extensible, siguiendo buenas prácticas de ingeniería de datos y pensado como pieza publicable de un portfolio profesional.

---

## 🎯 Objetivos del proyecto

- Construir un dataset histórico consistente de partidos de Copa Libertadores (1996–2024).
- Garantizar reproducibilidad total desde datos crudos.
- Aplicar reglas de QA explícitas y documentadas.
- Resolver problemas reales de datos históricos (formatos inconsistentes, nombres variables, información incompleta).
- Dejar una base sólida para análisis, dashboards y modelos posteriores.

---

## 🗂️ Estructura del repositorio

# Copa Libertadores 1996–2024  
### Dataset reproducible de partidos con QA, normalización y EDA

## 📌 Descripción general

Este proyecto construye un **dataset reproducible y auditable de partidos de Copa Libertadores entre 1996 y 2024**, a partir de fuentes textuales (RSSSF), aplicando parsing robusto, control de calidad (QA), normalización de entidades, enriquecimiento con metadatos y análisis exploratorio de datos (EDA).

El resultado es un **dataset listo para análisis**, documentado, versionado y extensible, siguiendo buenas prácticas de ingeniería de datos y pensado como pieza publicable de un portfolio profesional.

---

## 🎯 Objetivos del proyecto

- Construir un dataset histórico consistente de partidos de Copa Libertadores (1996–2024).
- Garantizar reproducibilidad total desde datos crudos.
- Aplicar reglas de QA explícitas y documentadas.
- Resolver problemas reales de datos históricos (formatos inconsistentes, nombres variables, información incompleta).
- Dejar una base sólida para análisis, dashboards y modelos posteriores.

---

## 🗂️ Estructura del repositorio

Libertadores-1996-2024/
│
├── datos/
│ ├── crudos/ # Archivos originales (.txt RSSSF)
│ ├── procesados/ # CSV intermedios y finales
│ └── referencias/ # Tablas maestras (equipos, alias)
│
├── src/
│ ├── parser/ # Parsing de texto RSSSF
│ └── referencias/ # Normalización y enriquecimiento
│
├── notebooks/
│ ├── 01_eda_inicial.ipynb
│ └── 02_eda_enriquecido.ipynb
│
├── reportes/
│ └── referencias/ # Reportes de QA y faltantes
│
├── docs/
│ ├── alcance_dataset.md
│ ├── reglas_qa.md
│ └── diccionario_datos.md
│
├── tests/ # Placeholder para tests futuros
├── app/ # Placeholder para dashboard (Streamlit)
└── README.md


---

## 📥 Fuente de datos

- **RSSSF (Rec.Sport.Soccer Statistics Foundation)**  
  Fuente histórica ampliamente utilizada para estadísticas de fútbol.

Características de la fuente:
- Texto plano (`.txt`)
- Formato no estructurado
- Convenciones distintas entre fases (grupos vs eliminatorias)
- Nombres de equipos variables a lo largo del tiempo

Esto motiva la construcción de un parser propio en lugar de scraping estructurado.

---

## 🔄 Pipeline de datos

### 1. Ingesta (datos crudos)
- Descarga manual de archivos `.txt` por temporada (1996–2024).
- Los archivos se almacenan **sin modificar** en `datos/crudos/`.

### 2. Parsing RSSSF
Se implementa un parser capaz de manejar dos grandes formatos:

#### Fase de grupos
Ejemplo:

Mar 13: Barcelona - Espoli 3-2

Se extraen:
- fecha
- equipo local
- equipo visitante
- goles

#### Eliminatorias (ida y vuelta)
Ejemplo:

San José Bol Barcelona Ecu 1-0 1-2 2-2 2-4p

Decisiones de diseño:
- Se guarda el **resultado agregado** como texto (`agregado_texto`)
- **No se parsean penales** en la versión v1
- Cada serie eliminatoria se representa como una única observación

Salida:

datos/crudos/partidos_rsssf_raw.csv

---

### 3. Transformación a esquema v1
Se estandarizan columnas, tipos y convenciones.

Columnas principales:
- `temporada`
- `competicion`
- `fase`
- `instancia`
- `fecha`
- `equipo_local`
- `equipo_visitante`
- `goles_local`
- `goles_visitante`
- `resultado`
- `fuente`
- `archivo_fuente`
- `linea_partido`

Salida:


datos/procesados/partidos_rsssf_v1.csv


---

## ✅ Control de Calidad (QA)

El QA se implementa como un paso formal y documentado.

### QA estructural
- No existen duplicados según:
  - temporada
  - fecha
  - equipo_local
  - equipo_visitante
- Tipos válidos:
  - goles ≥ 0
  - fechas válidas
  - temporadas entre 1996 y 2024

### QA lógica
- Consistencia entre goles y resultado:
  - goles_local > goles_visitante → "L"
  - goles_local < goles_visitante → "V"
  - goles_local = goles_visitante → "E"

### QA de cobertura
- Todas las temporadas entre 1996 y 2024 están presentes
- Cada temporada tiene al menos un partido

### Manejo de errores
- Registros inválidos se excluyen del dataset final
- Los errores se reportan para revisión manual

Salida:


datos/procesados/partidos_rsssf1_validos_normalizado.csv


## 🔤 Normalización de equipos

Problema:
- RSSSF presenta múltiples variantes para un mismo club (abreviaturas, paréntesis, ciudades, cambios históricos).

Solución:
- Se implementa una tabla explícita de alias:


datos/referencias/equipos_alias.csv


Formato:


equipo_alias → equipo_canonico


Ejemplo:


San Lorenzo → San Lorenzo de Almagro
Univ. de Chile → Universidad de Chile


La normalización se aplica **sin modificar los datos crudos**, garantizando trazabilidad.


## 🌍 Enriquecimiento con metadatos

Se construye una tabla maestra de clubes:


datos/referencias/equipos_referencia.csv


Campos:
- equipo (canónico)
- país
- ciudad
- estadio_principal
- fuente_referencia
- notas

El dataset de partidos se enriquece con:
- `pais_local`
- `pais_visitante`
- `ciudad_sede`
- `estadio` (aproximado: estadio del equipo local)

Salida final:


datos/procesados/partidos_rsssf1_enriquecido.csv


Se generan reportes automáticos de clubes sin match para asegurar cobertura completa.


## 📊 Análisis Exploratorio (EDA)

Los notebooks incluyen análisis como:
- Distribución de goles por partido
- Participaciones por país
- Partidos por estadio (aproximado)
- Evolución temporal de partidos

El EDA permite validar consistencia, detectar outliers y preparar visualizaciones posteriores.


## 📁 Diccionario de datos

El esquema completo del dataset se documenta en:


docs/diccionario_datos.md


Incluye:
- nombre de columna
- tipo
- descripción
- observaciones relevantes


## ⚙️ Reproducibilidad

### Requisitos
- Python 3.11+
- pandas
- matplotlib

### Setup
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

# Pipeline de Procesamiento: Copa Libertadores (RSSSF)

## ⚙️ Ejecución (Orden Lógico)

El proceso se divide en etapas secuenciales donde cada paso genera archivos versionados y auditables:

1. **Parsing RSSSF**: Extracción de datos desde las fuentes originales.
2. **Transformación a esquema v1**: Adaptación de los datos al modelo de datos inicial.
3. **QA (Quality Assurance)**: Validación de consistencia formal del pipeline.
4. **Normalización de equipos**: Aplicación de alias explícitos para estandarizar nombres.
5. **Enriquecimiento con referencias**: Incorporación de metadatos adicionales.
6. **EDA (Exploratory Data Analysis)**: Análisis exploratorio inicial.

## 📊 Análisis Exploratorio (EDA)

Los notebooks incluyen análisis como:
- **Distribución de goles por partido**: Histogramas de frecuencia de anotaciones.
- **Participaciones por país**: Rendimiento ofensivo y participaciones nacionales.
- **Partidos por estadio**: Visualización de sedes más frecuentes.
- **Evolución temporal**: Tendencias de partidos y goles por temporada.

El EDA permite validar consistencia, detectar outliers y preparar visualizaciones posteriores.

## 📁 Diccionario de datos

El esquema completo del dataset se documenta en:

`docs/diccionario_datos.md`

Incluye detalles de las 21 columnas procesadas:
- **Nombre de columna**: (ej. `temporada`, `resultado_norm`, `goles_local`).
- **Tipo**: (ej. `int64`, `object`, `float64`).
- **Descripción**: Definición funcional de cada campo.
- **Observaciones relevantes**: Notas sobre valores nulos o fuentes.

## 🧠 Decisiones de Diseño

- **Sin scraping dinámico**: Se optó por RSSSF debido a su estabilidad histórica frente a sitios dinámicos.
- **Sin fuzzy matching automático**: Se prioriza el control y la trazabilidad manual de nombres.
- **Alias explícitos**: El mapeo de equipos es transparente y revisable.
- **Separación de datos**: Distinción clara entre datos crudos, procesados y referencias.

## 🚀 Próximos Pasos (v2)

- **Parsing de penales**: Detalle de definiciones desde los doce pasos.
- **Estructura de llaves**: Separación de partidos de ida y vuelta.
- **Dashboard**: Integración con Streamlit para visualización interactiva.
- **Métricas avanzadas**: Implementación de modelos xG y ELO.

## ⚙️ Reproducibilidad

### Requisitos
- **Python 3.11+**
- **pandas**
- **matplotlib**

### Setup
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## 📌 Estado del Proyecto
- **Versión: v1**

- **Estado: Terminado y publicable.**

- **Calidad: QA OK, cobertura completa y dataset reproducible.**