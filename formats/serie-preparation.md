# Format : Série de préparation

Courte série d'émissions dialoguées pour préparer une échéance précise (entretien, oral, concours).
Modèle : « Le G7 à portée de main » (épisodes `2026-10-23-g7-1` à `2026-10-30-g7-7`, puis
`2026-11-03-g7-flash` la veille de l'entretien).

## Principe

- **Un plan de série d'abord** : 5 à 8 épisodes, chacun avec un thème (le poste et ses enjeux,
  chaque grand dossier, le vocabulaire, les questions probables, la présentation de deux minutes),
  puis un flash de révision la veille.
- **Chaque épisode** : 1 700 à 2 500 mots, 10 à 15 minutes, dialogue animatrice et experte
  (`Marie` et `Lea`), comme `le-soir.md`.
- Questions de l'animatrice courtes et concrètes (« Où se trouve exactement ce poste ? »),
  réponses de l'experte structurées et chiffrées.
- Pour l'anglais, une réplique en voix `Harriet`.

## Livraison

`episodes/AAAA-MM-JJ-<serie>-<n>.json` (ex. `2026-10-23-g7-1.json`), avec `pub_utc` pour fixer
l'heure de publication (ex. `"2026-10-23T16:45:00Z"`). Titre : « <Nom de la série> · <n> · <thème> ».

**Attention** : le flux est public. Ne pas citer de données personnelles (nom, coordonnées,
détails de candidature) ; parler du poste, pas de la personne.
