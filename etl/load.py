import pyodbc
import pandas as pd
import numpy as np

from database import get_connection


def truncate_dimension(nombre):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM {nombre}")

    conn.commit()

    conn.close()


def insert_dataframe(df, tabla):

    conn = get_connection()

    cursor = conn.cursor()

    columnas = list(df.columns)

    columnas_sql = ",".join(columnas)

    parametros = ",".join(["?"] * len(columnas))

    sql = f"""

    INSERT INTO {tabla}

    ({columnas_sql})

    VALUES

    ({parametros})

    """

    for fila in df.itertuples(index=False):

        valores = []

        for valor in fila:

            # Convertir NaN de pandas a NULL de SQL Server
            if pd.isna(valor):
                valores.append(None)

            # Convertir enteros de numpy
            elif isinstance(valor, np.integer):
                valores.append(int(valor))

            # Convertir decimales de numpy
            elif isinstance(valor, np.floating):
                valores.append(float(valor))

            else:
                valores.append(valor)

        cursor.execute(sql, tuple(valores))

    conn.commit()

    conn.close()

    print(f"{tabla} cargada correctamente.")