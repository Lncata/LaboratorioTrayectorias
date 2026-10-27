"""Etapa de carga de varios experimentos.

Formato esperado (formato habitual de los datos de dinámica peatonal):

    # description: UNI_CORR_500_01
    # framerate: 25.00
    # PersID  Frame  X  Y  Z
    1   98   4.6012   1.8909   1.7600
    1   99   4.5359   1.8976   1.7600

- Las líneas que empiezan con '#' son comentarios (pueden traer metadatos).
- Las columnas van separadas por espacios, tabulaciones o comas.
- Orden de columnas: id, frame, x, y y opcionalmente z.
"""

import re
from pathlib import Path

from models.experimento import Experimento
from models.observacion import Observacion
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

EXTENSIONES_VALIDAS = (".txt", ".csv", ".dat")

# Factores para llevar cada unidad a metros.
FACTORES_A_METROS = {"m": 1.0, "cm": 0.01, "mm": 0.001}

# Busca en un comentario algo como "framerate: 25" o "fps = 16".
PATRON_FPS = re.compile(r"(?:framerate|fps)\s*[:=]?\s*([\d.]+)", re.IGNORECASE)


class CargaExperimentos(EtapaPipeline[None, list[Experimento]]):
    """Carga una colección de experimentos desde la ruta configurada."""

    def ejecutar(
        self,
        entrada: None,
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Carga los experimentos indicados por la configuración."""
        experimentos = self._cargar_experimentos(contexto.ruta_entrada, contexto)
        if not experimentos:
            raise FileNotFoundError(
                f"No se encontraron archivos de datos en '{contexto.ruta_entrada}'"
            )
        for exp in experimentos:
            print(
                f"  {exp.nombre}: {len(exp.observaciones)} observaciones, "
                f"fps={exp.fps}, unidad original={exp.unidad_original}, "
                f"líneas descartadas={exp.lineas_descartadas}"
            )
        return experimentos

    def _cargar_experimentos(
        self, ruta_entrada: Path, contexto: ContextoPipeline
    ) -> list[Experimento]:
        """Carga los experimentos disponibles en la ruta recibida."""
        return [
            self._cargar_archivo(archivo, contexto)
            for archivo in self._listar_archivos(ruta_entrada)
        ]

    # ------------------------------------------------------------------ #
    # Funciones auxiliares
    # ------------------------------------------------------------------ #

    @staticmethod
    def _listar_archivos(ruta: Path) -> list[Path]:
        """Devuelve los archivos de datos: uno solo o todos los de una carpeta."""
        if ruta.is_file():
            return [ruta]
        if ruta.is_dir():
            return sorted(
                filter(lambda p: p.suffix.lower() in EXTENSIONES_VALIDAS, ruta.iterdir())
            )
        return []

    def _cargar_archivo(self, archivo: Path, contexto: ContextoPipeline) -> Experimento:
        """Lee un archivo y lo convierte en un Experimento."""
        lineas = archivo.read_text(encoding="utf-8").splitlines()

        comentarios = [l for l in lineas if l.strip().startswith("#")]
        datos = [l for l in lineas if l.strip() and not l.strip().startswith("#")]

        # Cada línea se convierte en una tupla de números (o None si está mala).
        filas = [self._parsear_linea(l) for l in datos]
        filas_ok = [f for f in filas if f is not None]

        unidad = self._determinar_unidad(filas_ok, contexto.unidad)
        factor = FACTORES_A_METROS[unidad]

        observaciones = [self._crear_observacion(f, factor) for f in filas_ok]

        # Prioridad del fps: lo que diga el usuario > lo que diga el archivo.
        fps = contexto.fps if contexto.fps is not None else self._leer_fps(comentarios)

        return Experimento(
            nombre=archivo.stem,
            fps=fps,
            unidad_original=unidad,
            lineas_descartadas=len(filas) - len(filas_ok),
            observaciones=observaciones,
        )

    @staticmethod
    def _parsear_linea(linea: str) -> tuple[float, ...] | None:
        """Convierte una línea de texto en una tupla de números.

        Devuelve None si la línea no tiene al menos 4 valores numéricos.
        """
        valores = linea.replace(",", " ").split()
        try:
            numeros = tuple(map(float, valores))
        except ValueError:
            return None
        return numeros if len(numeros) >= 4 else None

    @staticmethod
    def _crear_observacion(fila: tuple[float, ...], factor: float) -> Observacion:
        """Crea una Observacion a partir de una fila, convirtiendo a metros."""
        id_peaton, frame, x, y, *resto = fila
        z = resto[0] * factor if resto else None
        return Observacion(
            id_peaton=int(id_peaton),
            frame=int(frame),
            x=x * factor,
            y=y * factor,
            z=z,
        )

    @staticmethod
    def _leer_fps(comentarios: list[str]) -> float | None:
        """Busca la frecuencia de muestreo en los comentarios del archivo."""
        coincidencias = (PATRON_FPS.search(c) for c in comentarios)
        return next((float(m.group(1)) for m in coincidencias if m), None)

    @staticmethod
    def _determinar_unidad(filas: list[tuple[float, ...]], unidad: str) -> str:
        """Decide la unidad de las coordenadas.

        Si el usuario la indicó (m, cm, mm) se usa esa. En modo 'auto' se
        estima: un corredor mide unos pocos metros, así que si alguna
        coordenada supera 100, los datos casi seguro están en centímetros.
        """
        if unidad != "auto":
            return unidad
        if not filas:
            return "m"
        maximo = max(max(abs(f[2]), abs(f[3])) for f in filas)
        return "cm" if maximo > 100 else "m"
