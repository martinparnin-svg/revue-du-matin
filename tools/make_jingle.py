"""Jingle original de la « Revue du matin » : intro, transition, fin.
Synthèse additive pure (aucun échantillon externe) -> WAV 44,1 kHz stéréo.
"""
import numpy as np
import wave, sys, os

SR = 44100
BPM = 108
BEAT = 60 / BPM
rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a, d, s, r, sr=SR):
    a_n, d_n, r_n = int(a * sr), int(d * sr), int(r * sr)
    s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([
        np.linspace(0, 1, a_n, endpoint=False),
        np.linspace(1, s, d_n, endpoint=False),
        np.full(s_n, s),
        np.linspace(s, 0, r_n),
    ])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def onepole_lp(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def mallet(freq, dur, vel=1.0):
    """Timbre de vibraphone/marimba doux : partiels 1, 4, 9.8 avec déclins différents."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    trem = 1 + 0.06 * np.sin(2 * np.pi * 5.2 * t)
    sig = (np.sin(2 * np.pi * freq * t) * np.exp(-t * 2.2) * trem
           + 0.35 * np.sin(2 * np.pi * freq * 4.0 * t) * np.exp(-t * 9)
           + 0.12 * np.sin(2 * np.pi * freq * 9.8 * t) * np.exp(-t * 22))
    attack = np.minimum(1, t / 0.004)
    return vel * sig * attack


def bell(freq, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    partials = [(1, 1, 1.4), (2.76, 0.5, 2.5), (5.4, 0.25, 4), (8.93, 0.12, 7)]
    sig = sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t * d) for r, a, d in partials)
    return vel * sig * np.minimum(1, t / 0.002)


def pad(notes, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for m in notes:
        f = midi(m)
        for det in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (det / 12)
            # dent de scie adoucie (8 harmoniques)
            sig += sum(np.sin(2 * np.pi * ff * k * t + rng.uniform(0, 6.28)) / k for k in range(1, 9))
    sig = onepole_lp(sig, 1400)
    sig = onepole_lp(sig, 2200)
    return vel * sig * env_adsr(n, 0.35, 0.4, 0.75, 0.6) / (len(notes) * 6)


def bass(m, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return vel * sig * env_adsr(n, 0.01, 0.25, 0.6, 0.15)


def kick(vel=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 35)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return vel * np.sin(ph) * np.exp(-t * 9)


def shaker(vel=1.0):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    hp = noise - onepole_lp(noise, 5000)
    return vel * hp * np.exp(-t * 45) * np.minimum(1, t / 0.008)


class Track:
    def __init__(self, seconds):
        self.L = np.zeros(int(seconds * SR))
        self.R = np.zeros(int(seconds * SR))

    def add(self, sig, at, pan=0.0, gain=1.0):
        i = int(at * SR)
        j = min(len(self.L), i + len(sig))
        s = sig[: j - i] * gain
        self.L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414
        self.R[i:j] += s * np.sqrt((1 + pan) / 2) * 1.414

    def reverb(self, mix=0.22):
        # petite réverbération : lignes de retard croisées
        for d, g in ((0.031, 0.5), (0.047, 0.42), (0.071, 0.35), (0.113, 0.28), (0.167, 0.2), (0.241, 0.14)):
            k = int(d * SR)
            self.L[k:] += mix * g * self.R[:-k]
            self.R[k:] += mix * g * self.L[:-k]

    def fade_out(self, secs):
        n = int(secs * SR)
        f = np.linspace(1, 0, n) ** 1.5
        self.L[-n:] *= f
        self.R[-n:] *= f

    def write(self, path):
        st = np.stack([self.L, self.R], axis=1)
        st /= np.max(np.abs(st)) + 1e-9
        st *= 0.89
        pcm = (st * 32767).astype(np.int16)
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())


# Motif signature : sol – do – ré – mi … sol (montée « lever du jour »)
MOTIF = [(67, 0.0), (72, 0.5), (74, 1.0), (76, 1.5), (79, 2.5)]
# Accords : Cmaj9 – Am9 – Fmaj7(#11) – G6sus → C(add9)
CHORDS = [([48, 55, 59, 62, 64], 36), ([45, 52, 55, 59, 60], 33), ([41, 48, 52, 57, 59], 29), ([43, 50, 55, 57, 62], 31)]


def intro(path):
    bars = 4
    tr = Track(bars * 4 * BEAT + 2.8)
    for b, (notes, root) in enumerate(CHORDS):
        t0 = b * 4 * BEAT
        tr.add(pad([n + 12 for n in notes[1:]], 4 * BEAT + 0.6, 0.9), t0, pan=0)
        tr.add(bass(root, 1.5 * BEAT, 0.55), t0)
        tr.add(bass(root, 0.9 * BEAT, 0.45), t0 + 2.5 * BEAT)
        for q in range(4):
            if b > 0 or q >= 2:
                tr.add(kick(0.5 if q % 2 == 0 else 0.3), t0 + q * BEAT)
        for e in range(8):
            if b > 0:
                tr.add(shaker(0.035 if e % 2 else 0.018), t0 + e * BEAT / 2, pan=0.35)
        # arpège de vibraphone
        arp = [notes[2] + 12, notes[3] + 12, notes[4] + 12, notes[3] + 12]
        for k, m in enumerate(arp):
            tr.add(mallet(midi(m), 1.4, 0.18), t0 + (k * 2 + 1) * BEAT / 2, pan=-0.3)
    # thème principal au vibraphone, sur les mesures 2 et 3
    for m, beat in MOTIF:
        tr.add(mallet(midi(m), 2.2, 0.55), 4 * BEAT + beat * BEAT, pan=0.1)
    for m, beat in MOTIF[:4]:
        tr.add(mallet(midi(m + 2), 2.0, 0.42), 8 * BEAT + beat * BEAT, pan=0.1)
    # résolution finale : accord + cloche
    tf = bars * 4 * BEAT
    tr.add(pad([60, 64, 67, 71, 74], 2.6, 1.0), tf)
    tr.add(bass(36, 2.2, 0.6), tf)
    tr.add(kick(0.55), tf)
    for m in (72, 76, 79, 84):
        tr.add(mallet(midi(m), 2.6, 0.32), tf + 0.02 * (m - 72) / 4)
    tr.add(bell(midi(91), 2.6, 0.22), tf + 0.08, pan=0.25)
    tr.reverb(0.25)
    tr.fade_out(1.6)
    tr.write(path)


def transition(path):
    tr = Track(2.6)
    for (m, beat), v in zip([(72, 0), (76, 0.5), (79, 1.0)], (0.5, 0.45, 0.6)):
        tr.add(mallet(midi(m), 2.0, v), beat * BEAT + 0.05, pan=-0.15 + beat * 0.2)
    tr.add(pad([60, 64, 67, 74], 2.2, 0.45), 0.0)
    tr.add(bell(midi(91), 1.8, 0.12), BEAT + 0.05, pan=0.3)
    tr.reverb(0.25)
    tr.fade_out(1.0)
    tr.write(path)


def outro(path):
    tr = Track(6.5)
    for m, beat in MOTIF:
        tr.add(mallet(midi(m), 2.4, 0.5), 0.1 + beat * BEAT, pan=0.1)
    tr.add(pad([53, 57, 60, 64], 4 * BEAT + 0.4, 0.8), 0)
    tr.add(bass(29, 3 * BEAT, 0.5), 0)
    tr.add(pad([48, 55, 59, 62, 64], 3.5, 0.9), 4 * BEAT)
    tr.add(bass(36, 2.5, 0.5), 4 * BEAT)
    tr.add(bell(midi(84), 3.0, 0.25), 4 * BEAT + 0.05)
    tr.reverb(0.3)
    tr.fade_out(2.5)
    tr.write(path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    intro(os.path.join(out, "jingle_intro.wav"))
    transition(os.path.join(out, "jingle_transition.wav"))
    outro(os.path.join(out, "jingle_outro.wav"))
    print("ok")
