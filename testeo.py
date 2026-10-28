# ===================================================
# ARCHIVO TEMPORAL SOLO PARA TESTEAR CLASES Y METODOS
# =================================================== 


from pathlib import Path

from models.observacion import Observacion
from models.trayectoria import Trayectoria
from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from stages.individual import AnalisisIndividual

# Crear observaciones de prueba
obs = [
    Observacion(1, 0, 0.00, 0, 0),
    Observacion(1, 25, 0.04, 0, 0),
    Observacion(1, 50, 0.08, 0, 0),
    Observacion(1, 75, 1.08, 0, 0),
    Observacion(1, 100, 1.10, 0, 0)
]

# Construir una trayectoria
trayectoria = Trayectoria(1, obs)

# Crear un experimento
experimento = Experimento(
    nombre="Experimento de prueba",
    trayectorias=[trayectoria]
)

# Crear configuracion
contexto = ContextoPipeline(
    ruta_entrada=Path("./data"),
    ruta_salida=Path("./results"),
    fps=25
)

# Ejecutar analisis individual
analisis = AnalisisIndividual()
experimentos = analisis.ejecutar([experimento], contexto)

# Mostrar resultados
for exp in experimentos:
    print("Experimento:", exp.nombre)

    for id_peaton, indicadores in exp.resultados_individuales.items():
        print("Peaton:", id_peaton)

        for nombre, valor in indicadores.items():
            print(f"{nombre}: {valor:.3f}")
