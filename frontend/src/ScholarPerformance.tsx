import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import "./scholar-performance.css";

type Options = {
  room: string;
  dialogue: string;
  revision: number;
  act: number;
  paused: boolean;
  online: boolean;
  token: string;
  active: boolean;
};
type ScholarSpeech = {
  provider: "kokoro-onnx";
  voice: "bm_lewis";
  text: string;
  revision: number;
  duration_ms: number;
  content_type: "audio/wav";
  audio_base64: string;
  playback_rate: 1.05;
};
function validSpeech(value: unknown): value is ScholarSpeech {
  if (!value || typeof value !== "object") return false;
  const sample = value as ScholarSpeech;
  return (
    sample.provider === "kokoro-onnx" &&
    sample.voice === "bm_lewis" &&
    sample.content_type === "audio/wav" &&
    sample.playback_rate === 1.05 &&
    typeof sample.text === "string" &&
    Number.isInteger(sample.revision) &&
    typeof sample.duration_ms === "number" &&
    sample.duration_ms > 0 &&
    typeof sample.audio_base64 === "string" &&
    sample.audio_base64.length > 0
  );
}

/** Approved still concept and genuine local Lewis audio; deliberately no fake visemes. */
export function useScholarPerformance(options: Options): {
  avatar: ReactNode;
  controls: ReactNode;
  speaking: boolean;
  stop: () => void;
} {
  const audio = useRef<HTMLAudioElement | null>(null),
    request = useRef<AbortController | null>(null),
    objectURL = useRef<string | null>(null);
  const generation = useRef(0),
    enabledRef = useRef(false),
    lastSpoken = useRef(""),
    latest = useRef(options),
    previousAct = useRef(options.act);
  latest.current = options;
  const [enabled, setEnabled] = useState(false),
    [available, setAvailable] = useState<boolean | null>(null),
    [loading, setLoading] = useState(false),
    [playing, setPlaying] = useState(false);
  const [message, setMessage] = useState(
      "Muted. Enable Lewis voice when your table is ready.",
    ),
    [error, setError] = useState("");
  const bindAudio = useCallback((node: HTMLAudioElement | null) => {
    if (audio.current && audio.current !== node) {
      audio.current.pause();
      audio.current.removeAttribute("src");
      audio.current.load();
    }
    audio.current = node;
  }, []);
  function stop() {
    generation.current += 1;
    request.current?.abort();
    request.current = null;
    if (audio.current) {
      audio.current.pause();
      audio.current.currentTime = 0;
      audio.current.removeAttribute("src");
      audio.current.load();
    }
    if (objectURL.current) {
      URL.revokeObjectURL(objectURL.current);
      objectURL.current = null;
    }
    setLoading(false);
    setPlaying(false);
  }
  function mute() {
    enabledRef.current = false;
    setEnabled(false);
    stop();
    setMessage("Lewis voice muted.");
  }
  useEffect(() => {
    if (!options.active) {
      mute();
      return;
    }
    setMessage("Muted. Enable Lewis voice when your table is ready.");
    setAvailable(null);
    const abort = new AbortController();
    fetch("/api/scholar-speech/status", { signal: abort.signal })
      .then((response) => {
        if (!response.ok) throw Error("status");
        return response.json();
      })
      .then((value) => {
        if (!abort.signal.aborted)
          setAvailable(
            typeof value.available === "boolean" &&
              value.available &&
              value.provider === "kokoro-onnx" &&
              value.voice === "bm_lewis" &&
              value.playback_rate === 1.05,
          );
      })
      .catch(() => {
        if (!abort.signal.aborted) setAvailable(false);
      });
    return () => abort.abort();
  }, [options.active, options.room]);
  useEffect(() => {
    if (!options.online || !options.active) {
      enabledRef.current = false;
      setEnabled(false);
      stop();
    }
    if (previousAct.current > 0 && options.act === 0) mute();
    previousAct.current = options.act;
  }, [options.online, options.active, options.act]);
  async function perform() {
    const current = latest.current;
    if (
      !enabledRef.current ||
      !current.active ||
      !current.online ||
      current.paused ||
      !current.token ||
      !audio.current
    )
      return;
    stop();
    const ownGeneration = generation.current;
    lastSpoken.current = current.dialogue;
    setLoading(true);
    setError("");
    setMessage("Preparing the current public dialogue in Lewis’s voice…");
    const abort = new AbortController();
    request.current = abort;
    try {
      const response = await fetch(
        `/api/rooms/${encodeURIComponent(current.room)}/scholar-speech`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${current.token}`,
          },
          body: JSON.stringify({}),
          signal: abort.signal,
        },
      );
      if (!response.ok)
        throw Error(
          response.status === 409
            ? "stale"
            : response.status === 401 || response.status === 403
              ? "access"
              : response.status === 429
                ? "busy"
                : "unavailable",
        );
      const sample: unknown = await response.json(),
        now = latest.current;
      if (
        generation.current !== ownGeneration ||
        !enabledRef.current ||
        !now.active ||
        !now.online ||
        now.paused ||
        now.revision !== current.revision ||
        now.dialogue !== current.dialogue
      )
        return;
      if (
        !validSpeech(sample) ||
        sample.revision !== current.revision ||
        sample.text !== current.dialogue
      )
        throw Error("stale");
      const binary = atob(sample.audio_base64),
        bytes = new Uint8Array(binary.length);
      for (let index = 0; index < binary.length; index += 1)
        bytes[index] = binary.charCodeAt(index);
      const element = audio.current;
      if (!element) return;
      const url = URL.createObjectURL(new Blob([bytes], { type: "audio/wav" }));
      objectURL.current = url;
      element.src = url;
      element.volume = 1;
      element.preservesPitch = true;
      element.playbackRate = 1.05;
      await element.play();
      if (generation.current !== ownGeneration) return;
      if (
        !enabledRef.current ||
        !latest.current.active ||
        latest.current.paused ||
        !latest.current.online
      ) {
        element.pause();
        return;
      }
      setPlaying(true);
      setMessage("Lewis is speaking · approved pace +5% · pitch preserved.");
    } catch (failure) {
      if (generation.current !== ownGeneration || abort.signal.aborted) return;
      const kind = failure instanceof Error ? failure.message : "unavailable";
      if (kind === "stale")
        setMessage("The case changed. Replay the current dialogue when ready.");
      else
        setError(
          kind === "access"
            ? "Open the authenticated TV link from the host desk to enable Lewis voice."
            : kind === "busy"
              ? "Lewis voice is already preparing a line. Try Replay dialogue shortly."
              : "Lewis voice is unavailable or playback was blocked. Captions and evidence still work; try Replay dialogue or use an explicit fallback.",
        );
    } finally {
      if (generation.current === ownGeneration) setLoading(false);
    }
  }
  useEffect(() => {
    stop();
    if (options.paused) {
      setMessage("Evening paused. Lewis voice stopped.");
      return;
    }
    if (
      enabled &&
      options.active &&
      options.online &&
      lastSpoken.current !== options.dialogue
    )
      void perform();
    return () => {
      generation.current += 1;
      request.current?.abort();
      audio.current?.pause();
    };
  }, [
    options.dialogue,
    options.revision,
    options.paused,
    options.online,
    options.active,
    options.room,
    enabled,
  ]);
  useEffect(
    () => () => {
      generation.current += 1;
      request.current?.abort();
      audio.current?.pause();
      if (objectURL.current) URL.revokeObjectURL(objectURL.current);
    },
    [],
  );
  function enable() {
    if (
      !latest.current.online ||
      latest.current.paused ||
      !latest.current.active
    )
      return;
    enabledRef.current = true;
    lastSpoken.current = "";
    setError("");
    setEnabled(true);
    setMessage("Lewis voice enabled.");
  }
  const canPlay =
    options.online && !options.paused && !!options.token && available === true;
  return {
    stop,
    speaking: playing,
    avatar: (
      <div
        className="scholar-portrait"
        role="img"
        aria-label="Approved Scholar concept portrait"
      >
        <img
          src="/casting/vale.png"
          alt="Reginald P. Wobblebottom — the approved Scholar concept, wearing round spectacles and a tweed waistcoat"
        />
      </div>
    ),
    controls: (
      <section
        className="scholar-performance"
        aria-label="Scholar detective performance"
      >
        <div className="scholar-performance-controls">
          {enabled ? (
            <button onClick={mute}>Mute Lewis voice</button>
          ) : (
            <button onClick={enable} disabled={!canPlay}>
              Enable Lewis voice
            </button>
          )}
          <button
            onClick={() => {
              stop();
              setMessage(
                "Speech stopped. New public dialogue may play; mute to stay silent.",
              );
            }}
            disabled={!enabled && !loading && !playing}
          >
            Stop speech
          </button>
          <button
            onClick={() => void perform()}
            disabled={!enabled || !canPlay || loading}
          >
            Replay dialogue
          </button>
        </div>
        <p>
          Approved Scholar portrait + Lewis · British English · +5% pace with
          pitch preserved. This is a still concept portrait; the final 3D rig
          and lip sync are pending.
        </p>
        {!options.token && (
          <p className="scholar-performance-error">
            For Lewis voice, open the authenticated TV link from the host desk.
            The public TV view still works.
          </p>
        )}
        {available === false && (
          <p className="scholar-performance-error">
            The local Lewis voice is unavailable on this server. No Windows US
            voice is substituted; choose a fallback explicitly if needed.
          </p>
        )}
        <p role="status">{loading ? "Preparing Lewis dialogue…" : message}</p>
        {error && (
          <p className="scholar-performance-error" role="alert">
            {error}
          </p>
        )}
        <audio
          ref={bindAudio}
          aria-label="Lewis dialogue audio"
          preload="none"
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => {
            setPlaying(false);
            setMessage(
              "Line finished. Listening for the next public dialogue.",
            );
          }}
        />
      </section>
    ),
  };
}
