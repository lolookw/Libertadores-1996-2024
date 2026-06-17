# Prompt para completar el dataset con Claude u otra IA

## Contexto del archivo

Este prompt está pensado para enviarlo a Claude (claude.ai) o ChatGPT y obtener de vuelta filas CSV con los datos faltantes del dataset Copa Libertadores 1996–2024.

El dataset actual tiene **2281 partidos**, pero le faltan aproximadamente **~775 filas** adicionales:
- Grupos 1997 (~60 filas), 1998 parcial (~50), 2011 completo (~160), 2012 (~105)
- Eliminatorias de 2000 a 2024 (Octavos, Cuartos, Semifinal, Final) (~400 filas)

Con esas filas el dataset pasa a ~3050 partidos y queda listo para correr `Modelo-Libertadores`.

---

## Esquema del CSV (21 columnas)

```
temporada,competicion,fase,instancia,fecha,pais_sede,ciudad_sede,estadio,equipo_local,equipo_visitante,pais_local,pais_visitante,goles_local,goles_visitante,resultado,fuente,url_fuente,id_partido_fuente,observaciones,resultado_norm,fecha_parseada
```

| Columna | Tipo | Descripción | Valores posibles |
|---------|------|-------------|-----------------|
| `temporada` | int | Año de la edición | 1996–2024 |
| `competicion` | str | Siempre igual | `Copa Libertadores` |
| `fase` | str | Fase del torneo | `Grupos`, `Octavos`, `Cuartos`, `Semifinal`, `Final` |
| `instancia` | str | Sub-instancia | `Group A`…`Group H` (grupos), `Ida` o `Vuelta` (eliminatorias) |
| `fecha` | str | Fecha del partido | `YYYY-MM-DD` |
| `pais_sede` | str | País sede (dejar vacío si no se sabe) | Argentina, Brasil, etc. |
| `ciudad_sede` | str | Ciudad sede (idem) | Buenos Aires, etc. |
| `estadio` | str | Nombre del estadio (idem) | |
| `equipo_local` | str | Equipo local (nombre canónico) | |
| `equipo_visitante` | str | Equipo visitante | |
| `pais_local` | str | País del equipo local | Argentina, Brasil, etc. |
| `pais_visitante` | str | País del equipo visitante | |
| `goles_local` | int | Goles del equipo local | 0, 1, 2, … |
| `goles_visitante` | int | Goles del equipo visitante | 0, 1, 2, … |
| `resultado` | str | Resultado del partido | `L` (local), `V` (visitante), `E` (empate) |
| `fuente` | str | Fuente del dato | `Wikipedia` (si viene de ahí) |
| `url_fuente` | str | URL de referencia | (opcional) |
| `id_partido_fuente` | str | ID en la fuente | (dejar vacío) |
| `observaciones` | str | Notas | (dejar vacío, o `agregado=X-Y` para series) |
| `resultado_norm` | str | Igual a resultado | `L`, `V`, `E` |
| `fecha_parseada` | str | Igual a fecha | `YYYY-MM-DD` |

**Reglas de consistencia:**
- `resultado` = `L` si `goles_local > goles_visitante`
- `resultado` = `V` si `goles_local < goles_visitante`
- `resultado` = `E` si `goles_local == goles_visitante`
- `resultado_norm` siempre igual a `resultado`
- `fecha_parseada` siempre igual a `fecha`
- Para eliminatorias: cada serie tiene DOS filas: una con `instancia=Ida` y otra con `instancia=Vuelta`, con equipos invertidos en la vuelta. El local del partido de ida es visitante en el de vuelta.
- `pais_sede` y `ciudad_sede` = país/ciudad del equipo local (aproximado)

---

## Prompt — copiar y pegar completo

