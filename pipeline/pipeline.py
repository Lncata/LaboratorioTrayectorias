"""Coordinación secuencial de etapas de procesamiento."""

from typing import Any

from .contexto import ContextoPipeline
from .etapa import EtapaPipeline


class Pipeline:
    """Ejecuta una colección de etapas sobre un contexto compartido."""

    def __init__(self, etapas: list[EtapaPipeline[Any, Any]]) -> None:
        self._etapas = list(etapas)

    def ejecutar(self, contexto: ContextoPipeline) -> bool:
        """Pasa cada resultado a la etapa siguiente; se detiene ante una etapa pendiente o un error de datos."""
        resultado: Any = None
        for etapa in self._etapas:
            nombre_etapa = type(etapa).__name__
            print(f"Ejecutando etapa: {nombre_etapa}")
            try:
                resultado = etapa.ejecutar(resultado, contexto)
            except NotImplementedError as error:
                detalle = str(error) or "Etapa pendiente de implementación"
                print(f"Pipeline detenido en {nombre_etapa}: {detalle}.")
                return False
            except (FileNotFoundError, ValueError, OSError) as error:
                # datos o rutas inválidos: se informa la causa en vez de mostrar un traceback
                print(f"Error en {nombre_etapa}: {error}")
                return False
        return True
