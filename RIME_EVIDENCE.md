# Rime Evidence — ToneCraft

## Hard Voice Claim

ToneCraft uses Rime-generated speech as the primary reference performance for theatre rehearsal.

The hard voice problem addressed is **controlled vocal delivery**, specifically providing a consistent spoken reference against which an actor can rehearse pacing and pauses.

## Why Rime Is Essential

Rime is not used as a welcome message, optional playback, or decorative feature.

For every rehearsal line, ToneCraft can generate spoken reference audio using Rime. The actor listens to that performance before recording their own delivery.

Removing Rime-generated speech removes the central reference-performance loop of the application.

## Acceptance Test

### Test

Given a written script line:

1. Submit the line to ToneCraft.
2. Generate its reference performance.
3. Play the generated Rime audio.
4. Record an actor performing the same line.
5. Run the comparison.
6. Verify that the application produces measurable timing information for the two performances.

### Expected Result

The system should:

* Generate spoken reference audio using Rime.
* Make the audio available for playback.
* Allow the actor to record their own performance.
* Compare timing characteristics between the reference and recording.
* Report measurable differences in pacing / pauses.

## Procedure

The test was performed through the ToneCraft web application.

The backend was deployed using FastAPI and the Rime API.

Rime configuration used in the demonstrated build:

* Model: `coda`
* Speaker: `astra`
* Endpoint: `https://users.rime.ai/v1/rime-tts`
* Language: English

The Rime API key is stored server-side as an environment variable.

## Observed Result

The complete rehearsal path was successfully tested locally:

1. Script creation worked.
2. Rime reference audio was generated.
3. Reference audio could be played.
4. User recording worked.
5. Timing / pause comparison produced results.

The backend deployment was also verified through its status endpoint, which confirmed that the Rime API configuration and Clerk JWKS configuration were loaded successfully.

## Limitations

The current prototype evaluates measurable delivery characteristics such as pacing and pauses. It does not claim to objectively evaluate acting quality, emotion, character interpretation, or artistic performance.

The deployed backend may experience additional latency after periods of inactivity because of the hosting environment.

The current prototype is intended as a rehearsal aid rather than an automated acting judge.
