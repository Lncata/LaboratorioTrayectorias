# Análisis de Trayectorias Peatonales

Laboratorio 1 — Programación Científica.

Pipeline en Python que lee trayectorias de peatones registradas en experimentos de un corredor, reconstruye la trayectoria de cada persona y calcula indicadores individuales (distancia, velocidad, eficiencia, detenciones) y colectivos (zonas, densidad, flujo), comparando varios experimentos.

## Requisitos

- Linux con Python 3.10 o superior
- Git
- `matplotlib` (solo para los gráficos; el pipeline usa únicamente la librería estándar)

## Instalación

```bash
git clone https://github.com/Lncata/LaboratorioTrayectorias.git
cd LaboratorioTrayectorias
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Datos

Los datos provienen del experimento de flujo unidireccional en corredor (`uni_corr_500`) del archivo de datos de dinámica peatonal del Forschungszentrum Jülich: https://ped.fz-juelich.de/db/doku.php?id=corridor5

Los archivos van en la carpeta `data/`, uno por experimento. Formato de cada archivo:

```
# framerate: 16 fps
# id frame x/m y/m z/m
1 235 7.50699 2.87235 1.871
```

| Columna | Significado | Unidad |
|---|---|---|
| id | identificador del peatón | — |
| frame | número de cuadro | — |
| x, y | posición en el corredor | m |
| z | altura de la persona | m |

La frecuencia de muestreo (fps) se lee del encabezado de cada archivo.

## Ejecución

Pipeline completo:

```bash
python3 main.py --input ./data --output ./results
```

Gráficos (después de ejecutar el pipeline):

```bash
python3 graficos.py --results ./results --data ./data --output ./results/graficos
```

Opciones de `main.py`:

| Opción | Descripción | Por defecto |
|---|---|---|
| `--input` | archivo o carpeta con los `.txt` | `./data` |
| `--output` | carpeta de resultados | `./results` |
| `--fps` | fuerza una frecuencia para todos los archivos | se lee del archivo |
| `--unidad` | unidad de las coordenadas (`m` o `cm`) | `m` |

Ayuda: `python3 main.py --help`

## Etapas del pipeline

| # | Etapa | Archivo | Qué hace |
|---|---|---|---|
| 1 | Carga | `stages/carga.py` | Lee los archivos y crea un `Experimento` por archivo |
| 2 | Preparación | `stages/preparacion.py` | Valida, agrupa por peatón, ordena por frame y crea las `Trayectoria` |
| 3 | Análisis individual | `stages/individual.py` | Distancia, desplazamiento, velocidades, eficiencia y detenciones de cada peatón |
| 4 | Análisis espacial | `stages/espacial.py` | Indicadores por zona, densidad y flujo |
| 5 | Comparación | `stages/colectivo.py` | Resumen por experimento y correlación densidad–velocidad |
| 6 | Exportación | `stages/exportacion.py` | Guarda los resultados en `results/` |

## Estructura del proyecto

```
main.py            punto de entrada del pipeline
graficos.py        genera los gráficos del informe
pipeline/          coordinación de etapas (Pipeline, EtapaPipeline, ContextoPipeline)
models/            Observacion, Trayectoria, Experimento, ResultadoAnalisis
stages/            las 6 etapas del pipeline
data/              datos de entrada
results/           resultados generados
```

## Resultados generados

| Archivo | Contenido |
|---|---|
| `results/individual.csv` | una fila por peatón con todos sus indicadores |
| `results/experimentos.csv` | una fila por experimento: peatones, velocidad, densidad, flujo, distancia y tiempo medios |
| `results/zonas.csv` | peatones, velocidad media y tiempo medio de cruce por zona |
| `results/densidad_flujo.csv` | densidad y flujo de cada segundo de cada experimento |
| `results/resumen.json` | resumen por experimento y correlación densidad–velocidad |
| `results/graficos/*.png` | figuras para el informe |

## Decisiones metodológicas

- **Velocidad:** se calcula entre posiciones separadas por 1 segundo para reducir el ruido del seguimiento de video.
- **Detención:** tramo en que la velocidad (en ventana de 1 s) es menor a 0,1 m/s.
- **Zonas:** el tramo x ∈ [−5, 5] m se divide en tres zonas de igual largo (izquierda, centro, derecha).
- **Densidad:** ρ = N / A en un área de medición de 10 × 5 m (x ∈ [−5, 5], y ∈ [0, 5]).
- **Flujo:** J = N / Δt, con N el número de peatones que cruzan la línea x = 0.
