# ==============================================================================
# TP N.º 2 - Limpieza y preparación de datos (Unidad 3)
# Introducción al Análisis de Datos - UTN FRT - Comisión 11
# Integrante: Villalba Mara Patricia
# Caso: Club Deportivo Cerro Alto - Padrón de socios y cuotas
#
# Entrada : ../datos/Registro_Socios_Cuotas_Cerro_Alto_Para_Alumnos.xlsx (original, no se modifica)
# Salida  : ../datos/Registro_Socios_LIMPIO.xlsx  (hoja "Socios_limpio" + hoja "Bitacora")
#
# Cada bloque de limpieza tiene un código Pn que corresponde al problema
# relevado en el TP N.º 1. El script registra en la bitácora cuántas filas
# afectó cada decisión.
# ==============================================================================

import os
import pandas as pd

CARPETA = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(CARPETA, '..', 'datos')          # carpeta compartida por los TPs
ARCHIVO_ORIGINAL = os.path.join(DATOS, 'Registro_Socios_Cuotas_Cerro_Alto_Para_Alumnos.xlsx')
ARCHIVO_LIMPIO = os.path.join(DATOS, 'Registro_Socios_LIMPIO.xlsx')

# Fecha de corte para calcular la antigüedad (fin del período relevado).
# Se fija y se documenta para que el cálculo sea reproducible.
FECHA_CORTE = pd.Timestamp('2026-10-31')

bitacora = []  # una fila por decisión: problema, decisión, razón, filas afectadas


def registrar(problema, decision, razon, filas):
    """Agrega una decisión a la bitácora de limpieza."""
    bitacora.append({'Problema TP1': problema, 'Decisión': decision,
                     'Razón': razon, 'Filas afectadas': filas})


def agregar_alerta(df, mascara, texto):
    """Suma un texto a la columna REVISAR en las filas indicadas, sin pisar alertas previas."""
    actual = df.loc[mascara, 'REVISAR']
    df.loc[mascara, 'REVISAR'] = actual.where(actual == '', actual + ' | ') + texto


# ------------------------------------------------------------------------------
# 1. CARGA. La fila 1 del Excel es un título, por eso skiprows=1.
#    Se lee TELÉFONO como texto para que no se pierdan dígitos.
# ------------------------------------------------------------------------------
original = pd.read_excel(ARCHIVO_ORIGINAL, skiprows=1, dtype={'TELÉFONO': str})
df = original.copy()          # se trabaja sobre una copia: el original queda intacto
df['REVISAR'] = ''            # columna de alertas para casos que requieren confirmar con la fuente


# ------------------------------------------------------------------------------
# 2. INSPECCIÓN INICIAL (se guarda para compararla al final)
# ------------------------------------------------------------------------------
def inspeccionar(datos, col_categoria):
    """Métricas de calidad que se repiten antes y después de limpiar."""
    cuota_txt = datos['CUOTA'].astype(str)
    cuota_es_numero = pd.api.types.is_numeric_dtype(datos['CUOTA'])
    alta_es_fecha = pd.api.types.is_datetime64_any_dtype(datos['ALTA'])
    return {
        'Registros (filas)': len(datos),
        'Filas exactamente duplicadas': int(datos.duplicated(subset=[c for c in datos.columns if c != 'REVISAR']).sum()),
        'IDs repetidos': int(datos['ID'].duplicated().sum()),
        'DNI repetidos': int(datos['DNI'].duplicated().sum()),
        'Variantes de ACTIVIDAD': int(datos['ACTIVIDAD'].nunique()),
        'Variantes de categoría': int(datos[col_categoria].nunique()),
        'EMAIL vacío': int(datos['EMAIL'].isna().sum()),
        'TELÉFONO vacío': int(datos['TELÉFONO'].isna().sum()),
        'CUOTA guardada como texto': 0 if cuota_es_numero else len(datos),
        'Cuotas negativas': int(cuota_txt.str.contains('-').sum()),
        'Cuotas > $100.000': int((pd.to_numeric(datos['CUOTA'], errors='coerce') > 100000).sum()) if cuota_es_numero
                             else int(cuota_txt.str.contains('185.000', regex=False).sum()),
        'CUOTA vacía (marcada a propósito)': int(datos['CUOTA'].isna().sum()),
        'ALTA guardada como texto': 0 if alta_es_fecha else len(datos),
        'Fechas de ALTA inexistentes': int(datos['ALTA'].isna().sum()) if alta_es_fecha
                                       else int(pd.to_datetime(datos['ALTA'], format='%Y-%m-%d', errors='coerce').isna().sum()),
    }


