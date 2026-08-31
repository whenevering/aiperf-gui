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
- Les graphiques sont affiches avant les blocs de resultat par concurrence
- Chaque niveau de concurrence a son propre bloc avec TTFT, P99 requete, ITL, TPS sortie, RPS et longueur de sortie
- Les tableaux de metriques AIPerf et les avertissements sont replies par defaut
- L'etat en cours utilise un fondu de couleur; les etats reussi et echec utilisent des couleurs plus visibles
- Page d'aide multilingue separee

## Image Release

Les Releases GitHub fournissent une image Docker compressee :

```text
aiperf-gui-0.1.0-yyyy-mm-dd.tar.gz
```

Chargement et execution :

```bash
docker load -i aiperf-gui-0.1.0-2026-08-31.tar.gz
docker run --rm -p 8080:8080 aiperf-gui:0.1.0
```

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
