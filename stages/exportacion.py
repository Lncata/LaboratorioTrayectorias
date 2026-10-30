"""Etapa de exportación de resultados."""

import csv
import json
from pathlib import Path

from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

ZONAS = ["izquierda", "centro", "derecha"]
METRICAS_ZONA = ["peatones", "velocidad_media", "tiempo_medio_cruce", "cruces_completos"]
METRICAS_EXPERIMENTO = [
    "cantidad_peatones",
    "velocidad_media",
    "densidad_media",
    "flujo_medio",
    "distancia_media",
    "tiempo_medio",
]


class ExportacionResultados(EtapaPipeline[ResultadoAnalisis, None]):
    """Guarda los resultados en archivos CSV y JSON."""

    def ejecutar(self, resultados: ResultadoAnalisis, contexto: ContextoPipeline) -> None:
        ruta = contexto.ruta_salida
        ruta.mkdir(parents=True, exist_ok=True)
        self._exportar(resultados, ruta)
        print(f"  Resultados guardados en '{ruta}'")

    def _exportar(self, resultados: ResultadoAnalisis, ruta: Path) -> None:
        experimentos = resultados.experimentos
        comparacion = resultados.comparacion

        individuales = [
            {"experimento": exp.nombre, "id_peaton": id_peaton, **indicadores}
            for exp in experimentos
            for id_peaton, indicadores in exp.resultados_individuales.items()
        ]

        zonas = [
            {"experimento": exp.nombre, "zona": zona,
             **{m: exp.resultados_colectivos[f"zona_{zona}_{m}"] for m in METRICAS_ZONA}}
            for exp in experimentos
            for zona in ZONAS
        ]

        series = []
        for exp in experimentos:
            colectivos = exp.resultados_colectivos
            segundo = 0
            while f"densidad_segundo_{segundo}" in colectivos:
                series.append({
                    "experimento": exp.nombre,
                    "segundo": segundo,
                    "densidad": colectivos[f"densidad_segundo_{segundo}"],
                    "flujo": colectivos.get(f"flujo_segundo_{segundo}", 0.0),
                })
                segundo += 1

        resumen = [
            {"experimento": exp.nombre, "fps": exp.fps,
             **{m: comparacion[f"{exp.nombre}_{m}"] for m in METRICAS_EXPERIMENTO}}
            for exp in experimentos
        ]

        self._guardar_csv(ruta / "individual.csv", individuales)
        self._guardar_csv(ruta / "zonas.csv", zonas)
        self._guardar_csv(ruta / "densidad_flujo.csv", series)
        self._guardar_csv(ruta / "experimentos.csv", resumen)

        correlacion = comparacion.get("correlacion_densidad_velocidad")
        resumen_json = {
            "experimentos": [self._redondear(fila) for fila in resumen],
            "correlacion_densidad_velocidad": round(correlacion, 4) if correlacion is not None else None,
        }
        with open(ruta / "resumen.json", "w", encoding="utf-8") as f:
            json.dump(resumen_json, f, indent=2, ensure_ascii=False)

    def _guardar_csv(self, archivo: Path, filas: list[dict]) -> None:
        with open(archivo, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
            escritor.writeheader()
            for fila in filas:
                escritor.writerow(self._redondear(fila))

    def _redondear(self, fila: dict) -> dict:
        return {k: round(v, 4) if isinstance(v, float) else v for k, v in fila.items()}
