"""Etapa 1: carga de los archivos de datos.

Cada archivo .txt es un experimento. Formato de cada archivo:

    # framerate: 25.00
    # PersID  Frame  X  Y  Z
    1   98   4.6012   1.8909   1.7600

Las líneas que empiezan con '#' son comentarios.
Las columnas son: id del peatón, frame, x, y, z (z es opcional).
"""

from models.experimento import Experimento
from models.observacion import Observacion
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class CargaExperimentos(EtapaPipeline[None, list[Experimento]]):
    """Lee los archivos de entrada y crea un Experimento por archivo."""

    def ejecutar(self, entrada: None, contexto: ContextoPipeline) -> list[Experimento]:
        ruta = contexto.ruta_entrada

        # La entrada puede ser un archivo o una carpeta con varios .txt
        if ruta.is_file():
            archivos = [ruta]
        else:
            archivos = sorted(ruta.glob("*.txt"))

        if len(archivos) == 0:
            raise FileNotFoundError(f"No hay archivos .txt en '{ruta}'")

        experimentos = [self._leer_archivo(archivo, contexto) for archivo in archivos]

        for exp in experimentos:
            print(f"  {exp.nombre}: {len(exp.observaciones)} observaciones, "
                  f"fps={exp.fps}, líneas descartadas={exp.lineas_descartadas}")
        return experimentos

    def _leer_archivo(self, archivo, contexto: ContextoPipeline) -> Experimento:
        """Lee un archivo línea por línea y devuelve un Experimento."""
        fps = contexto.fps          # si el usuario dio --fps, se usa ese
        factor = 0.01 if contexto.unidad == "cm" else 1.0   # para pasar a metros
        observaciones = []
        descartadas = 0

        with open(archivo, encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()

                if linea == "":
                    continue

                # Comentario: si trae el framerate y no nos dieron --fps, lo guardamos
                if linea.startswith("#"):
                    if "framerate" in linea and fps is None:
                        fps = float(linea.split(":", 1)[1].strip().split()[0])
                    continue

                partes = linea.split()
                try:
                    obs = Observacion(
                        id_peaton=int(partes[0]),
                        frame=int(float(partes[1])),
                        x=float(partes[2]) * factor,
                        y=float(partes[3]) * factor,
                        z=float(partes[4]) * factor if len(partes) > 4 else None,
                    )
                except (ValueError, IndexError):
                    # línea con texto en vez de números o con columnas faltantes
                    descartadas += 1
                    continue

                observaciones.append(obs)

        return Experimento(
            nombre=archivo.stem,
            fps=fps,
            lineas_descartadas=descartadas,
            observaciones=observaciones,
        )
