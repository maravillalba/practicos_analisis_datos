# ==============================================================================
# TP N.º 3 - Análisis y visualización (Unidades 4 y 5)
# Introducción al Análisis de Datos - UTN FRT - Comisión 11
# Integrante: Villalba Mara Patricia
#
# Entrada : ../datos/Registro_Socios_LIMPIO.xlsx (dataset limpio generado por el TP N.º 2)
# Salidas : cerro_alto_tp3.sql  -> base NO normalizada (tabla única "socios",
#                                  estructura de cerro_alto_simple.sql de la
#                                  cátedra) + INSERT de los datos limpios + consultas
#           resultados_tp3.txt  -> resultado de cada consulta
#           grafico_q1..q5.png  -> gráficos para el informe
#
# Las consultas se escriben en SQL estándar (funcionan en MySQL Workbench) y
# acá se ejecutan con SQLite, que viene incluido en Python, para verificarlas.
# ==============================================================================

import os
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')                      # genera los PNG sin abrir ventanas
import matplotlib.pyplot as plt

CARPETA = os.path.dirname(os.path.abspath(__file__))
ruta = lambda nombre: os.path.join(CARPETA, nombre)

# ------------------------------------------------------------------------------
# 1. CARGA DEL DATASET LIMPIO (TP N.º 2)
# ------------------------------------------------------------------------------
df = pd.read_excel(os.path.join(CARPETA, '..', 'datos', 'Registro_Socios_LIMPIO.xlsx'), sheet_name='Socios_limpio',
                   dtype={'TELÉFONO': str})
df['ALTA'] = pd.to_datetime(df['ALTA'])

# Adaptación a la tabla única de la cátedra (cerro_alto_simple.sql).
# Se agrega la columna "condicion" (Vigente / Baja), creada en el TP N.º 2 al
# separar CAT., porque sin ella no se puede excluir al socio dado de baja.
socios = pd.DataFrame({
    'id': df['ID'],
    'socio': df['SOCIO'],
    'dni': df['DNI'],
    'alta': df['ALTA'].dt.strftime('%Y-%m-%d'),          # NaT -> NaN -> NULL
    'actividad': df['ACTIVIDAD'],
    'cat': df['TIPO_SOCIO'],
    'cuota': df['CUOTA'],                                # 105 queda NULL a propósito
    'estado': df['ESTADO'],
    'email': df['EMAIL'],
    'telefono': df['TELÉFONO'],
    'observaciones': df['OBSERVACIONES'],
    'antiguedad_meses': df['ANTIGÜEDAD_MESES'],
    'condicion': df['CONDICIÓN'],
})

# ------------------------------------------------------------------------------
# 2. GENERACIÓN DEL SCRIPT SQL (MySQL) CON LOS DATOS LIMPIOS
# ------------------------------------------------------------------------------
def valor_sql(v):
    if pd.isna(v):
        return 'NULL'
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f'{v:.2f}' if isinstance(v, float) else str(v)
    return "'" + str(v).replace("'", "''") + "'"

CREATE = """CREATE TABLE socios (
    id INT,
    socio VARCHAR(100) NOT NULL,
    dni INT,
    alta DATE,
    actividad VARCHAR(50),
    cat VARCHAR(50),
    cuota DECIMAL(10, 2),
    estado VARCHAR(50),
    email VARCHAR(100),
    telefono VARCHAR(50),
    observaciones TEXT,
    antiguedad_meses DECIMAL(5, 1),
    condicion VARCHAR(20)   -- agregada: Vigente / Baja (TP N.º 2)
);"""

columnas = list(socios.columns)
filas_sql = []
for _, fila in socios.iterrows():
    valores = []
    for c in columnas:
        v = fila[c]
        if c in ('id', 'dni') and not pd.isna(v):
            v = int(v)
        if c == 'antiguedad_meses' and not pd.isna(v):
            v = float(v)
        valores.append(valor_sql(v))
    filas_sql.append('(' + ', '.join(valores) + ')')
