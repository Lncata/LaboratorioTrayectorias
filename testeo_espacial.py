
from pathlib import Path

from pipeline.contexto import ContextoPipeline
from stages.carga import CargaExperimentos
from stages.preparacion import PreparacionTrayectorias
from stages.espacial import AnalisisEspacial

# Configurar un experimento real
contexto = ContextoPipeline(
    ruta_entrada=Path("data/uni_corr_500_01.txt"),
    ruta_salida=Path("results"),
    fps=None,
    unidad="m"
)

# Etapa 1: cargar datos
carga = CargaExperimentos()
experimentos = carga.ejecutar(None, contexto)

# Etapa 2: reconstruir trayectorias
preparacion = PreparacionTrayectorias()
experimentos = preparacion.ejecutar(experimentos, contexto)

# Etapa 3: ejecutar analisis espacial
espacial = AnalisisEspacial()
experimentos = espacial.ejecutar(experimentos, contexto)

# Mostrar los resultados
exp = experimentos[0]
resultados = exp.resultados_colectivos

print("\nRESUMEN ESPACIAL")

print("Experimento:", exp.nombre)
print("FPS:", exp.fps)

print("\nAnalisis de zonas:")
for zona in ["izquierda", "centro", "derecha"]:
    print(f"\nZona {zona}:")
    print("  Peatones:", resultados[f"zona_{zona}_peatones"])
    print(
        "  Velocidad media:",
        round(resultados[f"zona_{zona}_velocidad_media"], 3)
    )
    print(
        "  Tiempo medio de cruce:",
        round(resultados[f"zona_{zona}_tiempo_medio_cruce"], 3)
    )

print("\nDensidad:")
print("  Media:", round(resultados["densidad_media"], 4))
print("  Maxima:", round(resultados["densidad_maxima"], 4))

print("\nFlujo:")
print("  Cruces:", resultados["cruces_total"])
print("  Flujo medio:", round(resultados["flujo_medio"], 4))
print("  Izquierda a derecha:", resultados["cruces_izq_der"])
print("  Derecha a izquierda:", resultados["cruces_der_izq"])
