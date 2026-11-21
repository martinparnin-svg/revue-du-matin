"""Vérifie un script avant de le déposer (épisode du flux ou création hors flux).

Usage : python scripts/valider.py episodes/2026-11-21.json [autres fichiers…]
        python scripts/valider.py creations/ma-chronique.json

Sortie : 0 si tout est bon (avertissements possibles), 1 s'il y a au moins une erreur.
À lancer AVANT chaque commit : une erreur ici, c'est un épisode raté chez GitHub Actions.
Aucune dépendance hors bibliothèque standard, à part PyYAML (déjà requis par le dépôt).
"""
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTS_PAR_MINUTE = 165          # débit moyen mesuré de la voix
MAX_CHAPITRE = 3000            # chapitre à une voix : au-delà, le découper en deux (consigne éditoriale)
RE_EPISODE = re.compile(r"^\d{4}-\d{2}-\d{2}(-[a-z0-9][a-z0-9-]*)?$")
RE_CREATION = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def voix_connues(cfg):
    """Noms de voix acceptés pour le service actif (None = pas de contrôle possible)."""
    v = cfg["voice"]
    provider = v["provider"]
    if provider == "mistral":
        return {k.lower() for k in v["mistral"].get("voices", {}) if k != "default"}
    return None


def verifier(path, cfg):
    erreurs, avert = [], []
    nom = os.path.basename(path)
    stem = nom[:-5] if nom.endswith(".json") else nom
    dossier = os.path.basename(os.path.dirname(os.path.abspath(path)))

    if not nom.endswith(".json"):
        erreurs.append("le fichier doit finir par .json")
    try:
        ep = json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [f"JSON illisible : {e}"], [], 0

    if dossier == "episodes":
        if not RE_EPISODE.match(stem):
            erreurs.append("nom attendu : AAAA-MM-JJ.json ou AAAA-MM-JJ-suffixe.json (ex. -soir)")
        if ep.get("date") != stem[:10]:
            erreurs.append(f"« date » ({ep.get('date')}) différente de la date du nom de fichier ({stem[:10]})")
    elif dossier == "creations":
        if not RE_CREATION.match(stem):
            erreurs.append("nom attendu : minuscules, chiffres et tirets (ex. chronique-energie.json)")
    else:
        avert.append(f"dossier « {dossier} » inhabituel : episodes/ (flux) ou creations/ (hors flux)")

    for cle in ("title", "chapters"):
        if not ep.get(cle):
            erreurs.append(f"champ « {cle} » manquant ou vide")
    if dossier == "episodes" and not ep.get("summary"):
        avert.append("champ « summary » vide : la description de l'épisode sera vide dans l'application")
    if "jingles" in ep and not isinstance(ep["jingles"], bool):
        erreurs.append("« jingles » doit valoir true ou false")

    connues = voix_connues(cfg)
    mots = 0
    for i, ch in enumerate(ep.get("chapters") or []):
        ou = f"chapitre {i + 1} « {ch.get('title', '?')} »"
        if not ch.get("title"):
            erreurs.append(f"chapitre {i + 1} sans titre")
        a_par, a_seg = bool(ch.get("paragraphs")), bool(ch.get("segments"))
        if a_par == a_seg:
            erreurs.append(f"{ou} : il faut soit « paragraphs » (une voix), soit « segments » (dialogue), pas les deux ni aucun")
            continue
        textes = []
        voix = []
        if a_par:
            textes = [p for p in ch["paragraphs"] if isinstance(p, str)]
            if len(textes) != len(ch["paragraphs"]) or not all(t.strip() for t in textes):
                erreurs.append(f"{ou} : chaque paragraphe doit être un texte non vide")
            voix.append(ch.get("voice"))
        else:
            for j, seg in enumerate(ch["segments"]):
                if "pause" in seg:
                    if not isinstance(seg["pause"], (int, float)) or not 0 < seg["pause"] <= 30:
                        erreurs.append(f"{ou}, segment {j + 1} : « pause » doit être un nombre de secondes (0 à 30)")
                    continue
                if not str(seg.get("text", "")).strip():
                    erreurs.append(f"{ou}, segment {j + 1} : texte vide")
                    continue
                textes.append(seg["text"])
                voix.append(seg.get("voice"))
        longueur = sum(len(t) for t in textes)
        if a_par and longueur > MAX_CHAPITRE:  # les dialogues sont découpés réplique par réplique
            avert.append(f"{ou} : {longueur} caractères (au-delà de {MAX_CHAPITRE}, découper en deux chapitres)")
        texte = " ".join(textes)
        mots += len(texte.split())
        if re.search(r"\[[^\]]*\]", texte):
            avert.append(f"{ou} : crochets trouvés (sources ?) ; ils seraient lus à voix haute")
        if re.search(r"https?://", texte):
            avert.append(f"{ou} : une adresse web serait lue à voix haute")
        if re.search(r"^\s*[-•*]\s", texte, re.M):
            avert.append(f"{ou} : liste à puces ; écrire des phrases pour l'oreille")
        if connues is not None:
            for v in voix:
                if v and v.lower() not in connues:
                    avert.append(f"{ou} : voix « {v} » inconnue de config.yml, lue avec la voix par défaut")
    return erreurs, avert, mots


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    cfg = yaml.safe_load(open(os.path.join(ROOT, "config.yml"), encoding="utf-8"))
    code = 0
    for path in sys.argv[1:]:
        erreurs, avert, mots = verifier(path, cfg)
        minutes = mots / MOTS_PAR_MINUTE
        etat = "ERREUR" if erreurs else "OK"
        print(f"{etat} {path} : {mots} mots, environ {minutes:.0f} min de voix")
        for e in erreurs:
            print(f"  erreur : {e}")
        for a in avert:
            print(f"  attention : {a}")
        if erreurs:
            code = 1
    sys.exit(code)


if __name__ == "__main__":
    main()
