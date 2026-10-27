"""Modelo básico de una observación peatonal."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Observacion:
    """Representa la posición registrada de un peatón en un cuadro.

    Es inmutable (frozen=True): una observación es un dato medido y no
    debería cambiar después de ser leída. Las coordenadas se guardan
    siempre en metros (la conversión se hace al cargar).
    """

    id_peaton: int
    frame: int
    x: float
    y: float
    z: float | None = None  # algunos archivos no traen altura

    @property
    def posicion(self) -> tuple[float, float]:
        """Posición en el plano como tupla (x, y)."""
        return (self.x, self.y)
