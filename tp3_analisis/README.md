# TP N.º 3 – Análisis y visualización

Cinco preguntas de negocio sobre el dataset limpio del TP N.º 2, resueltas con SQL y Pandas.

| Pregunta | Resultado | Gráfico |
|---|---|---|
| Q1 · Socios vigentes por actividad | 18 vigentes; Pádel concentra 7 | Barras horizontales |
| Q2 · Cuotas al día | 75 % de los que deben pagar; $74.000 pendientes | Torta |
| Q3 · Morosidad por actividad | Fútbol 5: 50 % pendiente (2 de 4) | Barras con color destacado |
| Q4 · Cuota promedio por tipo | Activo $18.750 · Cadete $12.000 | Tabla |
| Q5 · Altas por año | 13 de 18 en 2024; ninguna en 2025 | Líneas |

## Archivos

| Archivo | Contenido |
|---|---|
| `tp3_analisis.py` | Ejecuta las consultas, verifica SQL vs Pandas y genera los gráficos |
| `cerro_alto_tp3.sql` | Base **no normalizada** (tabla única `socios`, estructura de `cerro_alto_simple.sql` de la cátedra) con los datos limpios y las consultas, para MySQL |
| `resultados_tp3.txt` | Salida de cada consulta |
| `grafico_q*.png` | Gráficos del informe |

## Decisiones de datos

- Se usan los datos limpios del TP N.º 2 (19 registros) y no `cerro_alto_simple_insercion.sql`, para mantener
  las decisiones documentadas. Por ejemplo, se conserva a Florencia Castro (119) y la cuota de 105 queda en NULL
  hasta que tesorería la confirme.
- Se agregó la columna `condicion` (Vigente / Baja) a la tabla única para excluir al socio dado de baja (111).

```bash
python tp3_analisis.py        # requiere haber corrido antes el TP 2
```
