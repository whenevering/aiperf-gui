# AIPerf GUI

[中文](README.md) | [English](README.en.md) | Francais | [Deutsch](README.de.md) | [Espanol](README.es.md)

AIPerf GUI est une console Web Dockerisee pour NVIDIA AIPerf 0.12.0. Elle permet de tester des services de modeles compatibles OpenAI avec des niveaux de concurrence, des metriques de latence et de debit, la decouverte des modeles, le proxy et les journaux en temps reel.

![Capture AIPerf GUI](docs/screenshot.png)

## Fonctions

- Basee sur `nvcr.io/nvidia/ai-dynamo/aiperf:0.12.0`
- Interface Web locale sur le port `8080`
- Support de `chat` et `completions`
- Saisie manuelle du modele et chargement via `/models`
- Sweeps de concurrence comme `1,2,4,8,16`
- Reglages pour tokens d'entree, tokens de sortie, requetes, prechauffe et delai
- Options streaming, sortie fixe, metriques serveur, proxy et sans proxy
- Cartes et graphiques pour TTFT, latence, ITL, TPS sortie, RPS et longueur de sortie
- Page d'aide multilingue separee

## Demarrage Rapide

```bash
./build.sh
./run.sh
```

Ouvrir :

```text
http://127.0.0.1:8080
```

## Licence

GNU General Public License v3.0. Voir [LICENSE](LICENSE).
