"""Funciones puras para el análisis espacial: zonas, densidad y flujo.

Reciben listas de `Trayectoria` (observaciones ordenadas por frame) y la
frecuencia de muestreo; devuelven diccionarios nuevos sin modificar nada.
"""

from __future__ import annotations

from collections import Counter
from itertools import groupby
from math import ceil, hypot
from typing import TYPE_CHECKING, Optional, Sequence

from funciones.movimiento import suma_secuencial

if TYPE_CHECKING:  # solo para anotar tipos: evita un ciclo de imports con models/
    from models.observacion import Observacion
    from models.trayectoria import Trayectoria

# Región de medición (m): x entre -5 y 5, y entre 0 y 5 -> 50 m²
AREA = (-5.0, 5.0, 0.0, 5.0)
LINEA_FLUJO_X = 0.0
# Zonas de igual largo (3.33 m) dentro de x en [-5, 5]
ZONAS = (
    ("izquierda", -5.0, -5.0 / 3.0),
    ("centro", -5.0 / 3.0, 5.0 / 3.0),
    ("derecha", 5.0 / 3.0, 5.0),
)


def _listas_validas(trayectorias: Sequence[Trayectoria]) -> list[list[Observacion]]:
    """Observaciones de las trayectorias con al menos dos puntos."""
    return [t.observaciones for t in trayectorias if len(t.observaciones) >= 2]


# ---------------------------------------------------------------- zonas

def tiempo_cruce(obs: Sequence[Observacion], fps: float, xmin: float, xmax: float) -> Optional[float]:
    """Segundos que tarda un peatón en cruzar la zona [xmin, xmax); None si no la cruza completa."""
    sentido = 1 if obs[-1].x > obs[0].x else -1
    limite_entrada, limite_salida = (xmin, xmax) if sentido > 0 else (xmax, xmin)

    def cruza(a: Observacion, b: Observacion, limite: float) -> bool:
        return a.x < limite <= b.x if sentido > 0 else a.x > limite >= b.x

    def instante(a: Observacion, b: Observacion, limite: float) -> float:
        return a.frame + (b.frame - a.frame) * ((limite - a.x) / (b.x - a.x))

    pasos = [(a, b) for a, b in zip(obs, obs[1:]) if b.x != a.x and b.frame > a.frame]
    i_entrada = next((i for i, (a, b) in enumerate(pasos) if cruza(a, b, limite_entrada)), None)
    if i_entrada is None:
        return None
    paso_salida = next(((a, b) for a, b in pasos[i_entrada:] if cruza(a, b, limite_salida)), None)
    if paso_salida is None:
        return None

    t_entrada = instante(*pasos[i_entrada], limite_entrada)
    t_salida = instante(*paso_salida, limite_salida)
    return (t_salida - t_entrada) / fps if t_salida > t_entrada else None


def indicadores_zona(
    trayectorias: Sequence[Trayectoria], fps: float, nombre: str, xmin: float, xmax: float
) -> dict[str, float]:
    """Peatones presentes, velocidad media y tiempo medio de cruce de una zona."""
    listas = _listas_validas(trayectorias)

    presentes = sum(1 for obs in listas if any(xmin <= o.x < xmax for o in obs))

    # pasos entre observaciones consecutivas cuyo punto medio cae en la zona
    pasos = [
        (a, b)
        for obs in listas
        for a, b in zip(obs, obs[1:])
        if b.frame - a.frame > 0 and xmin <= (a.x + b.x) / 2 < xmax
    ]
    distancia = suma_secuencial(hypot(b.x - a.x, b.y - a.y) for a, b in pasos)
    tiempo = suma_secuencial((b.frame - a.frame) / fps for a, b in pasos)

    tiempos = [t for t in (tiempo_cruce(obs, fps, xmin, xmax) for obs in listas) if t is not None]

    return {
        f"zona_{nombre}_peatones": float(presentes),
        f"zona_{nombre}_velocidad_media": distancia / tiempo if tiempo > 0 else 0.0,
        f"zona_{nombre}_tiempo_medio_cruce": sum(tiempos) / len(tiempos) if tiempos else 0.0,
        f"zona_{nombre}_cruces_completos": float(len(tiempos)),
    }


