# Modèles oraux

Chaque fichier décrit **un format de création vocale** : à quoi il sert, sa durée, ses voix, sa
structure, son style, et où déposer le script. Un exemple réel accompagne chaque format dans
`exemples/`.

| Format | Fichier | Voix | Durée | Où déposer |
|---|---|---|---|---|
| Revue du matin | `revue-du-matin.md` | une voix (Marie) | 18 à 20 min (30 le lundi) | `episodes/AAAA-MM-JJ.json` |
| Le soir | `le-soir.md` | dialogue Marie et Léa | 18 à 20 min | `episodes/AAAA-MM-JJ-soir.json` |
| Série de préparation | `serie-preparation.md` | dialogue | 10 à 15 min par épisode | `episodes/AAAA-MM-JJ-<serie>-<n>.json` |
| Flash | `flash.md` | une voix | 3 à 6 min | `episodes/` ou `creations/` |
| Chronique | `chronique.md` | une voix | 5 à 8 min | `creations/<nom>.json` |
| Lecture | `lecture.md` | une voix, sans jingle | selon le texte | `creations/<nom>.json` |

## Règles communes à tous les formats

- **Écrire pour l'oreille** : phrases courtes, une idée par phrase, transitions dites à l'oral,
  chiffres arrondis et en toutes lettres quand c'est plus clair, sigles expliqués à la première
  occurrence. Jamais de liste à puces, de crochets, de parenthèses ni d'adresse web dans le texte lu.
- **Attribuer** : « selon la Cour des comptes… ». Aucun fait sans source consultée le jour même.
  Présenter les positions en présence sans prendre parti.
- **Voix** : `Marie` (animatrice), `Lea` (experte, intervenante), `Harriet` (passages en anglais).
  Les correspondances sont dans `config.yml` (`voice.mistral.voices`).
- **Vérifier avant de déposer** : `python scripts/valider.py <fichier>`.
- **Tout ce qui est déposé est public** (GitHub Pages et flux podcast) : aucun contenu personnel.

## Ajouter ou améliorer un format

Un format est un simple fichier Markdown. Pour en créer un : copier le plus proche, l'adapter,
ajouter un exemple dans `exemples/`, l'inscrire dans le tableau ci-dessus, puis proposer la
modification par une branche et une demande de fusion (voir `skills/studio-vocal/SKILL.md`).