antes = inspeccionar(df, 'CAT.')


# ==============================================================================
# 3. TRATAMIENTO DE CALIDAD (consigna 2)
# ==============================================================================

# --- P1 · Unicidad: el registro 101 está cargado dos veces -------------------
# Coinciden ID, DNI, fecha, cuota, mail y teléfono; solo cambian "Activo/Activa"
# y "día/dia". Es el mismo caso real -> se conserva la primera aparición.
filas_p1 = df.duplicated(subset=['ID', 'DNI'], keep='first')
df = df[~filas_p1]
registrar('P1', 'Eliminar la 2.ª fila del ID 101',
          'Mismo ID, DNI y datos de contacto: es el mismo socio cargado dos veces', int(filas_p1.sum()))

# --- P2 · Unicidad: "J. Perez" (110) es Juan Pérez (109) ------------------------
# Mismo DNI, alta, actividad, mail y teléfono. Se conserva 109 (nombre completo).
claves_persona = ['DNI', 'ALTA', 'EMAIL', 'TELÉFONO']
filas_p2 = df.duplicated(subset=claves_persona, keep='first')
ids_p2 = ', '.join(str(i) for i in df.loc[filas_p2, 'ID'])
df = df[~filas_p2]
registrar('P2', f'Eliminar el ID {ids_p2} y conservar el 109',
          'Mismo DNI + mismos datos de contacto que Juan Pérez; la fuente lo indica en OBSERVACIONES',
          int(filas_p2.sum()))

# --- P3 · Validez: 108 y 119 comparten DNI pero son dos personas distintas -----
# NO se elimina ninguna: si se deduplicara solo por DNI se perdería una socia real.
dni_repetido = df['DNI'].duplicated(keep=False)
agregar_alerta(df, dni_repetido, 'DNI compartido con otro socio: verificar con el área de socios')
registrar('P3', 'Conservar 108 y 119 y marcarlas en REVISAR',
          'Nombre, alta, actividad, mail y teléfono distintos: no es duplicado, un DNI está mal cargado',
          int(dni_repetido.sum()))

# --- P12 · Consistencia: ACTIVIDAD con 12 variantes para 6 deportes -----------
# Tabla de equivalencias (misma lógica que BUSCARV en Excel).
equivalencias_actividad = {
    'padel': 'Pádel', 'pádel': 'Pádel',
    'futbol 5': 'Fútbol 5', 'fútbol 5': 'Fútbol 5',
    'natacion': 'Natación', 'natación': 'Natación',
    'basquet': 'Básquet', 'básquet': 'Básquet',
    'gimnasio': 'Gimnasio', 'tenis': 'Tenis',
}
actividad_antes = df['ACTIVIDAD'].copy()
df['ACTIVIDAD'] = df['ACTIVIDAD'].str.strip().str.lower().map(equivalencias_actividad)
registrar('P12', 'Unificar ACTIVIDAD con una tabla de equivalencias',
          'Mismas actividades escritas con distintas mayúsculas/tildes',
          int((actividad_antes != df['ACTIVIDAD']).sum()))

# --- P4 + P13 · CAT. mezcla tipo de socio y condición; "Activo/Activa" -------
# Se separa en dos variables: TIPO_SOCIO y CONDICIÓN.
cat_original = df['CAT.'].str.strip()
df['CONDICIÓN'] = cat_original.map(lambda c: 'Baja' if c == 'Inactivo' else 'Vigente')
df['TIPO_SOCIO'] = cat_original.replace({'Activa': 'Activo', 'Inactivo': 'Sin dato'})
registrar('P13', 'Unificar "Activa" como "Activo"',
          'Misma categoría escrita de dos formas (no depende del género)',
          int((cat_original == 'Activa').sum()))
