import os
import uuid
import shutil
from pathlib import Path

import httpx
import librosa
import numpy as np
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from db import get_conn, init_db
from auth import get_current_user


init_db()

RIME_API_KEY = os.getenv("RIME_API_KEY")
RIME_SPEAKER = os.getenv("RIME_SPEAKER", "cove")
RIME_MODEL_ID = "coda"
RIME_ENDPOINT = "https://users.rime.ai/v1/rime-tts"

AUDIO_DIR = Path("audio_files")
AUDIO_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Theatre Rehearsal Partner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

TONE_INSTRUCTIONS = {
    "grief": "Speak slowly, in a heavy, breaking voice, with long pauses between phrases.",
    "sarcasm": "Speak with a dry, mocking tone, drawing out words ironically.",
    "urgency": "Speak quickly and sharply, with tension and no pauses, as if time is running out.",
    "tender": "Speak softly and warmly, with gentle pacing and care.",
    "commanding": "Speak firmly and assertively, with clear enunciation and authority.",
    "neutral": "Speak in a plain, even, conversational tone.",
}


class ScriptIn(BaseModel):
    text: str


class ToneIn(BaseModel):
    tone: str


@app.get("/status")
def status():
    return {
        "provider": "rime",
        "model": RIME_MODEL_ID,
        "speaker": RIME_SPEAKER,
        "endpoint": RIME_ENDPOINT,
        "api_key_loaded": bool(RIME_API_KEY),
    }


def get_line_or_404(conn, line_id: str, user_id: str):
    row = conn.execute(
        "SELECT * FROM lines WHERE line_id = ? AND user_id = ?",
        (line_id, user_id),
    ).fetchone()
    if not row:
        raise HTTPException(404, "Line not found")
    return row


@app.post("/scripts")
def create_script(payload: ScriptIn, user=Depends(get_current_user)):
    try:
        user_id = user["sub"]
        raw_lines = [l.strip() for l in payload.text.splitlines() if l.strip()]

        if not raw_lines:
            raise HTTPException(400, "No lines found in script")

        script_id = uuid.uuid4().hex[:8]
        conn = get_conn()

        conn.execute(
            "INSERT INTO scripts (script_id, user_id) VALUES (?, ?)",
            (script_id, user_id),
        )

        result_lines = []

        for text in raw_lines:
            line_id = uuid.uuid4().hex[:8]

            conn.execute(
                "INSERT INTO lines (line_id, script_id, user_id, text) VALUES (?, ?, ?, ?)",
                (line_id, script_id, user_id, text),
            )

            result_lines.append({
                "line_id": line_id,
                "text": text
            })

        conn.commit()
        conn.close()

        return {
            "script_id": script_id,
            "lines": result_lines
        }

    except HTTPException:
        raise

    except Exception as e:
        print("!!! CREATE SCRIPT ERROR !!!")
        print(type(e).__name__)
        print(str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Create script failed: {type(e).__name__}: {str(e)}"
        )

    # user_id = user["sub"]
    # raw_lines = [l.strip() for l in payload.text.splitlines() if l.strip()]
    # if not raw_lines:
    #     raise HTTPException(400, "No lines found in script")

    # script_id = uuid.uuid4().hex[:8]
    # conn = get_conn()
    # conn.execute(
    #     "INSERT INTO scripts (script_id, user_id) VALUES (?, ?)",
    #     (script_id, user_id),
    # )

    # result_lines = []
    # for text in raw_lines:
    #     line_id = uuid.uuid4().hex[:8]
    #     conn.execute(
    #         "INSERT INTO lines (line_id, script_id, user_id, text) VALUES (?, ?, ?, ?)",
    #         (line_id, script_id, user_id, text),
    #     )
    #     result_lines.append({"line_id": line_id, "text": text})

    # conn.commit()
    # conn.close()

    # return {"script_id": script_id, "lines": result_lines}


