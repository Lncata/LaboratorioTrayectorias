"""Etapa 2: validación, organización y reconstrucción de trayectorias."""

import math
from dataclasses import replace
from itertools import groupby
from operator import attrgetter

from models.experimento import Experimento
from models.observacion import Observacion
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


def es_valida(obs: Observacion) -> bool:
    """Frame no negativo y coordenadas x e y numéricas."""
    return obs.frame >= 0 and not (math.isnan(obs.x) or math.isnan(obs.y))


def validar(observaciones: list[Observacion]) -> list[Observacion]:
    """Quita observaciones imposibles y repetidas (se conserva la primera de cada par id-frame)."""
    primeras = {
        (obs.id_peaton, obs.frame): obs
        for obs in reversed([o for o in observaciones if es_valida(o)])
    }
    return list(primeras.values())


def reconstruir_trayectorias(observaciones: list[Observacion]) -> list[Trayectoria]:
    """Una trayectoria por peatón (orden temporal); se necesitan al menos 2 puntos."""
    ordenadas = sorted(observaciones, key=lambda obs: (obs.id_peaton, obs.frame))
    trayectorias = [
        Trayectoria(id_peaton, list(grupo))
        for id_peaton, grupo in groupby(ordenadas, key=attrgetter("id_peaton"))
    ]
    return [t for t in trayectorias if len(t.observaciones) >= 2]


class PreparacionTrayectorias(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Limpia las observaciones y arma una trayectoria por peatón."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline) -> list[Experimento]:
        return [self._preparar(experimento) for experimento in experimentos]

    def _preparar(self, experimento: Experimento) -> Experimento:
        validas = validar(experimento.observaciones)
        trayectorias = reconstruir_trayectorias(validas)

        invalidas = len(experimento.observaciones) - len(validas)
        print(f"  {experimento.nombre}: {invalidas} observaciones inválidas, "
              f"{len(trayectorias)} trayectorias")

        if experimento.fps is None:
            raise ValueError(f"{experimento.nombre} no tiene fps: use --fps")
        return replace(experimento, trayectorias=trayectorias)
