import pandas as pd
from extract import extract_sources

from transform import transformar_pacientes
from transform import transformar_medicos
from transform import transformar_diagnosticos
from transform import transformar_servicios
from transform import transformar_seguro
from transform import crear_dim_tiempo
from transform import transformar_camas
from transform import transformar_personal
from load import truncate_dimension
from load import insert_dataframe
from fact_builder import probar_dimensiones
from fact_builder import construir_fact_atencion
from fact_builder import construir_fact_ocupacion
from fact_builder import construir_fact_satisfaccion
from fact_builder import construir_fact_horas_extras
from fact_builder import mostrar_resumen_fact

from incremental import cargar_incremental


def main():

    data = extract_sources()

    pacientes = transformar_pacientes(data["pacientes"])

    medicos = transformar_medicos(data["medicos"])

    diagnosticos = transformar_diagnosticos(
        data["diagnosticos"]
    )

    fila_desconocido = pd.DataFrame([{
        "CodigoCIE10": "DESCONOCIDO",
        "Descripcion": "Diagnostico desconocido",
        "Categoria": "No Clasificado"
    }])

    diagnosticos = pd.concat(
        [fila_desconocido, diagnosticos],
        ignore_index=True
    )

    servicios = transformar_servicios(data["atenciones"])

    fila_servicio_desconocido = pd.DataFrame([{
        "CodigoServicio": "DESCONOCIDO",
        "NombreServicio": "Servicio Desconocido"
    }])

    servicios = pd.concat(
        [fila_servicio_desconocido, servicios],
        ignore_index=True
    )

    seguros = transformar_seguro(pacientes)

    tiempo = crear_dim_tiempo()

    camas = transformar_camas(data["camas"])

    personal = transformar_personal(data["horas"])
    
    truncate_dimension("DIM_TIEMPO")

    insert_dataframe(

        tiempo[

            [

                "TiempoKey",

                "FechaCompleta",

                "Dia",

                "Mes",

                "NombreMes",

                "Trimestre",

                "Anio",

                "SemanaAnio",

                "DiaSemana"

            ]

        ],

        "DIM_TIEMPO"

    )
    
    truncate_dimension("DIM_PACIENTE")

    insert_dataframe(

        pacientes[

            [

                "IdPaciente",

                "NombreCompleto",

                "Sexo",

                "FechaNacimiento",

                "Edad",

                "Ciudad",

                "TipoSeguro"

            ]

        ].rename(

            columns={

                "IdPaciente":"IdPacienteOrigen"

            }

        ),

        "DIM_PACIENTE"

    )
    
    truncate_dimension("DIM_MEDICO")

    insert_dataframe(

        medicos[

            [

                "CodigoMedico",

                "NombreMedico",

                "Especialidad",

                "Estado"

            ]

        ],

        "DIM_MEDICO"

    )
    
    truncate_dimension("DIM_DIAGNOSTICO")

    insert_dataframe(

        diagnosticos[

            [

                "CodigoCIE10",

                "Descripcion",

                "Categoria"

            ]

        ],

        "DIM_DIAGNOSTICO"

    )
    
    truncate_dimension("DIM_SERVICIO")

    insert_dataframe(

        servicios,

        "DIM_SERVICIO"

    )
    
    truncate_dimension("DIM_SEGURO")

    insert_dataframe(

        seguros,

        "DIM_SEGURO"

    )
    
    truncate_dimension("DIM_CAMA")

    insert_dataframe(

        camas,

        "DIM_CAMA"

    )

    truncate_dimension("DIM_PERSONAL")

    insert_dataframe(

        personal[

            [

                "CodigoPersonal",

                "NombrePersonal",

                "Cargo",

                "Servicio",

                "Turno",

                "Estado"

            ]

        ],

        "DIM_PERSONAL"

    )
    
    probar_dimensiones()

    print()

    print("="*60)
    print("CONSTRUYENDO TABLAS FACT")
    print("="*60)

    fact_atencion = construir_fact_atencion(data)

    fact_ocupacion = construir_fact_ocupacion(data)

    fact_satisfaccion = construir_fact_satisfaccion(data)

    fact_horas = construir_fact_horas_extras(data)

    mostrar_resumen_fact(

        fact_atencion,

        fact_ocupacion,

        fact_satisfaccion,

        fact_horas

    )

    print()

    print("="*60)

    print("CARGANDO DIMENSIONES")

    print("="*60)
    
    print()

    print("Pacientes limpios")

    print(pacientes.head())

    print()

    print(servicios)
    
    print()

    print("Dim Tiempo")

    print(tiempo.head())

    print()

    print("Dim Cama")

    print(camas.head())

    print()

    print("Dim Personal")

    print(personal.head())
    
    print()

    print("="*60)
    print("CARGA INCREMENTAL")
    print("="*60)

    cargar_incremental(

        fact_atencion,

        "FACT_ATENCION",

        "FACT_ATENCION"

    )

    cargar_incremental(

        fact_ocupacion,

        "FACT_OCUPACION_CAMAS",

        "FACT_OCUPACION_CAMAS"

    )

    cargar_incremental(

        fact_satisfaccion,

        "FACT_SATISFACCION",

        "FACT_SATISFACCION"

    )

    cargar_incremental(

        fact_horas,

        "FACT_HORAS_EXTRAS",

        "FACT_HORAS_EXTRAS"

    )

    print()

    print("="*60)
    print("ETL FINALIZADO")
    print("="*60)


if __name__ == "__main__":

    main()