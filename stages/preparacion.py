"""Etapa 2: validación, organización y reconstrucción de trayectorias."""

import math

from models.experimento import Experimento
from models.observacion import Observacion
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class PreparacionTrayectorias(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Limpia las observaciones y arma una trayectoria por peatón."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline) -> list[Experimento]:
        for exp in experimentos:
            validas = self._validar_observaciones(exp.observaciones)
            por_peaton = self._organizar_observaciones(validas)
            exp.trayectorias = self._reconstruir_trayectorias(por_peaton)

            invalidas = len(exp.observaciones) - len(validas)
            print(f"  {exp.nombre}: {invalidas} observaciones inválidas, "
                  f"{len(exp.trayectorias)} trayectorias")

            if exp.fps is None:
                raise ValueError(f"{exp.nombre} no tiene fps: use --fps")
        return experimentos

    def _validar_observaciones(self, observaciones: list[Observacion]) -> list[Observacion]:
        """Elimina observaciones con valores imposibles o repetidas."""
        validas = []
        vistas = set()   # pares (id, frame) que ya aparecieron

        for obs in observaciones:
            clave = (obs.id_peaton, obs.frame)

            if obs.frame < 0:
                continue                      # frame negativo: imposible
            if math.isnan(obs.x) or math.isnan(obs.y):
                continue                      # coordenada vacía (NaN)
            if clave in vistas:
                continue                      # mismo peatón dos veces en el mismo frame

            vistas.add(clave)
            validas.append(obs)
        return validas

    def _organizar_observaciones(self, observaciones: list[Observacion]) -> dict[int, list[Observacion]]:
        """Agrupa las observaciones por peatón y las ordena por frame."""
        por_peaton = {}
        for obs in observaciones:
            if obs.id_peaton not in por_peaton:
                por_peaton[obs.id_peaton] = []
            por_peaton[obs.id_peaton].append(obs)

        for lista in por_peaton.values():
            lista.sort(key=lambda obs: obs.frame)
        return por_peaton

    def _reconstruir_trayectorias(self, por_peaton: dict[int, list[Observacion]]) -> list[Trayectoria]:
        """Crea una Trayectoria por peatón (se necesitan al menos 2 puntos)."""
        return [
            Trayectoria(id_peaton, lista)
            for id_peaton, lista in sorted(por_peaton.items())
            if len(lista) >= 2
        ]
