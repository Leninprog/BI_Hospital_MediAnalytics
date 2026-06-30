import pandas as pd

from database import get_connection


# ==========================================================
# LEER TODAS LAS DIMENSIONES DESDE SQL SERVER
# ==========================================================

def cargar_dimensiones():

    conn = get_connection()

    dimensiones = {}

    dimensiones["paciente"] = pd.read_sql("""

        SELECT
            PacienteKey,
            IdPacienteOrigen,
            TipoSeguro
        FROM DIM_PACIENTE

    """, conn)

    dimensiones["medico"] = pd.read_sql("""

        SELECT
            MedicoKey,
            CodigoMedico
        FROM DIM_MEDICO

    """, conn)

    dimensiones["diagnostico"] = pd.read_sql("""

        SELECT
            DiagnosticoKey,
            CodigoCIE10
        FROM DIM_DIAGNOSTICO

    """, conn)

    dimensiones["servicio"] = pd.read_sql("""

        SELECT
            ServicioKey,
            CodigoServicio
        FROM DIM_SERVICIO

    """, conn)

    dimensiones["seguro"] = pd.read_sql("""

        SELECT
            SeguroKey,
            TipoSeguro
        FROM DIM_SEGURO

    """, conn)

    dimensiones["tiempo"] = pd.read_sql("""

        SELECT
            TiempoKey,
            FechaCompleta
        FROM DIM_TIEMPO

    """, conn)

    dimensiones["cama"] = pd.read_sql("""

        SELECT
            CamaKey,
            NumeroCama
        FROM DIM_CAMA

    """, conn)

    dimensiones["personal"] = pd.read_sql("""

        SELECT
            PersonalKey,
            CodigoPersonal
        FROM DIM_PERSONAL

    """, conn)

    conn.close()

    return dimensiones


# ==========================================================
# SOLO PARA COMPROBAR
# ==========================================================

def probar_dimensiones():

    dims = cargar_dimensiones()

    print()

    print("=" * 60)
    print("DIMENSIONES")
    print("=" * 60)

    for nombre, tabla in dims.items():

        print(f"{nombre.upper():15} {len(tabla)}")


# ==========================================================
# NORMALIZAR SERVICIOS
# ==========================================================

def normalizar_servicio(valor):

    if pd.isna(valor):
        return "DESCONOCIDO"

    valor = str(valor).strip()

    if valor == "":
        return "DESCONOCIDO"

    mapa = {

        "URG": "URG",
        "Urgencia": "URG",

        "CONS": "CONS",
        "consulta": "CONS",

        "HOSP": "HOSP",
        "Hospital": "HOSP",

        "CIR": "CIR"

    }

    return mapa.get(valor, "DESCONOCIDO")


# ==========================================================
# FACT ATENCION
# ==========================================================

