# Decisiones de diseño — Dataset Libertadores v1

Este documento registra las decisiones técnicas no obvias tomadas durante el desarrollo del dataset, con su razonamiento. El objetivo es que el proyecto sea auditable y extensible.

---

## 1. Fuente de datos: RSSSF en lugar de scraping dinámico

**Decisión**: usar los archivos `.txt` de RSSSF como fuente primaria en lugar de scrapers sobre sitios como BDFutbol, Soccerway o el sitio oficial de la CONMEBOL.

**Razonamiento**: los sitios dinámicos cambian estructura con frecuencia y requieren mantenimiento continuo del scraper. RSSSF publica texto plano estático disponible desde los años 90, con cobertura histórica completa desde 1996. Los archivos `.txt` se committean en el repositorio, lo que convierte la descarga en un paso opcional y garantiza que el pipeline pueda reproducirse sin acceso a internet.

**Trade-off**: RSSSF no incluye datos de sede, ciudad ni estadio en forma consistente. Esos campos se dejan vacíos y se completan en el paso de enriquecimiento con la tabla de referencia de clubes.

---

## 2. Sin fuzzy matching para normalización de equipos

**Decisión**: la normalización de nombres de clubes se hace con una tabla explícita de alias (`equipos_alias.csv`), no con algoritmos de similitud (Levenshtein, RapidFuzz, etc.).

**Razonamiento**: el fuzzy matching es no determinista — distintos umbrales o versiones de la librería pueden producir resultados distintos entre ejecuciones, rompiendo la reproducibilidad. Con una tabla explícita, cada decisión de normalización es visible, revisable y versionada en git. Para datos históricos donde los nombres cambian por fusiones de clubes o cambios de nombre formales, la decisión de equiparar dos nombres siempre requiere juicio humano de todas formas.

**Trade-off**: la tabla requiere curaduría manual. Los equipos que no tienen alias definido permanecen con su nombre RSSSF original, lo cual es correcto: mejor nombre exacto de la fuente que una normalización automática incorrecta.

---

## 3. Separación en capas: rsssf / intermedios / procesados / referencias

**Decisión**: los datos fluyen en cuatro capas con contratos claros, en lugar de transformar todo en un único script.

**Razonamiento**:
- `rsssf/`: fuente sin modificar. Si RSSSF cambia o desaparece, el pipeline puede seguir corriendo desde estos archivos.
- `intermedios/`: output del parser, previo a QA. Permite depurar el parser sin re-ejecutar los pasos de validación.
- `procesados/`: datos validados y normalizados. Es el único artefacto que consume el EDA.
- `referencias/`: tablas maestras independientes del pipeline principal. Pueden actualizarse sin re-ejecutar el parser.

Esta separación permite identificar exactamente en qué paso se introduce un problema de calidad.

---

## 4. Strings vacíos (`""`) en lugar de `NaN` para campos sin datos de sede

**Decisión**: cuando RSSSF no provee datos de ciudad, estadio o país sede, se escribe `""` en lugar de `NaN`.

**Razonamiento**: el paso de enriquecimiento posterior hace un join por nombre de equipo y rellena esos campos desde `equipos_referencia.csv`. La función `_rellenar_si_vacio` interpreta tanto `NaN` como `""` como "sin dato", pero usar `""` hace el contrato explícito en el CSV y evita ambigüedades de dtype cuando pandas infiere columnas como `object` vs `float64` por la presencia de `NaN`.

**Trade-off**: el código downstream tiene que checar `== ""` además de `pd.isna()`. Está documentado en el diccionario de datos.

---

## 5. Archivos `.txt` RSSSF commiteados en el repositorio

**Decisión**: los 29 archivos `.txt` (uno por temporada 1996–2024) se incluyen en el repositorio en lugar de descargarse en tiempo de ejecución.

**Razonamiento**: los archivos de RSSSF pueden cambiar o desaparecer. El script de descarga (`descargar_libertadores_rsssf.py`) ya cumplió su función. Tener los `.txt` en git convierte el repositorio en su propio ancla de datos: quien clone puede reproducir el pipeline completo sin acceso a la red. El tamaño total es de ~450 KB, insignificante para un repositorio de datos.

**Trade-off**: los datos quedan "congelados" en la versión descargada. Si RSSSF corrige un error histórico, hay que re-descargar manualmente y re-ejecutar el pipeline desde el inicio.