"""Etapa de análisis espacial, densidad y flujo."""

from dataclasses import replace
from functools import reduce

from funciones.espacio import ZONAS, densidad, flujo, indicadores_zona
from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class AnalisisEspacial(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Zonas, densidad y flujo de cada experimento (sin modificar los recibidos)."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline) -> list[Experimento]:
        return [self._analizar(experimento) for experimento in experimentos]

    def _analizar(self, experimento: Experimento) -> Experimento:
        fps = experimento.fps
        if fps is None or fps <= 0:
            raise ValueError(f"FPS invalidos para {experimento.nombre}")
        trayectorias = experimento.trayectorias

        # une en un solo diccionario los indicadores de cada zona
        zonas = reduce(lambda acumulado, zona: {**acumulado, **indicadores_zona(trayectorias, fps, *zona)}, ZONAS, {})
        dens = densidad(trayectorias, fps)
        fluj = flujo(trayectorias, fps)

        print(f"\nExperimento: {experimento.nombre}")
        print(f"  Densidad media: {dens['densidad_media']:.4f}")
        print(f"  Flujo medio: {fluj['flujo_medio']:.4f}")
        print(f"  Cruces totales: {fluj['cruces_total']:.0f}")

        return replace(experimento, resultados_colectivos={**experimento.resultados_colectivos, **zonas, **dens, **fluj})
