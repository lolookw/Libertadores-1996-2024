# Alcance del dataset v1 – Copa Libertadores 1996–2024

## Objetivo
Construir un dataset reproducible de partidos de Copa Libertadores entre 1996 y 2024, orientado a análisis histórico, econométrico y de rendimiento deportivo.

## Unidad de observación
Cada fila del dataset representa un partido oficial de Copa Libertadores.

## Cobertura temporal
- Desde: 1996
- Hasta: 2024

## Competencias incluidas
- Copa Libertadores
  - Fase de grupos
  - Fases eliminatorias (octavos, cuartos, semifinales)
  - Final (partido único o ida/vuelta según temporada)

## Competencias excluidas
- Fases preliminares / clasificatorios
- Copa Sudamericana
- Amistosos

## Nivel de detalle
El dataset v1 incluye únicamente información básica del partido:
- Equipos
- Resultado
- Fecha y sede
- Fase del torneo

No se incluyen métricas avanzadas (xG, árbitros, asistencia, penales).

## Fuentes de datos
- Plan A: sitios web estructurados
- Plan B: archivos de texto tipo RSSSF

La fuente exacta de cada partido se indica en las columnas `fuente` y `url_fuente`.

## Limitaciones conocidas

- **Temporada 2011 no incluida**: el archivo RSSSF de 2011 utiliza un formato alternativo (sin guion como separador entre equipos en grupos, rangos de fechas en múltiples líneas, sufijos `x` para extra time). El parser v1 no cubre este formato. El dataset cubre 28 de las 29 temporadas del rango.

## Versionado
Este documento describe el alcance del dataset versión v1.  
Cambios futuros deberán documentarse en versiones posteriores.
