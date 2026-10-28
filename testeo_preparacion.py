# =================================================
# ARCHIVO TEMPORAL PARA TESTEAR 
# =================================================


from pathlib import Path
from stages.individual import AnalisisIndividual
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


# Etapa 3: analizar las trayectorias individuales
analisis = AnalisisIndividual()
experimentos = analisis.ejecutar(experimentos, contexto)

print("\nRESULTADOS DEL ANALISIS INDIVIDUAL")

for exp in experimentos:

    print(f"\nExperimento: {exp.nombre}")
    print(f"FPS: {exp.fps}")

    resultados = exp.resultados_individuales

    print(f"Peatones analizados: {len(resultados)}")

    # Mostrar los indicadores de un peaton como ejemplo
    if resultados:
        id_peaton, indicadores = next(iter(resultados.items()))

        print(f"Ejemplo - Peaton {id_peaton}")

        for nombre, valor in indicadores.items():
            print(f"  {nombre}: {valor:.3f}")

# Comprobar las frecuencias del dataset
for exp in experimentos:
    fps_esperados = 25 if exp.nombre == "uni_corr_500_02" else 16
    assert exp.fps == fps_esperados, (
        f"FPS incorrectos en {exp.nombre}: {exp.fps}"
    )

print("\nFrecuencias verificadas correctamente.")
print("Analisis individual completado.")

