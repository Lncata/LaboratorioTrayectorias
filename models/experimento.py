"""Entidad que agrupa los datos y resultados de un experimento."""

from dataclasses import dataclass, field

from .observacion import Observacion
from .trayectoria import Trayectoria


@dataclass(frozen=True)
class Experimento:
    """Un archivo de datos: sus observaciones, trayectorias y resultados.

    Es inmutable: cada etapa del pipeline devuelve una copia nueva
    (`dataclasses.replace`) con los campos que calculó.
    """

    nombre: str
    fps: float | None = None
    lineas_descartadas: int = 0
    observaciones: list[Observacion] = field(default_factory=list)
    trayectorias: list[Trayectoria] = field(default_factory=list)
    resultados_individuales: dict[int, dict[str, float]] = field(default_factory=dict)
    resultados_colectivos: dict[str, float] = field(default_factory=dict)
