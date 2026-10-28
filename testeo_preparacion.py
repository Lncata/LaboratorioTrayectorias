# =================================================
# ARCHIVO TEMPORAL PARA TESTEAR 
# =================================================


from pathlib import Path

from pipeline.contexto import ContextoPipeline
from stages.carga import CargaExperimentos
from stages.preparacion import PreparacionTrayectorias

# Configurar los datos de entrada
contexto = ContextoPipeline(
    ruta_entrada=Path("data"),
    ruta_salida=Path("results"),
    fps=None,
    unidad="m"
)

# Etapa 1: cargar los experimentos
carga = CargaExperimentos()
experimentos = carga.ejecutar(None, contexto)

# Etapa 2: preparar las trayectorias
preparacion = PreparacionTrayectorias()
experimentos = preparacion.ejecutar(experimentos, contexto)

# Mostrar un resumen
print("\nRESUMEN FINAL")

for exp in experimentos:
    print(f"\nExperimento: {exp.nombre}")
    print(f"FPS: {exp.fps}")
    print(f"Observaciones: {len(exp.observaciones)}")
    print(f"Trayectorias: {len(exp.trayectorias)}")

print("\nTotal de experimentos:", len(experimentos))
