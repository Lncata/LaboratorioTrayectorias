"""Etapa de comparación de experimentos."""

from statistics import StatisticsError, correlation, fmean

from models.experimento import Experimento
from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


def resumen_experimento(exp: Experimento) -> dict[str, float]:
    """Indicadores comparables de un experimento (con el nombre como prefijo)."""
    individuales = list(exp.resultados_individuales.values())
    if not individuales:
        raise ValueError(f"{exp.nombre} no tiene resultados individuales.")
    faltantes = [c for c in ("densidad_media", "flujo_medio") if c not in exp.resultados_colectivos]
    if faltantes:
        raise ValueError(f"Falta {faltantes[0]} en {exp.nombre}.")

    promedio = lambda clave: fmean(ind[clave] for ind in individuales)
    return {
        f"{exp.nombre}_cantidad_peatones": float(len(individuales)),
        f"{exp.nombre}_velocidad_media": promedio("velocidad_media"),
        f"{exp.nombre}_densidad_media": exp.resultados_colectivos["densidad_media"],
        f"{exp.nombre}_flujo_medio": exp.resultados_colectivos["flujo_medio"],
        f"{exp.nombre}_distancia_media": promedio("distancia_total"),
        f"{exp.nombre}_tiempo_medio": promedio("tiempo_total"),
    }


def correlacion_densidad_velocidad(experimentos: list[Experimento], comparacion: dict[str, float]) -> dict[str, float]:
    """Correlación de Pearson entre densidad media y velocidad media de los experimentos."""
    densidades = [comparacion[f"{e.nombre}_densidad_media"] for e in experimentos]
    velocidades = [comparacion[f"{e.nombre}_velocidad_media"] for e in experimentos]
    try:
        return {"correlacion_densidad_velocidad": correlation(densidades, velocidades)}
    except StatisticsError:  # menos de 2 experimentos o valores constantes
        return {}


class ComparacionExperimentos(EtapaPipeline[list[Experimento], ResultadoAnalisis]):
    """Compara los indicadores de varios experimentos."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline) -> ResultadoAnalisis:
        if not experimentos:
            raise ValueError("No se recibieron experimentos para comparar.")
        return ResultadoAnalisis(experimentos=experimentos, comparacion=self._comparar(experimentos))

    def _comparar(self, experimentos: list[Experimento]) -> dict[str, float]:
        comparacion = {clave: valor for exp in experimentos for clave, valor in resumen_experimento(exp).items()}
        return {**comparacion, **correlacion_densidad_velocidad(experimentos, comparacion)}
