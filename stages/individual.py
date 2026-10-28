"""Etapa de análisis individual de los experimentos."""

from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline
from math import hypot

class AnalisisIndividual(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Coordina el análisis de múltiples trayectorias y reúne sus indicadores."""

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Analiza las trayectorias de cada experimento."""
        raise NotImplementedError("Etapa pendiente de implementación")

    def _calcular_indicadores(
        self,
        trayectoria: Trayectoria,
        fps: float | None,
    ) -> dict[str, float]:
        """Calcula los indicadores individuales de una trayectoria."""

        if fps is None or fps <= 0:
            raise ValueError("Los FPS deben ser mayores a cero")

        observaciones = sorted(trayectoria.observaciones, key=lambda obs: obs.frame)

        if not observaciones:
            raise ValueError("La trayectoria no tiene observaciones")

        inicial = observaciones[0]
        final = observaciones[-1]

        # calcular indicadores usando clase Trayectoria
        distancia_total = trayectoria.calcular_distancia_total()
        desplazamiento = trayectoria.calcular_desplazamiento()
        velocidad_media = trayectoria.calcular_velocidad_media(fps)

        # calcular tiempo total
        tiempo_total = (final.frame - inicial.frame) / fps

        # calcular velocidad maxima
        velocidad_maxima = 0.0

        for i in range(len(observaciones) -1):
            actual = observaciones[i]
            siguiente = observaciones[i + 1]

            delta_frames = siguiente.frame - actual.frame

            if delta_frames <= 0:
                raise ValueError("Hay frames repetidos o invalidos")

            delta_t = delta_frames / fps

            distancia = hypot(siguiente.x - actual.x, siguiente.y - actual.y)

            velocidad = distancia / delta_t
            velocidad_maxima = max(velocidad_maxima, velocidad)

        # calcular eficiencia de la trayectoria 
        eficiencia = (desplazamiento / distancia_total if distancia_total > 0 else 0.0)

        return {
            "x_inicial": float(inicial.x),
            "y_inicial": float(inicial.y),
            "x_final": float(final.x),
            "y_final": float(final.y),
            "tiempo_total": tiempo_total,
            "distancia_total": distancia_total,
            "desplazamiento": desplazamiento,
            "velocidad_media": velocidad_media,
            "velocidad_maxima": velocidad_maxima,
            "eficiencia": eficiencia
        }
    
    def _detectar_detenciones(
        self,
        trayectoria: Trayectoria,
        fps: float | None,
    ) -> list[tuple[int, int]]:
        """Identifica intervalos de detención de una trayectoria."""

        if fps is None or fps <= 0:
            raise ValueError("Los FPS deben ser mayores a cero")

        observaciones = sorted(trayectoria.observaciones, key=lambda obs: obs.frame)

        if len(observaciones) < 2:
            return []

        umbral_velocidad = 0.1
        detenciones = []
        inicio_detencion = None 
        fin_detencion = None

        for i in range(len(observaciones)- 1):
            actual = observaciones[i]
            siguiente = observaciones[i + 1]

            delta_frames = siguiente.frame - actual.frame

            if delta_frames <= 0:
                raise ValueError("Hay frames repetidos o invalidos")

            delta_t = delta_frames / fps 

            distancia = hypot(siguiente.x - actual.x, siguiente.y - actual.y)

            velocidad = distancia / delta_t

            if velocidad < umbral_velocidad :
                if inicio_detencion is None :
                    inicio_detencion = actual.frame

                fin_detencion = siguiente.frame

            elif inicio_detencion is not None:
                detenciones.append((inicio_detencion, fin_detencion))

                inicio_detencion = None
                fin_detencion = None

        if inicio_detencion is not None:
            detenciones.append((inicio_detencion, fin_detencion))

        return detenciones

        