INSERT = (f"INSERT INTO socios ({', '.join(columnas)}) VALUES\n"
          + ',\n'.join(filas_sql) + ';')

# ------------------------------------------------------------------------------
# 3. CONSULTAS (una por pregunta de negocio)
# ------------------------------------------------------------------------------
CONSULTAS = {
    'Q1': ('¿Cuántos socios vigentes tiene el club y en qué actividades se concentran?',
"""SELECT actividad,
       COUNT(*) AS socios_vigentes
FROM socios
WHERE condicion = 'Vigente'
GROUP BY actividad
ORDER BY socios_vigentes DESC;"""),

    'Q2a': ('¿Qué parte de los socios vigentes tiene la cuota al día? (detalle por estado)',
"""SELECT estado,
       COUNT(*) AS cantidad,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM socios WHERE condicion = 'Vigente'), 1) AS porcentaje,
       SUM(cuota) AS monto
FROM socios
WHERE condicion = 'Vigente'
GROUP BY estado
ORDER BY cantidad DESC;"""),

    'Q2b': ('¿Qué porcentaje de los socios que deben pagar está al día y cuánto dinero está pendiente?',
"""SELECT COUNT(*) AS socios_que_pagan_cuota,
       SUM(CASE WHEN estado = 'Pagado' THEN 1 ELSE 0 END) AS al_dia,
       ROUND(SUM(CASE WHEN estado = 'Pagado' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS porcentaje_al_dia,
       SUM(CASE WHEN estado = 'Pendiente' THEN cuota ELSE 0 END) AS monto_pendiente
FROM socios
WHERE condicion = 'Vigente'
  AND estado <> 'Exento';"""),

    'Q3': ('¿En qué actividades se concentra la morosidad?',
"""SELECT actividad,
       COUNT(*) AS socios_que_pagan,
       SUM(CASE WHEN estado = 'Pendiente' THEN 1 ELSE 0 END) AS pendientes,
       ROUND(SUM(CASE WHEN estado = 'Pendiente' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS porcentaje_pendiente,
       SUM(CASE WHEN estado = 'Pendiente' THEN cuota ELSE 0 END) AS monto_pendiente
FROM socios
WHERE condicion = 'Vigente'
  AND estado <> 'Exento'
GROUP BY actividad
ORDER BY porcentaje_pendiente DESC, pendientes DESC;"""),

    'Q4': ('¿Cuál es la cuota promedio por tipo de socio?',
"""SELECT cat AS tipo_socio,
       COUNT(cuota) AS socios_con_cuota,
       ROUND(AVG(cuota), 2) AS cuota_promedio,
       MIN(cuota) AS cuota_minima,
       MAX(cuota) AS cuota_maxima
FROM socios
WHERE condicion = 'Vigente'
  AND cuota > 0          -- excluye exentos ($0) y la cuota a verificar (NULL)
GROUP BY cat
ORDER BY cuota_promedio DESC;"""),
}

# Propuesta de IA (consigna 5), tal como se recibió, para verificarla.
PROPUESTA_IA = """SELECT estado,
       COUNT(*) AS cantidad,
       (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM socios)) AS porcentaje
FROM socios
GROUP BY estado;"""

# ------------------------------------------------------------------------------
# 4. EJECUCIÓN (SQLite en memoria) Y REGISTRO DE RESULTADOS
# ------------------------------------------------------------------------------
con = sqlite3.connect(':memory:')
con.execute(CREATE)
con.execute(INSERT)
assert con.execute('SELECT COUNT(*) FROM socios').fetchone()[0] == len(df) == 19

resultados = {k: pd.read_sql_query(sql, con) for k, (_, sql) in CONSULTAS.items()}
resultado_ia = pd.read_sql_query(PROPUESTA_IA, con)

