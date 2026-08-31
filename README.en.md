# AIPerf GUI

[中文](README.md) | English | [Francais](README.fr.md) | [Deutsch](README.de.md) | [Espanol](README.es.md)

AIPerf GUI is a Docker-packaged Web console for NVIDIA AIPerf 0.12.0. It helps benchmark OpenAI-compatible model services with concurrency sweeps, latency metrics, throughput metrics, model discovery, proxy settings, and live logs.

![AIPerf GUI screenshot](docs/screenshot.png)

## Features

- Based on `nvcr.io/nvidia/ai-dynamo/aiperf:0.12.0`
- Local Web GUI on port `8080`
- Supports `chat` and `completions`
- Manual model entry plus `/models` fetching
- Concurrency sweeps such as `1,2,4,8,16`
- Configurable input tokens, output tokens, requests, warmup, and timeout
- Streaming, fixed output, server metrics, proxy, and no-proxy controls
- Charts are shown before the per-concurrency result blocks
- Each concurrency level is rendered as its own result block with TTFT, request P99, ITL, output TPS, RPS, and output length
- Detailed AIPerf metric tables and warning sections are collapsed by default
- Running status uses a fading background pulse; succeeded and failed states use brighter status colors
- Separate multilingual help page

## Release Image

GitHub Releases provide a compressed Docker image:

```text
aiperf-gui-0.1.0-yyyy-mm-dd.tar.gz
```

Load and run it with:

```bash
docker load -i aiperf-gui-0.1.0-2026-08-31.tar.gz
docker run --rm -p 8080:8080 aiperf-gui:0.1.0
```

## Quick Start

```bash
./build.sh
./run.sh
```

Open:

```text
http://127.0.0.1:8080
```

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).