registrar('P4', 'Separar CAT. en TIPO_SOCIO y CONDICIÓN (Vigente / Baja)',
          '"Inactivo" es una condición, no un tipo de socio. El tipo de 111 queda "Sin dato" para no inventarlo',
          int((cat_original == 'Inactivo').sum()))

# --- P5 · Validez: CUOTA guardada como texto con formatos distintos -----------
# "$ 18.500", "$18.500", "$0", "$-18.500" -> número entero (18500, 0, -18500).
cuota_texto = df['CUOTA'].astype(str)
df['CUOTA'] = (cuota_texto.str.replace('$', '', regex=False)
                          .str.replace('.', '', regex=False)
                          .str.replace(' ', '', regex=False)
                          .astype(int))
registrar('P5', 'Convertir CUOTA de texto a número entero',
          'Con texto no se puede sumar ni promediar; se quitan "$", espacios y puntos de miles',
          len(df))

# --- P6 · Validez: cuota negativa (104) ---------------------------------------
# La propia fuente indica la causa ("Revisar signo") y la tarifa de un socio
# Activo es $18.500 -> se corrige solo el signo y se deja la alerta.
negativas = df['CUOTA'] < 0
df.loc[negativas, 'CUOTA'] = df.loc[negativas, 'CUOTA'].abs()
agregar_alerta(df, negativas, 'Cuota corregida de -18500 a 18500: confirmar con comprobante')
registrar('P6', 'Corregir el signo de la cuota negativa',
          'Una cuota no puede ser negativa; la fuente señaló el signo como causa', int(negativas.sum()))

# --- P7 · Validez: cuota de $185.000 (105) ------------------------------------
# Es un error de tipeo, pero no se sabe el valor correcto: puede ser 18500
# (un 0 de más) o 12000 (tarifa del otro Cadete). No se inventa: queda vacía
# (NaN) para que no entre en promedios, y se marca para tesorería.
sospechosas = df['CUOTA'] > 100000
df['CUOTA'] = df['CUOTA'].astype('float')          # float admite NaN
df.loc[sospechosas, 'CUOTA'] = float('nan')
agregar_alerta(df, sospechosas, 'Cuota original 185000: verificar tarifa Cadete con tesorería')
registrar('P7', 'Dejar la cuota de 105 como faltante (NaN) y marcarla',
          'Valor imposible con dos correcciones posibles (18500 o 12000): no hay evidencia para elegir',
          int(sospechosas.sum()))


# ==============================================================================
# 4. TRANSFORMACIONES ADICIONALES (consigna 3)
# ==============================================================================

# --- P8 + P9 · Conversión de tipo: ALTA de texto a fecha ----------------------
# errors='coerce' convierte "2026-02-30" (fecha inexistente) en NaT (faltante)
# en lugar de inventar un día.
df['ALTA'] = pd.to_datetime(df['ALTA'], format='%Y-%m-%d', errors='coerce')
fecha_invalida = df['ALTA'].isna()
agregar_alerta(df, fecha_invalida, 'Fecha de alta original inexistente (2026-02-30): pedir la real')
registrar('P9', 'Convertir ALTA de texto a tipo fecha',
          'Permite ordenar y calcular la antigüedad', len(df))
registrar('P8', 'La fecha inexistente queda como faltante (NaT) y marcada',
          'El 30 de febrero no existe; no se inventa otro día', int(fecha_invalida.sum()))

# --- Variable derivada 1: ANTIGÜEDAD_MESES a la fecha de corte ----------------
# Meses completos entre ALTA y FECHA_CORTE.
meses = ((FECHA_CORTE.year - df['ALTA'].dt.year) * 12
         + (FECHA_CORTE.month - df['ALTA'].dt.month)
         - (FECHA_CORTE.day < df['ALTA'].dt.day).astype(int))
df['ANTIGÜEDAD_MESES'] = meses.astype('Int64')     # Int64 admite faltantes
registrar('Transformación', f'Crear ANTIGÜEDAD_MESES al {FECHA_CORTE:%d/%m/%Y}',
          'Variable derivada pedida por la consigna 3; fecha de corte fija y documentada',
          int(df['ANTIGÜEDAD_MESES'].notna().sum()))

