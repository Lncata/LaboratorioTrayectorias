"""Genera los gráficos del informe a partir de los archivos de results/."""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def leer_csv(archivo: Path) -> list[dict]:
    with open(archivo, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def nombre_corto(experimento: str) -> str:
    return experimento.split("_")[-1]


def velocidad_vs_densidad(experimentos: list[dict], salida: Path) -> None:
    densidades = [float(e["densidad_media"]) for e in experimentos]
    velocidades = [float(e["velocidad_media"]) for e in experimentos]

    plt.figure(figsize=(7, 5))
    plt.scatter(densidades, velocidades)
    for e, d, v in zip(experimentos, densidades, velocidades):
        plt.annotate(nombre_corto(e["experimento"]), (d, v), textcoords="offset points", xytext=(5, 5))
    plt.xlabel("Densidad media (personas/m²)")
    plt.ylabel("Velocidad media (m/s)")
    plt.title("Velocidad media vs densidad por experimento")
    plt.grid(alpha=0.3)
    plt.savefig(salida / "velocidad_vs_densidad.png", dpi=150, bbox_inches="tight")
    plt.close()


def flujo_vs_densidad(experimentos: list[dict], salida: Path) -> None:
    densidades = [float(e["densidad_media"]) for e in experimentos]
    flujos = [float(e["flujo_medio"]) for e in experimentos]

    plt.figure(figsize=(7, 5))
    plt.scatter(densidades, flujos, color="tab:orange")
    for e, d, j in zip(experimentos, densidades, flujos):
        plt.annotate(nombre_corto(e["experimento"]), (d, j), textcoords="offset points", xytext=(5, 5))
    plt.xlabel("Densidad media (personas/m²)")
    plt.ylabel("Flujo medio (personas/s)")
    plt.title("Flujo vs densidad por experimento")
    plt.grid(alpha=0.3)
    plt.savefig(salida / "flujo_vs_densidad.png", dpi=150, bbox_inches="tight")
    plt.close()


def densidad_en_el_tiempo(series: list[dict], salida: Path) -> None:
    por_experimento = {}
    for fila in series:
        if fila["experimento"] not in por_experimento:
            por_experimento[fila["experimento"]] = ([], [])
        por_experimento[fila["experimento"]][0].append(int(fila["segundo"]))
        por_experimento[fila["experimento"]][1].append(float(fila["densidad"]))

    plt.figure(figsize=(10, 5))
    for experimento, (segundos, densidades) in por_experimento.items():
        plt.plot(segundos, densidades, label=nombre_corto(experimento))
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Densidad (personas/m²)")
    plt.title("Densidad en el área de medición a lo largo del tiempo")
    plt.legend(title="Experimento", ncol=3)
    plt.grid(alpha=0.3)
    plt.savefig(salida / "densidad_en_el_tiempo.png", dpi=150, bbox_inches="tight")
    plt.close()


def velocidad_por_zona(zonas: list[dict], salida: Path) -> None:
    experimentos = sorted({z["experimento"] for z in zonas})
    nombres_zona = ["izquierda", "centro", "derecha"]
    ancho = 0.25

    plt.figure(figsize=(10, 5))
    for i, zona in enumerate(nombres_zona):
        velocidades = [
            float(z["velocidad_media"])
            for e in experimentos
            for z in zonas
            if z["experimento"] == e and z["zona"] == zona
        ]
        posiciones = [j + (i - 1) * ancho for j in range(len(experimentos))]
        plt.bar(posiciones, velocidades, width=ancho, label=zona)
    plt.xticks(range(len(experimentos)), [nombre_corto(e) for e in experimentos])
    plt.xlabel("Experimento")
    plt.ylabel("Velocidad media en la zona (m/s)")
    plt.title("Velocidad media por zona del corredor")
    plt.legend(title="Zona")
    plt.grid(axis="y", alpha=0.3)
    plt.savefig(salida / "velocidad_por_zona.png", dpi=150, bbox_inches="tight")
    plt.close()


def velocidades_individuales(individuales: list[dict], salida: Path) -> None:
    experimentos = sorted({fila["experimento"] for fila in individuales})
    datos = [
        [float(fila["velocidad_media"]) for fila in individuales if fila["experimento"] == e]
        for e in experimentos
    ]

    plt.figure(figsize=(10, 5))
    plt.boxplot(datos, showfliers=False)
    plt.xticks(range(1, len(experimentos) + 1), [nombre_corto(e) for e in experimentos])
    plt.xlabel("Experimento")
    plt.ylabel("Velocidad media del peatón (m/s)")
    plt.title("Distribución de la velocidad media de los peatones")
    plt.grid(axis="y", alpha=0.3)
    plt.savefig(salida / "velocidades_individuales.png", dpi=150, bbox_inches="tight")
    plt.close()


def leer_trayectorias(archivo: Path, cantidad: int) -> dict[int, tuple[list, list]]:
    trayectorias = {}
    with open(archivo, encoding="utf-8") as f:
        for linea in f:
            if linea.startswith("#") or linea.strip() == "":
                continue
            partes = linea.split()
            id_peaton = int(partes[0])
            if id_peaton > cantidad:
                continue
            if id_peaton not in trayectorias:
                trayectorias[id_peaton] = ([], [])
            trayectorias[id_peaton][0].append(float(partes[2]))
            trayectorias[id_peaton][1].append(float(partes[3]))
    return trayectorias


def trayectorias(datos: Path, salida: Path, cantidad: int = 40) -> None:
    archivos = sorted(datos.glob("*.txt"))
    elegidos = [archivos[0], archivos[-1]]

    fig, ejes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for eje, archivo in zip(ejes, elegidos):
        for xs, ys in leer_trayectorias(archivo, cantidad).values():
            eje.plot(xs, ys, linewidth=0.8)
        eje.set_title(f"{archivo.stem}: primeros {cantidad} peatones")
        eje.set_ylabel("y (m)")
        eje.set_aspect("equal")
        eje.grid(alpha=0.3)
    ejes[-1].set_xlabel("x (m)")
    plt.savefig(salida / "trayectorias.png", dpi=150, bbox_inches="tight")
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera los gráficos del informe.")
    parser.add_argument("--results", type=Path, default=Path("./results"))
    parser.add_argument("--data", type=Path, default=Path("./data"))
    parser.add_argument("--output", type=Path, default=Path("./results/graficos"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    experimentos = leer_csv(args.results / "experimentos.csv")
    velocidad_vs_densidad(experimentos, args.output)
    flujo_vs_densidad(experimentos, args.output)
    densidad_en_el_tiempo(leer_csv(args.results / "densidad_flujo.csv"), args.output)
    velocidad_por_zona(leer_csv(args.results / "zonas.csv"), args.output)
    velocidades_individuales(leer_csv(args.results / "individual.csv"), args.output)
    trayectorias(args.data, args.output)

    print(f"Gráficos guardados en '{args.output}'")


if __name__ == "__main__":
    main()
