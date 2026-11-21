"""Fabrique les épisodes MP3 à partir des scripts déposés dans episodes/AAAA-MM-JJ.json.

Format attendu du JSON :
{
  "date": "2026-10-14",
  "title": "Revue du matin · 14 octobre 2026",
  "summary": "Les sujets du jour en une ou deux phrases.",
  "links": {"note": "https://...", "page": "https://..."},   (facultatif)
  "style": "consigne de ton pour la voix (facultatif, remplace celle de config.yml ; Gemini uniquement)",
  "jingles": true,   (facultatif, false = ni générique ni transitions, pour une lecture ou une création courte)
  "chapters": [{"title": "…", "voice": "Charon (facultatif)", "paragraphs": ["…", "…"]},
               {"title": "Le débat", "segments": [{"voice": "Algieba", "text": "…"}, {"voice": "Kore", "text": "…"}]}]
}
Épisodes : episodes/AAAA-MM-JJ.json (le matin) et episodes/AAAA-MM-JJ-soir.json (l'émission du soir, dialoguée).
Le MP3 porte le même nom que le script : docs/audio/AAAA-MM-JJ.mp3, docs/audio/AAAA-MM-JJ-flash.mp3.

Créations hors flux : creations/<nom>.json (même format), publiées dans docs/creations/<nom>.mp3,
sans entrer dans le flux podcast. Les modèles d'écriture sont dans formats/.

Usage : python scripts/build_episode.py            (épisodes pas encore fabriqués)
        python scripts/build_episode.py --test FICHIER.json  (essai hors flux, publié dans docs/tests/)
        python scripts/build_episode.py --creations          (créations pas encore fabriquées)
        python scripts/build_episode.py --creation NOM       (refabrique creations/NOM.json)
        python scripts/build_episode.py 2026-10-14 (refabrique cet épisode)
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import copy
import tempfile

import yaml

sys.path.insert(0, os.path.dirname(__file__))
from tts import synthesize, TTSError  # noqa: E402
from feed import write_feed  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, "docs", "audio")
CREATIONS_SRC = os.path.join(ROOT, "creations")
CREATIONS_OUT = os.path.join(ROOT, "docs", "creations")
MAX_CHARS = 3200  # taille maximale d'un appel de synthèse (≈ 3 à 4 min d'audio)


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def to_wav(src, dst):
    """Normalise n'importe quel fichier audio en WAV 44,1 kHz stéréo pour l'assemblage."""
    run(["ffmpeg", "-y", "-i", src, "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", dst])


def silence(ms, dst):
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{ms / 1000:.3f}",
         "-c:a", "pcm_s16le", dst])


def chunks(paragraphs):
    """Regroupe les paragraphes en blocs de taille raisonnable, sans couper une phrase."""
    out, cur = [], ""
    for p in paragraphs:
        p = " ".join(p.split())
        if cur and len(cur) + len(p) + 1 > MAX_CHARS:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        out.append(cur)
    return out


def build(ep_path, cfg, out_mp3=None):
    ep = json.load(open(ep_path, encoding="utf-8"))
    stem = os.path.basename(ep_path)[:-5]  # AAAA-MM-JJ ou AAAA-MM-JJ-flash
    if ep.get("style"):  # ton propre à cet épisode (ex. le flash, plus rythmé)
        cfg = copy.deepcopy(cfg)
        cfg["voice"]["gemini"]["style"] = ep["style"]
    os.makedirs(AUDIO_DIR, exist_ok=True)
    out_mp3 = out_mp3 or os.path.join(AUDIO_DIR, f"{stem}.mp3")
    os.makedirs(os.path.dirname(out_mp3), exist_ok=True)
    tmp = tempfile.mkdtemp()
    parts = []

    def add(path):
        parts.append(path)

    a = cfg["audio"]
    j = os.path.join(ROOT, "assets")
    jingles = ep.get("jingles", True)
    if jingles:
        for name in ("intro", "transition", "outro"):
            to_wav(os.path.join(j, f"jingle_{name}.mp3"), os.path.join(tmp, f"j_{name}.wav"))
    silence(a["pause_between_paragraphs_ms"], os.path.join(tmp, "gap.wav"))
    silence(900, os.path.join(tmp, "gap_long.wav"))

    if jingles:
        add(os.path.join(tmp, "j_intro.wav"))
    n = 0
    for ci, ch in enumerate(ep["chapters"]):
        if ci > 0:
            add(os.path.join(tmp, "j_transition.wav") if jingles else os.path.join(tmp, "gap_long.wav"))
        # Un chapitre est soit lu d'une seule voix ("paragraphs"), soit dialogué ("segments" :
        # répliques successives, chacune avec sa voix, sans jingle entre elles).
        # Un segment {"pause": 6} insère un silence de 6 secondes (temps de réflexion laissé à l'auditeur).
        if ch.get("segments"):
            parts_ch = []
            for seg in ch["segments"]:
                if seg.get("pause"):
                    parts_ch.append(("__pause__", float(seg["pause"]), None))
                elif seg.get("text", "").strip():
                    parts_ch.append((seg.get("voice"), [seg["text"]], seg.get("style")))
        else:
            parts_ch = [(ch.get("voice"), ch["paragraphs"], None)]
        for seg_voice, paras, seg_style in parts_ch:
            if seg_voice == "__pause__":
                n += 1
                pw = os.path.join(tmp, f"pause_{n:03d}.wav")
                silence(int(paras * 1000), pw)
                add(pw)
                continue
            # Le nom est gardé tel quel : les identifiants ElevenLabs sont sensibles à la casse.
            # Chaque service normalise lui-même (voir scripts/tts.py).
            voice = (seg_voice or "").strip() or None
            # un segment peut porter son propre ton (ex. passage en anglais lu avec un accent natif)
            cfg_seg = cfg
            if seg_style:
                cfg_seg = copy.deepcopy(cfg)
                cfg_seg["voice"]["gemini"]["style"] = seg_style
            for block in chunks(paras):
                n += 1
                raw = os.path.join(tmp, f"tts_{n:03d}.audio")
                print(f"  synthèse {n} ({len(block)} caractères) — {ch['title']}" + (f" — voix {voice}" if voice else ""), flush=True)
                try:
                    synthesize(block, cfg_seg, raw, voice)
                except TTSError as exc:
                    if not voice:
                        raise
                    # voix refusée : on bascule sur la voix par défaut plutôt que de perdre l'épisode
                    print(f"::warning title=Voix {voice}::{exc} — passage lu avec la voix par défaut", flush=True)
                    synthesize(block, cfg_seg, raw, None)
                wav = os.path.join(tmp, f"tts_{n:03d}.wav")
                to_wav(raw, wav)
                add(wav)
                add(os.path.join(tmp, "gap.wav"))
    add(os.path.join(tmp, "gap_long.wav"))
    if jingles:
        add(os.path.join(tmp, "j_outro.wav"))

    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    joined = os.path.join(tmp, "joined.wav")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    run(["ffmpeg", "-y", "-i", joined, "-af", f"loudnorm=I={a['target_lufs']}:TP=-1.5:LRA=11",
         "-ar", "44100", "-ac", "2", "-b:a", a["bitrate"],
         "-metadata", f"title={ep['title']}", "-metadata", f"artist={cfg['show']['author']}", out_mp3])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Épisode prêt : {out_mp3}")


def write_creations_index(cfg):
    """Page docs/creations/index.html : liste des créations publiées, la plus récente en haut."""
    from html import escape as h
    os.makedirs(CREATIONS_OUT, exist_ok=True)
    rows = []
    for mp3 in sorted(glob.glob(os.path.join(CREATIONS_OUT, "*.mp3")), key=os.path.getmtime, reverse=True):
        stem = os.path.basename(mp3)[:-4]
        src = os.path.join(CREATIONS_SRC, f"{stem}.json")
        meta = json.load(open(src, encoding="utf-8")) if os.path.exists(src) else {}
        rows.append(f'<li><a href="{h(stem)}.mp3">{h(meta.get("title", stem))}</a>'
                    f'<br><small>{h(meta.get("summary", ""))}</small></li>')
    page = ("<!doctype html><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\">"
            f"<title>Créations · {h(cfg['show']['title'])}</title>"
            "<body style=\"font-family:sans-serif;max-width:40rem;margin:2rem auto;padding:0 1rem\">"
            "<h1>Créations vocales</h1><ul>" + "".join(rows) + "</ul></body>")
    with open(os.path.join(CREATIONS_OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)


def build_creations(cfg, names=None):
    """Fabrique les créations hors flux : toutes celles sans MP3, ou celles nommées."""
    srcs = sorted(glob.glob(os.path.join(CREATIONS_SRC, "*.json")))
    if names:
        wanted = {os.path.basename(n)[:-5] if n.endswith(".json") else os.path.basename(n) for n in names}
        todo = [s for s in srcs if os.path.basename(s)[:-5] in wanted]
        missing = wanted - {os.path.basename(s)[:-5] for s in todo}
        for m in sorted(missing):
            print(f"::error title=Création introuvable::creations/{m}.json", flush=True)
    else:
        todo = [s for s in srcs if not os.path.exists(
            os.path.join(CREATIONS_OUT, os.path.basename(s).replace(".json", ".mp3")))]
    failed = bool(names and missing)
    for src in todo:
        stem = os.path.basename(src)[:-5]
        print(f"Fabrication de la création {stem}")
        try:
            build(src, cfg, os.path.join(CREATIONS_OUT, f"{stem}.mp3"))
        except Exception as exc:
            print(f"::error title=Échec de {stem}::{exc}", flush=True)
            failed = True
    write_creations_index(cfg)
    if failed:
        sys.exit(1)


def main():
    cfg = yaml.safe_load(open(os.path.join(ROOT, "config.yml"), encoding="utf-8"))
    global MAX_CHARS
    MAX_CHARS = cfg["voice"].get(cfg["voice"]["provider"], {}).get("max_chars", MAX_CHARS)
    if len(sys.argv) > 1 and sys.argv[1] in ("--creations", "--creation"):
        build_creations(cfg, sys.argv[2:] if sys.argv[1] == "--creation" else None)
        return
    if len(sys.argv) > 2 and sys.argv[1] == "--test":
        src = sys.argv[2] if os.path.isabs(sys.argv[2]) else os.path.join(ROOT, sys.argv[2])
        out = os.path.join(ROOT, "docs", "tests", os.path.basename(src).replace(".json", ".mp3"))
        print(f"Essai hors flux : {os.path.basename(src)}")
        build(src, cfg, out)
        return
    eps = sorted(glob.glob(os.path.join(ROOT, "episodes", "*.json")))
    if len(sys.argv) > 1:
        # « 2026-10-15 » refabrique tous les épisodes du jour ; « 2026-10-15-soir » celui du soir seul
        todo = []
        for d in sys.argv[1:]:
            todo += [e for e in eps if os.path.basename(e)[:-5] == d or os.path.basename(e).startswith(d + "-")]
    else:
        todo = [e for e in eps if not os.path.exists(
            os.path.join(AUDIO_DIR, os.path.basename(e).replace(".json", ".mp3")))]
    failed = False
    for e in todo:
        print(f"Fabrication de {os.path.basename(e)}")
        try:
            build(e, cfg)
        except Exception as exc:  # message visible dans le résumé du run
            print(f"::error title=Échec de {os.path.basename(e)}::{exc}", flush=True)
            failed = True
    write_feed(cfg, ROOT)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