def construir_fact_atencion(data):

    dims = cargar_dimensiones()

    at = data["atenciones"].copy()

    fac = data["facturacion"].copy()

    # ----------------------------
    # NORMALIZAR FECHAS
    # ----------------------------

    at["FechaAtencion"] = pd.to_datetime(
        at["FechaAtencion"]
    ).dt.date

    fac["FechaFactura"] = pd.to_datetime(
        fac["FechaFactura"]
    ).dt.date

    dims["tiempo"]["FechaCompleta"] = pd.to_datetime(
        dims["tiempo"]["FechaCompleta"]
    ).dt.date

    # ----------------------------
    # NORMALIZAR SERVICIOS
    # ----------------------------

    at["CodigoServicio"] = at["CodigoServicio"].apply(
        normalizar_servicio
    )

    fac["CodigoServicio"] = fac["CodigoServicio"].apply(
        normalizar_servicio
    )

    # ----------------------------
    # MERGE FACTURACION
    # ----------------------------

    fact = at.merge(

        fac,

        left_on="IdAtencion",

        right_on="IdAtencion",

        how="left",

        suffixes=("", "_fac")

    )

    # ----------------------------
    # TIEMPO
    # ----------------------------

    fact = fact.merge(

        dims["tiempo"],

        left_on="FechaAtencion",

        right_on="FechaCompleta",

        how="left"

    )

    # ----------------------------
    # PACIENTE
    # ----------------------------

    fact = fact.merge(

        dims["paciente"],

        left_on="IdPaciente",

        right_on="IdPacienteOrigen",

        how="left"

    )

    # ----------------------------
    # MEDICO
    # ----------------------------

    fact = fact.merge(

        dims["medico"],

        on="CodigoMedico",

        how="left"

    )

    # ----------------------------
    # DIAGNOSTICO
    # ----------------------------

    fact = fact.merge(

        dims["diagnostico"],

        left_on="CodigoDiagnostico",

        right_on="CodigoCIE10",

        how="left"

    )
    
    # Buscar el DiagnosticoKey real asignado a la fila "DESCONOCIDO"
    desconocido = dims["diagnostico"][
        dims["diagnostico"]["CodigoCIE10"] == "DESCONOCIDO"
    ]

    if desconocido.empty:
        raise ValueError(
            "No existe la fila 'DESCONOCIDO' en DIM_DIAGNOSTICO. "
            "Verifica que main.py la haya insertado antes de correr el ETL."
        )

    key_desconocido = int(desconocido["DiagnosticoKey"].iloc[0])

    fact["DiagnosticoKey"] = (
        fact["DiagnosticoKey"]
        .fillna(key_desconocido)
        .astype(int)
    )
    
    print("\nDIAGNOSTICOS SIN MATCH")
    print(
        fact[
            fact["DiagnosticoKey"].isna()
        ][
            ["CodigoDiagnostico"]
        ]
        .drop_duplicates()
        .head(50)
    )

    # ----------------------------
    # SERVICIO
    # ----------------------------

    fact = fact.merge(

        dims["servicio"],

        on="CodigoServicio",

        how="left"

    )
    
    print("\nCOLUMNAS FACT:")
    print(fact.columns.tolist())

    # ----------------------------
    # SEGURO
    # ----------------------------

    fact["TipoSeguro"] = (

        fact["TipoSeguro_x"]

        .fillna(fact["TipoSeguro_y"])

        .astype(str)

        .str.strip()

        .str.title()

    )

    fact = fact.merge(

        dims["seguro"],

        on="TipoSeguro",

        how="left"

    )

    # ----------------------------
    # READMITIDO
    # ----------------------------

    fact["Readmitido30Dias"] = (

        fact["Readmitido30Dias"]

        .fillna(0)

        .astype(int)

    )

    # ----------------------------
    # COLUMNAS FINALES
    # ----------------------------

    fact = fact[

        [

            "TiempoKey",

            "PacienteKey",

            "MedicoKey",

            "ServicioKey",

            "DiagnosticoKey",

            "SeguroKey",

            "TiempoEsperaMin",

            "DuracionConsultaMin",

            "MontoTotal",

            "MontoCubierto",

            "CostoOperativo",

            "Readmitido30Dias",

            "FechaModificacion"

        ]

    ]

    fact = fact.rename(

        columns={

            "MontoTotal": "MontoFacturado"

        }

    )

    print()

    print("=" * 60)

    print("FACT ATENCION")

    print("=" * 60)

    print(fact.head())

    print()

    print("Registros:", len(fact))
    
    print()
    print("DIAGNOSTICO KEYS EN FACT")
    print(
        fact["DiagnosticoKey"]
        .sort_values()
        .drop_duplicates()
        .head(20)
    )

    print()
    print("MIN:", fact["DiagnosticoKey"].min())
    print("MAX:", fact["DiagnosticoKey"].max())

    print()
    print("NULOS:")
    print(fact["DiagnosticoKey"].isna().sum())

    return fact

# ==========================================================
# FACT OCUPACION CAMAS
# ==========================================================

def construir_fact_ocupacion(data):

    dims = cargar_dimensiones()

    camas = data["camas"].copy()

    camas["Fecha"] = pd.to_datetime(
        camas["Fecha"]
    ).dt.date

    dims["tiempo"]["FechaCompleta"] = pd.to_datetime(
        dims["tiempo"]["FechaCompleta"]
    ).dt.date

    camas["Servicio"] = camas["Servicio"].apply(
        normalizar_servicio
    )

    dims["cama"]["NumeroCama"] = dims["cama"]["NumeroCama"].astype(str)

    camas["NroCama"] = camas["NroCama"].astype(str)

    fact = camas.merge(

        dims["tiempo"],

        left_on="Fecha",

        right_on="FechaCompleta",

        how="left"

    )

    fact = fact.merge(

        dims["servicio"],

        left_on="Servicio",

        right_on="CodigoServicio",

        how="left"

    )

    fact = fact.merge(

        dims["cama"],

        left_on="NroCama",

        right_on="NumeroCama",

        how="left"

    )

    fact["Ocupada"] = (

        fact["Estado"]

        .str.upper()

        .eq("OCUPADA")

        .astype(int)

    )

    fact = fact[[

        "TiempoKey",

        "ServicioKey",

        "CamaKey",

        "Ocupada",

        "FechaModificacion"

    ]]

    print()

    print("="*60)

    print("FACT OCUPACION CAMAS")

    print("="*60)

    print(fact.head())

    print()

    print("Registros:", len(fact))

    return fact


