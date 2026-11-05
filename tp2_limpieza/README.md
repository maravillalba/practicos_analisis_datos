# TP N.º 2 – Limpieza y preparación de datos

`practico.py` aplica, con Python/Pandas, el tratamiento propuesto en el TP N.º 1 para cada problema (P1 a P16).

- **Entrada:** `../datos/Registro_Socios_Cuotas_Cerro_Alto_Para_Alumnos.xlsx` (no se modifica).
- **Salida:** `../datos/Registro_Socios_LIMPIO.xlsx`, con 3 hojas:
  - `Socios_limpio`: los 19 socios.
  - `Bitacora`: cada decisión con su razón y las filas afectadas.
  - `Validacion`: métricas antes y después.
- **Transformaciones:** ALTA y CUOTA convertidas de texto a fecha y a número. Variables derivadas
  `ANTIGÜEDAD_MESES` (al 31/10/2026) y `SEGMENTO_ANTIGÜEDAD`.
- **Casos a confirmar con el club:** quedan marcados en la columna `REVISAR` (104, 105, 106, 108, 111 y 119).
- **Controles:** el script tiene 8 controles `assert` que lo detienen si queda algún problema sin resolver.

```bash
python practico.py
```

