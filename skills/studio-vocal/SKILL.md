---
name: studio-vocal
description: Écrire et publier une création vocale (Revue du matin, Le soir, série de préparation, flash, chronique, lecture) avec le dépôt revue-du-matin, qui fabrique le MP3 et le flux podcast. À utiliser pour toute émission ou capsule audio destinée à être écoutée en podcast.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [podcast, audio, tts, radio, voxtral]
    related_skills: [auditions-parlementaires]
---

# Studio vocal

Toi, Hermes, tu écris le script. GitHub Actions fait le reste : synthèse vocale (Voxtral par
défaut), jingles, mixage, MP3 et flux podcast. Tu ne lances jamais toi-même la synthèse vocale.

## Quand l'utiliser

- Une émission ou capsule audio à écouter dans l'application de podcasts, ou à partager par lien.
- **Pas pour** un message vocal personnel ou une réponse vocale dans Telegram : utilise ta propre
  synthèse vocale. Ici, **tout est public** (GitHub Pages).

## Repères rapides

| Élément | Où |
|---|---|
| Dépôt local | `~/outils/revue-du-matin` (faire `git pull` avant chaque travail) |
| Formats (modèles oraux) | `formats/*.md`, exemples dans `formats/exemples/` |
| Format du fichier JSON | en-tête de `scripts/build_episode.py` |
| Vérification | `python3 scripts/valider.py <fichier>` |
| Flux podcast | `episodes/AAAA-MM-JJ[-suffixe].json` → `docs/audio/…mp3` |
| Hors flux | `creations/<nom>.json` → `docs/creations/<nom>.mp3` |
| Voix et service | `config.yml` (`voice.provider`, `voice.mistral.voices`) |
| Journal des leçons | `AMELIORATIONS.md` |

Adresses publiques : `https://martinparnin-svg.github.io/revue-du-matin/audio/<nom>.mp3`,
`…/creations/<nom>.mp3`, flux `…/feed.xml`.

## Procédure

1. `cd ~/outils/revue-du-matin && git pull --rebase`.
2. Lis le format demandé dans `formats/` et son exemple. Lis aussi `AMELIORATIONS.md` : il contient
   les corrections déjà demandées par l'utilisateur.
3. Fais la recherche (sources du jour, au moins deux par sujet principal), puis écris le script
   directement en JSON.
4. `python3 scripts/valider.py <fichier>` : corrige toute erreur ; traite les avertissements
   (chapitre trop long, crochets, adresses web, listes, voix inconnue). Vérifie la durée annoncée.
5. Dépose : `git add <fichier> && git commit -m "Script du <date>" && git push`.
   Ne touche à aucun autre fichier dans ce commit.
6. Vérifie la fabrication une dizaine de minutes plus tard : `git pull` puis présence du MP3, ou
   `gh run list -L 3` si l'outil `gh` est disponible. En cas d'échec, lis le journal du run
   (`gh run view <id> --log-failed`) et signale la cause exacte à l'utilisateur.
7. Envoie à l'utilisateur : le titre, les sujets en une ligne chacun, ce qui manque éventuellement.

## Modèles d'IA

Contenu public : fournisseur `mistral-public`, modèle GLM-5.3-Flash par défaut. Si la qualité de
l'écriture en français déçoit, rédige le script avec Mistral Large 4. N'utilise Claude que si
l'utilisateur le demande.

## Pièges connus

- Le texte est lu tel quel : pas de crochets, parenthèses, listes, adresses web, abréviations
  ambiguës. Écris « deux virgule cinq pour cent », pas « 2,5 % », quand c'est plus clair.
- Un chapitre à une voix au-delà de 3 000 caractères : le découper en deux chapitres.
- Une voix absente de `config.yml` est lue avec la voix par défaut, sans erreur visible.
- `style` ne sert qu'avec Gemini ; il est ignoré avec Voxtral.
- « HTTP 402 You need a subscription » dans le journal du run : la clé `MISTRAL_API_KEY` du dépôt
  n'a pas accès à la synthèse vocale (organisation sans abonnement). Ne relance pas : préviens
  l'utilisateur, qui doit remplacer le secret par une clé de son organisation Mistral payante.
- Le flux et les créations sont publics : jamais de données personnelles.

## S'améliorer

Tu es encouragé à améliorer cet outil, dans ce cadre :

- **Après chaque correction de l'utilisateur**, ajoute une ligne datée dans `AMELIORATIONS.md`
  (rubrique « Leçons »), et commite-la avec le script suivant.
- **Contenus** (`episodes/`, `creations/`, `AMELIORATIONS.md`) : commit direct sur `main`.
- **Tout le reste** (formats, ce fichier, scripts, `config.yml`) : crée une branche
  `hermes/<sujet>`, pousse-la, ouvre une demande de fusion (`gh pr create`) ou envoie le lien de la
  branche à l'utilisateur. Il relit et fusionne lui-même.
- **Jamais** : modifier `.github/workflows/`, les secrets, ou supprimer des épisodes publiés.
- Teste avant de proposer : `scripts/valider.py` sur les exemples de `formats/exemples/` ; pour
  une modification des scripts audio, demande à l'utilisateur de lancer le workflow « Épisode
  d'essai (hors flux) » depuis l'onglet Actions.
