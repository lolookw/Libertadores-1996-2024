# Auditoría dataset enhanced — Copa Libertadores 1996–2024

## Resumen
- Total partidos: 2575
- Temporadas cubiertas: 29 de 29
- Rango: 1996–2024
- Promedio goles local: 1.75
- Promedio goles visitante: 0.99

## Cobertura por temporada

| Temporada | Grupos | Octavos | Cuartos | Semifinal | Final | Total |
|-----------|--------|---------|---------|-----------|-------|-------|
| 1996 | 60 | 6 | 4 | 2 | 2 | 74 |
| 1997 | ⚠️ 0 | 0 | 10 | ⚠️ 0 | 2 | 12 |
| 1998 | 9 | 0 | 4 | 4 | 2 | 19 |
| 1999 | 72 | 0 | ⚠️ 0 | ⚠️ 0 | 2 | 74 |
| 2000 | 106 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 106 |
| 2001 | 108 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 108 |
| 2002 | 99 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 99 |
| 2003 | 105 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 105 |
| 2004 | 105 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 105 |
| 2005 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |
| 2006 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |
| 2007 | 94 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 94 |
| 2008 | 89 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 89 |
| 2009 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |
| 2010 | 94 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 94 |
| 2011 | 95 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 95 |
| 2012 | 86 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 86 |
| 2013 | 78 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 78 |
| 2014 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |
| 2015 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |
| 2016 | 95 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 95 |
| 2017 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |
| 2018 | 95 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 95 |
| 2019 | 94 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 94 |
| 2020 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |
| 2021 | 93 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 93 |
| 2022 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |
| 2023 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |
| 2024 | 96 | 0 | ⚠️ 0 | ⚠️ 0 | ⚠️ 0 | 96 |

## Campos con valores faltantes (post-enhanced)

- `instancia`: 9 valores vacíos/nulos de 2575
- `url_fuente`: 2575 valores vacíos/nulos de 2575
- `id_partido_fuente`: 2575 valores vacíos/nulos de 2575
- `observaciones`: 2537 valores vacíos/nulos de 2575

## Gaps conocidos — requieren completado via IA

Ver `docs/prompt_completar_datos.md` para el prompt listo para enviar a Claude u otra IA.

| Año | Tipo de gap | Estimación filas faltantes |
|-----|------------|---------------------------|
| 1997 | Grupos completos (formato RSSSF sin espacio) | ~60 |
| 1998 | Grupos parciales (misma causa) | ~50 |
| 2012 | Grupos casi completos (formato sin guion) | ~105 |
| 2000–2024 | Eliminatorias (Octavos, Cuartos, Semifinal, Final) | ~400 |

**Total estimado de filas faltantes**: ~615 partidos adicionales.

Con esas filas, el dataset pasaría de ~2575 a ~3190 partidos.
