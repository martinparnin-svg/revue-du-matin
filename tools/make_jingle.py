"""Jingles de la « Revue du matin », version 2 : esprit matinale d'information.
Pulsation de synthé en doubles croches, batterie sèche, montée de bruit, impact final.
Composition originale, synthèse pure (aucun échantillon externe).

Usage : python tools/make_jingle.py assets/
"""
import os
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
BPM = 128
B = 60 / BPM          # une noire
S16 = B / 4           # une double croche
rng = np.random.default_rng(11)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def filt(x, kind, f):
    wn = np.clip(np.asarray(f, dtype=float) / (SR / 2), 1e-4, 0.99)
    b, a = butter(2, wn if wn.ndim else float(wn), btype=kind)
    return lfilter(b, a, x)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def saw(freq, t, n=14):
    return sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, n + 1))


# --- instruments -------------------------------------------------------------

def pluck(m, dur=0.22, vel=1.0, bright=1.0):
    """Synthé « pluck » : harmoniques aiguës qui s'éteignent plus vite (filtre qui se referme)."""
    t = t_axis(dur)
    f = midi(m)
    sig = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (10 + 9 * k / bright)) for k in range(1, 16))
    return vel * sig * np.minimum(1, t / 0.002)


def stab(notes, dur=0.9, vel=1.0):
    """Accord cuivré bref et brillant (attaque franche, déclin)."""
    t = t_axis(dur)
    sig = np.zeros_like(t)
    for m in notes:
        for det in (-0.08, 0.08):
            f = midi(m) * 2 ** (det / 12)
            sig += sum(np.sin(2 * np.pi * f * k * t + k) / k * np.exp(-t * (2.2 + 0.9 * k)) for k in range(1, 12))
    env = np.minimum(1, t / 0.008) * np.exp(-t * 1.6)
    return vel * sig * env / len(notes)


def lead(m, dur, vel=1.0):
    """Ligne d'accroche : synthé chaud légèrement saturé, petit vibrato."""
    t = t_axis(dur)
    f = midi(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.2))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = sum(np.sin(k * ph) / k for k in range(1, 9))
    sig = np.tanh(1.6 * sig)
    env = np.minimum(1, t / 0.012) * np.where(t < dur - 0.05, 1.0, np.maximum(0, (dur - t) / 0.05)) * (0.75 + 0.25 * np.exp(-t * 6))
    return vel * filt(sig, "low", 3800) * env


def bass(m, dur, vel=1.0):
    t = t_axis(dur)
    f = midi(m)
    sig = np.tanh(1.8 * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)))
    return vel * sig * np.minimum(1, t / 0.004) * np.exp(-t * 3.5)


def kick(vel=1.0):
    t = t_axis(0.38)
    f = 45 + 120 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    click = rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.25
    return vel * (np.tanh(2.2 * np.sin(ph)) * np.exp(-t * 7) + click)


def clap(vel=1.0):
    t = t_axis(0.25)
    n = filt(rng.standard_normal(len(t)), "band", [900, 4500])
    env = np.zeros_like(t)
    for off in (0, 0.009, 0.018):
        env += np.where(t >= off, np.exp(-(t - off) * 55), 0)
    env += np.exp(-t * 14) * 0.35
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.4
    return vel * (n * env + body)


def hat(vel=1.0, open_=False):
    t = t_axis(0.25 if open_ else 0.06)
    n = filt(rng.standard_normal(len(t)), "high", 7000)
    return vel * n * np.exp(-t * (14 if open_ else 70))


def crash(vel=1.0, dur=1.8):
    t = t_axis(dur)
    n = filt(rng.standard_normal(len(t)), "high", 4500)
    return vel * n * np.exp(-t * 2.6) * np.minimum(1, t / 0.003)


def boom(vel=1.0, dur=1.4):
    t = t_axis(dur)
    f = 38 + 30 * np.exp(-t * 6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return vel * np.sin(ph) * np.exp(-t * 2.4) * np.minimum(1, t / 0.005)


def riser(dur, vel=1.0):
    """Montée : bruit dont le filtre s'ouvre + glissando ascendant."""
    t = t_axis(dur)
    x = t / dur
    noise = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    seg = int(0.02 * SR)
    for i in range(0, len(t), seg):  # filtre passe-bande glissant par petits segments
        c = 400 + 9000 * (i / len(t)) ** 2
        out[i:i + seg] = filt(noise[i:i + seg + 200], "band", [c * 0.6, min(c * 1.6, 20000)])[: len(out[i:i + seg])]
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1400 * x ** 2) / SR) * 0.25
    return vel * (out * 0.8 + sweep) * x ** 2.2


# --- table de mixage ---------------------------------------------------------

