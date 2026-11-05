# Trabajos Prácticos – Introducción al Análisis de Datos

**UTN FRT – Tecnicatura Universitaria en Programación – Ciclo 2026**
Comisión 11 · Villalba Mara Patricia
Caso integrador: **Club Deportivo Cerro Alto** (padrón de socios y cuotas)

Los tres TPs forman una sola cadena de trabajo: cada uno usa el resultado del anterior.

```
datos/Registro_Socios_..._Para_Alumnos.xlsx   (original de la cátedra, sin modificar)
        │
        ▼  TP 1 · detectar los problemas de calidad
        ▼  TP 2 · limpiarlos  ──►  datos/Registro_Socios_LIMPIO.xlsx
        ▼  TP 3 · analizar y visualizar el dataset limpio
```

| TP | Tema | Contenido | Resultado principal |
|---|---|---|---|
| [TP 1](tp1_calidad/) | Calidad e inspección de datos | Informe | 16 problemas de calidad en las 5 dimensiones; 21 registros para 19 personas |
| [TP 2](tp2_limpieza/) | Limpieza y preparación | `practico.py` + informe | Dataset limpio de 19 socios, con bitácora y validación antes/después |
| [TP 3](tp3_analisis/) | Análisis y visualización | `tp3_analisis.py`, SQL, gráficos + informe | 75 % de cuotas al día, $74.000 pendientes, morosidad concentrada en Fútbol 5 |

## Estructura

```
practicos_analisis_datos/
├── datos/            # original de la cátedra + dataset limpio que genera el TP 2
├── tp1_calidad/      # informe del TP 1
├── tp2_limpieza/     # script de limpieza + informe del TP 2
└── tp3_analisis/     # script de análisis, SQL, resultados, gráficos + informe del TP 3
```

## Cómo ejecutarlo

Requisitos: Python 3.10 o superior.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1            # PowerShell  (CMD: .venv\Scripts\activate.bat)
pip install pandas openpyxl matplotlib

cd tp2_limpieza
python practico.py                    # genera datos/Registro_Socios_LIMPIO.xlsx
cd ../tp3_analisis
python tp3_analisis.py                # genera resultados, SQL y gráficos
```

Para la base de datos del TP 3: abrir `tp3_analisis/cerro_alto_tp3.sql` en MySQL Workbench y ejecutarlo.
