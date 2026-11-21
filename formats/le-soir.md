# Format : Le soir

Émission dialoguée qui prend **un seul sujet** du jour et le creuse : une animatrice pose les
questions, une experte présente les arguments en présence sans prendre parti.
Exemple : `exemples/le-soir.json` (20 novembre 2026, Royaume-Uni et Union européenne).

## Durée et voix

- 3 000 à 3 300 mots, environ 18 à 20 minutes. Publication vers 17 h 30, heure de Paris.
- `Marie` : animatrice. Questions courtes, relances, transitions.
- `Lea` : experte. Réponses développées, 500 à 900 caractères par réplique.
- Chaque chapitre est une suite de `segments` qui alternent les deux voix. `{"pause": 6}` laisse
  six secondes de réflexion à l'auditeur, par exemple avant une question de copie.

## Structure

1. **Ouverture** : accueil, rappel que les voix sont des voix de synthèse et que l'experte présente
   les arguments sans prendre parti, puis l'enjeu du jour en une question.
2. **Le récit** : comment on en est arrivé là, les dates et les chiffres.
3. **Le débat** : les arguments de chaque camp, attribués, puis ce qui reste incertain.
4. **Ailleurs** : comparaison avec d'autres pays ou précédents.
5. **Pour votre copie** : problématique, plan possible, références à citer.
6. **Au revoir** : la phrase à retenir, puis l'annonce du rendez-vous suivant.

## Livraison

`episodes/AAAA-MM-JJ-soir.json`. Titre : « Le soir · <sujet> · <jour> <mois> ». Le résumé
(`summary`) pose la question de l'émission.
