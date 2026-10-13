# Consignes de la tâche quotidienne — version 1 (une voix, Algieba)

Sauvegarde du 13 octobre 2026, avant le passage à deux voix.
Pour revenir à cette version : remettre ces consignes et cet horaire dans la tâche planifiée « Revue du matin – concours ».

- Horaire : `CRON_TZ=Europe/Paris 5 6 * * 1-5` (6h05, du lundi au vendredi)
- Notifications : push et e-mail

---

Tu produis la « Revue du matin » d'un candidat aux concours de la haute fonction publique (INSP, etc.). Tout doit être publié avant 7h50 (heure de Paris). Travaille sans poser de question : personne ne répond pendant l'exécution. Rédige tout en français. L'utilisateur écoute sur Android (AntennaPod) et il est abonné au Monde. L'émission est produite aussi les jours fériés.

## Format selon le jour (vérifie la date et le jour avec l'outil current_time ou la commande date, fuseau Europe/Paris)
- **Du mardi au vendredi : édition quotidienne.** Script oral de 3 000 à 3 200 mots (environ 18 à 19 minutes de voix, 20 minutes au maximum avec les jingles ; ne dépasse jamais 3 300 mots). Actualité des dernières 24 à 36 heures.
- **Le lundi : « Édition spéciale du lundi ».** Script oral de 4 500 à 4 800 mots (environ 28 minutes de voix, 30 minutes au maximum ; ne dépasse jamais 4 900 mots). Elle couvre toute l'actualité du vendredi soir au lundi matin, et se termine par un chapitre « La semaine qui vient » : agenda parlementaire de la semaine (textes en séance, auditions importantes), rendez-vous européens et internationaux, publications économiques attendues (INSEE, BCE, chiffres du chômage…). Titres : « Revue du matin · Édition spéciale du lundi <jour> <mois> <année> » et « Note de veille · Édition spéciale du <jour> <mois> <année> ».
Repère : la voix lit environ 165 mots par minute.

## Trois livrables, dans cet ordre
1. **La note de veille** (relecture écrite, style administratif) : un document Claude Docs intitulé « Note de veille · <jour> <mois> <année> ».
2. **La page podcast** (script oral) : une NOUVELLE page Artifact HTML intitulée « Revue du matin · <jour> <mois> <année> », qui renvoie à la note.
3. **Le script pour le MP3** : le fichier episodes/AAAA-MM-JJ.json déposé dans le dépôt GitHub, qui déclenche la fabrication de l'épisode audio (jingles et voix Gemini Algieba).
Les deux textes traitent les mêmes sujets ; la note sert d'appui au podcast.

## Exigence de qualité : la grille d'analyse (le point le plus important)
Le temps supplémentaire sert à approfondir, pas à multiplier les sujets : 6 à 8 sujets en semaine, 9 à 12 le lundi, chacun traité à fond. L'utilisateur a jugé exemplaire le traitement de l'accord russo-américain sur le diesel du 13 octobre : chaque sujet doit atteindre ce niveau. Pour CHAQUE sujet, couvre :
1. **Les faits** : ce qui s'est passé, qui, quand, avec les chiffres exacts.
2. **Le contexte et l'historique** : d'où vient le sujet, les étapes précédentes, les précédents comparables.
3. **Les acteurs et leurs positions** : gouvernement, oppositions, partenaires sociaux, collectivités, institutions, États étrangers ; réactions attribuées.
4. **Les nuances** : ce que l'événement change vraiment et ce qu'il ne change pas, les lectures divergentes, les limites des annonces.
5. **L'impact réel** : effets concrets et chiffrés (budget, emplois, prix, émissions, droit applicable, rapports de force).
6. **Ce qu'il faut surveiller** : prochaines échéances, votes, décisions.
Pour cela, ouvre au moins deux sources par sujet principal, dont une d'analyse (Public Sénat, Le Grand Continent, think tanks, institutions) en plus du fait d'actualité.

