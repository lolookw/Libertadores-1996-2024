# CLAUDE.md — Copa Libertadores 1996–2024

Contexto del proyecto para Claude Code y Claude en general.

## Qué es este proyecto

Dataset reproducible de partidos de Copa Libertadores 1996–2024, construido desde fuentes RSSSF (texto plano). Pipeline de 5 etapas: parse → transform → QA → alias → enriquecimiento → enhanced.

El dataset alimenta `Modelo-Libertadores` (en `/home/lolo/Desktop/coding/Modelo-Libertadores`), un modelo predictivo 1X2 de resultados de Copa Libertadores.

## Estado actual del dataset

**Archivo principal para modelos**: `datos/procesados/partidos_rsssf1_enhanced.csv`

| Métrica | Valor |
|---------|-------|
| Total partidos | 2575 |
| Temporadas | 29/29 |
| Cobertura grupos | Alta (todas las temporadas presentes) |
| Cobertura eliminatorias | Baja — solo 1996–1999 |

### Gaps conocidos

| Año | Problema | Causa |
|-----|---------|-------|
| 1997 | Sin grupos (~60 filas) | Formato RSSSF sin espacios alrededor del guion |
| 1998 | Grupos parciales (~50 filas) | Mismo problema |
| 2012 | Grupos parciales (~105 filas) | Formato sin guion entre equipos |
| 2000–2024 | Sin eliminatorias (~400 filas) | Parser no maneja fechas cross-month en bloques multi-línea |

**Para completar estos datos**: ver `docs/prompt_completar_datos.md`.

## Esquema del CSV principal

```
temporada,competicion,fase,instancia,fecha,pais_sede,ciudad_sede,estadio,
equipo_local,equipo_visitante,pais_local,pais_visitante,
goles_local,goles_visitante,resultado,fuente,url_fuente,id_partido_fuente,
observaciones,resultado_norm,fecha_parseada
```

- `resultado`: `L` (local gana), `V` (visitante gana), `E` (empate)
- `fase`: `Grupos`, `Octavos`, `Cuartos`, `Semifinal`, `Final`
- `instancia`: para grupos = `Group A`…`Group H`; para series = `Ida` o `Vuelta`
- Strings vacíos `""` representan "sin dato" (no NaN), salvo los campos numéricos

## Pipeline de ejecución

```bash
python src/rsssf/parser_rsssf.py                    # 1. Parse RSSSF txt
python src/rsssf/transformar_rsssf_a_v1.py          # 2. Schema v1
python src/qa/chequeos_qa.py                        # 3. QA
python src/referencia/alias_robusto.py              # 4. Alias
python src/referencia/enriquecer_partidos_con_referencia.py  # 5. Enriquecimiento
python src/pipeline/generar_enhanced.py             # 6. Enhanced (fixes + audit)
```

## Para completar datos con IA

```bash
# 1. Ir a claude.ai, abrir el prompt en docs/prompt_completar_datos.md
# 2. Copiar el prompt + especificar el año/fase a completar
# 3. Guardar el CSV devuelto en datos/externos/
# 4. Fusionar:
python src/pipeline/fusionar_datos_ia.py datos/externos/nombre.csv
```

## Convenciones clave

- Los archivos RSSSF de origen están en `datos/rsssf/*.txt` (29 archivos, uno por año)
- `datos/crudos/`, `datos/intermedios/`, `datos/procesados/` están en .gitignore (se generan)
- `datos/referencias/` y `datos/rsssf/` están versionados en git
- Tabla de alias: `datos/referencias/equipos_alias.csv` (66 registros)
- Tabla de referencia: `datos/referencias/equipos_referencia.csv` (222 equipos)
- Nombre canónico de equipos: usar el valor de `equipo` en `equipos_referencia.csv`

## Conexión con Modelo-Libertadores

El proyecto `Modelo-Libertadores` lee:
```python
df = pd.read_csv("../Libertadores-1996-2024/datos/procesados/partidos_rsssf1_enhanced.csv")
```
(o el path equivalente configurado en su `configuracion.py`).

Las columnas más críticas para el modelo son:
`temporada`, `fecha`, `fase`, `equipo_local`, `equipo_visitante`,
`goles_local`, `goles_visitante`, `resultado`, `pais_local`, `pais_visitante`

## Decisiones de diseño

Ver `docs/decisiones.md` para el razonamiento completo detrás de cada elección.
Las principales:
1. RSSSF como fuente (estabilidad histórica vs. scrapers dinámicos)
2. Alias explícitos, sin fuzzy matching (reproducibilidad)
3. Separación en capas de datos (debug granular por etapa)
4. Strings vacíos en lugar de NaN para campos sin dato de sede