import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { TalkingHead } from "@met4citizen/talkinghead";
import { LipsyncEn } from "@met4citizen/talkinghead/modules/lipsync-en.mjs";
import "./talking-detective.css";

export type SpeechTiming = {
  words: string[];
  wtimes: number[];
  wdurations: number[];
};
export type TalkingDetectiveHandle = {
  unlock(): Promise<void>;
  speakAudio(bytes: ArrayBuffer, timing: SpeechTiming): Promise<boolean>;
  stop(): void;
};
type Props = {
  label: string;
  className?: string;
  onModelState?: (state: "loading" | "ready" | "failed") => void;
  onProgress?: (progress: number) => void;
  onSpeakingChange?: (speaking: boolean) => void;
  onWord?: (word: string) => void;
  onComplete?: () => void;
  onError?: (message: string) => void;
};

/** One renderer and approved performance profile shared by auditions and live TV. */
const TalkingDetective = forwardRef<TalkingDetectiveHandle, Props>(
  function TalkingDetective(props, ref) {
    const host = useRef<HTMLDivElement>(null),
      canvasHost = useRef<HTMLDivElement>(null);
    const headRef = useRef<TalkingHead | null>(null),
      contextRef = useRef<AudioContext | null>(null);
    const generation = useRef(0),
      playing = useRef(false),
      ready = useRef(false),
      callbacks = useRef(props);
    callbacks.current = props;

    function stop() {
      generation.current += 1;
      playing.current = false;
      headRef.current?.stopSpeaking();
      if (host.current) {
        host.current.dataset.speaking = "false";
        host.current.dataset.visemeMax = "0";
        host.current.dataset.visemeActiveCount = "0";
      }
      callbacks.current.onSpeakingChange?.(false);
      callbacks.current.onWord?.("");
    }
    useImperativeHandle(ref, () => ({
      async unlock() {
        if (!ready.current || !contextRef.current)
          throw Error("The animated avatar is not ready.");
        await contextRef.current.resume();
      },
      async speakAudio(bytes, timing) {
        stop();
        const ownGeneration = generation.current;
        const context = contextRef.current,
          head = headRef.current;
        if (!ready.current || !context || !head)
          throw Error("The animated avatar is unavailable.");
        const audio = await context.decodeAudioData(bytes);
        if (ownGeneration !== generation.current || !ready.current)
          return false;
        head.speakAudio({ audio, ...timing }, { lipsyncLang: "en" }, (word) => {
          if (ownGeneration === generation.current)
            callbacks.current.onWord?.(word.trim());
        });
        playing.current = true;
        callbacks.current.onSpeakingChange?.(true);
        return true;
      },
      stop,
    }));

    useEffect(() => {
      let disposed = false;
      queueMicrotask(async () => {
        if (disposed || !host.current || !canvasHost.current) return;
        callbacks.current.onModelState?.("loading");
        let head: TalkingHead | null = null;
        try {
          const context = new AudioContext();
          contextRef.current = context;
          const node = host.current;
          let motions = 0,
            previous = 0,
            expressionTime = 0,
            expressionWeight = 0,
            observedSpeaking = false,
            observedGeneration = generation.current;
          head = new TalkingHead(canvasHost.current, {
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
            avatarSpeakingHeadMove: 0.38,
            update: (dt: number) => {
              if (disposed || !head) return;
              expressionTime += Math.min(dt, 100) / 1000;
              expressionWeight +=
                ((head.isSpeaking ? 1 : 0) - expressionWeight) *
                (1 - Math.exp(-dt / 300));
              const expressions: Record<string, number> = {
                browInnerUp: 0.1 + 0.06 * Math.sin(expressionTime * 1.2),
                browOuterUpLeft: 0.08 + 0.06 * Math.sin(expressionTime * 0.9),
                browOuterUpRight:
                  0.04 + 0.03 * Math.sin(expressionTime * 0.9 + 1),
                eyeSquintLeft: 0.04,
                eyeSquintRight: 0.04,
              };
              for (const [name, value] of Object.entries(expressions))
                if (head.mtAvatar[name])
                  head.mtAvatar[name].realtime = value * expressionWeight;
              if (observedGeneration !== generation.current) {
                observedSpeaking = false;
                observedGeneration = generation.current;
              }
              if (head.isSpeaking) observedSpeaking = true;
              node.dataset.expressionWeight = expressionWeight.toFixed(3);
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
              node.dataset.visemeMax = maximum.toFixed(3);
              node.dataset.visemeActiveCount = String(active);
              node.dataset.visemeMotionCount = String(motions);
              node.dataset.speaking = String(head.isSpeaking);
              if (
                playing.current &&
                observedSpeaking &&
                !head.isSpeaking &&
                !head.isAudioPlaying
              ) {
                playing.current = false;
                observedSpeaking = false;
                callbacks.current.onSpeakingChange?.(false);
                callbacks.current.onWord?.("");
                callbacks.current.onComplete?.();
              }
            },
          });
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
                callbacks.current.onProgress?.(
                  Math.round((event.loaded / event.total) * 100),
                );
            },
          );
          if (disposed) {
            head.dispose();
            return;
          }
          for (const [name, target] of Object.entries(head.mtAvatar))
            if (name.startsWith("viseme_"))
              target.limit = (value: number) =>
                Math.max(0, Math.min(0.38, value * 0.45));
          canvasHost.current
            ?.querySelector("canvas")
            ?.setAttribute("aria-hidden", "true");
          ready.current = true;
          node.dataset.modelState = "ready";
          callbacks.current.onModelState?.("ready");
        } catch {
          if (disposed) return;
          ready.current = false;
          head?.dispose();
          headRef.current = null;
          if (contextRef.current?.state !== "closed")
            void contextRef.current?.close();
          contextRef.current = null;
          if (host.current) host.current.dataset.modelState = "failed";
          callbacks.current.onModelState?.("failed");
          callbacks.current.onError?.(
            "Animated avatar unavailable. Captions and evidence remain available.",
          );
        }
      });
      return () => {
        disposed = true;
        ready.current = false;
        playing.current = false;
        generation.current += 1;
        headRef.current?.dispose();
        headRef.current = null;
        if (contextRef.current && contextRef.current.state !== "closed")
          void contextRef.current.close();
        contextRef.current = null;
      };
    }, []);
    return (
      <div
        className={`talking-detective ${props.className || ""}`}
        ref={host}
        role="img"
        aria-label={props.label}
        data-model-state="loading"
        data-speaking="false"
        data-viseme-max="0"
        data-viseme-motion-count="0"
      >
        <div className="talking-detective-canvas" ref={canvasHost} />
      </div>
    );
  },
);
export default TalkingDetective;

