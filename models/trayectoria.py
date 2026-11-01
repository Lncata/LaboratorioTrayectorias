"""Modelo básico de una trayectoria peatonal."""

from dataclasses import dataclass, field

from funciones.movimiento import (
    UMBRAL_DETENCION,
    desplazamiento,
    detectar_detenciones,
    exigir_fps_positivo,
    distancia_total,
    por_frame,
    tiempo_total,
    ventanas_de_un_segundo,
)

from .observacion import Observacion


@dataclass
class Trayectoria:
    """Observaciones de un peatón y los cálculos propios de su recorrido.

    Cada método ordena las observaciones por frame y delega el cálculo en
    funciones puras (`funciones.movimiento`); la trayectoria no se modifica.
    """

    id_peaton: int
    observaciones: list[Observacion] = field(default_factory=list)

    def calcular_distancia_total(self) -> float:
        """Distancia total recorrida por el peatón."""
        return distancia_total(por_frame(self.observaciones))

    def calcular_desplazamiento(self) -> float:
        """Distancia directa entre la posición inicial y la final."""
        return desplazamiento(por_frame(self.observaciones))

    def calcular_velocidad_media(self, fps: float) -> float:
        """Velocidad media (distancia total / tiempo total) según la frecuencia del experimento."""
        exigir_fps_positivo(fps)
        if len(self.observaciones) < 2:
            return 0.0
        tiempo = tiempo_total(por_frame(self.observaciones), fps)
        return self.calcular_distancia_total() / tiempo if tiempo > 0 else 0.0

    def calcular_indicadores(self, fps: float, umbral_detencion: float = UMBRAL_DETENCION) -> dict[str, float]:
        """Todos los indicadores individuales: recorrido, velocidades, eficiencia y detenciones."""
        exigir_fps_positivo(fps)
        obs = por_frame(self.observaciones)
        ventanas = ventanas_de_un_segundo(obs, fps)
        detenciones = detectar_detenciones(ventanas, umbral_detencion)

        distancia = self.calcular_distancia_total()
        despl = self.calcular_desplazamiento()
        tiempo = tiempo_total(obs, fps)
        t_detenido = sum((fin - inicio) / fps for inicio, fin in detenciones)

        return {
            "x_inicial": obs[0].x,
            "y_inicial": obs[0].y,
            "x_final": obs[-1].x,
            "y_final": obs[-1].y,
            "tiempo_total": tiempo,
            "distancia_total": distancia,
            "desplazamiento": despl,
            "velocidad_media": self.calcular_velocidad_media(fps),
            "velocidad_maxima": max(v for _, _, v in ventanas),
            "eficiencia": despl / distancia if distancia > 0 else 0.0,
            "cantidad_detenciones": len(detenciones),
            "tiempo_detenido": t_detenido,
            "porcentaje_detenido": 100 * t_detenido / tiempo if tiempo > 0 else 0.0,
        }
