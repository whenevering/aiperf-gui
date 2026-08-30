# AIPerf GUI

[中文](README.md) | [English](README.en.md) | [Francais](README.fr.md) | [Deutsch](README.de.md) | Espanol

AIPerf GUI es una consola Web Dockerizada para NVIDIA AIPerf 0.12.0. Permite evaluar servicios de modelos compatibles con OpenAI usando barridos de concurrencia, metricas de latencia y rendimiento, descubrimiento de modelos, proxy y logs en vivo.

![Captura de AIPerf GUI](docs/screenshot.png)

## Funciones

- Basado en `nvcr.io/nvidia/ai-dynamo/aiperf:0.12.0`
- Web GUI local en el puerto `8080`
- Soporta `chat` y `completions`
- Entrada manual de modelo y carga mediante `/models`
- Barridos de concurrencia como `1,2,4,8,16`
- Configuracion de tokens de entrada, tokens de salida, solicitudes, preparacion y tiempo limite
- Controles de streaming, salida fija, metricas servidor, proxy y sin proxy
- Tarjetas y graficas para TTFT, latencia, ITL, TPS de salida, RPS y longitud de salida
- Pagina de ayuda multilingue separada

## Inicio Rapido

```bash
./build.sh
./run.sh
```

Abrir:

```text
http://127.0.0.1:8080
```

## Licencia

GNU General Public License v3.0. Ver [LICENSE](LICENSE).