# -------------------------------------------------------------- densidad

def _media(valores: Sequence[float]) -> float:
    return suma_secuencial(valores) / len(valores)


def densidad(trayectorias: Sequence[Trayectoria], fps: float, area: tuple = AREA) -> dict[str, float]:
    """Densidad (personas/m²) por frame dentro del área: media, máxima y media por segundo."""
    xmin, xmax, ymin, ymax = area
    superficie = (xmax - xmin) * (ymax - ymin)
    observaciones = [o for t in trayectorias for o in t.observaciones]

    if not observaciones:
        return {"densidad_media": 0.0, "densidad_maxima": 0.0,
                "area_medicion_m2": superficie, "frames_analizados": 0.0}

    primer = min(o.frame for o in observaciones)
    ultimo = max(o.frame for o in observaciones)
    conteos = Counter(o.frame for o in observaciones if xmin <= o.x < xmax and ymin <= o.y < ymax)
    densidades = [conteos.get(frame, 0) / superficie for frame in range(primer, ultimo + 1)]

    # el segundo de cada frame crece con el índice, así que groupby agrupa sin ordenar
    por_segundo = {
        segundo: _media([d for _, d in grupo])
        for segundo, grupo in groupby(enumerate(densidades), key=lambda par: int(par[0] / fps))
    }

    return {
        "densidad_media": suma_secuencial(densidades) / len(densidades),
        "densidad_maxima": max(densidades),
        "area_medicion_m2": superficie,
        "frames_analizados": float(len(densidades)),
        **{f"densidad_segundo_{s}": d for s, d in por_segundo.items()},
    }


# ------------------------------------------------------------------ flujo

def primer_cruce(obs: Sequence[Observacion], linea: float) -> Optional[tuple[float, str]]:
    """(frame interpolado, sentido) del primer cruce de x = linea; None si nunca la cruza."""
    fuera_de_linea = [o for o in obs if o.x != linea]  # los puntos sobre la línea se ignoran
    par = next(
        ((a, b) for a, b in zip(fuera_de_linea, fuera_de_linea[1:])
         if a.x < linea < b.x or a.x > linea > b.x),
        None,
    )
    if par is None:
        return None
    a, b = par
    frame = a.frame + ((linea - a.x) / (b.x - a.x)) * (b.frame - a.frame)
    return frame, "izq_der" if a.x < linea else "der_izq"


def flujo(trayectorias: Sequence[Trayectoria], fps: float, linea: float = LINEA_FLUJO_X) -> dict[str, float]:
    """Flujo J = N / Δt a través de la línea x = linea, total y por segundo."""
    listas = [sorted(obs, key=lambda o: o.frame) for obs in _listas_validas(trayectorias)]

    if not listas:
        return {"cruces_total": 0.0, "flujo_medio": 0.0, "duracion_observada_s": 0.0,
                "cruces_izq_der": 0.0, "cruces_der_izq": 0.0, "flujo_maximo_por_segundo": 0.0}

    primer = min(obs[0].frame for obs in listas)
    ultimo = max(obs[-1].frame for obs in listas)
    duracion = (ultimo - primer) / fps

    cruces = [c for c in (primer_cruce(obs, linea) for obs in listas) if c is not None]
    cantidad_segundos = max(1, ceil(duracion))
    por_segundo = Counter(min(int((frame - primer) / fps), cantidad_segundos - 1) for frame, _ in cruces)

    return {
        "cruces_total": float(len(cruces)),
        "flujo_medio": len(cruces) / duracion if duracion > 0 else 0.0,
        "duracion_observada_s": duracion,
        "cruces_izq_der": float(sum(1 for _, sentido in cruces if sentido == "izq_der")),
        "cruces_der_izq": float(sum(1 for _, sentido in cruces if sentido == "der_izq")),
        "flujo_maximo_por_segundo": float(max(por_segundo.values(), default=0)),
        **{f"flujo_segundo_{s}": float(por_segundo.get(s, 0)) for s in range(cantidad_segundos)},
    }
