"""Funciones puras para los indicadores de una trayectoria individual.

Todas reciben secuencias de `Observacion` ordenadas por frame y devuelven
valores nuevos; ninguna modifica sus argumentos.
"""

from __future__ import annotations

from functools import reduce
from math import hypot, sqrt
from operator import add
from typing import TYPE_CHECKING, Iterable, Iterator, Sequence

if TYPE_CHECKING:  # solo para anotar tipos: evita un ciclo de imports con models/
    from models.observacion import Observacion

UMBRAL_DETENCION = 0.1  # m/s: por debajo de este valor (ventana de 1 s) se considera detenido

Ventana = tuple[int, int, float]  # (frame_inicio, frame_fin, velocidad en m/s)


def suma_secuencial(valores) -> float:
    """Suma de izquierda a derecha, sin compensación.

    `sum()` de Python 3.12+ compensa errores de redondeo en floats; aquí se usa
    `reduce(add)` para reproducir exactamente la acumulación con `+=` del pipeline original.
    """
    return reduce(add, valores, 0.0)


def exigir_fps_positivo(fps: float) -> None:
    """Los FPS deben ser mayores que 0 para convertir frames en segundos."""
    if fps is None or fps <= 0:
        raise ValueError("Los FPS deben ser mayores a 0.")


def por_frame(observaciones: Sequence[Observacion]) -> list[Observacion]:
    """Copia ordenada temporalmente de las observaciones."""
    return sorted(observaciones, key=lambda obs: obs.frame)


def distancia(a: Observacion, b: Observacion) -> float:
    """Distancia euclidiana en el plano entre dos observaciones."""
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def distancia_total(obs: Sequence[Observacion]) -> float:
    """Suma de las distancias entre observaciones consecutivas."""
    return suma_secuencial(map(distancia, obs, obs[1:]))


def desplazamiento(obs: Sequence[Observacion]) -> float:
    """Distancia directa entre la primera y la última observación."""
    return distancia(obs[0], obs[-1]) if len(obs) >= 2 else 0.0


def tiempo_total(obs: Sequence[Observacion], fps: float) -> float:
    """Segundos entre la primera y la última observación."""
    return (obs[-1].frame - obs[0].frame) / fps


def ventanas_de_un_segundo(obs: Sequence[Observacion], fps: float) -> list[Ventana]:
    """Velocidad entre posiciones separadas por 1 s (reduce el ruido del seguimiento)."""
    paso = min(int(fps), len(obs) - 1)
    return [
        (a.frame, b.frame, hypot(b.x - a.x, b.y - a.y) / ((b.frame - a.frame) / fps))
        for a, b in zip(obs, obs[paso:])
    ]


def fusionar_intervalos(intervalos: Iterable[tuple[int, int]]) -> Iterator[tuple[int, int]]:
    """Une intervalos (inicio, fin), ordenados por inicio, que se superponen o se tocan."""
    actual: tuple[int, int] | None = None
    for inicio, fin in intervalos:
        if actual is not None and inicio <= actual[1]:
            actual = (actual[0], max(actual[1], fin))
        else:
            if actual is not None:
                yield actual
            actual = (inicio, fin)
    if actual is not None:
        yield actual


def detectar_detenciones(ventanas: Sequence[Ventana], umbral: float = UMBRAL_DETENCION) -> list[tuple[int, int]]:
    """Detenciones como intervalos (frame_inicio, frame_fin).

    Cada ventana de 1 s con velocidad menor al umbral es un intervalo detenido. Como las
    ventanas se solapan, los intervalos superpuestos se fusionan: así un mismo tramo no se
    cuenta dos veces y el tiempo detenido nunca supera el tiempo total.
    """
    lentas = ((inicio, fin) for inicio, fin, velocidad in ventanas if velocidad < umbral and fin > inicio)
    return list(fusionar_intervalos(lentas))
