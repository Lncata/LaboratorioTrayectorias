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

## Guía de ejecución en Linux (paso a paso)

Esta guía parte de un Linux sin nada instalado y se probó en Ubuntu 24.04 con Python 3.12. En otras distribuciones solo cambia el comando de instalación del paso 1. Todos los comandos se escriben en una terminal y, desde el paso 2, se ejecutan **dentro de la carpeta del proyecto**.

### 1. Verificar (o instalar) los requisitos del sistema

```bash
python3 --version   # debe mostrar 3.10 o superior
git --version
```

Si falta algo, en Ubuntu o Debian:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

En Fedora o RHEL: `sudo dnf install -y python3 python3-pip git`. Si trabaja en un servidor sin permisos de administrador, pida al administrador que instale lo que falte.

> En Ubuntu y Debian el paquete `python3-venv` es necesario para el paso 3.

### 2. Obtener el proyecto

Si trabaja en el servidor del laboratorio, conéctese primero: `ssh usuario@servidor`. Luego:

```bash
git clone https://github.com/Lncata/LaboratorioTrayectorias.git
cd LaboratorioTrayectorias
```

Si el proyecto está en su computador y debe llevarlo al servidor, cópielo con `scp -r LaboratorioTrayectorias usuario@servidor:~/`.

### 3. Crear el entorno virtual e instalar las dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

El prompt mostrará `(.venv)` al comienzo. En cada terminal nueva hay que volver a activar el entorno con `source .venv/bin/activate` (para salir: `deactivate`). El pipeline solo usa la librería estándar; `matplotlib` se necesita únicamente para los gráficos.

### 4. Comprobar que están los datos

```bash
ls data/
```

Deben aparecer los 9 archivos `uni_corr_500_01.txt` a `uni_corr_500_09.txt`.

### 5. Ejecutar el pipeline

```bash
python3 main.py --input ./data --output ./results
```

Demora entre 15 y 25 segundos. Al comienzo imprime la configuración y las etapas, y debe terminar así (el código de salida es 0):

```
Configuración seleccionada:
  Entrada: data
  Salida: results
  Frecuencia (fps): no especificada
  Umbral de detención: 0.1 m/s
Ejecutando etapa: CargaExperimentos
  uni_corr_500_01: 28993 observaciones, fps=16.0, líneas descartadas=0
  ...
Ejecutando etapa: ExportacionResultados
  Resultados guardados en 'results'
```

Compruebe el código de salida con `echo $?` (debe ser `0`; si es `1`, el pipeline imprimió la causa del error).

### 6. Revisar los resultados

```bash
ls results
head -3 results/experimentos.csv
```

Deben existir `individual.csv`, `experimentos.csv`, `zonas.csv`, `densidad_flujo.csv` y `resumen.json`.

### 7. Generar los gráficos

```bash
python3 graficos.py --results ./results --data ./data --output ./results/graficos
ls results/graficos
```

No requiere pantalla ni entorno gráfico. Se crean 6 imágenes `.png`. Para verlas desde su computador: `scp "usuario@servidor:~/LaboratorioTrayectorias/results/graficos/*.png" .`

### Problemas frecuentes

| Mensaje o síntoma | Causa y solución |
|---|---|
| `python3: command not found` | Falta Python. Ver paso 1. |
| `ensurepip is not available` al crear el entorno | Falta `python3-venv`: `sudo apt install python3-venv` y repetir el paso 3. |
| `externally-managed-environment` al usar `pip` | No instale paquetes fuera del entorno virtual. Active `.venv` (paso 3). |
| `ModuleNotFoundError: No module named 'matplotlib'` | El entorno no está activado o falta instalar: `source .venv/bin/activate` y `pip install -r requirements.txt`. |
| `Error: la ruta de entrada '...' no existe` | Está fuera de la carpeta del proyecto o escribió mal `--input`. |
| `No hay archivos .txt en '...'` | La carpeta indicada no contiene datos. Revise el paso 4. |
| `... no tiene fps: use --fps` | El archivo no trae el encabezado `# framerate`. Indíquelo, por ejemplo `--fps 16`. |
| `Permission denied` al guardar resultados | Use una carpeta donde pueda escribir: `--output ~/resultados`. |

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
| `--fps` | fuerza una frecuencia (mayor que 0) para todos los archivos | se lee del archivo |
| `--unidad` | unidad de las coordenadas (`m` o `cm`) | `m` |
| `--umbral-detencion` | velocidad (m/s) bajo la cual un peatón se considera detenido | `0.1` |

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
models/            Observacion, Trayectoria, Experimento (inmutables), ResultadoAnalisis
funciones/         funciones puras de cálculo: movimiento.py (indicadores individuales) y espacio.py (zonas, densidad, flujo)
stages/            las 6 etapas del pipeline
data/              datos de entrada
results/           resultados generados
```

## Diseño funcional

Los cálculos viven en `funciones/` como funciones puras: reciben datos y devuelven valores nuevos, sin estado global. `Trayectoria` agrupa los cálculos propios de un peatón y delega en ellas. Las etapas solo orquestan: no modifican los objetos que reciben, sino que devuelven un `Experimento` nuevo (`dataclasses.replace`). Se usan `map`, `reduce`, `groupby`, `Counter` y comprensiones donde resultan naturales.

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
- **Detención:** cada ventana de 1 s con velocidad menor a 0,1 m/s es un intervalo detenido; como las ventanas se solapan, los intervalos superpuestos se fusionan en una sola detención. Así un mismo tramo no se cuenta dos veces y el tiempo detenido nunca supera el tiempo total del peatón. El umbral se puede cambiar con `--umbral-detencion`.
- **Zonas:** el tramo x ∈ [−5, 5] m se divide en tres zonas de igual largo (izquierda, centro, derecha).
- **Densidad:** ρ = N / A en un área de medición de 10 × 5 m (x ∈ [−5, 5], y ∈ [0, 5]).
- **Flujo:** J = N / Δt, con N el número de peatones que cruzan la línea x = 0.