# --- Verificación cruzada SQL vs Pandas (misma lógica: GROUP BY <-> groupby) ---
vig = df[df['CONDICIÓN'] == 'Vigente']
pandas_q1 = vig.groupby('ACTIVIDAD').size().sort_values(ascending=False)
assert pandas_q1.sum() == resultados['Q1']['socios_vigentes'].sum() == 18
assert dict(pandas_q1) == dict(zip(resultados['Q1']['actividad'], resultados['Q1']['socios_vigentes']))
pagan = vig[vig['ESTADO'] != 'Exento']
assert round((pagan['ESTADO'] == 'Pagado').mean() * 100, 1) == resultados['Q2b']['porcentaje_al_dia'][0]

# --- Q4 complementada con estadística descriptiva (Pandas) ---------------------
# SQL no tiene mediana ni moda estándar: se calculan con Pandas.
cuotas_pagantes = vig.loc[vig['CUOTA'] > 0, 'CUOTA']
descriptiva = pd.Series({
    'n (socios que pagan, con cuota registrada)': cuotas_pagantes.count(),
    'Media': round(cuotas_pagantes.mean(), 2),
    'Mediana': cuotas_pagantes.median(),
    'Moda': cuotas_pagantes.mode().iloc[0],
    'Mínimo': cuotas_pagantes.min(),
    'Máximo': cuotas_pagantes.max(),
    'Rango': cuotas_pagantes.max() - cuotas_pagantes.min(),
    'Desvío estándar': round(cuotas_pagantes.std(), 2),
})

# --- Q5 (Pandas): evolución de altas por año -----------------------------------
# Se usan TODOS los socios (también el dado de baja: su alta ocurrió igual).
# La fila 106 no tiene fecha válida y queda afuera (n = 18).
altas_por_anio = (df['ALTA'].dt.year.dropna().astype(int)
                  .value_counts().reindex(range(2021, 2027), fill_value=0))

with open(ruta('resultados_tp3.txt'), 'w', encoding='utf-8') as f:
    for k, (pregunta, sql) in CONSULTAS.items():
        f.write(f'===== {k}: {pregunta}\n{sql}\n\n{resultados[k].to_string(index=False)}\n\n')
    f.write('===== Q4 (complemento Pandas): estadística descriptiva de la cuota\n')
    f.write(descriptiva.to_string() + '\n\n')
    f.write('===== Q5 (Pandas): altas por año\n' + altas_por_anio.to_string() + '\n\n')
    f.write('===== Consigna 5: propuesta de IA ejecutada sin cambios\n'
            f'{PROPUESTA_IA}\n\n{resultado_ia.to_string(index=False)}\n')

with open(ruta('cerro_alto_tp3.sql'), 'w', encoding='utf-8') as f:
    f.write('-- TP N.º 3 - Base NO normalizada (tabla única) con los datos limpios del TP N.º 2\n')
    f.write('CREATE DATABASE IF NOT EXISTS club_deportivo_cerro_alto;\nUSE club_deportivo_cerro_alto;\n\n')
    f.write('DROP TABLE IF EXISTS socios;\n' + CREATE + '\n\n' + INSERT + '\n\n')
    for k, (pregunta, sql) in CONSULTAS.items():
        f.write(f'-- {k}: {pregunta}\n{sql}\n\n')
    f.write('-- Q5: ¿Cómo evolucionaron las altas de socios por año? (versión MySQL;\n'
            '-- en el informe se resolvió con Pandas: no muestra los años sin altas, como 2025)\n'
            'SELECT YEAR(alta) AS anio, COUNT(*) AS altas\nFROM socios\nWHERE alta IS NOT NULL\n'
            'GROUP BY YEAR(alta)\nORDER BY anio;\n')

# ------------------------------------------------------------------------------
# 5. GRÁFICOS (Unidad 5: el gráfico se elige según la pregunta)
# ------------------------------------------------------------------------------
AZUL, NARANJA, GRIS = '#2a78d6', '#eb6834', '#b9b8b2'
TINTA, TINTA_2 = '#0b0b0b', '#52514e'
plt.rcParams.update({'font.size': 11, 'axes.edgecolor': TINTA_2, 'axes.labelcolor': TINTA_2,
                     'xtick.color': TINTA_2, 'ytick.color': TINTA_2, 'axes.titleweight': 'bold',
                     'axes.titlesize': 13, 'axes.titlelocation': 'left',
                     'axes.spines.top': False, 'axes.spines.right': False})


