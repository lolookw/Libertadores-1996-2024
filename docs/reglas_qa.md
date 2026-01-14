# Reglas de QA – Dataset Libertadores v1

## QA estructural

- No deben existir filas duplicadas según la clave:
  - temporada
  - fecha
  - equipo_local
  - equipo_visitante

- Los registros duplicados se consideran **inválidos** y se excluyen del dataset procesado.

- Tipos de datos:
  - temporada: entero entre 1996 y 2024
  - goles_local, goles_visitante: enteros mayores o iguales a 0

## QA lógica

- El campo `resultado` se normaliza antes de validarse:
  - "Local" → "L"
  - "Visitante" → "V"
  - "Empate" → "E"

- Valores fuera de este dominio se consideran inválidos.

- El campo `resultado` debe ser consistente:
  - goles_local > goles_visitante → "L"
  - goles_local < goles_visitante → "V"
  - goles_local = goles_visitante → "E"
  

## QA de consistencia

- Los nombres de equipos deben estar normalizados
- Los países deben escribirse en español (ej: Argentina, Brasil)

## QA de cobertura

- Todas las temporadas entre 1996 y 2024 deben estar presentes
- Cada temporada debe tener al menos un partido
- Se deben generar alertas si una temporada tiene una cantidad anormalmente baja de partidos

## Manejo de errores

- Las reglas de QA se aplican de forma automática sobre el dataset de entrada.

- Los registros que violen una o más reglas de QA se consideran **inválidos**:
  - No se incluyen en el dataset procesado final.
  - Se guardan en un archivo separado para revisión manual.

- El dataset procesado contiene únicamente registros válidos.

- El pipeline solo se detiene ante errores críticos de estructura, como:
  - Columnas obligatorias faltantes.
  - Imposibilidad de leer el archivo de entrada.
  - Fechas no parseables de forma masiva.

