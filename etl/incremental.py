import pandas as pd

from database import get_connection
from load import insert_dataframe


# ==========================================================
# OBTENER FECHA ÚLTIMA CARGA
# ==========================================================

def obtener_ultima_fecha(nombre_proceso):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT UltimaFechaCarga

        FROM ETL_CONTROL

        WHERE NombreProceso = ?

    """, nombre_proceso)

    fila = cursor.fetchone()

    conn.close()

    if fila:

        return pd.to_datetime(fila[0])

    return pd.Timestamp("1900-01-01")


# ==========================================================
# ACTUALIZAR FECHA DE CARGA
# ==========================================================

def actualizar_fecha(nombre_proceso, fecha):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE ETL_CONTROL

        SET UltimaFechaCarga = ?

        WHERE NombreProceso = ?

    """, fecha, nombre_proceso)

    conn.commit()

    conn.close()


# ==========================================================
# FILTRAR SOLO NUEVOS REGISTROS
# ==========================================================

def filtrar_incremental(df, nombre_proceso):

    ultima = obtener_ultima_fecha(nombre_proceso)

    df["FechaModificacion"] = pd.to_datetime(
        df["FechaModificacion"]
    )

    nuevos = df[
        df["FechaModificacion"] > ultima
    ].copy()

    return nuevos


# ==========================================================
# CARGA INCREMENTAL
# ==========================================================

def cargar_incremental(df, tabla, proceso):

    nuevos = filtrar_incremental(df, proceso)

    if len(nuevos) == 0:

        print(f"{tabla}: sin registros nuevos.")

        return

    insertar = nuevos.drop(
        columns=["FechaModificacion"]
    )

    insert_dataframe(

        insertar,

        tabla

    )

    actualizar_fecha(

        proceso,

        nuevos["FechaModificacion"].max()

    )

    print(f"{tabla}: {len(nuevos)} registros cargados.")