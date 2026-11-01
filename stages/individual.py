"""Etapa de análisis individual de los experimentos."""

from dataclasses import replace

from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class AnalisisIndividual(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Calcula los indicadores de cada peatón (sin modificar los experimentos recibidos)."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline) -> list[Experimento]:
        return [self._analizar(experimento, contexto.umbral_detencion) for experimento in experimentos]

    def _analizar(self, experimento: Experimento, umbral_detencion: float) -> Experimento:
        resultados = {
            t.id_peaton: t.calcular_indicadores(experimento.fps, umbral_detencion)
            for t in experimento.trayectorias
        }
        return replace(experimento, resultados_individuales=resultados)
