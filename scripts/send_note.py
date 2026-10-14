"""Convertit la note de veille (notes/AAAA-MM-JJ.md) en Word et l'envoie par courriel.

Usage : python scripts/send_note.py [AAAA-MM-JJ]   (par défaut : la note la plus récente)
Secrets (variables d'environnement) : GMAIL_USER, GMAIL_APP_PASSWORD, MAIL_TO
Sans secrets, le fichier Word est seulement fabriqué (docs/notes/), sans envoi.
"""
import glob
import os
import re
import smtplib
import subprocess
import sys
from email.message import EmailMessage
from email.utils import formatdate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]


def build_docx(md_path):
    date = os.path.basename(md_path)[:-3]
    out_dir = os.path.join(ROOT, "build")
    os.makedirs(out_dir, exist_ok=True)
    y, m, d = (int(x) for x in date.split("-"))
    nom = f"Note de veille {d:02d}-{m:02d}-{y}.docx"
    out = os.path.join(out_dir, nom)
    subprocess.run(["pandoc", md_path, "-f", "gfm", "-o", out,
                    "--reference-doc", os.path.join(ROOT, "assets", "note-reference.docx"),
                    "-M", "lang=fr-FR"], check=True)
    style_tables(out)
    return date, out, f"{d} {MOIS[m - 1]} {y}"


def style_tables(path):
    """Tableaux pleine largeur, bordures fines, ligne d'en-tête colorée et en gras."""
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import RGBColor

    doc = Document(path)
    for t in doc.tables:
        tblPr = t._tbl.tblPr
        for tag in ("w:tblW", "w:tblBorders", "w:tblLayout"):
            for el in tblPr.findall(qn(tag)):
                tblPr.remove(el)
        w = OxmlElement("w:tblW")
        w.set(qn("w:w"), "5000")
        w.set(qn("w:type"), "pct")
        tblPr.append(w)
        borders = OxmlElement("w:tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            b = OxmlElement(f"w:{side}")
            b.set(qn("w:val"), "single")
            b.set(qn("w:sz"), "4")
            b.set(qn("w:color"), "B8C2D0")
            borders.append(b)
        tblPr.append(borders)
        for i, row in enumerate(t.rows):
            for cell in row.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                mar = OxmlElement("w:tcMar")
                for side in ("top", "bottom", "left", "right"):
                    m = OxmlElement(f"w:{side}")
                    m.set(qn("w:w"), "60" if side in ("top", "bottom") else "90")
                    m.set(qn("w:type"), "dxa")
                    mar.append(m)
                tcPr.append(mar)
                if i == 0:
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:color"), "auto")
                    shd.set(qn("w:fill"), "E3E8F4")
                    tcPr.append(shd)
                    for p in cell.paragraphs:
                        for r in p.runs:
                            r.font.bold = True
                            r.font.color.rgb = RGBColor(0x00, 0x00, 0x91)
    doc.save(path)


def first_lines(md_path, n=8):
    """Reprend la synthèse (liste numérotée qui suit « Synthèse ») pour le corps du courriel."""
    txt = open(md_path, encoding="utf-8").read()
    m = re.search(r"#+\s*Synthèse\s*\n(.*?)(\n#|\Z)", txt, re.S)
    block = m.group(1) if m else ""
    items = [re.sub(r"[*_`]|\[(.*?)\]\(.*?\)", r"\1", l).strip() for l in block.splitlines() if re.match(r"\s*\d+[.)]\s", l)]
    return items[:n]


def send(date, docx_path, date_fr, md_path):
    user, pwd, to = (os.environ.get(k, "").strip() for k in ("GMAIL_USER", "GMAIL_APP_PASSWORD", "MAIL_TO"))
    if not (user and pwd and to):
        print("::warning title=Courriel::secrets GMAIL_USER / GMAIL_APP_PASSWORD / MAIL_TO absents : pas d'envoi")
        return False
    msg = EmailMessage()
    msg["Subject"] = f"Note de veille · {date_fr}"
    msg["From"] = f"Revue du matin <{user}>"
    msg["To"] = to
    msg["Date"] = formatdate(localtime=True)
    synth = first_lines(md_path)
    body = [f"Bonjour,", "", f"Veuillez trouver ci-joint la note de veille du {date_fr}."]
    if synth:
        body += ["", "Synthèse :"] + [f"  {s}" for s in synth]
    body += ["", "L'épisode audio du jour est disponible dans votre application de podcasts.", "", "Revue du matin"]
    msg.set_content("\n".join(body))
    with open(docx_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application",
                           subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
                           filename=os.path.basename(docx_path))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as s:
        s.login(user, pwd)
        s.send_message(msg)
    print(f"Courriel envoyé : {msg['Subject']} ({os.path.getsize(docx_path)} octets)")
    return True


def main():
    if len(sys.argv) > 1 and sys.argv[1]:
        md = os.path.join(ROOT, "notes", f"{sys.argv[1]}.md")
    else:
        notes = sorted(glob.glob(os.path.join(ROOT, "notes", "*.md")))
        if not notes:
            print("Aucune note à envoyer.")
            return
        md = notes[-1]
    if not os.path.exists(md):
        print(f"::error title=Note::{md} introuvable")
        sys.exit(1)
    date, docx_path, date_fr = build_docx(md)
    print("Word prêt :", docx_path)
    send(date, docx_path, date_fr, md)


if __name__ == "__main__":
    main()
