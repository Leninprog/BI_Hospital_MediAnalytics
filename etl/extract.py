# ============================================
# EXTRACCIÓN DE DATOS
# ============================================

import pandas as pd

from config import DATA_DIR


def extract_sources():

    print("=" * 60)
    print("LEYENDO FUENTES...")
    print("=" * 60)

    pacientes = pd.read_excel(DATA_DIR / "Pacientes.xlsx")

    medicos = pd.read_excel(DATA_DIR / "Medicos.xlsx")

    diagnosticos = pd.read_excel(DATA_DIR / "Diagnosticos.xlsx")

    atenciones = pd.read_excel(DATA_DIR / "Atenciones.xlsx")

    facturacion = pd.read_excel(DATA_DIR / "Facturacion_2026.xlsx")

    camas = pd.read_csv(DATA_DIR / "Camas.csv")

    encuestas = pd.read_csv(DATA_DIR / "Encuestas.csv")

    horas = pd.read_csv(DATA_DIR / "HorasExtras.csv")

    print("Pacientes:", len(pacientes))
    print("Medicos:", len(medicos))
    print("Diagnosticos:", len(diagnosticos))
    print("Atenciones:", len(atenciones))
    print("Facturacion:", len(facturacion))
    print("Camas:", len(camas))
    print("Encuestas:", len(encuestas))
    print("Horas Extras:", len(horas))

    return {
        "pacientes": pacientes,
        "medicos": medicos,
        "diagnosticos": diagnosticos,
        "atenciones": atenciones,
        "facturacion": facturacion,
        "camas": camas,
        "encuestas": encuestas,
        "horas": horas
    }