# Revue du matin

Podcast quotidien de veille (relations internationales, économie, industrie, IA) pour la préparation des concours.

## Fonctionnement

1. Chaque matin, une tâche planifiée Claude rédige le script et le dépose dans `episodes/AAAA-MM-JJ.json`.
2. Ce dépôt déclenche le workflow « Fabriquer l'épisode » : synthèse vocale (Gemini TTS par défaut), jingle, normalisation du volume, MP3.
3. Le MP3 et le flux `feed.xml` sont publiés sur GitHub Pages ; l'application de podcasts (AntennaPod) récupère l'épisode.

## Réglages

Tout se règle dans `config.yml` :

- `voice.provider` : `gemini`, `elevenlabs` ou `google_chirp` ;
- `voice.gemini.voice` : nom de la voix (voir le workflow « Écouter les voix disponibles ») ;
- `voice.gemini.style` : consigne de ton.

Les clés d'API sont des secrets GitHub (Settings › Secrets and variables › Actions) :
`GEMINI_API_KEY`, et au besoin `ELEVENLABS_API_KEY` ou `GOOGLE_TTS_API_KEY`.

## Fichiers

- `assets/` : jingles (composition originale) et pochette ;
- `scripts/` : synthèse (`tts.py`), assemblage (`build_episode.py`), flux (`feed.py`), extraits de voix ;
- `docs/` : site publié (audio, flux, extraits).