type LocalPerformanceOptions = {
  room: string;
  dialogue: string;
  revision: number;
  paused: boolean;
  online: boolean;
  token: string;
  animated: boolean;
  onAnimatedChange: (animated: boolean) => void;
};
type LocalSpeech = SpeechTiming & {
  provider: "windows-sapi";
  voice: "david" | "zira";
  text: string;
  revision: number;
  audio_base64: string;
  content_type: "audio/wav";
};
function isLocalSpeech(value: unknown): value is LocalSpeech {
  if (!value || typeof value !== "object") return false;
  const sample = value as LocalSpeech;
  return (
    sample.provider === "windows-sapi" &&
    sample.content_type === "audio/wav" &&
    ["david", "zira"].includes(sample.voice) &&
    typeof sample.text === "string" &&
    Number.isInteger(sample.revision) &&
    typeof sample.audio_base64 === "string" &&
    !!sample.audio_base64 &&
    Array.isArray(sample.words) &&
    sample.words.length > 0 &&
    sample.words.every((word) => typeof word === "string") &&
    Array.isArray(sample.wtimes) &&
    Array.isArray(sample.wdurations) &&
    sample.words.length === sample.wtimes.length &&
    sample.words.length === sample.wdurations.length &&
    [...sample.wtimes, ...sample.wdurations].every(
      (time) => typeof time === "number" && Number.isFinite(time) && time >= 0,
    )
  );
}