def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(ruta(nombre), dpi=200, facecolor='white')
    plt.close(fig)


# Q1 - comparar categorías -> barras horizontales ordenadas
q1 = resultados['Q1'].sort_values('socios_vigentes')
fig, ax = plt.subplots(figsize=(7, 3.6))
barras = ax.barh(q1['actividad'], q1['socios_vigentes'], color=AZUL, height=0.6)
ax.bar_label(barras, padding=4, color=TINTA)
ax.set_xlim(0, q1['socios_vigentes'].max() + 1.5)
ax.set_xlabel('Socios vigentes')
ax.set_title('Pádel concentra 7 de los 18 socios vigentes')
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y', length=0)
ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
guardar(fig, 'grafico_q1_socios_por_actividad.png')

# Q2 - partes de un todo con 3 categorías -> torta (2 a 5 categorías)
q2 = resultados['Q2a'].set_index('estado').reindex(['Pagado', 'Pendiente', 'Exento'])
fig, ax = plt.subplots(figsize=(7.5, 4))
colores = [AZUL, NARANJA, GRIS]
cuñas, _ = ax.pie(q2['cantidad'], colors=colores, startangle=90, counterclock=False,
                  wedgeprops={'edgecolor': 'white', 'linewidth': 2})
etiquetas = [f'{e}: {int(n)} ({p:.1f} %)' for e, n, p in zip(q2.index, q2['cantidad'], q2['porcentaje'])]
ax.legend(cuñas, etiquetas, loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
ax.set_title('2 de cada 3 socios vigentes tienen la cuota pagada')
ax.set_aspect('equal')
guardar(fig, 'grafico_q2_estado_cuotas.png')

# Q3 - comparar categorías, destacando la relevante -> barras con color con propósito
q3 = resultados['Q3'].sort_values(['porcentaje_pendiente', 'pendientes'])
fig, ax = plt.subplots(figsize=(7, 3.6))
maximo = q3['porcentaje_pendiente'].max()
colores = [NARANJA if p == maximo else GRIS for p in q3['porcentaje_pendiente']]
barras = ax.barh(q3['actividad'], q3['porcentaje_pendiente'], color=colores, height=0.6)
ax.bar_label(barras, labels=[f'{p:.0f} %  ({int(n)} de {int(t)})' for p, n, t in
                             zip(q3['porcentaje_pendiente'], q3['pendientes'], q3['socios_que_pagan'])],
             padding=4, color=TINTA)
ax.set_xlim(0, 100)
ax.set_xlabel('% de socios con la cuota pendiente')
ax.set_title('Fútbol 5 tiene la mitad de sus socios con la cuota pendiente')
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y', length=0)
guardar(fig, 'grafico_q3_morosidad_por_actividad.png')

# Q5 - evolución temporal -> líneas
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(altas_por_anio.index, altas_por_anio.values, color=AZUL, linewidth=2, marker='o', markersize=7)
for x, y in altas_por_anio.items():
    ax.annotate(str(y), (x, y), textcoords='offset points', xytext=(0, 8), ha='center', color=TINTA)
ax.set_ylim(0, altas_por_anio.max() + 3)
ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))   # cantidades enteras
ax.set_xticks(list(altas_por_anio.index))
ax.set_xticklabels([str(a) if a != 2026 else '2026*' for a in altas_por_anio.index])
ax.set_ylabel('Altas de socios')
ax.set_title('Las altas se concentraron en 2024 y cayeron a cero en 2025')
ax.text(0, -0.28, '* 2026 hasta octubre. Sin la fila 106 (fecha de alta inválida).',
        transform=ax.transAxes, fontsize=9, color=TINTA_2)
ax.grid(axis='y', color='#e6e5e0', linewidth=0.8)
ax.set_axisbelow(True)
guardar(fig, 'grafico_q5_altas_por_anio.png')

print(open(ruta('resultados_tp3.txt'), encoding='utf-8').read())
