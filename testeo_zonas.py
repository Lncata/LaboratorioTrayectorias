# =================================================
# ARCHIVO TEMPORAL PARA TESTEAR 
# =================================================

from models.observacion import Observacion
from models.trayectoria import Trayectoria
from models.experimento import Experimento
from stages.espacial import AnalisisEspacial

# Peaton que avanza un metro cada segundo
observaciones = [
    Observacion(1, i * 16, float(i - 6), 2.0, 1.7)
    for i in range(13)
]

trayectoria = Trayectoria(1, observaciones)

experimento = Experimento(
    nombre="prueba_zonas",
    trayectorias=[trayectoria],
    fps=16
)

analisis = AnalisisEspacial()
resultados = analisis._analizar_zonas(experimento)

for nombre, valor in resultados.items():
    print(f"{nombre}: {valor:.3f}")
