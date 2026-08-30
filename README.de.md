# AIPerf GUI

[中文](README.md) | [English](README.en.md) | [Francais](README.fr.md) | Deutsch | [Espanol](README.es.md)

AIPerf GUI ist eine Dockerisierte Web-Konsole fuer NVIDIA AIPerf 0.12.0. Sie hilft beim Benchmarking OpenAI-kompatibler Modelldienste mit Parallelitaets-Sweeps, Latenz- und Durchsatzmetriken, Modellabruf, Proxy-Einstellungen und Live-Logs.

![AIPerf GUI Screenshot](docs/screenshot.png)

## Funktionen

- Basiert auf `nvcr.io/nvidia/ai-dynamo/aiperf:0.12.0`
- Lokale Web-GUI auf Port `8080`
- Unterstuetzt `chat` und `completions`
- Manuelle Modelleingabe plus Abruf ueber `/models`
- Parallelitaets-Sweeps wie `1,2,4,8,16`
- Einstellbare Eingabe-Tokens, Ausgabe-Tokens, Anfragen, Warmup und Timeout
- Streaming, feste Ausgabe, Servermetriken, Proxy und No-Proxy
- Ergebnis-Karten und Diagramme fuer TTFT, Latenz, ITL, Ausgabe-TPS, RPS und Ausgabe-Laenge
- Separate mehrsprachige Hilfeseite

## Schnellstart

```bash
./build.sh
./run.sh
```

Oeffnen:

```text
http://127.0.0.1:8080
```

## Lizenz

GNU General Public License v3.0. Siehe [LICENSE](LICENSE).
