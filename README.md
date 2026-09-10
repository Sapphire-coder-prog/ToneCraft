# ToneCraft — Say it like you mean it.

ToneCraft is a voice-first theatre rehearsal tool that helps actors practice not only **what** they say, but **how** they say it.

## Problem

When rehearsing a script alone, actors often lack a consistent performance reference. Reading the same line repeatedly does not provide feedback on pacing, pauses, or delivery.

ToneCraft creates a spoken reference for each line and lets the actor record their own performance and compare it against the reference.

## Solution

ToneCraft turns a written script into an interactive rehearsal workflow:

1. The actor enters a script.
2. ToneCraft breaks the script into individual lines.
3. The actor selects a desired tone.
4. Rime generates the reference performance.
5. The actor listens to the reference.
6. The actor records their own delivery.
7. ToneCraft compares measurable timing characteristics such as pacing and pauses.

The goal is not to tell an actor that there is one "correct" performance. Instead, the generated performance provides a consistent reference that the actor can rehearse against.

## Why Voice Is Essential

Voice is the core of ToneCraft rather than an optional interface feature.

Rime-generated speech is the reference performance that the actor listens to and responds to. Without spoken output, the central rehearsal loop disappears.

ToneCraft specifically addresses the voice problem of **controlled delivery and expressive performance**, where pacing, pauses and vocal delivery matter to the user experience.

## Rime Integration

Rime provides the primary spoken output in ToneCraft.

The backend calls the Rime TTS API to generate reference audio for individual script lines. Generated audio is stored by the backend and served to the frontend for playback.

Rime configuration used in the demonstrated build:

* Model: `coda`
* Speaker: `astra`
* Endpoint: `https://users.rime.ai/v1/rime-tts`
* Language: English
* Audio: generated TTS audio returned by the Rime API
* Transport: HTTPS API request from the FastAPI backend

Rime credentials are kept server-side and are not included in the repository.

## Architecture

```text
User
 │
 ▼
GitHub Pages Frontend
 │
 │ HTTPS API requests
 ▼
FastAPI Backend on Render
 │
 ├── Clerk authentication
 │
 ├── SQLite
 │    ├── scripts
 │    └── lines / rehearsal metadata
 │
 ├── Rime TTS
 │
 └── Audio storage
 │
 ▼
Reference speech
 │
 ▼
Actor listens → records performance
 │
 ▼
Timing / pacing comparison
```

## Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* FastAPI
* SQLite
* PyJWT

### Voice

* Rime TTS

### Authentication

* Clerk

### Hosting

* GitHub Pages
* Render

## Running Locally

### Backend

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create a `.env` file using `.env.example` and provide the required credentials.

Start the backend:

```bash
uvicorn backend.main:app --reload
```

### Frontend

Open the frontend through a local web server and configure the backend URL in the frontend configuration.

## Known Limitations

* The current comparison focuses on measurable timing characteristics such as pacing and pauses rather than attempting to judge subjective acting quality.
* Backend hosting may experience a cold-start delay after inactivity.
* Browser microphone permissions are required for recording.
* The deployed frontend currently works reliably through the direct `index.html` path; the root GitHub Pages path may show inconsistent routing on some devices.

## Security

Secrets such as Rime and Clerk credentials are stored as environment variables and are not committed to the repository.

## Project Status

ToneCraft is a working prototype built for the Rime/DataForge hackathon.