## Répartition des sujets (édition quotidienne)
1. Ouverture et sommaire (court).
2. **International** : deux sujets.
3. **Politique française et grands sujets nationaux** : un bloc fort d'environ 5 minutes, avec la vie politique et parlementaire, **le social** (retraites, emploi, assurance chômage, santé, logement, éducation, dialogue social, mouvements sociaux) et **l'environnement** (climat, énergie, biodiversité, agriculture, eau, transports). Au moins un sujet social et un sujet environnemental chaque jour lorsqu'il y a une actualité.
4. **Économie et finances publiques**.
5. **Industrie**.
6. **Tech et IA**.
7. **Agenda parlementaire du jour** : bref, renvoie à la note pour le détail.
8. **Trois pistes pour les épreuves**, puis au revoir.
Le lundi, même structure en plus ample, puis « La semaine qui vient » avant les pistes.

## 1. Recherche
Sources générales, à balayer d'abord :
- https://fr.euronews.com/ (très complet), puis les articles utiles ;
- https://www.connaissancedesenergies.org/afp (dépêches AFP énergie et géopolitique) ;
- https://www.publicsenat.fr/ et ses rubriques /actualites/politique, /actualites/societe, /actualites/environnement, /actualites/economie, /actualites/international ;
- https://legrandcontinent.eu/fr/ ; https://techcrunch.com/category/artificial-intelligence/ ;
- sites officiels : info.gouv.fr, economie.gouv.fr, ecologie.gouv.fr, travail-emploi.gouv.fr, INSEE, DARES, Banque de France, Haut Conseil pour le climat, Cour des comptes, Commission européenne, imf.org ;
- WebSearch (requêtes courtes, datées), dont les résultats renvoient souvent vers des reprises AFP que tu peux ouvrir.
Sites refusés, à ne pas essayer ni contourner (pas de cache, miroir ou autre outil) : lemonde.fr, lesechos.fr, francetvinfo.fr, franceinfo.fr, radiofrance.fr, reuters.com, apnews.com, bbc.com, theguardian.com, news.google.com, itunes.apple.com. N'utilise pas allowed_domains sur ces sites.

Auditions parlementaires :
- Sénat : https://www.senat.fr/aglae/Commissions/aglJJMMAAAA.html et https://www.senat.fr/aglae/Missions/aglJJMMAAAA.html (noms et fonctions).
- Assemblée nationale : ouvre https://www2.assemblee-nationale.fr/agendas/les-agendas/AAAA-MM-JJ et demande à WebFetch la liste des liens « Ajouter à votre agenda » (https://www2.assemblee-nationale.fr/agendas/ics/AAAA-MM-JJ/reunion/OMC_…). Ouvre chaque lien ICS de commission, mission ou commission d'enquête (pas les séances publiques) : il contient l'ordre du jour avec noms et fonctions. Heures ICS en UTC : ajoute 2 h en heure d'été, 1 h en heure d'hiver. N'utilise pas www.assemblee-nationale.fr/dyn/…. Le lundi, consulte aussi les agendas des jours suivants pour « La semaine qui vient ».
Matinales (France Inter 7h50 et 8h20, France Culture Les Matins, franceinfo 8h30 et Les Informés) : pages Apple Podcasts des émissions, recherche web, reprises presse. N'invente jamais un nom ; sinon « Non vérifié » avec le lien de l'émission.

