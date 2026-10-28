"""Modelo básico de una trayectoria peatonal."""

from dataclasses import dataclass, field

from .observacion import Observacion

from math import sqrt

@dataclass
class Trayectoria:
    """Representa las observaciones y cálculos propios de un peatón."""

    id_peaton: int
    observaciones: list[Observacion] = field(default_factory=list)

    def calcular_distancia_total(self) -> float:
        """Calcula la distancia total recorrida por el peatón."""

        observaciones = sorted(self.observaciones, key=lambda obs: obs.frame)
        distancia_total = 0.0

        for i in range(len(observaciones)- 1):
            actual = observaciones[i]
            siguiente = observaciones[i + 1]

            dx = siguiente.x - actual.x
            dy = siguiente.y - actual.y

            distancia = sqrt(dx**2 + dy**2)
            distancia_total += distancia

        return distancia_total

    def calcular_desplazamiento(self) -> float:
        """Calcula el desplazamiento entre el inicio y el final."""

        if len(self.observaciones) < 2:
            return 0.0

        observaciones = sorted(self.observaciones, key=lambda obs: obs.frame)

        inicial = observaciones[0]
        final = observaciones[-1]

        dx = final.x - inicial.x
        dy = final.y - inicial.y

        desplazamiento = sqrt(dx**2 + dy**2)

        return desplazamiento

    def calcular_velocidad_media(self, fps: float) -> float:
        """Calcula la velocidad media usando la frecuencia del experimento."""

        if fps <= 0:
            raise ValueError("Los FPS deben ser mayores a 0.")

        if len(self.observaciones) < 2:
            return 0.0

        observaciones = sorted(self.observaciones, key=lambda obs: obs.frame)

        frame_inicial = observaciones[0].frame
        frame_final = observaciones[-1].frame

        tiempo_total = (frame_final - frame_inicial) / fps

        if tiempo_total <= 0:
            return 0.0

        distancia_total = self.calcular_distancia_total() 

        velocidad_media = distancia_total / tiempo_total

        return velocidad_media       
