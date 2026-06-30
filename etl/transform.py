# ============================================
# TRANSFORMACIÓN DE DATOS
# ============================================

import pandas as pd
import numpy as np

from datetime import datetime


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def limpiar_texto(valor):

    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if valor == "":
        return None

    return valor.title()


def calcular_edad(fecha):

    if pd.isna(fecha):
        return None

    hoy = datetime.today()

    return (
        hoy.year
        - fecha.year
        - (
            (hoy.month, hoy.day)
            <
            (fecha.month, fecha.day)
        )
    )
    
    # ============================================
# DIM PACIENTE
# ============================================

def transformar_pacientes(df):

    df = df.copy()

    df["NombreCompleto"] = df["NombreCompleto"].apply(limpiar_texto)

    df["Ciudad"] = df["Ciudad"].apply(limpiar_texto)

    df["TipoSeguro"] = df["TipoSeguro"].apply(limpiar_texto)

    df["Sexo"] = df["Sexo"].fillna("No especificado")

    df["Edad"] = (
        df["FechaNacimiento"]
        .apply(calcular_edad)
        .fillna(0)
        .astype(int)
    )

    return df

# ============================================
# DIM MEDICO
# ============================================

def transformar_medicos(df):

    df = df.copy()

    df["NombreMedico"] = df["NombreMedico"].apply(limpiar_texto)

    df["Especialidad"] = df["Especialidad"].apply(limpiar_texto)

    df["Estado"] = df["Estado"].apply(limpiar_texto)

    return df

# ============================================
# DIM DIAGNOSTICO
# ============================================

def transformar_diagnosticos(df):

    df = df.copy()

    df["Descripcion"] = df["Descripcion"].apply(limpiar_texto)

    df["Categoria"] = df["Categoria"].apply(limpiar_texto)

    return df

# ============================================
# DIM SERVICIO
# ============================================

def transformar_servicios(df_atenciones):

    df = df_atenciones.copy()

    mapa = {
        "URG": ("URG", "Urgencias"),
        "Urgencia": ("URG", "Urgencias"),
        "CONS": ("CONS", "Consulta Externa"),
        "consulta": ("CONS", "Consulta Externa"),
        "HOSP": ("HOSP", "Hospitalización"),
        "Hospital": ("HOSP", "Hospitalización"),
        "CIR": ("CIR", "Cirugía")
    }

    registros = []

    for codigo in df["CodigoServicio"].dropna().unique():

        if codigo in mapa:

            registros.append({
                "CodigoServicio": mapa[codigo][0],
                "NombreServicio": mapa[codigo][1]
            })

    servicios = pd.DataFrame(registros).drop_duplicates()

    return servicios

# ============================================
# DIM SEGURO
# ============================================

def transformar_seguro(df):

    seguros = pd.DataFrame({

        "TipoSeguro":

        sorted(

            df["TipoSeguro"]

            .dropna()

            .str.strip()

            .str.title()

            .unique()

        )

    })

    return seguros

# ============================================
# DIM TIEMPO
# ============================================

def crear_dim_tiempo():

    fechas = pd.date_range(
        start="2025-01-01",
        end="2026-12-31",
        freq="D"
    )

    tiempo = pd.DataFrame()

    tiempo["FechaCompleta"] = fechas

    tiempo["TiempoKey"] = tiempo["FechaCompleta"].dt.strftime("%Y%m%d").astype(int)

    tiempo["Dia"] = tiempo["FechaCompleta"].dt.day

    tiempo["Mes"] = tiempo["FechaCompleta"].dt.month

    tiempo["NombreMes"] = tiempo["FechaCompleta"].dt.month_name(locale="es_ES")

    tiempo["Trimestre"] = tiempo["FechaCompleta"].dt.quarter

    tiempo["Anio"] = tiempo["FechaCompleta"].dt.year

    tiempo["SemanaAnio"] = tiempo["FechaCompleta"].dt.isocalendar().week.astype(int)

    tiempo["DiaSemana"] = tiempo["FechaCompleta"].dt.day_name(locale="es_ES")

    return tiempo

# ============================================
# DIM CAMA
# ============================================

def transformar_camas(df):

    camas = df.copy()

    camas = camas.rename(columns={

        "NroCama":"NumeroCama",

        "Servicio":"ServicioAsignado"

    })

    camas = camas[

        [

            "NumeroCama",

            "Piso",

            "ServicioAsignado"

        ]

    ]

    camas = camas.drop_duplicates()

    return camas

# ============================================
# DIM PERSONAL
# ============================================

def transformar_personal(df):

    personal = df.copy()

    personal["NombrePersonal"] = personal["NombrePersonal"].apply(limpiar_texto)

    personal["Cargo"] = personal["Cargo"].apply(limpiar_texto)

    personal["Servicio"] = personal["Servicio"].apply(limpiar_texto)

    personal["Turno"] = personal["Turno"].apply(limpiar_texto)

    personal["Estado"] = "Activo"

    personal = personal.drop_duplicates(
        subset="CodigoPersonal"
    )

    return personal