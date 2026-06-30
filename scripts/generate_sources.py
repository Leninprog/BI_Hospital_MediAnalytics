from faker import Faker
import pandas as pd
import numpy as np
from pathlib import Path
from random import randint, choice, random
from datetime import datetime, timedelta

fake = Faker("es_ES")
np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_sources"

DATA_DIR.mkdir(exist_ok=True)

print("Generando fuentes MediAnalytics...")

print("Generando pacientes...")

ciudades = [
    "Quito",
    "Guayaquil",
    "Cuenca",
    "Ambato",
    "Manta",
    "Loja",
    "Riobamba",
    "Machala"
]

seguros = [
    "Publico",
    "Privado",
    "Particular"
]

pacientes = []

for i in range(1, 2001):

    nombre = fake.name()

    if random() < 0.03:
        nombre = nombre.lower()

    ciudad = choice(ciudades)

    if random() < 0.02:
        ciudad = f" {ciudad} "

    sexo = choice(["M", "F"])

    if random() < 0.01:
        sexo = None

    fecha_nac = fake.date_between(
        start_date="-90y",
        end_date="-1y"
    )

    if random() < 0.01:
        fecha_nac = None

    pacientes.append({
        "IdPaciente": i,
        "NombreCompleto": nombre,
        "Sexo": sexo,
        "FechaNacimiento": fecha_nac,
        "Ciudad": ciudad,
        "TipoSeguro": choice(seguros),
        "FechaModificacion": fake.date_time_between(
            start_date="-18M",
            end_date="now"
        )
    })

df_pacientes = pd.DataFrame(pacientes)

df_pacientes.to_excel(
    DATA_DIR / "Pacientes.xlsx",
    index=False
)

print("Pacientes.xlsx generado")

print("Generando médicos...")

especialidades = [
    "Cardiología",
    "Pediatría",
    "Neurología",
    "Traumatología",
    "Medicina General",
    "Ginecología",
    "Cirugía General"
]

medicos = []

for i in range(1, 51):

    esp = choice(especialidades)

    if random() < 0.05:
        esp = esp.upper()

    if random() < 0.05:
        esp = esp.lower()

    medicos.append({
        "CodigoMedico": f"MED{i:03}",
        "NombreMedico": fake.name(),
        "Especialidad": esp,
        "Estado": choice(["Activo", "Activo", "Activo", "Inactivo"]),
        "FechaModificacion": fake.date_time_between(
            start_date="-18M",
            end_date="now"
        )
    })

df_medicos = pd.DataFrame(medicos)

df_medicos.to_excel(
    DATA_DIR / "Medicos.xlsx",
    index=False
)

print("Medicos.xlsx generado")

print("Generando diagnósticos...")

categorias = [
    "Respiratorio",
    "Cardiovascular",
    "Neurológico",
    "Digestivo",
    "Traumatológico",
    "Ginecológico"
]

diagnosticos = []

for i in range(1, 101):

    diagnosticos.append({
        "CodigoCIE10": f"D{i:03}",
        "Descripcion": f"Diagnóstico {i}",
        "Categoria": choice(categorias),
        "FechaModificacion": fake.date_time_between(
            start_date="-18M",
            end_date="now"
        )
    })

df_diag = pd.DataFrame(diagnosticos)

df_diag.to_excel(
    DATA_DIR / "Diagnosticos.xlsx",
    index=False
)

print("Diagnosticos.xlsx generado")
print("Catálogos generados correctamente")

print("Preparando datos para atenciones...")

ids_pacientes = df_pacientes["IdPaciente"].tolist()
ids_medicos = df_medicos["CodigoMedico"].tolist()
ids_diagnosticos = df_diag["CodigoCIE10"].tolist()

servicios = {
    "URG": "Urgencias",
    "CONS": "Consulta Externa",
    "HOSP": "Hospitalizacion",
    "CIR": "Cirugia"
}

print("Generando atenciones...")

atenciones = []

for i in range(1, 10001):

    servicio = choice(list(servicios.keys()))

    if random() < 0.02:
        servicio = choice([
            "Urgencia",
            "URG",
            "consulta",
            "Hospital",
            ""
        ])

    tiempo_espera = randint(5, 180)

    if random() < 0.01:
        tiempo_espera = -5

    diagnostico = choice(ids_diagnosticos)

    if random() < 0.01:
        diagnostico = None

    fecha_atencion = fake.date_time_between(
        start_date="-18M",
        end_date="now"
    )

    atenciones.append({
        "IdAtencion": i,
        "IdPaciente": choice(ids_pacientes),
        "CodigoMedico": choice(ids_medicos),
        "CodigoServicio": servicio,
        "CodigoDiagnostico": diagnostico,
        "FechaAtencion": fecha_atencion,
        "TiempoEsperaMin": tiempo_espera,
        "DuracionConsultaMin": randint(10, 90),
        "CostoOperativo": round(
            np.random.uniform(20, 500),
            2
        ),
        "Readmitido30Dias": np.random.choice(
            [0, 1],
            p=[0.9, 0.1]
        ),
        "FechaModificacion": fake.date_time_between(
            start_date=fecha_atencion,
            end_date="now"
        )
    })

df_atenciones = pd.DataFrame(atenciones)

df_atenciones.to_excel(
    DATA_DIR / "Atenciones.xlsx",
    index=False
)

print("Atenciones.xlsx generado")

print("Generando facturación...")

# Cada atención genera exactamente UNA factura asociada (1 a 1).
# Esto asegura que el merge en el ETL sea correcto y no duplique filas.
facturas = []