# --- Variable derivada 2: SEGMENTO_ANTIGÜEDAD (categorización) ----------------
df['SEGMENTO_ANTIGÜEDAD'] = pd.cut(df['ANTIGÜEDAD_MESES'].astype('float'),
                                   bins=[-1, 11, 35, 1000],
                                   labels=['Nuevo (<12 meses)', 'Regular (12-35)', 'Antiguo (36+)'])
registrar('Transformación', 'Crear SEGMENTO_ANTIGÜEDAD (Nuevo / Regular / Antiguo)',
          'Agrupa la antigüedad para el análisis del TP N.º 3',
          int(df['SEGMENTO_ANTIGÜEDAD'].notna().sum()))


# ==============================================================================
# 5. RESTO DEL TRATAMIENTO DE CALIDAD
# ==============================================================================

# --- P10 + P11 · Completitud: EMAIL y TELÉFONO vacíos ------------------------
# No se imputa (no se puede inventar un contacto): se marca explícitamente.
email_vacio = df['EMAIL'].isna()
tel_vacio = df['TELÉFONO'].isna()
df['EMAIL'] = df['EMAIL'].fillna('Sin dato')
df['TELÉFONO'] = df['TELÉFONO'].fillna('Sin dato')
registrar('P10', 'EMAIL vacío -> "Sin dato"', 'Faltante marcado explícitamente; se pide al socio',
          int(email_vacio.sum()))
registrar('P11', 'TELÉFONO vacío -> "Sin dato"', 'Faltante marcado explícitamente; se pide al socio',
          int(tel_vacio.sum()))

# --- P14 · Consistencia: nombres sin tilde ----------------------------------
# Se corrigen contra la fuente: la tabla impresa del padrón
# (Registro_Socios_Cuotas_Cerro_Alto_Solo_Tabla.pdf) muestra los nombres con tilde.
correccion_nombres = {
    'Rocio Farias': 'Rocío Farías',
    'Lucia Peralta': 'Lucía Peralta',
    'Agustin Silva': 'Agustín Silva',
    'Sofia Martínez': 'Sofía Martínez',
}
nombres_antes = df['SOCIO'].copy()
df['SOCIO'] = df['SOCIO'].replace(correccion_nombres)
registrar('P14', 'Corregir nombres sin tilde según el padrón impreso',
          'Corrección contra una fuente, no por suposición', int((nombres_antes != df['SOCIO']).sum()))

# --- P15 · Actualidad: socio dado de baja en 2023 (111) ----------------------
# Se conserva el registro (historial), pero CONDICIÓN = "Baja" permite
# excluirlo de los análisis de socios vigentes.
baja = df['CONDICIÓN'] == 'Baja'
agregar_alerta(df, baja, 'Baja en 2023: excluir de socios vigentes y de cuotas a cobrar')
registrar('P15', 'Marcar 111 como Baja (ya resuelto con CONDICIÓN)',
          'La observación confirma la baja; no se borra para no perder el historial', int(baja.sum()))

# --- P16 · Actualidad: la observación "Fecha alta futura" (119) está vieja ---
obs_vieja = df['OBSERVACIONES'] == 'Fecha alta futura'
df.loc[obs_vieja, 'OBSERVACIONES'] = 'Alta 30/09/2026 válida (observación original desactualizada)'
registrar('P16', 'Actualizar la observación de 119',
          'El 30/09/2026 es anterior a la fecha de corte: la fecha es válida', int(obs_vieja.sum()))

# --- Otras normalizaciones de texto ------------------------------------------
df['ESTADO'] = df['ESTADO'].str.strip().str.capitalize()   # PAGADO -> Pagado (solo presentación)
registrar('Formato', 'ESTADO en mayúsculas -> "Pagado", "Pendiente", etc.',
          'Solo presentación: el formato ya era uniforme, no era un problema de calidad', len(df))

# --- Atípicos reales A1 (118, $22.000) y A2 (120, alta 2021, $0) -------------
registrar('A1, A2', 'Conservar sin cambios',
          'Son valores reales y explicables (Tenis tiene otra tarifa; 120 es Honorario exento)', 2)


