import { useEffect, useRef, useState } from "react";
import TalkingDetective, {
  type TalkingDetectiveHandle,
} from "./TalkingDetective";
import "./audition.css";

type Sample = {
  id: string;
  title: string;
  text: string;
  words: string[];
  wtimes: number[];
  wdurations: number[];
  audio_url: string;
  duration_ms: number;
};
type Voice = {
  id: string;
  name: string;
  locale: string;
  gender: string;
  samples: Sample[];
};
type Manifest = {
  available: boolean;
  voices: Voice[];
  timing_source?: string;
  message?: string;
};

function validManifest(value: unknown): value is Manifest {
  if (!value || typeof value !== "object") return false;
  const manifest = value as Manifest;
  return (
    typeof manifest.available === "boolean" &&
    Array.isArray(manifest.voices) &&
    manifest.voices.every(
      (voice) =>
        voice &&
        typeof voice.id === "string" &&
        typeof voice.name === "string" &&
        typeof voice.locale === "string" &&
        typeof voice.gender === "string" &&
        Array.isArray(voice.samples) &&
        voice.samples.every(
          (sample) =>
            sample &&
            [sample.id, sample.title, sample.text, sample.audio_url].every(
              (item) => typeof item === "string",
            ) &&
            sample.audio_url.startsWith("/api/audition/audio/") &&
            Array.isArray(sample.words) &&
            sample.words.length > 0 &&
            sample.words.every((word) => typeof word === "string") &&
            Array.isArray(sample.wtimes) &&
            Array.isArray(sample.wdurations) &&
            sample.words.length === sample.wtimes.length &&
            sample.words.length === sample.wdurations.length &&
            [...sample.wtimes, ...sample.wdurations].every(
              (time) =>
                typeof time === "number" && Number.isFinite(time) && time >= 0,
            ) &&
            typeof sample.duration_ms === "number" &&
            sample.duration_ms > 0,
        ),
    )
  );
}

