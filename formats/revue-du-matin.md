# Format : Revue du matin

Podcast quotidien de veille d'un candidat aux concours de la haute fonction publique (INSP…).
Exemple : `exemples/revue-du-matin.json`. Reprise adaptée de
`reference/consignes-tache-quotidienne-v1-une-voix.md` (version d'origine).

## Calendrier et durée

- **Du mardi au vendredi** : 3 000 à 3 200 mots (18 à 19 min de voix ; jamais plus de 3 300 mots).
  Actualité des dernières 24 à 36 heures.
- **Le lundi, « Édition spéciale du lundi »** : 4 500 à 4 800 mots (jamais plus de 4 900), du
  vendredi soir au lundi matin, avec un chapitre final « La semaine qui vient » (agenda
  parlementaire, rendez-vous européens et internationaux, publications économiques attendues).
- Produit aussi les jours fériés. À publier avant 7 h 50, heure de Paris. Repère : 165 mots par minute.
- Vérifier la date et le jour (`TZ=Europe/Paris date`) avant d'écrire.

## Structure (un chapitre par bloc, 3 000 caractères au plus par chapitre)

1. Ouverture et sommaire (court).
2. International : deux sujets.
3. Politique française et grands sujets nationaux, environ 5 minutes : vie politique et
   parlementaire, au moins un sujet social et un sujet environnemental quand l'actualité s'y prête.
4. Économie et finances publiques.
5. Industrie.
6. Tech et IA.
7. Agenda parlementaire du jour, bref.
8. Trois pistes pour les épreuves, puis au revoir.

Le lundi : même structure en plus ample, puis « La semaine qui vient » avant les pistes.

## Exigence de qualité : la grille d'analyse

6 à 8 sujets en semaine, 9 à 12 le lundi, chacun traité à fond plutôt que d'en multiplier le nombre.
Pour chaque sujet : les faits (qui, quand, chiffres exacts) ; le contexte et l'historique ; les
acteurs et leurs positions ; les nuances (ce que cela change et ne change pas) ; l'impact réel,
chiffré ; ce qu'il faut surveiller. Au moins deux sources par sujet principal, dont une d'analyse.

## Sources

- Générales : fr.euronews.com, connaissancedesenergies.org/afp (dépêches AFP), publicsenat.fr,
  legrandcontinent.eu/fr, techcrunch.com (IA), sites officiels (info.gouv.fr, INSEE, DARES,
  Banque de France, Cour des comptes, Commission européenne, FMI).
- Auditions : agendas des commissions du Sénat (senat.fr/aglae) et de l'Assemblée nationale
  (agendas et fichiers ICS des réunions ; heures en UTC).
- Sites qui refusent la lecture automatique : ne pas insister ni contourner (lemonde.fr,
  lesechos.fr, franceinfo.fr, radiofrance.fr, reuters.com, apnews.com, bbc.com, theguardian.com).
- Ne jamais inventer un nom : sinon dire « non vérifié ».

## Style

Podcast de radio publique de qualité : ton chaleureux et vivant, transitions naturelles
(« Restons en Europe… », « Changement de décor… »), attributions à l'oral, équilibre politique.
Voix : `Marie`. Titre : « Revue du matin · <jour> <mois> <année> ».

## Livraison

`episodes/AAAA-MM-JJ.json`, `links` facultatif. Une note de veille écrite peut être déposée dans
`notes/AAAA-MM-JJ.md` (conversion en Word : workflow « Envoyer la note de veille », lancé à la main).