class Mix:
    def __init__(self, seconds):
        n = int(seconds * SR)
        self.L, self.R = np.zeros(n), np.zeros(n)

    def add(self, sig, at, pan=0.0, gain=1.0):
        i = int(at * SR)
        if i >= len(self.L):
            return
        j = min(len(self.L), i + len(sig))
        s = sig[: j - i] * gain
        self.L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414
        self.R[i:j] += s * np.sqrt((1 + pan) / 2) * 1.414

    def room(self, mix=0.12):
        for d, g in ((0.023, 0.5), (0.041, 0.4), (0.067, 0.3), (0.101, 0.2)):
            k = int(d * SR)
            self.L[k:] += mix * g * self.R[:-k]
            self.R[k:] += mix * g * self.L[:-k]

    def fade(self, secs):
        n = int(secs * SR)
        f = np.linspace(1, 0, n) ** 2
        self.L[-n:] *= f
        self.R[-n:] *= f

    def write(self, path):
        st = np.stack([self.L, self.R], axis=1)
        st = np.tanh(1.3 * st / (np.max(np.abs(st)) + 1e-9)) / np.tanh(1.3)  # léger « glue »
        pcm = (st * 0.92 * 32767).astype(np.int16)
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())


# Harmonie : ré mineur → si bémol → fa → do (tension), résolution sur ré (accord avec 9e)
PULSE = [(50, 62), (46, 58), (41, 53), (48, 60)]   # (basse, note de pulsation) par demi-mesure
HOOK = [(74, 0.0, 0.5), (77, 0.5, 0.5), (81, 1.0, 0.75), (79, 1.75, 0.25), (81, 2.0, 1.0)]  # ré fa la sol la


def groove(mx, t0, beats, hats=True, claps=True):
    for q in range(beats):
        mx.add(kick(0.55), t0 + q * B)
        if claps and q % 2 == 1:
            mx.add(clap(0.45), t0 + q * B, pan=0.05)
        if hats:
            mx.add(hat(0.18), t0 + q * B + B / 2, pan=0.4)
            mx.add(hat(0.08), t0 + q * B + B / 4, pan=0.4)


def pulse_bar(mx, t0, beats=8):
    """Pulsation de doubles croches qui change d'accord toutes les deux noires."""
    for s in range(beats * 4):
        bass_n, p = PULSE[(s // 8) % 4]
        accent = 1.0 if s % 4 == 0 else 0.6
        mx.add(pluck(p + (12 if s % 8 == 6 else 0), 0.2, 0.55 * accent, bright=0.7 + 0.5 * s / (beats * 4)),
               t0 + s * S16, pan=-0.25 if s % 2 else 0.25)
        if s % 8 == 0:
            mx.add(bass(bass_n - 12, 2 * B, 0.55), t0 + s * S16)


def intro(path):
    hit = 8 * B                       # impact après deux mesures
    mx = Mix(hit + 2.0)
    pulse_bar(mx, 0, 8)
    groove(mx, B * 2, 6, hats=True, claps=True)
    mx.add(kick(0.7), 0)
    for m, beat, d in HOOK:          # accroche sur la 2e mesure
        mx.add(lead(m, d * B, 0.42), 4 * B + beat * B)
    mx.add(riser(2 * B, 0.5), hit - 2 * B)
    mx.add(stab([62, 65, 69, 72, 76], 1.6, 1.6), hit)          # ré mineur add9, éclatant
    mx.add(lead(86, 1.3, 0.35), hit, pan=0.1)
    mx.add(boom(1.0), hit)
    mx.add(kick(1.0), hit)
    mx.add(crash(0.35), hit, pan=0.2)
    mx.room(0.12)
    mx.fade(0.9)
    mx.write(path)


def transition(path):
    mx = Mix(1.5)
    mx.add(riser(0.45, 0.45), 0)
    for i, m in enumerate((74, 77, 81)):
        mx.add(pluck(m, 0.25, 0.45, 1.2), 0.45 + i * S16, pan=-0.2 + 0.2 * i)
    hit = 0.45 + 3 * S16
    mx.add(stab([62, 69, 74, 76], 0.9, 0.7), hit)
    mx.add(kick(0.8), hit)
    mx.add(crash(0.2, 1.0), hit, pan=0.3)
    mx.room(0.12)
    mx.fade(0.5)
    mx.write(path)


def outro(path):
    hit = 4 * B
    mx = Mix(hit + 2.4)
    pulse_bar(mx, 0, 4)
    groove(mx, 0, 4)
    for m, beat, d in HOOK[:4]:
        mx.add(lead(m, d * B, 0.4), beat * B)
    mx.add(riser(B, 0.35), hit - B)
    mx.add(stab([50, 62, 66, 69, 76], 2.2, 1.6), hit)          # ré majeur : conclusion lumineuse
    mx.add(boom(0.9, 1.8), hit)
    mx.add(kick(0.9), hit)
    mx.add(crash(0.3, 2.2), hit)
    mx.room(0.14)
    mx.fade(1.6)
    mx.write(path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for name, fn in (("intro", intro), ("transition", transition), ("outro", outro)):
        wav = os.path.join(out, f"jingle_{name}.wav")
        fn(wav)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-af",
                        "loudnorm=I=-15:TP=-1.0:LRA=9", "-ar", "44100", "-b:a", "160k",
                        os.path.join(out, f"jingle_{name}.mp3")], check=True)
        os.remove(wav)
    print("ok")