export default function VoiceAudition() {
  const viewer = useRef<TalkingDetectiveHandle>(null),
    fallbackAudio = useRef<HTMLAudioElement>(null);
  const requestRef = useRef<AbortController | null>(null),
    generation = useRef(0),
    playingRef = useRef(false),
    mounted = useRef(false);
  const [manifest, setManifest] = useState<Manifest | null>(null),
    [voiceId, setVoiceId] = useState("zira"),
    [sampleId, setSampleId] = useState("greeting");
  const [modelState, setModelState] = useState<"loading" | "ready" | "failed">(
      "loading",
    ),
    [progress, setProgress] = useState<number | null>(null);
  const [status, setStatus] = useState("Loading local audition files…"),
    [playing, setPlaying] = useState(false),
    [loadingAudio, setLoadingAudio] = useState(false),
    [error, setError] = useState("");
  const [currentWord, setCurrentWord] = useState("");
  const selectedVoice =
    manifest?.voices.find((voice) => voice.id === voiceId) ||
    manifest?.voices[0];
  const selectedSample =
    selectedVoice?.samples.find((sample) => sample.id === sampleId) ||
    selectedVoice?.samples[0];

  function stop(message = "Audition stopped.") {
    generation.current += 1;
    requestRef.current?.abort();
    requestRef.current = null;
    viewer.current?.stop();
    if (fallbackAudio.current) {
      fallbackAudio.current.pause();
      fallbackAudio.current.currentTime = 0;
    }
    playingRef.current = false;
    setPlaying(false);
    setLoadingAudio(false);
    setCurrentWord("");
    setStatus(message);
  }

  useEffect(() => {
    let disposed = false;
    mounted.current = true;
    const abort = new AbortController();
    // Defer work so StrictMode's rehearsal cleanup cannot leave a loading renderer behind.
    queueMicrotask(async () => {
      if (disposed) return;
      fetch("/api/audition", { signal: abort.signal })
        .then((response) => {
          if (!response.ok) throw Error("manifest");
          return response.json();
        })
        .then((data) => {
          if (disposed) return;
          if (!validManifest(data)) throw Error("manifest");
          setManifest(data);
          if (!data.available || !data.voices.length)
            setError(
              "Local voice samples are not prepared on this computer. Run the audition preparation step in the setup guide.",
            );
        })
        .catch(() => {
          if (!disposed)
            setError(
              "The local voice samples could not be loaded. Check that the server and audition files are ready.",
            );
        });
    });
    return () => {
      disposed = true;
      mounted.current = false;
      abort.abort();
      generation.current += 1;
      requestRef.current?.abort();
      playingRef.current = false;
      if (fallbackAudio.current) {
        fallbackAudio.current.pause();
        fallbackAudio.current.removeAttribute("src");
        fallbackAudio.current.load();
      }
      viewer.current?.stop();
    };
  }, []);

  async function play() {
    if (!selectedSample || !selectedVoice) return;
    stop("Preparing the selected recording…");
    setError("");
    setLoadingAudio(true);
    const ownGeneration = generation.current;
    if (modelState !== "ready" || !viewer.current) {
      try {
        const audio = fallbackAudio.current;
        if (!audio) throw Error("audio");
        audio.src = selectedSample.audio_url;
        await audio.play();
        if (generation.current !== ownGeneration || !mounted.current) {
          audio.pause();
          return;
        }
        playingRef.current = true;
        setPlaying(true);
        setStatus("Playing audio only — avatar unavailable.");
      } catch {
        if (generation.current === ownGeneration)
          setError(
            "Audio playback was blocked or unavailable. Try Play audition again.",
          );
      } finally {
        if (generation.current === ownGeneration) setLoadingAudio(false);
      }
      return;
    }
    try {
      const currentViewer = viewer.current;
      await currentViewer.unlock();
      const request = new AbortController();
      requestRef.current = request;
      const response = await fetch(selectedSample.audio_url, {
        signal: request.signal,
      });
      if (!response.ok) throw Error("audio");
      const bytes = await response.arrayBuffer();
      if (generation.current !== ownGeneration || !mounted.current) return;
      const started = await currentViewer.speakAudio(bytes, {
        words: selectedSample.words,
        wtimes: selectedSample.wtimes,
        wdurations: selectedSample.wdurations,
      });
      if (!started || generation.current !== ownGeneration || !mounted.current)
        return;
      playingRef.current = true;
      setPlaying(true);
      setStatus(`Playing ${selectedVoice.name} with word-timed lip sync.`);
    } catch {
      if (generation.current === ownGeneration)
        setError(
          "This local recording could not play. Check the sample files and try again.",
        );
    } finally {
      if (generation.current === ownGeneration) setLoadingAudio(false);
    }
  }

  return (
    <div className="audition-page">
      <header className="audition-header">
        <a className="brand" href="/">
          <span className="seal">W</span>
          <span>
            WOBBLEBOTTOM
            <span className="brand-sub">VOICE & PERFORMANCE LAB</span>
          </span>
        </a>
        <a className="audition-back" href="/">
          Return to the manor ↗
        </a>
      </header>
      <main className="audition-layout">
        <section className="audition-stage-panel">
          <div className="eyebrow">A TECHNICAL AUDITION · NO PAID SERVICES</div>
          <h1>A voice with a face.</h1>
          <p className="audition-intro">
            Listen to the same three lines with two existing Windows voices.
            Watch the recorded words drive real avatar mouth shapes.
          </p>
          <div className="audition-portrait">
            <TalkingDetective
              ref={viewer}
              label="TalkingHead audition avatar"
              className="audition-avatar"
              onModelState={(state) => {
                setModelState(state);
                if (state === "ready")
                  setStatus(
                    "Ready. Choose a voice and line, then play the audition.",
                  );
              }}
              onProgress={setProgress}
              onSpeakingChange={setPlaying}
              onWord={setCurrentWord}
              onComplete={() => {
                playingRef.current = false;
                setStatus(
                  "Audition complete. Compare the other voice on the same line.",
                );
              }}
              onError={() =>
                setStatus(
                  "Avatar unavailable. Prepared voice samples can still play as audio only.",
                )
              }
            />
            {modelState === "loading" && (
              <div className="audition-loading" role="status">
                Loading licensed sample avatar · 35 MB
                {progress !== null ? ` · ${progress}%` : "…"}
              </div>
            )}
            {modelState === "failed" && (
              <div className="audition-loading">
                Audio-only mode · avatar unavailable
              </div>
            )}
            <div className="audition-model-label">
              Licensed sample avatar — not Wobblebottom
              <span>CC0 clothed human demo · TalkingHead renderer</span>
            </div>
          </div>
          <section
            className="audition-caption"
            aria-label="Current audition text"
          >
            <span className="eyebrow">THE SELECTED LINE</span>
            <p>
              {selectedSample?.text ||
                "Local sample recordings will appear here when prepared."}
            </p>
            {playing && currentWord && (
              <span className="audition-current-word" aria-live="off">
                Speaking: {currentWord}
              </span>
            )}
          </section>
        </section>
        <aside className="audition-controls">
          <section className="panel">
            <div className="eyebrow">COMPARE THE PERFORMANCE</div>
            <h2>The audition desk</h2>
            <p className="audition-note">
              Existing Windows demo voices · en-US. These are not the final
              British detective voice.
            </p>
            <label htmlFor="audition-voice">Existing voice</label>
            <select
              id="audition-voice"
              value={selectedVoice?.id || ""}
              disabled={!manifest?.available}
              onChange={(event) => {
                stop("Voice changed. Ready to audition.");
                setVoiceId(event.target.value);
              }}
            >
              {!manifest?.voices.length && (
                <option value="">No prepared voices</option>
              )}
              {manifest?.voices.map((voice) => (
                <option value={voice.id} key={voice.id}>
                  {voice.name} · {voice.locale}
                </option>
              ))}
            </select>
            <label htmlFor="audition-line">Audition line</label>
            <select
              id="audition-line"
              value={selectedSample?.id || ""}
              disabled={!selectedVoice}
              onChange={(event) => {
                stop("Line changed. Ready to audition.");
                setSampleId(event.target.value);
              }}
            >
              {!selectedVoice?.samples.length && (
                <option value="">No prepared lines</option>
              )}
              {selectedVoice?.samples.map((sample) => (
                <option value={sample.id} key={sample.id}>
                  {sample.title}
                </option>
              ))}
            </select>
            <div className="audition-actions">
              <button
                className="primary"
                onClick={play}
                disabled={
                  !selectedSample || loadingAudio || modelState === "loading"
                }
              >
                Play audition
              </button>
              <button
                onClick={() => stop()}
                disabled={!playing && !loadingAudio}
              >
                Stop audition
              </button>
            </div>
            <p className="audition-status" role="status">
              {loadingAudio ? "Preparing local audio…" : status}
            </p>
            {error && (
              <p className="audition-error" role="alert">
                {error}
              </p>
            )}
          </section>
          <section className="panel">
            <div className="eyebrow">WHAT YOU ARE HEARING</div>
            <h3>Recorded speech. Timed lips.</h3>
            <p className="audition-note">
              Local WAV recordings use Windows SAPI word-start timings. Word
              durations are estimated; TalkingHead derives English visemes from
              those recorded words.
            </p>
            <p className="audition-note">
              No microphone, browser speech imitation, API key, or paid voice
              generation. Nothing plays until you press Play.
            </p>
          </section>
          <section className="panel">
            <div className="eyebrow">FOR THE FINAL DETECTIVE</div>
            <h3>Voice references</h3>
            <a
              className="share-link"
              href="https://elevenlabs.io/voice-library/old-male"
              target="_blank"
              rel="noreferrer"
            >
              Listen to Older Joe on ElevenLabs ↗
            </a>
            <a
              className="share-link"
              href="https://elevenlabs.io/docs/help-center/product/voices/my-voices/what-are-default-voices"
              target="_blank"
              rel="noreferrer"
            >
              Eldrin voice details ↗
            </a>
            <p className="tiny">
              External reference pages only. This audition does not generate
              either paid voice or select the final character.
            </p>
          </section>
        </aside>
      </main>
      <audio
        ref={fallbackAudio}
        preload="none"
        onEnded={() => {
          playingRef.current = false;
          setPlaying(false);
          setStatus("Audio-only audition complete.");
        }}
      />
    </div>
  );
}
