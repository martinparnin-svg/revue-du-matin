"""Reconstitue episodes/AAAA-MM-JJ.json à partir de la page podcast publiée (filet de sécurité).

Usage : python3 -I tools/page_vers_episode.py <page.html> <AAAA-MM-JJ> <url de la page>
Ne garde que le texte lu à l'antenne : les <p> des <article class="chap">, sans les mentions techniques.
"""
import html, json, os, re, sys
from html.parser import HTMLParser

TECH = ("Script produit", "Sur Android")


class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.chaps = []; s.inp = False; s.buf = ""; s.links = []; s.inart = False
    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag == "article" and "chap" in (a.get("class") or ""):
            s.chaps.append({"title": html.unescape(a.get("data-title", "")), "voice": "Algieba", "paragraphs": []}); s.inart = True
        if tag == "p" and s.inart:
            s.inp = True; s.buf = ""
        if tag == "a" and a.get("href"):
            s.links.append(a["href"])
    def handle_endtag(s, tag):
        if tag == "p" and s.inp:
            t = " ".join(s.buf.split())
            if t and not t.startswith(TECH):
                s.chaps[-1]["paragraphs"].append(t)
            s.inp = False
        if tag == "article":
            s.inart = False
    def handle_data(s, d):
        if s.inp:
            s.buf += d


src_path, date, page_url = sys.argv[1:4]
src = open(src_path, encoding="utf-8").read()
p = P(); p.feed(src)
title = html.unescape(re.search(r"<title>(.*?)</title>", src, re.S).group(1).strip())
page_id = page_url.rstrip("/").split("/")[-1]
note = next((l for l in p.links if "artifact" in l and page_id not in l), "")
chaps = [c for c in p.chaps if c["paragraphs"]]
mid = [c["title"] for c in chaps if c["title"] not in ("Ouverture", "Le tour de l'actu", "Aujourd'hui", "La semaine qui vient", "Pour la copie")]
ep = {"date": date, "title": title, "summary": "Au programme : " + " ; ".join(mid) + ".",
      "links": {"note": note, "page": page_url}, "chapters": chaps}
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "episodes", f"{date}.json")
json.dump(ep, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
words = sum(len(x.split()) for c in chaps for x in c["paragraphs"])
print(f"{out} : {len(chaps)} chapitres, {words} mots, note={note}")
for c in chaps:
    print(" -", c["title"], sum(len(x) for x in c["paragraphs"]), "car.")
print("Dernier paragraphe :", chaps[-1]["paragraphs"][-1])
