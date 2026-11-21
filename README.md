# Revue du matin

Podcast quotidien de veille (relations internationales, économie, industrie, IA) pour la préparation des concours,
et studio de création vocale : chroniques, lectures, séries de préparation, flashs.

## Fonctionnement

1. Un agent (Hermes, ou une tâche planifiée Claude) rédige le script selon un modèle de `formats/` et le dépose dans
   `episodes/AAAA-MM-JJ.json` (flux podcast) ou `creations/<nom>.json` (hors flux).
2. Ce dépôt déclenche le workflow « Fabriquer l'épisode » ou « Fabriquer une création » : synthèse vocale
   (Voxtral de Mistral par défaut), jingles, normalisation du volume, MP3.
3. Le MP3 et le flux `feed.xml` sont publiés sur GitHub Pages ; l'application de podcasts (AntennaPod) récupère l'épisode.

## Réglages

Tout se règle dans `config.yml` :

- `voice.provider` : `mistral`, `gemini`, `elevenlabs` ou `google_chirp` ;
- `voice.mistral.voices` : correspondance entre les noms de voix des scripts et les voix Voxtral ;
- `voice.gemini.voice` : nom de la voix (voir le workflow « Écouter les voix disponibles ») ;
- `voice.gemini.style` : consigne de ton.

Les clés d'API sont des secrets GitHub (Settings › Secrets and variables › Actions) :
`MISTRAL_API_KEY`, et au besoin `GEMINI_API_KEY`, `ELEVENLABS_API_KEY` ou `GOOGLE_TTS_API_KEY`.

## Fichiers

- `assets/` : jingles (composition originale) et pochette ;
- `scripts/` : synthèse (`tts.py`), assemblage (`build_episode.py`), flux (`feed.py`), extraits de voix ;
- `docs/` : site publié (audio, flux, extraits, `creations/`) ;
- `formats/` : modèles oraux (un fichier par format, avec exemples) ;
- `creations/` : scripts hors flux ;
- `skills/studio-vocal/SKILL.md` : mode d'emploi pour l'agent Hermes ;
- `AMELIORATIONS.md` : leçons retenues et idées en attente.

## Vérifier un script avant de le déposer

```bash
python3 scripts/valider.py episodes/2026-11-21.json
```

Contrôle le format, les voix, la longueur des chapitres et la durée estimée.

## Utilisation par Hermes

Cloner le dépôt dans `~/outils/revue-du-matin`, puis déclarer le dossier de compétences dans
`~/.hermes/config.yaml` :

```yaml
skills:
  external_dirs:
    - ~/outils/revue-du-matin/skills
```

Hermes trouve alors la compétence `studio-vocal`. Il dépose directement les scripts ; toute autre
modification passe par une branche `hermes/…` et une demande de fusion à relire.