```
Sos un asistente experto en Copa Libertadores de América. Tengo un dataset de partidos de Copa Libertadores 1996–2024 que está incompleto. Necesito que generes las filas faltantes en formato CSV, exactamente con estas 21 columnas en este orden:

temporada,competicion,fase,instancia,fecha,pais_sede,ciudad_sede,estadio,equipo_local,equipo_visitante,pais_local,pais_visitante,goles_local,goles_visitante,resultado,fuente,url_fuente,id_partido_fuente,observaciones,resultado_norm,fecha_parseada

Reglas obligatorias:
1. resultado = L si goles_local > goles_visitante, V si goles_local < goles_visitante, E si son iguales
2. resultado_norm es siempre igual a resultado
3. fecha_parseada es siempre igual a fecha (formato YYYY-MM-DD)
4. Para eliminatorias: cada serie se representa con DOS filas — Ida y Vuelta. En la fila Vuelta los equipos se invierten (el visitante de la Ida pasa a ser el local)
5. pais_sede ≈ pais_local (el partido se juega en la cancha del local, aproximadamente)
6. ciudad_sede y estadio: completar con el estadio principal del equipo local cuando sea conocido
7. fuente = "Wikipedia"
8. url_fuente, id_partido_fuente: dejar vacío
9. observaciones: para eliminatorias, poner "agregado=X-Y" con el marcador global de la serie
10. competicion = "Copa Libertadores" siempre
11. Si no sabés un dato con certeza (fecha exacta, goles), usá la mejor estimación y aclaralo en observaciones

[TAREA ESPECÍFICA — reemplazá esto con lo que necesitás]

Necesito los partidos de la fase de [FASE] de Copa Libertadores [AÑO].
Generá TODAS las filas correspondientes en CSV sin texto adicional antes ni después, solo el CSV.
No incluyas la línea de headers. Solo las filas de datos.
```

---

## Tareas por sección — copiar en lugar de `[TAREA ESPECÍFICA]`

### Para completar eliminatorias de un año específico

```
Necesito los partidos de las fases eliminatorias (Octavos, Cuartos, Semifinal y Final) 
de Copa Libertadores [AÑO]. 
Incluí todas las series, con fila de Ida y fila de Vuelta por cada serie.
Para la Final: si fue partido único, una sola fila con instancia=Final. 
Si fue ida y vuelta, dos filas.
Solo CSV, sin headers, sin explicaciones.
```

### Para completar grupos de un año específico

```
Necesito los partidos de la fase de Grupos de Copa Libertadores [AÑO].
Cada grupo lleva [N] equipos y [M] partidos por equipo (todos contra todos).
instancia = "Group A", "Group B", etc.
Solo CSV, sin headers, sin explicaciones.
```

### Para completar 2011 completo

```
Necesito TODOS los partidos de Copa Libertadores 2011, desde la Primera Ronda 
hasta la Final. Organizalos primero por fase (Grupos: instancia=Group A/B/C/D/E/F/G/H; 
Octavos: instancia=Ida/Vuelta; Cuartos: Ida/Vuelta; Semifinal: Ida/Vuelta; Final: Ida/Vuelta).
Solo CSV, sin headers, sin explicaciones.
```

---

## Cómo incorporar las filas al dataset

Una vez que Claude te devuelva el CSV, guardalo como `datos/externos/completado_ia_YYYY.csv` y corré:

```bash
python src/pipeline/fusionar_datos_ia.py datos/externos/completado_ia_YYYY.csv
```

(Ver `src/pipeline/fusionar_datos_ia.py`)

---

## Notas de calidad

- Claude 3.5/4 tiene conocimiento histórico de Copa Libertadores pero puede tener errores en fechas exactas o goles. Verificar los datos de Final y Semifinal contra Wikipedia.
- Para grupos, los goles en general son más fáciles de verificar con RSSSF o Wikipedia.
- El modelo `Modelo-Libertadores` es robusto a pequeños errores en goles, pero NO a errores en `equipo_local`, `equipo_visitante`, `pais_local` o `pais_visitante`.
- Siempre correr `python src/qa/chequeos_qa.py` sobre el CSV fusionado antes de usar el dataset en el modelo.