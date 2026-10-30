"""Etapa de análisis individual de los experimentos."""

from math import hypot

from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

UMBRAL_DETENCION = 0.1


class AnalisisIndividual(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Calcula los indicadores de cada peatón."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline) -> list[Experimento]:
        for experimento in experimentos:
            fps = experimento.fps
            resultados = {}

            for trayectoria in experimento.trayectorias:
                indicadores = self._calcular_indicadores(trayectoria, fps)
                detenciones = self._detectar_detenciones(trayectoria, fps)

                tiempo_detenido = sum((fin - inicio) / fps for inicio, fin in detenciones)
                tiempo_total = indicadores["tiempo_total"]

                indicadores["cantidad_detenciones"] = len(detenciones)
                indicadores["tiempo_detenido"] = tiempo_detenido
                indicadores["porcentaje_detenido"] = 100 * tiempo_detenido / tiempo_total if tiempo_total > 0 else 0.0

                resultados[trayectoria.id_peaton] = indicadores

            experimento.resultados_individuales = resultados
        return experimentos

    def _velocidades(self, trayectoria: Trayectoria, fps: float) -> list[tuple[int, int, float]]:
        """Velocidad en ventanas de 1 segundo: (frame_inicio, frame_fin, velocidad)."""
        obs = trayectoria.observaciones
        paso = min(int(fps), len(obs) - 1)
        velocidades = []

        for i in range(len(obs) - paso):
            a = obs[i]
            b = obs[i + paso]
            dt = (b.frame - a.frame) / fps
            velocidades.append((a.frame, b.frame, hypot(b.x - a.x, b.y - a.y) / dt))
        return velocidades

    def _calcular_indicadores(self, trayectoria: Trayectoria, fps: float) -> dict[str, float]:
        """Calcula los indicadores individuales de una trayectoria."""
        inicial = trayectoria.observaciones[0]
        final = trayectoria.observaciones[-1]

        distancia_total = trayectoria.calcular_distancia_total()
        desplazamiento = trayectoria.calcular_desplazamiento()
        velocidades = [v for _, _, v in self._velocidades(trayectoria, fps)]

        return {
            "x_inicial": inicial.x,
            "y_inicial": inicial.y,
            "x_final": final.x,
            "y_final": final.y,
            "tiempo_total": (final.frame - inicial.frame) / fps,
            "distancia_total": distancia_total,
            "desplazamiento": desplazamiento,
            "velocidad_media": trayectoria.calcular_velocidad_media(fps),
            "velocidad_maxima": max(velocidades),
            "eficiencia": desplazamiento / distancia_total if distancia_total > 0 else 0.0,
        }

    def _detectar_detenciones(self, trayectoria: Trayectoria, fps: float) -> list[tuple[int, int]]:
        """Tramos seguidos en que la velocidad (en 1 s) es menor al umbral."""
        detenciones = []
        inicio = None
        fin = None

        for frame_a, frame_b, velocidad in self._velocidades(trayectoria, fps):
            if velocidad < UMBRAL_DETENCION:
                if inicio is None:
                    inicio = frame_a
                fin = frame_b
            elif inicio is not None:
                detenciones.append((inicio, fin))
                inicio = None

        if inicio is not None:
            detenciones.append((inicio, fin))
        return detenciones