@app.post("/lines/{line_id}/tone")
def set_tone(line_id: str, payload: ToneIn, user=Depends(get_current_user)):
    if payload.tone not in TONE_INSTRUCTIONS:
        raise HTTPException(400, f"Tone must be one of {list(TONE_INSTRUCTIONS.keys())}")

    conn = get_conn()
    get_line_or_404(conn, line_id, user["sub"])
    conn.execute(
        "UPDATE lines SET tone = ? WHERE line_id = ? AND user_id = ?",
        (payload.tone, line_id, user["sub"]),
    )
    conn.commit()
    conn.close()

    return {"line_id": line_id, "tone": payload.tone}


@app.post("/lines/{line_id}/generate")
async def generate_line(line_id: str, user=Depends(get_current_user)):
    conn = get_conn()
    line = get_line_or_404(conn, line_id, user["sub"])

    if not RIME_API_KEY:
        raise HTTPException(500, "RIME_API_KEY not set in .env")

    instruction = TONE_INSTRUCTIONS[line["tone"]]
    prompt_text = f"{instruction} {line['text']}"

    headers = {
        "Authorization": f"Bearer {RIME_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    body = {
        "speaker": RIME_SPEAKER,
        "text": prompt_text,
        "modelId": RIME_MODEL_ID,
        "language": "en",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(RIME_ENDPOINT, headers=headers, json=body)

    if resp.status_code != 200:
        raise HTTPException(502, f"Rime API error {resp.status_code}: {resp.text}")

    filename = f"{line_id}_ref.mp3"
    filepath = AUDIO_DIR / filename
    with open(filepath, "wb") as f:
        f.write(resp.content)

    conn.execute(
        "UPDATE lines SET ref_audio_path = ? WHERE line_id = ? AND user_id = ?",
        (str(filepath), line_id, user["sub"]),
    )
    conn.commit()
    conn.close()

    return {"line_id": line_id, "audio_url": f"/audio/{filename}", "prompt_used": prompt_text}


@app.post("/lines/{line_id}/recording")
async def upload_recording(
    line_id: str, file: UploadFile = File(...), user=Depends(get_current_user)
):
    conn = get_conn()
    get_line_or_404(conn, line_id, user["sub"])

    ext = Path(file.filename).suffix or ".webm"
    filename = f"{line_id}_rec{ext}"
    filepath = AUDIO_DIR / filename

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    conn.execute(
        "UPDATE lines SET recording_path = ? WHERE line_id = ? AND user_id = ?",
        (str(filepath), line_id, user["sub"]),
    )
    conn.commit()
    conn.close()

    return {"line_id": line_id, "recording_url": f"/audio/{filename}"}


def analyze_audio(path: str):
    y, sr = librosa.load(path, sr=None, mono=True)
    duration_sec = librosa.get_duration(y=y, sr=sr)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])

    non_silent_intervals = librosa.effects.split(y, top_db=30)
    pause_count = max(0, len(non_silent_intervals) - 1)

    return {
        "duration_sec": round(float(duration_sec), 2),
        "tempo_bpm": round(tempo, 1),
        "pause_count": int(pause_count),
    }


@app.get("/lines/{line_id}/compare")
def compare_line(line_id: str, user=Depends(get_current_user)):
    conn = get_conn()
    line = get_line_or_404(conn, line_id, user["sub"])
    conn.close()

    if not line["ref_audio_path"]:
        raise HTTPException(400, "Generate the Rime reference audio first")
    if not line["recording_path"]:
        raise HTTPException(400, "Upload a user recording first")

    ref_stats = analyze_audio(line["ref_audio_path"])
    user_stats = analyze_audio(line["recording_path"])

    tempo_diff = user_stats["tempo_bpm"] - ref_stats["tempo_bpm"]
    pause_diff = user_stats["pause_count"] - ref_stats["pause_count"]

    if abs(tempo_diff) < 10:
        tempo_comment = "Your pacing was close to the reference."
    elif tempo_diff > 0:
        tempo_comment = "You spoke faster than the reference delivery."
    else:
        tempo_comment = "You spoke slower than the reference delivery."

    if pause_diff == 0:
        pause_comment = "You used a similar number of pauses."
    elif pause_diff > 0:
        pause_comment = "You paused more often than the reference."
    else:
        pause_comment = "You paused less often than the reference."

    return {
        "line_id": line_id,
        "tone": line["tone"],
        "reference": ref_stats,
        "user": user_stats,
        "comparison": f"{tempo_comment} {pause_comment}",
    }