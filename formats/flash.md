# Format : Flash

Bulletin court et rythmé : les titres de l'actualité, ou une révision express avant une échéance.
Exemples : `exemples/flash.json` (format actualité), `episodes/2026-11-03-g7-flash.json` (révision).

- 500 à 900 mots, 3 à 6 minutes. Une voix (`Marie`), ou un dialogue court pour une révision.
- Actualité : « Bonjour, il est sept heures cinquante, voici le flash… », 4 à 6 titres, une à trois
  phrases chacun, puis renvoi vers l'émission complète.
- Révision : les dates et chiffres à retenir, une structure à mémoriser, trois réflexes.
- Champ `style` (Gemini uniquement) : `"brisk, crisp radio news bulletin anchor, clear and energetic, steady fast pace"`.

Livraison : `episodes/AAAA-MM-JJ-flash.json` pour le flux, ou `creations/<nom>.json` hors flux.