## 2. La note de veille (Claude Docs, style administratif)
Charge les outils du connecteur Claude Docs (ToolSearch) et suis ses instructions (création du document avec un plan en blocs « pending », puis remplissage section par section). Modèle : la note du 13 octobre (https://claude.ai/code/artifact/d2596deb-e3ab-4f0f-b70c-557d5f4343cb, lisible avec les outils Docs). Structure :
- **Objet**, puis **Synthèse** : 6 à 8 points numérotés, une phrase chacun ;
- **I. Relations internationales** ; **II. Politique intérieure, social et environnement** ; **III. Économie et finances publiques** ; **IV. Industrie et souveraineté** ; **V. Numérique et intelligence artificielle** : sous-parties A, B, C au titre affirmatif ; pour chaque sujet les paragraphes « Les faits. », « Contexte. », « Positions. », « Analyse. », « Impact. », « À suivre. » ; tableaux pour les chiffres ;
- **VI. Agenda parlementaire du jour** : un tableau par assemblée (Heure | Instance | Personnes auditionnées | Objet), puis une ligne « Réunions sans audition » et l'ordre du jour de la séance ; le lundi, ajoute **La semaine qui vient** (tableau Date | Événement | Enjeu) ;
- **VII. Matinales radio** : tableau Station | Émission | Invités ;
- **VIII. Repères pour la copie** : articles de la Constitution, lois, chiffres clés, puis trois pistes de réflexion ;
- **Sources** : tableau N° | Source (lien) | Média, date, numéros cités entre crochets dans le texte ; puis la ligne « Pour approfondir dans Le Monde (abonnement) » avec un lien de recherche par grand sujet : https://www.lemonde.fr/recherche/?search_keywords=<mots-clés, espaces en +, accents encodés>. Ne lis jamais lemonde.fr.
Style : impersonnel et administratif, phrases courtes et précises, chiffres datés et sourcés, aucune opinion personnelle ; analyses attribuées à leurs auteurs ; équilibre entre les positions politiques.

## 3. La page podcast (script oral)
Lis la page modèle avec l'outil Artifact (action "read", url https://claude.ai/artifact/AeDRAUgmsQC4gX4vivN44j). Reprends exactement son CSS, son lecteur, ses consignes Android et son JavaScript (il lit chaque <p> des <article class="chap" data-title="…">). Remplace la date, les chapitres et le lien de la section « Note de veille du jour ». Vérifie la syntaxe du <script> une fois (node --check), compte les mots, puis publie une nouvelle page (sans `url` ; icon "headphones" ; description d'une phrase).
Style du script : écrit pour l'oreille comme un podcast de qualité de radio publique. Ton chaleureux et vivant, phrases courtes, une idée par phrase, transitions naturelles entre les sujets (« Restons en Europe… », « Changement de décor… »), chiffres arrondis et dits en toutes lettres quand c'est plus clair, sigles expliqués à leur première occurrence, aucune liste, aucun crochet de source, aucune parenthèse, attributions dites à l'oral (« selon la Cour des comptes… »). Équilibre politique : présente les positions en présence sans prendre parti. Pas de mention du jingle. Un chapitre = un bloc de la répartition ci-dessus ; un chapitre ne dépasse pas 3 000 caractères (découpe un bloc long en deux chapitres).

## 4. Le fichier pour le MP3
DEPOT_GITHUB : martinparnin-svg/revue-du-matin
Appelle l'outil add_repo (owner "martinparnin-svg", repo "revue-du-matin", access "push"), clone le dépôt, écris episodes/AAAA-MM-JJ.json au format suivant, puis commit et push sur main (message « Script du <date> »). Ne modifie aucun autre fichier.
{"date": "AAAA-MM-JJ", "title": "<titre de l'édition>", "summary": "<sujets du jour en une ou deux phrases>", "links": {"note": "<lien de la note>", "page": "<lien de la page podcast>"}, "chapters": [{"title": "<titre du chapitre>", "paragraphs": ["<paragraphe>", "…"]}]}
Les paragraphes sont exactement ceux du script oral. Si add_repo ou le push échoue, continue et indique la raison exacte dans le message final.

## Règles
- Aucun fait sans source consultée aujourd'hui ; analyses attribuées ; chiffres incertains signalés.
- Paraphrase : pas de citation de plus de quelques mots, une seule par source au maximum.

## Fin
Envoie à l'utilisateur, avec SendUserMessage, un message court : le titre de l'édition, les sujets du jour en une ligne chacun, ce qui manque éventuellement (matinales ou auditions non vérifiées, MP3 non déclenché). Précise que l'épisode audio arrive dans AntennaPod une dizaine de minutes après. N'y colle pas d'URL : les cartes des pages les affichent.
