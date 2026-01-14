# Diccionario de datos – Dataset Libertadores v1

## Identificación del partido

| Columna | Tipo | Descripción |
|------|----|------------|
| temporada | int | Año de la edición de la Copa Libertadores |
| competicion | str | Nombre de la competencia ("Copa Libertadores") |
| fase | str | Fase del torneo (Grupos, Octavos, etc.) |
| instancia | str | Subinstancia (Grupo A, Ida, Vuelta, etc.) |

## Fecha y sede

| Columna | Tipo | Descripción |
|------|----|------------|
| fecha | date | Fecha del partido (YYYY-MM-DD) |
| pais_sede | str | País donde se disputó el partido |
| ciudad_sede | str | Ciudad del partido (puede ser null) |
| estadio | str | Estadio (puede ser null) |

## Equipos

| Columna | Tipo | Descripción |
|------|----|------------|
| equipo_local | str | Nombre normalizado del equipo local |
| equipo_visitante | str | Nombre normalizado del equipo visitante |
| pais_local | str | País del equipo local |
| pais_visitante | str | País del equipo visitante |

## Resultado

| Columna | Tipo | Descripción |
|------|----|------------|
| goles_local | int | Goles del equipo local |
| goles_visitante | int | Goles del equipo visitante |
| resultado | str | Resultado desde el punto de vista del local (L/V/E) |

## Metadata

| Columna | Tipo | Descripción |
|------|----|------------|
| fuente | str | Fuente de los datos |
| url_fuente | str | URL de origen |
| id_partido_fuente | str | Identificador en la fuente (si existe) |
| observaciones | str | Comentarios o aclaraciones |