for idx, atencion in enumerate(atenciones, start=1):

    seguro = choice([
        "Publico",
        "Privado",
        "Particular"
    ])

    if random() < 0.03:
        seguro = choice([
            "PUBLICO",
            "privado",
            "PARTICULAR"
        ])

    monto_total = round(
        np.random.uniform(50, 2000),
        2
    )

    if random() < 0.01:
        monto_total = None

    monto_cubierto = None

    if monto_total is not None:
        monto_cubierto = round(
            monto_total * np.random.uniform(0.4, 1),
            2
        )

    fecha_factura = fake.date_time_between(
        start_date=atencion["FechaAtencion"],
        end_date="now"
    )

    facturas.append({
        "NumFactura": f"FAC{idx:06}",
        "IdAtencion": atencion["IdAtencion"],
        "IdPaciente": atencion["IdPaciente"],
        "FechaFactura": fecha_factura,
        "CodigoServicio": atencion["CodigoServicio"],
        "MontoTotal": monto_total,
        "MontoCubierto": monto_cubierto,
        "TipoSeguro": seguro,
        "EstadoCobro": choice([
            "Pagado",
            "Pendiente",
            "Anulado"
        ]),
        "FechaModificacion": fake.date_time_between(
            start_date=fecha_factura,
            end_date="now"
        )
    })

df_facturas = pd.DataFrame(facturas)

df_facturas.to_excel(
    DATA_DIR / "Facturacion_2026.xlsx",
    index=False
)

print("Facturacion_2026.xlsx generado")

print("Generando camas...")

camas = []

for i in range(1, 15001):

    fecha_registro = fake.date_time_between(
        start_date="-18M",
        end_date="now"
    )

    estado = choice([
        "Ocupada",
        "Disponible",
        "Mantenimiento"
    ])

    if random() < 0.03:
        estado = choice([
            "ocupada",
            "OCUPADA",
            "disponible",
            "DISPONIBLE"
        ])

    paciente = None

    if "ocup" in estado.lower():
        paciente = choice(ids_pacientes)

    camas.append({
        "Fecha": fecha_registro.date(),
        "NroCama": f"C-{randint(1,500):03}",
        "Piso": randint(1, 8),
        "Servicio": choice(list(servicios.values())),
        "Estado": estado,
        "IdPaciente": paciente,
        "Turno": choice([
            "Mañana",
            "Tarde",
            "Noche"
        ]),
        "HoraRegistro": fecha_registro,
        "FechaModificacion": fake.date_time_between(
            start_date=fecha_registro,
            end_date="now"
        )
    })

df_camas = pd.DataFrame(camas)

df_camas.to_csv(
    DATA_DIR / "Camas.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Camas.csv generado")

print("Generando encuestas...")

encuestas = []

comentarios = [
    "Excelente atención",
    "Tiempo de espera elevado",
    "Muy buena experiencia",
    "Regular",
    "Volvería nuevamente",
    "",
    None
]

for i in range(1, 5001):

    fecha_encuesta = fake.date_time_between(
        start_date="-18M",
        end_date="now"
    )

    puntaje_general = randint(1, 10)

    if random() < 0.01:
        puntaje_general = choice([0, 11])

    puntaje_espera = randint(1, 10)

    if random() < 0.01:
        puntaje_espera = choice([0, 11])

    puntaje_trato = randint(1, 10)

    if random() < 0.01:
        puntaje_trato = choice([0, 11])

    encuestas.append({
        "IdEncuesta": i,
        "IdPaciente": choice(ids_pacientes),
        "CodigoMedico": choice(ids_medicos),
        "CodigoServicio": choice(list(servicios.keys())),
        "FechaEncuesta": fecha_encuesta,
        "PuntajeGeneral": puntaje_general,
        "PuntajeEspera": puntaje_espera,
        "PuntajeTrato": puntaje_trato,
        "Comentario": choice(comentarios),
        "FechaModificacion": fake.date_time_between(
            start_date=fecha_encuesta,
            end_date="now"
        )
    })

df_encuestas = pd.DataFrame(encuestas)

df_encuestas.to_csv(
    DATA_DIR / "Encuestas.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Encuestas.csv generado")

print("Generando horas extras...")

personal = []

for i in range(1, 101):

    personal.append({
        "CodigoPersonal": f"PER{i:03}",
        "NombrePersonal": fake.name(),
        "Cargo": choice([
            "Enfermero",
            "Enfermera",
            "Auxiliar",
            "Supervisor"
        ])
    })

horas_extras = []

for i in range(1, 3001):

    empleado = choice(personal)

    turno = choice([
        "Mañana",
        "Tarde",
        "Noche"
    ])

    if random() < 0.05:
        turno = choice([
            "noche",
            "NOCHE",
            "mañana"
        ])

    fecha_registro = fake.date_between(
        start_date="-18M",
        end_date="today"
    )

    horas_extras.append({
        "IdRegistro": i,
        "CodigoPersonal": empleado["CodigoPersonal"],
        "NombrePersonal": empleado["NombrePersonal"],
        "Cargo": empleado["Cargo"],
        "Servicio": choice(list(servicios.values())),
        "Turno": turno,
        "FechaRegistro": fecha_registro,
        "HorasExtras": round(
            np.random.uniform(1, 12),
            2
        ),
        "CostoHoraExtra": round(
            np.random.uniform(5, 25),
            2
        ),
        "FechaModificacion": fake.date_time_between(
            start_date="-18M",
            end_date="now"
        )
    })

df_horas = pd.DataFrame(horas_extras)

df_horas.to_csv(
    DATA_DIR / "HorasExtras.csv",
    index=False,
    encoding="utf-8-sig"
)

print("HorasExtras.csv generado")

print("=" * 50)
print("TODAS LAS FUENTES GENERADAS CORRECTAMENTE")
print("=" * 50)