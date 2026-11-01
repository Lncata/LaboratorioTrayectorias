"""Configuración de una ejecución del pipeline."""

from dataclasses import dataclass
from pathlib import Path

from funciones.movimiento import UMBRAL_DETENCION


@dataclass(frozen=True)
class ContextoPipeline:
    """Contiene únicamente las opciones de ejecución del programa."""

    ruta_entrada: Path
    ruta_salida: Path
    fps: float | None = None
    unidad: str = "m"  # "m" o "cm"
    umbral_detencion: float = UMBRAL_DETENCION  # m/s
