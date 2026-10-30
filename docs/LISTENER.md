# Continuous listener and detective event contract

The listener supplements the existing room WebSocket. It does not replace typed dialogue or the host's act and clue controls.

## Consent, audio and cost

Each guest opts in separately. The guest browser requests `getUserMedia` only after the consent prompt and asks the browser for echo cancellation, noise suppression and automatic gain control. Every up-to-five-second interval is recorded as a fresh, finalized MediaRecorder file; timeslice fragments are not sent because later WebM/Ogg fragments may not decode alone. A `listener.audio` JSON header and one binary WebSocket frame carry each clip (maximum 512 KiB). The server validates container type, duration and header agreement before transcription, and reserves usage using the verified duration. Raw audio is held only for the request and is never written to disk or room records. Device/browser echo cancellation varies; use headphones or mute the TV if the browser reports it is unavailable.

Speech recognition cannot reliably tell which of several nearby guests spoke. Each microphone transcript is therefore shown privately to the opted-in guest before it enters shared room memory. The guest confirms a roster identity, marks it unattributed, or discards the clip. Unattributed clips remain visible as such but do not generate claims, theories, contradictions or follow-up answers. Typed observations are submitted by the authenticated guest and are attributed to that guest.

Paid transcription is off by default. In `.env`, set both `MYSTERY_TRANSCRIPTION_ENABLED=true` and `MYSTERY_ALLOW_PAID_TRANSCRIPTION=true`, set `OPENAI_API_KEY`, then restart the server. The model defaults to `gpt-4o-mini-transcribe`; room usage defaults to 900 seconds. The displayed cost is an estimate based on captured duration and configured rate, not a provider invoice. The default rate is $0.003/minute, based on [current OpenAI API pricing](https://platform.openai.com/pricing/). Changing it updates the estimate. Provider failures consume the reserved room allowance so repeated retries cannot bypass the cap.

## Client to server WebSocket events

| Event | Payload | Effect |
| --- | --- | --- |
| `listener.start` | `{consent:true, source:"typed"|"microphone"}` | Starts this connection's listener session. Consent is mandatory. |
| `listener.resume` | `{consent:true}` | Resumes a muted session with renewed consent. |
| `listener.mute` | `{}` | Blocks transcript/audio submissions on this connection. |
| `listener.stop` | `{}` | Ends the session and clears pending audio metadata. |
| `listener.transcript` | `{text:string}` | Adds a typed or transcribed utterance to shared room memory. |
| `listener.audio` | `{duration_seconds:0.5..5,mime_type:string}` then binary frame | Announces one audio chunk for transcription. |
| `listener.confirm_transcript` | `{id:string,speaker_id:guestId|"unattributed"|"discard"}` | Confirms the source of the pending microphone transcript, saves it, or discards it. |

All commands require a joined guest connection. The server binds the guest identity to its authenticated socket and rejects client-supplied identities. Unknown or malformed events return a normal `error` event. Organizers pause all incoming listener work with the existing room pause control.

## Server to client events and snapshot

The ordinary `state` event contains `listener.utterances`, `listener.theories`, `listener.follow_up`, `listener.interventions` and `listener.usage`. It preserves bounded room history across reconnects and restarts. `listener.status` reports connection-local state. `listener.confirmation_required` is private to the opted-in guest and contains the uncommitted recognized text and current guest roster; a new consented session, Stop, pause or reset clears it. `listener.utterance`, `listener.theory`, `listener.contradiction`, `listener.follow_up`, and `listener.invitation` events describe new decisions; `listener.error` reports transcription failures without returning provider error text or secrets.

Contradiction analysis is deterministic and limited to direct, affirmative, unambiguous suspect, time and place statements. It abstains on reported speech, negation, uncertainty, and ambiguous clauses. It waits for three distinct attributed guests before intervening. It can quote a clue only if the exact server-authored clue has already been released in the current room and its canonical time/location scope matches. The follow-up is fixed from the conflicting statements; the target's next attributed utterance is linked as its answer and remains in memory. Listener events do not increment the narration revision, so discussion does not restart Lewis playback. The listener never decides or announces guilt. Theory records remain unverified or contested and do not reveal canonical solution facts. Supporting/challenging references are pruned with transcript retention.

## Demonstration

1. Start a room, invite three guests, and start the case. Release the “Music-room recording” evidence in Act 2.
2. Each guest opens **Detective at the table**, accepts consent, then chooses **Enable typed listening** (no API key needed).
3. Submit: “Ada was in the library at 9:20.”; “Felix remained in the music room at 9:20.”; “Ada remained in the music room at 9:20.”
4. After the third guest speaks, Wobblebottom flags the conflicting Ada accounts and asks the lower-turn speaker to identify the source or reconcile them. That guest submits an answer; the answer is visibly retained in the transcript and follow-up card.

Run backend tests with `python -m pytest backend/tests/test_listener.py`. Run the frontend checks from `frontend` with `npm test` and `npm run build`.