# ==========================================================
# FACT SATISFACCION
# ==========================================================

def construir_fact_satisfaccion(data):

    dims = cargar_dimensiones()

    enc = data["encuestas"].copy()

    enc["FechaEncuesta"] = pd.to_datetime(
        enc["FechaEncuesta"]
    ).dt.date

    dims["tiempo"]["FechaCompleta"] = pd.to_datetime(
        dims["tiempo"]["FechaCompleta"]
    ).dt.date

    enc["CodigoServicio"] = enc["CodigoServicio"].apply(
        normalizar_servicio
    )

    fact = enc.merge(

        dims["tiempo"],

        left_on="FechaEncuesta",

        right_on="FechaCompleta",

        how="left"

    )

    fact = fact.merge(

        dims["paciente"],

        left_on="IdPaciente",

        right_on="IdPacienteOrigen",

        how="left"

    )

    fact = fact.merge(

        dims["medico"],

        on="CodigoMedico",

        how="left"

    )

    fact = fact.merge(

        dims["servicio"],

        on="CodigoServicio",

        how="left"

    )

    fact = fact[[

        "TiempoKey",

        "PacienteKey",

        "MedicoKey",

        "ServicioKey",

        "PuntajeGeneral",

        "PuntajeEspera",

        "PuntajeTrato",

        "FechaModificacion"

    ]]

    print()

    print("="*60)

    print("FACT SATISFACCION")

    print("="*60)

    print(fact.head())

    print()

    print("Registros:", len(fact))

    return fact

# ==========================================================
# FACT HORAS EXTRAS
# ==========================================================

def construir_fact_horas_extras(data):

    dims = cargar_dimensiones()

    horas = data["horas"].copy()

    horas["FechaRegistro"] = pd.to_datetime(
        horas["FechaRegistro"]
    ).dt.date

    dims["tiempo"]["FechaCompleta"] = pd.to_datetime(
        dims["tiempo"]["FechaCompleta"]
    ).dt.date

    horas["Servicio"] = horas["Servicio"].apply(
        normalizar_servicio
    )

    fact = horas.merge(

        dims["tiempo"],

        left_on="FechaRegistro",

        right_on="FechaCompleta",

        how="left"

    )

    fact = fact.merge(

        dims["personal"],

        on="CodigoPersonal",

        how="left"

    )

    fact = fact.merge(

        dims["servicio"],

        left_on="Servicio",

        right_on="CodigoServicio",

        how="left"

    )

    fact = fact[[

        "TiempoKey",

        "PersonalKey",

        "ServicioKey",

        "HorasExtras",

        "CostoHoraExtra",

        "FechaModificacion"

    ]]

    print()

    print("="*60)

    print("FACT HORAS EXTRAS")

    print("="*60)

    print(fact.head())

    print()

    print("Registros:", len(fact))

    return fact


# ==========================================================
# VALIDAR FACT
# ==========================================================

def validar_fact(df, nombre):

    print()

    print("="*60)

    print(f"VALIDANDO {nombre}")

    print("="*60)

    nulos = df.isnull().sum()

    print(nulos[nulos > 0])

    print()

    print("Duplicados:", df.duplicated().sum())

    print()

    print("Total registros:", len(df))


# ==========================================================
# RESUMEN GENERAL
# ==========================================================

def mostrar_resumen_fact(

    fact_atencion,

    fact_ocupacion,

    fact_satisfaccion,

    fact_horas

):

    print()

    print("="*60)

    print("RESUMEN DEL ETL")

    print("="*60)

    print()

    print(f"FACT_ATENCION............. {len(fact_atencion):>8}")

    print(f"FACT_OCUPACION_CAMAS...... {len(fact_ocupacion):>8}")

    print(f"FACT_SATISFACCION......... {len(fact_satisfaccion):>8}")

    print(f"FACT_HORAS_EXTRAS......... {len(fact_horas):>8}")

    print()

    validar_fact(fact_atencion, "FACT_ATENCION")

    validar_fact(fact_ocupacion, "FACT_OCUPACION_CAMAS")

    validar_fact(fact_satisfaccion, "FACT_SATISFACCION")

    validar_fact(fact_horas, "FACT_HORAS_EXTRAS")