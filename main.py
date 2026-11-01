"""Punto de entrada"""

import argparse
from pathlib import Path
from typing import Sequence

from funciones.movimiento import UMBRAL_DETENCION
from pipeline.contexto import ContextoPipeline
from pipeline.pipeline import Pipeline
from stages import (
    AnalisisEspacial,
    AnalisisIndividual,
    CargaExperimentos,
    ComparacionExperimentos,
    ExportacionResultados,
    PreparacionTrayectorias,
)


def numero_positivo(texto: str) -> float:
    """Convierte el argumento a número y exige que sea mayor que cero."""
    try:
        valor = float(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{texto}' no es un número")
    if valor <= 0:
        raise argparse.ArgumentTypeError(f"debe ser mayor que 0 (recibido: {texto})")
    return valor


def crear_parser() -> argparse.ArgumentParser:
    """Crea el analizador de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Pipeline inicial: Análisis de Trayectorias Peatonales."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("./data"),
        help="Archivo o directorio de entrada (por defecto: ./data).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./results"),
        help="Directorio de salida (por defecto: ./results).",
    )
    parser.add_argument(
        "--fps",
        type=numero_positivo,
        default=None,
        help="Frecuencia de muestreo del experimento, en cuadros por segundo. "
        "Si no se indica, se lee del encabezado de cada archivo.",
    )
    parser.add_argument(
        "--unidad",
        choices=["m", "cm"],
        default="m",
        help="Unidad de las coordenadas en los archivos (por defecto: m).",
    )
    parser.add_argument(
        "--umbral-detencion",
        type=numero_positivo,
        default=UMBRAL_DETENCION,
        help="Velocidad (m/s) bajo la cual un peatón se considera detenido "
        f"(por defecto: {UMBRAL_DETENCION}).",
    )
    return parser


def main(argumentos: Sequence[str] | None = None) -> int:
    """Configura y ejecuta las etapas del pipeline."""
    configuracion = crear_parser().parse_args(argumentos)
    contexto = ContextoPipeline(
        ruta_entrada=configuracion.input,
        ruta_salida=configuracion.output,
        fps=configuracion.fps,
        unidad=configuracion.unidad,
        umbral_detencion=configuracion.umbral_detencion,
    )
    etapas = [
        CargaExperimentos(),        # 1. archivos -> list[Experimento]
        PreparacionTrayectorias(),  # 2. validar, agrupar y ordenar
        AnalisisIndividual(),       # 3. métricas por peatón
        AnalisisEspacial(),         # 4. zonas, densidad y flujo
        ComparacionExperimentos(),  # 5. list[Experimento] -> ResultadoAnalisis
        ExportacionResultados(),    # 6. guardar archivos
    ]
    pipeline = Pipeline(etapas)

    print("Configuración seleccionada:")
    print(f"  Entrada: {contexto.ruta_entrada}")
    print(f"  Salida: {contexto.ruta_salida}")
    frecuencia = str(contexto.fps) if contexto.fps is not None else "no especificada"
    print(f"  Frecuencia (fps): {frecuencia}")
    print(f"  Umbral de detención: {contexto.umbral_detencion} m/s")

    if not contexto.ruta_entrada.exists():
        print(f"Error: la ruta de entrada '{contexto.ruta_entrada}' no existe.")
        return 1

    return 0 if pipeline.ejecutar(contexto) else 1


if __name__ == "__main__":
    raise SystemExit(main())
