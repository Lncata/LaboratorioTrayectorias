"""Modelo básico de una observación peatonal."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Observacion:
    """Posición de un peatón en un frame. Coordenadas en metros (inmutable)."""

    id_peaton: int
    frame: int
    x: float
    y: float
    z: float | None = None  # algunos archivos no traen altura
