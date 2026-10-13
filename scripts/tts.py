"""Synthèse vocale interchangeable.

Chaque service expose la même fonction : synthesize(text, cfg, out_path) -> écrit un fichier audio.
Pour changer de voix, modifier `voice.provider` dans config.yml et ajouter la clé
correspondante dans les secrets GitHub (GEMINI_API_KEY, ELEVENLABS_API_KEY ou GOOGLE_TTS_API_KEY).
"""
import base64
import json
import os
import time

import requests


class TTSError(RuntimeError):
    pass


def _post_with_retry(url, headers, body, tries=6, wait=20):
    last = None
    for attempt in range(tries):
        r = requests.post(url, headers=headers, data=json.dumps(body), timeout=300)
        if r.status_code == 200:
            return r
        last = f"HTTP {r.status_code}: {r.text[:500]}"
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(wait * (attempt + 1))
            continue
        break
    raise TTSError(last)


# --- Gemini TTS -------------------------------------------------------------

def gemini(text, cfg, out_path):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise TTSError("Secret GEMINI_API_KEY absent")
    g = cfg["voice"]["gemini"]
    content = {"type": "text", "text": text}
    if g.get("style"):
        content["annotations"] = [{"type": "speech_metadata", "style": g["style"]}]
    body = {
        "model": g["model"],
        "input": [{"type": "user_input", "content": [content]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": g["voice"]}]},
    }
    r = _post_with_retry(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        {"x-goog-api-key": key, "Content-Type": "application/json"},
        body,
    )
    data = r.json()
    audio = None
    for step in data.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for c in step.get("content", []):
            if c.get("type") == "audio" and c.get("data"):
                audio = c["data"]
    if not audio:
        raise TTSError("Réponse Gemini sans audio : " + json.dumps(data)[:500])
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(audio))
    time.sleep(g.get("pause_between_calls_s", 0))
    return out_path


# --- ElevenLabs -------------------------------------------------------------

def elevenlabs(text, cfg, out_path):
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise TTSError("Secret ELEVENLABS_API_KEY absent")
    e = cfg["voice"]["elevenlabs"]
    r = _post_with_retry(
        f"https://api.elevenlabs.io/v1/text-to-speech/{e['voice_id']}?output_format=mp3_44100_128",
        {"xi-api-key": key, "Content-Type": "application/json"},
        {"text": text, "model_id": e["model"], "language_code": "fr"},
    )
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path


# --- Google Cloud TTS (Chirp 3 HD) ------------------------------------------

def google_chirp(text, cfg, out_path):
    key = os.environ.get("GOOGLE_TTS_API_KEY")
    if not key:
        raise TTSError("Secret GOOGLE_TTS_API_KEY absent")
    v = cfg["voice"]["google_chirp"]["voice"]
    r = _post_with_retry(
        f"https://texttospeech.googleapis.com/v1/text:synthesize?key={key}",
        {"Content-Type": "application/json"},
        {
            "input": {"text": text},
            "voice": {"languageCode": "fr-FR", "name": v},
            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000},
        },
    )
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(r.json()["audioContent"]))
    return out_path


PROVIDERS = {"gemini": gemini, "elevenlabs": elevenlabs, "google_chirp": google_chirp}


def synthesize(text, cfg, out_path):
    name = cfg["voice"]["provider"]
    if name not in PROVIDERS:
        raise TTSError(f"Service inconnu : {name}")
    return PROVIDERS[name](text, cfg, out_path)
