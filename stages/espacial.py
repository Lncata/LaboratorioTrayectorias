"""Etapa de análisis espacial, densidad y flujo."""

from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline
from math import hypot
from collections import defaultdict
from math import ceil

class AnalisisEspacial(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa el análisis por zonas y los cálculos de densidad y flujo."""


    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Analiza las zonas, densidad y flujo de cada experimento"""

        for experimento in experimentos:

            fps = experimento.fps

            if fps is None or fps <= 0:
                raise ValueError(
                    f"FPS invalidos para {experimento.nombre}"
                )

            # Analizar las zonas del corredor
            resultados_zonas = self._analizar_zonas(experimento)

            # Calcular densidad peatonal
            resultados_densidad = self._calcular_densidad(experimento)

            # Calcular flujo peatonal
            resultados_flujo = self._calcular_flujo(
                experimento, fps
            )

            # Reunir los resultados del experimento
            experimento.resultados_colectivos.update(
                resultados_zonas
            )

            experimento.resultados_colectivos.update(
                resultados_densidad
            )

            experimento.resultados_colectivos.update(
                resultados_flujo
            )

            print(f"\nExperimento: {experimento.nombre}")
            print(
                f"  Densidad media: "
                f"{resultados_densidad['densidad_media']:.4f}"
            )
            print(
                f"  Flujo medio: "
                f"{resultados_flujo['flujo_medio']:.4f}"
            )
            print(
                f"  Cruces totales: "
                f"{resultados_flujo['cruces_total']:.0f}"
            )

        return experimentos



    def _analizar_zonas(self, experimento: Experimento) -> dict[str, float]:
        """Calcula indicadores de movimiento por zonas del corredor"""

        fps = experimento.fps

        if fps is None or fps <= 0:
            raise ValueError("FPS invalidos para el experimento")

        # Division provisional del corredor en tres zonas
        zonas = {
            "izquierda": (-5.0, -5.0 / 3.0),
            "centro": (-5.0 / 3.0, 5.0 / 3.0),
            "derecha": (5.0 / 3.0, 5.0)
        }

        resultados = {}

        for nombre, (xmin, xmax) in zonas.items():
            peatones = set()
            distancia_total = 0.0
            tiempo_total = 0.0
            tiempos_cruce = []

            for trayectoria in experimento.trayectorias:
                observaciones = trayectoria.observaciones

                if len(observaciones) < 2:
                    continue

                # Contar peatones presentes en la zona
                if any(xmin <= obs.x < xmax for obs in observaciones):
                    peatones.add(trayectoria.id_peaton)

                # Calcular la velocidad dentro de la zona
                for actual, siguiente in zip(
                    observaciones, observaciones[1:]
                ):
                    delta_frames = siguiente.frame - actual.frame

                    if delta_frames <= 0:
                        continue

                    x_medio = (actual.x + siguiente.x) / 2

                    if xmin <= x_medio < xmax:
                        distancia = hypot(
                            siguiente.x - actual.x,
                            siguiente.y - actual.y
                        )

                        distancia_total += distancia
                        tiempo_total += delta_frames / fps

                # Determinar el sentido de movimiento
                sentido = (
                    1 if observaciones[-1].x > observaciones[0].x
                    else -1
                )

                limite_entrada = xmin if sentido > 0 else xmax
                limite_salida = xmax if sentido > 0 else xmin

                entrada = None
                salida = None

                # Detectar cuando cruza ambos limites de la zona
                for actual, siguiente in zip(
                    observaciones, observaciones[1:]
                ):
                    if sentido > 0:
                        cruza_entrada = (
                            actual.x < limite_entrada <= siguiente.x
                        )
                        cruza_salida = (
                            actual.x < limite_salida <= siguiente.x
                        )
                    else:
                        cruza_entrada = (
                            actual.x > limite_entrada >= siguiente.x
                        )
                        cruza_salida = (
                            actual.x > limite_salida >= siguiente.x
                        )

                    delta_x = siguiente.x - actual.x
                    delta_frame = siguiente.frame - actual.frame

                    if delta_x == 0 or delta_frame <= 0:
                        continue

                    if entrada is None and cruza_entrada:
                        entrada = actual.frame + delta_frame * (
                            (limite_entrada - actual.x) / delta_x
                        )

                    if entrada is not None and cruza_salida:
                        salida = actual.frame + delta_frame * (
                            (limite_salida - actual.x) / delta_x
                        )
                        break

                if entrada is not None and salida is not None:
                    if salida > entrada:
                        tiempos_cruce.append((salida - entrada) / fps)

            # Calcular los promedios de la zona
            velocidad_media = (
                distancia_total / tiempo_total
                if tiempo_total > 0 else 0.0
            )

            tiempo_medio_cruce = (
                sum(tiempos_cruce) / len(tiempos_cruce)
                if tiempos_cruce else 0.0
            )

            resultados[f"zona_{nombre}_peatones"] = float(len(peatones))
            resultados[f"zona_{nombre}_velocidad_media"] = velocidad_media
            resultados[f"zona_{nombre}_tiempo_medio_cruce"] = tiempo_medio_cruce
            resultados[f"zona_{nombre}_cruces_completos"] = float(len(tiempos_cruce))

        return resultados

  
    def _calcular_densidad(self, experimento: Experimento) -> dict[str, float]:
        """Calcula la densidad peatonal dentro de una region central."""

        if experimento.fps is None or experimento.fps <= 0:
            raise ValueError("Los FPS deben ser mayores a cero")

        # Limites de la region de medicion, en metros
        xmin, xmax = -5.0, 5.0
        ymin, ymax = 0.0, 5.0

        area = (xmax - xmin) * (ymax - ymin)

        conteos_por_frame = defaultdict(int)
        primer_frame = None
        ultimo_frame = None

        # Recorrer todas las observaciones validas
        for trayectoria in experimento.trayectorias:
            for obs in trayectoria.observaciones:

                if primer_frame is None or obs.frame < primer_frame:
                    primer_frame = obs.frame

                if ultimo_frame is None or obs.frame > ultimo_frame:
                    ultimo_frame = obs.frame

                # Contar peatones dentro del area
                if xmin <= obs.x < xmax and ymin <= obs.y < ymax:
                    conteos_por_frame[obs.frame] += 1

        if primer_frame is None:
            return {
                "densidad_media": 0.0,
                "densidad_maxima": 0.0,
                "area_medicion_m2": area,
                "frames_analizados": 0.0
            }

        acumulado = 0.0
        densidad_maxima = 0.0

        sumas_por_segundo = defaultdict(float)
        frames_por_segundo = defaultdict(int)

        # Calcular densidad para cada frame
        for frame in range(primer_frame, ultimo_frame + 1):

            cantidad = conteos_por_frame.get(frame, 0)
            densidad = cantidad / area

            acumulado += densidad
            densidad_maxima = max(densidad_maxima, densidad)

            # Agrupar mediciones en intervalos de un segundo
            segundo = int((frame - primer_frame) / experimento.fps)

            sumas_por_segundo[segundo] += densidad
            frames_por_segundo[segundo] += 1

        total_frames = ultimo_frame - primer_frame + 1

        resultados = {
            "densidad_media": acumulado / total_frames,
            "densidad_maxima": densidad_maxima,
            "area_medicion_m2": area,
            "frames_analizados": float(total_frames)
        }

        # Obtener densidad media de cada segundo
        for segundo in sorted(sumas_por_segundo):
            resultados[f"densidad_segundo_{segundo}"] = (
                sumas_por_segundo[segundo] / frames_por_segundo[segundo]
            )

        return resultados
 


    def _calcular_flujo(
        self,
        experimento: Experimento,
        fps: float | None,
    ) -> dict[str, float]:
        """Calcula el flujo peatonal a traves de la linea X=0."""

        if fps is None:
            fps = experimento.fps

        if fps is None or fps <= 0:
            raise ValueError("Los FPS deben ser mayores a cero")

        linea_x = 0.0
        cruces = []
        primer_frame = None
        ultimo_frame = None

        for trayectoria in experimento.trayectorias:

            observaciones = sorted(
                trayectoria.observaciones,
                key=lambda obs: obs.frame
            )

            if len(observaciones) < 2:
                continue

            inicio = observaciones[0].frame
            fin = observaciones[-1].frame

            primer_frame = (
                inicio if primer_frame is None
                else min(primer_frame, inicio)
            )

            ultimo_frame = (
                fin if ultimo_frame is None
                else max(ultimo_frame, fin)
            )

            # Buscar el primer cruce confirmado de cada peaton
            anterior = None

            for obs in observaciones:

                # Ignorar puntos exactamente sobre la linea
                if obs.x == linea_x:
                    continue

                if anterior is not None:

                    cruza_derecha = (
                        anterior.x < linea_x < obs.x
                    )

                    cruza_izquierda = (
                        anterior.x > linea_x > obs.x
                    )

                    if cruza_derecha or cruza_izquierda:

                        proporcion = (
                            (linea_x - anterior.x) /
                            (obs.x - anterior.x)
                        )

                        frame_cruce = (
                            anterior.frame +
                            proporcion * (obs.frame - anterior.frame)
                        )

                        sentido = (
                            "izq_der" if cruza_derecha
                            else "der_izq"
                        )

                        cruces.append((frame_cruce, sentido))
                        break

                anterior = obs

        if primer_frame is None:
            return {
                "cruces_total": 0.0,
                "flujo_medio": 0.0,
                "duracion_observada_s": 0.0,
                "cruces_izq_der": 0.0,
                "cruces_der_izq": 0.0,
                "flujo_maximo_por_segundo": 0.0
            }

        duracion = (ultimo_frame - primer_frame) / fps

        cruces_izq_der = sum(
            1 for _, sentido in cruces
            if sentido == "izq_der"
        )

        cruces_der_izq = sum(
            1 for _, sentido in cruces
            if sentido == "der_izq"
        )

        flujo_medio = (
            len(cruces) / duracion
            if duracion > 0 else 0.0
        )

        cruces_por_segundo = defaultdict(int)
        cantidad_segundos = max(1, ceil(duracion))

        for frame_cruce, _ in cruces:

            segundo = int(
                (frame_cruce - primer_frame) / fps
            )

            segundo = min(segundo, cantidad_segundos - 1)

            cruces_por_segundo[segundo] += 1

        resultados = {
            "cruces_total": float(len(cruces)),
            "flujo_medio": flujo_medio,
            "duracion_observada_s": duracion,
            "cruces_izq_der": float(cruces_izq_der),
            "cruces_der_izq": float(cruces_der_izq),
            "flujo_maximo_por_segundo": float(
                max(cruces_por_segundo.values(), default=0)
            )
        }

        for segundo in range(cantidad_segundos):
            resultados[f"flujo_segundo_{segundo}"] = float(
                cruces_por_segundo.get(segundo, 0)
            )

        return resultados
