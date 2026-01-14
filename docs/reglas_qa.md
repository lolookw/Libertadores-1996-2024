# Reglas de QA – Dataset Libertadores v1

## QA estructural

- No deben existir filas duplicadas según:
  - temporada
  - fecha
  - equipo_local
  - equipo_visitante

- Tipos de datos:
  - temporada: entero entre 1996 y 2024
  - goles_local, goles_visitante: enteros mayores o iguales a 0

## QA lógica

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

- Los registros que violen reglas críticas no se incluyen en el dataset final
- Los errores deben registrarse para revisión manual
