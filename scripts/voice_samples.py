"""Fabrique un court extrait avec plusieurs voix Gemini pour choisir celle qui plaît le plus.
Les extraits sont publiés dans docs/samples/ et listés sur docs/samples/index.html.
"""
import copy
import os
import subprocess
import sys

import yaml

sys.path.insert(0, os.path.dirname(__file__))
from tts import synthesize  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = ("Bonjour, nous sommes le mardi 13 octobre, et voici votre revue du matin. "
        "Au sommaire : l'accord pétrolier entre Washington et Moscou, le budget 2027 qui arrive à l'Assemblée, "
        "et le premier grand modèle d'intelligence artificielle de Meta. C'est parti.")
VOICES = ["Sulafat", "Achird", "Charon", "Algieba", "Gacrux", "Vindemiatrix", "Sadaltager", "Kore"]

cfg = yaml.safe_load(open(os.path.join(ROOT, "config.yml"), encoding="utf-8"))
out_dir = os.path.join(ROOT, "docs", "samples")
os.makedirs(out_dir, exist_ok=True)
rows = []
for v in VOICES:
    c = copy.deepcopy(cfg)
    c["voice"]["provider"] = "gemini"
    c["voice"]["gemini"]["voice"] = v
    raw = os.path.join(out_dir, f"{v}.audio")
    print("Voix", v, flush=True)
    synthesize(TEXT, c, raw)
    subprocess.run(["ffmpeg", "-y", "-i", raw, "-b:a", "96k", os.path.join(out_dir, f"{v}.mp3")],
                   check=True, capture_output=True)
    os.remove(raw)
    rows.append(f'<li><strong>{v}</strong><br><audio controls preload="none" src="{v}.mp3"></audio></li>')

html = f"""<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Choix de la voix</title>
<style>body{{font-family:system-ui,sans-serif;max-width:640px;margin:2rem auto;padding:0 16px;line-height:1.5}}
li{{margin:0 0 1.2rem}}audio{{width:100%;margin-top:.3rem}}</style>
<h1>Choix de la voix</h1><p>Même texte, lu par huit voix Gemini. Notez celle que vous préférez.</p>
<ul style="list-style:none;padding:0">{''.join(rows)}</ul>"""
open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(html)
print("Extraits prêts")