/** Takes public narration scalars only: private guest cards cannot enter speech requests. */
export function useLocalDetectivePerformance(
  options: LocalPerformanceOptions,
): { avatar: ReactNode; controls: ReactNode; speaking: boolean; stop: () => void } {
  const viewer = useRef<TalkingDetectiveHandle>(null),
    request = useRef<AbortController | null>(null);
  const generation = useRef(0),
    lastSpoken = useRef(""),
    latest = useRef(options),
    enabledRef = useRef(false);
  latest.current = options;
  const [enabled, setEnabled] = useState(false),
    [speaking, setSpeaking] = useState(false),
    [voice, setVoice] = useState<"david" | "zira">("zira"),
    [loading, setLoading] = useState(false);
  const [available, setAvailable] = useState<boolean | null>(null),
    [modelState, setModelState] = useState<"loading" | "ready" | "failed">(
      "loading",
    );
  const [progress, setProgress] = useState<number | null>(null),
    [message, setMessage] = useState(
      "Muted. Enable local voice to hear the detective.",
    ),
    [error, setError] = useState("");
  function stop() {
    generation.current += 1;
    request.current?.abort();
    request.current = null;
    viewer.current?.stop();
    setLoading(false);
  }
  function mute() {
    enabledRef.current = false;
    setEnabled(false);
    stop();
    setMessage("Local voice muted.");
  }
  useEffect(() => {
    if (!options.animated) {
      mute();
      return;
    }
    const abort = new AbortController();
    setAvailable(null);
    fetch("/api/speech/status", { signal: abort.signal })
      .then((response) => {
        if (!response.ok) throw Error("status");
        return response.json();
      })
      .then((value) => {
        if (abort.signal.aborted) return;
        if (typeof value.available !== "boolean") throw Error("status");
        setAvailable(value.available);
      })
      .catch(() => {
        if (!abort.signal.aborted) setAvailable(false);
      });
    return () => abort.abort();
  }, [options.animated, options.room]);
  useEffect(() => {
    if (!options.online) {
      enabledRef.current = false;
      setEnabled(false);
      stop();
      setMessage("Disconnected. Re-enable local voice after reconnecting.");
    }
    if (!options.animated) {
      enabledRef.current = false;
      setEnabled(false);
      stop();
    }
  }, [options.online, options.animated]);

  async function perform() {
    const current = latest.current;
    if (
      !enabledRef.current ||
      !current.animated ||
      !current.online ||
      current.paused ||
      !current.token ||
      modelState !== "ready"
    )
      return;
    stop();
    const ownGeneration = generation.current;
    const requestVoice = voice;
    lastSpoken.current = current.dialogue;
    setLoading(true);
    setError("");
    setMessage("Preparing the current public dialogue…");
    const abort = new AbortController();
    request.current = abort;
    try {
      const response = await fetch(
        `/api/rooms/${encodeURIComponent(current.room)}/speech`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${current.token}`,
          },
          body: JSON.stringify({ voice: requestVoice }),
          signal: abort.signal,
        },
      );
      if (!response.ok) {
        if (response.status === 401 || response.status === 403)
          throw Error("access");
        if (response.status === 409) throw Error("stale");
        if (response.status === 429) throw Error("busy");
        throw Error("unavailable");
      }
      const sample: unknown = await response.json();
      const now = latest.current;
      if (
        ownGeneration !== generation.current ||
        !enabledRef.current ||
        !now.online ||
        now.paused ||
        !now.animated ||
        now.revision !== current.revision ||
        now.dialogue !== current.dialogue
      )
        return;
      if (
        !isLocalSpeech(sample) ||
        sample.revision !== current.revision ||
        sample.text !== current.dialogue ||
        sample.voice !== requestVoice
      )
        throw Error("stale");
      const binary = atob(sample.audio_base64),
        bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1)
        bytes[i] = binary.charCodeAt(i);
      const started = await viewer.current?.speakAudio(bytes.buffer, {
        words: sample.words,
        wtimes: sample.wtimes,
        wdurations: sample.wdurations,
      });
      if (ownGeneration !== generation.current || !enabledRef.current) return;
      if (started)
        setMessage(
          `Speaking the room’s current dialogue with Microsoft ${requestVoice === "zira" ? "Zira" : "David"}.`,
        );
    } catch (failure) {
      if (ownGeneration !== generation.current || abort.signal.aborted) return;
      const kind = failure instanceof Error ? failure.message : "unavailable";
      if (kind === "stale")
        setMessage(
          "The case changed. Use Replay dialogue when the table is ready.",
        );
      else
        setError(
          kind === "access"
            ? "Open the authenticated TV link from the host desk to use local voice."
            : kind === "busy"
              ? "Local speech is already preparing a line. Try Replay dialogue shortly."
              : "Local speech is unavailable. Captions and evidence still work; check the server’s Windows voice setup.",
        );
    } finally {
      if (ownGeneration === generation.current) setLoading(false);
    }
  }
  useEffect(() => {
    stop();
    if (options.paused) {
      setMessage("Evening paused. Speech stopped.");
      return;
    }
    if (
      enabled &&
      options.animated &&
      options.online &&
      modelState === "ready" &&
      lastSpoken.current !== options.dialogue
    )
      void perform();
    return () => {
      generation.current += 1;
      request.current?.abort();
      viewer.current?.stop();
    };
  }, [
    options.dialogue,
    options.revision,
    options.paused,
    options.online,
    options.animated,
    options.room,
    enabled,
    modelState,
    voice,
  ]);
  useEffect(
    () => () => {
      generation.current += 1;
      request.current?.abort();
      viewer.current?.stop();
    },
    [],
  );
  async function enable() {
    try {
      await viewer.current?.unlock();
      if (
        !latest.current.online ||
        !latest.current.animated ||
        latest.current.paused
      )
        return;
      enabledRef.current = true;
      lastSpoken.current = "";
      setError("");
      setEnabled(true);
      setMessage("Local voice enabled.");
    } catch {
      setError(
        "The avatar’s audio is not ready. Try Enable local voice again.",
      );
    }
  }
  const canPlay =
    options.online &&
    !options.paused &&
    !!options.token &&
    modelState === "ready" &&
    available === true;
  return {
    stop,
    speaking,
    avatar: options.animated ? (
      <>
        <TalkingDetective
          ref={viewer}
          label="TalkingHead detective"
          onModelState={setModelState}
          onProgress={setProgress}
          onSpeakingChange={setSpeaking}
          onComplete={() =>
            setMessage("Line finished. Listening for the next public dialogue.")
          }
          onError={setError}
        />
        {modelState !== "ready" && (
          <div className="animated-stage-notice">
            <strong>
              {modelState === "failed"
                ? "Animated avatar unavailable"
                : `Loading licensed sample${progress !== null ? ` · ${progress}%` : "…"}`}
            </strong>
            Captions and evidence remain available.
          </div>
        )}
      </>
    ) : null,
    controls: (
      <section
        className="local-performance"
        aria-label="Local detective performance"
      >
        <div className="local-performance-controls">
          <label>
            <input
              type="checkbox"
              checked={options.animated}
              onChange={(event) =>
                options.onAnimatedChange(event.target.checked)
              }
            />{" "}
            Animated detective
          </label>
          {options.animated && (
            <>
              <label htmlFor="local-detective-voice">Local voice</label>
              <select
                id="local-detective-voice"
                value={voice}
                onChange={(event) => {
                  mute();
                  setVoice(event.target.value as "zira" | "david");
                  setMessage("Voice changed. Enable local voice when ready.");
                }}
              >
                <option value="zira">Microsoft Zira · en-US</option>
                <option value="david">Microsoft David · en-US</option>
              </select>
              {enabled ? (
                <button onClick={mute}>Mute local voice</button>
              ) : (
                <button onClick={enable} disabled={!canPlay}>
                  Enable local voice
                </button>
              )}
              <button
                onClick={() => {
                  stop();
                  setMessage(
                    "Speech stopped. The next new dialogue may play; mute to remain silent.",
                  );
                }}
                disabled={!enabled && !loading}
              >
                Stop speech
              </button>
              <button
                onClick={async () => {
                  try {
                    await viewer.current?.unlock();
                    void perform();
                  } catch {
                    setError("Audio is not ready. Try again after loading.");
                  }
                }}
                disabled={!enabled || !canPlay || loading}
              >
                Replay dialogue
              </button>
            </>
          )}
        </div>
        {options.animated && (
          <>
            <p>
              Licensed sample avatar — not final Wobblebottom. Existing Windows
              voices are a local demonstration, not the final British voice.
              Muted until you enable it.
            </p>
            {!options.token && (
              <p className="performance-error">
                For local voice, open the authenticated TV link from the host
                desk. The public TV view still works.
              </p>
            )}
            {available === false && (
              <p className="performance-error">
                Local Windows speech is unavailable on this server. Captions and
                evidence remain available.
              </p>
            )}
            <p role="status">
              {loading ? "Preparing current dialogue…" : message}
            </p>
            {error && (
              <p className="performance-error" role="alert">
                {error}
              </p>
            )}
          </>
        )}
      </section>
    ),
  };
}
