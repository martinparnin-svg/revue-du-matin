"""Fabrique les épisodes MP3 à partir des scripts déposés dans episodes/AAAA-MM-JJ.json.

Format attendu du JSON :
{
  "date": "2026-10-14",
  "title": "Revue du matin · 14 octobre 2026",
  "summary": "Les sujets du jour en une ou deux phrases.",
  "links": {"note": "https://...", "page": "https://..."},
  "style": "consigne de ton pour la voix (facultatif, remplace celle de config.yml)",
  "chapters": [{"title": "…", "voice": "Charon (facultatif)", "paragraphs": ["…", "…"]},
               {"title": "Le débat", "segments": [{"voice": "Algieba", "text": "…"}, {"voice": "Kore", "text": "…"}]}]
}
Épisodes : episodes/AAAA-MM-JJ.json (le matin) et episodes/AAAA-MM-JJ-soir.json (l'émission du soir, dialoguée).
Le MP3 porte le même nom que le script : docs/audio/AAAA-MM-JJ.mp3, docs/audio/AAAA-MM-JJ-flash.mp3.

Usage : python scripts/build_episode.py            (épisodes pas encore fabriqués)
        python scripts/build_episode.py --test FICHIER.json  (essai hors flux, publié dans docs/tests/)
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
    for name in ("intro", "transition", "outro"):
        to_wav(os.path.join(j, f"jingle_{name}.mp3"), os.path.join(tmp, f"j_{name}.wav"))
    silence(a["pause_between_paragraphs_ms"], os.path.join(tmp, "gap.wav"))
    silence(900, os.path.join(tmp, "gap_long.wav"))

    add(os.path.join(tmp, "j_intro.wav"))
    n = 0
    for ci, ch in enumerate(ep["chapters"]):
        if ci > 0:
            add(os.path.join(tmp, "j_transition.wav"))
        # Un chapitre est soit lu d'une seule voix ("paragraphs"), soit dialogué ("segments" :
        # répliques successives, chacune avec sa voix, sans jingle entre elles).
        if ch.get("segments"):
            parts_ch = [(seg.get("voice"), [seg["text"]]) for seg in ch["segments"] if seg.get("text", "").strip()]
        else:
            parts_ch = [(ch.get("voice"), ch["paragraphs"])]
        for seg_voice, paras in parts_ch:
            voice = (seg_voice or "").strip().capitalize() or None
            for block in chunks(paras):
                n += 1
                raw = os.path.join(tmp, f"tts_{n:03d}.audio")
                print(f"  synthèse {n} ({len(block)} caractères) — {ch['title']}" + (f" — voix {voice}" if voice else ""), flush=True)
                try:
                    synthesize(block, cfg, raw, voice)
                except TTSError as exc:
                    if not voice:
                        raise
                    # voix refusée : on bascule sur la voix par défaut plutôt que de perdre l'épisode
                    print(f"::warning title=Voix {voice}::{exc} — passage lu avec la voix par défaut", flush=True)
                    synthesize(block, cfg, raw, None)
                wav = os.path.join(tmp, f"tts_{n:03d}.wav")
                to_wav(raw, wav)
                add(wav)
                add(os.path.join(tmp, "gap.wav"))
    add(os.path.join(tmp, "gap_long.wav"))
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


def main():
    cfg = yaml.safe_load(open(os.path.join(ROOT, "config.yml"), encoding="utf-8"))
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
