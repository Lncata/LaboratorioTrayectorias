
"""Etapa de comparación de experimentos."""

from statistics import fmean

from models.experimento import Experimento
from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class ComparacionExperimentos(
    EtapaPipeline[list[Experimento], ResultadoAnalisis]
):
    """Compara los indicadores de varios experimentos."""

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> ResultadoAnalisis:
        """Reune los experimentos y sus resultados comparativos."""

        if not experimentos:
            raise ValueError("No se recibieron experimentos para comparar.")

        comparacion = self._comparar(experimentos)

        return ResultadoAnalisis(
            experimentos=experimentos,
            comparacion=comparacion
        )

    def _comparar(
        self,
        experimentos: list[Experimento]
    ) -> dict[str, float]:
        """Calcula indicadores comparables entre experimentos."""

        comparacion = {}
        densidades = []
        velocidades = []

        for exp in experimentos:

            individuales = list(
                exp.resultados_individuales.values()
            )

            if not individuales:
                raise ValueError(
                    f"{exp.nombre} no tiene resultados individuales."
                )

            for clave in ("densidad_media", "flujo_medio"):
                if clave not in exp.resultados_colectivos:
                    raise ValueError(
                        f"Falta {clave} en {exp.nombre}."
                    )

            # Promedios individuales del experimento
            velocidad_media = fmean(
                ind["velocidad_media"] for ind in individuales
            )

            distancia_media = fmean(
                ind["distancia_total"] for ind in individuales
            )

            tiempo_medio = fmean(
                ind["tiempo_total"] for ind in individuales
            )

            # Resultados obtenidos del analisis espacial
            densidad_media = exp.resultados_colectivos[
                "densidad_media"
            ]

            flujo_medio = exp.resultados_colectivos[
                "flujo_medio"
            ]

            # Guardar los indicadores del experimento
            prefijo = exp.nombre

            comparacion[f"{prefijo}_cantidad_peatones"] = float(
                len(individuales)
            )

            comparacion[f"{prefijo}_velocidad_media"] = velocidad_media
            comparacion[f"{prefijo}_densidad_media"] = densidad_media
            comparacion[f"{prefijo}_flujo_medio"] = flujo_medio
            comparacion[f"{prefijo}_distancia_media"] = distancia_media
            comparacion[f"{prefijo}_tiempo_medio"] = tiempo_medio

            densidades.append(densidad_media)
            velocidades.append(velocidad_media)

        # Relacion entre densidad y velocidad entre experimentos
        if len(densidades) >= 2:

            media_densidades = fmean(densidades)
            media_velocidades = fmean(velocidades)

            suma_cruzada = sum(
                (d - media_densidades) * (v - media_velocidades)
                for d, v in zip(densidades, velocidades)
            )

            suma_densidades = sum(
                (d - media_densidades) ** 2
                for d in densidades
            )

            suma_velocidades = sum(
                (v - media_velocidades) ** 2
                for v in velocidades
            )

            if suma_densidades > 0 and suma_velocidades > 0:

                correlacion = suma_cruzada / (
                    suma_densidades * suma_velocidades
                ) ** 0.5

                comparacion[
                    "correlacion_densidad_velocidad"
                ] = correlacion

        return comparacion