# ==============================================================================
# 6. ORDEN FINAL DE COLUMNAS Y EXPORTACIÓN
# ==============================================================================
columnas = ['ID', 'SOCIO', 'DNI', 'ALTA', 'ANTIGÜEDAD_MESES', 'SEGMENTO_ANTIGÜEDAD',
            'ACTIVIDAD', 'TIPO_SOCIO', 'CONDICIÓN', 'CUOTA', 'ESTADO',
            'EMAIL', 'TELÉFONO', 'OBSERVACIONES', 'REVISAR']
limpio = df[columnas].reset_index(drop=True)


# ==============================================================================
# 7. VALIDACIÓN FINAL (consigna 5): se repite la inspección inicial
# ==============================================================================
despues = inspeccionar(limpio.rename(columns={'TIPO_SOCIO': 'CAT.'}), 'CAT.')
# EMAIL/TELÉFONO ahora dicen "Sin dato": se cuentan como faltantes marcados.
despues['EMAIL vacío'] = 0
despues['TELÉFONO vacío'] = 0

validacion = pd.DataFrame({'Antes': antes, 'Después': despues})
validacion.index.name = 'Métrica'

# Controles automáticos: si alguno falla, el script se detiene con un error.
assert limpio['ID'].is_unique, 'Quedaron IDs repetidos'
assert set(limpio['ACTIVIDAD']) == {'Pádel', 'Fútbol 5', 'Natación', 'Básquet', 'Gimnasio', 'Tenis'}
assert 'Activa' not in set(limpio['TIPO_SOCIO'])
assert (limpio['CUOTA'].dropna() >= 0).all(), 'Quedaron cuotas negativas'
assert (limpio['CUOTA'].dropna() <= 22000).all(), 'Quedaron cuotas fuera de las tarifas conocidas'
assert limpio['EMAIL'].notna().all() and limpio['TELÉFONO'].notna().all()
assert pd.api.types.is_datetime64_any_dtype(limpio['ALTA'])
assert (limpio['ALTA'].dropna() <= FECHA_CORTE).all(), 'Hay altas posteriores a la fecha de corte'

print('\nVALIDACIÓN FINAL (antes vs. después)')
print(validacion.to_string())
print('\nFilas marcadas para revisar con la fuente:')
print(limpio.loc[limpio['REVISAR'] != '', ['ID', 'SOCIO', 'REVISAR']].to_string(index=False))

bitacora_df = pd.DataFrame(bitacora)
with pd.ExcelWriter(ARCHIVO_LIMPIO, engine='openpyxl') as writer:
    salida = limpio.copy()
    salida['ALTA'] = salida['ALTA'].dt.date                     # fecha sin hora
    salida['SEGMENTO_ANTIGÜEDAD'] = salida['SEGMENTO_ANTIGÜEDAD'].astype(str).replace('nan', '')
    salida.to_excel(writer, sheet_name='Socios_limpio', index=False)
    bitacora_df.to_excel(writer, sheet_name='Bitacora', index=False)
    validacion.to_excel(writer, sheet_name='Validacion')

    # Formato legible: moneda, fecha dd/mm/aaaa, ancho de columnas y encabezado fijo
    hoja = writer.sheets['Socios_limpio']
    formatos = {'ALTA': 'dd/mm/yyyy', 'CUOTA': '"$" #,##0', 'ANTIGÜEDAD_MESES': '0'}
    for i, col in enumerate(salida.columns, start=1):
        letra = hoja.cell(row=1, column=i).column_letter
        ancho = max(len(str(col)), *(len(str(v)) for v in salida[col])) + 2
        hoja.column_dimensions[letra].width = min(ancho, 60)
        if col in formatos:
            for celda in hoja[letra][1:]:
                celda.number_format = formatos[col]
    hoja.freeze_panes = 'A2'
    for nombre in ['Bitacora', 'Validacion']:
        h = writer.sheets[nombre]
        for columna in h.columns:
            h.column_dimensions[columna[0].column_letter].width = min(
                max(len(str(c.value or '')) for c in columna) + 2, 90)

print(f'\nArchivo generado: {os.path.basename(ARCHIVO_LIMPIO)} ({len(limpio)} filas)')
