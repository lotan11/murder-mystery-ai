import { useEffect, useRef, useState } from "react";
import { TalkingHead } from "@met4citizen/talkinghead";
import { LipsyncEn } from "@met4citizen/talkinghead/modules/lipsync-en.mjs";
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
  const mount = useRef<HTMLDivElement>(null),
    fallbackAudio = useRef<HTMLAudioElement>(null);
  const headRef = useRef<TalkingHead | null>(null),
    contextRef = useRef<AudioContext | null>(null);
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
    headRef.current?.stopSpeaking();
    if (fallbackAudio.current) {
      fallbackAudio.current.pause();
      fallbackAudio.current.currentTime = 0;
    }
    playingRef.current = false;
    if (mount.current) {
      mount.current.dataset.speaking = "false";
      mount.current.dataset.visemeMax = "0";
      mount.current.dataset.visemeActiveCount = "0";
    }
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
      if (disposed || !mount.current) return;
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
      let head: TalkingHead | null = null;
      try {
        const context = new AudioContext();
        contextRef.current = context;
        const host = mount.current;
        let motions = 0,
          previous = 0;
        head = new TalkingHead(host, {
          audioCtx: context,
          lipsyncLang: "en",
          lipsyncModules: [],
          cameraView: "head",
          modelFPS: 30,
          modelPixelRatio:
            Math.min(window.devicePixelRatio || 1, 1.5) /
            (window.devicePixelRatio || 1),
          cameraRotateEnable: false,
          lightAmbientColor: 0xf0e5cf,
          lightAmbientIntensity: 1.7,
          lightDirectColor: 0xb5c8c5,
          lightDirectIntensity: 7,
          avatarIdleEyeContact: 0.7,
          avatarSpeakingEyeContact: 0.8,
          avatarIdleHeadMove: 0.2,
          avatarSpeakingHeadMove: 0.3,
          update: () => {
            if (disposed || !head) return;
            let maximum = 0,
              active = 0;
            for (const [name, target] of Object.entries(head.mtAvatar)) {
              if (!name.startsWith("viseme_")) continue;
              let actual = 0;
              target.ms.forEach((values, index) => {
                actual = Math.max(
                  actual,
                  Math.abs(values[target.is[index]] || 0),
                );
              });
              maximum = Math.max(maximum, actual);
              if (actual > 0.02) active += 1;
            }
            if (head.isSpeaking && Math.abs(maximum - previous) > 0.005)
              motions += 1;
            previous = maximum;
            host.dataset.visemeMax = maximum.toFixed(3);
            host.dataset.visemeActiveCount = String(active);
            host.dataset.visemeMotionCount = String(motions);
            host.dataset.speaking = String(head.isSpeaking);
            if (
              playingRef.current &&
              !head.isSpeaking &&
              !head.isAudioPlaying
            ) {
              playingRef.current = false;
              setPlaying(false);
              setCurrentWord("");
              setStatus(
                "Audition complete. Compare the other voice on the same line.",
              );
            }
          },
        });
        // Direct import is bundled by Vite; no variable URL language-module request or CDN.
        head.lipsync.en = new LipsyncEn();
        headRef.current = head;
        await head.showAvatar(
          {
            url: "/audition/mpfb.glb",
            body: "F",
            lipsyncLang: "en",
            avatarMood: "neutral",
          },
          (event) => {
            if (!disposed && event.total > 0)
              setProgress(Math.round((event.loaded / event.total) * 100));
          },
        );
        if (disposed) {
          head.dispose();
          return;
        }
        host.querySelector("canvas")?.setAttribute("aria-hidden", "true");
        setModelState("ready");
        setStatus("Ready. Choose a voice and line, then play the audition.");
      } catch {
        if (disposed) return;
        head?.dispose();
        headRef.current = null;
        void contextRef.current?.close();
        contextRef.current = null;
        setModelState("failed");
        setStatus(
          "Avatar unavailable. Prepared voice samples can still play as audio only.",
        );
      }
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
      headRef.current?.dispose();
      headRef.current = null;
      if (contextRef.current && contextRef.current.state !== "closed")
        void contextRef.current.close();
      contextRef.current = null;
    };
  }, []);

  async function play() {
    if (!selectedSample || !selectedVoice) return;
    stop("Preparing the selected recording…");
    setError("");
    setLoadingAudio(true);
    const ownGeneration = generation.current;
    if (modelState !== "ready" || !headRef.current || !contextRef.current) {
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
      const head = headRef.current,
        context = contextRef.current;
      await context.resume();
      const request = new AbortController();
      requestRef.current = request;
      const response = await fetch(selectedSample.audio_url, {
        signal: request.signal,
      });
      if (!response.ok) throw Error("audio");
      const audio = await context.decodeAudioData(await response.arrayBuffer());
      if (generation.current !== ownGeneration || !mounted.current) return;
      head.speakAudio(
        {
          audio,
          words: selectedSample.words,
          wtimes: selectedSample.wtimes,
          wdurations: selectedSample.wdurations,
        },
        { lipsyncLang: "en" },
        (word) => {
          if (generation.current === ownGeneration && mounted.current)
            setCurrentWord(word.trim());
        },
      );
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
            <div
              ref={mount}
              className="audition-avatar"
              role="img"
              aria-label="TalkingHead audition avatar"
              data-model-state={modelState}
              data-speaking="false"
              data-viseme-max="0"
              data-viseme-motion-count="0"
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
