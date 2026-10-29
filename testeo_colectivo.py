
from pathlib import Path

from pipeline.contexto import ContextoPipeline
from stages.carga import CargaExperimentos
from stages.preparacion import PreparacionTrayectorias
from stages.individual import AnalisisIndividual
from stages.espacial import AnalisisEspacial
from stages.colectivo import ComparacionExperimentos

contexto = ContextoPipeline(
    ruta_entrada=Path("data"),
    ruta_salida=Path("results"),
    fps=None,
    unidad="m"
)

# Ejecutar todas las etapas desarrolladas
experimentos = CargaExperimentos().ejecutar(None, contexto)

experimentos = PreparacionTrayectorias().ejecutar(
    experimentos, contexto
)

experimentos = AnalisisIndividual().ejecutar(
    experimentos, contexto
)

experimentos = AnalisisEspacial().ejecutar(
    experimentos, contexto
)

resultado = ComparacionExperimentos().ejecutar(
    experimentos, contexto
)

# Mostrar comparacion de experimentos
print("\nCOMPARACION DE EXPERIMENTOS")

comparacion = resultado.comparacion

for exp in resultado.experimentos:

    nombre = exp.nombre
    print(f"\nExperimento: {nombre}")

    indicadores = {
        "Peatones": "cantidad_peatones",
        "Velocidad media": "velocidad_media",
        "Densidad media": "densidad_media",
        "Flujo medio": "flujo_medio",
        "Distancia media": "distancia_media",
        "Tiempo medio": "tiempo_medio"
    }

    for etiqueta, clave in indicadores.items():
        valor = comparacion[f"{nombre}_{clave}"]
        print(f"  {etiqueta}: {valor:.4f}")

print("\nCORRELACION DENSIDAD - VELOCIDAD")

clave = "correlacion_densidad_velocidad"

if clave in comparacion:
    print(f"Correlacion: {comparacion[clave]:.4f}")
else:
    print("No fue posible calcular la correlacion.")

print("\nTotal de experimentos:", len(resultado.experimentos))
print("Comparacion finalizada.")
